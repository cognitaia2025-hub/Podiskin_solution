"""
Router de Auditoría - Endpoints para consulta de logs
=====================================================
"""

from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from audit.service import AuditService
from auth.middleware import get_current_user
from auth.permissions import check_permission
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit", tags=["Auditoría"])

audit_service = AuditService()


# ============================================================================
# MODELS
# ============================================================================

class AuditLogResponse(BaseModel):
    id: int
    usuario_id: int
    usuario_nombre: Optional[str]
    accion: str
    modulo: str
    descripcion: str
    datos_anteriores: Optional[dict]
    datos_nuevos: Optional[dict]
    ip_address: Optional[str]
    fecha_hora: datetime


class AuditLogsListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total: int
    limit: int
    offset: int


class UserActivityResponse(BaseModel):
    modulo: str
    accion: str
    cantidad: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/logs", response_model=AuditLogsListResponse)
async def get_audit_logs(
    usuario_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    modulo: Optional[str] = Query(None, description="Filtrar por módulo"),
    accion: Optional[str] = Query(None, description="Filtrar por tipo de acción"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde (ISO format)"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta (ISO format)"),
    limit: int = Query(100, ge=1, le=500, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene logs de auditoría con filtros opcionales.
    
    Requiere permiso: administracion:read
    """
    # Verificar permiso de administración
    if not check_permission(current_user['id'], "administracion:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a los logs de auditoría"
        )
    
    try:
        result = audit_service.get_logs(
            usuario_id=usuario_id,
            modulo=modulo,
            accion=accion,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            limit=limit,
            offset=offset
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error obteniendo logs de auditoría: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener logs de auditoría"
        )


@router.get("/user-activity/{usuario_id}", response_model=List[UserActivityResponse])
async def get_user_activity(
    usuario_id: int,
    days: int = Query(30, ge=1, le=365, description="Días hacia atrás"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene resumen de actividad de un usuario.
    
    Requiere permiso: administracion:read
    """
    # Verificar permiso de administración
    if not check_permission(current_user['id'], "administracion:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a la actividad de usuarios"
        )
    
    try:
        activity = audit_service.get_user_activity(usuario_id, days)
        return activity
        
    except Exception as e:
        logger.error(f"Error obteniendo actividad de usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener actividad de usuario"
        )


@router.get("/modules", response_model=List[str])
async def get_audit_modules(current_user: dict = Depends(get_current_user)):
    """
    Obtiene lista de módulos disponibles para filtrar auditoría.
    """
    # Verificar permiso de administración
    if not check_permission(current_user['id'], "administracion:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a esta información"
        )
    
    return [
        "pagos",
        "facturas",
        "gastos",
        "cortes_caja",
        "pacientes",
        "citas",
        "usuarios",
        "inventario",
        "expedientes"
    ]


@router.get("/actions", response_model=List[str])
async def get_audit_actions(current_user: dict = Depends(get_current_user)):
    """
    Obtiene lista de acciones disponibles para filtrar auditoría.
    """
    # Verificar permiso de administración
    if not check_permission(current_user['id'], "administracion:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a esta información"
        )
    
    return [
        "crear",
        "actualizar",
        "eliminar",
        "cancelar",
        "aprobar",
        "rechazar"
    ]
