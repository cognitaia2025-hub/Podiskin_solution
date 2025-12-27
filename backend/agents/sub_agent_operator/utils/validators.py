"""
Validadores - Validación de Datos
==================================

Funciones para validar datos de citas y pacientes.
"""

import logging
import re
from typing import Dict, Any, List, Tuple
from datetime import datetime, time, date

from ..config import config
from ..utils.database import _get_connection, _put_connection

logger = logging.getLogger(__name__)


def validate_appointment_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida datos de una cita.

    Args:
        data: Diccionario con datos de la cita

    Returns:
        Tupla (es_valido, lista_de_errores)
    """
    errors = []

    # Validar campos requeridos
    required_fields = ["paciente_id", "fecha", "hora", "tratamiento"]
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Campo requerido faltante: {field}")

    # Validar formato de fecha
    if data.get("fecha"):
        try:
            fecha = datetime.fromisoformat(data["fecha"]).date()
            # No permitir fechas pasadas
            if fecha < date.today():
                errors.append("No se pueden agendar citas en fechas pasadas")
        except ValueError:
            errors.append("Formato de fecha inválido (usar YYYY-MM-DD)")

    # Validar formato de hora
    if data.get("hora"):
        try:
            time.fromisoformat(data["hora"])
        except ValueError:
            errors.append("Formato de hora inválido (usar HH:MM)")

    # Validar duración
    if data.get("duracion"):
        duracion = data["duracion"]
        if not isinstance(duracion, int) or duracion < 15 or duracion > 120:
            errors.append("Duración debe ser entre 15 y 120 minutos")

    return len(errors) == 0, errors


def validate_patient_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida datos de un paciente.

    Args:
        data: Diccionario con datos del paciente

    Returns:
        Tupla (es_valido, lista_de_errores)
    """
    errors = []

    # Validar campos requeridos
    if not data.get("nombre"):
        errors.append("Nombre es requerido")

    if not data.get("telefono"):
        errors.append("Teléfono es requerido")

    # Validar formato de teléfono
    if data.get("telefono"):
        telefono = data["telefono"]
        # Permitir formatos: 123-456-7890, (123) 456-7890, 1234567890
        if not re.match(r"^[\d\-\(\)\s]+$", telefono):
            errors.append("Formato de teléfono inválido")

        # Verificar longitud mínima
        digits = re.sub(r"\D", "", telefono)
        if len(digits) < 10:
            errors.append("Teléfono debe tener al menos 10 dígitos")

    # Validar formato de email
    if data.get("email"):
        email = data["email"]
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            errors.append("Formato de email inválido")

    # Validar fecha de nacimiento
    if data.get("fecha_nacimiento"):
        try:
            fecha_nac = datetime.fromisoformat(data["fecha_nacimiento"]).date()
            if fecha_nac > date.today():
                errors.append("Fecha de nacimiento no puede ser futura")
        except ValueError:
            errors.append("Formato de fecha de nacimiento inválido")

    return len(errors) == 0, errors


def check_business_hours(fecha: str, hora: str) -> Tuple[bool, str]:
    """
    Verifica si una fecha/hora está dentro del horario de atención.

    Args:
        fecha: Fecha en formato YYYY-MM-DD
        hora: Hora en formato HH:MM

    Returns:
        Tupla (es_valido, mensaje_error)
    """
    try:
        fecha_obj = datetime.fromisoformat(fecha).date()
        hora_obj = time.fromisoformat(hora)

        # Obtener día de la semana
        day_name = fecha_obj.strftime("%A").lower()

        # Mapear días en inglés a español
        day_map = {
            "monday": "monday",
            "tuesday": "tuesday",
            "wednesday": "wednesday",
            "thursday": "thursday",
            "friday": "friday",
            "saturday": "saturday",
            "sunday": "sunday",
        }

        day_key = day_map.get(day_name)

        # Verificar si está cerrado
        if day_key in config.closed_days:
            return False, f"La clínica está cerrada los {day_key}"

        # Verificar horario
        if day_key in config.weekday_hours:
            hours = config.weekday_hours[day_key]
            start = time.fromisoformat(hours["start"])
            end = time.fromisoformat(hours["end"])

            if not (start <= hora_obj <= end):
                return (
                    False,
                    f"Fuera de horario de atención ({hours['start']} - {hours['end']})",
                )

        return True, ""

    except Exception as e:
        logger.error(f"Error checking business hours: {e}", exc_info=True)
        return False, "Error al validar horario"


def detect_duplicate_patient(telefono: str, nombre: str) -> Dict[str, Any]:
    """
    Detecta si ya existe un paciente con el mismo teléfono o nombre.

    Args:
        telefono: Teléfono del paciente
        nombre: Nombre del paciente

    Returns:
        Diccionario con resultado de la búsqueda
    """
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        # Buscar por teléfono exacto
        cursor.execute(
            "SELECT id, nombre, telefono FROM pacientes WHERE telefono = %s",
            (telefono,),
        )
        by_phone = cursor.fetchone()

        # Buscar por nombre similar
        cursor.execute(
            "SELECT id, nombre, telefono FROM pacientes WHERE nombre ILIKE %s",
            (f"%{nombre}%",),
        )
        by_name = cursor.fetchall()

        cursor.close()

        result = {
            "has_duplicates": bool(by_phone or by_name),
            "by_phone": None,
            "by_name": [],
        }

        if by_phone:
            result["by_phone"] = {
                "id": by_phone[0],
                "nombre": by_phone[1],
                "telefono": by_phone[2],
            }

        if by_name:
            result["by_name"] = [
                {"id": row[0], "nombre": row[1], "telefono": row[2]} for row in by_name
            ]

        return result

    except Exception as e:
        logger.error(f"Error detecting duplicates: {e}", exc_info=True)
        return {"has_duplicates": False, "error": str(e)}

    finally:
        if conn:
            _put_connection(conn)
