"""
Context Tools - Prioridad 3
============================

Tools para contexto conversacional aislado por paciente.

⚠️ CRÍTICO: Siempre filtrar por id_contacto (thread-scoped).

Referencias:
- https://docs.langchain.com/oss/python/concepts/memory#user-specific-memory
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
# TOOL: Buscar Conversaciones Previas (Aisladas por Paciente)
# ============================================================================

@tool
async def buscar_conversaciones_previas(
    query: Annotated[str, "Consulta del usuario"],
    contact_id: Annotated[int, "ID del contacto (thread-scoped)"]
) -> str:
    """
    🔑 PRIORIDAD 3: Busca en conversaciones previas DEL MISMO paciente.
    
    ⚠️ AISLAMIENTO: Solo busca conversaciones de contact_id especificado.
    
    Args:
        query: Consulta del usuario
        contact_id: ID del contacto (thread-scoped)
        
    Returns:
        JSON string con conversaciones similares o mensaje vacío
    """
    pool = await get_pool()
    embeddings_service = get_embeddings_service()
    
    logger.info(f"🔍 [Context Tool] Buscando contexto del contacto {contact_id}")
    
    try:
        # Generar embedding de la consulta
        query_embedding = embeddings_service.embed_query(query)
        
        # ⚠️ FILTRO CRÍTICO: WHERE id_contacto = $1
        sql_query = """
            SELECT 
                id,
                id_conversacion,
                resumen_conversacion,
                embedding,
                metadata,
                fecha_creacion
            FROM conversaciones_embeddings
            WHERE id_contacto = $1
            ORDER BY fecha_creacion DESC
            LIMIT 20
        """
        
        rows = await pool.fetch(sql_query, contact_id)
        
        if not rows:
            logger.info(f"ℹ️ No hay conversaciones previas del contacto {contact_id}")
            return json.dumps({
                "encontrado": False,
                "mensaje": "No hay conversaciones previas de este paciente."
            })
        
        # Calcular similitud coseno
        results = []
        
        for row in rows:
            conv_embedding = pickle.loads(row['embedding'])
            
            similarity = float(np.dot(query_embedding, conv_embedding) / 
                             (np.linalg.norm(query_embedding) * np.linalg.norm(conv_embedding)))
            
            if similarity >= 0.75:  # Umbral para contexto
                results.append({
                    'conversacion_id': row['id_conversacion'],
                    'resumen': row['resumen_conversacion'],
                    'similarity': round(similarity, 3),
                    'fecha': row['fecha_creacion'].isoformat(),
                    'metadata': row['metadata']
                })
        
        # Ordenar por similitud
        results.sort(key=lambda x: x['similarity'], reverse=True)
        results = results[:3]  # Top 3
        
        if results:
            logger.info(f"✅ [Context Tool] {len(results)} conversaciones similares encontradas")
            
            # Actualizar última consulta
            for r in results:
                await pool.execute(
                    "UPDATE conversaciones_embeddings SET fecha_ultima_consulta = NOW() WHERE id_conversacion = $1",
                    r['conversacion_id']
                )
            
            return json.dumps({
                "encontrado": True,
                "conversaciones": results,
                "contact_id": contact_id
            }, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "encontrado": False,
                "mensaje": "No se encontraron conversaciones previas relevantes."
            })
    
    except Exception as e:
        logger.error(f"❌ Error buscando contexto: {e}", exc_info=True)
        return json.dumps({
            "encontrado": False,
            "error": str(e)
        })


# ============================================================================
# TOOL: Guardar Resumen de Conversación
# ============================================================================

@tool
async def guardar_resumen_conversacion(
    contact_id: Annotated[int, "ID del contacto"],
    conversation_id: Annotated[int, "ID de la conversación"],
    resumen: Annotated[str, "Resumen de la conversación"],
    metadata: Annotated[dict, "Metadata adicional"]
) -> str:
    """
    Guarda resumen de conversación con embedding para futuras búsquedas.
    
    Args:
        contact_id: ID del contacto (aislamiento)
        conversation_id: ID de la conversación
        resumen: Resumen textual de la conversación
        metadata: Metadata adicional (topicos, tipo_consulta, etc.)
        
    Returns:
        Mensaje de confirmación
    """
    pool = await get_pool()
    embeddings_service = get_embeddings_service()
    
    try:
        # Generar embedding del resumen
        embedding = embeddings_service.embed_query(resumen)
        embedding_bytes = pickle.dumps(embedding)
        
        # Insertar en BD
        await pool.execute(
            """
            INSERT INTO conversaciones_embeddings 
            (id_contacto, id_conversacion, resumen_conversacion, embedding, metadata)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (id_conversacion) 
            DO UPDATE SET 
                resumen_conversacion = EXCLUDED.resumen_conversacion,
                embedding = EXCLUDED.embedding,
                metadata = EXCLUDED.metadata
            """,
            contact_id, conversation_id, resumen, embedding_bytes, json.dumps(metadata)
        )
        
        logger.info(f"✅ [Context Tool] Resumen guardado para conversación {conversation_id}")
        return "Resumen de conversación guardado correctamente."
    
    except Exception as e:
        logger.error(f"❌ Error guardando resumen: {e}", exc_info=True)
        return f"Error guardando resumen: {str(e)}"
