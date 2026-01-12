"""
Nodo: Análisis de Sentimiento
==============================

Analiza el sentimiento e intención del mensaje del paciente.
Usa la tabla `analisis_sentimiento` existente.
"""

import logging
from ..state import AgentState, Sentimiento
from db import get_pool

logger = logging.getLogger(__name__)


async def sentiment_analyzer(state: AgentState) -> dict:
    """
    Analiza el sentimiento del último mensaje.

    Args:
        state: Estado actual del agente

    Returns:
        Dict con el sentimiento analizado
    """
    pool = get_pool()
    msg = state["messages"][-1]["content"]
    chat_id = state["chat_id"]

    logger.info(f"Analizando sentimiento para chat {chat_id}")

    try:
        # Buscar si ya existe análisis para este mensaje
        async with pool.acquire() as conn:
            # Buscar conversación por chat_id
            conv = await conn.fetchrow(
                "SELECT id FROM conversaciones WHERE chat_id = $1", chat_id
            )

            if not conv:
                # Crear conversación si no existe
                conv = await conn.fetchrow(
                    """
                    INSERT INTO conversaciones (chat_id, estado, fecha_creacion)
                    VALUES ($1, 'activa', CURRENT_TIMESTAMP)
                    RETURNING id
                    """,
                    chat_id,
                )

            # Analizar sentimiento con LLM (simplificado por ahora)
            # TODO: Integrar con modelo de análisis de sentimiento real
            sentimiento_detectado = await _analizar_con_llm(msg)

            # Guardar en BD
            await conn.execute(
                """
                INSERT INTO analisis_sentimiento 
                (id_conversacion, sentimiento, intencion, confianza, fecha_analisis)
                VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP)
                """,
                conv["id"],
                sentimiento_detectado.sentimiento,
                sentimiento_detectado.intencion,
                sentimiento_detectado.confianza,
            )

            logger.info(f"Sentimiento detectado: {sentimiento_detectado.sentimiento}")

            return {"sentimiento": sentimiento_detectado}

    except Exception as e:
        logger.error(f"Error analizando sentimiento: {e}", exc_info=True)
        # Sentimiento por defecto en caso de error
        return {
            "sentimiento": Sentimiento(
                sentimiento="positivo", intencion="consulta", confianza=0.5
            )
        }


async def _analizar_con_llm(mensaje: str) -> Sentimiento:
    """
    Analiza el sentimiento usando el LLM.

    Args:
        mensaje: Mensaje a analizar

    Returns:
        Sentimiento detectado
    """
    from ..config import llm

    prompt = f"""
    Analiza el siguiente mensaje de un paciente y determina:
    1. Sentimiento: positivo, negativo, urgente, o furioso
    2. Intención: queja, consulta, cita, compra, u otro
    3. Confianza: 0.0 a 1.0
    
    Mensaje: "{mensaje}"
    
    Responde SOLO en formato JSON:
    {{"sentimiento": "...", "intencion": "...", "confianza": 0.0}}
    """

    response = await llm.ainvoke(prompt)

    # Parsear respuesta (simplificado)
    import json

    try:
        data = json.loads(response.content)
        return Sentimiento(**data)
    except:
        # Fallback
        return Sentimiento(sentimiento="positivo", intencion="consulta", confianza=0.7)
