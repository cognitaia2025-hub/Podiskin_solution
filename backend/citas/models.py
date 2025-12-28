"""
Modelos Pydantic para el módulo de citas
=========================================

Define los esquemas de request/response para los endpoints REST.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# ENUMS
# ============================================================================


class TipoCita(str, Enum):
    """Tipos de cita disponibles."""
    CONSULTA = "Consulta"
    SEGUIMIENTO = "Seguimiento"
    URGENCIA = "Urgencia"


class EstadoCita(str, Enum):
    """Estados posibles de una cita."""
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    EN_CURSO = "En_Curso"
    COMPLETADA = "Completada"
    CANCELADA = "Cancelada"
    NO_ASISTIO = "No_Asistio"


# ============================================================================
# REQUEST MODELS
# ============================================================================


class CitaCreate(BaseModel):
    """Modelo para crear una nueva cita."""
    id_paciente: int = Field(..., gt=0, description="ID del paciente")
    id_podologo: int = Field(..., gt=0, description="ID del podólogo")
    fecha_hora_inicio: datetime = Field(..., description="Fecha y hora de inicio (YYYY-MM-DDTHH:mm:ss)")
    tipo_cita: TipoCita = Field(default=TipoCita.CONSULTA, description="Tipo de cita")
    motivo_consulta: Optional[str] = Field(None, max_length=500, description="Motivo de la consulta")
    notas_recepcion: Optional[str] = Field(None, max_length=500, description="Notas de recepción")

    @field_validator("fecha_hora_inicio")
    @classmethod
    def validate_fecha_hora(cls, v: datetime) -> datetime:
        """Valida que la fecha sea futura (al menos 1 hora desde ahora)."""
        if v.tzinfo is None:
            # Si no tiene timezone, asumimos que es local
            from datetime import timezone
            v = v.replace(tzinfo=timezone.utc)
        return v


class CitaUpdate(BaseModel):
    """Modelo para actualizar una cita existente."""
    fecha_hora_inicio: Optional[datetime] = None
    tipo_cita: Optional[TipoCita] = None
    motivo_consulta: Optional[str] = Field(None, max_length=500)
    notas_recepcion: Optional[str] = Field(None, max_length=500)
    estado: Optional[EstadoCita] = None


class CitaCancel(BaseModel):
    """Modelo para cancelar una cita."""
    motivo_cancelacion: str = Field(..., min_length=3, max_length=500, description="Motivo de la cancelación")


# ============================================================================
# RESPONSE MODELS
# ============================================================================


class PacienteInfo(BaseModel):
    """Información básica del paciente."""
    id: int
    nombre_completo: str


class PodologoInfo(BaseModel):
    """Información básica del podólogo."""
    id: int
    nombre_completo: str


class CitaResponse(BaseModel):
    """Modelo de respuesta para una cita."""
    id: int
    id_paciente: int
    id_podologo: int
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    tipo_cita: str
    estado: str
    motivo_consulta: Optional[str] = None
    notas_recepcion: Optional[str] = None
    motivo_cancelacion: Optional[str] = None
    es_primera_vez: bool
    recordatorio_24h_enviado: bool
    recordatorio_2h_enviado: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    # Información relacionada
    paciente: Optional[PacienteInfo] = None
    podologo: Optional[PodologoInfo] = None

    model_config = {
        "from_attributes": True
    }


class CitaListResponse(BaseModel):
    """Modelo de respuesta para lista de citas."""
    total: int
    citas: List[CitaResponse]


# ============================================================================
# DISPONIBILIDAD
# ============================================================================


class SlotDisponibilidad(BaseModel):
    """Slot de tiempo con disponibilidad."""
    hora: str = Field(..., description="Hora en formato HH:MM")
    disponible: bool
    motivo: Optional[str] = Field(None, description="Motivo si no está disponible")


class DisponibilidadResponse(BaseModel):
    """Respuesta de disponibilidad de horarios."""
    fecha: str
    podologo: PodologoInfo
    slots: List[SlotDisponibilidad]
