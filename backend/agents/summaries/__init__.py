"""
Summaries SubAgent - SubAgente de Resúmenes
Genera resúmenes de consultas y búsqueda semántica en historial
"""

from .graph import compiled_graph, execute_summaries, create_initial_summary_state
from .state import SummaryState
from .config import SUMMARY_TEMPLATES

__all__ = [
    "compiled_graph",
    "execute_summaries",
    "create_initial_summary_state",
    "SummaryState",
    "SUMMARY_TEMPLATES"
]
