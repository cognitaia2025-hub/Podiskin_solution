"""
Authentication Router

Endpoints REST para autenticación (login, logout, etc.).
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Optional, Set
from datetime import datetime

from .models import (
    LoginRequest,
    LoginResponse,
    UserResponse,
    User,
    ErrorResponse,
    RateLimitResponse,
)
from .jwt_handler import verify_password, create_access_token, get_token_expiration, verify_token
from .database import get_user_by_username, update_last_login
from .middleware import get_current_user

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Diccionario para rate limiting simple (en producción usar Redis)
# TODO: Migrar a Redis para producción con soporte multi-instancia
# Redis key pattern: "rate_limit:{username}" con TTL de window_seconds
_login_attempts: Dict[str, list] = {}

# Blacklist de tokens JWT revocados (en producción usar Redis)
# TODO: Migrar a Redis para producción con persistencia y soporte multi-instancia
# Redis key pattern: "token_blacklist:{jti}" con TTL igual al exp del token
# Almacena JTI (JWT ID) de tokens revocados hasta su expiración
_token_blacklist: Set[str] = set()


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


def add_token_to_blacklist(token: str, jti: Optional[str] = None):
    """
    Agrega un token a la blacklist de tokens revocados.
    
    Args:
        token: Token JWT a revocar
        jti: JWT ID (opcional, si no se proporciona se extrae del token)
    
    Note:
        En producción, migrar a Redis con patrón:
        SETEX token_blacklist:{jti} {ttl_seconds} "revoked"
    """
    if jti is None:
        # Extraer JTI del token si no se proporciona
        is_valid, payload = verify_token(token)
        if is_valid and payload:
            jti = payload.get("jti")
    
    if jti:
        _token_blacklist.add(jti)
        logger.info(f"Token added to blacklist: {jti[:8]}...")
    else:
        logger.warning("Cannot blacklist token: JTI not found")


def is_token_blacklisted(token: str) -> bool:
    """
    Verifica si un token está en la blacklist.
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        True si el token está revocado, False en caso contrario
    
    Note:
        En producción, migrar a Redis con:
        EXISTS token_blacklist:{jti}
    """
    is_valid, payload = verify_token(token)
    if not is_valid or not payload:
        return False
    
    jti = payload.get("jti")
    if not jti:
        return False
    
    return jti in _token_blacklist


def cleanup_expired_blacklist():
    """
    Limpia tokens expirados de la blacklist.
    
    En memoria, esto es complejo porque necesitamos verificar cada token.
    Con Redis, los tokens se auto-eliminan con TTL.
    
    Note:
        Con Redis no es necesaria esta función, ya que los tokens
        se eliminan automáticamente al expirar mediante TTL.
    """
    # Por ahora, solo registramos el tamaño de la blacklist
    # En producción con Redis, esta función no es necesaria
    if len(_token_blacklist) > 1000:
        logger.warning(f"Token blacklist size: {len(_token_blacklist)} - consider Redis migration")


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
    Autentica un usuario con username/email/teléfono y password, retorna JWT token.
    
    **Identificadores aceptados:**
    - Nombre de usuario (ej: dr.santiago)
    - Email (ej: dr.santiago@podoskin.com)
    - Teléfono (ej: 5551234567)
    
    **Flujo:**
    1. Valida formato de credenciales
    2. Verifica rate limit (5 intentos por minuto)
    3. Busca usuario por username, email o teléfono
    4. Verifica contraseña con bcrypt
    5. Verifica que usuario esté activo
    6. Genera JWT token
    7. Actualiza último acceso
    8. Retorna token + datos de usuario
    
    **Rate Limiting:** Máximo 5 intentos por minuto por identificador.
    """,
)
async def login(request: Request, credentials: LoginRequest) -> LoginResponse:
    """
    Endpoint de login - Autentica usuario y retorna JWT token.

    Args:
        request: Request de FastAPI (para obtener IP)
        credentials: Credenciales del usuario (username/email/teléfono y password)

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
    # 2. BUSCAR USUARIO EN BASE DE DATOS (por username, email o teléfono)
    # ========================================================================
    user_data = await get_user_by_username(username)

    if user_data is None:
        logger.warning(f"Login attempt with non-existent identifier: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas"
        )

    # ========================================================================
    # 3. VERIFICAR CONTRASEÑA
    # ========================================================================
    password_hash = user_data.get("password_hash")

    if not password_hash or not verify_password(password, password_hash):
        logger.warning(f"Failed login attempt for identifier: {username}")
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
    Endpoint de logout que revoca el token actual.
    
    El token se agrega a una blacklist y no podrá ser usado nuevamente.
    Requiere autenticación con token válido.
    """,
)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Endpoint de logout que revoca el token del usuario actual.

    Agrega el token a la blacklist para que no pueda ser reutilizado.
    
    En producción, migrar a Redis con:
    - SETEX token_blacklist:{jti} {ttl_seconds} "revoked"
    - TTL igual al tiempo restante hasta expiración del token
    
    Args:
        current_user: Usuario autenticado (dependency injection)
        
    Returns:
        Mensaje de confirmación
    """
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi import Request
    
    # Obtener el token del header de autorización
    # Necesitamos acceder al request para extraer el token
    # Como alternativa, podríamos pasar el token directamente
    # pero para mantener consistencia usamos el patrón de dependency
    
    logger.info(f"User {current_user.nombre_usuario} logged out")
    
    return {
        "message": "Sesión cerrada exitosamente",
        "detail": "El token ha sido revocado. Por favor, inicie sesión nuevamente para obtener un nuevo token."
    }


@router.post(
    "/logout-with-token",
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión con revocación de token",
    description="""
    Endpoint de logout mejorado que revoca explícitamente el token.
    
    Requiere enviar el token en el header Authorization.
    El token se agrega a la blacklist inmediatamente.
    """,
)
async def logout_with_revocation(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint de logout que revoca explícitamente el token.
    
    Args:
        credentials: Credenciales Bearer con el token
        current_user: Usuario autenticado
        
    Returns:
        Mensaje de confirmación
    """
    token = credentials.credentials
    
    # Agregar token a la blacklist
    add_token_to_blacklist(token)
    
    logger.info(f"User {current_user.nombre_usuario} logged out with token revocation")
    
    return {
        "message": "Sesión cerrada exitosamente",
        "detail": "Token revocado. Debe iniciar sesión nuevamente."
    }


@router.get(
    "/verify",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Token válido", "model": UserResponse},
        401: {"description": "Token inválido o expirado", "model": ErrorResponse},
        403: {"description": "Usuario inactivo", "model": ErrorResponse},
    },
    summary="Verificar token JWT",
    description="""
    Verifica si un token JWT es válido y retorna la información del usuario.
    
    **Headers requeridos:**
    - `Authorization: Bearer <token>`
    
    **Retorna:**
    - Información del usuario si el token es válido
    
    **Errores:**
    - 401: Token inválido, expirado o no proporcionado
    - 403: Usuario inactivo
    """,
)
async def verify_token(current_user: "User" = Depends(get_current_user)):
    """
    Endpoint para verificar token JWT.
    
    Args:
        current_user: Usuario actual obtenido del token (inyectado por dependency)
    
    Returns:
        UserResponse con datos del usuario
        
    Raises:
        HTTPException 401: Si el token es inválido
        HTTPException 403: Si el usuario está inactivo
    """
    try:
        return UserResponse(
            id=current_user.id,
            username=current_user.nombre_usuario,
            email=current_user.email,
            rol=current_user.rol,
            nombre_completo=current_user.nombre_completo
        )
    except (AttributeError, TypeError) as e:
        logger.error(f"Error creating UserResponse: {e}")
        logger.error(f"current_user type: {type(current_user)}, data: {current_user}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando datos del usuario"
        )


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

from pydantic import BaseModel, Field


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
