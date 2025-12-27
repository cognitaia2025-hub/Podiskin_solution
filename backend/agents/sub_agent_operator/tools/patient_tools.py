"""
Tools de Pacientes - Herramientas para consultar y gestionar pacientes
======================================================================

Funciones para interactuar con la tabla de pacientes en PostgreSQL.
"""

import logging
from typing import Dict, List, Any, Optional

from ..utils.database import _get_connection, _put_connection

logger = logging.getLogger(__name__)


def search_patients(
    query: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Busca pacientes en la base de datos.

    Args:
        query: Texto para buscar en nombre o teléfono
        filters: Filtros adicionales (estado, etc.)
        limit: Máximo número de resultados

    Returns:
        Lista de pacientes encontrados
    """
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        # Query base
        sql = """
            SELECT 
                id,
                nombre,
                telefono,
                email,
                fecha_nacimiento,
                direccion,
                notas,
                fecha_registro
            FROM pacientes
            WHERE 1=1
        """
        params = []

        # Búsqueda por texto
        if query:
            sql += " AND (nombre ILIKE %s OR telefono ILIKE %s)"
            params.extend([f"%{query}%", f"%{query}%"])

        # Filtros adicionales
        if filters:
            if filters.get("estado"):
                # Asumiendo que hay un campo estado
                sql += " AND estado = %s"
                params.append(filters["estado"])

        # Ordenar por nombre
        sql += " ORDER BY nombre"

        # Limitar
        sql += f" LIMIT {limit}"

        logger.debug(f"Executing query: {sql} with params: {params}")
        cursor.execute(sql, params)

        # Convertir resultados
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            result = dict(zip(columns, row))
            # Convertir dates a strings
            if result.get("fecha_nacimiento"):
                result["fecha_nacimiento"] = result["fecha_nacimiento"].isoformat()
            if result.get("fecha_registro"):
                result["fecha_registro"] = result["fecha_registro"].isoformat()
            results.append(result)

        cursor.close()
        logger.info(f"Found {len(results)} patients")
        return results

    except Exception as e:
        logger.error(f"Error searching patients: {e}", exc_info=True)
        return []

    finally:
        if conn:
            _put_connection(conn)


def get_patient_by_id(patient_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene un paciente por su ID.

    Args:
        patient_id: ID del paciente

    Returns:
        Diccionario con datos del paciente o None
    """
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                id,
                nombre,
                telefono,
                email,
                fecha_nacimiento,
                direccion,
                notas,
                fecha_registro
            FROM pacientes
            WHERE id = %s
        """

        cursor.execute(query, (patient_id,))
        row = cursor.fetchone()

        if row:
            columns = [desc[0] for desc in cursor.description]
            result = dict(zip(columns, row))
            # Convertir dates a strings
            if result.get("fecha_nacimiento"):
                result["fecha_nacimiento"] = result["fecha_nacimiento"].isoformat()
            if result.get("fecha_registro"):
                result["fecha_registro"] = result["fecha_registro"].isoformat()
            cursor.close()
            return result

        cursor.close()
        return None

    except Exception as e:
        logger.error(f"Error getting patient {patient_id}: {e}", exc_info=True)
        return None

    finally:
        if conn:
            _put_connection(conn)


def get_patient_history(patient_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Obtiene el historial de citas de un paciente.

    Args:
        patient_id: ID del paciente
        limit: Máximo número de citas a retornar

    Returns:
        Lista de citas del paciente
    """
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                id,
                fecha,
                hora,
                duracion,
                tratamiento,
                estado,
                notas
            FROM citas
            WHERE paciente_id = %s
            ORDER BY fecha DESC, hora DESC
            LIMIT %s
        """

        cursor.execute(query, (patient_id, limit))

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
        logger.info(f"Found {len(results)} appointments for patient {patient_id}")
        return results

    except Exception as e:
        logger.error(f"Error getting patient history: {e}", exc_info=True)
        return []

    finally:
        if conn:
            _put_connection(conn)
