"""
Modelos Pydantic para Podólogos
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime


class PodologoBase(BaseModel):
    """Base para Podólogo"""
    cedula_profesional: str = Field(..., description="Cédula profesional única")
    nombre_completo: str = Field(..., min_length=1, max_length=255)
    especialidad: Optional[str] = Field(None, max_length=255)
    telefono: str = Field(..., max_length=20)
    email: Optional[EmailStr] = None
    fecha_contratacion: Optional[date] = None


class PodologoCreate(PodologoBase):
    """Crear nuevo Podólogo"""
    id_usuario: Optional[int] = Field(None, description="ID del usuario asociado")
    activo: bool = Field(True, description="Estado activo/inactivo")


class PodologoUpdate(BaseModel):
    """Actualizar Podólogo existente"""
    cedula_profesional: Optional[str] = None
    nombre_completo: Optional[str] = Field(None, min_length=1, max_length=255)
    especialidad: Optional[str] = Field(None, max_length=255)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    activo: Optional[bool] = None
    fecha_contratacion: Optional[date] = None
    id_usuario: Optional[int] = None


class PodologoResponse(PodologoBase):
    """Respuesta de Podólogo"""
    id: int
    activo: bool
    fecha_registro: datetime
    id_usuario: Optional[int] = None

    class Config:
        from_attributes = True


class PodologoListItem(BaseModel):
    """Item resumido para listados"""
    id: int
    nombre_completo: str
    cedula_profesional: str
    especialidad: Optional[str]
    telefono: str
    email: Optional[str]
    activo: bool

    class Config:
        from_attributes = True
