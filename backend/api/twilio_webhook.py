"""
Twilio WhatsApp Webhook
=======================

Endpoint para recibir mensajes de Twilio y procesarlos con el Agente Maya.

Referencias:
- https://www.twilio.com/docs/whatsapp/api
- https://docs.langchain.com/oss/python/langgraph/workflows-agents
"""

from fastapi import APIRouter, Form, Response, Request, HTTPException
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
import logging
from datetime import datetime
import os
import json

from db import get_pool
from agents.whatsapp_medico.graph import whatsapp_graph
from agents.whatsapp_medico.tools.filter_tools import check_filters

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["Twilio Webhook"])

# Validador de firma Twilio
try:
    validator = RequestValidator(os.getenv("TWILIO_AUTH_TOKEN", ""))
except:
    validator = None
    logger.warning("Twilio validator not initialized - will skip signature validation")

# ============================================================================
# VALIDACIÓN DE FIRMA TWILIO
# ============================================================================

def validate_twilio_signature(request: Request, form_data: dict) -> bool:
    """
    Valida que el webhook venga de Twilio verificando la firma X-Twilio-Signature.
    
    Referencias:
    - https://www.twilio.com/docs/usage/security#validating-requests
    """
    if not validator:
        logger.warning("Twilio validator not configured")
        return True
    
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    
    # En desarrollo, skip validation
    if os.getenv("ENVIRONMENT") == "development":
        logger.warning("Skipping Twilio signature validation (development mode)")
        return True
    
    is_valid = validator.validate(url, form_data, signature)
    
    if not is_valid:
        logger.error(f"Invalid Twilio signature from {request.client.host if request.client else 'unknown'}")
    
    return is_valid

# ============================================================================
# WEBHOOK PRINCIPAL
# ============================================================================

@router.post("/twilio")
async def twilio_webhook_handler(
    request: Request,
    From: str = Form(...),      # whatsapp:+5216862262377
    To: str = Form(...),        # whatsapp:+16206986058
    Body: str = Form(...),      # "Hola, quiero una cita"
    MessageSid: str = Form(...)  # SMxxxxxxxxxxxx
):
    """
    Webhook principal de Twilio para WhatsApp.
    
    Flujo:
    1. Validar firma de Twilio
    2. Limpiar número de teléfono
    3. Aplicar filtros (blacklist/whitelist)
    4. Buscar/crear contacto en BD
    5. Buscar/crear conversación
    6. Guardar mensaje entrante
    7. Ejecutar Agente Maya (LangGraph)
    8. Guardar respuesta en BD
    9. Retornar TwiML con respuesta
    """
    pool = await get_pool()
    
    # Preparar form_data para validación
    form_data = {
        "From": From,
        "To": To,
        "Body": Body,
        "MessageSid": MessageSid
    }
    
    # Log del webhook
    try:
        await pool.execute(
            """
            INSERT INTO twilio_webhook_logs 
            (message_sid, from_number, to_number, body, signature_valid, raw_payload)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            MessageSid, From, To, Body, True, json.dumps(form_data)
        )
    except Exception as e:
        logger.error(f"Error logging webhook: {e}")
    
    # 1. Validar firma
    if not validate_twilio_signature(request, form_data):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")
    
    # 2. Limpiar número (quitar "whatsapp:+")
    phone = From.replace("whatsapp:+", "").replace("whatsapp:", "")
    logger.info(f"📨 Mensaje de Twilio: {phone} → '{Body[:50]}...'")
    
    try:
        # 3. Aplicar filtros
        filter_result = await check_filters(phone, is_group=False)
        
        if filter_result['blocked']:
            logger.warning(f"⛔ Número bloqueado: {phone} - Razón: {filter_result['reason']}")
            
            # Retornar sin respuesta (silent drop)
            resp = MessagingResponse()
            return Response(content=str(resp), media_type="application/xml")
        
        # 4. Buscar/crear contacto
        contacto = await pool.fetchrow(
            "SELECT * FROM contactos WHERE telefono = $1 OR whatsapp_id = $1",
            phone
        )
        
        if not contacto:
            contacto_id = await pool.fetchval(
                """
                INSERT INTO contactos (telefono, whatsapp_id, nombre, tipo, origen)
                VALUES ($1, $1, 'Usuario WhatsApp', 'Prospecto', 'WhatsApp')
                RETURNING id
                """,
                phone
            )
            logger.info(f"✨ Nuevo contacto creado: {contacto_id}")
        else:
            contacto_id = contacto['id']
        
        # 5. Buscar/crear conversación activa
        conversacion = await pool.fetchrow(
            """
            SELECT * FROM conversaciones
            WHERE id_contacto = $1 AND estado = 'Activa'
            ORDER BY fecha_ultima_actividad DESC LIMIT 1
            """,
            contacto_id
        )
        
        if not conversacion:
            conv_id = await pool.fetchval(
                """
                INSERT INTO conversaciones (id_contacto, canal, estado, categoria)
                VALUES ($1, 'WhatsApp', 'Activa', 'Consulta')
                RETURNING id
                """,
                contacto_id
            )
            logger.info(f"💬 Nueva conversación creada: {conv_id}")
        else:
            conv_id = conversacion['id']
        
        # 6. Guardar mensaje entrante
        mensaje_id = await pool.fetchval(
            """
            INSERT INTO mensajes (
                id_conversacion, direccion, enviado_por_tipo, contenido, fecha_envio,
                metadata
            )
            VALUES ($1, 'Entrante', 'Contacto', $2, $3, $4)
            RETURNING id
            """,
            conv_id,
            Body,
            datetime.now(),
            json.dumps({
                "twilio_message_sid": MessageSid,
                "from_number": phone,
                "timestamp_recepcion": datetime.now().isoformat()
            })
        )
        
        # 7. Ejecutar Agente Maya con LangGraph
        logger.info(f"🤖 Ejecutando Agente Maya para contacto {contacto_id}")
        
        # Crear state inicial
        initial_state = {
            "messages": [{"role": "user", "content": Body}],
            "chat_id": str(conv_id),
            "paciente_id": contacto.get('id_paciente') if contacto else None,
            "sentimiento": None,
            "rag_docs": [],
            "respuesta_generada": None,
            "debe_escalar": False,
            "respuesta_humana": None
        }
        
        # Ejecutar agente con thread_id = contact_id (aislamiento)
        config = {"configurable": {"thread_id": str(contacto_id)}}
        
        try:
            result = await whatsapp_graph.ainvoke(initial_state, config=config)
            
            # Extraer respuesta generada
            respuesta = result.get('respuesta_generada', '')
            if not respuesta and result.get('messages'):
                last_message = result['messages'][-1]
                respuesta = last_message.get('content', '') if isinstance(last_message, dict) else str(last_message)
            
            debe_escalar = result.get('debe_escalar', False)
            
            if not respuesta:
                respuesta = "Disculpe, tenemos problemas técnicos temporales. Un miembro de nuestro equipo le responderá pronto."
                debe_escalar = True
            
            logger.info(f"✅ Respuesta generada (escalar: {debe_escalar})")
        
        except Exception as e:
            logger.error(f"❌ Error ejecutando agente: {e}", exc_info=True)
            respuesta = "Disculpe, tenemos problemas técnicos temporales. Por favor intente más tarde."
            debe_escalar = True
        
        # 8. Guardar respuesta en BD
        await pool.execute(
            """
            INSERT INTO mensajes (
                id_conversacion, direccion, enviado_por_tipo, contenido, fecha_envio,
                metadata
            )
            VALUES ($1, 'Saliente', 'Bot', $2, $3, $4)
            """,
            conv_id,
            respuesta,
            datetime.now(),
            json.dumps({
                "requires_human": debe_escalar,
                "twilio_response_to": MessageSid
            })
        )
        
        # Actualizar conversación
        await pool.execute(
            """
            UPDATE conversaciones 
            SET fecha_ultima_actividad = $1,
                requiere_atencion = $2
            WHERE id = $3
            """,
            datetime.now(),
            debe_escalar,
            conv_id
        )
        
        # Actualizar log de webhook
        await pool.execute(
            """
            UPDATE twilio_webhook_logs
            SET procesado = true,
                respuesta_enviada = $1,
                fecha_procesamiento = $2
            WHERE message_sid = $3
            """,
            respuesta, datetime.now(), MessageSid
        )
        
        # 9. Construir respuesta TwiML
        twiml_resp = MessagingResponse()
        twiml_resp.message(respuesta)
        
        logger.info(f"📤 Respuesta enviada a {phone}")
        
        return Response(content=str(twiml_resp), media_type="application/xml")
    
    except Exception as e:
        logger.error(f"❌ Error procesando webhook de Twilio: {e}", exc_info=True)
        
        # Actualizar log con error
        try:
            await pool.execute(
                """
                UPDATE twilio_webhook_logs
                SET procesado = true,
                    error = $1,
                    fecha_procesamiento = $2
                WHERE message_sid = $3
                """,
                str(e), datetime.now(), MessageSid
            )
        except Exception as db_error:
            logger.error(f"Error al actualizar error en BD: {db_error}")
        
        # Responder con mensaje de error genérico
        twiml_resp = MessagingResponse()
        twiml_resp.message("Disculpe, tenemos problemas técnicos temporales. Por favor intente más tarde.")
        
        return Response(content=str(twiml_resp), media_type="application/xml")
