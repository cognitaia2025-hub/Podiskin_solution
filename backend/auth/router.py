"""
Authentication Router

Endpoints REST para autenticación (login, logout, etc.).
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Dict, List

from .models import (
    LoginRequest,
    LoginResponse,
    UserResponse,
    ErrorResponse,
    RateLimitResponse,
)
from .jwt_handler import verify_password, create_access_token, get_token_expiration, hash_password
from .database import get_user_by_username, update_last_login
from .middleware import get_current_user

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Diccionario para rate limiting simple (en producción usar Redis)
_login_attempts: Dict[str, list] = {}


def check_rate_limit(
    username: str, max_attempts: int = 5, window_seconds: int = 60
) -> tuple[bool, int]:
    """
    Verifica si un usuario ha excedido el límite de intentos de login.

    Args:
        username: Nombre de usuario
        max_attempts: Máximo de intentos permitidos
        window_seconds: Ventana de tiempo en segundos

    Returns:
        Tupla (permitido, segundos_para_reintentar)
    """
    import time

    current_time = time.time()

    # Inicializar si no existe
    if username not in _login_attempts:
        _login_attempts[username] = []

    # Limpiar intentos antiguos
    _login_attempts[username] = [
        attempt_time
        for attempt_time in _login_attempts[username]
        if current_time - attempt_time < window_seconds
    ]

    # Verificar si excede el límite
    if len(_login_attempts[username]) >= max_attempts:
        oldest_attempt = _login_attempts[username][0]
        retry_after = int(window_seconds - (current_time - oldest_attempt))
        return False, max(retry_after, 1)

    # Agregar intento actual
    _login_attempts[username].append(current_time)

    return True, 0


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Login exitoso", "model": LoginResponse},
        401: {"description": "Credenciales incorrectas", "model": ErrorResponse},
        403: {"description": "Usuario inactivo", "model": ErrorResponse},
        422: {"description": "Error de validación", "model": ErrorResponse},
        429: {"description": "Demasiados intentos", "model": RateLimitResponse},
    },
    summary="Iniciar sesión",
    description="""
    Autentica un usuario con username y password, retorna JWT token.
    
    **Flujo:**
    1. Valida formato de credenciales
    2. Verifica rate limit (5 intentos por minuto)
    3. Busca usuario en base de datos
    4. Verifica contraseña con bcrypt
    5. Verifica que usuario esté activo
    6. Genera JWT token
    7. Actualiza último acceso
    8. Retorna token + datos de usuario
    
    **Rate Limiting:** Máximo 5 intentos por minuto por usuario.
    """,
)
async def login(request: Request, credentials: LoginRequest) -> LoginResponse:
    """
    Endpoint de login - Autentica usuario y retorna JWT token.

    Args:
        request: Request de FastAPI (para obtener IP)
        credentials: Credenciales del usuario (username y password)

    Returns:
        LoginResponse con token JWT y datos del usuario

    Raises:
        HTTPException 401: Credenciales incorrectas
        HTTPException 403: Usuario inactivo
        HTTPException 429: Demasiados intentos de login
    """
    username = credentials.username
    password = credentials.password

    # ========================================================================
    # 1. VERIFICAR RATE LIMIT
    # ========================================================================
    allowed, retry_after = check_rate_limit(username)
    if not allowed:
        logger.warning(f"Rate limit exceeded for user: {username}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos. Espere antes de reintentar",
            headers={"Retry-After": str(retry_after)},
        )

    # ========================================================================
    # 2. BUSCAR USUARIO EN BASE DE DATOS
    # ========================================================================
    user_data = await get_user_by_username(username)

    if user_data is None:
        logger.warning(f"Login attempt with non-existent user: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas"
        )

    # ========================================================================
    # 3. VERIFICAR CONTRASEÑA
    # ========================================================================
    password_hash = user_data.get("password_hash")

    if not password_hash or not verify_password(password, password_hash):
        logger.warning(f"Failed login attempt for user: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas"
        )

    # ========================================================================
    # 4. VERIFICAR USUARIO ACTIVO
    # ========================================================================
    if not user_data.get("activo", False):
        logger.warning(f"Login attempt with inactive user: {username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo"
        )

    # ========================================================================
    # 5. GENERAR JWT TOKEN
    # ========================================================================
    token_data = {"sub": user_data["nombre_usuario"], "rol": user_data["rol"]}

    access_token = create_access_token(token_data)

    # ========================================================================
    # 6. ACTUALIZAR ÚLTIMO ACCESO
    # ========================================================================
    await update_last_login(user_data["id"])

    # ========================================================================
    # 7. PREPARAR RESPUESTA
    # ========================================================================
    user_response = UserResponse(
        id=user_data["id"],
        username=user_data["nombre_usuario"],
        email=user_data["email"],
        rol=user_data["rol"],
        nombre_completo=user_data["nombre_completo"],
    )

    response = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=get_token_expiration(),
        user=user_response,
    )

    logger.info(f"Successful login for user: {username}")

    return response


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión",
    description="""
    Endpoint de logout (placeholder).
    
    Nota: Con JWT stateless, el logout se maneja en el cliente eliminando el token.
    Este endpoint puede usarse para registrar el evento o invalidar tokens en una blacklist.
    """,
)
async def logout():
    """
    Endpoint de logout.

    Con JWT stateless no es necesario hacer nada en el servidor,
    el cliente simplemente elimina el token.

    En el futuro podría implementarse:
    - Blacklist de tokens
    - Registro de eventos de logout
    - Invalidación de refresh tokens
    """
    return {"message": "Sesión cerrada exitosamente"}


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Verifica que el servicio de autenticación esté funcionando",
)
async def health_check():
    """
    Health check del servicio de autenticación.

    Returns:
        Status del servicio
    """
    return {"status": "healthy", "service": "auth", "version": "1.0.0"}


# ============================================================================
# ENDPOINTS DE PERFIL DE USUARIO
# ============================================================================

from .middleware import get_current_user
from fastapi import Depends
from pydantic import BaseModel, Field
from typing import Optional


class ProfileUpdate(BaseModel):
    """Modelo para actualización de perfil."""

    nombre_completo: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[str] = Field(None, max_length=100)


class PasswordChange(BaseModel):
    """Modelo para cambio de contraseña."""

    current_password: str
    new_password: str = Field(..., min_length=6)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener perfil actual",
    description="Retorna los datos del usuario actualmente autenticado",
)
async def get_my_profile(current_user=Depends(get_current_user)):
    """Obtiene el perfil del usuario actual."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        rol=current_user.rol,
        nombre_completo=current_user.nombre_completo,
    )


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Actualizar perfil",
    description="Actualiza los datos del perfil del usuario actual",
)
async def update_my_profile(
    profile_data: ProfileUpdate, current_user=Depends(get_current_user)
):
    """Actualiza el perfil del usuario actual."""
    from .database import update_user_profile

    updates = {}
    if profile_data.nombre_completo:
        updates["nombre_completo"] = profile_data.nombre_completo
    if profile_data.email:
        updates["email"] = profile_data.email

    if updates:
        updated = await update_user_profile(current_user.id, updates)
        if updated:
            return UserResponse(
                id=current_user.id,
                username=current_user.username,
                email=updates.get("email", current_user.email),
                rol=current_user.rol,
                nombre_completo=updates.get(
                    "nombre_completo", current_user.nombre_completo
                ),
            )

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        rol=current_user.rol,
        nombre_completo=current_user.nombre_completo,
    )


@router.put(
    "/me/password",
    summary="Cambiar contraseña",
    description="Cambia la contraseña del usuario actual",
)
async def change_password(
    password_data: PasswordChange, current_user=Depends(get_current_user)
):
    """Cambia la contraseña del usuario actual."""
    from .database import get_user_by_username, update_user_password
    from .jwt_handler import verify_password, hash_password

    # Verificar contraseña actual
    user_data = await get_user_by_username(current_user.username)
    if not verify_password(password_data.current_password, user_data["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta",
        )

    # Actualizar contraseña
    new_hash = hash_password(password_data.new_password)
    await update_user_password(current_user.id, new_hash)

    return {"message": "Contraseña actualizada correctamente"}


# ============================================================================
# USER MANAGEMENT ENDPOINTS (ADMIN ONLY)
# ============================================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserListResponse(BaseModel):
    """Response model for user list"""
    id: int
    nombre_usuario: str
    nombre_completo: str
    email: str
    rol: Optional[str]
    activo: bool
    ultimo_login: Optional[datetime]
    fecha_registro: Optional[datetime]


class UserCreateRequest(BaseModel):
    """Request model for creating a new user"""
    nombre_usuario: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    nombre_completo: str = Field(..., min_length=3)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    id_rol: int = Field(..., ge=1)


class UserUpdateRequest(BaseModel):
    """Request model for updating a user"""
    nombre_completo: Optional[str] = Field(None, min_length=3)
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    id_rol: Optional[int] = Field(None, ge=1)
    activo: Optional[bool] = None


@router.get(
    "/users",
    response_model=List[UserListResponse],
    summary="Listar usuarios",
    description="Obtiene la lista de todos los usuarios del sistema. Solo administradores.",
)
async def list_users(
    activo_only: bool = True,
    current_user=Depends(get_current_user)
):
    """Lista todos los usuarios del sistema."""
    # Verificar que sea admin
    if current_user.rol != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden listar usuarios"
        )
    
    from .database import get_all_users
    users = await get_all_users(activo_only=activo_only)
    return users


@router.post(
    "/users",
    response_model=UserListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario en el sistema. Solo administradores.",
)
async def create_user_endpoint(
    user_data: UserCreateRequest,
    current_user=Depends(get_current_user)
):
    """Crea un nuevo usuario."""
    # Verificar que sea admin
    if current_user.rol != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden crear usuarios"
        )
    
    from .database import create_user
    
    # Hash de la contraseña
    password_hash = hash_password(user_data.password)
    
    # Crear usuario
    new_user = await create_user(
        nombre_usuario=user_data.nombre_usuario,
        password_hash=password_hash,
        nombre_completo=user_data.nombre_completo,
        email=user_data.email,
        id_rol=user_data.id_rol,
        creado_por=current_user.id
    )
    
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear usuario. El nombre de usuario o email puede estar duplicado."
        )
    
    return new_user


@router.get(
    "/users/{user_id}",
    response_model=UserListResponse,
    summary="Obtener usuario",
    description="Obtiene un usuario por su ID. Solo administradores.",
)
async def get_user_endpoint(
    user_id: int,
    current_user=Depends(get_current_user)
):
    """Obtiene un usuario por ID."""
    # Verificar que sea admin
    if current_user.rol != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden ver usuarios"
        )
    
    from .database import get_user_by_id
    user = await get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user


@router.put(
    "/users/{user_id}",
    response_model=UserListResponse,
    summary="Actualizar usuario",
    description="Actualiza un usuario existente. Solo administradores.",
)
async def update_user_endpoint(
    user_id: int,
    user_data: UserUpdateRequest,
    current_user=Depends(get_current_user)
):
    """Actualiza un usuario existente."""
    # Verificar que sea admin
    if current_user.rol != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden actualizar usuarios"
        )
    
    from .database import update_user
    
    updated_user = await update_user(
        user_id=user_id,
        nombre_completo=user_data.nombre_completo,
        email=user_data.email,
        id_rol=user_data.id_rol,
        activo=user_data.activo
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return updated_user


@router.delete(
    "/users/{user_id}",
    summary="Desactivar usuario",
    description="Desactiva un usuario (soft delete). Solo administradores.",
)
async def delete_user_endpoint(
    user_id: int,
    current_user=Depends(get_current_user)
):
    """Desactiva un usuario (soft delete)."""
    # Verificar que sea admin
    if current_user.rol != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden desactivar usuarios"
        )
    
    # No permitir que un admin se desactive a sí mismo
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta"
        )
    
    from .database import delete_user
    success = await delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return {"message": "Usuario desactivado correctamente", "id": user_id}
