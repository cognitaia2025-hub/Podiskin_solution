"""
Escalation Tools - Herramientas de escalamiento
================================================

Tools que Maya puede usar para escalar dudas al administrador.
Incluye funcionalidad de aprendizaje (save_faq) y recuperación de respuestas.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_core.tools import tool

from ..utils.escalation import create_pending_question, format_question_for_admin
from ..utils.database import _get_connection, _put_connection
from .knowledge_tools import save_to_knowledge_base

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


@tool
def get_admin_reply(duda_id: int) -> Dict[str, Any]:
    """
    Obtiene la respuesta del administrador para una duda escalada.

    Esta función se usa para reanudar el flujo después de que el
    administrador ha respondido a una pregunta escalada.

    Args:
        duda_id: ID de la duda escalada

    Returns:
        Diccionario con la respuesta del admin o estado pendiente
    """
    logger.info(f"Consultando respuesta de admin para duda #{duda_id}")

    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, duda, respuesta, estado, 
                           fecha_creacion, fecha_respuesta,
                           respondido_por
                    FROM dudas_pendientes
                    WHERE id = %s
                    """,
                    (duda_id,),
                )
                row = cur.fetchone()
        finally:
            _put_connection(conn)

        if not row:
            return {"success": False, "error": f"Duda #{duda_id} no encontrada"}

        duda_id, pregunta, respuesta, estado, fecha_creacion, fecha_respuesta, admin = (
            row
        )

        if estado == "respondida" and respuesta:
            logger.info(f"Respuesta encontrada para duda #{duda_id}")
            return {
                "success": True,
                "has_reply": True,
                "duda_id": duda_id,
                "pregunta": pregunta,
                "respuesta": respuesta,
                "admin": admin,
                "fecha_respuesta": (
                    fecha_respuesta.isoformat() if fecha_respuesta else None
                ),
            }
        else:
            logger.info(f"Duda #{duda_id} aún pendiente")
            return {
                "success": True,
                "has_reply": False,
                "duda_id": duda_id,
                "estado": estado,
                "message": "La pregunta aún está pendiente de respuesta",
            }

    except Exception as e:
        logger.error(f"Error obteniendo respuesta de admin: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@tool
def save_faq_to_knowledge_base(
    pregunta: str,
    respuesta: str,
    duda_id: Optional[int] = None,
    categoria: Optional[str] = None,
    validado: bool = True,
) -> Dict[str, Any]:
    """
    Guarda una pregunta y respuesta en la base de conocimiento.

    Esta función implementa el patrón de "aprendizaje" permitiendo
    que las respuestas del admin se guarden automáticamente para
    futuras consultas similares.

    Args:
        pregunta: La pregunta original del usuario
        respuesta: La respuesta proporcionada por el admin
        duda_id: ID de la duda original (para auditoría)
        categoria: Categoría opcional (ej: "tratamientos", "precios")
        validado: Si la respuesta ha sido validada por un humano

    Returns:
        Diccionario con el resultado de guardar en KB
    """
    logger.info(f"Guardando FAQ en knowledge base: {pregunta[:50]}...")

    try:
        # Usar la función existente de knowledge_tools (no es un @tool, es función regular)
        # Por eso se llama directamente sin .invoke()
        kb_id = save_to_knowledge_base(pregunta, respuesta, categoria)

        # Registrar auditoría y actualizar duda como aprendida
        # Usamos una sola conexión para todas las operaciones relacionadas
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                # Actualizar la duda como aprendida
                if duda_id:
                    cur.execute(
                        """
                        UPDATE dudas_pendientes
                        SET aprendida = TRUE,
                            fecha_aprendizaje = NOW()
                        WHERE id = %s
                        """,
                        (duda_id,),
                    )

                # Registrar en audit_logs
                cur.execute(
                    """
                    INSERT INTO audit_logs 
                    (tabla, accion, registro_id, detalles, usuario)
                    VALUES ('knowledge_base', 'insert', %s, %s, 'whatsapp_agent')
                    """,
                    (
                        kb_id,
                        f"FAQ aprendida desde duda #{duda_id}" if duda_id else "FAQ manual",
                    ),
                )

                conn.commit()
        finally:
            _put_connection(conn)

        logger.info(f"FAQ guardada exitosamente en KB #{kb_id}")

        return {
            "success": True,
            "kb_id": kb_id,
            "message": f"Pregunta guardada en base de conocimiento (ID: {kb_id})",
            "validado": validado,
        }

    except Exception as e:
        logger.error(f"Error guardando FAQ en KB: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
