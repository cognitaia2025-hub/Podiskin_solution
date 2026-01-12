"""
State Management para Agente WhatsApp
=====================================

Define el estado que viaja entre nodos del grafo.

Actualizado para Twilio + LangGraph v1+ con:
- Thread-scoped memory por contact_id
- Confidence-based routing
- Behavior rules dinámicas
- Contexto recuperado con fuente
"""

from typing import TypedDict, Annotated, Literal, Optional
import operator
from pydantic import BaseModel


class Sentimiento(BaseModel):
    """Resultado del análisis de sentimiento"""

    sentimiento: Literal["positivo", "negativo", "urgente", "furioso"]
    intencion: Literal["queja", "consulta", "cita", "compra", "otro"]
    confianza: float


class RagDoc(BaseModel):
    """Documento recuperado del RAG"""

    id: int
    respuesta_sugerida: str
    score: float
    trigger_match: bool


class AgentState(TypedDict):
    """
    Estado del agente que viaja entre nodos.

    Attributes:
        messages: Historial de mensajes (se acumulan con operator.add)
        chat_id: ID único de la conversación de WhatsApp
        
        # Thread-scoped identifiers (NUEVO)
        contact_id: ID del contacto (usado como thread_id para aislamiento)
        conversation_id: ID de la conversación actual
        
        paciente_id: ID del paciente en la BD (None si es nuevo)
        
        # Mensaje actual (NUEVO)
        message: Mensaje actual a procesar
        
        sentimiento: Análisis de sentimiento del último mensaje
        rag_docs: Documentos recuperados del RAG (se acumulan)
        
        # Contexto recuperado con fuente (NUEVO)
        retrieved_context: Contexto recuperado de las tools
        fuente: Fuente del contexto (sql_estructurado, knowledge_base_validated, contexto_conversacional)
        confidence: Score de confianza (0.0-1.0)
        
        # Metadata estructurada (NUEVO)
        metadata: Dict con metadata adicional (tabla_consultada, kb_id, etc.)
        
        # Behavior rules (NUEVO)
        behavior_rules: Lista de reglas de comportamiento activas
        
        respuesta_generada: Respuesta generada por el LLM
        debe_escalar: Flag para indicar si necesita intervención humana
        escalation_reason: Razón del escalamiento (NUEVO)
        respuesta_humana: Respuesta proporcionada por el humano (para auto-aprendizaje)
        
        # Control de flujo (NUEVO)
        next_action: Próxima acción a tomar
    """

    messages: Annotated[list[dict], operator.add]
    chat_id: str
    
    # Thread-scoped identifiers
    contact_id: str
    conversation_id: str
    
    paciente_id: Optional[int]
    
    # Mensaje actual
    message: str
    
    sentimiento: Optional[Sentimiento]
    rag_docs: Annotated[list[RagDoc], operator.add]
    
    # Contexto recuperado con fuente
    retrieved_context: str
    fuente: str
    confidence: float
    
    # Metadata estructurada
    metadata: dict
    
    # Behavior rules
    behavior_rules: list[dict]
    
    respuesta_generada: Optional[str]
    debe_escalar: bool
    escalation_reason: Optional[str]
    respuesta_humana: Optional[str]
    
    # Control de flujo
    next_action: Optional[str]
