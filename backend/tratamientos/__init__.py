"""
Módulo de Tratamientos - Podoskin Solution
==========================================

Módulo para gestión de tratamientos, signos vitales y diagnósticos.
"""

from .router import router
from .models import (
    TratamientoCreate,
    TratamientoUpdate,
    TratamientoResponse,
    SignosVitalesCreate,
    SignosVitalesResponse,
    DiagnosticoCreate,
    DiagnosticoResponse,
    CIE10Response,
)

__all__ = [
    "router",
    "TratamientoCreate",
    "TratamientoUpdate",
    "TratamientoResponse",
    "SignosVitalesCreate",
    "SignosVitalesResponse",
    "DiagnosticoCreate",
    "DiagnosticoResponse",
    "CIE10Response",
]
