"""
Inventory Models
================
Pydantic models for inventory API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# ============================================================================
# RESPONSE MODELS
# ============================================================================


class ProductResponse(BaseModel):
    """Response model for a single product"""

    id: int
    codigo_producto: str
    codigo_barras: Optional[str] = None
    nombre: str
    descripcion: Optional[str] = None
    categoria: str
    subcategoria: Optional[str] = None
    stock_actual: int
    stock_minimo: int
    stock_maximo: int
    unidad_medida: str
    costo_unitario: Optional[Decimal] = None
    precio_venta: Optional[Decimal] = None
    margen_ganancia: Optional[Decimal] = None
    id_proveedor: Optional[int] = None
    tiempo_reposicion_dias: int
    requiere_receta: bool
    controlado: bool
    tiene_caducidad: bool
    fecha_caducidad: Optional[date] = None
    lote: Optional[str] = None
    ubicacion_almacen: Optional[str] = None
    activo: bool
    fecha_registro: Optional[datetime] = None
    registrado_por: Optional[int] = None


class ProductListItem(BaseModel):
    """Simplified product model for list views"""

    id: int
    codigo_producto: str
    nombre: str
    categoria: str
    stock_actual: int
    stock_minimo: int
    stock_maximo: int
    unidad_medida: str
    costo_unitario: Optional[Decimal] = None
    precio_venta: Optional[Decimal] = None
    activo: bool


class ProductListResponse(BaseModel):
    """Paginated response for product list"""

    total: int
    productos: List[ProductListItem]


class StockAlertResponse(BaseModel):
    """Response model for low stock alerts"""

    id: int
    codigo_producto: str
    nombre: str
    categoria: str
    stock_actual: int
    stock_minimo: int
    cantidad_requerida: int
    proveedor: Optional[str] = None
    telefono_proveedor: Optional[str] = None
    tiempo_reposicion_dias: int
    costo_unitario: Optional[Decimal] = None
    costo_reposicion: Optional[Decimal] = None


class StockMovementResponse(BaseModel):
    """Response model for stock movement"""

    id: int
    id_producto: int
    tipo_movimiento: str
    cantidad: int
    stock_anterior: int
    stock_nuevo: int
    motivo: str
    registrado_por: int
    fecha_movimiento: datetime


# ============================================================================
# REQUEST MODELS
# ============================================================================


class ProductCreateRequest(BaseModel):
    """Request model for creating a new product"""

    codigo_producto: str = Field(..., min_length=1, max_length=50)
    codigo_barras: Optional[str] = Field(None, max_length=50)
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    categoria: str = Field(
        ...,
        pattern="^(Material_Curacion|Instrumental|Medicamento|Consumible|Equipo_Medico|Producto_Venta|Material_Limpieza|Papeleria)$",
    )
    subcategoria: Optional[str] = Field(None, max_length=100)
    stock_actual: int = Field(default=0, ge=0)
    stock_minimo: int = Field(default=5, ge=0)
    stock_maximo: int = Field(default=100, ge=0)
    unidad_medida: str = Field(..., min_length=1, max_length=50)
    costo_unitario: Optional[Decimal] = Field(None, ge=0)
    precio_venta: Optional[Decimal] = Field(None, ge=0)
    margen_ganancia: Optional[Decimal] = Field(None, ge=0, le=100)
    id_proveedor: Optional[int] = Field(None, ge=1)
    tiempo_reposicion_dias: int = Field(default=7, ge=0)
    requiere_receta: bool = False
    controlado: bool = False
    tiene_caducidad: bool = False
    fecha_caducidad: Optional[date] = None
    lote: Optional[str] = Field(None, max_length=50)
    ubicacion_almacen: Optional[str] = Field(None, max_length=100)


class ProductUpdateRequest(BaseModel):
    """Request model for updating a product"""

    codigo_barras: Optional[str] = Field(None, max_length=50)
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = None
    categoria: Optional[str] = Field(
        None,
        pattern="^(Material_Curacion|Instrumental|Medicamento|Consumible|Equipo_Medico|Producto_Venta|Material_Limpieza|Papeleria)$",
    )
    subcategoria: Optional[str] = Field(None, max_length=100)
    stock_minimo: Optional[int] = Field(None, ge=0)
    stock_maximo: Optional[int] = Field(None, ge=0)
    unidad_medida: Optional[str] = Field(None, min_length=1, max_length=50)
    costo_unitario: Optional[Decimal] = Field(None, ge=0)
    precio_venta: Optional[Decimal] = Field(None, ge=0)
    margen_ganancia: Optional[Decimal] = Field(None, ge=0, le=100)
    id_proveedor: Optional[int] = Field(None, ge=1)
    tiempo_reposicion_dias: Optional[int] = Field(None, ge=0)
    requiere_receta: Optional[bool] = None
    controlado: Optional[bool] = None
    tiene_caducidad: Optional[bool] = None
    fecha_caducidad: Optional[date] = None
    lote: Optional[str] = Field(None, max_length=50)
    ubicacion_almacen: Optional[str] = Field(None, max_length=100)
    activo: Optional[bool] = None


class StockAdjustmentRequest(BaseModel):
    """Request model for stock adjustment"""

    tipo_movimiento: str = Field(
        ...,
        pattern="^(Entrada|Salida|Ajuste_Positivo|Ajuste_Negativo|Merma|Devolucion)$",
    )
    cantidad: int = Field(..., gt=0)
    motivo: str = Field(..., min_length=3, max_length=500)
    costo_unitario: Optional[Decimal] = Field(None, ge=0)
    numero_factura_proveedor: Optional[str] = Field(None, max_length=100)
    lote: Optional[str] = Field(None, max_length=50)
    fecha_caducidad: Optional[date] = None
