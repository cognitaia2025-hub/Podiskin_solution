"""
Filter Tools
============

Tools para aplicar filtros de entrada (blacklist/whitelist/grupos).

Referencias:
- https://docs.langchain.com/oss/python/langgraph/workflows-agents#conditional-routing
"""

import logging
from db import get_pool

logger = logging.getLogger(__name__)

# ============================================================================
# FUNCIÓN: Check Filters
# ============================================================================

async def check_filters(phone: str, is_group: bool = False, group_id: str = None) -> dict:
    """
    Verifica si un número o grupo está en blacklist/whitelist.
    
    Args:
        phone: Número de teléfono
        is_group: Si es un grupo
        group_id: ID del grupo (si aplica)
        
    Returns:
        Dict con resultado: {
            "blocked": bool,
            "reason": str,
            "filter_type": str
        }
    """
    pool = await get_pool()
    
    try:
        # Verificar blacklist
        if is_group and group_id:
            blacklisted = await pool.fetchrow(
                "SELECT * FROM whatsapp_filters WHERE tipo = 'grupo_bloqueado' AND valor = $1 AND activo = true",
                group_id
            )
        else:
            blacklisted = await pool.fetchrow(
                "SELECT * FROM whatsapp_filters WHERE tipo = 'blacklist' AND valor = $1 AND activo = true",
                phone
            )
        
        if blacklisted:
            logger.warning(f"⛔ Bloqueado: {phone} - Razón: {blacklisted['razon']}")
            return {
                "blocked": True,
                "reason": blacklisted['razon'] or "Número en blacklist",
                "filter_type": "blacklist"
            }
        
        # Verificar si hay whitelist activa (modo restrictivo)
        whitelist_exists = await pool.fetchval(
            "SELECT EXISTS(SELECT 1 FROM whatsapp_filters WHERE tipo = 'whitelist' AND activo = true)"
        )
        
        if whitelist_exists:
            # Si hay whitelist, verificar que el número esté en ella
            in_whitelist = await pool.fetchval(
                "SELECT EXISTS(SELECT 1 FROM whatsapp_filters WHERE tipo = 'whitelist' AND valor = $1 AND activo = true)",
                phone
            )
            
            if not in_whitelist:
                logger.warning(f"⛔ No en whitelist: {phone}")
                return {
                    "blocked": True,
                    "reason": "Número no autorizado (whitelist activa)",
                    "filter_type": "whitelist"
                }
        
        # Permitido
        return {
            "blocked": False,
            "reason": None,
            "filter_type": None
        }
    
    except Exception as e:
        logger.error(f"❌ Error verificando filtros: {e}", exc_info=True)
        # En caso de error, permitir (fail-open)
        return {
            "blocked": False,
            "reason": f"Error verificando filtros: {str(e)}",
            "filter_type": "error"
        }
