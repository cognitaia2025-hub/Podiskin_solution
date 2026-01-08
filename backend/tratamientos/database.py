"""
Database Utilities AsyncPG - Módulo de Tratamientos
====================================================

Versión migrada a AsyncPG puro.
Usa el pool centralizado de db.py en lugar de psycopg2.
"""

import logging
from typing import Optional, List, Dict, Any
from db import fetch_one, fetch_all, execute_returning

logger = logging.getLogger(__name__)


async def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Ejecuta SELECT que retorna múltiples filas"""
    return await fetch_all(query, *params)


async def execute_query_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """Ejecuta SELECT que retorna una fila"""
    return await fetch_one(query, *params)


async def execute_mutation(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """Ejecuta INSERT/UPDATE/DELETE con RETURNING"""
    return await execute_returning(query, *params)
