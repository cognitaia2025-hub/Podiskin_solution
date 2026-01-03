from pydantic import BaseModel, Field
from typing import Optional, Literal


# Tipos simples sin Enum para evitar problemas de validación
TipoServicio = Literal["servicio", "tratamiento"]
CategoriaServicio = Literal["general", "podologia", "estetica", "cirugia", "diagnostico"]

TIPOS_DISPONIBLES = ["servicio", "tratamiento"]
CATEGORIAS_DISPONIBLES = ["general", "podologia", "estetica", "cirugia", "diagnostico"]


class ServiceBase(BaseModel):
    nombre: str = Field(..., example="Consulta General")
    descripcion: Optional[str] = Field(None, example="Consulta médica general")
    precio: float = Field(..., example=500.0)
    duracion_minutos: int = Field(..., example=30)
    tipo: str = Field(default="servicio", example="servicio")
    categoria: str = Field(default="general", example="general")
    activo: Optional[bool] = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    duracion_minutos: Optional[int] = None
    tipo: Optional[str] = None
    categoria: Optional[str] = None
    activo: Optional[bool] = None


class ServiceResponse(ServiceBase):
    id: int

    class Config:
        from_attributes = True
