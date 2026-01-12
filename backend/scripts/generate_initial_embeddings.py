"""
Script para generar embeddings iniciales
=========================================

Genera embeddings para behavior_rules que tienen placeholder E'\\x00'.
"""

import asyncio
import logging
import sys
import os

# Agregar directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_pool
from agents.whatsapp_medico.utils.embeddings import get_embeddings_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_behavior_rules_embeddings():
    """Genera embeddings para reglas de comportamiento."""
    pool = await get_pool()
    embeddings_service = get_embeddings_service()
    
    logger.info("🔍 Buscando behavior_rules sin embeddings...")
    
    # Buscar reglas con embedding placeholder
    rules = await pool.fetch(
        """
        SELECT id, pattern
        FROM behavior_rules
        WHERE embedding = E'\\\\x00'
        """
    )
    
    if not rules:
        logger.info("✅ Todas las reglas ya tienen embeddings")
        return
    
    logger.info(f"📝 Generando embeddings para {len(rules)} reglas...")
    
    for rule in rules:
        try:
            # Generar embedding
            embedding_bytes = embeddings_service.embed_to_bytes(rule['pattern'])
            
            # Actualizar en BD
            await pool.execute(
                "UPDATE behavior_rules SET embedding = $1 WHERE id = $2",
                embedding_bytes,
                rule['id']
            )
            
            logger.info(f"✅ Embedding generado para regla #{rule['id']}")
        
        except Exception as e:
            logger.error(f"❌ Error generando embedding para regla #{rule['id']}: {e}")
    
    logger.info("✅ Proceso completado")


if __name__ == "__main__":
    asyncio.run(generate_behavior_rules_embeddings())
