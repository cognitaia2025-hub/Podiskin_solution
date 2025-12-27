"""
Sentiment Analysis - Sub-Agente WhatsApp
==========================================

Análisis de sentimiento para detectar urgencia, frustración o emergencias.
"""

import logging
import re
from typing import Dict, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class Sentiment(Enum):
    """Niveles de sentimiento detectados."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    URGENT = "urgent"
    EMERGENCY = "emergency"


# Palabras clave por categoría (español)
KEYWORDS = {
    "emergency": [
        "emergencia",
        "urgente",
        "ayuda",
        "auxilio",
        "dolor intenso",
        "sangre",
        "sangrado",
        "no puedo caminar",
        "mucho dolor",
        "accidente",
        "caí",
        "me caí",
        "fractura",
        "roto",
    ],
    "urgent": [
        "urgente",
        "rápido",
        "pronto",
        "necesito hoy",
        "lo antes posible",
        "cuanto antes",
        "no puede esperar",
        "asap",
        "inmediato",
    ],
    "negative": [
        "molesto",
        "enojado",
        "frustrado",
        "mal servicio",
        "queja",
        "tardaron",
        "esperé mucho",
        "no me contestaron",
        "decepcionado",
        "horrible",
        "pésimo",
        "nunca más",
        "cancelar todo",
    ],
    "positive": [
        "gracias",
        "excelente",
        "muy bien",
        "perfecto",
        "genial",
        "encantado",
        "feliz",
        "satisfecho",
        "recomiendo",
        "buenísimo",
        "maravilloso",
        "increíble",
        "muchas gracias",
    ],
}

# Emojis que indican sentimiento
EMOJI_SENTIMENT = {
    "positive": ["😊", "😄", "🙏", "👍", "💯", "❤️", "🎉", "✨", "💪"],
    "negative": ["😠", "😡", "😤", "😢", "😭", "👎", "💔", "😞", "😒"],
    "urgent": ["🆘", "⚠️", "🚨", "❗", "‼️", "⏰", "🔴"],
}


def analyze_sentiment(text: str) -> Dict[str, any]:
    """
    Analiza el sentimiento de un mensaje.

    Args:
        text: Texto del mensaje

    Returns:
        Diccionario con sentimiento, score, y razón
    """
    if not text:
        return {
            "sentiment": Sentiment.NEUTRAL.value,
            "score": 0.5,
            "is_urgent": False,
            "is_emergency": False,
            "reason": "Mensaje vacío",
        }

    text_lower = text.lower()
    scores = {
        "positive": 0,
        "negative": 0,
        "urgent": 0,
        "emergency": 0,
    }

    reasons = []

    # Analizar palabras clave
    for category, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                scores[category] += 1
                if scores[category] == 1:  # Solo primera vez
                    reasons.append(f"Palabra: '{keyword}'")

    # Analizar emojis
    for category, emojis in EMOJI_SENTIMENT.items():
        for emoji in emojis:
            if emoji in text:
                scores[category] += 0.5
                reasons.append(f"Emoji: {emoji}")

    # Detectar mayúsculas excesivas (indica frustración/urgencia)
    uppercase_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    if uppercase_ratio > 0.5 and len(text) > 10:
        scores["urgent"] += 0.5
        scores["negative"] += 0.3
        reasons.append("Uso excesivo de mayúsculas")

    # Detectar signos de exclamación múltiples
    if "!!!" in text or "?!?" in text:
        scores["urgent"] += 0.3
        reasons.append("Puntuación enfática")

    # Determinar sentimiento principal
    if scores["emergency"] >= 1:
        sentiment = Sentiment.EMERGENCY
        is_emergency = True
        is_urgent = True
    elif scores["urgent"] >= 1:
        sentiment = Sentiment.URGENT
        is_emergency = False
        is_urgent = True
    elif scores["negative"] > scores["positive"]:
        sentiment = Sentiment.NEGATIVE
        is_emergency = False
        is_urgent = scores["urgent"] > 0
    elif scores["positive"] > scores["negative"]:
        sentiment = Sentiment.POSITIVE
        is_emergency = False
        is_urgent = False
    else:
        sentiment = Sentiment.NEUTRAL
        is_emergency = False
        is_urgent = False

    # Calcular score normalizado
    total_score = sum(scores.values())
    if total_score > 0:
        sentiment_score = (scores["positive"] - scores["negative"]) / total_score
        sentiment_score = (sentiment_score + 1) / 2  # Normalizar a 0-1
    else:
        sentiment_score = 0.5

    logger.debug(
        f"Sentiment analysis: {sentiment.value} "
        f"(score: {sentiment_score:.2f}, urgent: {is_urgent})"
    )

    return {
        "sentiment": sentiment.value,
        "score": round(sentiment_score, 2),
        "is_urgent": is_urgent,
        "is_emergency": is_emergency,
        "scores": scores,
        "reason": "; ".join(reasons) if reasons else "Análisis automático",
    }


def should_escalate_by_sentiment(analysis: Dict) -> Tuple[bool, str]:
    """
    Determina si debe escalar a humano basado en el sentimiento.

    Args:
        analysis: Resultado de analyze_sentiment

    Returns:
        Tupla (should_escalate, reason)
    """
    if analysis["is_emergency"]:
        return True, "Emergencia detectada"

    if analysis["is_urgent"] and analysis["sentiment"] == "negative":
        return True, "Cliente urgente y frustrado"

    if analysis["scores"].get("negative", 0) >= 2:
        return True, "Cliente muy insatisfecho"

    return False, ""


def get_response_tone(sentiment: str) -> str:
    """
    Sugiere el tono de respuesta basado en el sentimiento.

    Args:
        sentiment: Sentimiento detectado

    Returns:
        Sugerencia de tono para la respuesta
    """
    tones = {
        "positive": "Mantén el tono amigable y entusiasta.",
        "neutral": "Usa un tono profesional y servicial.",
        "negative": "Sé empático, discúlpate si es necesario, y ofrece soluciones.",
        "urgent": "Responde rápidamente, muestra comprensión de la urgencia.",
        "emergency": "Prioriza la seguridad, ofrece ayuda inmediata o contacto directo.",
    }
    return tones.get(sentiment, tones["neutral"])
