"""
Database connection utilities for the pacientes module.
Migrado para usar pool centralizado de db.py
"""

from contextlib import asynccontextmanager
from db import get_connection, release_connection


@asynccontextmanager
async def get_db_connection():
    """
    Dependency to get database connection from centralized pool.
    
    Usage:
        async with get_db_connection() as conn:
            result = await conn.fetch("SELECT ...")
    """
    conn = await get_connection()
    try:
        yield conn
    finally:
        await release_connection(conn)
