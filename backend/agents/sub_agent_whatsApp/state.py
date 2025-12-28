"""
Estado del Sub-Agente de WhatsApp
==================================

Define el estado completo que maneja el sub-agente de WhatsApp.
Este estado es independiente y contiene toda la información necesaria
para gestionar una conversación.
"""

from typing import TypedDict, List, Dict, Optional, Annotated
from datetime import datetime
from langgraph.graph.message import add_messages


class WhatsAppAgentState(TypedDict):
    """
    Estado completo del sub-agente de WhatsApp.

    Este estado se mantiene durante toda la conversación y se persiste
    usando checkpointers de LangGraph.
    """

    # ========================================================================
    # IDENTIFICACIÓN
    # ========================================================================
    conversation_id: str
    """ID único de la conversación en la base de datos"""

    contact_id: int
    """ID del contacto en la tabla contactos"""

    patient_id: Optional[int]
    """ID del paciente si existe, None si es prospecto"""

    whatsapp_number: str
    """Número de WhatsApp del contacto (formato: +52XXXXXXXXXX)"""

    contact_name: str
    """Nombre del contacto desde WhatsApp"""

    # ========================================================================
    # MENSAJES
    # ========================================================================
    messages: Annotated[List[Dict], add_messages]
    """
    Historial de mensajes de la conversación.
    Usa add_messages para acumular automáticamente.
    
    Formato:
    {
        "role": "user" | "assistant" | "system",
        "content": "texto del mensaje",
        "timestamp": "2025-12-19T10:30:00"
    }
    """

    # ========================================================================
    # CONTEXTO RAG
    # ========================================================================
    retrieved_context: List[Dict]
    """
    Contexto recuperado del vector store.
    
    Formato:
    {
        "content": "texto del contexto",
        "score": 0.95,
        "metadata": {
            "conversation_id": 123,
            "timestamp": "2025-12-19T10:00:00"
        }
    }
    """

    patient_info: Optional[Dict]
    """
    Información del paciente si existe.
    
    Formato:
    {
        "id": 1,
        "nombre": "Juan Pérez",
        "telefono": "3331234567",
        "email": "juan@email.com",
        "fecha_registro": "2025-01-15"
    }
    """

    appointment_history: List[Dict]
    """
    Historial de citas del paciente.
    
    Formato:
    {
        "id": 1,
        "fecha_hora": "2025-12-21 14:00:00",
        "tratamiento": "Consulta General",
        "estado": "Completada"
    }
    """

    # ========================================================================
    # CLASIFICACIÓN DE INTENCIÓN
    # ========================================================================
    intent: str
    """
    Intención clasificada del último mensaje.
    
    Valores posibles:
    - "agendar": Quiere agendar una cita
    - "consulta": Pregunta sobre tratamientos/precios
    - "cancelar": Quiere cancelar/reagendar
    - "info": Información general de la clínica
    - "emergencia": Situación urgente
    - "otro": Otro tipo de mensaje
    """

    confidence: float
    """Confianza de la clasificación (0.0 - 1.0)"""

    entities: Dict
    """
    Entidades extraídas del mensaje.
    
    Formato:
    {
        "fecha": "2025-12-21",
        "hora": "14:00",
        "nombre": "Juan",
        "tratamiento": "Consulta General"
    }
    """

    # ========================================================================
    # CONTROL DE FLUJO
    # ========================================================================
    next_action: str
    """
    Próxima acción a ejecutar.
    
    Valores posibles:
    - "register_patient": Registrar nuevo paciente
    - "request_datetime": Solicitar fecha y hora
    - "check_availability": Verificar disponibilidad
    - "confirm_appointment": Confirmar cita
    - "suggest_alternatives": Sugerir horarios alternativos
    - "provide_info": Proporcionar información
    - "escalate": Escalar a humano
    """

    requires_human: bool
    """Indica si requiere intervención humana"""

    escalation_reason: Optional[str]
    """Razón del escalamiento si requires_human=True"""

    escalation_ticket_id: Optional[int]
    """ID del ticket de escalamiento creado (para interrupt/resume)"""

    admin_reply: Optional[str]
    """Respuesta del administrador (cuando se reanuda el flujo)"""

    # ========================================================================
    # GESTIÓN DE CITAS
    # ========================================================================
    pending_appointment: Optional[Dict]
    """
    Cita pendiente de confirmación.
    
    Formato:
    {
        "fecha": "2025-12-21",
        "hora": "14:00",
        "tratamiento_id": 1,
        "podologo_id": 1,
        "disponible": True
    }
    """

    suggested_slots: List[Dict]
    """
    Horarios sugeridos si no hay disponibilidad.
    
    Formato:
    {
        "fecha": "2025-12-22",
        "hora": "10:00",
        "podologo": "Dr. Santiago"
    }
    """

    # ========================================================================
    # METADATA
    # ========================================================================
    timestamp: str
    """Timestamp del último mensaje (ISO format)"""

    language: str
    """Idioma de la conversación (default: "es")"""

    session_start: str
    """Timestamp de inicio de la sesión"""

    message_count: int
    """Número de mensajes en la conversación"""

    # ========================================================================
    # ESTADO DE PROCESAMIENTO
    # ========================================================================
    processing_stage: str
    """
    Etapa actual del procesamiento.
    
    Valores posibles:
    - "classify": Clasificando intención
    - "retrieve": Recuperando contexto
    - "check_patient": Verificando paciente
    - "handle_action": Ejecutando acción
    - "generate": Generando respuesta
    - "complete": Procesamiento completo
    """

    error: Optional[str]
    """Mensaje de error si ocurrió algún problema"""


# ========================================================================
# ESTADO INICIAL
# ========================================================================


def create_initial_state(
    conversation_id: str,
    contact_id: int,
    whatsapp_number: str,
    contact_name: str,
    message: str,
    patient_id: Optional[int] = None,
) -> WhatsAppAgentState:
    """
    Crea el estado inicial para una nueva conversación.

    Args:
        conversation_id: ID de la conversación en BD
        contact_id: ID del contacto
        whatsapp_number: Número de WhatsApp
        contact_name: Nombre del contacto
        message: Primer mensaje del usuario
        patient_id: ID del paciente si existe

    Returns:
        Estado inicial del agente
    """
    now = datetime.now().isoformat()

    return WhatsAppAgentState(
        # Identificación
        conversation_id=conversation_id,
        contact_id=contact_id,
        patient_id=patient_id,
        whatsapp_number=whatsapp_number,
        contact_name=contact_name,
        # Mensajes
        messages=[{"role": "user", "content": message, "timestamp": now}],
        # Contexto
        retrieved_context=[],
        patient_info=None,
        appointment_history=[],
        # Clasificación
        intent="",
        confidence=0.0,
        entities={},
        # Control de flujo
        next_action="",
        requires_human=False,
        escalation_reason=None,
        escalation_ticket_id=None,
        admin_reply=None,
        # Gestión de citas
        pending_appointment=None,
        suggested_slots=[],
        # Metadata
        timestamp=now,
        language="es",
        session_start=now,
        message_count=1,
        # Procesamiento
        processing_stage="classify",
        error=None,
    )
