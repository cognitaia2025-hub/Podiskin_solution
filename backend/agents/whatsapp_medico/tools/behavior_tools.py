"""
Behavior Tools
==============

Tools para obtener reglas de comportamiento activas y dinámicas.

Referencias:
- https://docs.langchain.com/oss/python/langgraph/workflows-agents#dynamic-prompts
"""

import logging
from db import get_pool

logger = logging.getLogger(__name__)

# ============================================================================
# FUNCIÓN: Get Active Behavior Rules
# ============================================================================

async def get_active_behavior_rules() -> list:
    """
    Obtiene reglas de comportamiento activas y aprobadas para inyectar al System Prompt.
    
    Returns:
        Lista de dicts con reglas: [
            {
                "id": int,
                "pattern": str,
                "correction_logic": str,
                "categoria": str,
                "prioridad": int
            }
        ]
    """
    pool = await get_pool()
    
    try:
        sql_query = """
            SELECT 
                id,
                pattern,
                correction_logic,
                categoria,
                prioridad
            FROM behavior_rules
            WHERE activo = true
            AND aprobado = true
            ORDER BY prioridad ASC, fecha_creacion DESC
            LIMIT 20
        """
        
        rows = await pool.fetch(sql_query)
        
        rules = [dict(row) for row in rows]
        
        logger.info(f"✅ [Behavior Tool] {len(rules)} reglas activas obtenidas")
        
        return rules
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo behavior rules desde DB: {e}", exc_info=True)
        # Retornar [] como fallback para no romper el agente
        return []


async def increment_behavior_rule_usage(rule_id: int):
    """Incrementa contador de uso de una regla."""
    pool = await get_pool()
    
    try:
        await pool.execute(
            "UPDATE behavior_rules SET veces_utilizada = veces_utilizada + 1, ultima_utilizacion = NOW() WHERE id = $1",
            rule_id
        )
    except Exception as e:
        logger.error(f"❌ Error incrementando uso de regla: {e}")
