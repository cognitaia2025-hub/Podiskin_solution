"""
Nodo: Escalar a Humano
=======================

Marca la conversación para escalamiento a humano.
"""

import logging
from typing import Dict

from ..state import WhatsAppAgentState
from ..config import config, ESCALATION_MESSAGE
from ..utils import execute

logger = logging.getLogger(__name__)


async def escalate_to_human_node(state: WhatsAppAgentState) -> Dict:
    """
    Escala la conversación a un humano.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con escalamiento marcado
    """
    conversation_id = state["conversation_id"]
    reason = state.get("escalation_reason", "Confianza baja en clasificación")

    logger.warning(f"[{conversation_id}] Escalating to human. Reason: {reason}")

    try:
        # Actualizar conversación en BD
        await execute(
            """
            UPDATE conversaciones
            SET estado = 'Esperando_Humano',
                categoria = 'Escalado'
            WHERE id = %s
        """,
            int(conversation_id),
        )

        logger.info(f"[{conversation_id}] Conversation marked for human attention")

        # TODO: Notificar al equipo (webhook, email, etc.)
        # await notify_staff(conversation_id, contact_id, reason)

        return {
            **state,
            "requires_human": True,
            "escalation_reason": reason,
            "next_action": "send_escalation_message",
            "processing_stage": "generate",
        }

    except Exception as e:
        logger.error(
            f"[{conversation_id}] Error escalating to human: {str(e)}", exc_info=True
        )

        return {
            **state,
            "requires_human": True,
            "escalation_reason": reason,
            "error": f"Error en escalamiento: {str(e)}",
        }
