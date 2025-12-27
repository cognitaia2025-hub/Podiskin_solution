"""
Tools de Citas - Herramientas para consultar y gestionar citas
==============================================================

Funciones para interactuar con la tabla de citas en PostgreSQL.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date

from ..utils.database import _get_connection, _put_connection

logger = logging.getLogger(__name__)


def search_appointments(
    filters: Optional[Dict[str, Any]] = None, sort_by: str = "fecha", limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Busca citas en la base de datos con filtros opcionales.

    Args:
        filters: Diccionario con filtros (fecha, paciente_id, estado, etc.)
        sort_by: Campo por el cual ordenar (fecha, hora, paciente)
        limit: Máximo número de resultados

    Returns:
        Lista de citas encontradas
    """
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        # Construir query base
        query = """
            SELECT 
                c.id,
                c.paciente_id,
                p.nombre as paciente_nombre,
                p.telefono as paciente_telefono,
                c.fecha,
                c.hora,
                c.duracion,
                c.tratamiento,
                c.estado,
                c.notas
            FROM citas c
            JOIN pacientes p ON c.paciente_id = p.id
            WHERE 1=1
        """
        params = []

        # Aplicar filtros
        if filters:
            if filters.get("fecha"):
                query += " AND c.fecha = %s"
                params.append(filters["fecha"])

            if filters.get("paciente_id"):
                query += " AND c.paciente_id = %s"
                params.append(filters["paciente_id"])

            if filters.get("estado"):
                query += " AND c.estado = %s"
                params.append(filters["estado"])

            if filters.get("tratamiento"):
                query += " AND c.tratamiento ILIKE %s"
                params.append(f"%{filters['tratamiento']}%")

        # Ordenar
        valid_sort_fields = {
            "fecha": "c.fecha, c.hora",
            "hora": "c.hora",
            "paciente": "p.nombre",
        }
        order_by = valid_sort_fields.get(sort_by, "c.fecha, c.hora")
        query += f" ORDER BY {order_by}"

        # Limitar
        query += f" LIMIT {limit}"

        logger.debug(f"Executing query: {query} with params: {params}")
        cursor.execute(query, params)

        # Convertir resultados
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            result = dict(zip(columns, row))
            # Convertir date/time a strings
            if result.get("fecha"):
                result["fecha"] = result["fecha"].isoformat()
            if result.get("hora"):
                result["hora"] = str(result["hora"])
            results.append(result)

        cursor.close()
        logger.info(f"Found {len(results)} appointments")
        return results

    except Exception as e:
        logger.error(f"Error searching appointments: {e}", exc_info=True)
        return []

    finally:
        if conn:
            _put_connection(conn)


def get_appointment_by_id(appointment_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene una cita por su ID.

    Args:
        appointment_id: ID de la cita

    Returns:
        Diccionario con datos de la cita o None
    """
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                c.id,
                c.paciente_id,
                p.nombre as paciente_nombre,
                p.telefono as paciente_telefono,
                c.fecha,
                c.hora,
                c.duracion,
                c.tratamiento,
                c.estado,
                c.notas
            FROM citas c
            JOIN pacientes p ON c.paciente_id = p.id
            WHERE c.id = %s
        """

        cursor.execute(query, (appointment_id,))
        row = cursor.fetchone()

        if row:
            columns = [desc[0] for desc in cursor.description]
            result = dict(zip(columns, row))
            # Convertir date/time a strings
            if result.get("fecha"):
                result["fecha"] = result["fecha"].isoformat()
            if result.get("hora"):
                result["hora"] = str(result["hora"])
            cursor.close()
            return result

        cursor.close()
        return None

    except Exception as e:
        logger.error(f"Error getting appointment {appointment_id}: {e}", exc_info=True)
        return None

    finally:
        if conn:
            _put_connection(conn)


def check_availability(fecha: str, hora: str, duracion: int = 30) -> bool:
    """
    Verifica si un horario está disponible.

    Args:
        fecha: Fecha en formato YYYY-MM-DD
        hora: Hora en formato HH:MM
        duracion: Duración en minutos

    Returns:
        True si está disponible, False si no
    """
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        # Buscar citas que se traslapen
        query = """
            SELECT COUNT(*) 
            FROM citas 
            WHERE fecha = %s 
              AND estado != 'cancelada'
              AND (
                  (hora <= %s::time AND hora + (duracion || ' minutes')::interval > %s::time)
                  OR
                  (hora < (%s::time + (%s || ' minutes')::interval) AND hora >= %s::time)
              )
        """

        cursor.execute(query, (fecha, hora, hora, hora, duracion, hora))
        count = cursor.fetchone()[0]

        cursor.close()
        return count == 0

    except Exception as e:
        logger.error(f"Error checking availability: {e}", exc_info=True)
        return False

    finally:
        if conn:
            _put_connection(conn)
