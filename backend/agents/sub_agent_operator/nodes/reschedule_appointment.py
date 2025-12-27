"""
Nodo: Reagendar Cita
====================

Maneja el flujo de reagendamiento de una cita existente.
"""

import logging
from typing import Dict

from ..state import OperationsAgentState
from ..tools.action_tools import update_appointment
from ..tools.appointment_tools import check_availability, get_appointment_by_id

logger = logging.getLogger(__name__)


async def reschedule_appointment_node(state: OperationsAgentState) -> Dict:
    """
    Reagenda una cita existente.

    Flujo:
    1. Buscar cita original
    2. Verificar nueva disponibilidad
    3. Mostrar confirmación
    4. Si está confirmado, actualizar cita

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con resultado de la acción
    """
    session_id = state.get("session_id", "unknown")
    entities = state.get("entities", {})
    action_confirmed = state.get("action_confirmed", False)

    logger.info(f"[{session_id}] Rescheduling appointment...")

    try:
        # Obtener ID de la cita
        appointment_id = entities.get("appointment_id")

        if not appointment_id:
            return {
                **state,
                "context": "Necesito el ID de la cita para reagendar.",
            }

        # Buscar cita original
        original = get_appointment_by_id(appointment_id)

        if not original:
            return {
                **state,
                "context": f"No se encontró la cita con ID {appointment_id}",
            }

        # Preparar actualizaciones
        updates = {}

        if entities.get("date"):
            updates["fecha"] = entities["date"]

        if entities.get("time"):
            updates["hora"] = entities["time"]

        if entities.get("duration"):
            updates["duracion"] = entities["duration"]

        if not updates:
            return {
                **state,
                "context": "No se especificaron cambios para reagendar.",
            }

        # Verificar disponibilidad si cambia fecha/hora
        if "fecha" in updates or "hora" in updates:
            new_fecha = updates.get("fecha", original["fecha"])
            new_hora = updates.get("hora", original["hora"])
            duracion = updates.get("duracion", original["duracion"])

            is_available = check_availability(new_fecha, new_hora, duracion)

            if not is_available:
                return {
                    **state,
                    "context": "El nuevo horario no está disponible.",
                }

        # Si no está confirmado, preparar confirmación
        if not action_confirmed:
            return {
                **state,
                "action_type": "reschedule_appointment",
                "action_data": {
                    "appointment_id": appointment_id,
                    "original": original,
                    "updates": updates,
                },
                "next_action": "request_confirmation",
                "context": "Preparando confirmación de reagendamiento...",
            }

        # Actualizar cita
        result = update_appointment(appointment_id, updates)

        return {
            **state,
            "action_result": result,
            "context": result.get("message", "Cita reagendada"),
        }

    except Exception as e:
        logger.error(
            f"[{session_id}] Error in reschedule_appointment_node: {e}", exc_info=True
        )
        return {
            **state,
            "error": str(e),
            "context": "Error al reagendar la cita",
        }
