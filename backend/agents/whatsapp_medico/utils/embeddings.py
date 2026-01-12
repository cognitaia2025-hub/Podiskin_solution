"""
Embeddings Service
==================

Servicio para generar embeddings locales usando sentence-transformers.

Referencias:
- https://www.sbert.net/docs/usage/semantic_textual_similarity.html
"""

from sentence_transformers import SentenceTransformer
import logging
import pickle

logger = logging.getLogger(__name__)

# Modelo all-MiniLM-L6-v2 (384 dimensions, rápido y eficiente)
MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingsService:
    """Servicio de embeddings locales."""
    
    def __init__(self):
        logger.info(f"Inicializando modelo de embeddings: {MODEL_NAME}")
        self.model = SentenceTransformer(MODEL_NAME)
        logger.info("✅ Modelo de embeddings cargado")
    
    def embed_query(self, text: str) -> list:
        """
        Genera embedding de un texto.
        
        Args:
            text: Texto a convertir en embedding
            
        Returns:
            Lista de floats (384 dimensiones)
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_documents(self, texts: list[str]) -> list[list]:
        """
        Genera embeddings para múltiples textos.
        
        Args:
            texts: Lista de textos
            
        Returns:
            Lista de embeddings
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def embed_to_bytes(self, text: str) -> bytes:
        """
        Genera embedding y lo serializa a bytes para PostgreSQL.
        
        Args:
            text: Texto a convertir
            
        Returns:
            Bytes serializados con pickle
        """
        embedding = self.embed_query(text)
        return pickle.dumps(embedding)


# Instancia global
_embeddings_service = None


def get_embeddings_service() -> EmbeddingsService:
    """Obtiene instancia singleton del servicio de embeddings."""
    global _embeddings_service
    
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()
    
    return _embeddings_service
