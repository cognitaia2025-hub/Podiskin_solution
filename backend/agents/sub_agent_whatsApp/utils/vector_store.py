"""
Vector Store - Sub-Agente WhatsApp
===================================

Gestión de pgvector para almacenamiento y búsqueda de embeddings.
"""

import logging
import pickle
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio

import numpy as np

from .database import fetch, fetchrow, execute, execute_many
from .embeddings import get_embeddings_service

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Clase para gestionar el almacenamiento y búsqueda de vectores usando pgvector.

    Proporciona una interfaz de alto nivel para:
    - Agregar documentos con embeddings automáticos
    - Búsqueda por similitud semántica
    - Filtrado por metadatos y validación
    - Gestión de embeddings persistentes en PostgreSQL
    """

    def __init__(self, collection_name: str = "knowledge_base"):
        """
        Inicializa el vector store.

        Args:
            collection_name: Nombre de la tabla/colección a usar
        """
        self.collection_name = collection_name
        self.embeddings_service = get_embeddings_service()
        logger.info(f"VectorStore initialized for collection: {collection_name}")

    async def add_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None,
        doc_id: Optional[int] = None,
    ) -> int:
        """
        Agrega un documento al vector store.

        Args:
            text: Texto del documento (pregunta o contenido)
            metadata: Metadatos asociados (respuesta, categoría, etc.)
            embedding: Embedding pre-calculado (opcional, se calcula si no se provee)
            doc_id: ID del documento (opcional, para actualizaciones)

        Returns:
            ID del documento creado/actualizado
        """
        logger.info(f"Adding document to vector store: {text[:50]}...")

        try:
            # Generar embedding si no se provee
            if embedding is None:
                embedding = self.embeddings_service.embed_query(text)

            # Serializar embedding
            embedding_bytes = pickle.dumps(embedding)

            # Extraer metadata
            respuesta = metadata.get("respuesta", "") if metadata else ""
            categoria = metadata.get("categoria", "general") if metadata else "general"
            validado = metadata.get("validado", False) if metadata else False
            fuente_id = metadata.get("fuente_conversacion_id") if metadata else None

            if doc_id:
                # Actualizar documento existente
                query = """
                UPDATE knowledge_base
                SET pregunta = %s,
                    respuesta = %s,
                    pregunta_embedding = %s,
                    categoria = %s,
                    validado = %s,
                    fecha_actualizacion = NOW()
                WHERE id = %s
                RETURNING id
                """
                result = await fetchrow(
                    query,
                    text,
                    respuesta,
                    embedding_bytes,
                    categoria,
                    validado,
                    doc_id,
                )
            else:
                # Insertar nuevo documento
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
                    text,
                    respuesta,
                    embedding_bytes,
                    categoria,
                    validado,
                    fuente_id,
                )

            doc_id = result["id"]
            logger.info(f"Document added/updated successfully: ID {doc_id}")
            return doc_id

        except Exception as e:
            logger.error(f"Error adding document to vector store: {e}", exc_info=True)
            raise

    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
    ) -> List[int]:
        """
        Agrega múltiples documentos al vector store.

        Args:
            documents: Lista de diccionarios con keys:
                - text: Texto del documento
                - metadata: Metadatos opcionales

        Returns:
            Lista de IDs de documentos creados
        """
        logger.info(f"Adding {len(documents)} documents to vector store")

        doc_ids = []
        for doc in documents:
            doc_id = await self.add_document(
                text=doc["text"],
                metadata=doc.get("metadata"),
                embedding=doc.get("embedding"),
            )
            doc_ids.append(doc_id)

        logger.info(f"Successfully added {len(doc_ids)} documents")
        return doc_ids

    async def similarity_search(
        self,
        query_text: str,
        k: int = 5,
        threshold: float = 0.75,
        filter_validated: Optional[bool] = None,
        filter_category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Realiza búsqueda por similitud semántica.

        Args:
            query_text: Texto de consulta
            k: Número máximo de resultados
            threshold: Umbral mínimo de similitud (0.0 a 1.0)
            filter_validated: Filtrar solo validados (True/False/None)
            filter_category: Filtrar por categoría específica

        Returns:
            Lista de documentos similares con scores
        """
        logger.info(f"Searching similar documents for: {query_text[:50]}...")

        try:
            # Generar embedding de la consulta
            query_embedding = self.embeddings_service.embed_query(query_text)

            # Construir query SQL con filtros
            base_query = """
            SELECT 
                id,
                pregunta,
                respuesta,
                pregunta_embedding,
                categoria,
                validado,
                veces_consultada,
                fecha_creacion
            FROM knowledge_base
            WHERE pregunta_embedding IS NOT NULL
            """

            params = []
            if filter_validated is not None:
                base_query += " AND validado = %s"
                params.append(filter_validated)

            if filter_category:
                base_query += " AND categoria = %s"
                params.append(filter_category)

            base_query += " ORDER BY fecha_creacion DESC LIMIT 100"

            # Ejecutar query
            candidates = await fetch(base_query, *params)

            if not candidates:
                logger.info("No candidates found in vector store")
                return []

            # Calcular similitudes
            results = []
            for row in candidates:
                doc_embedding = pickle.loads(row["pregunta_embedding"])
                similarity = float(np.dot(query_embedding, doc_embedding))

                if similarity >= threshold:
                    results.append(
                        {
                            "id": row["id"],
                            "text": row["pregunta"],
                            "response": row["respuesta"],
                            "category": row["categoria"],
                            "validated": row["validado"],
                            "times_used": row["veces_consultada"],
                            "similarity": similarity,
                            "created_at": (
                                row["fecha_creacion"].isoformat()
                                if row["fecha_creacion"]
                                else None
                            ),
                        }
                    )

            # Ordenar por similitud
            results.sort(key=lambda x: x["similarity"], reverse=True)

            # Limitar a k resultados
            results = results[:k]

            logger.info(f"Found {len(results)} similar documents")

            # Actualizar contadores de uso
            if results:
                doc_ids = [r["id"] for r in results]
                await self._increment_usage_counters(doc_ids)

            return results

        except Exception as e:
            logger.error(f"Error in similarity search: {e}", exc_info=True)
            raise

    async def get_by_id(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un documento por su ID.

        Args:
            doc_id: ID del documento

        Returns:
            Diccionario con información del documento o None si no existe
        """
        logger.info(f"Getting document by ID: {doc_id}")

        try:
            query = """
            SELECT 
                id,
                pregunta,
                respuesta,
                categoria,
                validado,
                veces_consultada,
                fecha_creacion,
                fecha_actualizacion
            FROM knowledge_base
            WHERE id = %s
            """

            result = await fetchrow(query, doc_id)

            if not result:
                logger.info(f"Document {doc_id} not found")
                return None

            return {
                "id": result["id"],
                "text": result["pregunta"],
                "response": result["respuesta"],
                "category": result["categoria"],
                "validated": result["validado"],
                "times_used": result["veces_consultada"],
                "created_at": (
                    result["fecha_creacion"].isoformat()
                    if result["fecha_creacion"]
                    else None
                ),
                "updated_at": (
                    result["fecha_actualizacion"].isoformat()
                    if result["fecha_actualizacion"]
                    else None
                ),
            }

        except Exception as e:
            logger.error(f"Error getting document by ID: {e}", exc_info=True)
            raise

    async def update_validation(
        self,
        doc_id: int,
        validated: bool,
        validated_by: Optional[str] = None,
    ) -> bool:
        """
        Actualiza el estado de validación de un documento.

        Args:
            doc_id: ID del documento
            validated: Nuevo estado de validación
            validated_by: Usuario que validó (opcional)

        Returns:
            True si se actualizó correctamente, False si no existe
        """
        logger.info(f"Updating validation for document {doc_id}: {validated}")

        try:
            query = """
            UPDATE knowledge_base
            SET validado = %s,
                fecha_actualizacion = NOW()
            WHERE id = %s
            RETURNING id
            """

            result = await fetchrow(query, validated, doc_id)

            if not result:
                logger.warning(f"Document {doc_id} not found for validation update")
                return False

            # Registrar en audit_logs
            await execute(
                """
                INSERT INTO audit_logs (tabla, accion, registro_id, detalles, usuario)
                VALUES ('knowledge_base', 'update', %s, %s, %s)
                """,
                doc_id,
                f"Validación actualizada a: {validated}",
                validated_by or "system",
            )

            logger.info(f"Document {doc_id} validation updated successfully")
            return True

        except Exception as e:
            logger.error(f"Error updating validation: {e}", exc_info=True)
            raise

    async def delete_document(self, doc_id: int) -> bool:
        """
        Elimina un documento del vector store.

        Args:
            doc_id: ID del documento a eliminar

        Returns:
            True si se eliminó, False si no existía
        """
        logger.info(f"Deleting document {doc_id}")

        try:
            query = "DELETE FROM knowledge_base WHERE id = %s RETURNING id"
            result = await fetchrow(query, doc_id)

            if not result:
                logger.warning(f"Document {doc_id} not found for deletion")
                return False

            logger.info(f"Document {doc_id} deleted successfully")
            return True

        except Exception as e:
            logger.error(f"Error deleting document: {e}", exc_info=True)
            raise

    async def _increment_usage_counters(self, doc_ids: List[int]) -> None:
        """
        Incrementa los contadores de uso de los documentos.

        Args:
            doc_ids: Lista de IDs de documentos
        """
        try:
            if not doc_ids:
                return

            query = """
            UPDATE knowledge_base
            SET veces_consultada = veces_consultada + 1,
                fecha_actualizacion = NOW()
            WHERE id = ANY(%s)
            """

            await execute(query, doc_ids)

        except Exception as e:
            # No es crítico, solo log
            logger.warning(f"Error incrementing usage counters: {e}")

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del vector store.

        Returns:
            Diccionario con estadísticas
        """
        logger.info("Getting vector store statistics")

        try:
            stats_query = """
            SELECT 
                COUNT(*) as total_documents,
                COUNT(*) FILTER (WHERE validado = true) as validated_documents,
                COUNT(*) FILTER (WHERE pregunta_embedding IS NOT NULL) as with_embeddings,
                COUNT(DISTINCT categoria) as total_categories,
                SUM(veces_consultada) as total_queries
            FROM knowledge_base
            """

            stats = await fetchrow(stats_query)

            # Top categorías
            categories_query = """
            SELECT categoria, COUNT(*) as count
            FROM knowledge_base
            GROUP BY categoria
            ORDER BY count DESC
            LIMIT 5
            """

            categories = await fetch(categories_query)

            return {
                "total_documents": stats["total_documents"],
                "validated_documents": stats["validated_documents"],
                "with_embeddings": stats["with_embeddings"],
                "total_categories": stats["total_categories"],
                "total_queries": stats["total_queries"],
                "top_categories": [
                    {"name": c["categoria"], "count": c["count"]} for c in categories
                ],
            }

        except Exception as e:
            logger.error(f"Error getting statistics: {e}", exc_info=True)
            raise


# Instancia global del vector store
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """
    Obtiene la instancia global del vector store.

    Returns:
        Instancia de VectorStore
    """
    global _vector_store

    if _vector_store is None:
        _vector_store = VectorStore()

    return _vector_store
