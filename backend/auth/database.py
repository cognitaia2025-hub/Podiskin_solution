"""
Database Utilities - Autenticación
===================================

Funciones para acceder a la base de datos desde los endpoints de autenticación.
"""

import logging
from typing import Optional
from contextlib import asynccontextmanager
import asyncio

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

# Pool global de conexiones
_pool: Optional[pool.ThreadedConnectionPool] = None

# URL de base de datos desde environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/podoskin_db")


def _init_sync_pool():
    """Inicializa el pool de conexiones síncronamente."""
    global _pool

    if _pool is not None:
        return

    try:
        _pool = pool.ThreadedConnectionPool(
            minconn=2, 
            maxconn=10, 
            dsn=DATABASE_URL
        )
        logger.info("Auth database pool initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize auth database pool: {e}")
        raise


async def init_db_pool():
    """Inicializa el pool de conexiones de forma asíncrona."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _init_sync_pool)


async def close_db_pool():
    """Cierra el pool de conexiones."""
    global _pool
    if _pool is not None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _pool.closeall)
        _pool = None
        logger.info("Auth database pool closed")


def _get_connection():
    """Obtiene una conexión del pool."""
    if _pool is None:
        _init_sync_pool()
    return _pool.getconn()


def _return_connection(conn):
    """Devuelve una conexión al pool."""
    if _pool is not None:
        _pool.putconn(conn)


async def get_user_by_username(username: str) -> Optional[dict]:
    """
    Obtiene un usuario por su nombre de usuario.
    
    Args:
        username: Nombre de usuario a buscar
        
    Returns:
        Diccionario con datos del usuario o None si no existe
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_user_by_username_sync, username)


def _get_user_by_username_sync(username: str) -> Optional[dict]:
    """Versión síncrona de get_user_by_username."""
    conn = None
    try:
        conn = _get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT 
                    id,
                    nombre_usuario,
                    password_hash,
                    email,
                    rol,
                    nombre_completo,
                    activo,
                    ultimo_login,
                    fecha_registro
                FROM usuarios
                WHERE nombre_usuario = %s
                """,
                (username,)
            )
            result = cur.fetchone()
            return dict(result) if result else None
    except Exception as e:
        logger.error(f"Error getting user by username: {e}")
        return None
    finally:
        if conn:
            _return_connection(conn)


async def update_last_login(user_id: int) -> bool:
    """
    Actualiza el timestamp de último acceso de un usuario.
    
    Args:
        user_id: ID del usuario
        
    Returns:
        True si se actualizó correctamente, False si hubo error
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _update_last_login_sync, user_id)


def _update_last_login_sync(user_id: int) -> bool:
    """Versión síncrona de update_last_login."""
    conn = None
    try:
        conn = _get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE usuarios
                SET ultimo_login = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (user_id,)
            )
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error updating last login: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            _return_connection(conn)


async def is_user_active(user_id: int) -> bool:
    """
    Verifica si un usuario está activo.
    
    Args:
        user_id: ID del usuario
        
    Returns:
        True si el usuario está activo, False si no
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _is_user_active_sync, user_id)


def _is_user_active_sync(user_id: int) -> bool:
    """Versión síncrona de is_user_active."""
    conn = None
    try:
        conn = _get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT activo FROM usuarios WHERE id = %s",
                (user_id,)
            )
            result = cur.fetchone()
            return result[0] if result else False
    except Exception as e:
        logger.error(f"Error checking if user is active: {e}")
        return False
    finally:
        if conn:
            _return_connection(conn)
