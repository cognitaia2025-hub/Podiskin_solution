"""
Modelos para Estadísticas
=========================
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class TreatmentStats(BaseModel):
    """Estadísticas de tratamientos más usados"""
    tratamiento: str
    cantidad: int
    porcentaje: float

class OccupancyStats(BaseModel):
    """Estadísticas de ocupación de agenda"""
    fecha: date
    horas_disponibles: int
    horas_ocupadas: int
    porcentaje_ocupacion: float
    citas_programadas: int

class DashboardStats(BaseModel):
    """Estadísticas completas del dashboard"""
    # Básicas
    total_pacientes: int
    total_citas_mes: int
    ingresos_mes: float
    
    # Avanzadas
    top_treatments: List[TreatmentStats] = []
    ocupacion_semanal: List[OccupancyStats] = []
    ocupacion_promedio: float = 0.0
    
    # Tendencias
    crecimiento_pacientes: float = 0.0
    crecimiento_ingresos: float = 0.0
