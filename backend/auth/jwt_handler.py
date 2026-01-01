"""
JWT Handler - Gestión de Tokens
================================

Utilidades para generar, validar y decodificar JWT tokens.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de seguridad
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-PLEASE")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Contexto para password hashing - PBKDF2 funciona correctamente en Windows (bcrypt tiene bugs en Python 3.13+)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.

    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash de la contraseña almacenada

    Returns:
        True si la contraseña es correcta, False si no
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Genera un hash de una contraseña.

    Args:
        password: Contraseña en texto plano

    Returns:
        Hash de la contraseña
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT access token.

    Args:
        data: Datos a incluir en el token (debe incluir 'sub' y 'rol')
        expires_delta: Tiempo de expiración personalizado (opcional)

    Returns:
        JWT token codificado

    Example:
        >>> token = create_access_token({"sub": "dr.santiago", "rol": "Podologo"})
    """
    to_encode = data.copy()

    # Calcular tiempo de expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Agregar timestamps
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    # Codificar el token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un JWT token.

    Args:
        token: JWT token a decodificar

    Returns:
        Payload del token si es válido, None si es inválido

    Example:
        >>> payload = decode_access_token("eyJhbGciOiJIUzI1NiIs...")
        >>> print(payload["sub"])  # "dr.santiago"
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> tuple[bool, Optional[dict]]:
    """
    Verifica si un token es válido y retorna su payload.

    Args:
        token: JWT token a verificar

    Returns:
        Tupla (es_valido, payload)
        - es_valido: True si el token es válido
        - payload: Contenido del token o None si es inválido

    Example:
        >>> is_valid, payload = verify_token(token)
        >>> if is_valid:
        >>>     username = payload["sub"]
    """
    payload = decode_access_token(token)
    if payload is None:
        return False, None

    # Verificar que tenga los campos requeridos
    required_fields = ["sub", "rol", "exp", "iat"]
    if not all(field in payload for field in required_fields):
        return False, None

    return True, payload


def get_token_expiration() -> int:
    """
    Obtiene el tiempo de expiración de tokens en segundos.

    Returns:
        Segundos de expiración
    """
    return ACCESS_TOKEN_EXPIRE_MINUTES * 60
