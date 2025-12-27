"""
Grafo Principal - Sub-Agente de Operaciones
===========================================

Define el grafo de LangGraph que orquesta el flujo del agente.
"""

import logging
from langgraph.graph import StateGraph, END

from .state import OperationsAgentState
from .config import config
from .nodes.classify_intent import classify_intent_node
from .nodes.generate_response import generate_response_node
from .nodes.query_appointments import query_appointments_node
from .nodes.query_patients import query_patients_node
from .nodes.create_appointment import create_appointment_node
from .nodes.reschedule_appointment import reschedule_appointment_node
from .nodes.cancel_appointment import cancel_appointment_node
from .nodes.update_patient import update_patient_node
from .nodes.execute_action import execute_action_node
from .nodes.clarify import clarify_node
from .nodes.generate_report import generate_report_node
from .nodes.complex_search import complex_search_node

logger = logging.getLogger(__name__)


# ============================================================================
# ROUTING FUNCTIONS
# ============================================================================


def route_by_intent(state: OperationsAgentState) -> str:
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
        f"[{state.get('session_id')}] Routing by intent: "
        f"{intent} (confidence: {confidence:.2f})"
    )

    # Si confianza baja, pedir clarificación
    if confidence < config.intent_confidence_threshold:
        logger.warning(f"[{state.get('session_id')}] Low confidence ({confidence:.2f})")
        return "clarify"

    # Routing por intención
    intent_routing = {
        "consulta_citas": "query_appointments",
        "consulta_pacientes": "query_patients",
        "agendar": "create_appointment",
        "reagendar": "reschedule_appointment",
        "cancelar": "cancel_appointment",
        "modificar_paciente": "update_patient",
        "reporte": "generate_report",
        "busqueda_compleja": "complex_search",
    }

    next_node = intent_routing.get(intent, "generate_response")

    logger.info(f"[{state.get('session_id')}] Routing to: {next_node}")

    return next_node


# ============================================================================
# NODOS PLACEHOLDER
# ============================================================================


async def query_appointments_node(state: OperationsAgentState):
    """Consulta citas en la BD."""
    logger.info(f"[{state.get('session_id')}] Querying appointments...")
    # TODO: Implementar
    return state


async def query_patients_node(state: OperationsAgentState):
    """Consulta pacientes en la BD."""
    logger.info(f"[{state.get('session_id')}] Querying patients...")
    # TODO: Implementar
    return state


async def create_appointment_node(state: OperationsAgentState):
    """Crea una nueva cita."""
    logger.info(f"[{state.get('session_id')}] Creating appointment...")
    # TODO: Implementar
    return state


async def reschedule_appointment_node(state: OperationsAgentState):
    """Reagenda una cita existente."""
    logger.info(f"[{state.get('session_id')}] Rescheduling appointment...")
    # TODO: Implementar
    return state


async def cancel_appointment_node(state: OperationsAgentState):
    """Cancela una cita."""
    logger.info(f"[{state.get('session_id')}] Cancelling appointment...")
    # TODO: Implementar
    return state


async def update_patient_node(state: OperationsAgentState):
    """Actualiza datos de un paciente."""
    logger.info(f"[{state.get('session_id')}] Updating patient...")
    # TODO: Implementar
    return state


async def generate_report_node(state: OperationsAgentState):
    """Genera un reporte operativo."""
    logger.info(f"[{state.get('session_id')}] Generating report...")
    # TODO: Implementar
    return state


async def complex_search_node(state: OperationsAgentState):
    """Realiza búsquedas complejas con filtros."""
    logger.info(f"[{state.get('session_id')}] Complex search...")
    # TODO: Implementar
    return state


async def clarify_node(state: OperationsAgentState):
    """Pide clarificación al usuario."""
    logger.info(f"[{state.get('session_id')}] Requesting clarification...")
    # TODO: Implementar
    return state


async def execute_action_node(state: OperationsAgentState):
    """Ejecuta la acción confirmada."""
    logger.info(f"[{state.get('session_id')}] Executing action...")
    # TODO: Implementar
    return state


# ============================================================================
# CREAR GRAFO
# ============================================================================


def create_operations_graph(checkpointer=None):
    """
    Crea el grafo del agente de operaciones.

    Args:
        checkpointer: Checkpointer para persistencia (opcional)

    Returns:
        Grafo compilado
    """
    logger.info("Creating operations agent graph...")

    # Crear grafo
    workflow = StateGraph(OperationsAgentState)

    # ========================================================================
    # AGREGAR NODOS AL GRAFO
    # ========================================================================

    workflow.add_node("classify", classify_intent_node)
    workflow.add_node("query_appointments", query_appointments_node)
    workflow.add_node("query_patients", query_patients_node)
    workflow.add_node("create_appointment", create_appointment_node)
    workflow.add_node("reschedule_appointment", reschedule_appointment_node)
    workflow.add_node("cancel_appointment", cancel_appointment_node)
    workflow.add_node("update_patient", update_patient_node)
    workflow.add_node("generate_report", generate_report_node)
    workflow.add_node("complex_search", complex_search_node)
    workflow.add_node("clarify", clarify_node)
    workflow.add_node("execute_action", execute_action_node)
    workflow.add_node("generate_response", generate_response_node)

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
            "query_appointments": "query_appointments",
            "query_patients": "query_patients",
            "create_appointment": "create_appointment",
            "reschedule_appointment": "reschedule_appointment",
            "cancel_appointment": "cancel_appointment",
            "update_patient": "update_patient",
            "generate_report": "generate_report",
            "complex_search": "complex_search",
            "clarify": "clarify",
            "generate_response": "generate_response",
        },
    )

    # Edges de consultas → generate_response
    workflow.add_edge("query_appointments", "generate_response")
    workflow.add_edge("query_patients", "generate_response")
    workflow.add_edge("generate_report", "generate_response")
    workflow.add_edge("complex_search", "generate_response")

    # Edges de acciones → execute_action → generate_response
    workflow.add_edge("create_appointment", "execute_action")
    workflow.add_edge("reschedule_appointment", "execute_action")
    workflow.add_edge("cancel_appointment", "execute_action")
    workflow.add_edge("update_patient", "execute_action")
    workflow.add_edge("execute_action", "generate_response")

    # Edges finales
    workflow.add_edge("clarify", "generate_response")
    workflow.add_edge("generate_response", END)

    # ========================================================================
    # COMPILAR
    # ========================================================================

    if checkpointer:
        logger.info("Compiling graph with checkpointer...")
        app = workflow.compile(checkpointer=checkpointer)
    else:
        logger.info("Compiling graph without checkpointer...")
        app = workflow.compile()

    logger.info("Operations agent graph created successfully")

    return app


# ============================================================================
# INSTANCIA GLOBAL DEL GRAFO
# ============================================================================

checkpointer = None
logger.info("Running without checkpointer (persistence disabled for now)")

# Crear grafo global
operations_agent = create_operations_graph(checkpointer=checkpointer)


# ============================================================================
# FUNCIONES DE EJECUCIÓN
# ============================================================================


async def run_agent(
    state: OperationsAgentState, thread_id: str = None
) -> OperationsAgentState:
    """
    Ejecuta el agente con un estado inicial.

    Args:
        state: Estado inicial del agente
        thread_id: ID del thread para persistencia (opcional)

    Returns:
        Estado final del agente
    """
    session_id = state.get("session_id", "unknown")
    logger.info(f"[{session_id}] Running operations agent...")

    try:
        config_dict = {"configurable": {"thread_id": thread_id}} if thread_id else {}

        result = await operations_agent.ainvoke(state, config=config_dict)

        logger.info(f"[{session_id}] Agent execution completed successfully")
        return result

    except Exception as e:
        logger.error(f"[{session_id}] Error running agent: {e}", exc_info=True)
        return {
            **state,
            "error": str(e),
            "response": "Lo siento, ocurrió un error al procesar tu solicitud.",
            "processing_stage": "error",
        }
