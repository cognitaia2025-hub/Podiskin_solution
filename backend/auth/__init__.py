"""
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
    RateLimitResponse,
)

from .jwt_handler import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    verify_token,
    get_token_expiration,
)

from .middleware import (
    get_current_user,
    get_current_active_user,
    get_optional_current_user,
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
    StaffOnly,
)

from .router import router as auth_router

from .database import get_user_by_username, update_last_login, is_user_active

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
    "get_user_by_username",
    "update_last_login",
    "is_user_active",
]
