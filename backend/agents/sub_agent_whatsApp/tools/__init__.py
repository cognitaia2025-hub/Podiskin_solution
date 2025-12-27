"""
Tools Package - Sub-Agente WhatsApp
====================================

Herramientas LangChain para el sub-agente de WhatsApp.
"""

from .patient_tools import (
    search_patient,
    get_patient_info,
    register_patient,
)

from .appointment_tools import (
    get_available_slots,
    book_appointment,
    cancel_appointment,
    get_upcoming_appointments,
)

from .query_tools import (
    get_business_hours,
    get_location_info,
    get_treatments_from_db,
    search_treatment,
)

from .escalation_tools import (
    escalate_question_to_admin,
)

from .knowledge_tools import (
    search_knowledge_base,
)

__all__ = [
    # Patient tools
    "search_patient",
    "get_patient_info",
    "register_patient",
    # Appointment tools
    "get_available_slots",
    "book_appointment",
    "cancel_appointment",
    "get_upcoming_appointments",
    # Query tools
    "get_business_hours",
    "get_location_info",
    "get_treatments_from_db",
    "search_treatment",
    # Escalation tools
    "escalate_question_to_admin",
    # Knowledge base tools
    "search_knowledge_base",
]
