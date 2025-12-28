"""
Módulo de Autenticación
========================

Sistema de autenticación JWT con middleware RBAC para FastAPI.

Exports principales:
- router: APIRouter con endpoints de autenticación
- get_current_user: Middleware para obtener usuario autenticado
- RoleChecker: Middleware para verificar roles (RBAC)
- require_admin, require_podologo, require_recepcion: Helpers de autorización
"""

from .router import router
from .middleware import (
    get_current_user,
    get_current_user_optional,
    RoleChecker,
    require_admin,
    require_podologo,
    require_recepcion,
    require_any_authenticated
)
from .models import CurrentUser, LoginRequest, LoginResponse, UserResponse

__all__ = [
    # Router
    "router",
    
    # Middleware de autenticación
    "get_current_user",
    "get_current_user_optional",
    
    # Middleware de autorización (RBAC)
    "RoleChecker",
    "require_admin",
    "require_podologo",
    "require_recepcion",
    "require_any_authenticated",
    
    # Modelos
    "CurrentUser",
    "LoginRequest",
    "LoginResponse",
    "UserResponse",
]
