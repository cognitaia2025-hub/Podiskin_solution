"""
Tool: Save RAG Learning
=======================

Guarda nuevo conocimiento en la base de datos para auto-aprendizaje.
"""

import logging
from db import get_pool
from ..config import embedder

logger = logging.getLogger(__name__)


async def save_rag_learning(
    pregunta: str,
    respuesta: str,
    tono_cliente: str = "neutral",
    tono_respuesta: str = "profesional",
    categoria: str = "general",
    id_conversacion: int | None = None,
    id_duda: int | None = None,
) -> dict:
    """
    Aprende nueva respuesta para futuras consultas.

    Args:
        pregunta: Pregunta original del paciente
        respuesta: Respuesta del humano
        tono_cliente: Tono detectado del cliente
        tono_respuesta: Tono usado en la respuesta
        categoria: Categoría del aprendizaje
        id_conversacion: ID de la conversación (opcional)
        id_duda: ID de la duda escalada (opcional)

    Returns:
        Dict con el resultado de la operación
    """
    pool = get_pool()

    try:
        if embedder is None:
            logger.error("Embedder no disponible para auto-aprendizaje")
            return {"success": False, "error": "Embedder no disponible"}

        # Generar embeddings
        trigger_embedding = embedder.encode(pregunta).tolist()
        response_embedding = embedder.encode(respuesta).tolist()

        async with pool.acquire() as conn:
            # Insertar aprendizaje
            result = await conn.fetchrow(
                """
                INSERT INTO aprendizajes_agente (
                    pregunta_original,
                    contexto_trigger,
                    respuesta_sugerida,
                    respuesta_admin,
                    tono_cliente,
                    tono_respuesta,
                    categoria,
                    embedding_trigger,
                    embedding_respuesta,
                    id_conversacion,
                    id_duda,
                    validado,
                    activo,
                    fecha_creacion
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8::vector, $9::vector,
                    $10, $11, true, true, CURRENT_TIMESTAMP
                )
                RETURNING id
                """,
                pregunta,
                f"Cuando el cliente pregunta sobre: {pregunta[:100]}",
                respuesta,
                respuesta,
                tono_cliente,
                tono_respuesta,
                categoria,
                trigger_embedding,
                response_embedding,
                id_conversacion,
                id_duda,
            )

            aprendizaje_id = result["id"]
            logger.info(f"✅ Aprendizaje guardado: ID {aprendizaje_id}")

            return {
                "success": True,
                "aprendizaje_id": aprendizaje_id,
                "message": "Aprendizaje guardado exitosamente",
            }

    except Exception as e:
        logger.error(f"Error guardando aprendizaje: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
