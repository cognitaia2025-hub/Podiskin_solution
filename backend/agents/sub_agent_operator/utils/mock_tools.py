"""
Mock Tools - Versiones Mock de Tools para Modo Demo
===================================================

Versiones de los tools que usan datos en memoria en lugar de BD.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import date

from .mock_data import MOCK_PATIENTS, MOCK_APPOINTMENTS, MOCK_STATS

logger = logging.getLogger(__name__)


def search_appointments_mock(
    filters: Optional[Dict[str, Any]] = None, sort_by: str = "fecha", limit: int = 50
) -> List[Dict[str, Any]]:
    """Versión mock de search_appointments."""
    results = MOCK_APPOINTMENTS.copy()

    # Aplicar filtros
    if filters:
        if filters.get("fecha"):
            results = [a for a in results if a["fecha"] == filters["fecha"]]

        if filters.get("paciente_id"):
            results = [a for a in results if a["paciente_id"] == filters["paciente_id"]]

        if filters.get("estado"):
            results = [a for a in results if a["estado"] == filters["estado"]]

        if filters.get("tratamiento"):
            results = [
                a
                for a in results
                if filters["tratamiento"].lower() in a["tratamiento"].lower()
            ]

    # Ordenar
    if sort_by == "fecha":
        results.sort(key=lambda x: (x["fecha"], x["hora"]))
    elif sort_by == "hora":
        results.sort(key=lambda x: x["hora"])

    # Limitar
    return results[:limit]


def get_appointment_by_id_mock(appointment_id: int) -> Optional[Dict[str, Any]]:
    """Versión mock de get_appointment_by_id."""
    for apt in MOCK_APPOINTMENTS:
        if apt["id"] == appointment_id:
            return apt.copy()
    return None


def check_availability_mock(fecha: str, hora: str, duracion: int = 30) -> bool:
    """Versión mock de check_availability."""
    # Simplificado: siempre disponible para demo
    return True


def search_patients_mock(
    query: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Versión mock de search_patients."""
    results = MOCK_PATIENTS.copy()

    # Buscar por texto
    if query:
        results = [
            p
            for p in results
            if query.lower() in p["nombre"].lower() or query in p["telefono"]
        ]

    return results[:limit]


def get_patient_by_id_mock(patient_id: int) -> Optional[Dict[str, Any]]:
    """Versión mock de get_patient_by_id."""
    for patient in MOCK_PATIENTS:
        if patient["id"] == patient_id:
            return patient.copy()
    return None


def get_patient_history_mock(patient_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Versión mock de get_patient_history."""
    history = [apt for apt in MOCK_APPOINTMENTS if apt["paciente_id"] == patient_id]
    history.sort(key=lambda x: (x["fecha"], x["hora"]), reverse=True)
    return history[:limit]


def create_appointment_mock(data: Dict[str, Any]) -> Dict[str, Any]:
    """Versión mock de create_appointment."""
    logger.info(f"[MOCK] Creating appointment: {data}")
    return {
        "success": True,
        "appointment_id": 999,
        "message": "[MODO DEMO] Cita creada (no guardada en BD real)",
    }


def update_appointment_mock(
    appointment_id: int, updates: Dict[str, Any]
) -> Dict[str, Any]:
    """Versión mock de update_appointment."""
    logger.info(f"[MOCK] Updating appointment {appointment_id}: {updates}")
    return {
        "success": True,
        "appointment_id": appointment_id,
        "message": "[MODO DEMO] Cita actualizada (no guardada en BD real)",
    }


def cancel_appointment_mock(
    appointment_id: int, reason: Optional[str] = None
) -> Dict[str, Any]:
    """Versión mock de cancel_appointment."""
    logger.info(f"[MOCK] Cancelling appointment {appointment_id}: {reason}")
    return {
        "success": True,
        "appointment_id": appointment_id,
        "message": "[MODO DEMO] Cita cancelada (no guardada en BD real)",
    }


def create_patient_mock(data: Dict[str, Any]) -> Dict[str, Any]:
    """Versión mock de create_patient."""
    logger.info(f"[MOCK] Creating patient: {data}")
    return {
        "success": True,
        "patient_id": 999,
        "message": "[MODO DEMO] Paciente creado (no guardado en BD real)",
    }


def update_patient_mock(patient_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Versión mock de update_patient."""
    logger.info(f"[MOCK] Updating patient {patient_id}: {updates}")
    return {
        "success": True,
        "patient_id": patient_id,
        "message": "[MODO DEMO] Paciente actualizado (no guardado en BD real)",
    }


def generate_appointment_stats_mock(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Versión mock de generate_appointment_stats."""
    return {
        "success": True,
        "period": {
            "start": start_date or "2024-12-13",
            "end": end_date or "2024-12-19",
        },
        "total": MOCK_STATS["total_appointments_this_week"],
        "by_status": {
            "completada": MOCK_STATS["completed_appointments"],
            "cancelada": MOCK_STATS["cancelled_appointments"],
            "pendiente": MOCK_STATS["pending_appointments"],
        },
        "by_treatment": {
            "Pedicure": 2,
            "Onicomicosis": 1,
            "Uñas encarnadas": 1,
            "Tratamiento de callos": 1,
        },
    }


def generate_patient_stats_mock() -> Dict[str, Any]:
    """Versión mock de generate_patient_stats."""
    return {
        "success": True,
        "total": MOCK_STATS["total_patients"],
        "new_last_month": MOCK_STATS["new_patients_last_month"],
    }
