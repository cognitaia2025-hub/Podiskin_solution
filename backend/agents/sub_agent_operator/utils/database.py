"""
Utilidades de Base de Datos
============================

Funciones para gestionar conexiones a PostgreSQL.
Reutiliza el pool del sub-agente de WhatsApp.
"""

import logging
import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Pool de conexiones global
_pool = None


def _init_sync_pool():
    """Inicializa el pool de conexiones síncrono."""
    global _pool

    if _pool is not None:
        return

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment")

    try:
        _pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1, maxconn=10, dsn=database_url
        )
        logger.info("Database pool initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database pool: {e}", exc_info=True)
        raise


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


def close_pool():
    """Cierra el pool de conexiones."""
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None
        logger.info("Database pool closed successfully")
