"""
Database Utilities AsyncPG - Módulo de Citas
==============================================

Versión migrada a AsyncPG puro.
Usa el pool centralizado de db.py en lugar de psycopg2.
"""

import logging
from typing import Optional, List, Dict, Any
from db import fetch_one, fetch_all, execute_returning

logger = logging.getLogger(__name__)


# ============================================================================
# YA NO NECESITAMOS init_db_pool ni close_db_pool
# El pool centralizado ya está inicializado en main.py
# ============================================================================


async def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """
    Ejecuta una query SELECT y retorna los resultados como lista de diccionarios.
    
    Args:
        query: Query SQL con placeholders $1, $2, etc.
        params: Parámetros para la query
        
    Returns:
        Lista de diccionarios con los resultados
    """
    return await fetch_all(query, *params)


async def execute_query_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """
    Ejecuta una query SELECT y retorna un solo resultado.
    
    Args:
        query: Query SQL con placeholders $1, $2, etc.
        params: Parámetros para la query
        
    Returns:
        Diccionario con el resultado o None si no hay resultados
    """
    return await fetch_one(query, *params)


async def execute_mutation(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """
    Ejecuta una query INSERT/UPDATE/DELETE y retorna el resultado (si tiene RETURNING).
    
    Args:
        query: Query SQL con placeholders $1, $2, etc.
        params: Parámetros para la query
        
    Returns:
        Diccionario con el resultado si usa RETURNING, None en caso contrario
    """
    return await execute_returning(query, *params)
