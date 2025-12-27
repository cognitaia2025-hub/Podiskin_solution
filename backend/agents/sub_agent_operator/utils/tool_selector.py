"""
Tool Selector - Selecciona entre tools reales o mock
====================================================

Detecta si está en modo demo y usa los tools apropiados.
"""

import os

# Detectar modo demo
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

if DEMO_MODE:
    # Importar versiones mock
    from .mock_tools import (
        search_appointments_mock as search_appointments,
        get_appointment_by_id_mock as get_appointment_by_id,
        check_availability_mock as check_availability,
        search_patients_mock as search_patients,
        get_patient_by_id_mock as get_patient_by_id,
        get_patient_history_mock as get_patient_history,
        create_appointment_mock as create_appointment,
        update_appointment_mock as update_appointment,
        cancel_appointment_mock as cancel_appointment,
        create_patient_mock as create_patient,
        update_patient_mock as update_patient,
        generate_appointment_stats_mock as generate_appointment_stats,
        generate_patient_stats_mock as generate_patient_stats,
    )
else:
    # Importar versiones reales
    from ..tools.appointment_tools import (
        search_appointments,
        get_appointment_by_id,
        check_availability,
    )
    from ..tools.patient_tools import (
        search_patients,
        get_patient_by_id,
        get_patient_history,
    )
    from ..tools.action_tools import (
        create_appointment,
        update_appointment,
        cancel_appointment,
    )
    from ..tools.patient_action_tools import (
        create_patient,
        update_patient,
    )
    from ..tools.report_tools import (
        generate_appointment_stats,
        generate_patient_stats,
    )

# Exportar todos
__all__ = [
    "search_appointments",
    "get_appointment_by_id",
    "check_availability",
    "search_patients",
    "get_patient_by_id",
    "get_patient_history",
    "create_appointment",
    "update_appointment",
    "cancel_appointment",
    "create_patient",
    "update_patient",
    "generate_appointment_stats",
    "generate_patient_stats",
    "DEMO_MODE",
]
