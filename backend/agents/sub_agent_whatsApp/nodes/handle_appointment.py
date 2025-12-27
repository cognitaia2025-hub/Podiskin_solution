"""
Nodo: Gestionar Agendamiento
=============================

Gestiona el proceso de agendamiento de citas.
"""

import logging
from typing import Dict

from ..state import WhatsAppAgentState
from ..utils import fetchrow

logger = logging.getLogger(__name__)


async def handle_appointment_node(state: WhatsAppAgentState) -> Dict:
    """
    Gestiona el proceso de agendamiento de citas.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con información de agendamiento
    """
    conversation_id = state["conversation_id"]
    entities = state.get("entities", {})
    patient_id = state.get("patient_id")

    logger.info(f"[{conversation_id}] Handling appointment request...")

    try:
        # Si no es paciente registrado, no escalamos
        # Maya pedirá los datos necesarios directamente
        if not patient_id:
            logger.info(f"[{conversation_id}] New patient - Maya will collect data")
            # Continuar normalmente, Maya pedirá nombre y datos

        # Verificar si tiene fecha y hora
        if "fecha" not in entities or "hora" not in entities:
            logger.info(
                f"[{conversation_id}] Missing date/time, " f"requesting from user"
            )
            return {**state, "next_action": "request_datetime", "requires_human": False}

        # Verificar disponibilidad
        # TODO: Implementar check de disponibilidad real
        # Por ahora, asumir disponible

        logger.info(
            f"[{conversation_id}] Appointment slot available: "
            f"{entities['fecha']} {entities['hora']}"
        )

        # Crear cita pendiente
        pending = {
            "fecha": entities["fecha"],
            "hora": entities["hora"],
            "tratamiento_id": 1,  # Default: Consulta General
            "podologo_id": 1,
            "disponible": True,
        }

        return {
            **state,
            "pending_appointment": pending,
            "next_action": "confirm_appointment",
            "requires_human": False,
        }

    except Exception as e:
        logger.error(
            f"[{conversation_id}] Error handling appointment: {str(e)}", exc_info=True
        )

        return {
            **state,
            "error": f"Error en agendamiento: {str(e)}",
            "requires_human": True,
        }
