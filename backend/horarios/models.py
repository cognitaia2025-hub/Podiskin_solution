"""Modelos Pydantic para Horarios."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import time, date

class HorarioCreate(BaseModel):
    """Modelo para crear un horario de trabajo."""
    id_podologo: int = Field(..., description="ID del podólogo")
    dia_semana: int = Field(..., ge=0, le=6, description="0=Domingo, 6=Sábado")
    hora_inicio: time = Field(..., description="Hora de inicio (HH:MM)")
    hora_fin: time = Field(..., description="Hora de fin (HH:MM)")
    duracion_cita_minutos: int = Field(30, ge=15, le=120, description="Duración de cada cita")
    tiempo_buffer_minutos: int = Field(5, ge=0, le=30, description="Tiempo entre citas")
    max_citas_simultaneas: int = Field(1, ge=1, le=5, description="Máximo de citas simultáneas")
    fecha_inicio_vigencia: Optional[date] = None
    fecha_fin_vigencia: Optional[date] = None
    activo: bool = True

class HorarioUpdate(BaseModel):
    """Modelo para actualizar un horario."""
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    duracion_cita_minutos: Optional[int] = Field(None, ge=15, le=120)
    tiempo_buffer_minutos: Optional[int] = Field(None, ge=0, le=30)
    max_citas_simultaneas: Optional[int] = Field(None, ge=1, le=5)
    fecha_fin_vigencia: Optional[date] = None
    activo: Optional[bool] = None

class HorarioResponse(BaseModel):
    """Modelo de respuesta de horario."""
    id: int
    id_podologo: int
    nombre_podologo: str
    dia_semana: int
    dia_semana_nombre: str
    hora_inicio: str
    hora_fin: str
    duracion_cita_minutos: int
    tiempo_buffer_minutos: int
    max_citas_simultaneas: int
    activo: bool
    fecha_inicio_vigencia: Optional[date]
    fecha_fin_vigencia: Optional[date]
    
    class Config:
        from_attributes = True
