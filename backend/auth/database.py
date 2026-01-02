"""
Database Utilities - Autenticacion

Funciones para acceder a la base de datos usando psycopg3.
Solucion para evitar UnicodeDecodeError en Windows.
Ref: https://github.com/psycopg/psycopg2/issues
"""

import logging
from typing import Optional
import asyncio
import psycopg
from psycopg.rows import dict_row
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

# Pool global de conexiones
_pool = None

# Configuracion de base de datos
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "podoskin_db")
DB_USER = os.getenv("DB_USER", "podoskin_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "podoskin_password_123")

# Connection string
CONNINFO = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER}"


async def init_db_pool():
    """Inicializa el pool de conexiones psycopg3."""
    global _pool

    if _pool is not None:
        return

    try:
        # Usar psycopg3 AsyncConnectionPool
        from psycopg_pool import AsyncConnectionPool

        _pool = AsyncConnectionPool(
            conninfo=CONNINFO, min_size=2, max_size=10, open=False
        )
        await _pool.open()
        logger.info("Auth database pool initialized successfully")
    except ImportError:
        # Si no tiene psycopg_pool, usar conexion simple
        logger.warning("psycopg_pool not installed, using simple connections")
    except Exception as e:
        logger.error(f"Failed to initialize auth database pool: {e}")
        # No raise para que la app siga funcionando


async def close_db_pool():
    """Cierra el pool de conexiones."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Auth database pool closed")


async def _get_connection():
    """Obtiene una conexion."""
    if _pool is not None:
        return await _pool.getconn()
    else:
        return await psycopg.AsyncConnection.connect(CONNINFO)


async def _return_connection(conn):
    """Devuelve una conexion al pool."""
    if _pool is not None:
        await _pool.putconn(conn)
    else:
        await conn.close()


async def get_user_by_username(username: str) -> Optional[dict]:
    """
    Obtiene un usuario por su nombre de usuario.
    """
    conn = None
    try:
        conn = await _get_connection()
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT 
                    u.id,
                    u.nombre_usuario,
                    u.password_hash,
                    u.email,
                    r.nombre_rol as rol,
                    u.nombre_completo,
                    u.activo,
                    u.ultimo_login,
                    u.fecha_registro
                FROM usuarios u
                INNER JOIN roles r ON u.id_rol = r.id
                WHERE u.nombre_usuario = %s
                """,
                (username,),
            )
            user = await cur.fetchone()
            return dict(user) if user else None
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return None
    finally:
        if conn:
            await _return_connection(conn)


async def update_last_login(user_id: int) -> bool:
    """
    Actualiza el timestamp de ultimo acceso de un usuario.
    """
    conn = None
    try:
        conn = await _get_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE usuarios
                SET ultimo_login = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (user_id,),
            )
            await conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error updating last login: {e}")
        return False
    finally:
        if conn:
            await _return_connection(conn)


async def is_user_active(user_id: int) -> bool:
    """
    Verifica si un usuario esta activo.
    """
    conn = None
    try:
        conn = await _get_connection()
        async with conn.cursor() as cur:
            await cur.execute("SELECT activo FROM usuarios WHERE id = %s", (user_id,))
            result = await cur.fetchone()
            return result[0] if result else False
    except Exception as e:
        logger.error(f"Error checking if user is active: {e}")
        return False
    finally:
        if conn:
            await _return_connection(conn)


async def update_user_profile(user_id: int, updates: dict) -> bool:
    """
    Actualiza el perfil de un usuario.
    """
    conn = None
    try:
        conn = await _get_connection()
        async with conn.cursor() as cur:
            set_clauses = []
            params = []
            for key, value in updates.items():
                set_clauses.append(f"{key} = %s")
                params.append(value)
            params.append(user_id)
            query = f"UPDATE usuarios SET {', '.join(set_clauses)} WHERE id = %s"
            await cur.execute(query, params)
            await conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        return False
    finally:
        if conn:
            await _return_connection(conn)


async def update_user_password(user_id: int, password_hash: str) -> bool:
    """
    Actualiza la contraseña de un usuario.
    """
    conn = None
    try:
        conn = await _get_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE usuarios SET password_hash = %s WHERE id = %s",
                (password_hash, user_id),
            )
            await conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error updating user password: {e}")
        return False
    finally:
        if conn:
            await _return_connection(conn)
