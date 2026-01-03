"""
Stats Router - Estadísticas del Dashboard
==========================================
Endpoints para métricas y estadísticas del sistema.
"""

from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from psycopg.rows import dict_row

from auth.middleware import get_current_user
from auth.database import _get_connection, _return_connection


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
    description="Obtiene todas las métricas principales del sistema"
)
async def get_dashboard_stats(
    current_user=Depends(get_current_user)
):
    """
    Retorna estadísticas generales del dashboard con datos REALES de la BD.
    Por ahora retorna valores iniciales (ceros) para una app nueva.
    """
    
    conn = None
    try:
        conn = await _get_connection()
        
        # Fechas para filtros
        first_day_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
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
                (first_day_month,)
            )
            new_patients_month = (await cur.fetchone())[0] or 0
            
            # Citas de hoy
            await cur.execute(
                "SELECT COUNT(*) FROM citas WHERE fecha_hora >= %s AND fecha_hora < %s",
                (today_start, today_end)
            )
            appt_today = (await cur.fetchone())[0] or 0
            
            # Citas de esta semana
            await cur.execute(
                "SELECT COUNT(*) FROM citas WHERE fecha_hora >= %s AND fecha_hora < %s",
                (week_start, week_end)
            )
            appt_week = (await cur.fetchone())[0] or 0
            
            # Citas de este mes
            await cur.execute(
                "SELECT COUNT(*) FROM citas WHERE fecha_hora >= %s AND fecha_hora < %s",
                (first_day_month, month_end)
            )
            appt_month = (await cur.fetchone())[0] or 0
            
            # Citas por estado
            await cur.execute(
                """
                SELECT estado, COUNT(*) as cantidad
                FROM citas
                WHERE fecha_hora >= %s
                GROUP BY estado
                """,
                (first_day_month,)
            )
            status_rows = await cur.fetchall()
            status_dict = {row[0]: row[1] for row in status_rows}
            
            # Próximas citas (siguientes 7 días)
            await cur.execute(
                """
                SELECT COUNT(*) FROM citas 
                WHERE fecha_hora >= %s AND fecha_hora < %s
                AND estado NOT IN ('cancelada', 'completada')
                """,
                (today_start, future_7days)
            )
            upcoming = (await cur.fetchone())[0] or 0
        
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
                pendiente=status_dict.get('pendiente', 0),
                confirmada=status_dict.get('confirmada', 0),
                completada=status_dict.get('completada', 0),
                cancelada=status_dict.get('cancelada', 0),
                no_asistio=status_dict.get('no_asistio', 0)
            ),
            revenue_today=revenue_today,
            revenue_week=revenue_week,
            revenue_month=revenue_month,
            revenue_year=revenue_year,
            top_treatments=[],  # TODO: Implementar cuando exista tabla tratamientos
            ocupacion_porcentaje=0.0,  # TODO: Calcular basado en horarios
            upcoming_appointments=upcoming
        )
        
    except Exception as e:
        if conn:
            await conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )
    finally:
        if conn:
            await _return_connection(conn)


@router.get(
    "/appointments-trend",
    response_model=List[AppointmentTrend],
    summary="Tendencia de citas",
    description="Obtiene la cantidad de citas por día en los últimos N días"
)
async def get_appointments_trend(
    days: int = 30,
    current_user=Depends(get_current_user)
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
                    fecha_hora::date as fecha,
                    COUNT(*) as cantidad,
                    COUNT(*) FILTER (WHERE estado = 'completada') as completadas,
                    COUNT(*) FILTER (WHERE estado = 'cancelada') as canceladas
                FROM citas
                WHERE fecha_hora >= %s
                GROUP BY fecha_hora::date
                ORDER BY fecha
                """,
                (start_date,)
            )
            rows = await cur.fetchall()
        
        # Cerrar transacción de solo lectura
        await conn.rollback()
        
        return [
            AppointmentTrend(
                fecha=str(row['fecha']),
                cantidad=int(row['cantidad']),
                completadas=int(row['completadas'] or 0),
                canceladas=int(row['canceladas'] or 0)
            )
            for row in rows
        ]
        
    except Exception as e:
        if conn:
            await conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo tendencia de citas: {str(e)}"
        )
    finally:
        if conn:
            await _return_connection(conn)


@router.get(
    "/revenue-trend",
    response_model=List[RevenueTrend],
    summary="Tendencia de ingresos",
    description="Obtiene los ingresos por mes del último año"
)
async def get_revenue_trend(
    current_user=Depends(get_current_user)
):
    """Retorna tendencia de ingresos del último año"""
    # Por ahora retornar lista vacía hasta implementar módulo de pagos
    return []
