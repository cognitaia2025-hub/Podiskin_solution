"""
Endpoints API para Agente WhatsApp
==================================

Define los endpoints REST para interactuar con el agente.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from auth import get_current_user, User
from ..graph import whatsapp_graph
from ..utils_helpers import enviar_whatsapp, notificar_escalado
from ..tools import save_rag_learning

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents/whatsapp", tags=["WhatsApp Agent"])


# ============================================================================
# MODELOS PYDANTIC
# ============================================================================


class MensajeInput(BaseModel):
    """Mensaje entrante de WhatsApp"""

    content: str
    phone_number: Optional[str] = None


class RespuestaHumanaInput(BaseModel):
    """Respuesta del humano para HITL"""

    respuesta: str
    generar_aprendizaje: bool = True
    tono_cliente: str = "neutral"
    tono_respuesta: str = "profesional"
    categoria: str = "general"


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/{chat_id}/mensaje")
async def procesar_mensaje(
    chat_id: str, mensaje: MensajeInput, current_user: User = Depends(get_current_user)
):
    """
    Procesa un mensaje entrante de WhatsApp.

    Flujo:
    1. Ejecuta el grafo del agente
    2. Si debe_escalar → notifica frontend
    3. Si no → envía respuesta automática

    Args:
        chat_id: ID único del chat de WhatsApp
        mensaje: Contenido del mensaje
        current_user: Usuario autenticado

    Returns:
        Resultado del procesamiento
    """
    config = {"configurable": {"thread_id": chat_id}}

    try:
        logger.info(f"Procesando mensaje de {chat_id}")

        # Ejecutar grafo
        result = await whatsapp_graph.ainvoke(
            {
                "messages": [{"role": "user", "content": mensaje.content}],
                "chat_id": chat_id,
                "debe_escalar": False,
            },
            config,
        )

        # Verificar si necesita escalamiento
        if result.get("debe_escalar"):
            # Notificar frontend
            await notificar_escalado(
                {
                    "chat_id": chat_id,
                    "mensaje": mensaje.content,
                    "sentimiento": result.get("sentimiento"),
                    "sugerencia": result.get("respuesta_generada"),
                }
            )

            return {
                "status": "escalado",
                "message": "Duda escalada para atención humana",
                "sugerencia": result.get("respuesta_generada"),
            }

        # Enviar respuesta automática
        respuesta = result.get("respuesta_generada")
        if respuesta:
            await enviar_whatsapp(chat_id, respuesta)

            return {
                "status": "respondido",
                "respuesta": respuesta,
                "sentimiento": result.get("sentimiento"),
            }

        # Fallback
        return {"status": "error", "message": "No se pudo generar respuesta"}

    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error procesando mensaje: {str(e)}"
        )


@router.post("/{chat_id}/respuesta-humana")
async def respuesta_humana(
    chat_id: str,
    data: RespuestaHumanaInput,
    current_user: User = Depends(get_current_user),
):
    """
    Procesa la respuesta de un humano para una duda escalada.

    Flujo:
    1. Envía la respuesta al paciente
    2. Si generar_aprendizaje → guarda en RAG
    3. Actualiza el estado del grafo

    Args:
        chat_id: ID único del chat
        data: Respuesta del humano
        current_user: Usuario autenticado

    Returns:
        Resultado del procesamiento
    """
    config = {"configurable": {"thread_id": chat_id}}

    try:
        logger.info(f"Procesando respuesta humana para {chat_id}")

        # Enviar respuesta a WhatsApp
        await enviar_whatsapp(chat_id, data.respuesta)

        # Auto-aprendizaje si está habilitado
        if data.generar_aprendizaje:
            # Obtener el estado actual para la pregunta original
            state = await whatsapp_graph.aget_state(config)
            pregunta = state.values.get("messages", [])[-1].get("content", "")

            # Guardar aprendizaje
            result = await save_rag_learning(
                pregunta=pregunta,
                respuesta=data.respuesta,
                tono_cliente=data.tono_cliente,
                tono_respuesta=data.tono_respuesta,
                categoria=data.categoria,
            )

            if result["success"]:
                logger.info(f"✅ Aprendizaje guardado: {result['aprendizaje_id']}")
            else:
                logger.warning(
                    f"⚠️ No se pudo guardar aprendizaje: {result.get('error')}"
                )

        # Actualizar estado del grafo con la respuesta humana
        await whatsapp_graph.aupdate_state(config, {"respuesta_humana": data.respuesta})

        return {
            "status": "enviado",
            "message": "Respuesta enviada y procesada",
            "aprendizaje_guardado": data.generar_aprendizaje,
        }

    except Exception as e:
        logger.error(f"Error procesando respuesta humana: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error procesando respuesta: {str(e)}"
        )


@router.get("/{chat_id}/estado")
async def get_estado_conversacion(
    chat_id: str, current_user: User = Depends(get_current_user)
):
    """
    Obtiene el estado actual de una conversación.

    Args:
        chat_id: ID único del chat
        current_user: Usuario autenticado

    Returns:
        Estado actual del grafo
    """
    config = {"configurable": {"thread_id": chat_id}}

    try:
        state = await whatsapp_graph.aget_state(config)

        return {
            "chat_id": chat_id,
            "messages": state.values.get("messages", []),
            "sentimiento": state.values.get("sentimiento"),
            "debe_escalar": state.values.get("debe_escalar", False),
            "paciente_id": state.values.get("paciente_id"),
        }

    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error obteniendo estado: {str(e)}"
        )
