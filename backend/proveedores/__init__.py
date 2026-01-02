"""
Módulo Proveedores
==================
Gestión de proveedores del inventario.
"""

from .router import router
from .service import ProveedoresService

__all__ = ["router", "ProveedoresService"]
