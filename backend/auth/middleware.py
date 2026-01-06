"""
Middleware de Autenticación y Autorización

Middleware para JWT authentication y RBAC authorization.
"""

from typing import List, Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from .jwt_handler import verify_token
from .database import get_user_by_username, is_user_active
from .models import User, TokenData

logger = logging.getLogger(__name__)

# Security scheme para bearer token
security = HTTPBearer()


# ============================================================================
# AUTHENTICATION MIDDLEWARE
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency para obtener el usuario actual desde el JWT token.
    
    Valida el token JWT y retorna los datos del usuario.
    Lanza HTTPException si el token es inválido o el usuario no existe.
    
    Args:
        credentials: Credenciales HTTP Bearer del request
        
    Returns:
        Objeto User con los datos del usuario autenticado
        
    Raises:
        HTTPException 401: Si el token es inválido o expirado
        HTTPException 403: Si el usuario está inactivo o el token está revocado
        HTTPException 404: Si el usuario no existe
        
    Example:
        >>> @router.get("/protected")
        >>> async def protected_route(current_user: User = Depends(get_current_user)):
        >>>     return {"message": f"Hello {current_user.nombre_completo}"}
    """
    # Extraer el token
    token = credentials.credentials
    
    # Verificar si el token está en la blacklist (revocado)
    # Import local para evitar import circular
    from .router import is_token_blacklisted
    if is_token_blacklisted(token):
        logger.warning("Revoked token attempted to access resource")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revocado. Por favor, inicie sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validar y decodificar el token
    is_valid, payload = verify_token(token)
    
    if not is_valid or payload is None:
        logger.warning("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraer username del token
    username: str = payload.get("sub")
    if username is None:
        logger.warning("Token without username")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar usuario en base de datos
    user_data = await get_user_by_username(username)
    if user_data is None:
        logger.warning(f"User not found: {username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar que el usuario esté activo
    if not user_data.get("activo", False):
        logger.warning(f"Inactive user tried to access: {username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Crear objeto User
    return User(**user_data)


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
    
    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
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
) -> Optional[User]:
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


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency para obtener el usuario actual y verificar que esté activo.
    
    Este es un wrapper adicional de get_current_user para casos donde se necesite
    verificación explícita de usuario activo.
    
    Args:
        current_user: Usuario obtenido de get_current_user
        
    Returns:
        Objeto User verificado como activo
        
    Raises:
        HTTPException 403: Si el usuario está inactivo
        
    Example:
        >>> @router.post("/action")
        >>> async def action(user: User = Depends(get_current_active_user)):
        >>>     return {"status": "ok"}
    """
    if not current_user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Dependency para obtener el usuario actual opcionalmente.
    
    Similar a get_current_user pero no lanza excepción si no hay token,
    simplemente retorna None.
    
    Args:
        credentials: Credenciales HTTP Bearer del request (opcional)
        
    Returns:
        Objeto User si hay token válido, None si no hay token o es inválido
        
    Example:
        >>> @router.get("/public")
        >>> async def public_route(user: Optional[User] = Depends(get_optional_current_user)):
        >>>     if user:
        >>>         return {"message": f"Hello {user.nombre_completo}"}
        >>>     return {"message": "Hello guest"}
    """
    if credentials is None:
        return None
    
    try:
        # Intentar obtener usuario
        token = credentials.credentials
        is_valid, payload = verify_token(token)
        
        if not is_valid or payload is None:
            return None
        
        username = payload.get("sub")
        if username is None:
            return None
        
        # Buscar usuario (esto debe ser async pero para mantener compatibilidad...)
        # En producción considerar usar asyncio.create_task o similar
        import asyncio
        user_data = asyncio.run(get_user_by_username(username))
        
        if user_data is None or not user_data.get("activo", False):
            return None
        
        return User(**user_data)
    except Exception as e:
        logger.debug(f"Error getting optional user: {e}")
        return None
