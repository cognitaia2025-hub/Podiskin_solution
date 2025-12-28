"""
Modelos Pydantic para Autenticación
====================================

Modelos de datos para endpoints de autenticación y autorización.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


class LoginRequest(BaseModel):
    """Request para login de usuario"""
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nombre de usuario (3-50 caracteres, alfanumérico + _)"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Contraseña (8-100 caracteres)"
    )
    
    @validator('username')
    def validate_username(cls, v):
        """Valida formato del username"""
        if not re.match(r'^[a-zA-Z0-9_.]+$', v):
            raise ValueError('Username debe contener solo caracteres alfanuméricos, puntos y guiones bajos')
        return v


class UserResponse(BaseModel):
    """Información del usuario en respuesta"""
    
    id: int
    username: str
    email: str
    rol: str
    nombre_completo: str


class LoginResponse(BaseModel):
    """Response para login exitoso"""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user: UserResponse


class TokenPayload(BaseModel):
    """Payload del JWT token"""
    
    sub: str  # username
    rol: str
    exp: int  # expiration timestamp
    iat: int  # issued at timestamp


class CurrentUser(BaseModel):
    """Usuario actual autenticado"""
    
    id: int
    username: str
    email: str
    rol: str
    nombre_completo: str
    activo: bool
    
    class Config:
        from_attributes = True
