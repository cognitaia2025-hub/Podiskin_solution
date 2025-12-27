"""
Nodo: Generar Respuesta
========================

Genera la respuesta final usando el LLM.
"""

import os
import logging
from typing import Dict
from datetime import datetime
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

from ..state import WhatsAppAgentState
from ..config import config, SYSTEM_PROMPT_MAIN, ESCALATION_MESSAGE
from ..utils import get_response_tone, get_metrics_collector

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)
metrics = get_metrics_collector()

# LLM para generación de respuestas
llm = ChatAnthropic(
    model=config.llm_model,
    temperature=config.llm_temperature,
    max_tokens=config.llm_max_tokens,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)


async def generate_response_node(state: WhatsAppAgentState) -> Dict:
    """
    Genera la respuesta final usando el LLM.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con la respuesta generada
    """
    conversation_id = state["conversation_id"]
    next_action = state.get("next_action", "")

    logger.info(f"[{conversation_id}] Generating response...")

    try:
        # ====================================================================
        # 1. MENSAJES ESPECIALES (SIN LLM)
        # ====================================================================

        # Si es escalamiento, usar mensaje predefinido
        if next_action == "send_escalation_message":
            response_content = ESCALATION_MESSAGE

            logger.info(f"[{conversation_id}] Using escalation message")

            new_messages = state["messages"] + [
                {
                    "role": "assistant",
                    "content": response_content,
                    "timestamp": datetime.now().isoformat(),
                }
            ]

            return {**state, "messages": new_messages, "processing_stage": "complete"}

        # ====================================================================
        # 2. CONSTRUIR CONTEXTO
        # ====================================================================

        context_parts = []

        # Información del paciente
        if state.get("patient_info"):
            patient_info = state["patient_info"]
            context_parts.append(
                f"Paciente: {patient_info['nombre']}\n"
                f"Registrado desde: {patient_info.get('fecha_registro', 'N/A')}"
            )

        # Contexto de conversaciones previas
        if state.get("retrieved_context"):
            context_texts = [c["content"] for c in state["retrieved_context"][:3]]
            if context_texts:
                context_parts.append(
                    "Conversaciones previas relevantes:\n" + "\n".join(context_texts)
                )

        # Historial de citas
        if state.get("appointment_history"):
            appointments_text = "\n".join(
                [
                    f"- {a['fecha_hora']}: {a['tratamiento']} ({a['estado']})"
                    for a in state["appointment_history"][:3]
                ]
            )
            context_parts.append(f"Historial de citas:\n{appointments_text}")

        # Información de cita pendiente
        if state.get("pending_appointment"):
            apt = state["pending_appointment"]
            context_parts.append(
                f"Cita pendiente de confirmación:\n"
                f"Fecha: {apt.get('fecha')}\n"
                f"Hora: {apt.get('hora')}"
            )

        # Horarios sugeridos
        if state.get("suggested_slots"):
            slots_text = "\n".join(
                [f"- {s['fecha']} a las {s['hora']}" for s in state["suggested_slots"]]
            )
            context_parts.append(f"Horarios disponibles:\n{slots_text}")

        context = "\n\n".join(context_parts)

        # ====================================================================
        # 3. CONSTRUIR MENSAJES PARA LLM
        # ====================================================================

        messages = [{"role": "system", "content": SYSTEM_PROMPT_MAIN}]

        # Agregar contexto si existe
        if context:
            messages.append(
                {"role": "system", "content": f"Contexto adicional:\n{context}"}
            )

        # Agregar historial de conversación (últimos N mensajes)
        for msg in state["messages"][-config.max_context_messages :]:
            role = msg.type if hasattr(msg, "type") else msg.get("role", "user")
            content = msg.content if hasattr(msg, "content") else msg.get("content", "")
            # Convertir 'human' a 'user' para compatibilidad
            if role == "human":
                role = "user"
            elif role == "ai":
                role = "assistant"
            messages.append({"role": role, "content": content})

        # ====================================================================
        # 4. GENERAR RESPUESTA
        # ====================================================================

        logger.debug(f"[{conversation_id}] Invoking LLM...")

        # Agregar instrucción de tono basada en sentimiento
        sentiment = state.get("sentiment", {})
        if sentiment:
            tone_instruction = get_response_tone(sentiment.get("sentiment", "neutral"))
            messages.append(
                {
                    "role": "system",
                    "content": f"Instrucción de tono: {tone_instruction}",
                }
            )

        response = await llm.ainvoke(messages)
        response_content = response.content

        # Registrar éxito en métricas
        metrics.record_success()

        logger.info(
            f"[{conversation_id}] Response generated "
            f"({len(response_content)} chars)"
        )

        # ====================================================================
        # 5. AGREGAR RESPUESTA AL ESTADO
        # ====================================================================

        new_messages = state["messages"] + [
            {
                "role": "assistant",
                "content": response_content,
                "timestamp": datetime.now().isoformat(),
            }
        ]

        return {**state, "messages": new_messages, "processing_stage": "complete"}

    except Exception as e:
        logger.error(
            f"[{conversation_id}] Error generating response: {str(e)}", exc_info=True
        )

        # Respuesta de fallback
        fallback_message = (
            "Disculpa, estoy teniendo problemas técnicos en este momento. "
            "Un miembro de nuestro equipo te contactará pronto."
        )

        new_messages = state["messages"] + [
            {
                "role": "assistant",
                "content": fallback_message,
                "timestamp": datetime.now().isoformat(),
            }
        ]

        return {
            **state,
            "messages": new_messages,
            "processing_stage": "complete",
            "error": f"Error generando respuesta: {str(e)}",
            "requires_human": True,
        }
