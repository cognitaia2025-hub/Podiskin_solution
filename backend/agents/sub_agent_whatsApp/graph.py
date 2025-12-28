"""
Grafo Principal - Sub-Agente WhatsApp
======================================

Define el grafo de LangGraph que orquesta todo el flujo del sub-agente.
"""

import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver

from .state import WhatsAppAgentState
from .config import config
from .nodes import (
    classify_intent_node,
    retrieve_context_node,
    check_patient_node,
    handle_appointment_node,
    handle_query_node,
    handle_cancellation_node,
    escalate_to_human_node,
    generate_response_node,
    post_process_escalation_node,
)

logger = logging.getLogger(__name__)


# ============================================================================
# ROUTING FUNCTIONS
# ============================================================================


def route_by_intent(state: WhatsAppAgentState) -> str:
    """
    Enruta el flujo según la intención clasificada.

    Args:
        state: Estado actual del agente

    Returns:
        Nombre del siguiente nodo
    """
    intent = state.get("intent", "otro")
    confidence = state.get("confidence", 0.0)

    logger.info(
        f"[{state['conversation_id']}] Routing by intent: "
        f"{intent} (confidence: {confidence:.2f})"
    )

    # Si confianza baja, escalar a humano
    if confidence < config.intent_confidence_threshold:
        logger.warning(
            f"[{state['conversation_id']}] Low confidence ({confidence:.2f}), "
            f"escalating to human"
        )
        return "escalate"

    # Routing por intención
    intent_routing = {
        "agendar": "check_patient",
        "consulta": "retrieve",
        "cancelar": "handle_cancellation",
        "info": "handle_query",
        "emergencia": "generate",  # Maya responde directamente, no escala
    }

    next_node = intent_routing.get(intent, "generate")

    logger.info(f"[{state['conversation_id']}] Routing to: {next_node}")

    return next_node


def route_after_patient_check(state: WhatsAppAgentState) -> str:
    """
    Enruta después de verificar si es paciente.

    Args:
        state: Estado actual del agente

    Returns:
        Nombre del siguiente nodo
    """
    next_action = state.get("next_action", "")

    if next_action == "register_patient":
        # Es paciente nuevo, pero continuamos normalmente
        # El registro se hará como parte del proceso de agendamiento
        logger.info(
            f"[{state['conversation_id']}] New patient - continuing with appointment"
        )
        # No escalamos, continuamos normal

    # Continuar con agendamiento
    return "handle_appointment"


def route_after_action(state: WhatsAppAgentState) -> str:
    """
    Enruta después de ejecutar una acción (appointment, query, etc.).

    Args:
        state: Estado actual del agente

    Returns:
        Nombre del siguiente nodo
    """
    requires_human = state.get("requires_human", False)

    if requires_human:
        logger.info(f"[{state['conversation_id']}] Action requires human intervention")
        return "escalate"

    return "generate"


# ============================================================================
# CONSTRUCCIÓN DEL GRAFO
# ============================================================================


def create_whatsapp_graph(checkpointer=None) -> StateGraph:
    """
    Crea el grafo del sub-agente de WhatsApp.

    Args:
        checkpointer: Checkpointer para persistencia (opcional)

    Returns:
        Grafo compilado de LangGraph
    """
    logger.info("Creating WhatsApp agent graph...")

    # Crear grafo
    workflow = StateGraph(WhatsAppAgentState)

    # ========================================================================
    # AGREGAR NODOS
    # ========================================================================

    workflow.add_node("classify", classify_intent_node)
    workflow.add_node("retrieve", retrieve_context_node)
    workflow.add_node("check_patient", check_patient_node)
    workflow.add_node("handle_appointment", handle_appointment_node)
    workflow.add_node("handle_query", handle_query_node)
    workflow.add_node("handle_cancellation", handle_cancellation_node)
    workflow.add_node("escalate", escalate_to_human_node)
    workflow.add_node("generate", generate_response_node)
    workflow.add_node("post_process", post_process_escalation_node)

    # ========================================================================
    # DEFINIR FLUJO
    # ========================================================================

    # Punto de entrada
    workflow.set_entry_point("classify")

    # Routing condicional desde clasificación
    workflow.add_conditional_edges(
        "classify",
        route_by_intent,
        {
            "check_patient": "check_patient",
            "retrieve": "retrieve",
            "handle_cancellation": "handle_cancellation",
            "handle_query": "handle_query",
            "escalate": "escalate",
            "generate": "generate",
        },
    )

    # Routing después de verificar paciente
    workflow.add_conditional_edges(
        "check_patient",
        route_after_patient_check,
        {"handle_appointment": "handle_appointment", "generate": "generate"},
    )

    # Edges secuenciales
    workflow.add_edge("retrieve", "handle_query")

    # Routing después de acciones
    workflow.add_conditional_edges(
        "handle_appointment",
        route_after_action,
        {"generate": "generate", "escalate": "escalate"},
    )

    workflow.add_conditional_edges(
        "handle_query",
        route_after_action,
        {"generate": "generate", "escalate": "escalate"},
    )

    workflow.add_conditional_edges(
        "handle_cancellation",
        route_after_action,
        {"generate": "generate", "escalate": "escalate"},
    )

    # Edges finales
    workflow.add_edge("escalate", "generate")
    workflow.add_edge("generate", "post_process")
    workflow.add_edge("post_process", END)

    # ========================================================================
    # COMPILAR
    # ========================================================================

    if checkpointer:
        logger.info("Compiling graph with checkpointer...")
        app = workflow.compile(checkpointer=checkpointer)
    else:
        logger.info("Compiling graph without checkpointer...")
        app = workflow.compile()

    logger.info("WhatsApp agent graph created successfully")

    return app


# ============================================================================
# INSTANCIA GLOBAL DEL GRAFO
# ============================================================================

# Para persistencia, se recomienda usar PostgresSaver o MemorySaver
# En producción, usar PostgresSaver con la BD de la aplicación
# Para desarrollo/testing, usar MemorySaver

# Opción 1: Sin persistencia (para pruebas rápidas)
# checkpointer = None

# Opción 2: MemorySaver (para desarrollo - persiste solo en memoria)
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
logger.info("Using MemorySaver for checkpointing (development mode)")

# Opción 3: PostgresSaver (para producción - requiere async context manager)
# from langgraph.checkpoint.postgres import PostgresSaver
# import os
# database_url = os.getenv("DATABASE_URL")
# # Nota: PostgresSaver se debe usar con async context manager
# # Ver ejemplo en ejemplo de uso o en la documentación

# Crear grafo global
whatsapp_agent = create_whatsapp_graph(checkpointer=checkpointer)


# ============================================================================
# FUNCIONES DE EJECUCIÓN
# ============================================================================


async def run_agent(
    state: WhatsAppAgentState, thread_id: str = None
) -> WhatsAppAgentState:
    """
    Ejecuta el agente con un estado inicial.

    Args:
        state: Estado inicial del agente
        thread_id: ID del thread para persistencia (opcional)

    Returns:
        Estado final después de ejecutar el grafo
    """
    conversation_id = state.get("conversation_id", "unknown")

    logger.info(f"[{conversation_id}] Running WhatsApp agent...")

    try:
        # Configuración para el thread
        config_dict = {}
        if thread_id:
            config_dict = {"configurable": {"thread_id": thread_id}}

        # Ejecutar grafo
        result = await whatsapp_agent.ainvoke(state, config=config_dict)

        logger.info(f"[{conversation_id}] Agent execution completed successfully")

        return result

    except Exception as e:
        logger.error(
            f"[{conversation_id}] Error running agent: {str(e)}", exc_info=True
        )

        # Retornar estado con error
        return {
            **state,
            "error": str(e),
            "requires_human": True,
            "escalation_reason": f"Error en el agente: {str(e)}",
        }


async def stream_agent(state: WhatsAppAgentState, thread_id: str = None):
    """
    Ejecuta el agente en modo streaming.

    Args:
        state: Estado inicial del agente
        thread_id: ID del thread para persistencia (opcional)

    Yields:
        Eventos del grafo durante la ejecución
    """
    conversation_id = state.get("conversation_id", "unknown")

    logger.info(f"[{conversation_id}] Streaming WhatsApp agent...")

    try:
        # Configuración para el thread
        config_dict = {}
        if thread_id:
            config_dict = {"configurable": {"thread_id": thread_id}}

        # Stream del grafo
        async for event in whatsapp_agent.astream(state, config=config_dict):
            yield event

        logger.info(f"[{conversation_id}] Agent streaming completed")

    except Exception as e:
        logger.error(
            f"[{conversation_id}] Error streaming agent: {str(e)}", exc_info=True
        )
        raise


async def resume_agent_with_admin_reply(
    thread_id: str, admin_reply: str, ticket_id: int
) -> WhatsAppAgentState:
    """
    Reanuda el agente después de que el administrador ha respondido.

    Este método implementa el patrón de resume después de un escalamiento.
    Se usa cuando el grafo se pausó esperando respuesta del admin.

    Args:
        thread_id: ID del thread pausado
        admin_reply: Respuesta del administrador
        ticket_id: ID del ticket de escalamiento

    Returns:
        Estado final después de reanudar el grafo

    Ejemplo de uso:
        >>> # Cuando el admin responde vía webhook o UI:
        >>> result = await resume_agent_with_admin_reply(
        ...     thread_id="conv_123",
        ...     admin_reply="Sí, realizamos ese tratamiento",
        ...     ticket_id=456
        ... )
    """
    logger.info(f"Reanudando agente con respuesta de admin (ticket #{ticket_id})")

    try:
        # Configuración del thread
        config = {"configurable": {"thread_id": thread_id}}

        # Obtener estado actual del checkpointer
        current_state = whatsapp_agent.get_state(config)

        if not current_state or not current_state.values:
            logger.error(f"No se encontró estado para thread_id: {thread_id}")
            raise ValueError(f"Thread {thread_id} no encontrado en checkpointer")

        # Crear estado de reanudación con la respuesta del admin
        # Inyectamos los campos necesarios para que post_process_escalation
        # detecte que se está reanudando con respuesta del admin
        resume_state = {
            **current_state.values,
            "admin_reply": admin_reply,
            "escalation_ticket_id": ticket_id,
            "requires_human": False,  # Ya no requiere humano porque ya respondió
        }

        # Reanudar el grafo ejecutándolo con el estado actualizado
        # El checkpointer se encarga de mantener el historial
        result = await whatsapp_agent.ainvoke(resume_state, config=config)

        logger.info(f"Agente reanudado exitosamente (thread: {thread_id})")

        return result

    except Exception as e:
        logger.error(
            f"Error reanudando agente (thread: {thread_id}): {str(e)}", exc_info=True
        )
        raise


async def get_agent_state(thread_id: str) -> dict:
    """
    Obtiene el estado actual de un thread del agente.

    Útil para verificar si un agente está pausado esperando respuesta.

    Args:
        thread_id: ID del thread

    Returns:
        Estado actual del agente o None si no existe
    """
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state = whatsapp_agent.get_state(config)
        return state
    except Exception as e:
        logger.error(f"Error obteniendo estado del thread {thread_id}: {e}")
        return None
