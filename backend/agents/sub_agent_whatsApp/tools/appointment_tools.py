"""
Appointment Tools - Sub-Agente WhatsApp
========================================

Herramientas para gestión de citas.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_core.tools import tool

from ..utils import fetch, fetchrow, execute

load_dotenv()
logger = logging.getLogger(__name__)

# Configuración de horarios (podría venir de config)
BUSINESS_HOURS = {
    "start": 9,  # 9 AM
    "end": 18,  # 6 PM
    "lunch_start": 13,
    "lunch_end": 14,
    "slot_duration": 30,  # minutos
}

WORKING_DAYS = [0, 1, 2, 3, 4, 5]  # Lunes a Sábado


@tool
async def get_available_slots(date: str, duration_minutes: int = 30) -> Dict[str, Any]:
    """
    Obtiene los horarios disponibles para una fecha específica.

    Args:
        date: Fecha en formato YYYY-MM-DD
        duration_minutes: Duración de la cita en minutos (default: 30)

    Returns:
        Diccionario con horarios disponibles
    """
    logger.info(f"Getting available slots for: {date}")

    try:
        # Parsear fecha
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return {"error": "Formato de fecha inválido. Use YYYY-MM-DD"}

        # Verificar que no sea fecha pasada
        if target_date < datetime.now().date():
            return {"error": "No se pueden agendar citas en fechas pasadas"}

        # Verificar día laboral
        if target_date.weekday() not in WORKING_DAYS:
            return {"available": False, "message": "No hay atención ese día (domingo)"}

        # Obtener citas existentes para ese día
        query = """
        SELECT fecha_hora, duracion_minutos
        FROM citas
        WHERE DATE(fecha_hora) = %s
          AND estado NOT IN ('Cancelada', 'No_asistio')
        ORDER BY fecha_hora
        """
        existing_appointments = await fetch(query, target_date)

        # Generar slots disponibles
        slots = []
        current_time = datetime.combine(
            target_date, datetime.min.time().replace(hour=BUSINESS_HOURS["start"])
        )
        end_time = datetime.combine(
            target_date, datetime.min.time().replace(hour=BUSINESS_HOURS["end"])
        )

        while current_time < end_time:
            # Saltar hora de comida
            if (
                BUSINESS_HOURS["lunch_start"]
                <= current_time.hour
                < BUSINESS_HOURS["lunch_end"]
            ):
                current_time = current_time.replace(
                    hour=BUSINESS_HOURS["lunch_end"], minute=0
                )
                continue

            # Verificar si el slot está ocupado
            slot_end = current_time + timedelta(minutes=duration_minutes)
            is_available = True

            for apt in existing_appointments:
                apt_start = apt["fecha_hora"]
                apt_end = apt_start + timedelta(minutes=apt.get("duracion_minutos", 30))

                # Verificar superposición
                if (current_time < apt_end) and (slot_end > apt_start):
                    is_available = False
                    break

            if is_available:
                slots.append(
                    {"hora": current_time.strftime("%H:%M"), "disponible": True}
                )

            current_time += timedelta(minutes=BUSINESS_HOURS["slot_duration"])

        return {"fecha": date, "slots_disponibles": len(slots), "horarios": slots}

    except Exception as e:
        logger.error(f"Error getting available slots: {e}")
        return {"error": str(e)}


@tool
async def book_appointment(
    patient_id: int,
    date: str,
    time: str,
    service_type: str = "Consulta General",
    duration_minutes: int = 30,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Agenda una nueva cita para un paciente.

    Args:
        patient_id: ID del paciente
        date: Fecha en formato YYYY-MM-DD
        time: Hora en formato HH:MM
        service_type: Tipo de servicio (default: Consulta General)
        duration_minutes: Duración en minutos (default: 30)
        notes: Notas adicionales

    Returns:
        Diccionario con información de la cita creada
    """
    logger.info(f"Booking appointment for patient {patient_id}")

    try:
        # Parsear fecha y hora
        try:
            appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            return {"success": False, "error": "Formato de fecha/hora inválido"}

        # Verificar que no sea pasado
        if appointment_datetime < datetime.now():
            return {
                "success": False,
                "error": "No se pueden agendar citas en el pasado",
            }

        # Verificar que el paciente existe
        patient = await fetchrow(
            "SELECT id, nombre_completo FROM pacientes WHERE id = %s", patient_id
        )

        if not patient:
            return {"success": False, "error": "Paciente no encontrado"}

        # Verificar disponibilidad
        conflict_query = """
        SELECT id FROM citas
        WHERE fecha_hora = %s
          AND estado NOT IN ('Cancelada', 'No_asistio')
        """
        conflict = await fetchrow(conflict_query, appointment_datetime)

        if conflict:
            return {
                "success": False,
                "error": "El horario seleccionado no está disponible",
            }

        # Crear cita
        insert_query = """
        INSERT INTO citas (
            id_paciente, fecha_hora, duracion_minutos,
            estado, tipo_servicio, notas, creada_por
        ) VALUES (%s, %s, %s, 'Programada', %s, %s, 'WhatsApp')
        RETURNING id
        """

        result = await fetchrow(
            insert_query,
            patient_id,
            appointment_datetime,
            duration_minutes,
            service_type,
            notes,
        )

        logger.info(f"Appointment booked: {result['id']}")

        return {
            "success": True,
            "appointment_id": result["id"],
            "message": (
                f"Cita agendada para {patient['nombre_completo']} "
                f"el {date} a las {time}"
            ),
            "detalles": {
                "paciente": patient["nombre_completo"],
                "fecha": date,
                "hora": time,
                "servicio": service_type,
                "duracion": f"{duration_minutes} minutos",
            },
        }

    except Exception as e:
        logger.error(f"Error booking appointment: {e}")
        return {"success": False, "error": str(e)}


@tool
async def cancel_appointment(
    appointment_id: int, reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Cancela una cita existente.

    Args:
        appointment_id: ID de la cita a cancelar
        reason: Motivo de la cancelación

    Returns:
        Diccionario con resultado de la cancelación
    """
    logger.info(f"Cancelling appointment: {appointment_id}")

    try:
        # Verificar que la cita existe y no está cancelada
        appointment = await fetchrow(
            """
            SELECT c.*, p.nombre_completo as paciente_nombre
            FROM citas c
            JOIN pacientes p ON c.id_paciente = p.id
            WHERE c.id = %s
            """,
            appointment_id,
        )

        if not appointment:
            return {"success": False, "error": "Cita no encontrada"}

        if appointment["estado"] == "Cancelada":
            return {"success": False, "error": "La cita ya está cancelada"}

        # Cancelar cita
        update_query = """
        UPDATE citas
        SET estado = 'Cancelada',
            notas = COALESCE(notas, '') || %s
        WHERE id = %s
        """

        cancel_note = f"\n[Cancelada via WhatsApp: {reason or 'Sin motivo'}]"
        await execute(update_query, cancel_note, appointment_id)

        logger.info(f"Appointment cancelled: {appointment_id}")

        return {
            "success": True,
            "message": (
                f"Cita de {appointment['paciente_nombre']} "
                f"del {appointment['fecha_hora'].strftime('%Y-%m-%d %H:%M')} "
                f"ha sido cancelada"
            ),
        }

    except Exception as e:
        logger.error(f"Error cancelling appointment: {e}")
        return {"success": False, "error": str(e)}


@tool
async def get_upcoming_appointments(patient_id: int) -> Dict[str, Any]:
    """
    Obtiene las próximas citas de un paciente.

    Args:
        patient_id: ID del paciente

    Returns:
        Diccionario con las próximas citas del paciente
    """
    logger.info(f"Getting upcoming appointments for patient: {patient_id}")

    try:
        query = """
        SELECT id, fecha_hora, estado, tipo_servicio, duracion_minutos
        FROM citas
        WHERE id_paciente = %s
          AND fecha_hora >= NOW()
          AND estado NOT IN ('Cancelada', 'No_asistio', 'Completada')
        ORDER BY fecha_hora
        LIMIT 5
        """

        appointments = await fetch(query, patient_id)

        if not appointments:
            return {"found": False, "message": "No tiene citas programadas"}

        return {
            "found": True,
            "cantidad": len(appointments),
            "citas": [
                {
                    "id": apt["id"],
                    "fecha": apt["fecha_hora"].strftime("%Y-%m-%d"),
                    "hora": apt["fecha_hora"].strftime("%H:%M"),
                    "servicio": apt["tipo_servicio"],
                    "duracion": f"{apt['duracion_minutos']} min",
                    "estado": apt["estado"],
                }
                for apt in appointments
            ],
        }

    except Exception as e:
        logger.error(f"Error getting upcoming appointments: {e}")
        return {"error": str(e)}
