"""
Middleware de Permisos - Sistema de Control de Acceso Granular
==============================================================
Valida permisos de usuarios antes de ejecutar acciones.
"""

from functools import wraps
from typing import Callable
from fastapi import HTTPException, status, Depends
import psycopg
from psycopg.rows import dict_row
import os
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# PLANTILLAS DE PERMISOS PREDEFINIDAS
# ============================================================================

PERMISSION_TEMPLATES = {
    "admin": {
        "calendario": {"read": True, "write": True},
        "pacientes": {"read": True, "write": True},
        "cobros": {"read": True, "write": True},
        "expedientes": {"read": True, "write": True},
        "inventario": {"read": True, "write": True},
        "gastos": {"read": True, "write": True},
        "cortes_caja": {"read": True, "write": True},
        "administracion": {"read": True, "write": True}
    },
    "podologo": {
        "calendario": {"read": True, "write": False},
        "pacientes": {"read": True, "write": True},
        "cobros": {"read": True, "write": False},
        "expedientes": {"read": True, "write": True},
        "inventario": {"read": True, "write": False},
        "gastos": {"read": False, "write": False},
        "cortes_caja": {"read": False, "write": False},
        "administracion": {"read": False, "write": False}
    },
    "recepcionista": {
        "calendario": {"read": True, "write": True},
        "pacientes": {"read": True, "write": True},
        "cobros": {"read": True, "write": True},
        "expedientes": {"read": True, "write": False},
        "inventario": {"read": True, "write": False},
        "gastos": {"read": False, "write": False},
        "cortes_caja": {"read": True, "write": True},
        "administracion": {"read": False, "write": False}
    }
}


# ============================================================================
# FUNCIONES HELPER
# ============================================================================

def _get_connection():
    """Obtiene conexión a la base de datos."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "podoskin_db"),
        user=os.getenv("DB_USER", "podoskin_user"),
        password=os.getenv("DB_PASSWORD", "podoskin_password_123"),
        row_factory=dict_row
    )


def get_user_permissions(user_id: int) -> dict:
    """
    Obtiene permisos de un usuario desde la base de datos.
    
    Args:
        user_id: ID del usuario
        
    Returns:
        dict: Diccionario con permisos del usuario
    """
    try:
        with _get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT permisos FROM permisos_usuarios WHERE id_usuario = %s",
                    (user_id,)
                )
                result = cur.fetchone()
                
                if result:
                    return result['permisos']
                else:
                    # Si no tiene permisos, asignar plantilla vacía
                    logger.warning(f"Usuario {user_id} sin permisos registrados")
                    return {}
    except Exception as e:
        logger.error(f"Error obteniendo permisos: {e}")
        return {}


def check_permission(user_id: int, permission: str) -> bool:
    """
    Verifica si un usuario tiene un permiso específico.
    
    Args:
        user_id: ID del usuario
        permission: String en formato "modulo:accion" (ej: "cobros:write")
        
    Returns:
        bool: True si tiene permiso, False si no
    """
    try:
        module, action = permission.split(":")
        permisos = get_user_permissions(user_id)
        
        if not permisos:
            return False
            
        module_perms = permisos.get(module, {})
        return module_perms.get(action, False)
        
    except Exception as e:
        logger.error(f"Error verificando permiso {permission}: {e}")
        return False


# ============================================================================
# DECORADOR DE PERMISOS
# ============================================================================

def require_permission(permission: str):
    """
    Decorador para endpoints que requieren permisos específicos.
    
    Usage:
        @router.post("/pagos")
        @require_permission("cobros:write")
        async def crear_pago(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Obtener current_user de los kwargs (inyectado por Depends)
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No autenticado"
                )
            
            user_id = current_user.get('id') if isinstance(current_user, dict) else current_user.id
            
            if not check_permission(user_id, permission):
                logger.warning(
                    f"Usuario {user_id} intentó acción sin permiso: {permission}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"No tienes permiso para realizar esta acción ({permission})"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

async def verify_permission(permission: str, current_user: dict = Depends):
    """
    Dependency para verificar permisos en endpoints FastAPI.
    
    Usage:
        @router.post("/pagos")
        async def crear_pago(
            ...,
            _: None = Depends(verify_permission("cobros:write"))
        ):
            ...
    """
    user_id = current_user.get('id') if isinstance(current_user, dict) else current_user.id
    
    if not check_permission(user_id, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No tienes permiso para realizar esta acción"
        )
    return None
