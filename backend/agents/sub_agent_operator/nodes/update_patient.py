"""
Nodo: Actualizar Paciente
=========================

Maneja el flujo de actualización de datos de paciente.
"""

import logging
from typing import Dict

from ..state import OperationsAgentState
from ..tools.patient_action_tools import update_patient
from ..tools.patient_tools import get_patient_by_id

logger = logging.getLogger(__name__)


async def update_patient_node(state: OperationsAgentState) -> Dict:
    """
    Actualiza datos de un paciente.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con resultado de la acción
    """
    session_id = state.get("session_id", "unknown")
    entities = state.get("entities", {})
    action_confirmed = state.get("action_confirmed", False)

    logger.info(f"[{session_id}] Updating patient...")

    try:
        # Obtener ID del paciente
        patient_id = entities.get("patient_id")

        if not patient_id:
            return {
                **state,
                "context": "Necesito el ID del paciente para actualizar.",
            }

        # Buscar paciente
        patient = get_patient_by_id(patient_id)

        if not patient:
            return {
                **state,
                "context": f"No se encontró el paciente con ID {patient_id}",
            }

        # Preparar actualizaciones
        updates = {}

        if entities.get("telefono"):
            updates["telefono"] = entities["telefono"]

        if entities.get("email"):
            updates["email"] = entities["email"]

        if entities.get("direccion"):
            updates["direccion"] = entities["direccion"]

        if entities.get("notas"):
            updates["notas"] = entities["notas"]

        if not updates:
            return {
                **state,
                "context": "No se especificaron cambios para actualizar.",
            }

        # Si no está confirmado, preparar confirmación
        if not action_confirmed:
            return {
                **state,
                "action_type": "update_patient",
                "action_data": {
                    "patient_id": patient_id,
                    "patient": patient,
                    "updates": updates,
                },
                "next_action": "request_confirmation",
                "context": "Preparando confirmación de actualización...",
            }

        # Actualizar paciente
        result = update_patient(patient_id, updates)

        return {
            **state,
            "action_result": result,
            "context": result.get("message", "Paciente actualizado"),
        }

    except Exception as e:
        logger.error(f"[{session_id}] Error in update_patient_node: {e}", exc_info=True)
        return {
            **state,
            "error": str(e),
            "context": "Error al actualizar el paciente",
        }
