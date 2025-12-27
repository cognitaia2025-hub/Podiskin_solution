"""
Nodo: Clasificar Intención
==========================

Clasifica la intención del mensaje del usuario usando Claude Haiku 3.
"""

import os
import logging
import json
from typing import Dict
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

from ..state import OperationsAgentState
from ..config import config, SYSTEM_PROMPT_CLASSIFIER

load_dotenv()

logger = logging.getLogger(__name__)

# LLM para clasificación
llm_classifier = ChatAnthropic(
    model=config.llm_model,
    temperature=0.1,  # Baja para clasificación determinista
    max_tokens=512,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)


async def classify_intent_node(state: OperationsAgentState) -> Dict:
    """
    Clasifica la intención del mensaje del usuario.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con intent, confidence y entities
    """
    session_id = state.get("session_id", "unknown")
    current_message = state.get("current_message", "")

    logger.info(f"[{session_id}] Clasificando intención...")

    try:
        # Construir prompt
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_CLASSIFIER},
            {"role": "user", "content": current_message},
        ]

        # Invocar LLM
        response = await llm_classifier.ainvoke(messages)
        response_text = response.content

        # Parsear JSON
        try:
            result = json.loads(response_text)
            intent = result.get("intent", "otro")
            confidence = result.get("confidence", 0.5)
            entities = result.get("entities", {})
        except json.JSONDecodeError:
            logger.warning(f"[{session_id}] No se pudo parsear JSON, usando defaults")
            intent = "otro"
            confidence = 0.5
            entities = {}

        logger.info(
            f"[{session_id}] Intención clasificada: {intent} "
            f"(confianza: {confidence:.2f})"
        )

        return {
            **state,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
        }

    except Exception as e:
        logger.error(f"[{session_id}] Error clasificando intención: {e}", exc_info=True)
        return {
            **state,
            "intent": "otro",
            "confidence": 0.0,
            "entities": {},
            "error": str(e),
        }
