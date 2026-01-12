"""
Database Connection Pool - Centralizado con AsyncPG

Pool único compartido por todo el backend.
Reemplaza databases, psycopg2 y psycopg3.
"""

import os
import logging
from typing import Optional, Dict, List, Any
import asyncpg
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

# Configuración de base de datos
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "podoskin_db")
DB_USER = os.getenv("DB_USER", "podoskin_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "podoskin_password_123")

# Pool global de conexiones
_pool: Optional[asyncpg.Pool] = None


async def init_db_pool():
    """
    Inicializa el pool de conexiones AsyncPG.

    Este es el ÚNICO pool de conexiones del backend.
    Todos los módulos deben usar este pool.
    """
    global _pool

    if _pool is not None:
        logger.info("Database pool already initialized")
        return

    try:
        _pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            min_size=5,
            max_size=20,
            command_timeout=60,
        )
        logger.info(f"✅ AsyncPG pool initialized: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database pool: {e}")
        raise


async def close_db_pool():
    """Cierra el pool de conexiones."""
    global _pool

    if _pool is None:
        return

    try:
        await _pool.close()
        _pool = None
        logger.info("✅ Database pool closed")
    except Exception as e:
        logger.error(f"❌ Error closing database pool: {e}")


async def get_connection():
    """
    Obtiene una conexión del pool.

    Uso:
        conn = await get_connection()
        try:
            result = await conn.fetch("SELECT * FROM tabla")
        finally:
            await release_connection(conn)

    Returns:
        asyncpg.Connection
    """
    if _pool is None:
        await init_db_pool()

    return await _pool.acquire()


async def release_connection(conn):
    """
    Devuelve una conexión al pool.

    Args:
        conn: Conexión a devolver
    """
    if _pool is not None:
        await _pool.release(conn)


# Backward compatibility - mantener por ahora
async def get_db_connection():
    """Alias para compatibilidad con código existente."""
    return await get_connection()


async def get_db_connection_citas():
    """Alias para compatibilidad con reportes/router.py"""
    return await get_connection()


# DATABASE_URL para compatibilidad
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# ============================================================================
# WRAPPER PARA DATABASES LIBRARY (DEPRECATED)
# ============================================================================
# TODO: Eliminar cuando todos los módulos estén migrados
# Módulos pendientes: catalog/service.py


class DatabaseWrapper:
    """
    Wrapper que simula la API de databases library usando AsyncPG.

    DEPRECATED: Los módulos deben migrar a usar get_connection() directamente.
    """

    async def connect(self):
        """Simula databases.connect()"""
        await init_db_pool()

    async def disconnect(self):
        """Simula databases.disconnect()"""
        await close_db_pool()

    async def fetch_all(self, query: str, values: dict = None):
        """Simula databases.fetch_all()"""
        conn = await get_connection()
        try:
            # Convertir :param a $1, $2, etc
            pg_query, pg_params = self._convert_query(query, values or {})
            result = await conn.fetch(pg_query, *pg_params)
            return result
        finally:
            await release_connection(conn)

    async def fetch_one(self, query: str, values: dict = None):
        """Simula databases.fetch_one()"""
        conn = await get_connection()
        try:
            # Convertir :param a $1, $2, etc
            pg_query, pg_params = self._convert_query(query, values or {})
            result = await conn.fetchrow(pg_query, *pg_params)
            return result
        finally:
            await release_connection(conn)

    async def execute(self, query: str, values: dict = None):
        """Simula databases.execute()"""
        conn = await get_connection()
        try:
            # Convertir :param a $1, $2, etc
            pg_query, pg_params = self._convert_query(query, values or {})
            result = await conn.execute(pg_query, *pg_params)
            # Retornar número de filas afectadas
            return int(result.split()[-1]) if result else 0
        finally:
            await release_connection(conn)

    def _convert_query(self, query: str, values: dict):
        """
        Convierte query de databases (:param) a AsyncPG ($1, $2).

        Returns:
            (query_convertido, lista_de_parametros)
        """
        if not values:
            return query, []

        # Ordenar keys para mantener consistencia
        param_names = sorted(values.keys(), key=lambda k: query.find(f":{k}"))
        params = []
        converted_query = query

        for i, param_name in enumerate(param_names, 1):
            converted_query = converted_query.replace(f":{param_name}", f"${i}")
            params.append(values[param_name])

        return converted_query, params


# Instancia global para compatibilidad con databases library
database = DatabaseWrapper()


# ============================================================================
# FUNCIONES HELPER PARA MIGRACIÓN AsyncPG
# ============================================================================
# Estas funciones simplifican la migración de módulos que usan psycopg2


def get_pool() -> asyncpg.Pool:
    """
    Obtiene el pool de conexiones global.
    
    Returns:
        asyncpg.Pool: Pool de conexiones
        
    Raises:
        RuntimeError: Si el pool no está inicializado
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")
    return _pool


async def fetch_one(query: str, *params) -> Optional[dict]:
    """
    Ejecuta query y retorna un registro como diccionario.
    
    Args:
        query: Query SQL con placeholders $1, $2, etc.
        *params: Parámetros para la query
        
    Returns:
        Diccionario con el resultado o None
        
    Example:
        result = await fetch_one("SELECT * FROM users WHERE id = $1", user_id)
    """
    async with _pool.acquire() as conn:
        row = await conn.fetchrow(query, *params)
        return dict(row) if row else None


async def fetch_all(query: str, *params) -> list[dict]:
    """
    Ejecuta query y retorna todos los registros como lista de diccionarios.
    
    Args:
        query: Query SQL con placeholders $1, $2, etc.
        *params: Parámetros para la query
        
    Returns:
        Lista de diccionarios con los resultados
        
    Example:
        results = await fetch_all("SELECT * FROM users WHERE activo = $1", True)
    """
    async with _pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]


async def execute(query: str, *params) -> str:
    """
    Ejecuta INSERT/UPDATE/DELETE sin retornar datos.
    
    Args:
        query: Query SQL con placeholders $1, $2, etc.
        *params: Parámetros para la query
        
    Returns:
        Resultado de la ejecución (ej: "INSERT 0 1")
        
    Example:
        await execute("DELETE FROM users WHERE id = $1", user_id)
    """
    async with _pool.acquire() as conn:
        return await conn.execute(query, *params)


async def execute_returning(query: str, *params) -> Optional[dict]:
    """
    Ejecuta INSERT/UPDATE/DELETE con RETURNING y retorna el resultado.
    
    Args:
        query: Query SQL con RETURNING y placeholders $1, $2, etc.
        *params: Parámetros para la query
        
    Returns:
        Diccionario con el registro retornado o None
        
    Example:
        new_user = await execute_returning(
            "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *",
            name, email
        )
    """
    async with _pool.acquire() as conn:
        row = await conn.fetchrow(query, *params)
        return dict(row) if row else None
