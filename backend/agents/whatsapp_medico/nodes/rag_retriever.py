"""
Nodo: RAG Retriever
===================

Búsqueda en base de conocimiento usando pgvector.
Implementa Fase 1 (Triggers) + Fase 2 (Respuestas).
"""

import logging
from typing import List
from ..state import AgentState, RagDoc
from ..config import embedder
from db import get_pool

logger = logging.getLogger(__name__)


async def rag_retriever(state: AgentState) -> dict:
    """
    Busca conocimiento relevante en la base de datos.

    Fase 1: Busca triggers similares (¿Cuándo responder?)
    Fase 2: Busca respuestas sugeridas + datos del paciente

    Args:
        state: Estado actual del agente

    Returns:
        Dict con documentos RAG y flag de escalamiento
    """
    pool = get_pool()
    msg = state["messages"][-1]["content"]
    chat_id = state["chat_id"]

    logger.info(f"Buscando conocimiento RAG para chat {chat_id}")

    try:
        # Generar embedding del mensaje
        if embedder is None:
            logger.warning("Embedder no disponible, escalando")
            return {"rag_docs": [], "debe_escalar": True}

        msg_embedding = embedder.encode(msg).tolist()

        async with pool.acquire() as conn:
            # FASE 1: Buscar triggers similares (contexto_trigger)
            triggers = await conn.fetch(
                """
                SELECT 
                    id,
                    contexto_trigger,
                    respuesta_sugerida,
                    1 - (embedding_trigger <=> $1::vector) as score
                FROM aprendizajes_agente
                WHERE validado = true
                    AND activo = true
                ORDER BY embedding_trigger <=> $1::vector
                LIMIT 3
                """,
                msg_embedding,
            )

            if not triggers or triggers[0]["score"] < 0.7:
                logger.info("No se encontraron triggers relevantes, escalando")
                return {"rag_docs": [], "debe_escalar": True}

            # FASE 2: Obtener respuestas y datos del paciente
            rag_docs: List[RagDoc] = []

            for trigger in triggers:
                rag_docs.append(
                    RagDoc(
                        id=trigger["id"],
                        respuesta_sugerida=trigger["respuesta_sugerida"],
                        score=float(trigger["score"]),
                        trigger_match=True,
                    )
                )

            # Buscar paciente por chat_id
            paciente = await conn.fetchrow(
                """
                SELECT p.id, p.nombre, p.telefono
                FROM pacientes p
                JOIN conversaciones c ON c.id_paciente = p.id
                WHERE c.chat_id = $1
                LIMIT 1
                """,
                chat_id,
            )

            paciente_id = paciente["id"] if paciente else None

            logger.info(
                f"RAG: {len(rag_docs)} docs encontrados, "
                f"mejor score: {rag_docs[0].score:.2f}, "
                f"paciente_id: {paciente_id}"
            )

            return {
                "rag_docs": rag_docs,
                "paciente_id": paciente_id,
                "debe_escalar": False,
            }

    except Exception as e:
        logger.error(f"Error en RAG retrieval: {e}", exc_info=True)
        return {"rag_docs": [], "debe_escalar": True}
