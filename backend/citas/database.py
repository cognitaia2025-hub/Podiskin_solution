"""
Database Utilities - Módulo de Citas
=====================================

Utilidades para conexión y operaciones con PostgreSQL.
"""

import os
import logging
from typing import Optional, List, Dict, Any
import asyncio

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from dotenv import load_dotenv

# ✅ IMPORTAR CREDENCIALES DESDE auth/database.py
from auth.database import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Pool global de conexiones
_pool: Optional[pool.ThreadedConnectionPool] = None


def get_database_url() -> str:
    """Obtiene la URL de conexión a la base de datos."""
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


async def init_db_pool(database_url: Optional[str] = None):
    """
    Inicializa el pool de conexiones a la base de datos.
    
    Args:
        database_url: URL de conexión. Si no se proporciona, se construye desde variables importadas.
    """
    global _pool

    if _pool is not None:
        return

    try:
        if database_url is None:
            database_url = get_database_url()
        
        # Crear el pool de conexiones
        _pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=database_url
        )
        logger.info("✅ Database pool initialized for citas module")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database pool: {e}")
        raise


async def close_db_pool():
    """Cierra el pool de conexiones."""
    global _pool

    if _pool is None:
        return
        
    try:
        _pool.closeall()
        _pool = None
        logger.info("✅ Database pool closed")
    except Exception as e:
        logger.error(f"❌ Error closing database pool: {e}")


def _get_connection():
    """
    Obtiene una conexión del pool.
    
    Returns:
        Conexión de base de datos del pool
        
    Raises:
        Exception: Si el pool no está inicializado
    """
    global _pool

    if _pool is None:
        raise Exception("Database pool not initialized. Call init_db_pool() first.")

    return _pool.getconn()


def _put_connection(conn):
    """
    Devuelve una conexión al pool.
    
    Args:
        conn: Conexión a devolver al pool
    """
    global _pool
    if _pool is not None:
        _pool.putconn(conn)


async def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """
    Ejecuta una query SELECT y retorna los resultados como lista de diccionarios.
    
    Args:
        query: Query SQL a ejecutar
        params: Parámetros para la query
        
    Returns:
        Lista de diccionarios con los resultados
    """
    loop = asyncio.get_event_loop()
    
    def _execute():
        conn = _get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                result = cur.fetchall()
                return [dict(row) for row in result]
        finally:
            _put_connection(conn)
    
    return await loop.run_in_executor(None, _execute)


async def execute_query_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """
    Ejecuta una query SELECT y retorna un solo resultado.
    
    Args:
        query: Query SQL a ejecutar
        params: Parámetros para la query
        
    Returns:
        Diccionario con el resultado o None si no hay resultados
    """
    loop = asyncio.get_event_loop()
    
    def _execute():
        conn = _get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                result = cur.fetchone()
                return dict(result) if result else None
        finally:
            _put_connection(conn)
    
    return await loop.run_in_executor(None, _execute)


async def execute_mutation(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """
    Ejecuta una query INSERT/UPDATE/DELETE y retorna el resultado (si tiene RETURNING).
    
    Args:
        query: Query SQL a ejecutar
        params: Parámetros para la query
        
    Returns:
        Diccionario con el resultado si usa RETURNING, None en caso contrario
    """
    loop = asyncio.get_event_loop()
    
    def _execute():
        conn = _get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                conn.commit()
                # Si la query tiene RETURNING, obtener el resultado
                if cur.description:
                    result = cur.fetchone()
                    return dict(result) if result else None
                return None
        except Exception as e:
            conn.rollback()
            raise
        finally:
            _put_connection(conn)
    
    return await loop.run_in_executor(None, _execute)
