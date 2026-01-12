"""
Grafo Principal del Agente WhatsApp
===================================

Define el flujo completo del agente usando LangGraph.
"""

import logging
from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .nodes import (
    sentiment_analyzer,
    rag_retriever,
    response_generator,
    human_guardrails,
    human_review_node,
)
from .config import checkpointer

logger = logging.getLogger(__name__)


def create_graph():
    """
    Crea y compila el grafo del agente WhatsApp.

    Flujo:
    1. START → sentiment (analiza sentimiento)
    2. sentiment → retrieve (busca RAG)
    3. retrieve → generate (genera respuesta)
    4. generate → guardrails (decide si escalar)
    5a. guardrails → END (respuesta automática)
    5b. guardrails → human_review → END (HITL)

    Returns:
        Grafo compilado con checkpointer
    """
    logger.info("Creando grafo del agente WhatsApp...")

    # Crear grafo
    workflow = StateGraph(AgentState)

    # Agregar nodos
    workflow.add_node("sentiment", sentiment_analyzer)
    workflow.add_node("retrieve", rag_retriever)
    workflow.add_node("generate", response_generator)
    workflow.add_node("human_review", human_review_node)

    # Definir flujo lineal
    workflow.add_edge(START, "sentiment")
    workflow.add_edge("sentiment", "retrieve")
    workflow.add_edge("retrieve", "generate")

    # Edge condicional: decide si escalar o responder
    workflow.add_conditional_edges(
        "generate",
        human_guardrails,
        {
            "responder": END,  # Respuesta automática
            "escalar": "human_review",  # Necesita humano
        },
    )

    # Después de revisión humana, terminar
    workflow.add_edge("human_review", END)

    # Compilar con checkpointer para persistencia
    graph = workflow.compile(checkpointer=checkpointer)

    logger.info("✅ Grafo compilado exitosamente")

    return graph


# Instancia global del grafo
whatsapp_graph = create_graph()
