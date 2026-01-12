"""
Tools del Agente WhatsApp
=========================

Exporta todas las herramientas disponibles.
"""

# Tools existentes
from .save_rag_learning import save_rag_learning
from .query_paciente import query_paciente_data

# Tools especializadas - SQL (Prioridad 1)
from .sql_tools import (
    consultar_tratamientos_sql,
    consultar_horarios_sql,
    consultar_citas_sql,
    calcular_disponibilidad
)

# Tools especializadas - KB (Prioridad 2)
from .kb_tools import (
    buscar_knowledge_base_validada,
    registrar_feedback_kb
)

# Tools especializadas - Context (Prioridad 3)
from .context_tools import (
    buscar_conversaciones_previas,
    guardar_resumen_conversacion
)

# Tools auxiliares
from .filter_tools import check_filters
from .behavior_tools import (
    get_active_behavior_rules,
    increment_behavior_rule_usage
)

__all__ = [
    # Existentes
    "save_rag_learning",
    "query_paciente_data",
    # SQL Tools
    "consultar_tratamientos_sql",
    "consultar_horarios_sql",
    "consultar_citas_sql",
    "calcular_disponibilidad",
    # KB Tools
    "buscar_knowledge_base_validada",
    "registrar_feedback_kb",
    # Context Tools
    "buscar_conversaciones_previas",
    "guardar_resumen_conversacion",
    # Auxiliares
    "check_filters",
    "get_active_behavior_rules",
    "increment_behavior_rule_usage"
]
