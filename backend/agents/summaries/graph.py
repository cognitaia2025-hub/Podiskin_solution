"""
Summaries SubAgent Graph
Grafo LangGraph del SubAgente de Resúmenes
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .state import SummaryState, create_initial_summary_state
from .nodes import (
    fetch_patient_data,
    search_history,
    generate_summary,
    validate_summary,
    build_response
)
from .config import CHECKPOINTER_TYPE


def create_summary_graph():
    """
    Create the summaries subagent graph
    
    Flow:
    1. fetch_patient_data - Obtiene datos del paciente de DB
    2. search_history - Búsqueda semántica (si aplica)
    3. generate_summary - Genera resumen con LLM
    4. validate_summary - Valida calidad del resumen
    5. build_response - Construye respuesta final
    """
    
    # Create graph
    graph = StateGraph(SummaryState)
    
    # Add nodes
    graph.add_node("fetch_patient_data", fetch_patient_data)
    graph.add_node("search_history", search_history)
    graph.add_node("generate_summary", generate_summary)
    graph.add_node("validate_summary", validate_summary)
    graph.add_node("build_response", build_response)
    
    # Add edges
    graph.add_edge(START, "fetch_patient_data")
    graph.add_edge("fetch_patient_data", "search_history")
    graph.add_edge("search_history", "generate_summary")
    graph.add_edge("generate_summary", "validate_summary")
    graph.add_edge("validate_summary", "build_response")
    graph.add_edge("build_response", END)
    
    return graph


def compile_summary_graph():
    """
    Compile the summary graph with checkpointer
    """
    graph = create_summary_graph()
    
    # Setup checkpointer
    if CHECKPOINTER_TYPE == "memory":
        checkpointer = MemorySaver()
    else:
        # TODO: Add postgres/redis checkpointer
        checkpointer = MemorySaver()
    
    # Compile with checkpointer
    compiled = graph.compile(checkpointer=checkpointer)
    
    return compiled


# Create compiled graph instance
compiled_graph = compile_summary_graph()


# Helper function to execute summaries agent
async def execute_summaries(
    function_name: str,
    args: dict,
    patient_id: str,
    user_id: str,
    appointment_id: str = None,
    context: dict = None
) -> dict:
    """
    Execute the summaries subagent
    
    Args:
        function_name: 'generate_summary' or 'search_patient_history'
        args: Function arguments
        patient_id: Patient ID
        user_id: User ID
        appointment_id: Appointment ID (optional)
        context: Additional context from orchestrator
        
    Returns:
        dict with response data, message, status
    """
    # Create initial state
    initial_state = create_initial_summary_state(
        function_name=function_name,
        args=args,
        patient_id=patient_id,
        user_id=user_id,
        appointment_id=appointment_id,
        context=context
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


# Export for orchestrator
__all__ = [
    "compiled_graph",
    "execute_summaries",
    "create_initial_summary_state"
]
