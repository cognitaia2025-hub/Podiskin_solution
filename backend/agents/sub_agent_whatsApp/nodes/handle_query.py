"""
Nodo: Gestionar Consultas
==========================

Responde consultas sobre tratamientos, precios, etc.
"""

import logging
from typing import Dict

from ..state import WhatsAppAgentState

logger = logging.getLogger(__name__)


async def handle_query_node(state: WhatsAppAgentState) -> Dict:
    """
    Gestiona consultas sobre tratamientos, precios, etc.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado
    """
    conversation_id = state["conversation_id"]

    logger.info(f"[{conversation_id}] Handling query...")

    # Por ahora, solo marcar que se manejó la consulta
    # El LLM generará la respuesta basándose en el contexto

    return {
        **state,
        "next_action": "provide_info",
        "requires_human": False,
        "processing_stage": "generate",
    }
