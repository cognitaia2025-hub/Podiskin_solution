"""
Router de Facturas - Endpoints REST para facturación
====================================================
NOTA: Funcionalidad de timbrado SAT pendiente de implementación.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, status, Request
from typing import Optional
from datetime import datetime
import logging

from facturas.models import (
    FacturaCreate,
    FacturaCancel,
    FacturaResponse,
    FacturaListResponse
)
from facturas.service import facturas_service
from auth.middleware import get_current_user
from auth.permissions import check_permission

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/facturas", tags=["Facturas"])


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

@router.get("", response_model=FacturaListResponse)
async def listar_facturas(
    id_pago: Optional[int] = Query(None, description="Filtrar por ID de pago"),
    rfc_receptor: Optional[str] = Query(None, description="Filtrar por RFC del receptor"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta"),
    limit: int = Query(100, ge=1, le=500, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista facturas con filtros opcionales.
    
    Requiere permiso: cobros:read
    """
    # Verificar permiso
    if not check_permission(current_user.id, "cobros:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver facturas"
        )
    
    try:
        result = facturas_service.get_all(
            id_pago=id_pago,
            rfc_receptor=rfc_receptor,
            estado=estado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            limit=limit,
            offset=offset
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error listando facturas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener lista de facturas"
        )


@router.post("", response_model=FacturaResponse, status_code=status.HTTP_201_CREATED)
async def crear_factura(
    request: Request,
    factura: FacturaCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Solicita generación de factura para un pago.
    
    ⚠️ NOTA: Por ahora solo registra la solicitud.
    La integración con el SAT para timbrado se implementará próximamente.
    
    Requiere permiso: cobros:write
    """
    # Verificar permiso
    if not check_permission(current_user.id, "cobros:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para generar facturas"
        )
    
    try:
        ip_address = get_client_ip(request)
        
        factura_creada = facturas_service.create_placeholder(
            factura_data=factura,
            usuario_id=current_user.id,
            ip_address=ip_address
        )
        
        # Advertir que es pendiente de timbrado
        logger.warning(
            f"Factura {factura_creada['id']} creada pero pendiente de timbrado SAT"
        )
        
        return factura_creada
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creando factura: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la factura"
        )


@router.get("/{factura_id}", response_model=FacturaResponse)
async def obtener_factura(
    factura_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene una factura por ID.
    
    Requiere permiso: cobros:read
    """
    # Verificar permiso
    if not check_permission(current_user.id, "cobros:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver facturas"
        )
    
    try:
        factura = facturas_service.get_by_id(factura_id)
        
        if not factura:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Factura {factura_id} no encontrada"
            )
        
        return factura
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo factura {factura_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la factura"
        )


@router.put("/{factura_id}/cancelar", response_model=FacturaResponse)
async def cancelar_factura(
    request: Request,
    factura_id: int,
    cancelacion: FacturaCancel,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancela una factura.
    
    Requiere permiso: cobros:write
    """
    # Verificar permiso
    if not check_permission(current_user.id, "cobros:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para cancelar facturas"
        )
    
    try:
        ip_address = get_client_ip(request)
        
        factura_cancelada = facturas_service.cancel(
            factura_id=factura_id,
            motivo=cancelacion.motivo,
            usuario_id=current_user.id,
            ip_address=ip_address
        )
        
        return factura_cancelada
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error cancelando factura {factura_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cancelar la factura"
        )


@router.get("/sat/status")
async def obtener_estado_integracion_sat(
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene estado de la integración con el SAT.
    
    Por ahora retorna información sobre la implementación futura.
    """
    return {
        "estado": "no_implementado",
        "mensaje": "Integración con SAT pendiente de implementación",
        "funcionalidades_pendientes": [
            "Timbrado de facturas CFDI 4.0",
            "Generación de XML y PDF",
            "Envío por correo electrónico",
            "Cancelación ante el SAT",
            "Consulta de estatus de factura"
        ],
        "nota": "Actualmente solo se registran solicitudes de factura sin timbrado oficial"
    }
