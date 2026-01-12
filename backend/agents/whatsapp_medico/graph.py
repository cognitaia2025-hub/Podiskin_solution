"""
Grafo Principal del Agente WhatsApp
===================================

Define el flujo completo del agente usando LangGraph.

Versión actualizada con integración Twilio + LangGraph v1+:
- Router con filtros y behavior rules
- RAG Manager con búsqueda jerárquica (SQL → KB → Context)
- Generate Response con System Prompt dinámico
- Human Escalation con tickets
- Confidence-based routing
"""

import logging
from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .nodes import (
    # Nodos existentes
    sentiment_analyzer,
    rag_retriever,
    response_generator,
    human_guardrails,
    human_review_node,
    # Nuevos nodos
    node_router,
    node_rag_manager,
    node_generate_response,
    node_human_escalation,
)
from .config import checkpointer

logger = logging.getLogger(__name__)


def route_by_confidence(state: AgentState) -> str:
    """
    Enruta basado en confidence y requires_human.
    
    Flujo:
    - confidence >= 0.80 → generate_response_new
    - confidence < 0.80 → human_escalation
    - debe_escalar = True → human_escalation
    """
    if state.get('debe_escalar', False):
        return "human_escalation"
    
    confidence = state.get('confidence', 0.0)
    
    # Umbral de confianza desde env o default 0.80
    import os
    threshold = float(os.getenv('AGENT_CONFIDENCE_THRESHOLD', '0.80'))
    
    if confidence >= threshold:
        return "generate_response_new"
    else:
        logger.warning(f"⚠️ Confidence baja ({confidence:.2f}), escalando a humano")
        return "human_escalation"


def create_graph():
    """
    Crea y compila el grafo del agente WhatsApp.

    Flujo NUEVO (Twilio + LangGraph v1+):
    1. START → router (filtros + behavior rules)
    2. router → rag_manager (búsqueda jerárquica)
    3. rag_manager → [conditional] por confidence:
       - Alta (>=0.80) → generate_response_new
       - Baja (<0.80) → human_escalation
    4. generate_response_new → END
    5. human_escalation → END

    Flujo LEGACY (compatible con código existente):
    1. START → sentiment → retrieve → generate
    2. generate → guardrails → END o human_review

    Returns:
        Grafo compilado con checkpointer
    """
    logger.info("Creando grafo del agente WhatsApp con integración Twilio...")

    # Crear grafo
    workflow = StateGraph(AgentState)

    # ========================================================================
    # FLUJO NUEVO (Twilio + LangGraph v1+)
    # ========================================================================
    
    # Agregar nuevos nodos
    workflow.add_node("router", node_router)
    workflow.add_node("rag_manager", node_rag_manager)
    workflow.add_node("generate_response_new", node_generate_response)
    workflow.add_node("human_escalation", node_human_escalation)

    # ========================================================================
    # FLUJO LEGACY (mantener compatibilidad)
    # ========================================================================
    
    # Agregar nodos existentes
    workflow.add_node("sentiment", sentiment_analyzer)
    workflow.add_node("retrieve", rag_retriever)
    workflow.add_node("generate", response_generator)
    workflow.add_node("human_review", human_review_node)

    # ========================================================================
    # EDGES - FLUJO NUEVO (default)
    # ========================================================================
    
    # Flujo principal: router → rag_manager → conditional
    workflow.add_edge(START, "router")
    workflow.add_edge("router", "rag_manager")
    
    # Conditional edge basado en confidence
    workflow.add_conditional_edges(
        "rag_manager",
        route_by_confidence,
        {
            "generate_response_new": "generate_response_new",
            "human_escalation": "human_escalation"
        }
    )
    
    # Edges finales
    workflow.add_edge("generate_response_new", END)
    workflow.add_edge("human_escalation", END)

    # ========================================================================
    # EDGES - FLUJO LEGACY (para compatibilidad)
    # ========================================================================
    # Nota: El flujo legacy no se conecta al START por defecto
    # Se mantiene para uso futuro si es necesario
    
    workflow.add_edge("sentiment", "retrieve")
    workflow.add_edge("retrieve", "generate")
    
    # Edge condicional legacy
    workflow.add_conditional_edges(
        "generate",
        human_guardrails,
        {
            "responder": END,
            "escalar": "human_review",
        },
    )
    
    workflow.add_edge("human_review", END)

    # ========================================================================
    # COMPILAR
    # ========================================================================
    
    # Compilar con checkpointer para persistencia por thread_id
    graph = workflow.compile(checkpointer=checkpointer)

    logger.info("✅ Grafo compilado exitosamente con integración Twilio")
    logger.info("   Flujo principal: router → rag_manager → [confidence routing]")
    logger.info("   Flujo legacy: disponible para compatibilidad")

    return graph


# Instancia global del grafo
whatsapp_graph = create_graph()
