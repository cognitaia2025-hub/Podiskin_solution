"""
Pydantic models for the pacientes module.
Defines request/response schemas for patients, allergies, and medical history.
"""

from datetime import date, datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
import re


# ============================================================================
# PACIENTES MODELS
# ============================================================================

class PacienteBase(BaseModel):
    """Base model for patient data."""
    primer_nombre: str = Field(..., min_length=1, max_length=50)
    segundo_nombre: Optional[str] = Field(None, max_length=50)
    primer_apellido: str = Field(..., min_length=1, max_length=50)
    segundo_apellido: Optional[str] = Field(None, max_length=50)
    fecha_nacimiento: date
    sexo: Literal["M", "F", "O"]
    curp: Optional[str] = Field(None, max_length=18)
    telefono_principal: str = Field(..., min_length=10, max_length=15)
    telefono_secundario: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = None
    calle: Optional[str] = None
    numero_exterior: Optional[str] = None
    numero_interior: Optional[str] = None
    colonia: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    codigo_postal: Optional[str] = Field(None, alias="cp", max_length=10)
    ocupacion: Optional[str] = None
    estado_civil: Optional[str] = None
    referencia: Optional[str] = Field(None, alias="referencia_como_nos_conocio", max_length=255)
    
    @field_validator("curp")
    @classmethod
    def validate_curp(cls, v: Optional[str]) -> Optional[str]:
        """Validate CURP format if provided."""
        if v is not None and v:
            pattern = r"^[A-Z]{4}\d{6}[HM][A-Z]{5}\d{2}$"
            if not re.match(pattern, v):
                raise ValueError("CURP format invalid. Expected: 4 letters, 6 digits, H/M, 5 letters, 2 digits")
        return v
    
    @field_validator("fecha_nacimiento")
    @classmethod
    def validate_fecha_nacimiento(cls, v: date) -> date:
        """Ensure birth date is not in the future."""
        if v > date.today():
            raise ValueError("Birth date cannot be in the future")
        return v
    
    @field_validator("telefono_principal", "telefono_secundario")
    @classmethod
    def validate_telefono(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number contains only digits."""
        if v is not None and v:
            if not v.replace("+", "").replace(" ", "").replace("-", "").isdigit():
                raise ValueError("Phone number should contain only digits")
        return v


class PacienteCreate(PacienteBase):
    """Model for creating a new patient."""
    pass


class PacienteUpdate(BaseModel):
    """Model for updating an existing patient."""
    primer_nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    segundo_nombre: Optional[str] = Field(None, max_length=50)
    primer_apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    segundo_apellido: Optional[str] = Field(None, max_length=50)
    fecha_nacimiento: Optional[date] = None
    sexo: Optional[Literal["M", "F", "O"]] = None
    curp: Optional[str] = Field(None, max_length=18)
    telefono_principal: Optional[str] = Field(None, min_length=10, max_length=15)
    telefono_secundario: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = None
    calle: Optional[str] = None
    numero_exterior: Optional[str] = None
    numero_interior: Optional[str] = None
    colonia: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    codigo_postal: Optional[str] = Field(None, alias="cp", max_length=10)
    ocupacion: Optional[str] = None
    estado_civil: Optional[str] = None
    referencia: Optional[str] = Field(None, alias="referencia_como_nos_conocio", max_length=255)
    activo: Optional[bool] = None


class PacienteResponse(PacienteBase):
    """Model for patient response."""
    id: int
    nombre_completo: str
    edad: int
    activo: bool
    fecha_registro: datetime
    fecha_modificacion: Optional[datetime] = None
    ultima_cita: Optional[datetime] = None
    total_citas: int = 0
    
    class Config:
        from_attributes = True


class PacienteListItem(BaseModel):
    """Model for patient list item (simplified)."""
    id: int
    nombre_completo: str
    telefono_principal: str
    email: Optional[str] = None
    fecha_nacimiento: date
    edad: int
    ultima_cita: Optional[datetime] = None
    total_citas: int = 0
    activo: bool


class PacienteListResponse(BaseModel):
    """Model for paginated patient list response."""
    items: List[PacienteListItem]
    total: int
    page: int
    limit: int
    pages: int


# ============================================================================
# ALERGIAS MODELS
# ============================================================================

class AlergiaBase(BaseModel):
    """Base model for allergy data."""
    tipo: Literal["Medicamento", "Alimento", "Ambiental", "Material", "Otro"] = Field(alias="tipo_alergeno")
    nombre: str = Field(..., min_length=1, max_length=100, alias="nombre_alergeno")
    reaccion: Optional[str] = None
    severidad: Literal["Leve", "Moderada", "Grave", "Mortal"] = "Leve"
    fecha_diagnostico: Optional[date] = None
    notas: Optional[str] = None


class AlergiaCreate(AlergiaBase):
    """Model for creating a new allergy."""
    pass


class AlergiaResponse(AlergiaBase):
    """Model for allergy response."""
    id: int
    id_paciente: int
    activo: bool
    fecha_registro: datetime
    
    class Config:
        from_attributes = True


class AlergiaListResponse(BaseModel):
    """Model for allergy list response."""
    items: List[AlergiaResponse]
    total: int


# ============================================================================
# ANTECEDENTES MEDICOS MODELS
# ============================================================================

class AntecedenteBase(BaseModel):
    """Base model for medical history data."""
    tipo_categoria: Literal["Heredofamiliar", "Patologico", "Quirurgico", "Traumatico", "Transfusional"]
    nombre_enfermedad: str = Field(..., min_length=1, max_length=200)
    parentesco: Optional[str] = Field(None, max_length=50)
    fecha_inicio: Optional[date] = None
    descripcion_temporal: Optional[str] = None
    tratamiento_actual: Optional[str] = None
    controlado: Optional[bool] = None
    notas: Optional[str] = None


class AntecedenteCreate(AntecedenteBase):
    """Model for creating a new medical history entry."""
    pass


class AntecedenteResponse(AntecedenteBase):
    """Model for medical history response."""
    id: int
    id_paciente: int
    activo: bool
    fecha_registro: datetime
    
    class Config:
        from_attributes = True


class AntecedenteListResponse(BaseModel):
    """Model for medical history list response."""
    items: List[AntecedenteResponse]
    total: int
