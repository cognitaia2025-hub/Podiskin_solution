"""
Database Utilities - Sub-Agente WhatsApp
=========================================

Gestión de conexiones a PostgreSQL usando psycopg2.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from contextlib import asynccontextmanager
import json
import asyncio

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool

from ..config import config

logger = logging.getLogger(__name__)

# Pool global de conexiones
_pool: Optional[pool.ThreadedConnectionPool] = None


def _init_sync_pool():
    """Inicializa el pool de conexiones síncronamente."""
    global _pool

    if _pool is not None:
        return

    try:
        _pool = pool.ThreadedConnectionPool(
            minconn=1, maxconn=5, dsn=config.database_url
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


def _fetch_sync(query: str, args: tuple) -> List[Dict[str, Any]]:
    """Ejecuta query síncronamente."""
    conn = _get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, args)
            result = cur.fetchall()
            return [dict(row) for row in result]
    finally:
        _put_connection(conn)


async def fetch(query: str, *args) -> List[Dict[str, Any]]:
    """Ejecuta una query SELECT y retorna todos los resultados."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _fetch_sync, query, args)
    logger.debug(f"Query executed: {query[:50]}... | Rows: {len(result)}")
    return result


def _fetchrow_sync(query: str, args: tuple) -> Optional[Dict[str, Any]]:
    """Ejecuta query síncronamente y retorna un registro."""
    conn = _get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, args)
            row = cur.fetchone()
            # Commit si es INSERT/UPDATE/DELETE
            if not query.strip().upper().startswith("SELECT"):
                conn.commit()
            return dict(row) if row else None
    except Exception:
        conn.rollback()
        raise
    finally:
        _put_connection(conn)


async def fetchrow(query: str, *args) -> Optional[Dict[str, Any]]:
    """Ejecuta una query SELECT y retorna un solo registro."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _fetchrow_sync, query, args)
    logger.debug(f"Query executed: {query[:50]}... | Found: {result is not None}")
    return result


def _fetchval_sync(query: str, args: tuple) -> Any:
    """Ejecuta query y retorna un valor."""
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, args)
            row = cur.fetchone()
            return row[0] if row else None
    finally:
        _put_connection(conn)


async def fetchval(query: str, *args) -> Any:
    """Ejecuta una query SELECT y retorna un solo valor."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _fetchval_sync, query, args)
    logger.debug(f"Query executed: {query[:50]}... | Value: {result}")
    return result


def _execute_sync(query: str, args: tuple) -> str:
    """Ejecuta query INSERT/UPDATE/DELETE."""
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, args)
            conn.commit()
            return cur.statusmessage
    except Exception:
        conn.rollback()
        raise
    finally:
        _put_connection(conn)


async def execute(query: str, *args) -> str:
    """Ejecuta una query INSERT/UPDATE/DELETE."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _execute_sync, query, args)
    logger.debug(f"Query executed: {query[:50]}... | Status: {result}")
    return result


async def execute_many(query: str, args_list: List[Tuple]) -> None:
    """Ejecuta una query múltiples veces con diferentes parámetros."""

    def _execute_many_sync():
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.executemany(query, args_list)
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            _put_connection(conn)

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _execute_many_sync)
    logger.debug(f"Query executed {len(args_list)} times")


async def execute_transaction(queries: List[Tuple[str, Tuple]]) -> List[Any]:
    """Ejecuta múltiples queries en una transacción."""

    def _transaction_sync():
        conn = _get_connection()
        try:
            results = []
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for query, args in queries:
                    cur.execute(query, args)
                    if query.strip().upper().startswith("SELECT"):
                        rows = cur.fetchall()
                        results.append([dict(row) for row in rows])
                    else:
                        results.append(cur.statusmessage)
            conn.commit()
            return results
        except Exception:
            conn.rollback()
            raise
        finally:
            _put_connection(conn)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _transaction_sync)


# ========================================================================
# HELPER FUNCTIONS ESPECÍFICAS PARA EL SUB-AGENTE
# ========================================================================


async def get_or_create_contact(
    telefono: str, nombre: str, whatsapp_id: Optional[str] = None
) -> Dict:
    """Obtiene o crea un contacto por teléfono."""
    query = """
    SELECT * FROM contactos
    WHERE telefono = %s
    LIMIT 1
    """

    contact = await fetchrow(query, telefono)

    if contact:
        logger.info(f"Contact found: {contact['id']} - {nombre}")
        return contact

    insert_query = """
    INSERT INTO contactos (
        telefono, nombre, whatsapp_id, tipo, origen,
        activo, fecha_primer_contacto
    ) VALUES (
        %s, %s, %s, 'Prospecto', 'WhatsApp',
        true, NOW()
    )
    RETURNING *
    """

    new_contact = await fetchrow(insert_query, telefono, nombre, whatsapp_id)
    logger.info(f"New contact created: {new_contact['id']} - {nombre}")

    return new_contact


async def get_or_create_conversation(
    contact_id: int, whatsapp_chat_id: Optional[str] = None
) -> Dict:
    """Obtiene o crea una conversación activa para un contacto."""
    query = """
    SELECT * FROM conversaciones
    WHERE id_contacto = %s
      AND estado IN ('Activa', 'Esperando_Respuesta')
    ORDER BY fecha_ultima_actividad DESC
    LIMIT 1
    """

    conversation = await fetchrow(query, contact_id)

    if conversation:
        await execute(
            "UPDATE conversaciones SET fecha_ultima_actividad = NOW() WHERE id = %s",
            conversation["id"],
        )
        logger.info(f"Active conversation found: {conversation['id']}")
        return conversation

    insert_query = """
    INSERT INTO conversaciones (
        id_contacto, estado, categoria,
        fecha_inicio, fecha_ultima_actividad
    ) VALUES (
        %s, 'Activa', 'General',
        NOW(), NOW()
    )
    RETURNING *
    """

    new_conversation = await fetchrow(insert_query, contact_id)
    logger.info(f"New conversation created: {new_conversation['id']}")

    return new_conversation


async def save_message(
    conversation_id: int, rol: str, contenido: str, metadata: Optional[Dict] = None
) -> Dict:
    """Guarda un mensaje en la base de datos."""
    query = """
    INSERT INTO mensajes (
        id_conversacion, rol, contenido, metadata, fecha_envio
    ) VALUES (
        %s, %s, %s, %s, NOW()
    )
    RETURNING *
    """

    metadata_json = json.dumps(metadata) if metadata else None
    message = await fetchrow(query, conversation_id, rol, contenido, metadata_json)
    logger.debug(f"Message saved: {message['id']} - {rol}")

    return message


async def update_conversation_summary(
    conversation_id: int, resumen: str, embedding: Optional[List[float]] = None
) -> None:
    """Actualiza el resumen y embedding de una conversación."""
    if embedding:
        query = """
        UPDATE conversaciones
        SET resumen_ia = %s, embedding = %s
        WHERE id = %s
        """
        await execute(query, resumen, embedding, conversation_id)
    else:
        query = """
        UPDATE conversaciones
        SET resumen_ia = %s
        WHERE id = %s
        """
        await execute(query, resumen, conversation_id)

    logger.debug(f"Conversation summary updated: {conversation_id}")


# ========================================================================
# HEALTH CHECK
# ========================================================================


async def check_db_health() -> bool:
    """Verifica que la conexión a la base de datos esté funcionando."""
    try:
        result = await fetchval("SELECT 1")
        return result == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
