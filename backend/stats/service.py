"""
Servicio de Estadísticas
========================
Cálculo de métricas y estadísticas del sistema
"""

from datetime import datetime, timedelta, date
from typing import List, Dict, Any
import asyncpg

from .models import TreatmentStats, OccupancyStats, DashboardStats

async def calculate_top_treatments(
    conn: asyncpg.Connection,
    fecha_inicio: date,
    fecha_fin: date,
    limit: int = 5
) -> List[TreatmentStats]:
    """
    Calcula los tratamientos más utilizados en un periodo.
    
    Args:
        conn: Conexión a la base de datos
        fecha_inicio: Fecha de inicio del periodo
        fecha_fin: Fecha de fin del periodo
        limit: Número máximo de tratamientos a retornar
        
    Returns:
        Lista de TreatmentStats ordenada por cantidad
    """
    query = """
        SELECT 
            tipo_tratamiento as tratamiento,
            COUNT(*) as cantidad,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as porcentaje
        FROM tratamientos
        WHERE fecha BETWEEN $1 AND $2
        GROUP BY tipo_tratamiento
        ORDER BY cantidad DESC
        LIMIT $3
    """
    
    try:
        rows = await conn.fetch(query, fecha_inicio, fecha_fin, limit)
        return [
            TreatmentStats(
                tratamiento=row['tratamiento'],
                cantidad=row['cantidad'],
                porcentaje=float(row['porcentaje'])
            )
            for row in rows
        ]
    except Exception as e:
        # Si la tabla no existe o hay error, retornar lista vacía
        print(f"Error calculando top treatments: {e}")
        return []

async def calculate_occupancy_stats(
    conn: asyncpg.Connection,
    fecha_inicio: date,
    fecha_fin: date,
    horario_inicio: str = "09:00",
    horario_fin: str = "18:00"
) -> List[OccupancyStats]:
    """
    Calcula la ocupación de la agenda por día.
    
    Args:
        conn: Conexión a la base de datos
        fecha_inicio: Fecha de inicio
        fecha_fin: Fecha de fin
        horario_inicio: Hora de inicio de jornada (HH:MM)
        horario_fin: Hora de fin de jornada (HH:MM)
        
    Returns:
        Lista de OccupancyStats por día
    """
    # Calcular horas disponibles por día
    hora_inicio_parts = horario_inicio.split(":")
    hora_fin_parts = horario_fin.split(":")
    horas_disponibles = (
        int(hora_fin_parts[0]) - int(hora_inicio_parts[0])
    )
    
    query = """
        WITH ocupacion_diaria AS (
            SELECT 
                fecha,
                COUNT(*) as citas_programadas,
                SUM(EXTRACT(EPOCH FROM (hora_fin - hora_inicio)) / 3600) as horas_ocupadas
            FROM citas
            WHERE fecha BETWEEN $1 AND $2
                AND estado NOT IN ('cancelada')
            GROUP BY fecha
        )
        SELECT 
            fecha,
            COALESCE(citas_programadas, 0) as citas_programadas,
            COALESCE(horas_ocupadas, 0) as horas_ocupadas,
            $3 as horas_disponibles,
            ROUND(
                COALESCE(horas_ocupadas, 0) * 100.0 / $3, 
                2
            ) as porcentaje_ocupacion
        FROM ocupacion_diaria
        ORDER BY fecha
    """
    
    try:
        rows = await conn.fetch(
            query, 
            fecha_inicio, 
            fecha_fin, 
            horas_disponibles
        )
        return [
            OccupancyStats(
                fecha=row['fecha'],
                horas_disponibles=horas_disponibles,
                horas_ocupadas=int(row['horas_ocupadas']),
                porcentaje_ocupacion=float(row['porcentaje_ocupacion']),
                citas_programadas=row['citas_programadas']
            )
            for row in rows
        ]
    except Exception as e:
        print(f"Error calculando ocupación: {e}")
        return []

async def calculate_average_occupancy(
    ocupacion: List[OccupancyStats]
) -> float:
    """
    Calcula el promedio de ocupación.
    
    Args:
        ocupacion: Lista de estadísticas de ocupación
        
    Returns:
        Porcentaje promedio de ocupación
    """
    if not ocupacion:
        return 0.0
    
    total = sum(stat.porcentaje_ocupacion for stat in ocupacion)
    return round(total / len(ocupacion), 2)

async def get_dashboard_stats(
    conn: asyncpg.Connection,
    fecha_inicio: date,
    fecha_fin: date
) -> DashboardStats:
    """
    Obtiene todas las estadísticas del dashboard.
    
    Args:
        conn: Conexión a la base de datos
        fecha_inicio: Fecha de inicio del periodo
        fecha_fin: Fecha de fin del periodo
        
    Returns:
        DashboardStats con todas las métricas
    """
    # Estadísticas básicas
    basic_query = """
        SELECT 
            (SELECT COUNT(*) FROM pacientes WHERE activo = true) as total_pacientes,
            (SELECT COUNT(*) FROM citas 
             WHERE EXTRACT(MONTH FROM fecha) = EXTRACT(MONTH FROM $1)
               AND EXTRACT(YEAR FROM fecha) = EXTRACT(YEAR FROM $1)) as total_citas_mes,
            (SELECT COALESCE(SUM(monto), 0) FROM pagos 
             WHERE EXTRACT(MONTH FROM fecha_pago) = EXTRACT(MONTH FROM $1)
               AND EXTRACT(YEAR FROM fecha_pago) = EXTRACT(YEAR FROM $1)
               AND estado = 'pagado') as ingresos_mes
    """
    
    basic_stats = await conn.fetchrow(basic_query, fecha_inicio)
    
    # Estadísticas avanzadas
    top_treatments = await calculate_top_treatments(conn, fecha_inicio, fecha_fin)
    ocupacion_semanal = await calculate_occupancy_stats(conn, fecha_inicio, fecha_fin)
    ocupacion_promedio = await calculate_average_occupancy(ocupacion_semanal)
    
    # Calcular tendencias (comparar con mes anterior)
    mes_anterior_inicio = fecha_inicio - timedelta(days=30)
    mes_anterior_fin = fecha_inicio - timedelta(days=1)
    
    trends_query = """
        SELECT 
            (SELECT COUNT(*) FROM pacientes 
             WHERE fecha_registro BETWEEN $1 AND $2) as pacientes_mes_anterior,
            (SELECT COALESCE(SUM(monto), 0) FROM pagos 
             WHERE fecha_pago BETWEEN $1 AND $2
               AND estado = 'pagado') as ingresos_mes_anterior
    """
    
    trends = await conn.fetchrow(trends_query, mes_anterior_inicio, mes_anterior_fin)
    
    # Calcular crecimientos
    crecimiento_pacientes = 0.0
    if trends['pacientes_mes_anterior'] > 0:
        crecimiento_pacientes = round(
            ((basic_stats['total_pacientes'] - trends['pacientes_mes_anterior']) / 
             trends['pacientes_mes_anterior']) * 100, 
            2
        )
    
    crecimiento_ingresos = 0.0
    if trends['ingresos_mes_anterior'] > 0:
        crecimiento_ingresos = round(
            ((basic_stats['ingresos_mes'] - trends['ingresos_mes_anterior']) / 
             trends['ingresos_mes_anterior']) * 100, 
            2
        )
    
    return DashboardStats(
        total_pacientes=basic_stats['total_pacientes'],
        total_citas_mes=basic_stats['total_citas_mes'],
        ingresos_mes=float(basic_stats['ingresos_mes']),
        top_treatments=top_treatments,
        ocupacion_semanal=ocupacion_semanal,
        ocupacion_promedio=ocupacion_promedio,
        crecimiento_pacientes=crecimiento_pacientes,
        crecimiento_ingresos=crecimiento_ingresos
    )
