"""
Nodo: Generar Respuesta
=======================

Genera la respuesta final para el usuario en formato texto plano estructurado.
"""

import os
import logging
from typing import Dict
from datetime import datetime
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

from ..state import OperationsAgentState
from ..config import config, SYSTEM_PROMPT_MAIN

load_dotenv()

logger = logging.getLogger(__name__)

# LLM para generación de respuestas
llm = ChatAnthropic(
    model=config.llm_model,
    temperature=config.llm_temperature,
    max_tokens=config.llm_max_tokens,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)


async def generate_response_node(state: OperationsAgentState) -> Dict:
    """
    Genera la respuesta final usando el LLM.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con la respuesta generada
    """
    session_id = state.get("session_id", "unknown")

    logger.info(f"[{session_id}] Generando respuesta...")

    try:
        # ====================================================================
        # 1. CONSTRUIR CONTEXTO
        # ====================================================================

        context_parts = []

        # Datos recuperados
        if state.get("retrieved_data"):
            retrieved = state["retrieved_data"]
            context_parts.append(f"Datos encontrados:\n{retrieved}")

        # Resultado de acción
        if state.get("action_result"):
            result = state["action_result"]
            context_parts.append(f"Resultado de acción:\n{result}")

        # Contexto adicional
        if state.get("context"):
            context_parts.append(state["context"])

        context = "\n\n".join(context_parts) if context_parts else ""

        # ====================================================================
        # 2. CONSTRUIR MENSAJES
        # ====================================================================

        messages = [{"role": "system", "content": SYSTEM_PROMPT_MAIN}]

        # Agregar contexto si existe
        if context:
            messages.append({"role": "system", "content": f"Contexto:\n{context}"})

        # Agregar historial de conversación (últimos 10 mensajes)
        for msg in state.get("messages", [])[-config.max_context_messages :]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            messages.append({"role": role, "content": content})

        # Agregar mensaje actual
        current_message = state.get("current_message", "")
        messages.append({"role": "user", "content": current_message})

        # ====================================================================
        # 3. GENERAR RESPUESTA
        # ====================================================================

        logger.debug(f"[{session_id}] Invocando LLM...")

        response = await llm.ainvoke(messages)
        response_content = response.content

        logger.info(
            f"[{session_id}] Respuesta generada ({len(response_content)} chars)"
        )

        # ====================================================================
        # 4. ACTUALIZAR ESTADO
        # ====================================================================

        # Agregar mensaje del asistente al historial
        new_messages = state.get("messages", []) + [
            {
                "role": "user",
                "content": current_message,
                "timestamp": state.get("timestamp", datetime.now().isoformat()),
            },
            {
                "role": "assistant",
                "content": response_content,
                "timestamp": datetime.now().isoformat(),
            },
        ]

        return {
            **state,
            "messages": new_messages,
            "response": response_content,
            "processing_stage": "complete",
        }

    except Exception as e:
        logger.error(f"[{session_id}] Error generando respuesta: {e}", exc_info=True)
        return {
            **state,
            "response": "Lo siento, ocurrió un error al generar la respuesta.",
            "error": str(e),
            "processing_stage": "error",
        }
