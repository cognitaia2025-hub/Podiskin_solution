"""Módulo de Pagos - Gestión de cobros y pagos de citas."""

from .router import router
from .service import PagosService

__all__ = ["router", "PagosService"]
