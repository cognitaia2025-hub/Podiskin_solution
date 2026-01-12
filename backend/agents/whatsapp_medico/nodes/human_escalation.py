"""
Human Escalation Node
=====================

Crea ticket de escalamiento cuando el agente no puede responder.

Referencias:
- https://docs.langchain.com/oss/python/langgraph/workflows-agents#human-in-the-loop
"""

import logging
from typing import Dict, Any
from datetime import datetime

from db import get_pool
from ..state import AgentState

logger = logging.getLogger(__name__)


async def node_human_escalation(state: AgentState) -> Dict[str, Any]:
    """
    Crea ticket de escalamiento a humano.
    
    Flujo:
    1. Crear ticket en dudas_pendientes
    2. Actualizar conversación con requiere_atencion=true
    3. Generar respuesta al usuario
    4. Retornar state con requires_human=True
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con respuesta de escalamiento
    """
    conversation_id = int(state.get('conversation_id', 0))
    message = state.get('message', '')
    escalation_reason = state.get('escalation_reason', 'Consulta compleja')
    retrieved_context = state.get('retrieved_context', '')
    
    logger.info(f"🚨 [Human Escalation] Escalando conversación {conversation_id}")
    
    pool = await get_pool()
    
    try:
        # 1. Crear ticket en dudas_pendientes (si la tabla existe)
        try:
            ticket_id = await pool.fetchval(
                """
                INSERT INTO dudas_pendientes 
                (id_conversacion, pregunta_original, contexto_mensaje, estado, fecha_creacion)
                VALUES ($1, $2, $3, 'pendiente', $4)
                RETURNING id
                """,
                conversation_id,
                message,
                retrieved_context or "Sin contexto recuperado",
                datetime.now()
            )
            logger.info(f"✅ Ticket de escalamiento creado: #{ticket_id}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo crear ticket (tabla dudas_pendientes no existe?): {e}")
            ticket_id = None
        
        # 2. Actualizar conversación
        try:
            await pool.execute(
                """
                UPDATE conversaciones 
                SET requiere_atencion = true,
                    notas_internas = $1,
                    fecha_ultima_actividad = $2
                WHERE id = $3
                """,
                f"Escalado: {escalation_reason}",
                datetime.now(),
                conversation_id
            )
            logger.info(f"✅ Conversación {conversation_id} marcada con requiere_atencion")
        except Exception as e:
            logger.error(f"❌ Error actualizando conversación: {e}")
        
        # 3. Generar respuesta al usuario
        respuesta = """Gracias por tu consulta. Un miembro de nuestro equipo especializado te responderá en breve con información específica.

¿Hay algo más en lo que pueda ayudarte mientras tanto?"""
        
        # 4. Retornar state actualizado
        return {
            **state,
            'respuesta_generada': respuesta,
            'debe_escalar': True,
            'metadata': {
                **state.get('metadata', {}),
                'ticket_id': ticket_id,
                'escalated': True,
                'escalation_reason': escalation_reason
            }
        }
    
    except Exception as e:
        logger.error(f"❌ [Human Escalation] Error en escalamiento: {e}", exc_info=True)
        
        # Fallback
        return {
            **state,
            'respuesta_generada': "Disculpe, tenemos problemas técnicos. Por favor intente más tarde o contacte directamente a la clínica.",
            'debe_escalar': True
        }
