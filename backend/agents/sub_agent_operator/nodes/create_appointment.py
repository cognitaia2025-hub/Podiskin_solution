"""
Nodo: Crear Cita
================

Maneja el flujo de creación de una nueva cita.
"""

import logging
from typing import Dict

from ..state import OperationsAgentState
from ..tools.action_tools import create_appointment
from ..tools.appointment_tools import check_availability

logger = logging.getLogger(__name__)


async def create_appointment_node(state: OperationsAgentState) -> Dict:
    """
    Crea una nueva cita.

    Flujo:
    1. Validar datos requeridos
    2. Verificar disponibilidad
    3. Mostrar confirmación
    4. Si está confirmado, crear cita

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con resultado de la acción
    """
    session_id = state.get("session_id", "unknown")
    entities = state.get("entities", {})
    action_confirmed = state.get("action_confirmed", False)

    logger.info(f"[{session_id}] Creating appointment...")

    try:
        # Extraer datos de entidades
        appointment_data = {
            "paciente_id": entities.get("patient_id"),
            "fecha": entities.get("date"),
            "hora": entities.get("time"),
            "duracion": entities.get("duration", 30),
            "tratamiento": entities.get("treatment"),
            "notas": entities.get("notes", ""),
        }

        # Validar datos requeridos
        required = ["paciente_id", "fecha", "hora", "tratamiento"]
        missing = [f for f in required if not appointment_data.get(f)]

        if missing:
            return {
                **state,
                "next_action": "request_missing_data",
                "context": f"Faltan datos: {', '.join(missing)}",
            }

        # Verificar disponibilidad
        is_available = check_availability(
            appointment_data["fecha"],
            appointment_data["hora"],
            appointment_data["duracion"],
        )

        if not is_available:
            return {
                **state,
                "context": "El horario no está disponible. Por favor elige otro.",
            }

        # Si no está confirmado, preparar confirmación
        if not action_confirmed:
            return {
                **state,
                "action_type": "create_appointment",
                "action_data": appointment_data,
                "next_action": "request_confirmation",
                "context": "Preparando confirmación de agendamiento...",
            }

        # Crear cita
        result = create_appointment(appointment_data)

        return {
            **state,
            "action_result": result,
            "context": result.get("message", "Cita creada"),
        }

    except Exception as e:
        logger.error(
            f"[{session_id}] Error in create_appointment_node: {e}", exc_info=True
        )
        return {
            **state,
            "error": str(e),
            "context": "Error al crear la cita",
        }
