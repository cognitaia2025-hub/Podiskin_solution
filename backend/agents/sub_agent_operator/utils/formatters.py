"""
Formatters - Formateo de Respuestas
====================================

Funciones para formatear datos en texto estructurado.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def format_appointment_list(appointments: List[Dict[str, Any]]) -> str:
    """
    Formatea una lista de citas en texto estructurado.

    Args:
        appointments: Lista de citas

    Returns:
        String formateado
    """
    if not appointments:
        return "No se encontraron citas."

    # Agrupar por fecha
    by_date = {}
    for apt in appointments:
        fecha = apt.get("fecha", "Sin fecha")
        if fecha not in by_date:
            by_date[fecha] = []
        by_date[fecha].append(apt)

    # Formatear
    lines = [f"Citas encontradas: {len(appointments)}\n"]

    for fecha in sorted(by_date.keys()):
        citas = by_date[fecha]
        lines.append(f"\n=== {fecha} ===")

        for cita in sorted(citas, key=lambda x: x.get("hora", "")):
            hora = cita.get("hora", "??:??")
            paciente = cita.get("paciente_nombre", "Desconocido")
            tratamiento = cita.get("tratamiento", "N/A")
            estado = cita.get("estado", "N/A")

            lines.append(f"  {hora} - {paciente} ({tratamiento}) [{estado}]")

    return "\n".join(lines)


def format_patient_info(patient: Dict[str, Any]) -> str:
    """
    Formatea información de un paciente.

    Args:
        patient: Diccionario con datos del paciente

    Returns:
        String formateado
    """
    lines = [
        "=== INFORMACION DEL PACIENTE ===",
        f"ID: {patient.get('id', 'N/A')}",
        f"Nombre: {patient.get('nombre', 'N/A')}",
        f"Telefono: {patient.get('telefono', 'N/A')}",
    ]

    if patient.get("email"):
        lines.append(f"Email: {patient['email']}")

    if patient.get("fecha_nacimiento"):
        lines.append(f"Fecha de nacimiento: {patient['fecha_nacimiento']}")

    if patient.get("direccion"):
        lines.append(f"Direccion: {patient['direccion']}")

    if patient.get("fecha_registro"):
        lines.append(f"Registrado: {patient['fecha_registro']}")

    if patient.get("notas"):
        lines.append(f"\nNotas: {patient['notas']}")

    return "\n".join(lines)


def format_confirmation(action_type: str, action_data: Dict[str, Any]) -> str:
    """
    Formatea un mensaje de confirmación.

    Args:
        action_type: Tipo de acción
        action_data: Datos de la acción

    Returns:
        String formateado
    """
    if action_type == "create_appointment":
        return f"""
=== CONFIRMAR AGENDAMIENTO ===

Paciente: {action_data.get('paciente_nombre', 'ID: ' + str(action_data.get('paciente_id')))}
Fecha: {action_data.get('fecha')}
Hora: {action_data.get('hora')}
Duracion: {action_data.get('duracion', 30)} minutos
Tratamiento: {action_data.get('tratamiento')}

Responde SI para confirmar o NO para cancelar.
"""

    elif action_type == "reschedule_appointment":
        original = action_data.get("original", {})
        updates = action_data.get("updates", {})

        return f"""
=== CONFIRMAR REAGENDAMIENTO ===

Cita original:
  Fecha: {original.get('fecha')}
  Hora: {original.get('hora')}
  Paciente: {original.get('paciente_nombre')}

Nuevos datos:
  Fecha: {updates.get('fecha', original.get('fecha'))}
  Hora: {updates.get('hora', original.get('hora'))}

Responde SI para confirmar o NO para cancelar.
"""

    elif action_type == "cancel_appointment":
        appointment = action_data.get("appointment", {})

        return f"""
=== CONFIRMAR CANCELACION ===

Fecha: {appointment.get('fecha')}
Hora: {appointment.get('hora')}
Paciente: {appointment.get('paciente_nombre')}
Tratamiento: {appointment.get('tratamiento')}

Responde SI para confirmar o NO para cancelar.
"""

    elif action_type == "update_patient":
        patient = action_data.get("patient", {})
        updates = action_data.get("updates", {})

        lines = [
            "=== CONFIRMAR ACTUALIZACION DE PACIENTE ===",
            f"\nPaciente: {patient.get('nombre')}",
            "\nCambios:",
        ]

        for field, value in updates.items():
            lines.append(f"  {field}: {value}")

        lines.append("\nResponde SI para confirmar o NO para cancelar.")

        return "\n".join(lines)

    return "Confirmacion requerida. Responde SI o NO."


def format_report(data: Dict[str, Any], report_type: str) -> str:
    """
    Formatea un reporte.

    Args:
        data: Datos del reporte
        report_type: Tipo de reporte

    Returns:
        String formateado
    """
    if report_type == "appointments":
        stats = data.get("data", {})
        period = stats.get("period", {})

        lines = [
            "=== REPORTE DE CITAS ===",
            f"\nPeriodo: {period.get('start')} a {period.get('end')}",
            f"\nTotal de citas: {stats.get('total', 0)}",
        ]

        # Por estado
        by_status = stats.get("by_status", {})
        if by_status:
            lines.append("\nPor estado:")
            for status, count in by_status.items():
                lines.append(f"  {status}: {count}")

        # Por tratamiento
        by_treatment = stats.get("by_treatment", {})
        if by_treatment:
            lines.append("\nTratamientos mas solicitados:")
            for treatment, count in list(by_treatment.items())[:5]:
                lines.append(f"  {treatment}: {count}")

        return "\n".join(lines)

    elif report_type == "patients":
        stats = data.get("data", {})

        return f"""
=== REPORTE DE PACIENTES ===

Total de pacientes: {stats.get('total', 0)}
Nuevos (ultimo mes): {stats.get('new_last_month', 0)}
"""

    elif report_type == "general":
        apt_stats = data.get("appointments", {}).get("data", {})
        pat_stats = data.get("patients", {}).get("data", {})

        return f"""
=== REPORTE GENERAL ===

CITAS:
  Total: {apt_stats.get('total', 0)}
  Por estado: {apt_stats.get('by_status', {})}

PACIENTES:
  Total: {pat_stats.get('total', 0)}
  Nuevos (ultimo mes): {pat_stats.get('new_last_month', 0)}
"""

    return "Reporte no disponible"
