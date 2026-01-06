"""
Authorization Middleware - RBAC
================================

Middleware para control de acceso basado en roles (Role-Based Access Control).
"""

from functools import wraps
from typing import List, Callable
from fastapi import HTTPException, status, Depends
import logging

from .models import User
from .middleware import get_current_user

logger = logging.getLogger(__name__)


def require_role(allowed_roles: List[str]):
    """
    Decorator para requerir uno o más roles específicos.
    
    Valida que el usuario actual tenga uno de los roles permitidos.
    Si no tiene permiso, lanza HTTPException 403.
    
    Args:
        allowed_roles: Lista de roles permitidos (ej: ["Admin", "Podologo"])
        
    Returns:
        Decorated function que valida roles
        
    Raises:
        HTTPException 403: Si el usuario no tiene el rol requerido
        
    Example:
        >>> @router.post("/pacientes")
        >>> @require_role(["Admin", "Podologo", "Recepcionista"])
        >>> async def crear_paciente(
        >>>     paciente: PacienteCreate,
        >>>     current_user: User = Depends(get_current_user)
        >>> ):
        >>>     # Solo Admin, Podologo o Recepcionista pueden crear pacientes
        >>>     return {"status": "created"}
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            # Verificar que el usuario tenga uno de los roles permitidos
            if current_user.rol not in allowed_roles:
                logger.warning(
                    f"User {current_user.nombre_usuario} with role {current_user.rol} "
                    f"tried to access endpoint requiring roles {allowed_roles}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"No tiene permisos para esta acción. Roles requeridos: {', '.join(allowed_roles)}"
                )
            
            # Usuario tiene permiso, ejecutar función
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def require_admin():
    """
    Decorator para requerir rol de Administrador.
    
    Shortcut para @require_role(["Admin"])
    
    Example:
        >>> @router.delete("/usuarios/{user_id}")
        >>> @require_admin()
        >>> async def eliminar_usuario(
        >>>     user_id: int,
        >>>     current_user: User = Depends(get_current_user)
        >>> ):
        >>>     # Solo Admin puede eliminar usuarios
        >>>     return {"status": "deleted"}
    """
    return require_role(["Admin"])


def require_podologo():
    """
    Decorator para requerir rol de Podólogo o Admin.
    
    Shortcut para acciones médicas que requieren podólogo o admin.
    
    Example:
        >>> @router.post("/diagnosticos")
        >>> @require_podologo()
        >>> async def crear_diagnostico(
        >>>     diagnostico: DiagnosticoCreate,
        >>>     current_user: User = Depends(get_current_user)
        >>> ):
        >>>     # Solo Podologo o Admin pueden crear diagnósticos
        >>>     return {"status": "created"}
    """
    return require_role(["Admin", "Podologo"])


def require_staff():
    """
    Decorator para requerir cualquier rol de staff (todos menos paciente).
    
    Shortcut para acciones que puede realizar cualquier empleado.
    
    Example:
        >>> @router.get("/agenda")
        >>> @require_staff()
        >>> async def ver_agenda(current_user: User = Depends(get_current_user)):
        >>>     # Cualquier staff puede ver la agenda
        >>>     return {"agenda": [...]}
    """
    return require_role(["Admin", "Podologo", "Recepcionista", "Asistente"])


async def check_user_permission(
    current_user: User,
    required_roles: List[str]
) -> bool:
    """
    Verifica si un usuario tiene uno de los roles requeridos.
    
    Función auxiliar para verificación manual de permisos sin usar decorator.
    
    Args:
        current_user: Usuario a verificar
        required_roles: Lista de roles permitidos
        
    Returns:
        True si el usuario tiene permiso, False si no
        
    Example:
        >>> current_user = await get_current_user(credentials)
        >>> if not await check_user_permission(current_user, ["Admin", "Podologo"]):
        >>>     raise HTTPException(403, "No tiene permisos")
    """
    has_permission = current_user.rol in required_roles
    
    if not has_permission:
        logger.info(
            f"Permission check failed: User {current_user.nombre_usuario} "
            f"(role: {current_user.rol}) does not have required roles: {required_roles}"
        )
    else:
        logger.debug(
            f"Permission check passed: User {current_user.nombre_usuario} "
            f"(role: {current_user.rol}) has required permission"
        )
    
    return has_permission


async def verify_user_owns_resource(
    current_user: User,
    resource_user_id: int
) -> bool:
    """
    Verifica si un usuario es dueño de un recurso o es administrador.
    
    Útil para verificar que un usuario solo pueda modificar sus propios recursos,
    excepto si es administrador.
    
    Args:
        current_user: Usuario actual
        resource_user_id: ID del usuario dueño del recurso
        
    Returns:
        True si el usuario es dueño del recurso o es admin, False si no
        
    Example:
        >>> # Verificar que solo el usuario o admin pueda modificar el perfil
        >>> if not await verify_user_owns_resource(current_user, user_id):
        >>>     raise HTTPException(403, "No puede modificar este recurso")
    """
    is_owner = current_user.id == resource_user_id
    is_admin = current_user.rol == "Admin"
    has_access = is_owner or is_admin
    
    if not has_access:
        logger.warning(
            f"Resource ownership check failed: User {current_user.nombre_usuario} "
            f"(id: {current_user.id}) attempted to access resource owned by user id: {resource_user_id}"
        )
    else:
        logger.debug(
            f"Resource ownership check passed: User {current_user.nombre_usuario} "
            f"(owner: {is_owner}, admin: {is_admin})"
        )
    
    return has_access


class RoleChecker:
    """
    Clase para validación de roles como dependency de FastAPI.
    
    Alternativa a los decorators, puede usarse directamente como dependency.
    
    Example:
        >>> # Definir roles permitidos
        >>> allow_admin_only = RoleChecker(["Admin"])
        >>> 
        >>> @router.delete("/usuarios/{user_id}")
        >>> async def eliminar_usuario(
        >>>     user_id: int,
        >>>     current_user: User = Depends(allow_admin_only)
        >>> ):
        >>>     return {"status": "deleted"}
    """
    
    def __init__(self, allowed_roles: List[str]):
        """
        Inicializa el checker con los roles permitidos.
        
        Args:
            allowed_roles: Lista de roles que tienen permiso
        """
        self.allowed_roles = allowed_roles
    
    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """
        Valida que el usuario tenga uno de los roles permitidos.
        
        Args:
            current_user: Usuario actual obtenido del token
            
        Returns:
            Usuario validado
            
        Raises:
            HTTPException 403: Si el usuario no tiene permiso
        """
        if current_user.rol not in self.allowed_roles:
            logger.warning(
                f"User {current_user.nombre_usuario} with role {current_user.rol} "
                f"tried to access endpoint requiring roles {self.allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permisos para esta acción. Roles requeridos: {', '.join(self.allowed_roles)}"
            )
        return current_user


# Instancias predefinidas de RoleChecker para uso común
AdminOnly = RoleChecker(["Admin"])
PodologoOrAdmin = RoleChecker(["Admin", "Podologo"])
StaffOnly = RoleChecker(["Admin", "Podologo", "Recepcionista", "Asistente"])
