"""Router de Gastos - Endpoints REST."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .service import gastos_service
from citas.database import (
    _get_connection as get_db_connection_citas,
)  # Para transacciones

router = APIRouter(prefix="/gastos", tags=["Gastos"])

# Categorías de gastos actualizadas según operación real
CATEGORIAS = [
    "SERVICIOS_BASICOS",  # Luz, agua, internet
    "SERVICIOS_PROFESIONALES",  # Contabilidad, asesoría
    "RENTA_LOCAL",  # Renta del consultorio
    "MATERIAL_MEDICO",  # Gasas, guantes, jeringas
    "MEDICAMENTOS",  # Lidocaína, benzocaína
    "LIMPIEZA",  # Lysol, toallas, sanitas
    "CAFETERIA",  # Café, vasos, servilletas
    "MANTENIMIENTO",  # Reparaciones, WD-40
    "OTROS",  # Gastos no clasificados
]

# Legacy categories for backwards compatibility
CATEGORIAS_LEGACY = [
    "Renta",
    "Servicios",
    "Insumos",
    "Marketing",
    "Mantenimiento",
    "Capacitacion",
    "Papeleria",
    "Limpieza",
    "Varios",
]

METODOS_PAGO = [
    "Efectivo",
    "Transferencia",
    "Tarjeta_Debito",
    "Tarjeta_Credito",
    "Cheque",
]


class GastoCreate(BaseModel):
    categoria: str = Field(
        ..., description="Categoría del gasto (nuevo formato con enum)"
    )
    concepto: str = Field(..., min_length=3)
    monto: float = Field(..., gt=0)
    fecha_gasto: Optional[datetime] = None
    metodo_pago: str = Field(...)
    factura_disponible: bool = False
    folio_factura: Optional[str] = None
    registrado_por: Optional[int] = None
    notas: Optional[str] = None


class ProductoInventario(BaseModel):
    """Producto del inventario vinculado a un gasto"""

    id: int = Field(..., description="ID del producto en inventario")
    cantidad: float = Field(..., gt=0, description="Cantidad comprada")
    precio_unitario: float = Field(..., ge=0, description="Precio unitario de compra")


class GastoConInventarioRequest(BaseModel):
    """Request para crear gasto y actualizar inventario simultáneamente"""

    categoria: str = Field(..., description="Categoría del gasto")
    concepto: str = Field(..., min_length=3)
    monto: float = Field(..., gt=0)
    fecha_gasto: Optional[datetime] = None
    metodo_pago: str = Field(...)
    factura_disponible: bool = False
    folio_factura: Optional[str] = None
    registrado_por: Optional[int] = None
    notas: Optional[str] = None
    productos: List[ProductoInventario] = Field(
        ..., min_items=1, description="Lista de productos a actualizar en inventario"
    )


@router.get("/")
async def listar_gastos(
    categoria: Optional[str] = Query(
        None, description="Categoría del gasto (nuevo o legacy)"
    ),
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
):
    """Lista gastos con filtros opcionales. Acepta categorías nuevas y legacy."""
    return await gastos_service.get_all(categoria=categoria, desde=desde, hasta=hasta)


@router.get("/resumen")
async def resumen_gastos():
    """Obtiene resumen de gastos por categoría."""
    return await gastos_service.get_resumen()


@router.post("/", status_code=201)
async def crear_gasto(gasto: GastoCreate):
    """Registra un nuevo gasto."""
    # Validar categoría (acepta nuevas categorías o legacy)
    if gasto.categoria not in CATEGORIAS and gasto.categoria not in CATEGORIAS_LEGACY:
        raise HTTPException(
            400,
            f"Categoría inválida. Use categorías nuevas: {CATEGORIAS} o legacy: {CATEGORIAS_LEGACY}",
        )
    if gasto.metodo_pago not in METODOS_PAGO:
        raise HTTPException(400, f"Método de pago inválido. Use: {METODOS_PAGO}")
    return await gastos_service.create(gasto.dict())


@router.post("/con-inventario", status_code=201)
async def crear_gasto_con_inventario(request: GastoConInventarioRequest):
    """
    Registra un gasto y actualiza inventario automáticamente.

    Este endpoint permite:
    1. Registrar el gasto en la tabla gastos
    2. Vincular productos comprados en gastos_inventario
    3. Actualizar el stock de productos en inventario_productos

    Todo se ejecuta en una transacción atómica.
    """
    # Validaciones
    if (
        request.categoria not in CATEGORIAS
        and request.categoria not in CATEGORIAS_LEGACY
    ):
        raise HTTPException(
            400, f"Categoría inválida. Use: {CATEGORIAS} o {CATEGORIAS_LEGACY}"
        )
    if request.metodo_pago not in METODOS_PAGO:
        raise HTTPException(400, f"Método de pago inválido. Use: {METODOS_PAGO}")

    # Verificar que la suma de productos no exceda el monto total
    suma_productos = sum(p.cantidad * p.precio_unitario for p in request.productos)
    if suma_productos > request.monto:
        raise HTTPException(
            400,
            f"La suma de productos (${suma_productos:.2f}) excede el monto del gasto (${request.monto:.2f})",
        )

    conn = None
    try:
        # Obtener conexión con transacción
        conn = get_db_connection_citas()
        cur = conn.cursor()

        # 1. Insertar gasto
        insert_gasto_query = """
            INSERT INTO gastos (
                categoria, concepto, monto, fecha_gasto, metodo_pago,
                factura_disponible, folio_factura, registrado_por, notas
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """
        cur.execute(
            insert_gasto_query,
            (
                request.categoria,
                request.concepto,
                request.monto,
                request.fecha_gasto or datetime.now(),
                request.metodo_pago,
                request.factura_disponible,
                request.folio_factura,
                request.registrado_por,
                request.notas,
            ),
        )
        gasto_id = cur.fetchone()[0]

        # 2. Insertar vinculación en gastos_inventario y actualizar stock
        productos_actualizados = []
        for producto in request.productos:
            # Verificar que el producto existe
            cur.execute(
                "SELECT id, nombre, stock_actual FROM inventario_productos WHERE id = %s",
                (producto.id,),
            )
            prod_data = cur.fetchone()
            if not prod_data:
                conn.rollback()
                raise HTTPException(404, f"Producto con ID {producto.id} no encontrado")

            prod_id, prod_nombre, stock_actual = prod_data

            # Insertar vinculación
            cur.execute(
                """
                INSERT INTO gastos_inventario (
                    gasto_id, producto_id, cantidad_comprada, precio_unitario
                ) VALUES (%s, %s, %s, %s)
                """,
                (gasto_id, producto.id, producto.cantidad, producto.precio_unitario),
            )

            # Actualizar stock
            nuevo_stock = stock_actual + producto.cantidad
            cur.execute(
                """
                UPDATE inventario_productos 
                SET stock_actual = %s
                WHERE id = %s
                """,
                (nuevo_stock, producto.id),
            )

            productos_actualizados.append(
                {
                    "id": prod_id,
                    "nombre": prod_nombre,
                    "stock_anterior": stock_actual,
                    "stock_nuevo": nuevo_stock,
                    "cantidad_agregada": producto.cantidad,
                }
            )

        # Commit de transacción
        conn.commit()

        return {
            "success": True,
            "gasto_id": gasto_id,
            "monto_total": request.monto,
            "productos_actualizados": len(productos_actualizados),
            "detalles": productos_actualizados,
            "message": f"Gasto registrado y {len(productos_actualizados)} productos actualizados en inventario",
        }

    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(500, f"Error al procesar gasto con inventario: {str(e)}")
    finally:
        if conn:
            conn.close()
