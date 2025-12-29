"""
RAG Tools - Sub-Agente WhatsApp
================================

Herramientas de Retrieval-Augmented Generation para contexto conversacional.
"""

import logging
import pickle
from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain_core.tools import tool

from ..utils import fetch, fetchrow, execute, get_embeddings_service

logger = logging.getLogger(__name__)


@tool
async def retrieve_context(
    query: str,
    conversation_id: Optional[int] = None,
    k: int = 5,
    threshold: float = 0.75,
) -> Dict[str, Any]:
    """
    Recupera contexto relevante usando búsqueda semántica.

    Busca en conversaciones previas, FAQs y knowledge base para encontrar
    información relevante que ayude a responder la consulta actual.

    Args:
        query: Consulta o pregunta del usuario
        conversation_id: ID de la conversación actual (para excluir)
        k: Número máximo de resultados a retornar
        threshold: Umbral mínimo de similitud (0.0 a 1.0)

    Returns:
        Diccionario con contexto relevante encontrado
    """
    logger.info(f"Retrieving context for query: {query[:50]}...")

    try:
        # Obtener servicio de embeddings
        embeddings_service = get_embeddings_service()

        # Generar embedding de la consulta
        query_embedding = embeddings_service.embed_query(query)

        # Buscar en knowledge base
        kb_query = """
        SELECT 
            id,
            pregunta,
            respuesta,
            pregunta_embedding,
            categoria,
            veces_consultada
        FROM knowledge_base
        WHERE pregunta_embedding IS NOT NULL
        ORDER BY fecha_creacion DESC
        LIMIT 50
        """
        kb_results = await fetch(kb_query)

        # Calcular similitudes
        import numpy as np

        contexts = []

        for row in kb_results:
            kb_embedding = pickle.loads(row["pregunta_embedding"])
            similarity = float(np.dot(query_embedding, kb_embedding))

            if similarity >= threshold:
                contexts.append(
                    {
                        "source": "knowledge_base",
                        "id": row["id"],
                        "pregunta": row["pregunta"],
                        "respuesta": row["respuesta"],
                        "categoria": row["categoria"],
                        "similarity": similarity,
                        "relevancia": "alta" if similarity >= 0.9 else "media",
                    }
                )

        # Buscar en conversaciones previas (resúmenes)
        if conversation_id:
            conv_query = """
            SELECT 
                id,
                resumen_ia,
                embedding,
                categoria,
                fecha_inicio
            FROM conversaciones
            WHERE id != %s
              AND resumen_ia IS NOT NULL
              AND embedding IS NOT NULL
              AND estado = 'Finalizada'
            ORDER BY fecha_ultima_actividad DESC
            LIMIT 30
            """
            conv_results = await fetch(conv_query, conversation_id)

            for row in conv_results:
                if row["embedding"]:
                    conv_embedding = pickle.loads(row["embedding"])
                    similarity = float(np.dot(query_embedding, conv_embedding))

                    if similarity >= threshold:
                        contexts.append(
                            {
                                "source": "conversacion_previa",
                                "id": row["id"],
                                "resumen": row["resumen_ia"],
                                "categoria": row["categoria"],
                                "fecha": row["fecha_inicio"].isoformat(),
                                "similarity": similarity,
                                "relevancia": "alta" if similarity >= 0.9 else "media",
                            }
                        )

        # Ordenar por similitud
        contexts.sort(key=lambda x: x["similarity"], reverse=True)

        # Limitar a k resultados
        contexts = contexts[:k]

        if not contexts:
            return {
                "success": True,
                "found": False,
                "message": "No se encontró contexto relevante",
                "contexts": [],
            }

        logger.info(f"Found {len(contexts)} relevant contexts")

        return {
            "success": True,
            "found": True,
            "count": len(contexts),
            "contexts": contexts,
        }

    except Exception as e:
        logger.error(f"Error retrieving context: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@tool
async def index_conversation(
    conversation_id: int,
    pregunta: str,
    respuesta: str,
    metadata: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Indexa una conversación en la base de conocimiento para futuras búsquedas.

    Guarda una pregunta-respuesta validada de una conversación real
    para que pueda ser recuperada en contextos similares futuros.

    Args:
        conversation_id: ID de la conversación
        pregunta: Pregunta del usuario
        respuesta: Respuesta proporcionada
        metadata: Metadatos adicionales (categoría, validación, etc.)

    Returns:
        Diccionario con resultado de la indexación
    """
    logger.info(f"Indexing conversation {conversation_id}")

    try:
        # Obtener servicio de embeddings
        embeddings_service = get_embeddings_service()

        # Generar embedding de la pregunta
        pregunta_embedding = embeddings_service.embed_query(pregunta)
        embedding_bytes = pickle.dumps(pregunta_embedding)

        # Extraer metadata
        categoria = metadata.get("categoria", "general") if metadata else "general"
        validado = metadata.get("validado", False) if metadata else False

        # Guardar en knowledge base
        query = """
        INSERT INTO knowledge_base (
            pregunta,
            respuesta,
            pregunta_embedding,
            categoria,
            validado,
            fuente_conversacion_id
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """

        result = await fetchrow(
            query,
            pregunta,
            respuesta,
            embedding_bytes,
            categoria,
            validado,
            conversation_id,
        )

        kb_id = result["id"]

        # Registrar en audit_logs
        await execute(
            """
            INSERT INTO audit_logs (tabla, accion, registro_id, detalles, usuario)
            VALUES ('knowledge_base', 'insert', %s, %s, 'whatsapp_agent')
            """,
            kb_id,
            f"Conversación {conversation_id} indexada automáticamente",
        )

        logger.info(f"Conversation indexed successfully as KB #{kb_id}")

        return {
            "success": True,
            "kb_id": kb_id,
            "message": "Conversación indexada exitosamente",
        }

    except Exception as e:
        logger.error(f"Error indexing conversation: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@tool
async def search_similar_conversations(
    conversation_id: int,
    k: int = 5,
    threshold: float = 0.80,
) -> Dict[str, Any]:
    """
    Busca conversaciones similares a una conversación dada.

    Útil para encontrar patrones, resolver casos similares o
    aprender de interacciones previas exitosas.

    Args:
        conversation_id: ID de la conversación de referencia
        k: Número máximo de conversaciones similares a retornar
        threshold: Umbral mínimo de similitud

    Returns:
        Diccionario con conversaciones similares encontradas
    """
    logger.info(f"Searching similar conversations to {conversation_id}")

    try:
        # Obtener la conversación de referencia
        ref_query = """
        SELECT id, resumen_ia, embedding, categoria
        FROM conversaciones
        WHERE id = %s AND embedding IS NOT NULL
        """
        ref_conv = await fetchrow(ref_query, conversation_id)

        if not ref_conv:
            return {
                "success": False,
                "error": "Conversación no encontrada o sin embedding",
            }

        # Deserializar embedding de referencia
        import numpy as np

        ref_embedding = pickle.loads(ref_conv["embedding"])

        # Buscar conversaciones similares
        search_query = """
        SELECT 
            id,
            resumen_ia,
            embedding,
            categoria,
            estado,
            fecha_inicio,
            fecha_ultima_actividad
        FROM conversaciones
        WHERE id != %s
          AND embedding IS NOT NULL
          AND estado = 'Finalizada'
        ORDER BY fecha_ultima_actividad DESC
        LIMIT 100
        """
        candidates = await fetch(search_query, conversation_id)

        similar_conversations = []

        for row in candidates:
            candidate_embedding = pickle.loads(row["embedding"])
            similarity = float(np.dot(ref_embedding, candidate_embedding))

            if similarity >= threshold:
                similar_conversations.append(
                    {
                        "id": row["id"],
                        "resumen": row["resumen_ia"],
                        "categoria": row["categoria"],
                        "estado": row["estado"],
                        "fecha": row["fecha_inicio"].isoformat(),
                        "similarity": similarity,
                    }
                )

        # Ordenar por similitud
        similar_conversations.sort(key=lambda x: x["similarity"], reverse=True)

        # Limitar a k resultados
        similar_conversations = similar_conversations[:k]

        if not similar_conversations:
            return {
                "success": True,
                "found": False,
                "message": "No se encontraron conversaciones similares",
            }

        logger.info(f"Found {len(similar_conversations)} similar conversations")

        return {
            "success": True,
            "found": True,
            "count": len(similar_conversations),
            "reference_conversation": {
                "id": ref_conv["id"],
                "resumen": ref_conv["resumen_ia"],
                "categoria": ref_conv["categoria"],
            },
            "similar_conversations": similar_conversations,
        }

    except Exception as e:
        logger.error(f"Error searching similar conversations: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
