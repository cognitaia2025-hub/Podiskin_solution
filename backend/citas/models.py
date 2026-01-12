"""
Modelos Pydantic para el módulo de citas
=========================================

Define los esquemas de request/response para los endpoints REST.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator


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


class UnidadTiempo(str, Enum):
    """Unidades de tiempo para recordatorios."""

    MINUTOS = "minutos"
    HORAS = "horas"
    DIAS = "días"


class MetodoEnvio(str, Enum):
    """Métodos de envío de recordatorios."""

    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"


class FrecuenciaRecurrencia(str, Enum):
    """Frecuencias de recurrencia."""

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


# ============================================================================
# REQUEST MODELS
# ============================================================================


class PacienteNuevoInput(BaseModel):
    """Datos mínimos para crear un paciente "walk-in" desde el flujo de cita."""

    primer_nombre: str = Field(..., min_length=1, max_length=50)
    segundo_nombre: Optional[str] = Field(None, max_length=50)
    primer_apellido: str = Field(..., min_length=1, max_length=50)
    segundo_apellido: Optional[str] = Field(None, max_length=50)
    telefono_principal: str = Field(..., min_length=7, max_length=20)


class CitaCreate(BaseModel):
    """Modelo para crear una nueva cita (Smart Create).

    Acepta o bien `id_paciente` (paciente existente) o bien `nuevo_paciente`.
    El frontend debe enviar `fecha_hora_inicio` y `fecha_hora_fin`.
    """

    id_paciente: Optional[int] = Field(
        None, gt=0, description="ID del paciente existente"
    )
    nuevo_paciente: Optional[PacienteNuevoInput] = None
    id_podologo: int = Field(..., gt=0, description="ID del podólogo")
    id_tratamiento: Optional[int] = Field(
        None, gt=0, description="ID del tratamiento a aplicar"
    )
    fecha_hora_inicio: datetime = Field(..., description="Fecha y hora de inicio")
    fecha_hora_fin: datetime = Field(..., description="Fecha y hora de fin")
    tipo_cita: TipoCita = Field(default=TipoCita.CONSULTA, description="Tipo de cita")
    motivo_consulta: Optional[str] = Field(
        None, max_length=500, description="Motivo de la consulta"
    )
    notas_recepcion: Optional[str] = Field(
        None, max_length=500, description="Notas de recepción"
    )
    color_hex: Optional[str] = Field(
        None, description="Color opcional para la cita en formato HEX, ej. #FFAA00"
    )

    @model_validator(mode="after")
    def check_patient_or_new(self):
        if not self.id_paciente and not self.nuevo_paciente:
            raise ValueError("Debe proporcionar `id_paciente` o `nuevo_paciente`")
        if self.id_paciente and self.nuevo_paciente:
            raise ValueError(
                "Proporcione sólo `id_paciente` o `nuevo_paciente`, no ambos"
            )
        if (
            self.fecha_hora_inicio
            and self.fecha_hora_fin
            and self.fecha_hora_fin <= self.fecha_hora_inicio
        ):
            raise ValueError(
                "`fecha_hora_fin` debe ser posterior a `fecha_hora_inicio`"
            )
        return self


class CitaUpdate(BaseModel):
    """Modelo para actualizar una cita existente."""

    fecha_hora_inicio: Optional[datetime] = None
    tipo_cita: Optional[TipoCita] = None
    motivo_consulta: Optional[str] = Field(None, max_length=500)
    notas_recepcion: Optional[str] = Field(None, max_length=500)
    estado: Optional[EstadoCita] = None


class CitaCancel(BaseModel):
    """Modelo para cancelar una cita."""

    motivo_cancelacion: str = Field(
        ..., min_length=3, max_length=500, description="Motivo de la cancelación"
    )


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

    model_config = {"from_attributes": True}


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


# ============================================================================
# RECORDATORIOS
# ============================================================================


class RecordatorioCreate(BaseModel):
    """Modelo para crear un recordatorio."""

    tiempo: int = Field(..., gt=0, description="Cantidad de tiempo antes de la cita")
    unidad: UnidadTiempo = Field(..., description="Unidad de tiempo")
    metodo_envio: MetodoEnvio = Field(
        default=MetodoEnvio.WHATSAPP, description="Método de envío del recordatorio"
    )


class RecordatorioResponse(BaseModel):
    """Modelo de respuesta para un recordatorio."""

    id: int
    id_cita: int
    tiempo: int
    unidad: str
    enviado: bool
    fecha_envio: Optional[datetime] = None
    metodo_envio: str
    error_envio: Optional[str] = None
    fecha_creacion: datetime

    model_config = {"from_attributes": True}


class RecordatorioListResponse(BaseModel):
    """Lista de recordatorios."""

    total: int
    recordatorios: List[RecordatorioResponse]


# ============================================================================
# RECURRENCIA / SERIES
# ============================================================================


class ReglaRecurrencia(BaseModel):
    """Regla de recurrencia para citas."""

    frequency: FrecuenciaRecurrencia = Field(..., description="Frecuencia de recurrencia")
    interval: int = Field(default=1, gt=0, description="Intervalo entre ocurrencias")
    count: Optional[int] = Field(None, gt=0, description="Número total de ocurrencias")
    until: Optional[datetime] = Field(None, description="Fecha hasta la cual se repite")
    byweekday: Optional[List[int]] = Field(
        None, description="Días de la semana (0=Lun, 6=Dom)"
    )

    @field_validator("byweekday")
    @classmethod
    def validate_weekdays(cls, v):
        if v is not None:
            if not all(0 <= day <= 6 for day in v):
                raise ValueError("byweekday debe contener valores entre 0 y 6")
        return v


class SerieCreate(BaseModel):
    """Modelo para crear una serie de citas recurrentes."""

    regla_recurrencia: ReglaRecurrencia = Field(..., description="Regla de recurrencia")
    fecha_inicio: datetime = Field(..., description="Fecha de inicio de la serie")
    fecha_fin: Optional[datetime] = Field(None, description="Fecha de fin de la serie")
    id_paciente: int = Field(..., gt=0, description="ID del paciente")
    id_podologo: int = Field(..., gt=0, description="ID del podólogo")
    tipo_cita: TipoCita = Field(default=TipoCita.CONSULTA, description="Tipo de cita")
    duracion_minutos: int = Field(default=30, gt=0, description="Duración de cada cita")
    hora_inicio: str = Field(..., description="Hora de inicio en formato HH:MM")
    notas_serie: Optional[str] = Field(None, max_length=500, description="Notas para toda la serie")


class SerieUpdate(BaseModel):
    """Modelo para actualizar una serie."""

    fecha_fin: Optional[datetime] = None
    activa: Optional[bool] = None
    notas_serie: Optional[str] = Field(None, max_length=500)


class SerieResponse(BaseModel):
    """Modelo de respuesta para una serie."""

    id: int
    regla_recurrencia: dict
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    id_paciente: int
    id_podologo: int
    tipo_cita: str
    duracion_minutos: int
    hora_inicio: str
    notas_serie: Optional[str] = None
    activa: bool
    fecha_creacion: datetime
    paciente: Optional[PacienteInfo] = None
    podologo: Optional[PodologoInfo] = None
    citas_generadas: int = 0

    model_config = {"from_attributes": True}


class SerieListResponse(BaseModel):
    """Lista de series."""

    total: int
    series: List[SerieResponse]
