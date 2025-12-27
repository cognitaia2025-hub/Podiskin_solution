"""
Embeddings Service - Sub-Agente WhatsApp
=========================================

Servicio de embeddings local usando all-MiniLM-L6-v2.
"""

import logging
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings

from ..config import config

logger = logging.getLogger(__name__)


class LocalEmbeddings(Embeddings):
    """
    Embeddings locales usando sentence-transformers.

    Utiliza el modelo all-MiniLM-L6-v2 que genera embeddings de 384 dimensiones.
    """

    def __init__(self, model_name: str = None):
        """
        Inicializa el servicio de embeddings.

        Args:
            model_name: Nombre del modelo (default: all-MiniLM-L6-v2)
        """
        self.model_name = model_name or config.embedding_model
        self.dimension = config.embedding_dimension

        logger.info(f"Loading embedding model: {self.model_name}")

        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(
                f"Embedding model loaded successfully. Dimension: {self.dimension}"
            )
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}", exc_info=True)
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Genera embeddings para múltiples documentos.

        Args:
            texts: Lista de textos a embedear

        Returns:
            Lista de embeddings (cada uno es una lista de floats)
        """
        if not texts:
            return []

        try:
            logger.debug(f"Embedding {len(texts)} documents...")

            embeddings = self.model.encode(
                texts,
                batch_size=config.embedding_batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,  # Normalizar para similitud coseno
            )

            # Convertir a lista de listas
            result = embeddings.tolist()

            logger.debug(f"Successfully embedded {len(texts)} documents")
            return result

        except Exception as e:
            logger.error(f"Error embedding documents: {str(e)}", exc_info=True)
            raise

    def embed_query(self, text: str) -> List[float]:
        """
        Genera embedding para una consulta individual.

        Args:
            text: Texto a embedear

        Returns:
            Embedding como lista de floats
        """
        try:
            logger.debug(f"Embedding query: {text[:50]}...")

            embedding = self.model.encode(
                [text],
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )[0]

            result = embedding.tolist()

            logger.debug("Query embedded successfully")
            return result

        except Exception as e:
            logger.error(f"Error embedding query: {str(e)}", exc_info=True)
            raise

    def similarity(self, text1: str, text2: str) -> float:
        """
        Calcula la similitud coseno entre dos textos.

        Args:
            text1: Primer texto
            text2: Segundo texto

        Returns:
            Similitud coseno (0.0 a 1.0)
        """
        try:
            emb1 = np.array(self.embed_query(text1))
            emb2 = np.array(self.embed_query(text2))

            # Similitud coseno (ya están normalizados)
            similarity = np.dot(emb1, emb2)

            return float(similarity)

        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}", exc_info=True)
            raise

    def batch_similarity(self, query: str, texts: List[str]) -> List[float]:
        """
        Calcula la similitud de una consulta con múltiples textos.

        Args:
            query: Texto de consulta
            texts: Lista de textos para comparar

        Returns:
            Lista de similitudes
        """
        try:
            query_emb = np.array(self.embed_query(query))
            text_embs = np.array(self.embed_documents(texts))

            # Similitud coseno con todos los textos
            similarities = np.dot(text_embs, query_emb)

            return similarities.tolist()

        except Exception as e:
            logger.error(f"Error calculating batch similarity: {str(e)}", exc_info=True)
            raise


# ============================================================================
# INSTANCIA GLOBAL
# ============================================================================

# Singleton del servicio de embeddings
_embeddings_service: LocalEmbeddings = None


def get_embeddings_service() -> LocalEmbeddings:
    """
    Obtiene la instancia global del servicio de embeddings.

    Returns:
        Instancia de LocalEmbeddings
    """
    global _embeddings_service

    if _embeddings_service is None:
        _embeddings_service = LocalEmbeddings()

    return _embeddings_service


# ============================================================================
# UTILIDADES
# ============================================================================


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Divide un texto largo en chunks más pequeños.

    Args:
        text: Texto a dividir
        chunk_size: Tamaño máximo de cada chunk en caracteres
        overlap: Solapamiento entre chunks

    Returns:
        Lista de chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Si no es el último chunk, buscar el último espacio
        if end < len(text):
            last_space = text.rfind(" ", start, end)
            if last_space > start:
                end = last_space

        chunks.append(text[start:end].strip())
        start = end - overlap

    return chunks


def preprocess_text(text: str) -> str:
    """
    Preprocesa un texto antes de generar embeddings.

    Args:
        text: Texto a preprocesar

    Returns:
        Texto preprocesado
    """
    # Eliminar espacios múltiples
    text = " ".join(text.split())

    # Eliminar caracteres especiales excesivos
    # (mantener puntuación básica para contexto)

    return text.strip()
