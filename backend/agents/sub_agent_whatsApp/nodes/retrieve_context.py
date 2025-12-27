"""
Nodo: Recuperar Contexto (RAG)
===============================

Recupera contexto relevante usando búsqueda semántica en pgvector.
"""

import logging
from typing import Dict

from ..state import WhatsAppAgentState
from ..config import config
from ..utils import fetch

logger = logging.getLogger(__name__)


async def retrieve_context_node(state: WhatsAppAgentState) -> Dict:
    """
    Recupera contexto relevante del vector store y base de datos.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con contexto recuperado
    """
    conversation_id = state["conversation_id"]
    contact_id = state["contact_id"]
    patient_id = state.get("patient_id")

    logger.info(f"[{conversation_id}] Retrieving context...")

    try:
        retrieved_context = []
        appointment_history = []

        # ====================================================================
        # 1. RECUPERAR CONVERSACIONES PREVIAS (RAG)
        # ====================================================================

        # Por ahora, obtener últimas conversaciones del contacto
        # TODO: Implementar búsqueda semántica con pgvector cuando esté listo

        query = """
        SELECT m.contenido, m.rol, m.fecha_envio
        FROM mensajes m
        JOIN conversaciones c ON m.id_conversacion = c.id
        WHERE c.id_contacto = %s
          AND c.id != %s
        ORDER BY m.fecha_envio DESC
        LIMIT %s
        """

        previous_messages = await fetch(
            query, contact_id, int(conversation_id), config.rag_k
        )

        for msg in previous_messages:
            retrieved_context.append(
                {
                    "content": f"{msg['rol']}: {msg['contenido']}",
                    "score": 1.0,  # Placeholder
                    "metadata": {"timestamp": msg["fecha_envio"].isoformat()},
                }
            )

        logger.debug(
            f"[{conversation_id}] Retrieved {len(retrieved_context)} "
            f"previous messages"
        )

        # ====================================================================
        # 2. OBTENER HISTORIAL DE CITAS SI ES PACIENTE
        # ====================================================================

        if patient_id:
            query = """
            SELECT 
                c.id,
                c.fecha_hora,
                c.estado,
                c.tipo_servicio as tratamiento
            FROM citas c
            WHERE c.id_paciente = %s
            ORDER BY c.fecha_hora DESC
            LIMIT 5
            """

            appointments = await fetch(query, patient_id)

            for apt in appointments:
                appointment_history.append(
                    {
                        "id": apt["id"],
                        "fecha_hora": apt["fecha_hora_inicio"].isoformat(),
                        "tratamiento": apt["tratamiento"] or "Consulta General",
                        "estado": apt["estado"],
                    }
                )

            logger.debug(
                f"[{conversation_id}] Retrieved {len(appointment_history)} "
                f"appointments"
            )

        # ====================================================================
        # 3. ACTUALIZAR ESTADO
        # ====================================================================

        return {
            **state,
            "retrieved_context": retrieved_context,
            "appointment_history": appointment_history,
            "processing_stage": "handle_action",
        }

    except Exception as e:
        logger.error(
            f"[{conversation_id}] Error retrieving context: {str(e)}", exc_info=True
        )

        # En caso de error, continuar sin contexto
        return {
            **state,
            "retrieved_context": [],
            "appointment_history": [],
            "processing_stage": "handle_action",
            "error": f"Error recuperando contexto: {str(e)}",
        }
