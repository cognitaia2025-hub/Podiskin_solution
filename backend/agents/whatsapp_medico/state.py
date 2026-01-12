"""
State Management para Agente WhatsApp
=====================================

Define el estado que viaja entre nodos del grafo.
"""

from typing import TypedDict, Annotated, Literal
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
        paciente_id: ID del paciente en la BD (None si es nuevo)
        sentimiento: Análisis de sentimiento del último mensaje
        rag_docs: Documentos recuperados del RAG (se acumulan)
        respuesta_generada: Respuesta generada por el LLM
        debe_escalar: Flag para indicar si necesita intervención humana
        respuesta_humana: Respuesta proporcionada por el humano (para auto-aprendizaje)
    """

    messages: Annotated[list[dict], operator.add]
    chat_id: str
    paciente_id: int | None
    sentimiento: Sentimiento | None
    rag_docs: Annotated[list[RagDoc], operator.add]
    respuesta_generada: str | None
    debe_escalar: bool
    respuesta_humana: str | None
