"""
Nodo: Verificar Paciente
=========================

Verifica si el contacto es un paciente existente.
"""

import logging
from typing import Dict

from ..state import WhatsAppAgentState
from ..utils import fetchrow

logger = logging.getLogger(__name__)


async def check_patient_node(state: WhatsAppAgentState) -> Dict:
    """
    Verifica si el contacto es un paciente existente.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con información del paciente
    """
    conversation_id = state["conversation_id"]
    contact_id = state["contact_id"]

    logger.info(f"[{conversation_id}] Checking if contact is a patient...")

    try:
        # Buscar paciente asociado al contacto
        query = """
        SELECT p.*
        FROM pacientes p
        WHERE p.id_contacto = %s
        """

        patient = await fetchrow(query, contact_id)

        if patient:
            patient_info = {
                "id": patient["id"],
                "nombre": f"{patient['primer_nombre']} {patient['primer_apellido']}",
                "telefono": patient["telefono_principal"],
                "email": patient["email"],
                "fecha_registro": (
                    patient.get("fecha_registro").isoformat()
                    if patient.get("fecha_registro")
                    else None
                ),
            }

            logger.info(f"[{conversation_id}] Patient found: {patient_info['nombre']}")

            return {
                **state,
                "patient_id": patient["id"],
                "patient_info": patient_info,
                "processing_stage": "handle_action",
            }
        else:
            logger.info(f"[{conversation_id}] No patient record found for this contact")

            return {
                **state,
                "patient_id": None,
                "patient_info": None,
                "next_action": "register_patient",
                "processing_stage": "handle_action",
            }

    except Exception as e:
        logger.error(
            f"[{conversation_id}] Error checking patient: {str(e)}", exc_info=True
        )

        return {
            **state,
            "patient_id": None,
            "patient_info": None,
            "error": f"Error verificando paciente: {str(e)}",
        }
