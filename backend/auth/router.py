"""
Authentication Router

Endpoints REST para autenticación (login, logout, etc.).
"""

from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
import logging
from typing import Dict

from .models import (
    LoginRequest,
    LoginResponse,
    UserResponse,
    ErrorResponse,
    RateLimitResponse,
)
from .jwt_handler import verify_password, create_access_token, get_token_expiration
from .database import get_user_by_username, update_last_login

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
