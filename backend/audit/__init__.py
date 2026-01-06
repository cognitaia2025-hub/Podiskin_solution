"""Módulo de Auditoría - Registro de acciones del sistema."""

from .service import AuditService, log_action
from .router import router

__all__ = ["AuditService", "log_action", "router"]
