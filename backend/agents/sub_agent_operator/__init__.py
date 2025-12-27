"""
Sub-Agente de Operaciones - Podoskin Solution
==============================================

Agente especializado en gestión operativa:
- Consultas de citas y pacientes
- Agendamiento y reagendamiento
- Cancelaciones
- Actualización de datos
- Reportes operativos
"""

from .graph import run_agent, operations_agent

__version__ = "1.0.0"
__all__ = ["run_agent", "operations_agent"]
