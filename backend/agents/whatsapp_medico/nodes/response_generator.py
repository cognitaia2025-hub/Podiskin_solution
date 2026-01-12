"""
Nodo: Response Generator
========================

Genera respuestas usando el LLM con contexto RAG.
"""

import logging
from ..state import AgentState
from ..config import llm

logger = logging.getLogger(__name__)


async def response_generator(state: AgentState) -> dict:
    """
    Genera respuesta usando LLM con contexto RAG.

    Args:
        state: Estado actual del agente

    Returns:
        Dict con la respuesta generada
    """
    logger.info("Generando respuesta con LLM")

    try:
        # Construir contexto
        sentimiento = state.get("sentimiento")
        rag_docs = state.get("rag_docs", [])
        paciente_id = state.get("paciente_id")
        historial = state["messages"][-3:]  # Últimos 3 mensajes

        # Preparar contexto RAG
        rag_context = ""
        if rag_docs:
            rag_context = "\n".join(
                [
                    f"- {doc.respuesta_sugerida} (confianza: {doc.score:.0%})"
                    for doc in rag_docs[:2]  # Top 2
                ]
            )

        # Construir prompt
        prompt = f"""Eres un asistente médico virtual de una clínica de podología.

CONTEXTO DEL PACIENTE:
- ID Paciente: {paciente_id or "Nuevo paciente"}
- Sentimiento: {sentimiento.sentimiento if sentimiento else "neutral"}
- Intención: {sentimiento.intencion if sentimiento else "consulta"}

HISTORIAL RECIENTE:
{_format_messages(historial)}

CONOCIMIENTO DISPONIBLE:
{rag_context if rag_context else "No hay información específica disponible"}

INSTRUCCIONES:
1. Responde de forma empática y profesional
2. Usa tono médico pero accesible
3. Máximo 100 palabras
4. Si no tienes información suficiente, di: "Déjame consultar con un especialista"
5. NO inventes información médica
6. Adapta el tono al sentimiento del paciente

MENSAJE DEL PACIENTE:
{state["messages"][-1]["content"]}

RESPUESTA:"""

        # Generar respuesta
        response = await llm.ainvoke(prompt)
        respuesta_generada = response.content.strip()

        logger.info(f"Respuesta generada: {respuesta_generada[:50]}...")

        return {"respuesta_generada": respuesta_generada}

    except Exception as e:
        logger.error(f"Error generando respuesta: {e}", exc_info=True)
        return {
            "respuesta_generada": (
                "Disculpa, estoy teniendo problemas técnicos. "
                "Un especialista te atenderá pronto."
            ),
            "debe_escalar": True,
        }


def _format_messages(messages: list) -> str:
    """Formatea mensajes para el prompt"""
    formatted = []
    for msg in messages:
        role = "Paciente" if msg["role"] == "user" else "Asistente"
        formatted.append(f"{role}: {msg['content']}")
    return "\n".join(formatted)
