"""
Modelos Pydantic - Módulo de Tratamientos
==========================================

Modelos de datos para tratamientos, signos vitales y diagnósticos.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# ENUMS
# ============================================================================


class TipoDiagnostico(str, Enum):
    """Tipos de diagnóstico."""
    PRESUNTIVO = "Presuntivo"
    DEFINITIVO = "Definitivo"
    DIFERENCIAL = "Diferencial"


class ClasificacionIMC(str, Enum):
    """Clasificación del IMC."""
    BAJO_PESO = "Bajo peso"
    NORMAL = "Normal"
    SOBREPESO = "Sobrepeso"
    OBESIDAD = "Obesidad"


# ============================================================================
# TRATAMIENTOS
# ============================================================================


class TratamientoBase(BaseModel):
    """Modelo base para tratamiento."""
    codigo_servicio: str = Field(..., min_length=1, max_length=20)
    nombre_servicio: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio_base: Decimal = Field(..., ge=0, decimal_places=2)
    duracion_minutos: int = Field(default=30, ge=1)
    requiere_consentimiento: bool = False
    activo: bool = True


class TratamientoCreate(TratamientoBase):
    """Modelo para crear tratamiento."""
    pass


class TratamientoUpdate(BaseModel):
    """Modelo para actualizar tratamiento."""
    codigo_servicio: Optional[str] = Field(None, min_length=1, max_length=20)
    nombre_servicio: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio_base: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    duracion_minutos: Optional[int] = Field(None, ge=1)
    requiere_consentimiento: Optional[bool] = None
    activo: Optional[bool] = None


class TratamientoResponse(TratamientoBase):
    """Modelo de respuesta para tratamiento."""
    id: int
    fecha_registro: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SIGNOS VITALES
# ============================================================================


class SignosVitalesCreate(BaseModel):
    """Modelo para crear signos vitales."""
    peso_kg: Optional[Decimal] = Field(None, ge=0.1, le=500, decimal_places=2)
    talla_cm: Optional[Decimal] = Field(None, ge=30, le=250, decimal_places=2)
    presion_sistolica: Optional[int] = Field(None, ge=60, le=250)
    presion_diastolica: Optional[int] = Field(None, ge=40, le=150)
    frecuencia_cardiaca: Optional[int] = Field(None, ge=30, le=200)
    frecuencia_respiratoria: Optional[int] = Field(None, ge=8, le=60)
    temperatura_celsius: Optional[Decimal] = Field(None, ge=34, le=42, decimal_places=2)
    saturacion_oxigeno: Optional[int] = Field(None, ge=70, le=100)
    glucosa_capilar: Optional[int] = Field(None, ge=30, le=600)


class SignosVitalesResponse(BaseModel):
    """Modelo de respuesta para signos vitales."""
    id: int
    id_cita: int
    peso_kg: Optional[Decimal] = None
    talla_cm: Optional[Decimal] = None
    imc: Optional[Decimal] = None
    imc_clasificacion: Optional[str] = None
    presion_arterial: Optional[str] = None
    frecuencia_cardiaca: Optional[int] = None
    frecuencia_respiratoria: Optional[int] = None
    temperatura_celsius: Optional[Decimal] = None
    saturacion_oxigeno: Optional[int] = None
    glucosa_capilar: Optional[int] = None
    fecha_medicion: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DIAGNÓSTICOS
# ============================================================================


class DiagnosticoCreate(BaseModel):
    """Modelo para crear diagnóstico."""
    tipo: TipoDiagnostico
    descripcion: str = Field(..., min_length=1, max_length=500)
    codigo_cie10: Optional[str] = Field(None, pattern=r'^[A-Z]\d{2}(\.\d{1,2})?$')
    notas: Optional[str] = None

    @field_validator('codigo_cie10')
    @classmethod
    def validate_codigo_cie10(cls, v):
        """Valida el formato del código CIE-10."""
        if v and not v[0].isalpha():
            raise ValueError('El código CIE-10 debe comenzar con una letra')
        return v


class PodologoInfo(BaseModel):
    """Información del podólogo."""
    id: int
    nombre: str


class DiagnosticoResponse(BaseModel):
    """Modelo de respuesta para diagnóstico."""
    id: int
    id_cita: int
    tipo: str
    descripcion: str
    codigo_cie10: Optional[str] = None
    codigo_cie10_descripcion: Optional[str] = None
    diagnosticado_por: Optional[PodologoInfo] = None
    fecha_diagnostico: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CIE-10
# ============================================================================


class CIE10Response(BaseModel):
    """Modelo de respuesta para código CIE-10."""
    id: int
    codigo: str
    descripcion: str
    categoria: Optional[str] = None
    subcategoria: Optional[str] = None

    class Config:
        from_attributes = True
