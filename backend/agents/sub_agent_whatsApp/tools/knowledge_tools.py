"""
Knowledge Base Tools - Herramientas de Base de Conocimiento
============================================================

Tools para buscar y guardar en la base de conocimiento con embeddings.
"""

import logging
import pickle
from typing import Dict, Any, Optional
from langchain_core.tools import tool

from ..utils.embeddings import get_embeddings_service
from ..utils.database import _get_connection, _put_connection

logger = logging.getLogger(__name__)


@tool
def search_knowledge_base(question: str) -> Dict[str, Any]:
    """
    Busca en la base de conocimiento si hay una respuesta similar a la pregunta.

    Usa embeddings semánticos para encontrar preguntas similares aunque
    estén formuladas de manera diferente.

    Args:
        question: La pregunta del usuario

    Returns:
        Diccionario con la respuesta encontrada o None
    """
    logger.info(f"Buscando en KB: {question[:50]}...")

    try:
        # Obtener servicio de embeddings
        embeddings_service = get_embeddings_service()

        # Generar embedding de la pregunta
        question_embedding = embeddings_service.embed_query(question)

        # Obtener todas las preguntas de la KB
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, pregunta, respuesta, pregunta_embedding
                    FROM knowledge_base
                    WHERE pregunta_embedding IS NOT NULL
                    """
                )
                rows = cur.fetchall()
        finally:
            _put_connection(conn)

        if not rows:
            logger.info("KB vacía, no hay respuestas guardadas")
            return {
                "found": False,
                "message": "No hay respuestas en la base de conocimiento aún",
            }

        # Calcular similitudes
        best_match = None
        best_similarity = 0.0

        for row in rows:
            kb_id, kb_pregunta, kb_respuesta, kb_embedding_bytes = row

            # Deserializar embedding
            kb_embedding = pickle.loads(kb_embedding_bytes)

            # Calcular similitud
            import numpy as np

            similarity = np.dot(question_embedding, kb_embedding)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = {
                    "id": kb_id,
                    "pregunta": kb_pregunta,
                    "respuesta": kb_respuesta,
                    "similarity": float(similarity),
                }

        # Threshold de similitud
        THRESHOLD = 0.85

        if best_match and best_match["similarity"] >= THRESHOLD:
            # Incrementar contador
            conn = _get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE knowledge_base 
                        SET veces_consultada = veces_consultada + 1,
                            fecha_actualizacion = NOW()
                        WHERE id = %s
                        """,
                        (best_match["id"],),
                    )
                    conn.commit()
            finally:
                _put_connection(conn)

            logger.info(
                f"Encontrada respuesta similar (similarity: {best_match['similarity']:.2f})"
            )
            return {
                "found": True,
                "respuesta": best_match["respuesta"],
                "similarity": best_match["similarity"],
                "pregunta_original": best_match["pregunta"],
            }
        else:
            logger.info(
                f"No se encontró respuesta similar (best: {best_similarity:.2f})"
            )
            return {
                "found": False,
                "message": "No se encontró una respuesta similar en la base de conocimiento",
            }

    except Exception as e:
        logger.error(f"Error buscando en KB: {e}", exc_info=True)
        return {"found": False, "error": str(e)}


def save_to_knowledge_base(
    pregunta: str, respuesta: str, categoria: Optional[str] = None
) -> int:
    """
    Guarda una pregunta y respuesta en la base de conocimiento.

    Args:
        pregunta: La pregunta
        respuesta: La respuesta
        categoria: Categoría opcional

    Returns:
        ID del registro creado
    """
    logger.info(f"Guardando en KB: {pregunta[:50]}...")

    try:
        # Generar embedding
        embeddings_service = get_embeddings_service()
        embedding = embeddings_service.embed_query(pregunta)
        embedding_bytes = pickle.dumps(embedding)

        # Guardar en BD
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO knowledge_base 
                    (pregunta, respuesta, pregunta_embedding, categoria)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (pregunta, respuesta, embedding_bytes, categoria),
                )
                result = cur.fetchone()
                conn.commit()

                kb_id = result[0]
                logger.info(f"Guardado en KB #{kb_id}")
                return kb_id
        finally:
            _put_connection(conn)

    except Exception as e:
        logger.error(f"Error guardando en KB: {e}", exc_info=True)
        raise
