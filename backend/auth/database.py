"""
Database Utilities - Autenticacion

Funciones para acceder a la base de datos usando AsyncPG.
Pool centralizado compartido con todo el backend.
"""

import logging
import os
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

# Configuración de base de datos (para compatibilidad con módulos legacy)
# NOTA: Fallbacks removidos por seguridad. Usar .env obligatorio
DB_HOST = os.getenv("DB_HOST") or "127.0.0.1"
DB_PORT = int(os.getenv("DB_PORT") or "5432")
DB_NAME = os.getenv("DB_NAME") or "podoskin_db"
DB_USER = os.getenv("DB_USER") or "podoskin_user"
DB_PASSWORD = os.getenv("DB_PASSWORD")  # ⚠️ REQUERIDO en .env

if not DB_PASSWORD:
    logger.error("DB_PASSWORD no configurado en .env - La aplicación fallará")

# Connection string para compatibilidad con módulos legacy
CONNINFO = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"


async def get_user_by_username(username: str) -> Optional[dict]:
    """
    Obtiene un usuario por su nombre de usuario, email o teléfono.

    Busca en:
    - usuarios.nombre_usuario
    - usuarios.email
    - podologos.telefono (mediante JOIN)
    """
    from db import get_connection, release_connection

    conn = None
    try:
        conn = await get_connection()

        user = await conn.fetchrow(
            """
            SELECT 
                u.id,
                u.nombre_usuario,
                u.password_hash,
                u.email,
                u.rol,
                u.nombre_completo,
                u.activo,
                u.ultimo_login,
                u.fecha_registro
            FROM usuarios u
            LEFT JOIN podologos p ON u.id = p.id_usuario
            WHERE u.nombre_usuario = $1 
               OR u.email = $2
               OR p.telefono = $3
            LIMIT 1
            """,
            username,
            username,
            username,
        )

        return dict(user) if user else None
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return None
    finally:
        if conn:
            await release_connection(conn)


async def update_last_login(user_id: int) -> bool:
    """
    Actualiza el timestamp de ultimo acceso de un usuario.
    """
    from db import get_connection, release_connection

    conn = None
    try:
        conn = await get_connection()

        await conn.execute(
            """
            UPDATE usuarios
            SET ultimo_login = CURRENT_TIMESTAMP
            WHERE id = $1
            """,
            user_id,
        )

        return True
    except Exception as e:
        logger.error(f"Error updating last login: {e}")
        return False
    finally:
        if conn:
            await release_connection(conn)


async def is_user_active(user_id: int) -> bool:
    """
    Verifica si un usuario esta activo.
    """
    from db import get_connection, release_connection

    conn = None
    try:
        conn = await get_connection()

        result = await conn.fetchval(
            "SELECT activo FROM usuarios WHERE id = $1", user_id
        )

        return result if result is not None else False
    except Exception as e:
        logger.error(f"Error checking if user is active: {e}")
        return False
    finally:
        if conn:
            await release_connection(conn)


async def update_user_profile(user_id: int, updates: dict) -> bool:
    """
    Actualiza el perfil de un usuario.
    """
    from db import get_connection, release_connection

    conn = None
    try:
        conn = await get_connection()

        set_clauses = []
        params = []
        param_num = 1

        for key, value in updates.items():
            set_clauses.append(f"{key} = ${param_num}")
            params.append(value)
            param_num += 1

        params.append(user_id)
        query = f"UPDATE usuarios SET {', '.join(set_clauses)} WHERE id = ${param_num}"

        await conn.execute(query, *params)
        return True
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        return False
    finally:
        if conn:
            await release_connection(conn)


async def update_user_password(user_id: int, password_hash: str) -> bool:
    """
    Actualiza la contraseña de un usuario.
    """
    from db import get_connection, release_connection

    conn = None
    try:
        conn = await get_connection()

        await conn.execute(
            "UPDATE usuarios SET password_hash = $1 WHERE id = $2",
            password_hash,
            user_id,
        )

        return True
    except Exception as e:
        logger.error(f"Error updating user password for user_id={user_id}: {e}", exc_info=True)
        return False
    finally:
        if conn:
            await release_connection(conn)


async def get_all_users(activo_only: bool = True) -> list:
    """
    Obtiene todos los usuarios.
    """
    from db import get_connection, release_connection

    conn = None
    try:
        conn = await get_connection()

        query = """
            SELECT 
                u.id, 
                u.nombre_usuario, 
                u.nombre_completo, 
                u.email, 
                u.activo,
                u.ultimo_login,
                u.fecha_registro,
                u.rol
            FROM usuarios u
        """

        if activo_only:
            query += " WHERE u.activo = true"

        query += " ORDER BY u.id"

        users = await conn.fetch(query)
        return [dict(user) for user in users] if users else []
    except Exception as e:
        logger.error(f"Error fetching users from database: {e}", exc_info=True)
        raise RuntimeError(f"Error obteniendo lista de usuarios: {e}") from e
    finally:
        if conn:
            await release_connection(conn)


async def get_user_by_id(user_id: int) -> Optional[dict]:
    """
    Obtiene un usuario por ID.
    """
    from db import get_connection, release_connection

    conn = None
    try:
        conn = await get_connection()

        user = await conn.fetchrow(
            """
            SELECT 
                u.id, 
                u.nombre_usuario, 
                u.nombre_completo, 
                u.email, 
                u.activo,
                u.ultimo_login,
                u.fecha_registro,
                u.rol
            FROM usuarios u
            WHERE u.id = $1
            """,
            user_id,
        )

        return dict(user) if user else None
    except Exception as e:
        logger.error(f"Error fetching user by id: {e}")
        return None
    finally:
        if conn:
            await release_connection(conn)


async def create_user(
    nombre_usuario: str,
    password_hash: str,
    nombre_completo: str,
    email: str,
    rol: str,
    creado_por: int = None,
) -> Optional[dict]:
    """
    Crea un nuevo usuario (rol como texto).
    """
    from db import get_connection, release_connection

    conn = None
    try:
        conn = await get_connection()

        # 1. Obtener ID del rol
        role_row = await conn.fetchrow(
            "SELECT id FROM roles WHERE nombre_rol = $1", rol
        )

        if not role_row:
            logger.error(f"Role not found: {rol}")
            return None

        id_rol = role_row["id"]

        # 2. Insertar usuario
        user = await conn.fetchrow(
            """
            INSERT INTO usuarios (
                nombre_usuario, 
                password_hash, 
                nombre_completo, 
                email, 
                id_rol, 
                activo,
                creado_por
            )
            VALUES ($1, $2, $3, $4, $5, true, $6)
            RETURNING id, nombre_usuario, nombre_completo, email, activo, fecha_registro
            """,
            nombre_usuario,
            password_hash,
            nombre_completo,
            email,
            id_rol,
            creado_por,
        )

        if user:
            user_dict = dict(user)
            user_dict["rol"] = rol
            return user_dict

        return None
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None
    finally:
        if conn:
            await release_connection(conn)


async def update_user(
    user_id: int,
    nombre_completo: str = None,
    email: str = None,
    rol: str = None,
    activo: bool = None,
) -> Optional[dict]:
    """
    Actualiza un usuario existente.
    """
    from db import get_connection, release_connection

    conn = None
    try:
        conn = await get_connection()

        updates = []
        params = []
        param_num = 1

        if nombre_completo is not None:
            updates.append(f"nombre_completo = ${param_num}")
            params.append(nombre_completo)
            param_num += 1

        if email is not None:
            updates.append(f"email = ${param_num}")
            params.append(email)
            param_num += 1

        if rol is not None:
            # Obtener ID del rol
            role_row = await conn.fetchrow(
                "SELECT id FROM roles WHERE nombre_rol = $1", rol
            )
            if role_row:
                updates.append(f"id_rol = ${param_num}")
                params.append(role_row["id"])
                param_num += 1
            else:
                logger.warning(f"Role not found during update: {rol}")

        if activo is not None:
            updates.append(f"activo = ${param_num}")
            params.append(activo)
            param_num += 1

        if not updates:
            return await get_user_by_id(user_id)

        params.append(user_id)
        query = f"""
            UPDATE usuarios 
            SET {', '.join(updates)} 
            WHERE id = ${param_num} 
            RETURNING id, nombre_usuario, nombre_completo, email, activo, fecha_registro
        """

        user = await conn.fetchrow(query, *params)

        if user:
            user_dict = dict(user)
            # Si se actualizó el rol, usar el nuevo, si no, buscar el actual
            if rol:
                user_dict["rol"] = rol
            else:
                # Buscar rol actual
                role_res = await conn.fetchrow(
                    "SELECT rol FROM usuarios WHERE id = $1", user_id
                )
                user_dict["rol"] = role_res["rol"] if role_res else None

            return user_dict

        return None
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        return None
    finally:
        if conn:
            await release_connection(conn)


async def delete_user(user_id: int) -> bool:
    """
    Elimina un usuario (soft delete - pone activo=false).
    """
    from db import get_connection, release_connection

    conn = None
    try:
        conn = await get_connection()

        result = await conn.execute(
            "UPDATE usuarios SET activo = false WHERE id = $1", user_id
        )

        # result es un string como "UPDATE 1"
        return "1" in result
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return False
    finally:
        if conn:
            await release_connection(conn)


# ============================================================================
# WRAPPERS TEMPORALES PARA COMPATIBILIDAD CON MÓDULOS LEGACY
# ============================================================================
# TODO: Eliminar estos wrappers cuando todos los módulos estén migrados a AsyncPG
# Módulos pendientes: inventory/service.py, stats/router.py, citas/database.py


async def _get_connection():
    """
    Wrapper temporal para compatibilidad con módulos legacy.

    DEPRECATED: Usar directamente db.get_connection()
    """
    from db import get_connection

    return await get_connection()


async def _return_connection(conn):
    """
    Wrapper temporal para compatibilidad con módulos legacy.

    DEPRECATED: Usar directamente db.release_connection()
    """
    from db import release_connection

    await release_connection(conn)
