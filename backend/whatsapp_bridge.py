"""
WhatsApp Bridge API - Podoskin Solution
========================================

API FastAPI que conecta whatsapp-web.js con Maya.
"""

import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Importar agente Maya
import sys

sys.path.insert(0, "./agents")
from agents.sub_agent_whatsApp.graph import run_agent
from agents.sub_agent_whatsApp.utils import (
    init_db_pool,
    close_db_pool,
    get_or_create_contact,
    get_or_create_conversation,
    save_message,
)
from agents.sub_agent_whatsApp.utils.escalation import (
    parse_admin_response,
    get_pending_question,
    answer_pending_question,
)
from agents.sub_agent_whatsApp.config import WhatsAppAgentConfig

config = WhatsAppAgentConfig()
from langchain_core.messages import HumanMessage, AIMessage

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# MODELOS
# ============================================================================


class WhatsAppMessage(BaseModel):
    """Mensaje entrante de WhatsApp."""

    chat_id: str
    phone: str
    name: str
    message: str


class WhatsAppResponse(BaseModel):
    """Respuesta para WhatsApp."""

    success: bool
    response: str
    intent: Optional[str] = None
    error: Optional[str] = None
    # Campos para escalamiento
    admin_message: Optional[str] = None
    admin_chat_id: Optional[str] = None
    target_chat_id: Optional[str] = None


# ============================================================================
# APP LIFECYCLE
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la app."""
    logger.info("🚀 Iniciando Bridge API...")
    await init_db_pool()
    logger.info("✅ Conexión a base de datos establecida")
    yield
    logger.info("🔌 Cerrando conexiones...")
    await close_db_pool()


# ============================================================================
# APP
# ============================================================================

app = FastAPI(
    title="WhatsApp Bridge - Maya",
    description="API que conecta WhatsApp con el agente Maya",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Almacenar historial de mensajes por conversación
conversation_messages: dict = {}


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/")
async def root():
    """Health check."""
    return {"status": "ok", "service": "Maya WhatsApp Bridge"}


@app.post("/webhook/whatsapp", response_model=WhatsAppResponse)
async def handle_whatsapp_message(msg: WhatsAppMessage):
    """
    Recibe mensaje de WhatsApp y retorna respuesta de Maya.
    """
    # Ignorar mensajes vacíos
    if not msg.message or not msg.message.strip():
        logger.info(f"⚠️ Mensaje vacío de {msg.phone}, ignorando...")
        return WhatsAppResponse(success=True, response="", intent="empty")

    logger.info(f"📩 Mensaje de {msg.name} ({msg.phone}): {msg.message[:50]}...")

    # DETECTAR SI ES EL ADMIN RESPONDIENDO UNA DUDA
    if msg.chat_id == config.admin_chat_id:
        parsed = parse_admin_response(msg.message)
        if parsed:
            duda_id, respuesta = parsed
            logger.info(f"Admin respondiendo duda #{duda_id}")

            # Obtener duda
            duda = get_pending_question(duda_id)
            if duda and duda["estado"] == "pendiente":
                # Marcar como respondida
                answer_pending_question(duda_id, respuesta, msg.chat_id)

                # Retornar para enviar al paciente
                return WhatsAppResponse(
                    success=True,
                    response=f"Ya me informan que {respuesta}",
                    intent="admin_response",
                )
            else:
                return WhatsAppResponse(
                    success=True,
                    response=f"Duda #{duda_id} no encontrada o ya respondida.",
                    intent="admin_error",
                )
        # Si el admin escribe algo que no es respuesta, ignorar
        logger.info("Mensaje del admin sin formato #RESPUESTA_XXX, ignorando")
        return WhatsAppResponse(success=True, response="", intent="admin_chat")

    try:
        # Obtener o crear contacto
        contact = await get_or_create_contact(
            telefono=msg.phone, nombre=msg.name, whatsapp_id=msg.chat_id
        )
        contact_id = contact["id"]

        # Obtener o crear conversación
        conversation = await get_or_create_conversation(
            contact_id=contact_id, whatsapp_chat_id=msg.chat_id
        )
        conversation_id = conversation["id"]

        # Guardar mensaje del usuario
        await save_message(
            conversation_id=conversation_id, rol="user", contenido=msg.message
        )

        # Mantener historial de mensajes
        if conversation_id not in conversation_messages:
            conversation_messages[conversation_id] = []

        conversation_messages[conversation_id].append(HumanMessage(content=msg.message))

        # Preparar estado para el agente
        state = {
            "messages": conversation_messages[conversation_id].copy(),
            "conversation_id": str(conversation_id),
            "contact_id": contact_id,
            "patient_id": None,
            "intent": None,
            "confidence": 0.0,
            "entities": {},
            "requires_human": False,
            "escalation_reason": None,
            "retrieved_context": [],
            "appointment_history": [],
            "pending_appointment": None,
            "suggested_slots": [],
            "patient_info": None,
            "next_action": None,
            "processing_stage": "classify",
            "error": None,
        }

        # Ejecutar agente Maya
        result = await run_agent(state=state, thread_id=f"wa_{conversation_id}")

        # Obtener respuesta
        last_msg = result["messages"][-1]
        response = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

        # DETECTAR SI MAYA USÓ EL TOOL DE ESCALAMIENTO
        escalation_data = None
        for message in result["messages"]:
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tool_call in message.tool_calls:
                    if tool_call.get("name") == "escalate_question_to_admin":
                        # Maya usó el tool de escalamiento
                        logger.info("Maya escaló una duda al admin")
                        # Buscar el resultado del tool en los mensajes siguientes
                        for msg in result["messages"]:
                            if hasattr(msg, "content") and isinstance(msg.content, str):
                                try:
                                    import json

                                    content_data = json.loads(msg.content)
                                    if content_data.get("success") and content_data.get(
                                        "admin_message"
                                    ):
                                        escalation_data = content_data
                                        break
                                except:
                                    pass

        # Si hay escalamiento, retornar datos especiales
        if escalation_data:
            return WhatsAppResponse(
                success=True,
                response=escalation_data.get("patient_response", response),
                intent="escalated",
                admin_message=escalation_data.get("admin_message"),
                admin_chat_id=config.admin_chat_id,
            )

        # Agregar respuesta al historial
        conversation_messages[conversation_id].append(AIMessage(content=response))

        # Limitar historial a últimos 20 mensajes
        if len(conversation_messages[conversation_id]) > 20:
            conversation_messages[conversation_id] = conversation_messages[
                conversation_id
            ][-20:]

        # Guardar respuesta
        await save_message(
            conversation_id=conversation_id, rol="assistant", contenido=response
        )

        logger.info(f"🤖 Maya responde: {response[:50]}...")

        return WhatsAppResponse(
            success=True, response=response, intent=result.get("intent")
        )

    except Exception as e:
        logger.error(f"❌ Error procesando mensaje: {str(e)}", exc_info=True)
        return WhatsAppResponse(
            success=False,
            response="Disculpe, estoy teniendo problemas. Llame al 686-108-3647.",
            error=str(e),
        )


@app.post("/webhook/clear/{chat_id}")
async def clear_conversation(chat_id: str):
    """Limpia el historial de una conversación."""
    # Buscar y limpiar por chat_id
    for conv_id in list(conversation_messages.keys()):
        if chat_id in str(conv_id):
            del conversation_messages[conv_id]
            return {"success": True, "message": "Conversación limpiada"}
    return {"success": False, "message": "Conversación no encontrada"}


@app.post("/webhook/notify_admin")
async def notify_admin(duda_id: int, admin_message: str):
    """
    Endpoint para enviar notificación al admin sobre una duda.
    El cliente Node.js llamará esto para enviar el mensaje al admin.
    """
    return {
        "success": True,
        "admin_chat_id": config.admin_chat_id,
        "message": admin_message,
        "duda_id": duda_id,
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("whatsapp_bridge:app", host="0.0.0.0", port=8000, reload=True)
