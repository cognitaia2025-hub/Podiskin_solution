"""
Knowledge Base Tools - Prioridad 2
===================================

Tools para consultar knowledge base validada (pgvector).

⚠️ Solo para FAQs, políticas y procedimientos. NUNCA precios/horarios/servicios.

Referencias:
- https://docs.langchain.com/oss/python/concepts/memory#vector-stores
"""

from langchain.tools import tool
from typing import Annotated
import logging
import numpy as np
import pickle
import json

from db import get_pool
from ..utils.embeddings import get_embeddings_service

logger = logging.getLogger(__name__)

# ============================================================================
# TOOL: Buscar en Knowledge Base Validada
# ============================================================================

@tool
async def buscar_knowledge_base_validada(
    query: Annotated[str, "Pregunta del usuario"]
) -> str:
    """
    🔑 PRIORIDAD 2: Busca en knowledge base validada usando similitud coseno.
    
    ⚠️ Solo conocimiento general. NO precios, horarios ni servicios.
    
    Args:
        query: Pregunta del usuario
        
    Returns:
        JSON string con respuesta encontrada o mensaje de no encontrado
    """
    pool = await get_pool()
    embeddings_service = get_embeddings_service()
    
    logger.info(f"🔍 [KB Tool] Buscando en knowledge base: '{query[:50]}...'")
    
    try:
        # Generar embedding de la consulta
        query_embedding = embeddings_service.embed_query(query)
        
        # Buscar en KB (cosine similarity)
        sql_query = """
            SELECT 
                id,
                pregunta,
                respuesta,
                categoria,
                pregunta_embedding,
                veces_consultada,
                efectividad_score
            FROM knowledge_base_validated
            WHERE aprobado = true
            AND contiene_datos_operativos = false
            AND categoria IN ('FAQ_Proceso', 'Politica_Clinica', 'Informacion_General', 'Procedimiento_Medico')
            ORDER BY fecha_creacion DESC
            LIMIT 50
        """
        
        rows = await pool.fetch(sql_query)
        
        if not rows:
            logger.warning("⚠️ No hay entries en knowledge base validada")
            return json.dumps({
                "encontrado": False,
                "mensaje": "No se encontró información relevante en la base de conocimiento."
            })
        
        # Calcular similitud coseno con cada entry
        best_match = None
        best_similarity = 0.0
        
        for row in rows:
            kb_embedding = pickle.loads(row['pregunta_embedding'])
            
            # Similitud coseno normalizada (0-1)
            similarity = float(np.dot(query_embedding, kb_embedding) / 
                             (np.linalg.norm(query_embedding) * np.linalg.norm(kb_embedding)))
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = row
        
        # Umbral de confianza: 0.85
        MIN_CONFIDENCE = 0.85
        
        if best_match and best_similarity >= MIN_CONFIDENCE:
            # Incrementar contador de uso
            await pool.execute(
                "UPDATE knowledge_base_validated SET veces_consultada = veces_consultada + 1, fecha_ultimo_uso = NOW() WHERE id = $1",
                best_match['id']
            )
            
            logger.info(f"✅ [KB Tool] Match encontrado (similarity: {best_similarity:.3f})")
            
            return json.dumps({
                "encontrado": True,
                "pregunta": best_match['pregunta'],
                "respuesta": best_match['respuesta'],
                "categoria": best_match['categoria'],
                "confidence": round(best_similarity, 3),
                "kb_id": best_match['id']
            }, ensure_ascii=False, indent=2)
        else:
            logger.warning(f"⚠️ [KB Tool] Similarity muy baja: {best_similarity:.3f} (min: {MIN_CONFIDENCE})")
            return json.dumps({
                "encontrado": False,
                "confidence": round(best_similarity, 3) if best_match else 0.0,
                "mensaje": "No se encontró información suficientemente relevante."
            })
    
    except Exception as e:
        logger.error(f"❌ Error buscando en KB: {e}", exc_info=True)
        return json.dumps({
            "encontrado": False,
            "error": str(e)
        })


# ============================================================================
# TOOL: Registrar Feedback de KB
# ============================================================================

@tool
async def registrar_feedback_kb(
    kb_id: Annotated[int, "ID de la entry de KB"],
    feedback: Annotated[str, "positivo o negativo"]
) -> str:
    """
    Registra feedback de usuario sobre una respuesta de KB.
    
    Args:
        kb_id: ID de la entry en knowledge_base_validated
        feedback: "positivo" o "negativo"
        
    Returns:
        Mensaje de confirmación
    """
    pool = await get_pool()
    
    try:
        if feedback == "positivo":
            await pool.execute(
                "UPDATE knowledge_base_validated SET feedback_positivo = feedback_positivo + 1 WHERE id = $1",
                kb_id
            )
        elif feedback == "negativo":
            await pool.execute(
                "UPDATE knowledge_base_validated SET feedback_negativo = feedback_negativo + 1 WHERE id = $1",
                kb_id
            )
        else:
            return "Feedback inválido. Use 'positivo' o 'negativo'."
        
        logger.info(f"✅ [KB Tool] Feedback '{feedback}' registrado para KB #{kb_id}")
        return f"Feedback '{feedback}' registrado correctamente."
    
    except Exception as e:
        logger.error(f"❌ Error registrando feedback: {e}", exc_info=True)
        return f"Error registrando feedback: {str(e)}"
