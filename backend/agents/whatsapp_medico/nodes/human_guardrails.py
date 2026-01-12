"""
Nodo: Human Guardrails
======================

Decide si escalar a humano o responder automáticamente.
Implementa HITL (Human-in-the-Loop).
"""

import logging
from typing import Literal
from langgraph.types import interrupt
from ..state import AgentState

logger = logging.getLogger(__name__)


def human_guardrails(state: AgentState) -> Literal["responder", "escalar"]:
    """
    Decide si la respuesta puede enviarse automáticamente o necesita humano.

    Criterios de escalamiento:
    - Sentimiento furioso o urgente
    - RAG score bajo (<0.7)
    - Paciente nuevo sin historial
    - Flag debe_escalar activado

    Args:
        state: Estado actual del agente

    Returns:
        "responder" para envío automático, "escalar" para HITL
    """
    sent = state.get("sentimiento")
    rag_docs = state.get("rag_docs", [])
    debe_escalar = state.get("debe_escalar", False)
    paciente_id = state.get("paciente_id")

    # Criterio 1: Flag explícito
    if debe_escalar:
        logger.info("Escalando: flag debe_escalar activado")
        return "escalar"

    # Criterio 2: Sentimiento crítico
    if sent and sent.sentimiento in ["furioso", "urgente"]:
        logger.info(f"Escalando: sentimiento {sent.sentimiento}")
        return "escalar"

    # Criterio 3: RAG insuficiente
    if not rag_docs or rag_docs[0].score < 0.7:
        score = rag_docs[0].score if rag_docs else 0
        logger.info(f"Escalando: RAG score bajo ({score:.2f})")
        return "escalar"

    # Criterio 4: Paciente nuevo con consulta compleja
    if not paciente_id and sent and sent.intencion in ["queja", "urgente"]:
        logger.info("Escalando: paciente nuevo con consulta compleja")
        return "escalar"

    # Todo OK, responder automáticamente
    logger.info("Guardrails OK: respuesta automática aprobada")
    return "responder"


async def human_review_node(state: AgentState) -> dict:
    """
    Nodo que se ejecuta cuando hay intervención humana.

    Espera la respuesta del humano y la procesa para auto-aprendizaje.

    Args:
        state: Estado actual del agente

    Returns:
        Dict con la respuesta humana procesada
    """
    logger.info("Esperando revisión humana...")

    # Si ya hay respuesta humana, procesarla
    if state.get("respuesta_humana"):
        logger.info("Respuesta humana recibida, procesando auto-aprendizaje")

        # La respuesta humana se guardará en aprendizajes_agente
        # mediante el tool save_rag_learning (se llama desde el endpoint)

        return {
            "messages": [{"role": "assistant", "content": state["respuesta_humana"]}]
        }

    # Si no hay respuesta, interrumpir para esperar al humano
    logger.info("Interrumpiendo para esperar respuesta humana")

    interrupt(
        {
            "needs_human": True,
            "chat_id": state["chat_id"],
            "pregunta": state["messages"][-1]["content"],
            "sugerencia_bot": state.get("respuesta_generada"),
            "sentimiento": (
                state.get("sentimiento").dict() if state.get("sentimiento") else None
            ),
            "paciente_id": state.get("paciente_id"),
        }
    )

    return state
