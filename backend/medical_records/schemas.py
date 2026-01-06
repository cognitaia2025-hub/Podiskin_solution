"""
Medical Records Schemas
Modelos Pydantic para expedientes médicos
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date


class PatientSearchResponse(BaseModel):
    id: int
    nombre_completo: str
    primer_nombre: str
    segundo_nombre: Optional[str]
    primer_apellido: str
    segundo_apellido: Optional[str]
    fecha_nacimiento: date
    telefono: str
    email: Optional[str]
    sexo: str
    ultima_visita: Optional[datetime]
    total_consultas: int = 0
    tiene_alergias: bool = False
    diagnostico_reciente: Optional[str]


class UpcomingAppointmentResponse(BaseModel):
    id: int
    paciente_id: int
    fecha_hora: datetime
    paciente_nombre: str
    telefono: str
    motivo_consulta: Optional[str]
    ultima_visita: Optional[datetime]
    alergias_importantes: List[str] = []


class AllergyResponse(BaseModel):
    id: int
    tipo: str
    sustancia: str
    reaccion: Optional[str]
    severidad: str
    activo: bool


class AntecedentResponse(BaseModel):
    id: int
    tipo: str
    enfermedad: str
    parentesco: Optional[str]
    fecha_inicio: Optional[date]
    tratamiento_actual: Optional[str]
    controlado: Optional[bool]
    notas: Optional[str]


class LifestyleResponse(BaseModel):
    tipo_dieta: Optional[str]
    descripcion_dieta: Optional[str]
    ejercicio_frecuencia: Optional[str]
    tipo_ejercicio: Optional[str]
    tabaquismo: bool = False
    tabaco_cigarros_dia: Optional[int]
    tabaco_anios: Optional[int]
    alcoholismo: bool = False
    alcohol_frecuencia: Optional[str]
    drogas: bool = False
    drogas_tipo: Optional[str]
    inmunizaciones_completas: Optional[bool]
    esquema_vacunacion: Optional[str]
    higiene_sueno_horas: Optional[float]
    exposicion_toxicos: Optional[str]
    suplementos_vitaminas: Optional[str]
    notas: Optional[str]


class GynecologyResponse(BaseModel):
    menarca_edad: Optional[int]
    ritmo_menstrual_dias: Optional[str]
    fecha_ultima_menstruacion: Optional[date]
    gestaciones: int = 0
    partos: int = 0
    cesareas: int = 0
    abortos: int = 0
    metodo_anticonceptivo: Optional[str]
    menopausia: bool = False
    fecha_menopausia: Optional[date]
    notas_adicionales: Optional[str]


class ConsultationResponse(BaseModel):
    id: int
    fecha_consulta: datetime
    motivo_consulta: str
    sintomas: Optional[str]
    exploracion_fisica: Optional[str]
    plan_tratamiento: Optional[str]
    indicaciones: Optional[str]
    finalizada: bool
    fecha_finalizacion: Optional[datetime]
    podologo_nombre: Optional[str]


class DiagnosisResponse(BaseModel):
    id: int
    codigo_cie10: Optional[str]
    nombre_diagnostico: str
    tipo_diagnostico: str
    descripcion: Optional[str]
    fecha_diagnostico: date
    activo: bool


class MedicalRecordResponse(BaseModel):
    paciente_id: int
    paciente_nombre: str
    fecha_nacimiento: date
    sexo: str
    telefono: str
    email: Optional[str]
    fecha_ultima_actualizacion: Optional[datetime]
    alergias: List[AllergyResponse] = []
    antecedentes: List[AntecedentResponse] = []
    estilo_vida: Optional[LifestyleResponse]
    ginecologia: Optional[GynecologyResponse]
    consultas: List[ConsultationResponse] = []
    diagnosticos: List[DiagnosisResponse] = []


class MedicalRecordUpdate(BaseModel):
    data: dict = Field(..., description="Datos a actualizar en la sección")


class ConsultationCreate(BaseModel):
    motivo_consulta: str
    sintomas: Optional[str]
    exploracion_fisica: Optional[str]
    plan_tratamiento: Optional[str]
