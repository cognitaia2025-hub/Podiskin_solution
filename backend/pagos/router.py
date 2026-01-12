"""
Router de Pagos - Endpoints REST para gestión de cobros
=======================================================
"""

from fastapi import APIRouter, HTTPException, Query, Depends, status, Request
from typing import Optional
from datetime import datetime
import logging

from pagos.models import (
    PagoCreate,
    PagoUpdate,
    PagoResponse,
    PagoListResponse,
    PagoStats,
    ESTADOS_PAGO,
    METODOS_PAGO,
)
from pagos.service import pagos_service
from auth.middleware import get_current_user
from auth.permissions import check_permission

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pagos", tags=["Pagos y Cobros"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_client_ip(request: Request) -> str:
    """Obtiene IP del cliente desde el request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host if request.client else "unknown"


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get("", response_model=PagoListResponse)
async def listar_pagos(
    request: Request,
    id_cita: Optional[int] = Query(None, description="Filtrar por ID de cita"),
    id_paciente: Optional[int] = Query(None, description="Filtrar por ID de paciente"),
    estado_pago: Optional[str] = Query(None, description="Filtrar por estado"),
    metodo_pago: Optional[str] = Query(None, description="Filtrar por método de pago"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta"),
    factura_solicitada: Optional[bool] = Query(
        None, description="Filtrar por factura solicitada"
    ),
    factura_emitida: Optional[bool] = Query(
        None, description="Filtrar por factura emitida"
    ),
    limit: int = Query(100, ge=1, le=500, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    current_user: dict = Depends(get_current_user),
):
    """
    Lista pagos con filtros opcionales.

    Requiere permiso: cobros:read
    """
    # Verificar permiso
    if not check_permission(current_user.id, "cobros:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver los pagos",
        )

    try:
        result = pagos_service.get_all(
            id_cita=id_cita,
            id_paciente=id_paciente,
            estado_pago=estado_pago,
            metodo_pago=metodo_pago,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            factura_solicitada=factura_solicitada,
            factura_emitida=factura_emitida,
            limit=limit,
            offset=offset,
        )

        return result

    except Exception as e:
        logger.error(f"Error listando pagos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener lista de pagos",
        )


@router.post("", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
async def crear_pago(
    request: Request, pago: PagoCreate, current_user: dict = Depends(get_current_user)
):
    """
    Crea un nuevo pago.

    Requiere permiso: cobros:write
    """
    # Verificar permiso
    if not check_permission(current_user.id, "cobros:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear pagos",
        )

    try:
        # Si no se especifica recibo_por, usar el usuario actual
        if not pago.recibo_por:
            pago.recibo_por = current_user.id

        ip_address = get_client_ip(request)

        pago_creado = pagos_service.create(
            pago_data=pago, usuario_id=current_user.id, ip_address=ip_address
        )

        return pago_creado

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creando pago: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el pago",
        )


@router.get("/{pago_id}", response_model=PagoResponse)
async def obtener_pago(pago_id: int, current_user: dict = Depends(get_current_user)):
    """
    Obtiene un pago por ID.

    Requiere permiso: cobros:read
    """
    # Verificar permiso
    if not check_permission(current_user.id, "cobros:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver pagos",
        )

    try:
        pago = pagos_service.get_by_id(pago_id)

        if not pago:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pago {pago_id} no encontrado",
            )

        return pago

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo pago {pago_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el pago",
        )


@router.put("/{pago_id}", response_model=PagoResponse)
async def actualizar_pago(
    request: Request,
    pago_id: int,
    pago_update: PagoUpdate,
    current_user: dict = Depends(get_current_user),
):
    """
    Actualiza un pago existente.

    Requiere permiso: cobros:write
    """
    # Verificar permiso
    if not check_permission(current_user.id, "cobros:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar pagos",
        )

    try:
        ip_address = get_client_ip(request)

        pago_actualizado = pagos_service.update(
            pago_id=pago_id,
            pago_data=pago_update,
            usuario_id=current_user.id,
            ip_address=ip_address,
        )

        return pago_actualizado

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error actualizando pago {pago_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el pago",
        )


@router.get("/cita/{id_cita}", response_model=list[PagoResponse])
async def obtener_pagos_cita(
    id_cita: int, current_user: dict = Depends(get_current_user)
):
    """
    Obtiene todos los pagos de una cita específica.

    Requiere permiso: cobros:read
    """
    # Verificar permiso
    if not check_permission(current_user.id, "cobros:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver pagos",
        )

    try:
        pagos = pagos_service.get_by_cita(id_cita)
        return pagos

    except Exception as e:
        logger.error(f"Error obteniendo pagos de cita {id_cita}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener pagos de la cita",
        )


@router.get("/pendientes/lista", response_model=list[PagoResponse])
async def listar_pagos_pendientes(current_user: dict = Depends(get_current_user)):
    """
    Obtiene lista de pagos pendientes o parciales.

    Requiere permiso: cobros:read
    """
    # Verificar permiso
    if not check_permission(current_user.id, "cobros:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver pagos",
        )

    try:
        pagos = pagos_service.get_pendientes()
        return pagos

    except Exception as e:
        logger.error(f"Error obteniendo pagos pendientes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener pagos pendientes",
        )


@router.get("/stats/resumen", response_model=PagoStats)
async def obtener_estadisticas(
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta"),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtiene estadísticas de pagos.

    Requiere permiso: cobros:read
    """
    # Verificar permiso
    if not check_permission(current_user.id, "cobros:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver estadísticas de pagos",
        )

    try:
        stats = pagos_service.get_stats(
            fecha_desde=fecha_desde, fecha_hasta=fecha_hasta
        )

        return stats

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de pagos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estadísticas",
        )


@router.get("/estados/lista", response_model=list[str])
async def obtener_estados():
    """Obtiene lista de estados de pago disponibles."""
    return ESTADOS_PAGO


@router.get("/metodos/lista", response_model=list[str])
async def obtener_metodos_pago():
    """Obtiene lista de métodos de pago disponibles."""
    return METODOS_PAGO
