"""
Database Utilities - Módulo de Tratamientos
===========================================

Utilidades para conexión y operaciones con PostgreSQL.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import asyncio

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool

logger = logging.getLogger(__name__)

# Pool global de conexiones
_pool: Optional[pool.ThreadedConnectionPool] = None


def get_database_url() -> str:
    """Obtiene la URL de conexión a la base de datos."""
    # Intentar obtener desde variable de entorno
    db_url = os.getenv('DATABASE_URL')
    
    if db_url:
        return db_url
    
    # Construir desde componentes individuales
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'podoskin')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def _init_sync_pool():
    """Inicializa el pool de conexiones síncronamente."""
    global _pool

    if _pool is not None:
        return

    try:
        database_url = get_database_url()
        _pool = pool.ThreadedConnectionPool(
            minconn=1, 
            maxconn=10, 
            dsn=database_url
        )
        logger.info("Database pool initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
        raise


async def init_db_pool():
    """Inicializa el pool de conexiones."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _init_sync_pool)


async def close_db_pool():
    """Cierra el pool de conexiones."""
    global _pool

    if _pool is None:
        return

    try:
        _pool.closeall()
        _pool = None
        logger.info("Database pool closed successfully")
    except Exception as e:
        logger.error(f"Error closing database pool: {e}")


def _get_connection():
    """Obtiene una conexión del pool."""
    global _pool

    if _pool is None:
        _init_sync_pool()

    return _pool.getconn()


def _put_connection(conn):
    """Devuelve una conexión al pool."""
    global _pool
    if _pool is not None:
        _pool.putconn(conn)


@asynccontextmanager
async def get_db_connection():
    """Context manager para obtener una conexión del pool."""
    loop = asyncio.get_event_loop()
    conn = await loop.run_in_executor(None, _get_connection)
    try:
        yield conn
    finally:
        await loop.run_in_executor(None, _put_connection, conn)


async def execute_query(
    query: str, 
    params: tuple = (), 
    fetch_one: bool = False,
    fetch_all: bool = True
) -> Optional[List[Dict[str, Any]] | Dict[str, Any]]:
    """
    Ejecuta una query de lectura y retorna resultados.
    
    Args:
        query: SQL query a ejecutar
        params: Parámetros de la query
        fetch_one: Si True, retorna solo un resultado
        fetch_all: Si True, retorna todos los resultados
        
    Returns:
        Lista de diccionarios con los resultados o None
    """
    async with get_db_connection() as conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                
                if fetch_one:
                    result = cur.fetchone()
                    return dict(result) if result else None
                elif fetch_all:
                    results = cur.fetchall()
                    return [dict(row) for row in results]
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise


async def execute_mutation(
    query: str, 
    params: tuple = (),
    returning: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Ejecuta una query de escritura (INSERT, UPDATE, DELETE).
    
    Args:
        query: SQL query a ejecutar
        params: Parámetros de la query
        returning: Si True, espera un RETURNING y retorna el resultado
        
    Returns:
        Diccionario con el resultado del RETURNING o None
    """
    async with get_db_connection() as conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                conn.commit()
                
                if returning:
                    result = cur.fetchone()
                    return dict(result) if result else None
                else:
                    return None
                    
        except Exception as e:
            conn.rollback()
            logger.error(f"Error executing mutation: {e}")
            raise
