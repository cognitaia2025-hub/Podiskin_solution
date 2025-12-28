"""
Módulo de gestión de citas (appointments) - Podoskin Solution
==============================================================

Este módulo implementa el CRUD completo de citas con:
- Validación de disponibilidad
- Gestión de conflictos
- Cálculo automático de duración
"""

from .router import router

__all__ = ["router"]
