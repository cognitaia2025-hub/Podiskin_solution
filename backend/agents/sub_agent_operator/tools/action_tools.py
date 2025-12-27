"""
Tools de Acciones - Crear, Modificar y Cancelar Citas
=====================================================

Funciones para crear, actualizar y cancelar citas en PostgreSQL.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..utils.database import _get_connection, _put_connection

logger = logging.getLogger(__name__)


def create_appointment(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea una nueva cita en la base de datos.

    Args:
        data: Diccionario con datos de la cita
            - paciente_id: ID del paciente (requerido)
            - fecha: Fecha en formato YYYY-MM-DD (requerido)
            - hora: Hora en formato HH:MM (requerido)
            - duracion: Duración en minutos (default: 30)
            - tratamiento: Tipo de tratamiento (requerido)
            - notas: Notas adicionales (opcional)

    Returns:
        Diccionario con resultado de la operación
    """
    conn = None
    try:
        # Validar datos requeridos
        required_fields = ["paciente_id", "fecha", "hora", "tratamiento"]
        for field in required_fields:
            if field not in data:
                return {"success": False, "error": f"Campo requerido faltante: {field}"}

        conn = _get_connection()
        cursor = conn.cursor()

        # Insertar cita
        query = """
            INSERT INTO citas (
                paciente_id, fecha, hora, duracion, 
                tratamiento, estado, notas
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        params = (
            data["paciente_id"],
            data["fecha"],
            data["hora"],
            data.get("duracion", 30),
            data["tratamiento"],
            "pendiente",  # Estado inicial
            data.get("notas", ""),
        )

        cursor.execute(query, params)
        appointment_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()

        logger.info(f"Created appointment {appointment_id}")

        return {
            "success": True,
            "appointment_id": appointment_id,
            "message": f"Cita creada exitosamente (ID: {appointment_id})",
        }

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error creating appointment: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

    finally:
        if conn:
            _put_connection(conn)


def update_appointment(appointment_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Actualiza una cita existente.

    Args:
        appointment_id: ID de la cita
        updates: Diccionario con campos a actualizar
            - fecha: Nueva fecha
            - hora: Nueva hora
            - duracion: Nueva duración
            - tratamiento: Nuevo tratamiento
            - estado: Nuevo estado
            - notas: Nuevas notas

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

        allowed_fields = ["fecha", "hora", "duracion", "tratamiento", "estado", "notas"]

        for field in allowed_fields:
            if field in updates:
                set_clauses.append(f"{field} = %s")
                params.append(updates[field])

        if not set_clauses:
            return {"success": False, "error": "No hay campos válidos para actualizar"}

        # Agregar ID al final de params
        params.append(appointment_id)

        query = f"""
            UPDATE citas 
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
                "error": f"No se encontró la cita con ID {appointment_id}",
            }

        logger.info(f"Updated appointment {appointment_id}")

        return {
            "success": True,
            "appointment_id": appointment_id,
            "message": f"Cita actualizada exitosamente",
        }

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error updating appointment: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

    finally:
        if conn:
            _put_connection(conn)


def cancel_appointment(
    appointment_id: int, reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Cancela una cita.

    Args:
        appointment_id: ID de la cita
        reason: Razón de la cancelación (opcional)

    Returns:
        Diccionario con resultado de la operación
    """
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        # Actualizar estado a cancelada
        query = """
            UPDATE citas 
            SET estado = 'cancelada',
                notas = CASE 
                    WHEN notas = '' THEN %s
                    ELSE notas || E'\n' || %s
                END
            WHERE id = %s
        """

        cancellation_note = f"Cancelada: {reason}" if reason else "Cancelada"

        cursor.execute(query, (cancellation_note, cancellation_note, appointment_id))
        rows_affected = cursor.rowcount

        conn.commit()
        cursor.close()

        if rows_affected == 0:
            return {
                "success": False,
                "error": f"No se encontró la cita con ID {appointment_id}",
            }

        logger.info(f"Cancelled appointment {appointment_id}")

        return {
            "success": True,
            "appointment_id": appointment_id,
            "message": f"Cita cancelada exitosamente",
        }

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error cancelling appointment: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

    finally:
        if conn:
            _put_connection(conn)
