"""
Orchestrator Graph
Grafo LangGraph del Agente Padre Orquestador
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .state import OrchestratorState, create_initial_state
from .nodes import (
    classify_query,
    route_to_subagent,
    validate_response,
    build_response
)
from .config import CHECKPOINTER_TYPE


def create_orchestrator_graph():
    """
    Create the orchestrator graph
    
    Flow:
    1. classify_query - Determina si es simple o compleja
    2. route_to_subagent - Delega a SubAgente (si necesario)
    3. validate_response - Valida respuesta del SubAgente
    4. build_response - Construye respuesta final
    """
    
    # Create graph
    graph = StateGraph(OrchestratorState)
    
    # Add nodes
    graph.add_node("classify_query", classify_query)
    graph.add_node("route_to_subagent", route_to_subagent)
    graph.add_node("validate_response", validate_response)
    graph.add_node("build_response", build_response)
    
    # Add edges
    graph.add_edge(START, "classify_query")
    graph.add_edge("classify_query", "route_to_subagent")
    graph.add_edge("route_to_subagent", "validate_response")
    graph.add_edge("validate_response", "build_response")
    graph.add_edge("build_response", END)
    
    return graph


def compile_orchestrator_graph():
    """
    Compile the orchestrator graph with checkpointer
    """
    graph = create_orchestrator_graph()
    
    # Setup checkpointer based on config
    if CHECKPOINTER_TYPE == "memory":
        checkpointer = MemorySaver()
    else:
        # TODO: Add postgres/redis checkpointer
        checkpointer = MemorySaver()
    
    # Compile with checkpointer
    compiled = graph.compile(checkpointer=checkpointer)
    
    return compiled


# Create compiled graph instance
compiled_graph = compile_orchestrator_graph()


# Helper function to execute orchestrator
async def execute_orchestrator(
    function_name: str,
    args: dict,
    patient_id: str,
    user_id: str,
    appointment_id: str = None
) -> dict:
    """
    Execute the orchestrator for a function call
    
    Args:
        function_name: Name of the medical function
        args: Function arguments
        patient_id: Patient ID
        user_id: User ID (doctor)
        appointment_id: Appointment ID (optional)
        
    Returns:
        dict with response_data, response_message, response_status
    """
    # Create initial state
    initial_state = create_initial_state(
        function_name=function_name,
        args=args,
        patient_id=patient_id,
        user_id=user_id,
        appointment_id=appointment_id
    )
    
    # Execute graph
    result = compiled_graph.invoke(initial_state)
    
    # Return formatted response
    return {
        "data": result.get("response_data"),
        "message": result.get("response_message"),
        "status": result.get("response_status"),
        "execution_time_ms": result.get("execution_time_ms"),
        "messages": result.get("messages", []),
        "audit_log": result.get("audit_log", [])
    }


# Export for API endpoint
__all__ = [
    "compiled_graph",
    "execute_orchestrator",
    "create_initial_state"
]
