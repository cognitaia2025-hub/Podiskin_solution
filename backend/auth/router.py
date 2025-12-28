"""
Router de Autenticación
=======================

Endpoints REST para autenticación de usuarios.
"""

from fastapi import APIRouter, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from .models import LoginRequest, LoginResponse, UserResponse
from .utils import verify_password, create_access_token
from .database import get_user_by_username, update_last_login

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login de usuario",
    description="Autentica un usuario y retorna un JWT token"
)
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginRequest):
    """
    Endpoint de login
    
    **Flujo**:
    1. Valida formato de username/password
    2. Busca usuario en BD
    3. Verifica contraseña con bcrypt
    4. Verifica que usuario esté activo
    5. Genera JWT token
    6. Actualiza último login
    7. Retorna token y datos de usuario
    
    **Rate Limit**: 5 intentos por minuto por IP
    
    Args:
        request: Request object (para rate limiting)
        credentials: Username y password
        
    Returns:
        LoginResponse con access_token y datos del usuario
        
    Raises:
        HTTPException 401: Credenciales incorrectas
        HTTPException 403: Usuario inactivo
        HTTPException 422: Datos de entrada inválidos
        HTTPException 429: Rate limit excedido
    """
    # 1. Buscar usuario en BD
    user = get_user_by_username(credentials.username)
    
    # 2. Verificar que el usuario existe
    if not user:
        logger.warning(f"Login attempt for non-existent user: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"error_code": "AUTH_INVALID_CREDENTIALS"}
        )
    
    # 3. Verificar contraseña
    if not verify_password(credentials.password, user["password_hash"]):
        logger.warning(f"Invalid password for user: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"error_code": "AUTH_INVALID_CREDENTIALS"}
        )
    
    # 4. Verificar que el usuario esté activo
    if not user.get("activo", False):
        logger.warning(f"Login attempt for inactive user: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
            headers={"error_code": "AUTH_USER_INACTIVE"}
        )
    
    # 5. Generar JWT token
    token_data = {
        "sub": user["username"],
        "rol": user["rol"]
    }
    access_token = create_access_token(token_data)
    
    # 6. Actualizar último login
    update_last_login(user["id"])
    
    # 7. Preparar respuesta
    user_response = UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        rol=user["rol"],
        nombre_completo=user["nombre_completo"]
    )
    
    logger.info(f"Successful login for user: {credentials.username}")
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=3600,
        user=user_response
    )


@router.get(
    "/test",
    status_code=status.HTTP_200_OK,
    summary="Test endpoint",
    description="Endpoint de prueba para verificar que el router funciona"
)
async def test_auth():
    """
    Endpoint de prueba
    
    Returns:
        Mensaje de confirmación
    """
    return {
        "status": "ok",
        "message": "Auth router is working",
        "endpoints": [
            "POST /auth/login - Login de usuario"
        ]
    }
