from pydantic import BaseModel, Field
from typing import Optional

class ServiceBase(BaseModel):
    nombre: str = Field(..., example="Consulta General")
    descripcion: Optional[str] = Field(None, example="Consulta médica general")
    precio: float = Field(..., example=500.0)
    duracion_minutos: int = Field(..., example=30)
    activo: Optional[bool] = True

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(ServiceBase):
    pass

class ServiceResponse(ServiceBase):
    id: int

    class Config:
        orm_mode = True
