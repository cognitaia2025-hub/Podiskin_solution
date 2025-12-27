"""
Nodo: Cancelar Cita
===================

Maneja el flujo de cancelación de una cita.
"""

import logging
from typing import Dict

from ..state import OperationsAgentState
from ..tools.action_tools import cancel_appointment
from ..tools.appointment_tools import get_appointment_by_id

logger = logging.getLogger(__name__)


async def cancel_appointment_node(state: OperationsAgentState) -> Dict:
    """
    Cancela una cita.

    Flujo:
    1. Buscar cita
    2. Mostrar confirmación
    3. Si está confirmado, cancelar

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con resultado de la acción
    """
    session_id = state.get("session_id", "unknown")
    entities = state.get("entities", {})
    action_confirmed = state.get("action_confirmed", False)

    logger.info(f"[{session_id}] Cancelling appointment...")

    try:
        # Obtener ID de la cita
        appointment_id = entities.get("appointment_id")

        if not appointment_id:
            return {
                **state,
                "context": "Necesito el ID de la cita para cancelar.",
            }

        # Buscar cita
        appointment = get_appointment_by_id(appointment_id)

        if not appointment:
            return {
                **state,
                "context": f"No se encontró la cita con ID {appointment_id}",
            }

        # Verificar si ya está cancelada
        if appointment.get("estado") == "cancelada":
            return {
                **state,
                "context": "Esta cita ya está cancelada.",
            }

        # Si no está confirmado, preparar confirmación
        if not action_confirmed:
            return {
                **state,
                "action_type": "cancel_appointment",
                "action_data": {
                    "appointment_id": appointment_id,
                    "appointment": appointment,
                    "reason": entities.get("reason", ""),
                },
                "next_action": "request_confirmation",
                "context": "Preparando confirmación de cancelación...",
            }

        # Cancelar cita
        reason = entities.get("reason", "")
        result = cancel_appointment(appointment_id, reason)

        return {
            **state,
            "action_result": result,
            "context": result.get("message", "Cita cancelada"),
        }

    except Exception as e:
        logger.error(
            f"[{session_id}] Error in cancel_appointment_node: {e}", exc_info=True
        )
        return {
            **state,
            "error": str(e),
            "context": "Error al cancelar la cita",
        }
