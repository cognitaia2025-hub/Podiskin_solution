"""
Middleware de Autenticación y Autorización
==========================================

Middleware para JWT authentication y RBAC authorization.
"""

from typing import List, Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from .utils import decode_token
from .database import get_user_by_username
from .models import CurrentUser

logger = logging.getLogger(__name__)

# Security scheme para bearer token
security = HTTPBearer()


# ============================================================================
# AUTHENTICATION MIDDLEWARE
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Middleware de autenticación - Verifica JWT y obtiene usuario actual
    
    Args:
        credentials: Credenciales HTTP Bearer
        
    Returns:
        Usuario actual autenticado
        
    Raises:
        HTTPException: 401 si el token es inválido o expirado
        HTTPException: 403 si el usuario está inactivo
    """
    # Extraer token
    token = credentials.credentials
    
    # Decodificar token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraer username del payload
    username: str = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: falta username",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener usuario de BD
    user_data = get_user_by_username(username)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar que el usuario esté activo
    if not user_data.get("activo", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Crear objeto CurrentUser
    current_user = CurrentUser(
        id=user_data["id"],
        username=user_data["username"],
        email=user_data["email"],
        rol=user_data["rol"],
        nombre_completo=user_data["nombre_completo"],
        activo=user_data["activo"]
    )
    
    return current_user


# ============================================================================
# AUTHORIZATION MIDDLEWARE (RBAC)
# ============================================================================

class RoleChecker:
    """
    Dependency para verificar roles de usuario (RBAC)
    """
    
    def __init__(self, allowed_roles: List[str]):
        """
        Inicializa el checker con roles permitidos
        
        Args:
            allowed_roles: Lista de roles permitidos (ej: ["Admin", "Podologo"])
        """
        self.allowed_roles = allowed_roles
    
    async def __call__(self, current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        """
        Verifica que el usuario tenga uno de los roles permitidos
        
        Args:
            current_user: Usuario actual (inyectado por get_current_user)
            
        Returns:
            Usuario actual si tiene permiso
            
        Raises:
            HTTPException: 403 si el usuario no tiene permiso
        """
        if current_user.rol not in self.allowed_roles:
            logger.warning(
                f"User {current_user.username} (rol: {current_user.rol}) "
                f"attempted to access resource requiring roles: {self.allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permisos para esta acción. Roles requeridos: {', '.join(self.allowed_roles)}"
            )
        
        return current_user


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def require_admin():
    """Require Admin role"""
    return RoleChecker(["Admin"])


def require_podologo():
    """Require Podologo role (includes Admin)"""
    return RoleChecker(["Admin", "Podologo"])


def require_recepcion():
    """Require Recepcionista role (includes Admin and Podologo)"""
    return RoleChecker(["Admin", "Podologo", "Recepcionista"])


def require_any_authenticated():
    """Require any authenticated user"""
    return RoleChecker(["Admin", "Podologo", "Recepcionista", "Asistente"])


# ============================================================================
# OPTIONAL AUTHENTICATION
# ============================================================================

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[CurrentUser]:
    """
    Middleware de autenticación opcional
    
    Retorna el usuario si está autenticado, None si no
    No lanza excepción si no hay token
    
    Args:
        credentials: Credenciales HTTP Bearer (opcional)
        
    Returns:
        Usuario actual o None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
