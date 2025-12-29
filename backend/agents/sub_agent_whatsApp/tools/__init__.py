"""
Tools Package - Sub-Agente WhatsApp
====================================

Herramientas LangChain para el sub-agente de WhatsApp.
"""

from .patient_tools import (
    search_patient,
    get_patient_info,
    register_patient,
    create_patient,
    get_patient_history,
)

from .appointment_tools import (
    get_available_slots,
    book_appointment,
    cancel_appointment,
    get_upcoming_appointments,
    reschedule_appointment,
)

from .query_tools import (
    get_business_hours,
    get_location_info,
    get_treatments_from_db,
    search_treatment,
    get_treatment_info,
    get_clinic_info,
    get_prices,
    search_faq,
)

from .escalation_tools import (
    escalate_question_to_admin,
    get_admin_reply,
    save_faq_to_knowledge_base,
)

from .knowledge_tools import (
    search_knowledge_base,
)

from .rag_tools import (
    retrieve_context,
    index_conversation,
    search_similar_conversations,
)

__all__ = [
    # Patient tools
    "search_patient",
    "get_patient_info",
    "register_patient",
    "create_patient",
    "get_patient_history",
    # Appointment tools
    "get_available_slots",
    "book_appointment",
    "cancel_appointment",
    "get_upcoming_appointments",
    "reschedule_appointment",
    # Query tools
    "get_business_hours",
    "get_location_info",
    "get_treatments_from_db",
    "search_treatment",
    "get_treatment_info",
    "get_clinic_info",
    "get_prices",
    "search_faq",
    # Escalation tools
    "escalate_question_to_admin",
    "get_admin_reply",
    "save_faq_to_knowledge_base",
    # Knowledge base tools
    "search_knowledge_base",
    # RAG tools
    "retrieve_context",
    "index_conversation",
    "search_similar_conversations",
]
