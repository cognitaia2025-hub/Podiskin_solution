"""
Nodo: Post-Procesador de Escalamiento
======================================

Detecta si Maya indicó desconocimiento y automáticamente escala la pregunta.
"""

import logging
import re
from typing import Dict
from datetime import datetime

from ..state import WhatsAppAgentState
from ..tools.escalation_tools import escalate_question_to_admin

logger = logging.getLogger(__name__)


async def post_process_escalation_node(state: WhatsAppAgentState) -> Dict:
    """
    Post-procesa la respuesta para detectar si Maya necesita escalar.

    Si Maya indicó que "consultará" o "no tiene información",
    automáticamente llama al tool de escalamiento.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con escalamiento si es necesario
    """
    conversation_id = state["conversation_id"]

    # Obtener última respuesta de Maya
    if not state["messages"]:
        return state

    last_message = state["messages"][-1]
    response_content = (
        last_message.content
        if hasattr(last_message, "content")
        else last_message.get("content", "")
    )

    # Patrones que indican que Maya no sabe algo
    escalation_patterns = [
        r"consultaré",
        r"consultar",
        r"no tengo esa información",
        r"déjeme consultarlo",
        r"permítame consultar",
        r"consultarlo con el personal",
        r"consultarlo con el equipo",
    ]

    # Verificar si la respuesta indica desconocimiento
    should_escalate = any(
        re.search(pattern, response_content, re.IGNORECASE)
        for pattern in escalation_patterns
    )

    if not should_escalate:
        logger.debug(f"[{conversation_id}] No escalation needed")
        return state

    # ESCALAR AUTOMÁTICAMENTE
    logger.info(f"[{conversation_id}] Auto-escalating question to admin")

    try:
        # Obtener pregunta del usuario (penúltimo mensaje)
        user_question = ""
        for msg in reversed(state["messages"][:-1]):
            msg_type = msg.type if hasattr(msg, "type") else msg.get("role", "")
            if msg_type in ["human", "user"]:
                user_question = (
                    msg.content if hasattr(msg, "content") else msg.get("content", "")
                )
                break

        if not user_question:
            logger.warning(f"[{conversation_id}] Could not find user question")
            return state

        # Obtener info del paciente
        patient_info = state.get("patient_info", {})
        patient_name = patient_info.get("nombre", "Usuario")
        patient_phone = patient_info.get("telefono", state.get("phone", ""))
        patient_chat_id = state.get("chat_id", "")

        # Llamar al tool de escalamiento
        escalation_result = escalate_question_to_admin(
            patient_name=patient_name,
            patient_phone=patient_phone,
            patient_chat_id=patient_chat_id,
            question=user_question,
            context=f"Conversación ID: {conversation_id}",
        )

        if escalation_result.get("success"):
            logger.info(
                f"[{conversation_id}] Question escalated successfully "
                f"(duda_id: {escalation_result.get('duda_id')})"
            )

            # Reemplazar la respuesta de Maya con la del tool
            new_response = escalation_result.get("patient_response")

            # Actualizar último mensaje
            updated_messages = state["messages"][:-1] + [
                {
                    "role": "assistant",
                    "content": new_response,
                    "timestamp": datetime.now().isoformat(),
                }
            ]

            # Agregar datos de escalamiento al estado
            return {
                **state,
                "messages": updated_messages,
                "escalation_data": {
                    "duda_id": escalation_result.get("duda_id"),
                    "admin_message": escalation_result.get("admin_message"),
                    "escalated": True,
                },
            }
        else:
            logger.error(
                f"[{conversation_id}] Escalation failed: "
                f"{escalation_result.get('error')}"
            )
            return state

    except Exception as e:
        logger.error(f"[{conversation_id}] Error in escalation: {e}", exc_info=True)
        return state
