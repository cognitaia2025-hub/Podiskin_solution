"""
Inventory Service
=================
Business logic for inventory and product management operations.
"""

import logging
from typing import Optional, List, Tuple
from decimal import Decimal
from datetime import date

from auth.database import _get_connection, _return_connection
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)


# ============================================================================
# PRODUCT OPERATIONS
# ============================================================================


async def get_all_products(
    limit: int = 50,
    offset: int = 0,
    categoria: Optional[str] = None,
    activo: bool = True,
) -> Tuple[List[dict], int]:
    """
    Obtiene todos los productos con paginación y filtros.
    Retorna (productos, total_count)
    """
    conn = None
    try:
        conn = await _get_connection()
        async with conn.cursor(row_factory=dict_row) as cur:
            # Construir query con filtros
            where_clauses = []
            params = []

            if activo is not None:
                where_clauses.append("activo = %s")
                params.append(activo)

            if categoria:
                where_clauses.append("categoria = %s")
                params.append(categoria)

            where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

            # Contar total
            count_query = f"SELECT COUNT(*) FROM inventario_productos{where_sql}"
            await cur.execute(count_query, params)
            total = (await cur.fetchone())["count"]

            # Obtener productos
            query = f"""
                SELECT 
                    id, codigo_producto, nombre, categoria, 
                    stock_actual, stock_minimo, stock_maximo, unidad_medida,
                    costo_unitario, precio_venta, activo
                FROM inventario_productos
                {where_sql}
                ORDER BY nombre
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            await cur.execute(query, params)
            productos = await cur.fetchall()

            return [dict(p) for p in productos] if productos else [], total
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return [], 0
    finally:
        if conn:
            await _return_connection(conn)


async def get_product_by_id(product_id: int) -> Optional[dict]:
    """
    Obtiene un producto por ID con todos sus detalles.
    """
    conn = None
    try:
        conn = await _get_connection()
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT 
                    id, codigo_producto, codigo_barras, nombre, descripcion,
                    categoria, subcategoria, stock_actual, stock_minimo, stock_maximo,
                    unidad_medida, costo_unitario, precio_venta, margen_ganancia,
                    id_proveedor, tiempo_reposicion_dias, requiere_receta, controlado,
                    tiene_caducidad, fecha_caducidad, lote, ubicacion_almacen,
                    activo, fecha_registro, registrado_por
                FROM inventario_productos
                WHERE id = %s
                """,
                (product_id,),
            )
            product = await cur.fetchone()
            return dict(product) if product else None
    except Exception as e:
        logger.error(f"Error fetching product by id: {e}")
        return None
    finally:
        if conn:
            await _return_connection(conn)


async def create_product(
    codigo_producto: str,
    nombre: str,
    categoria: str,
    unidad_medida: str,
    registrado_por: int,
    **kwargs,
) -> Optional[dict]:
    """
    Crea un nuevo producto en el inventario.
    """
    conn = None
    try:
        conn = await _get_connection()
        async with conn.cursor(row_factory=dict_row) as cur:
            # Construir query dinámicamente con los campos opcionales
            fields = [
                "codigo_producto",
                "nombre",
                "categoria",
                "unidad_medida",
                "registrado_por",
            ]
            values_placeholders = ["%s", "%s", "%s", "%s", "%s"]
            values = [codigo_producto, nombre, categoria, unidad_medida, registrado_por]

            # Agregar campos opcionales si están presentes
            optional_fields = [
                "codigo_barras",
                "descripcion",
                "subcategoria",
                "stock_actual",
                "stock_minimo",
                "stock_maximo",
                "costo_unitario",
                "precio_venta",
                "margen_ganancia",
                "id_proveedor",
                "tiempo_reposicion_dias",
                "requiere_receta",
                "controlado",
                "tiene_caducidad",
                "fecha_caducidad",
                "lote",
                "ubicacion_almacen",
            ]

            for field in optional_fields:
                if field in kwargs and kwargs[field] is not None:
                    fields.append(field)
                    values_placeholders.append("%s")
                    values.append(kwargs[field])

            query = f"""
                INSERT INTO inventario_productos ({', '.join(fields)})
                VALUES ({', '.join(values_placeholders)})
                RETURNING id, codigo_producto, nombre, categoria, stock_actual, 
                          stock_minimo, stock_maximo, unidad_medida, activo
            """

            await cur.execute(query, values)
            product = await cur.fetchone()
            await conn.commit()

            return dict(product) if product else None
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        return None
    finally:
        if conn:
            await _return_connection(conn)


async def update_product(product_id: int, **kwargs) -> Optional[dict]:
    """
    Actualiza un producto existente.
    """
    conn = None
    try:
        conn = await _get_connection()
        async with conn.cursor(row_factory=dict_row) as cur:
            updates = []
            params = []

            # Campos actualizables
            updatable_fields = [
                "codigo_barras",
                "nombre",
                "descripcion",
                "categoria",
                "subcategoria",
                "stock_minimo",
                "stock_maximo",
                "unidad_medida",
                "costo_unitario",
                "precio_venta",
                "margen_ganancia",
                "id_proveedor",
                "tiempo_reposicion_dias",
                "requiere_receta",
                "controlado",
                "tiene_caducidad",
                "fecha_caducidad",
                "lote",
                "ubicacion_almacen",
                "activo",
            ]

            for field in updatable_fields:
                if field in kwargs and kwargs[field] is not None:
                    updates.append(f"{field} = %s")
                    params.append(kwargs[field])

            if not updates:
                return await get_product_by_id(product_id)

            params.append(product_id)
            query = f"""
                UPDATE inventario_productos
                SET {', '.join(updates)}
                WHERE id = %s
                RETURNING id, codigo_producto, nombre, categoria, stock_actual,
                          stock_minimo, stock_maximo, unidad_medida, activo
            """

            await cur.execute(query, params)
            product = await cur.fetchone()
            await conn.commit()

            return dict(product) if product else None
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        return None
    finally:
        if conn:
            await _return_connection(conn)


# ============================================================================
# STOCK OPERATIONS
# ============================================================================


async def adjust_stock(
    product_id: int,
    tipo_movimiento: str,
    cantidad: int,
    motivo: str,
    registrado_por: int,
    costo_unitario: Optional[Decimal] = None,
    numero_factura_proveedor: Optional[str] = None,
    lote: Optional[str] = None,
    fecha_caducidad: Optional[date] = None,
) -> Optional[dict]:
    """
    Registra un ajuste de stock (entrada, salida, ajuste, etc.).
    El trigger actualiza automáticamente el stock_actual.
    """
    conn = None
    try:
        conn = await _get_connection()
        async with conn.cursor(row_factory=dict_row) as cur:
            # Obtener stock actual
            await cur.execute(
                "SELECT stock_actual FROM inventario_productos WHERE id = %s",
                (product_id,),
            )
            result = await cur.fetchone()
            if not result:
                return None

            stock_anterior = result["stock_actual"]

            # Insertar movimiento (el trigger actualiza stock_nuevo y stock_actual)
            query = """
                INSERT INTO movimientos_inventario (
                    id_producto, tipo_movimiento, cantidad, stock_anterior,
                    motivo, registrado_por, costo_unitario, costo_total,
                    numero_factura_proveedor, lote, fecha_caducidad
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, id_producto, tipo_movimiento, cantidad, 
                          stock_anterior, stock_nuevo, fecha_movimiento
            """

            costo_total = (costo_unitario * cantidad) if costo_unitario else None

            await cur.execute(
                query,
                (
                    product_id,
                    tipo_movimiento,
                    cantidad,
                    stock_anterior,
                    motivo,
                    registrado_por,
                    costo_unitario,
                    costo_total,
                    numero_factura_proveedor,
                    lote,
                    fecha_caducidad,
                ),
            )

            movement = await cur.fetchone()
            await conn.commit()

            return dict(movement) if movement else None
    except Exception as e:
        logger.error(f"Error adjusting stock: {e}")
        return None
    finally:
        if conn:
            await _return_connection(conn)


async def get_low_stock_alerts() -> List[dict]:
    """
    Obtiene productos con stock bajo usando la vista alertas_stock_bajo.
    """
    conn = None
    try:
        conn = await _get_connection()
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT 
                    id, codigo_producto, nombre, categoria,
                    stock_actual, stock_minimo, cantidad_requerida,
                    proveedor, telefono_proveedor, tiempo_reposicion_dias,
                    costo_unitario, costo_reposicion
                FROM alertas_stock_bajo
                ORDER BY cantidad_requerida DESC
            """
            )
            alerts = await cur.fetchall()
            return [dict(a) for a in alerts] if alerts else []
    except Exception as e:
        logger.error(f"Error fetching low stock alerts: {e}")
        return []
    finally:
        if conn:
            await _return_connection(conn)
