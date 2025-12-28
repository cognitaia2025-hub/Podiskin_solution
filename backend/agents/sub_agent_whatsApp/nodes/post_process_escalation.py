"""
Nodo: Post-Procesamiento de Escalamiento
=========================================

Detecta si se necesita escalar a humano y maneja el flujo de
interrupt/resume para esperar respuesta del administrador.

Implementa los patrones de LangGraph:
- interrupt(): Pausa el grafo hasta que llegue respuesta del admin
- Command(resume=...): Reanuda el flujo con la respuesta
- save_faq(): Aprende de las respuestas validadas
"""

import logging
from typing import Dict
from datetime import datetime
from langgraph.types import interrupt, Command

from ..state import WhatsAppAgentState
from ..tools.escalation_tools import (
    escalate_question_to_admin,
    get_admin_reply,
    save_faq_to_knowledge_base,
)
from ..utils.database import _get_connection, _put_connection

logger = logging.getLogger(__name__)


async def post_process_escalation_node(state: WhatsAppAgentState) -> Dict:
    """
    Post-procesa la respuesta generada para detectar si se necesita
    escalamiento o si se está reanudando después de respuesta del admin.

    Flujo de Escalamiento:
    1. Detecta necesidad de escalar (baja confianza, pregunta no respondida)
    2. Crea ticket de escalamiento en BD
    3. Notifica al admin vía WhatsApp
    4. Ejecuta interrupt() para pausar el grafo
    5. Espera respuesta del admin (puede tomar horas/días)
    6. Cuando admin responde, el flujo se reanuda automáticamente
    7. Guarda la Q&A en knowledge_base (aprendizaje)
    8. Envía respuesta al paciente

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con información de escalamiento o aprendizaje
    """
    conversation_id = state.get("conversation_id", "unknown")
    logger.info(f"[{conversation_id}] Post-procesando escalamiento...")

    try:
        # =====================================================================
        # CASO 1: Reanudación después de respuesta del admin
        # =====================================================================
        if state.get("admin_reply"):
            logger.info(
                f"[{conversation_id}] Reanudando flujo con respuesta del admin"
            )

            admin_reply = state["admin_reply"]
            ticket_id = state.get("escalation_ticket_id")

            # Obtener la pregunta original del ticket
            original_question = None
            if ticket_id:
                reply_data = get_admin_reply.invoke({"duda_id": ticket_id})
                if reply_data.get("success") and reply_data.get("has_reply"):
                    original_question = reply_data.get("pregunta")

            # Guardar en knowledge base (patrón de aprendizaje)
            if original_question and ticket_id:
                logger.info(
                    f"[{conversation_id}] Guardando FAQ aprendida (ticket #{ticket_id})"
                )

                save_result = save_faq_to_knowledge_base.invoke(
                    {
                        "pregunta": original_question,
                        "respuesta": admin_reply,
                        "duda_id": ticket_id,
                        "categoria": "escalamiento",
                        "validado": True,
                    }
                )

                if save_result.get("success"):
                    logger.info(
                        f"[{conversation_id}] FAQ guardada en KB #{save_result.get('kb_id')}"
                    )
                else:
                    logger.warning(
                        f"[{conversation_id}] No se pudo guardar FAQ: {save_result.get('error')}"
                    )

            # Registrar auditoría de reanudación
            _log_resume_audit(conversation_id, ticket_id, admin_reply)

            return {
                **state,
                "processing_stage": "complete",
                "requires_human": False,
                "escalation_reason": None,
            }

        # =====================================================================
        # CASO 2: Detección de necesidad de escalamiento
        # =====================================================================

        # Verificar si ya se marcó para escalamiento
        if state.get("requires_human"):
            reason = state.get("escalation_reason", "Razón no especificada")
            logger.info(f"[{conversation_id}] Escalamiento detectado: {reason}")

            # Obtener información del paciente
            patient_name = state.get("contact_name", "Paciente")
            patient_phone = state.get("whatsapp_number", "")
            patient_chat_id = state.get("conversation_id", "")

            # Obtener última pregunta del usuario
            messages = state.get("messages", [])
            user_question = ""
            for msg in reversed(messages):
                msg_content = msg.content if hasattr(msg, "content") else msg.get("content", "")
                msg_role = msg.role if hasattr(msg, "role") else msg.get("role", "")
                if msg_role == "user":
                    user_question = msg_content
                    break

            # Crear ticket de escalamiento
            escalation_result = escalate_question_to_admin.invoke(
                {
                    "patient_name": patient_name,
                    "patient_phone": patient_phone,
                    "patient_chat_id": patient_chat_id,
                    "question": user_question,
                    "context": reason,
                }
            )

            if not escalation_result.get("success"):
                logger.error(
                    f"[{conversation_id}] Error en escalamiento: {escalation_result.get('error')}"
                )
                return {
                    **state,
                    "processing_stage": "complete",
                    "error": f"Error en escalamiento: {escalation_result.get('error')}",
                }

            ticket_id = escalation_result.get("duda_id")
            logger.info(f"[{conversation_id}] Ticket de escalamiento creado: #{ticket_id}")

            # ===============================================================
            # INTERRUPT: Pausar el grafo hasta que llegue respuesta del admin
            # ===============================================================
            logger.info(
                f"[{conversation_id}] Ejecutando interrupt para esperar respuesta del admin"
            )

            # Guardar ticket_id en el estado para cuando se reanude
            updated_state = {
                **state,
                "escalation_ticket_id": ticket_id,
                "processing_stage": "waiting_admin",
            }

            # Enviar mensaje al paciente notificando que se escaló
            # (esto se hace en generate_response_node antes de llegar aquí)

            # INTERRUPT con identificador único del ticket
            # El grafo se pausará aquí y se guardará el estado
            # Cuando el admin responda, se reanudará desde este punto
            interrupt(f"waiting_admin_response:{ticket_id}")

            return updated_state

        # =====================================================================
        # CASO 3: Verificación de respuestas con baja confianza
        # =====================================================================

        # Detectar frases de incertidumbre en la respuesta generada
        messages = state.get("messages", [])
        if messages:
            last_response = None
            for msg in reversed(messages):
                msg_role = msg.role if hasattr(msg, "role") else msg.get("role", "")
                if msg_role == "assistant":
                    last_response = msg.content if hasattr(msg, "content") else msg.get("content", "")
                    break

            if last_response and _contains_uncertainty(last_response):
                logger.warning(
                    f"[{conversation_id}] Respuesta contiene incertidumbre, "
                    "considerando escalamiento automático"
                )

                # Aquí podríamos decidir escalar automáticamente o
                # solo marcarlo para revisión posterior
                # Por ahora, solo lo registramos
                _log_uncertainty_audit(conversation_id, last_response)

        # =====================================================================
        # CASO 4: Flujo normal sin escalamiento
        # =====================================================================
        logger.info(f"[{conversation_id}] No se requiere escalamiento, flujo completo")

        return {
            **state,
            "processing_stage": "complete",
        }

    except Exception as e:
        logger.error(
            f"[{conversation_id}] Error en post-procesamiento de escalamiento: {str(e)}",
            exc_info=True,
        )
        return {
            **state,
            "processing_stage": "complete",
            "error": f"Error en post-procesamiento: {str(e)}",
        }


def _contains_uncertainty(text: str) -> bool:
    """
    Detecta si el texto contiene frases de incertidumbre.

    Args:
        text: Texto a analizar

    Returns:
        True si contiene frases de incertidumbre
    """
    uncertainty_phrases = [
        "no estoy segur",
        "no tengo información",
        "no sé",
        "no puedo confirmar",
        "déjeme consultar",
        "consultarlo con",
        "verificar con",
        "no cuento con",
        "no tengo datos",
    ]

    text_lower = text.lower()
    return any(phrase in text_lower for phrase in uncertainty_phrases)


def _log_resume_audit(conversation_id: str, ticket_id: int, admin_reply: str):
    """Registra en audit_logs la reanudación del flujo."""
    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO audit_logs
                    (tabla, accion, registro_id, detalles, usuario, fecha)
                    VALUES ('conversaciones', 'resume_after_admin', %s, %s, 'whatsapp_agent', NOW())
                    """,
                    (
                        conversation_id,
                        f"Reanudado después de respuesta admin (ticket #{ticket_id})",
                    ),
                )
                conn.commit()
        finally:
            _put_connection(conn)
    except Exception as e:
        logger.error(f"Error logging resume audit: {e}")


def _log_uncertainty_audit(conversation_id: str, response: str):
    """Registra en audit_logs una respuesta con incertidumbre."""
    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO audit_logs
                    (tabla, accion, registro_id, detalles, usuario, fecha)
                    VALUES ('conversaciones', 'uncertainty_detected', %s, %s, 'whatsapp_agent', NOW())
                    """,
                    (conversation_id, f"Respuesta con incertidumbre: {response[:100]}"),
                )
                conn.commit()
        finally:
            _put_connection(conn)
    except Exception as e:
        logger.error(f"Error logging uncertainty audit: {e}")
