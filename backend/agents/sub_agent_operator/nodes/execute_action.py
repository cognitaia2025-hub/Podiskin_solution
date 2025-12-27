"""
Nodo: Ejecutar Acción
=====================

Ejecuta acciones confirmadas por el usuario.
"""

import logging
from typing import Dict

from ..state import OperationsAgentState

logger = logging.getLogger(__name__)


async def execute_action_node(state: OperationsAgentState) -> Dict:
    """
    Ejecuta la acción confirmada.

    Este nodo es un paso intermedio que marca que la acción
    fue confirmada y permite que el nodo específico la ejecute.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado marcando acción como confirmada
    """
    session_id = state.get("session_id", "unknown")
    action_type = state.get("action_type")

    logger.info(f"[{session_id}] Executing action: {action_type}")

    # Marcar como confirmada para que el nodo específico ejecute
    return {
        **state,
        "action_confirmed": True,
        "context": f"Ejecutando {action_type}...",
    }
