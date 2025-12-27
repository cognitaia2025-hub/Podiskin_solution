"""
Nodo: Gestionar Cancelaciones
==============================

Gestiona cancelación/reagendamiento de citas.
"""

import logging
from typing import Dict

from ..state import WhatsAppAgentState
from ..utils import fetch

logger = logging.getLogger(__name__)


async def handle_cancellation_node(state: WhatsAppAgentState) -> Dict:
    """
    Gestiona cancelación/reagendamiento de citas.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado
    """
    conversation_id = state["conversation_id"]
    patient_id = state.get("patient_id")

    logger.info(f"[{conversation_id}] Handling cancellation request...")

    try:
        if not patient_id:
            logger.info(
                f"[{conversation_id}] Contact is not a patient, "
                f"no appointments to cancel"
            )
            return {**state, "next_action": "no_appointments", "requires_human": False}

        # Buscar citas activas
        query = """
        SELECT id, fecha_hora, estado
        FROM citas
        WHERE id_paciente = %s
          AND estado IN ('Programada', 'Confirmada')
          AND fecha_hora > NOW()
        ORDER BY fecha_hora
        LIMIT 5
        """

        active_appointments = await fetch(query, patient_id)

        if not active_appointments:
            logger.info(f"[{conversation_id}] No active appointments found")
            return {**state, "next_action": "no_appointments", "requires_human": False}

        # Si tiene citas, escalar a humano para confirmar cancelación
        logger.info(
            f"[{conversation_id}] Found {len(active_appointments)} "
            f"active appointments, escalating for confirmation"
        )

        return {
            **state,
            "entities": {
                **state.get("entities", {}),
                "active_appointments": [dict(a) for a in active_appointments],
            },
            "next_action": "confirm_cancellation",
            "requires_human": True,
            "escalation_reason": "Confirmación de cancelación de cita",
        }

    except Exception as e:
        logger.error(
            f"[{conversation_id}] Error handling cancellation: {str(e)}", exc_info=True
        )

        return {
            **state,
            "error": f"Error en cancelación: {str(e)}",
            "requires_human": True,
        }
