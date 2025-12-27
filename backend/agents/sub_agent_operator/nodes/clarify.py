"""
Nodo: Clarificar
================

Pide clarificación al usuario cuando la confianza es baja.
"""

import logging
from typing import Dict

from ..state import OperationsAgentState

logger = logging.getLogger(__name__)


async def clarify_node(state: OperationsAgentState) -> Dict:
    """
    Pide clarificación al usuario.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con mensaje de clarificación
    """
    session_id = state.get("session_id", "unknown")
    intent = state.get("intent", "otro")
    confidence = state.get("confidence", 0.0)

    logger.info(
        f"[{session_id}] Requesting clarification "
        f"(intent: {intent}, confidence: {confidence:.2f})"
    )

    # Preparar mensaje de clarificación
    clarification_message = (
        "No estoy seguro de entender tu solicitud. "
        "¿Podrías ser más específico?\n\n"
        "Puedo ayudarte con:\n"
        "- Consultar citas y pacientes\n"
        "- Agendar, reagendar o cancelar citas\n"
        "- Actualizar datos de pacientes\n"
        "- Generar reportes operativos"
    )

    return {
        **state,
        "context": clarification_message,
        "next_action": "generate_response",
    }
