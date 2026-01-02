"""
Módulo Roles
=============
Gestión de roles y permisos del sistema.
"""

from .router import router
from .service import RolesService

__all__ = ["router", "RolesService"]
