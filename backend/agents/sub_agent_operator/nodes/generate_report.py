"""
Nodo: Generar Reporte
=====================

Genera reportes operativos.
"""

import logging
from typing import Dict

from ..state import OperationsAgentState
from ..tools.report_tools import generate_appointment_stats, generate_patient_stats

logger = logging.getLogger(__name__)


async def generate_report_node(state: OperationsAgentState) -> Dict:
    """
    Genera un reporte operativo.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con datos del reporte
    """
    session_id = state.get("session_id", "unknown")
    entities = state.get("entities", {})
    current_message = state.get("current_message", "").lower()

    logger.info(f"[{session_id}] Generating report...")

    try:
        # Determinar tipo de reporte
        report_data = {}

        if "cita" in current_message or "agenda" in current_message:
            # Reporte de citas
            start_date = entities.get("start_date")
            end_date = entities.get("end_date")

            stats = generate_appointment_stats(start_date, end_date)
            report_data = {"type": "appointments", "data": stats}

        elif "paciente" in current_message:
            # Reporte de pacientes
            stats = generate_patient_stats()
            report_data = {"type": "patients", "data": stats}

        else:
            # Reporte general
            appointment_stats = generate_appointment_stats()
            patient_stats = generate_patient_stats()

            report_data = {
                "type": "general",
                "appointments": appointment_stats,
                "patients": patient_stats,
            }

        return {
            **state,
            "retrieved_data": report_data,
            "context": "Reporte generado exitosamente",
        }

    except Exception as e:
        logger.error(f"[{session_id}] Error generating report: {e}", exc_info=True)
        return {
            **state,
            "error": str(e),
            "context": "Error al generar el reporte",
        }
