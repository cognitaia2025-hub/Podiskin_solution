"""
Stats Router - Estadísticas del Dashboard
==========================================
Endpoints para métricas y estadísticas del sistema.
"""

from typing import List, Optional
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from psycopg.rows import dict_row
import logging

from auth.middleware import get_current_user
from auth.database import _get_connection, _return_connection

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/stats", tags=["Estadísticas"])


# ============================================================================
# MODELS
# ============================================================================


class AppointmentsByStatus(BaseModel):
    """Citas por estado"""

    pendiente: int = 0
    confirmada: int = 0
    completada: int = 0
    cancelada: int = 0
    no_asistio: int = 0


class TopTreatment(BaseModel):
    """Tratamiento más común"""

    nombre: str
    cantidad: int


class DashboardStats(BaseModel):
    """Estadísticas generales del dashboard"""

    # Métricas de pacientes
    total_patients: int
    active_patients: int
    new_patients_this_month: int

    # Citas
    total_appointments_today: int
    total_appointments_week: int
    total_appointments_month: int
    appointments_by_status: AppointmentsByStatus

    # Ingresos
    revenue_today: float
    revenue_week: float
    revenue_month: float
    revenue_year: float

    # Tratamientos
    top_treatments: List[TopTreatment]

    # Ocupación
    ocupacion_porcentaje: float

    # Próximas citas
    upcoming_appointments: int


class AppointmentTrend(BaseModel):
    """Tendencia de citas por día"""

    fecha: str
    cantidad: int
    completadas: int
    canceladas: int


class RevenueTrend(BaseModel):
    """Tendencia de ingresos por mes"""

    mes: str
    ingresos: float


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get(
    "/dashboard",
    response_model=DashboardStats,
    summary="Estadísticas del dashboard",
    description="Obtiene todas las métricas principales del sistema",
)
async def get_dashboard_stats(current_user=Depends(get_current_user)):
    """
    Retorna estadísticas generales del dashboard con datos REALES de la BD.
    Por ahora retorna valores iniciales (ceros) para una app nueva.
    """

    conn = None
    try:
        conn = await _get_connection()

        # Fechas para filtros
        first_day_month = datetime.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        week_start = today_start - timedelta(days=today_start.weekday())
        week_end = week_start + timedelta(days=7)
        month_end = (first_day_month + timedelta(days=32)).replace(day=1)
        future_7days = today_start + timedelta(days=7)

        async with conn.cursor() as cur:
            # Contar pacientes totales y activos
            await cur.execute("SELECT COUNT(*) FROM pacientes WHERE activo = true")
            total_patients = (await cur.fetchone())[0] or 0

            # Pacientes nuevos este mes
            await cur.execute(
                "SELECT COUNT(*) FROM pacientes WHERE fecha_registro >= %s AND activo = true",
                (first_day_month,),
            )
            new_patients_month = (await cur.fetchone())[0] or 0

            # Citas de hoy
            await cur.execute(
                "SELECT COUNT(*) FROM citas WHERE fecha_hora_inicio >= %s AND fecha_hora_inicio < %s",
                (today_start, today_end),
            )
            appt_today = (await cur.fetchone())[0] or 0

            # Citas de esta semana
            await cur.execute(
                "SELECT COUNT(*) FROM citas WHERE fecha_hora_inicio >= %s AND fecha_hora_inicio < %s",
                (week_start, week_end),
            )
            appt_week = (await cur.fetchone())[0] or 0

            # Citas de este mes
            await cur.execute(
                "SELECT COUNT(*) FROM citas WHERE fecha_hora_inicio >= %s AND fecha_hora_inicio < %s",
                (first_day_month, month_end),
            )
            appt_month = (await cur.fetchone())[0] or 0

            # Citas por estado
            await cur.execute(
                """
                SELECT estado, COUNT(*) as cantidad
                FROM citas
                WHERE fecha_hora_inicio >= %s
                GROUP BY estado
                """,
                (first_day_month,),
            )
            status_rows = await cur.fetchall()
            status_dict = {row[0]: row[1] for row in status_rows}

            # Próximas citas (siguientes 7 días)
            await cur.execute(
                """
                SELECT COUNT(*) FROM citas 
                WHERE fecha_hora_inicio >= %s AND fecha_hora_inicio < %s
                AND estado NOT IN ('cancelada', 'completada')
                """,
                (today_start, future_7days),
            )
            upcoming = (await cur.fetchone())[0] or 0

            # Top tratamientos (5 más frecuentes del mes)
            await cur.execute(
                """
                SELECT t.nombre_servicio, COUNT(dc.id) as cantidad
                FROM detalle_cita dc
                INNER JOIN tratamientos t ON dc.id_tratamiento = t.id
                INNER JOIN citas c ON dc.id_cita = c.id
                WHERE c.fecha_hora_inicio >= %s
                AND c.estado != 'cancelada'
                GROUP BY t.id, t.nombre_servicio
                ORDER BY cantidad DESC
                LIMIT 5
                """,
                (first_day_month,),
            )
            top_treatments_rows = await cur.fetchall()
            top_treatments = [
                TopTreatment(nombre=row[0], cantidad=row[1])
                for row in top_treatments_rows
            ]

            # Calcular porcentaje de ocupación basado en horarios
            # Ocupación = (horas con citas) / (horas disponibles) * 100
            # Calculamos para la semana actual
            await cur.execute(
                """
                WITH horarios_disponibles AS (
                    -- Calcular slots disponibles por día
                    SELECT 
                        dia_semana,
                        SUM(
                            EXTRACT(EPOCH FROM (hora_fin - hora_inicio)) / 
                            (duracion_cita_minutos * 60)
                        ) as slots_disponibles
                    FROM horarios_trabajo
                    WHERE activo = true
                    AND (fecha_fin_vigencia IS NULL OR fecha_fin_vigencia >= CURRENT_DATE)
                    GROUP BY dia_semana
                ),
                citas_semana AS (
                    -- Contar citas de esta semana
                    SELECT 
                        EXTRACT(DOW FROM fecha_hora_inicio)::integer as dia_semana,
                        COUNT(*) as citas_realizadas
                    FROM citas
                    WHERE fecha_hora_inicio >= %s 
                    AND fecha_hora_inicio < %s
                    AND estado NOT IN ('cancelada', 'no_asistio')
                    GROUP BY dia_semana
                )
                SELECT 
                    COALESCE(SUM(cs.citas_realizadas), 0) as total_citas,
                    COALESCE(SUM(hd.slots_disponibles), 0) as total_slots
                FROM horarios_disponibles hd
                LEFT JOIN citas_semana cs ON hd.dia_semana = cs.dia_semana
                """,
                (week_start, week_end),
            )
            ocupacion_row = await cur.fetchone()
            total_citas = ocupacion_row[0] or 0
            total_slots = ocupacion_row[1] or 0
            ocupacion_porcentaje = (
                (total_citas / total_slots * 100) if total_slots > 0 else 0.0
            )

        # Cerrar transacción de solo lectura
        await conn.rollback()

        # Ingresos (si no hay tabla de pagos, retornar 0)
        revenue_today = 0
        revenue_week = 0
        revenue_month = 0
        revenue_year = 0

        return DashboardStats(
            total_patients=total_patients,
            active_patients=total_patients,  # Todos los activos
            new_patients_this_month=new_patients_month,
            total_appointments_today=appt_today,
            total_appointments_week=appt_week,
            total_appointments_month=appt_month,
            appointments_by_status=AppointmentsByStatus(
                pendiente=status_dict.get("pendiente", 0),
                confirmada=status_dict.get("confirmada", 0),
                completada=status_dict.get("completada", 0),
                cancelada=status_dict.get("cancelada", 0),
                no_asistio=status_dict.get("no_asistio", 0),
            ),
            revenue_today=revenue_today,
            revenue_week=revenue_week,
            revenue_month=revenue_month,
            revenue_year=revenue_year,
            top_treatments=top_treatments,
            ocupacion_porcentaje=round(ocupacion_porcentaje, 2),
            upcoming_appointments=upcoming,
        )

    except Exception as e:
        logger.warning(
            f"Error obteniendo estadísticas (retornando valores vacíos): {e}"
        )
        if conn:
            await conn.rollback()

        # Retornar estadísticas vacías en lugar de error 500
        return DashboardStats(
            total_patients=0,
            active_patients=0,
            new_patients_this_month=0,
            total_appointments_today=0,
            total_appointments_week=0,
            total_appointments_month=0,
            appointments_by_status=AppointmentsByStatus(),
            revenue_today=0.0,
            revenue_week=0.0,
            revenue_month=0.0,
            revenue_year=0.0,
            top_treatments=[],
            ocupacion_porcentaje=0.0,
            upcoming_appointments=0,
        )
    finally:
        if conn:
            await _return_connection(conn)


@router.get(
    "/appointments-trend",
    response_model=List[AppointmentTrend],
    summary="Tendencia de citas",
    description="Obtiene la cantidad de citas por día en los últimos N días",
)
async def get_appointments_trend(
    days: int = 30, current_user=Depends(get_current_user)
):
    """Retorna tendencia de citas de los últimos N días"""

    conn = None
    try:
        conn = await _get_connection()

        start_date = datetime.now() - timedelta(days=days)

        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT 
                    fecha_hora_inicio::date as fecha,
                    COUNT(*) as cantidad,
                    COUNT(*) FILTER (WHERE estado = 'completada') as completadas,
                    COUNT(*) FILTER (WHERE estado = 'cancelada') as canceladas
                FROM citas
                WHERE fecha_hora_inicio >= %s
                GROUP BY fecha_hora_inicio::date
                ORDER BY fecha
                """,
                (start_date,),
            )
            rows = await cur.fetchall()

        # Cerrar transacción de solo lectura
        await conn.rollback()

        return [
            AppointmentTrend(
                fecha=str(row["fecha"]),
                cantidad=int(row["cantidad"]),
                completadas=int(row["completadas"] or 0),
                canceladas=int(row["canceladas"] or 0),
            )
            for row in rows
        ]

    except Exception as e:
        logger.warning(
            f"Error obteniendo tendencia de citas (retornando lista vacía): {e}"
        )
        if conn:
            await conn.rollback()
        # Retornar lista vacía en lugar de error 500
        return []
    finally:
        if conn:
            await _return_connection(conn)


@router.get(
    "/revenue-trend",
    response_model=List[RevenueTrend],
    summary="Tendencia de ingresos",
    description="Obtiene los ingresos por mes del último año",
)
async def get_revenue_trend(current_user=Depends(get_current_user)):
    """Retorna tendencia de ingresos del último año"""
    # Por ahora retornar lista vacía hasta implementar módulo de pagos
    return []


# ============================================================================
# NUEVO ENDPOINT: MÉTRICAS FINANCIERAS
# ============================================================================


class GastoPorCategoria(BaseModel):
    """Gasto por categoría"""

    categoria: str
    monto_total: float
    cantidad_gastos: int
    porcentaje: float


class ServicioRentable(BaseModel):
    """Servicio rentable con margen calculado"""

    nombre: str
    precio: float
    cantidad_veces_usado: int
    ingresos_generados: float
    costo_materiales_estimado: float
    margen_estimado: float


class ProductoCritico(BaseModel):
    """Producto con stock crítico"""

    id: int
    nombre: str
    stock_actual: float
    stock_minimo: int
    porcentaje_stock: float
    categoria: str
    unidad_medida: str


class MetricasFinancieras(BaseModel):
    """Métricas financieras completas para análisis de rentabilidad"""

    # Gastos
    gastos_fijos_mes: float
    gastos_variables_mes: float
    gastos_total_mes: float
    gastos_por_categoria: List[GastoPorCategoria]

    # Ingresos
    ingresos_mes: float

    # Pacientes
    total_pacientes_mes: int
    costo_promedio_paciente: float

    # Servicios
    servicios_rentables: List[ServicioRentable]

    # Inventario
    productos_criticos: List[ProductoCritico]

    # Resumen
    utilidad_bruta: float
    margen_utilidad: float


@router.get(
    "/metricas-financieras",
    response_model=MetricasFinancieras,
    summary="Métricas financieras completas",
    description="KPIs financieros: gastos por categoría, servicios rentables, productos críticos",
)
@router.get(
    "/metricas-financieras",
    response_model=MetricasFinancieras,
    summary="Métricas financieras completas",
    description="KPIs financieros: gastos por categoría, servicios rentables, productos críticos",
)
async def get_metricas_financieras(
    mes: Optional[int] = Query(
        None, ge=1, le=12, description="Mes (1-12), default mes actual"
    ),
    anio: Optional[int] = Query(None, ge=2020, description="Año, default año actual"),
    current_user=Depends(get_current_user),
):
    """
    Obtiene métricas financieras completas del negocio.
    Retorna ceros si ocurre algún error.
    """
    conn = None
    try:
        conn = await _get_connection()

        # Fechas para el mes solicitado
        now = datetime.now()
        mes_target = mes or now.month
        anio_target = anio or now.year
        fecha_inicio = datetime(anio_target, mes_target, 1)
        if mes_target == 12:
            fecha_fin = datetime(anio_target + 1, 1, 1)
        else:
            fecha_fin = datetime(anio_target, mes_target + 1, 1)

        # ===== GASTOS POR CATEGORÍA =====
        try:
            async with conn.transaction():
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT 
                            COALESCE(categoria::text, 'OTROS') as categoria,
                            SUM(monto) as monto_total,
                            COUNT(*) as cantidad_gastos
                        FROM gastos
                        WHERE fecha_gasto >= %s AND fecha_gasto < %s
                        GROUP BY categoria
                        ORDER BY monto_total DESC
                        """,
                        (fecha_inicio, fecha_fin),
                    )
                    gastos_rows = await cur.fetchall()
        except Exception as e:
            logger.error(f"Error consultando gastos: {e}")
            gastos_rows = []

        total_gastos = sum(row[1] for row in gastos_rows)

        gastos_por_categoria = [
            GastoPorCategoria(
                categoria=row[0],
                monto_total=float(row[1]),
                cantidad_gastos=row[2],
                porcentaje=(
                    (float(row[1]) / total_gastos * 100) if total_gastos > 0 else 0
                ),
            )
            for row in gastos_rows
        ]

        # Clasificar gastos fijos vs variables
        categorias_fijas = [
            "SERVICIOS_BASICOS",
            "SERVICIOS_PROFESIONALES",
            "RENTA_LOCAL",
            "SALARIOS_PERSONAL",
        ]
        gastos_fijos = sum(
            g.monto_total
            for g in gastos_por_categoria
            if g.categoria in categorias_fijas
        )
        gastos_variables = total_gastos - gastos_fijos

        # ===== INGRESOS DEL MES =====
        try:
            async with conn.transaction():
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT COALESCE(SUM(monto_pagado), 0) 
                        FROM pagos
                        WHERE fecha_pago >= %s AND fecha_pago < %s
                        """,
                        (fecha_inicio, fecha_fin),
                    )
                    ingresos_mes = float((await cur.fetchone())[0] or 0)
        except Exception as e:
            logger.error(f"Error consultando pagos: {e}")
            ingresos_mes = 0.0

        # ===== PACIENTES ATENDIDOS =====
        try:
            async with conn.transaction():
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT COUNT(DISTINCT id_paciente)
                        FROM citas
                        WHERE fecha_hora_inicio >= %s AND fecha_hora_inicio < %s
                        AND estado = 'completada'
                        """,
                        (fecha_inicio, fecha_fin),
                    )
                    total_pacientes_mes = (await cur.fetchone())[0] or 0
        except Exception as e:
            logger.error(f"Error consultando pacientes atendidos: {e}")
            total_pacientes_mes = 0

        costo_promedio_paciente = (
            (total_gastos / total_pacientes_mes) if total_pacientes_mes > 0 else 0
        )

        # ===== SERVICIOS MÁS RENTABLES =====
        servicios_rentables = []
        try:
            async with conn.transaction():
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT 
                            t.nombre_servicio,
                            t.precio_base,
                            COUNT(dc.id) as cantidad_veces,
                            SUM(t.precio_base) as ingresos_generados
                        FROM detalle_cita dc
                        INNER JOIN tratamientos t ON dc.id_tratamiento = t.id
                        INNER JOIN citas c ON dc.id_cita = c.id
                        WHERE c.fecha_hora_inicio >= %s AND c.fecha_hora_inicio < %s
                        AND c.estado = 'completada'
                        GROUP BY t.id, t.nombre_servicio, t.precio_base
                        ORDER BY ingresos_generados DESC
                        LIMIT 5
                        """,
                        (fecha_inicio, fecha_fin),
                    )
                    servicios_rows = await cur.fetchall()

            servicios_rentables = [
                ServicioRentable(
                    nombre=row[0],
                    precio=float(row[1] or 0),
                    cantidad_veces_usado=row[2],
                    ingresos_generados=float(row[3] or 0),
                    costo_materiales_estimado=float(row[3] or 0) * 0.15,
                    margen_estimado=85.0,
                )
                for row in servicios_rows
            ]
        except Exception as e:
            logger.error(f"Error consultando servicios rentables: {e}")
            servicios_rentables = []

        # ===== PRODUCTOS CRÍTICOS =====
        productos_criticos = []
        try:
            async with conn.transaction():
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT 
                            id,
                            nombre,
                            stock_actual,
                            stock_minimo,
                            COALESCE(categoria::text, 'Sin categoría') as categoria,
                            COALESCE(unidad_medida, 'UNIDAD') as unidad_medida
                        FROM inventario_productos
                        WHERE stock_actual < (stock_minimo * 1.3)
                        AND activo = true
                        ORDER BY (stock_actual::float / NULLIF(stock_minimo, 0)) ASC
                        LIMIT 10
                        """,
                    )
                    productos_rows = await cur.fetchall()

            productos_criticos = [
                ProductoCritico(
                    id=row[0],
                    nombre=row[1],
                    stock_actual=float(row[2]),
                    stock_minimo=row[3],
                    porcentaje_stock=(
                        (float(row[2]) / row[3] * 100) if row[3] > 0 else 0
                    ),
                    categoria=row[4],
                    unidad_medida=row[5],
                )
                for row in productos_rows
            ]
        except Exception as e:
            logger.error(f"Error consultando productos críticos: {e}")
            productos_criticos = []

        # Calcular utilidad y margen
        utilidad_bruta = ingresos_mes - total_gastos
        margen_utilidad = (
            (utilidad_bruta / ingresos_mes * 100) if ingresos_mes > 0 else 0
        )

        return MetricasFinancieras(
            gastos_fijos_mes=gastos_fijos,
            gastos_variables_mes=gastos_variables,
            gastos_total_mes=total_gastos,
            gastos_por_categoria=gastos_por_categoria,
            ingresos_mes=ingresos_mes,
            total_pacientes_mes=total_pacientes_mes,
            costo_promedio_paciente=costo_promedio_paciente,
            servicios_rentables=servicios_rentables,
            productos_criticos=productos_criticos,
            utilidad_bruta=utilidad_bruta,
            margen_utilidad=margen_utilidad,
        )

    except Exception as e:
        logger.error(f"Error crítico en metricas-financieras: {str(e)}")
        if conn:
            await conn.rollback()

        # Retornar objeto con ceros en lugar de error 500
        return MetricasFinancieras(
            gastos_fijos_mes=0.0,
            gastos_variables_mes=0.0,
            gastos_total_mes=0.0,
            gastos_por_categoria=[],
            ingresos_mes=0.0,
            total_pacientes_mes=0,
            costo_promedio_paciente=0.0,
            servicios_rentables=[],
            productos_criticos=[],
            utilidad_bruta=0.0,
            margen_utilidad=0.0,
        )
    finally:
        if conn:
            await _return_connection(conn)
