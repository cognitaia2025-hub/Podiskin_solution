"""
Módulo de Autenticación

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
Auth Module

Módulo de autenticación y autorización para Podoskin Solution.

Includes:
- JWT token generation and validation
- Password hashing with bcrypt
- Authentication middleware
- RBAC authorization
- Login endpoint
"""

from .models import (
    LoginRequest,
    LoginResponse,
    UserResponse,
    TokenData,
    User,
    ErrorResponse,
    RateLimitResponse
)

from .jwt_handler import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    verify_token,
    get_token_expiration
)

from .middleware import (
    get_current_user,
    get_current_active_user,
    get_optional_current_user
)

from .authorization import (
    require_role,
    require_admin,
    require_podologo,
    require_staff,
    check_user_permission,
    verify_user_owns_resource,
    RoleChecker,
    AdminOnly,
    PodologoOrAdmin,
    StaffOnly
)

from .router import router as auth_router

from .database import (
    init_db_pool,
    close_db_pool,
    get_user_by_username,
    update_last_login,
    is_user_active
)

__all__ = [
    # Models
    "LoginRequest",
    "LoginResponse",
    "UserResponse",
    "TokenData",
    "User",
    "ErrorResponse",
    "RateLimitResponse",
    
    # JWT Handler
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_access_token",
    "verify_token",
    "get_token_expiration",
    
    # Middleware
    "get_current_user",
    "get_current_active_user",
    "get_optional_current_user",
    
    # Authorization
    "require_role",
    "require_admin",
    "require_podologo",
    "require_staff",
    "check_user_permission",
    "verify_user_owns_resource",
    "RoleChecker",
    "AdminOnly",
    "PodologoOrAdmin",
    "StaffOnly",
    
    # Router
    "auth_router",
    
    # Database
    "init_db_pool",
    "close_db_pool",
    "get_user_by_username",
    "update_last_login",
    "is_user_active",
]
