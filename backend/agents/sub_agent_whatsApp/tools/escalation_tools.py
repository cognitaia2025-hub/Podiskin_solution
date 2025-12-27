"""
Escalation Tools - Herramientas de escalamiento
================================================

Tools que Maya puede usar para escalar dudas al administrador.
"""

import logging
from typing import Dict, Any
from langchain_core.tools import tool

from ..utils.escalation import create_pending_question, format_question_for_admin

logger = logging.getLogger(__name__)


@tool
def escalate_question_to_admin(
    patient_name: str,
    patient_phone: str,
    patient_chat_id: str,
    question: str,
    context: str = "",
) -> Dict[str, Any]:
    """
    Escala una pregunta al administrador cuando Maya no sabe la respuesta.

    Args:
        patient_name: Nombre del paciente
        patient_phone: Teléfono del paciente
        patient_chat_id: WhatsApp chat ID del paciente
        question: La pregunta que no se puede responder
        context: Contexto adicional de la conversación

    Returns:
        Diccionario con el resultado del escalamiento
    """
    logger.info(f"Escalando pregunta de {patient_name}: {question}")

    try:
        # Crear duda en BD
        duda_id = create_pending_question(
            paciente_chat_id=patient_chat_id,
            paciente_nombre=patient_name,
            paciente_telefono=patient_phone,
            duda=question,
            contexto=context,
        )

        # Formatear mensaje para admin
        admin_message = format_question_for_admin(
            duda_id=duda_id,
            paciente_nombre=patient_name,
            paciente_telefono=patient_phone,
            duda=question,
        )

        logger.info(f"Duda #{duda_id} escalada correctamente")

        return {
            "success": True,
            "duda_id": duda_id,
            "admin_message": admin_message,
            "patient_response": (
                "Disculpe, no tengo esa información pero déjeme consultarlo "
                "con el personal. Mientras me responden, ¿le puedo ayudar en "
                "algo más? ¿O le agendo una cita y el profesional le aclara "
                "su duda personalmente?"
            ),
        }

    except Exception as e:
        logger.error(f"Error escalando pregunta: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "patient_response": (
                "Disculpe, estoy teniendo problemas técnicos. "
                "Por favor llame al 686-108-3647."
            ),
        }
