"""
Nodo: Búsqueda Compleja
=======================

Realiza búsquedas complejas con múltiples filtros.
"""

import logging
from typing import Dict

from ..state import OperationsAgentState
from ..tools.appointment_tools import search_appointments
from ..tools.patient_tools import search_patients

logger = logging.getLogger(__name__)


async def complex_search_node(state: OperationsAgentState) -> Dict:
    """
    Realiza búsquedas complejas con múltiples filtros.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con resultados de búsqueda
    """
    session_id = state.get("session_id", "unknown")
    entities = state.get("entities", {})

    logger.info(f"[{session_id}] Complex search...")

    try:
        # Construir filtros complejos
        filters = {}

        # Filtros de citas
        if entities.get("date"):
            filters["fecha"] = entities["date"]

        if entities.get("status"):
            filters["estado"] = entities["status"]

        if entities.get("treatment"):
            filters["tratamiento"] = entities["treatment"]

        if entities.get("patient_id"):
            filters["paciente_id"] = entities["patient_id"]

        # Realizar búsqueda
        results = search_appointments(filters=filters, limit=100)

        logger.info(f"[{session_id}] Found {len(results)} results")

        return {
            **state,
            "retrieved_data": {
                "type": "complex_search",
                "count": len(results),
                "data": results,
                "filters": filters,
            },
            "context": f"Se encontraron {len(results)} resultados.",
        }

    except Exception as e:
        logger.error(f"[{session_id}] Error in complex search: {e}", exc_info=True)
        return {
            **state,
            "error": str(e),
            "context": "Error en la búsqueda compleja",
        }
