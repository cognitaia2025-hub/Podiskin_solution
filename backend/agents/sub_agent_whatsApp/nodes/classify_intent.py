"""
Nodo: Clasificar Intención
===========================

Clasifica la intención del último mensaje del usuario usando el LLM.
"""

import os
import json
import logging
from typing import Dict
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

from ..state import WhatsAppAgentState
from ..config import config, SYSTEM_PROMPT_CLASSIFIER
from ..utils import (
    analyze_sentiment,
    should_escalate_by_sentiment,
    get_metrics_collector,
    timed_node,
)

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)
metrics = get_metrics_collector()

# LLM para clasificación (temperatura baja para ser más determinista)
classifier_llm = ChatAnthropic(
    model=config.llm_model,
    temperature=config.classifier_temperature,
    max_tokens=config.classifier_max_tokens,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)


async def classify_intent_node(state: WhatsAppAgentState) -> Dict:
    """
    Clasifica la intención del último mensaje del usuario.

    Args:
        state: Estado actual del agente

    Returns:
        Estado actualizado con intent, confidence y entities
    """
    logger.info(f"[{state['conversation_id']}] Clasificando intención...")

    try:
        # Obtener último mensaje del usuario
        last_msg = state["messages"][-1]
        last_message = (
            last_msg.content
            if hasattr(last_msg, "content")
            else last_msg.get("content", "")
        )

        # Construir prompt
        prompt = f"""{SYSTEM_PROMPT_CLASSIFIER}

Mensaje del usuario: "{last_message}"

Responde SOLO con un objeto JSON válido en este formato:
{{
  "intent": "nombre_de_la_intencion",
  "confidence": 0.95,
  "entities": {{
    "fecha": "2025-12-21",
    "hora": "14:00",
    "nombre": "Juan"
  }}
}}

Las entidades son opcionales. Solo inclúyelas si están claramente mencionadas en el mensaje.
"""

        # Invocar LLM
        response = await classifier_llm.ainvoke(prompt)

        # Parsear respuesta JSON
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            # Si falla el parsing, intentar extraer JSON del texto
            content = response.content
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end != 0:
                result = json.loads(content[start:end])
            else:
                raise ValueError("No se pudo parsear la respuesta del LLM")

        intent = result.get("intent", "otro")
        confidence = result.get("confidence", 0.0)
        entities = result.get("entities", {})

        logger.info(
            f"[{state['conversation_id']}] Intención clasificada: "
            f"{intent} (confianza: {confidence:.2f})"
        )

        # Validar que la intención sea válida
        if intent not in config.intent_classes:
            logger.warning(
                f"[{state['conversation_id']}] Intención inválida: {intent}. "
                f"Usando 'otro'"
            )
            intent = "otro"
            confidence = 0.5

        # Registrar métricas
        metrics.record_intent(intent)

        # Analizar sentimiento del mensaje
        sentiment_result = analyze_sentiment(last_message)

        # Verificar si debe escalar por sentimiento
        should_escalate, escalate_reason = should_escalate_by_sentiment(
            sentiment_result
        )

        return {
            **state,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "sentiment": sentiment_result,
            "processing_stage": "retrieve",
            "requires_human": should_escalate,
            "escalation_reason": escalate_reason if should_escalate else None,
        }

    except Exception as e:
        logger.error(
            f"[{state['conversation_id']}] Error clasificando intención: {str(e)}",
            exc_info=True,
        )

        # En caso de error, usar valores por defecto
        return {
            **state,
            "intent": "otro",
            "confidence": 0.0,
            "entities": {},
            "processing_stage": "retrieve",
            "error": f"Error en clasificación: {str(e)}",
        }


def extract_entities_fallback(message: str) -> Dict:
    """
    Extracción de entidades básica como fallback.

    Args:
        message: Mensaje del usuario

    Returns:
        Diccionario con entidades extraídas
    """
    import re
    from datetime import datetime, timedelta

    entities = {}

    # Detectar fechas relativas
    message_lower = message.lower()

    if "mañana" in message_lower:
        tomorrow = datetime.now() + timedelta(days=1)
        entities["fecha"] = tomorrow.strftime("%Y-%m-%d")
    elif "hoy" in message_lower:
        entities["fecha"] = datetime.now().strftime("%Y-%m-%d")
    elif "pasado mañana" in message_lower:
        day_after = datetime.now() + timedelta(days=2)
        entities["fecha"] = day_after.strftime("%Y-%m-%d")

    # Detectar horas (formato 14:00, 2pm, 2:00pm, etc.)
    time_patterns = [
        r"(\d{1,2}):(\d{2})\s*(am|pm)?",
        r"(\d{1,2})\s*(am|pm)",
    ]

    for pattern in time_patterns:
        match = re.search(pattern, message_lower)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if len(match.groups()) > 1 else 0

            # Convertir a formato 24h si es PM
            if len(match.groups()) > 2 and match.group(3) == "pm" and hour < 12:
                hour += 12

            entities["hora"] = f"{hour:02d}:{minute:02d}"
            break

    return entities
