"""
Modelos Pydantic para Autenticación
====================================

Modelos de datos para endpoints de autenticación y autorización.
Modelos para request/response de autenticación y usuarios.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


class LoginRequest(BaseModel):
    """Modelo para request de login - acepta username, email o teléfono"""
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nombre de usuario, email o teléfono (3-50 caracteres)"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Contraseña (8-100 caracteres)"
    )
    
    @validator('username')
    def validate_username(cls, v):
        """
        Valida que el identificador sea válido:
        - Username: alfanumérico + _ + .
        - Email: formato email válido
        - Teléfono: solo dígitos
        """
        # Permitir username alfanumérico
        if re.match(r'^[a-zA-Z0-9_.]+$', v):
            return v
        # Permitir email
        if re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            return v
        # Permitir teléfono (solo dígitos)
        if re.match(r'^\d+$', v):
            return v
        
        raise ValueError('Debe proporcionar un nombre de usuario, email o teléfono válido')
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "dr.santiago",
                "password": "password123"
            }
        }


class UserResponse(BaseModel):
    """Modelo de datos del usuario en la respuesta"""
    
    id: int
    username: str
    email: str
    rol: str
    nombre_completo: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "dr.santiago",
                "email": "santiago@podoskin.com",
                "rol": "Podologo",
                "nombre_completo": "Dr. Santiago Ornelas"
            }
        }


class LoginResponse(BaseModel):
    """Modelo para response de login exitoso"""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(default=3600, description="Tiempo de expiración en segundos")
    user: UserResponse = Field(..., description="Datos del usuario autenticado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "id": 1,
                    "username": "dr.santiago",
                    "email": "santiago@podoskin.com",
                    "rol": "Podologo",
                    "nombre_completo": "Dr. Santiago Ornelas"
                }
            }
        }


class TokenData(BaseModel):
    """Modelo para datos contenidos en el JWT token"""
    
    sub: str = Field(..., description="Subject (username)")
    rol: str = Field(..., description="Rol del usuario")
    exp: int = Field(..., description="Timestamp de expiración")
    iat: int = Field(..., description="Timestamp de emisión")


class User(BaseModel):
    """Modelo completo de usuario (para uso interno)"""
    
    id: int
    nombre_usuario: str
    email: str
    rol: str
    nombre_completo: str
    activo: bool
    ultimo_login: Optional[datetime] = None
    fecha_registro: Optional[datetime] = None
    password_hash: Optional[str] = None  # Solo para verificación interna
    
    class Config:
        from_attributes = True  # Para Pydantic v2 (antes era orm_mode)


class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""
    
    detail: str = Field(..., description="Mensaje de error")
    error_code: str = Field(..., description="Código de error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Credenciales incorrectas",
                "error_code": "AUTH_INVALID_CREDENTIALS"
            }
        }


class RateLimitResponse(BaseModel):
    """Modelo para respuesta de rate limit excedido"""
    
    detail: str = Field(..., description="Mensaje de error")
    error_code: str = Field(default="RATE_LIMIT_EXCEEDED", description="Código de error")
    retry_after: int = Field(..., description="Segundos para reintentar")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Demasiados intentos. Espere 60 segundos",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "retry_after": 60
            }
        }
