"""
Inventory Router
================
REST API endpoints for inventory and product management.

Prefix: /api/inventory
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional

from auth.middleware import get_current_user
from inventory.models import (
    ProductResponse,
    ProductListItem,
    ProductListResponse,
    ProductCreateRequest,
    ProductUpdateRequest,
    StockAdjustmentRequest,
    StockAlertResponse,
    StockMovementResponse,
)
from inventory import service

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory Management"],
    responses={404: {"description": "Not found"}},
)


# ============================================================================
# HELPER FUNCTION
# ============================================================================


def require_admin_or_staff(current_user):
    """Verify current user is admin or staff, raise 403 if not."""
    if current_user.rol not in ["Admin", "Podologo", "Recepcionista"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo personal autorizado puede realizar esta operación",
        )


def require_admin(current_user):
    """Verify current user is admin, raise 403 if not."""
    if current_user.rol != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden realizar esta operación",
        )


# ============================================================================
# PRODUCT ENDPOINTS
# ============================================================================


@router.get(
    "",
    response_model=ProductListResponse,
    summary="Listar productos",
    description="Obtiene la lista de productos del inventario con paginación y filtros.",
)
async def list_products(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    categoria: Optional[str] = Query(None),
    activo: bool = Query(True),
    current_user=Depends(get_current_user),
):
    """Lista todos los productos del inventario."""
    require_admin_or_staff(current_user)

    productos, total = await service.get_all_products(
        limit=limit, offset=offset, categoria=categoria, activo=activo
    )

    return {"total": total, "productos": productos}


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Obtener producto",
    description="Obtiene un producto por su ID con todos sus detalles.",
)
async def get_product(product_id: int, current_user=Depends(get_current_user)):
    """Obtiene un producto por ID."""
    require_admin_or_staff(current_user)

    product = await service.get_product_by_id(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
        )

    return product


@router.post(
    "",
    response_model=ProductListItem,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
    description="Crea un nuevo producto en el inventario. Solo administradores.",
)
async def create_product(
    product_data: ProductCreateRequest, current_user=Depends(get_current_user)
):
    """Crea un nuevo producto."""
    require_admin(current_user)

    # Convertir el modelo a dict excluyendo None
    product_dict = product_data.model_dump(exclude_none=True)

    new_product = await service.create_product(
        codigo_producto=product_dict.pop("codigo_producto"),
        nombre=product_dict.pop("nombre"),
        categoria=product_dict.pop("categoria"),
        unidad_medida=product_dict.pop("unidad_medida"),
        registrado_por=current_user.id,
        **product_dict
    )

    if not new_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear producto. El código de producto puede estar duplicado.",
        )

    return new_product


@router.put(
    "/{product_id}",
    response_model=ProductListItem,
    summary="Actualizar producto",
    description="Actualiza un producto existente. Solo administradores.",
)
async def update_product(
    product_id: int,
    product_data: ProductUpdateRequest,
    current_user=Depends(get_current_user),
):
    """Actualiza un producto existente."""
    require_admin(current_user)

    # Convertir el modelo a dict excluyendo None
    update_dict = product_data.model_dump(exclude_none=True)

    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se proporcionaron datos para actualizar",
        )

    updated_product = await service.update_product(product_id, **update_dict)

    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
        )

    return updated_product


# ============================================================================
# STOCK ENDPOINTS
# ============================================================================


@router.post(
    "/{product_id}/adjust",
    response_model=StockMovementResponse,
    summary="Ajustar stock",
    description="Registra un ajuste de stock (entrada, salida, ajuste). Personal autorizado.",
)
async def adjust_stock(
    product_id: int,
    adjustment: StockAdjustmentRequest,
    current_user=Depends(get_current_user),
):
    """Ajusta el stock de un producto."""
    require_admin_or_staff(current_user)

    # Verificar que el producto existe
    product = await service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
        )

    # Registrar movimiento
    movement = await service.adjust_stock(
        product_id=product_id,
        tipo_movimiento=adjustment.tipo_movimiento,
        cantidad=adjustment.cantidad,
        motivo=adjustment.motivo,
        registrado_por=current_user.id,
        costo_unitario=adjustment.costo_unitario,
        numero_factura_proveedor=adjustment.numero_factura_proveedor,
        lote=adjustment.lote,
        fecha_caducidad=adjustment.fecha_caducidad,
    )

    if not movement:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al registrar ajuste de stock",
        )

    return movement


@router.get(
    "/alerts/low-stock",
    response_model=List[StockAlertResponse],
    summary="Alertas de stock bajo",
    description="Obtiene productos con stock por debajo del mínimo.",
)
async def get_low_stock_alerts(current_user=Depends(get_current_user)):
    """Obtiene alertas de productos con stock bajo."""
    require_admin_or_staff(current_user)

    alerts = await service.get_low_stock_alerts()
    return alerts
