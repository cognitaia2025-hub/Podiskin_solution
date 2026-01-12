"""
Node Router
===========

Primer nodo: Aplica filtros y obtiene behavior rules.

Referencias:
- https://docs.langchain.com/oss/python/langgraph/workflows-agents#nodes
"""

import logging
from typing import Dict, Any

from ..state import AgentState
from ..tools.filter_tools import check_filters
from ..tools.behavior_tools import get_active_behavior_rules

logger = logging.getLogger(__name__)


async def node_router(state: AgentState) -> Dict[str, Any]:
    """
    Nodo inicial: Aplica filtros y obtiene reglas de comportamiento.
    
    Flujo:
    1. Extraer contact_id del state
    2. Llamar a check_filters() para validar
    3. Si blocked=True, marcar para rechazo
    4. Obtener behavior_rules activas
    5. Guardar reglas en state
    6. Retornar state actualizado
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con behavior_rules y filtros aplicados
    """
    contact_id = state.get('contact_id', '')
    message = state.get('message', '')
    
    logger.info(f"🔀 [Router] Procesando mensaje del contacto {contact_id}")
    
    # 1. Aplicar filtros (blacklist/whitelist)
    # Extraer número de teléfono del contact_id si es necesario
    # Por ahora, asumimos que contact_id es suficiente
    phone = str(contact_id)
    
    try:
        filter_result = await check_filters(phone, is_group=False)
        
        if filter_result['blocked']:
            logger.warning(f"⛔ [Router] Contacto bloqueado: {contact_id} - {filter_result['reason']}")
            return {
                **state,
                'debe_escalar': True,
                'escalation_reason': f"Contacto bloqueado: {filter_result['reason']}",
                'next_action': 'reject'
            }
    
    except Exception as e:
        logger.error(f"❌ [Router] Error verificando filtros: {e}", exc_info=True)
        # En caso de error, permitir (fail-open)
    
    # 2. Obtener behavior rules activas
    try:
        behavior_rules = await get_active_behavior_rules()
        logger.info(f"✅ [Router] {len(behavior_rules)} reglas de comportamiento cargadas")
    except Exception as e:
        logger.error(f"❌ [Router] Error obteniendo behavior rules: {e}", exc_info=True)
        behavior_rules = []
    
    # 3. Retornar state actualizado
    return {
        **state,
        'behavior_rules': behavior_rules,
        'metadata': {
            **state.get('metadata', {}),
            'filter_checked': True,
            'behavior_rules_count': len(behavior_rules)
        }
    }
