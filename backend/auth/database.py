"""
Database Utilities para Autenticación
======================================

Funciones para acceso a datos de usuarios.
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/podoskin"
)


def get_db_connection():
    """
    Obtiene una conexión a la base de datos
    
    Returns:
        Conexión psycopg2
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene un usuario por su username
    
    Args:
        username: Nombre de usuario
        
    Returns:
        Diccionario con datos del usuario o None si no existe
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT 
                    id,
                    nombre_usuario as username,
                    password_hash,
                    nombre_completo,
                    email,
                    rol,
                    activo,
                    ultimo_login
                FROM usuarios
                WHERE nombre_usuario = %s
                """,
                (username,)
            )
            user = cursor.fetchone()
            return dict(user) if user else None
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return None
    finally:
        if conn:
            conn.close()


def update_last_login(user_id: int) -> bool:
    """
    Actualiza el último login del usuario
    
    Args:
        user_id: ID del usuario
        
    Returns:
        True si se actualizó correctamente
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE usuarios
                SET ultimo_login = %s
                WHERE id = %s
                """,
                (datetime.now(timezone.utc), user_id)
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
            conn.close()
