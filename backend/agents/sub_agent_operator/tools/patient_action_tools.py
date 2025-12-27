"""
Tools de Pacientes - Acciones
==============================

Funciones para crear y actualizar pacientes.
"""

import logging
from typing import Dict, Any

from ..utils.database import _get_connection, _put_connection

logger = logging.getLogger(__name__)


def create_patient(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea un nuevo paciente.

    Args:
        data: Diccionario con datos del paciente
            - nombre: Nombre completo (requerido)
            - telefono: Teléfono (requerido)
            - email: Email (opcional)
            - fecha_nacimiento: Fecha de nacimiento (opcional)
            - direccion: Dirección (opcional)
            - notas: Notas (opcional)

    Returns:
        Diccionario con resultado de la operación
    """
    conn = None
    try:
        # Validar datos requeridos
        if not data.get("nombre") or not data.get("telefono"):
            return {"success": False, "error": "Nombre y teléfono son requeridos"}

        conn = _get_connection()
        cursor = conn.cursor()

        # Insertar paciente
        query = """
            INSERT INTO pacientes (
                nombre, telefono, email, fecha_nacimiento, 
                direccion, notas, fecha_registro
            )
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE)
            RETURNING id
        """

        params = (
            data["nombre"],
            data["telefono"],
            data.get("email", ""),
            data.get("fecha_nacimiento"),
            data.get("direccion", ""),
            data.get("notas", ""),
        )

        cursor.execute(query, params)
        patient_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()

        logger.info(f"Created patient {patient_id}")

        return {
            "success": True,
            "patient_id": patient_id,
            "message": f"Paciente creado exitosamente (ID: {patient_id})",
        }

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error creating patient: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

    finally:
        if conn:
            _put_connection(conn)


def update_patient(patient_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Actualiza datos de un paciente.

    Args:
        patient_id: ID del paciente
        updates: Diccionario con campos a actualizar

    Returns:
        Diccionario con resultado de la operación
    """
    conn = None
    try:
        if not updates:
            return {"success": False, "error": "No hay campos para actualizar"}

        conn = _get_connection()
        cursor = conn.cursor()

        # Construir query dinámicamente
        set_clauses = []
        params = []

        allowed_fields = [
            "nombre",
            "telefono",
            "email",
            "fecha_nacimiento",
            "direccion",
            "notas",
        ]

        for field in allowed_fields:
            if field in updates:
                set_clauses.append(f"{field} = %s")
                params.append(updates[field])

        if not set_clauses:
            return {"success": False, "error": "No hay campos válidos para actualizar"}

        params.append(patient_id)

        query = f"""
            UPDATE pacientes 
            SET {', '.join(set_clauses)}
            WHERE id = %s
        """

        cursor.execute(query, params)
        rows_affected = cursor.rowcount

        conn.commit()
        cursor.close()

        if rows_affected == 0:
            return {
                "success": False,
                "error": f"No se encontró el paciente con ID {patient_id}",
            }

        logger.info(f"Updated patient {patient_id}")

        return {
            "success": True,
            "patient_id": patient_id,
            "message": "Paciente actualizado exitosamente",
        }

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error updating patient: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

    finally:
        if conn:
            _put_connection(conn)
