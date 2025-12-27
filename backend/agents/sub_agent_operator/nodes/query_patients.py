"""
Nodo: Consultar Pacientes
=========================

Consulta pacientes en la base de datos.
"""

import logging
from typing import Dict

from ..state import OperationsAgentState
from ..tools.patient_tools import search_patients, get_patient_history

logger = logging.getLogger(__name__)


async def query_patients_node(state: OperationsAgentState) -> Dict:
    """
    Consulta pacientes en la base de datos.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con datos de pacientes recuperados
    """
    session_id = state.get("session_id", "unknown")
    entities = state.get("entities", {})
    current_message = state.get("current_message", "")

    logger.info(f"[{session_id}] Querying patients...")

    try:
        # Determinar tipo de consulta
        query_text = None
        filters = {}
        include_history = False

        # Buscar por nombre o teléfono
        if entities.get("patient_name"):
            query_text = entities["patient_name"]

        # Detectar si se pide historial
        if (
            "historial" in current_message.lower()
            or "citas de" in current_message.lower()
        ):
            include_history = True

        # Buscar pacientes
        logger.debug(f"[{session_id}] Query: {query_text}, Filters: {filters}")
        patients = search_patients(query=query_text, filters=filters, limit=50)

        logger.info(f"[{session_id}] Found {len(patients)} patients")

        # Si se encontró un solo paciente y se pide historial, obtenerlo
        history = None
        if include_history and len(patients) == 1:
            patient_id = patients[0]["id"]
            history = get_patient_history(patient_id, limit=10)
            logger.info(
                f"[{session_id}] Retrieved history for patient {patient_id}: {len(history)} appointments"
            )

        # Guardar en estado
        retrieved_data = {
            "type": "patients",
            "count": len(patients),
            "data": patients,
            "query": query_text,
        }

        if history:
            retrieved_data["history"] = history

        context = f"Se encontraron {len(patients)} pacientes."
        if history:
            context += f" Historial: {len(history)} citas."

        return {
            **state,
            "retrieved_data": retrieved_data,
            "context": context,
        }

    except Exception as e:
        logger.error(f"[{session_id}] Error querying patients: {e}", exc_info=True)
        return {
            **state,
            "error": str(e),
            "context": "Ocurrió un error al consultar los pacientes.",
        }
