"""
Nodo: Consultar Citas
=====================

Consulta citas en la base de datos según los filtros especificados.
"""

import logging
from typing import Dict
from datetime import datetime, date

from ..state import OperationsAgentState
from ..tools.appointment_tools import search_appointments

logger = logging.getLogger(__name__)


async def query_appointments_node(state: OperationsAgentState) -> Dict:
    """
    Consulta citas en la base de datos.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con datos de citas recuperadas
    """
    session_id = state.get("session_id", "unknown")
    entities = state.get("entities", {})

    logger.info(f"[{session_id}] Querying appointments...")

    try:
        # Construir filtros desde entidades
        filters = {}

        # Filtro por fecha
        if entities.get("date"):
            filters["fecha"] = entities["date"]
        elif "hoy" in state.get("current_message", "").lower():
            filters["fecha"] = date.today().isoformat()
        elif "mañana" in state.get("current_message", "").lower():
            from datetime import timedelta

            tomorrow = date.today() + timedelta(days=1)
            filters["fecha"] = tomorrow.isoformat()

        # Filtro por paciente
        if entities.get("patient_id"):
            filters["paciente_id"] = entities["patient_id"]

        # Filtro por estado
        if entities.get("status"):
            filters["estado"] = entities["status"]
        elif "cancelada" in state.get("current_message", "").lower():
            filters["estado"] = "cancelada"
        elif "pendiente" in state.get("current_message", "").lower():
            filters["estado"] = "pendiente"

        # Filtro por tratamiento
        if entities.get("treatment"):
            filters["tratamiento"] = entities["treatment"]

        # Buscar citas
        logger.debug(f"[{session_id}] Filters: {filters}")
        appointments = search_appointments(filters=filters, limit=50)

        logger.info(f"[{session_id}] Found {len(appointments)} appointments")

        # Guardar en estado
        return {
            **state,
            "retrieved_data": {
                "type": "appointments",
                "count": len(appointments),
                "data": appointments,
                "filters": filters,
            },
            "context": f"Se encontraron {len(appointments)} citas.",
        }

    except Exception as e:
        logger.error(f"[{session_id}] Error querying appointments: {e}", exc_info=True)
        return {
            **state,
            "error": str(e),
            "context": "Ocurrió un error al consultar las citas.",
        }
