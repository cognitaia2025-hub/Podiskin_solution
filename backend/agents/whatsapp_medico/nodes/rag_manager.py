"""
RAG Manager Node - Búsqueda Dual Optimizada
============================================

Implementa búsqueda con prioridades estrictas:
1. SQL estructurado (FUENTE DE VERDAD)
2. Knowledge Base validada (pgvector)
3. Contexto conversacional (aislado por contacto)

Referencias:
- https://docs.langchain.com/oss/python/langgraph/agentic-rag
"""

import logging
from typing import Dict, Any
import json

from ..state import AgentState
from ..tools.sql_tools import (
    consultar_tratamientos_sql,
    consultar_horarios_sql,
    consultar_citas_sql
)
from ..tools.kb_tools import buscar_knowledge_base_validada
from ..tools.context_tools import buscar_conversaciones_previas

logger = logging.getLogger(__name__)


async def node_rag_manager(state: AgentState) -> Dict[str, Any]:
    """
    Nodo de búsqueda dual con prioridades estrictas.
    
    Flujo:
    1. Clasificar tipo de consulta
    2. PRIORIDAD 1: Buscar en SQL estructurado
    3. PRIORIDAD 2: Buscar en Knowledge Base validada
    4. PRIORIDAD 3: Buscar en contexto conversacional
    5. Si nada funciona: Escalar a humano
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con contexto recuperado
    """
    query = state.get('message', '')
    contact_id = int(state.get('contact_id', 0))
    
    logger.info(f"🔍 [RAG Manager] Procesando consulta del contacto {contact_id}")
    
    # ========================================================================
    # PASO 1: Clasificar tipo de consulta
    # ========================================================================
    tipo_consulta = await clasificar_tipo_consulta(query)
    logger.info(f"📊 Tipo de consulta detectado: {tipo_consulta}")
    
    # ========================================================================
    # PASO 2: PRIORIDAD 1 - SQL Estructurado
    # ========================================================================
    
    if tipo_consulta in ['servicio', 'precio', 'tratamiento']:
        logger.info("🔑 [PRIORIDAD 1] Consultando tabla estructurada: tratamientos")
        
        # Extraer término de búsqueda
        termino = extraer_termino_tratamiento(query)
        
        if termino:
            result = await consultar_tratamientos_sql(termino)
            
            # Verificar si se encontró algo
            try:
                data = json.loads(result)
                if isinstance(data, list) and len(data) > 0:
                    logger.info(f"✅ Servicios encontrados en SQL: {len(data)}")
                    return {
                        **state,
                        'retrieved_context': result,
                        'fuente': 'sql_estructurado',
                        'confidence': 1.0,  # Máxima confianza
                        'metadata': {
                            **state.get('metadata', {}),
                            'tipo_consulta': tipo_consulta,
                            'tabla': 'tratamientos',
                            'termino_busqueda': termino
                        }
                    }
            except json.JSONDecodeError as e:
                logger.warning(f"Error parsing JSON de tratamientos: {e}")
            except Exception as e:
                logger.error(f"Error inesperado en búsqueda de tratamientos: {e}", exc_info=True)
    
    if tipo_consulta in ['horario', 'disponibilidad']:
        logger.info("🔑 [PRIORIDAD 1] Consultando tabla estructurada: horarios_trabajo")
        
        # Extraer día de la semana
        dia_semana = extraer_dia_semana(query)
        
        if dia_semana is not None:
            result = await consultar_horarios_sql(dia_semana)
            
            try:
                data = json.loads(result)
                if isinstance(data, list) and len(data) > 0:
                    logger.info(f"✅ Horarios encontrados en SQL")
                    return {
                        **state,
                        'retrieved_context': result,
                        'fuente': 'sql_estructurado',
                        'confidence': 1.0,
                        'metadata': {
                            **state.get('metadata', {}),
                            'tipo_consulta': tipo_consulta,
                            'tabla': 'horarios_trabajo',
                            'dia_semana': dia_semana
                        }
                    }
            except json.JSONDecodeError as e:
                logger.warning(f"Error parsing JSON de horarios: {e}")
            except Exception as e:
                logger.error(f"Error inesperado en búsqueda de horarios: {e}", exc_info=True)
    
    if tipo_consulta == 'cita':
        logger.info("🔑 [PRIORIDAD 1] Consultando tabla estructurada: citas")
        
        result = await consultar_citas_sql(contact_id)
        
        try:
            if "No se encontraron" not in result:
                logger.info(f"✅ Citas encontradas en SQL")
                return {
                    **state,
                    'retrieved_context': result,
                    'fuente': 'sql_estructurado',
                    'confidence': 1.0,
                    'metadata': {
                        **state.get('metadata', {}),
                        'tipo_consulta': tipo_consulta,
                        'tabla': 'citas',
                        'contact_id': contact_id
                    }
                }
        except json.JSONDecodeError as e:
            logger.warning(f"Error parsing resultado de citas: {e}")
        except Exception as e:
            logger.error(f"Error inesperado en consulta de citas: {e}", exc_info=True)
    
    # ========================================================================
    # PASO 3: PRIORIDAD 2 - Knowledge Base Validada (pgvector)
    # ========================================================================
    logger.info("🔑 [PRIORIDAD 2] Buscando en knowledge_base_validated")
    
    kb_result = await buscar_knowledge_base_validada(query)
    
    try:
        kb_data = json.loads(kb_result)
        if kb_data.get('encontrado', False) and kb_data.get('confidence', 0) >= 0.85:
            logger.info(f"✅ Match en KB (confidence: {kb_data['confidence']})")
            return {
                **state,
                'retrieved_context': kb_result,
                'fuente': 'knowledge_base_validated',
                'confidence': kb_data['confidence'],
                'metadata': {
                    **state.get('metadata', {}),
                    'tipo_consulta': tipo_consulta,
                    'kb_id': kb_data.get('kb_id'),
                    'categoria': kb_data.get('categoria')
                }
            }
    except json.JSONDecodeError as e:
        logger.warning(f"Error parsing JSON de knowledge base: {e}")
    except KeyError as e:
        logger.debug(f"Clave faltante en resultado de KB: {e}")
    except Exception as e:
        logger.error(f"Error inesperado en búsqueda de KB: {e}", exc_info=True)
    
    # ========================================================================
    # PASO 4: PRIORIDAD 3 - Contexto Conversacional (aislado)
    # ========================================================================
    logger.info(f"🔑 [PRIORIDAD 3] Buscando en conversaciones del contacto {contact_id}")
    
    context_result = await buscar_conversaciones_previas(query, contact_id)
    
    try:
        context_data = json.loads(context_result)
        if context_data.get('encontrado', False):
            conversations = context_data.get('conversaciones', [])
            if conversations:
                best_similarity = conversations[0]['similarity']
                logger.info(f"✅ Contexto conversacional encontrado (similarity: {best_similarity})")
                return {
                    **state,
                    'retrieved_context': context_result,
                    'fuente': 'contexto_conversacional',
                    'confidence': best_similarity,
                    'metadata': {
                        **state.get('metadata', {}),
                        'tipo_consulta': tipo_consulta,
                        'contact_id': contact_id,
                        'conversaciones_ids': [c['conversacion_id'] for c in conversations]
                    }
                }
    except json.JSONDecodeError as e:
        logger.warning(f"Error parsing JSON de conversaciones: {e}")
    except KeyError as e:
        logger.debug(f"Clave faltante en resultado de conversaciones: {e}")
    except Exception as e:
        logger.error(f"Error inesperado en búsqueda de conversaciones: {e}", exc_info=True)
    
    # ========================================================================
    # PASO 5: SI NADA FUNCIONA - Escalar a Humano
    # ========================================================================
    logger.warning(f"⚠️ No se encontró información para: '{query[:50]}...'")
    
    return {
        **state,
        'retrieved_context': "",
        'fuente': 'no_encontrado',
        'confidence': 0.0,
        'debe_escalar': True,
        'escalation_reason': f'No se encontró información para la consulta: "{query}"',
        'metadata': {
            **state.get('metadata', {}),
            'tipo_consulta': tipo_consulta
        }
    }


# ============================================================================
# UTILIDADES
# ============================================================================

async def clasificar_tipo_consulta(query: str) -> str:
    """
    Clasifica el tipo de consulta del usuario.
    
    Returns:
        'servicio', 'precio', 'tratamiento', 'horario', 'disponibilidad', 'cita', 'general'
    """
    query_lower = query.lower()
    
    # Palabras clave por tipo
    keywords = {
        'servicio': ['servicio', 'tratamiento', 'ofrece', 'tratan', 'hacen'],
        'precio': ['precio', 'cuesta', 'costo', 'tarifa', 'cuánto', 'valor'],
        'tratamiento': ['onicomicosis', 'plantillas', 'callos', 'láser', 'uñas'],
        'horario': ['horario', 'hora', 'atienden', 'abierto', 'abren', 'cierran'],
        'disponibilidad': ['disponibilidad', 'disponible', 'cita', 'agendar', 'reservar'],
        'cita': ['mi cita', 'mis citas', 'cita agendada', 'próxima cita']
    }
    
    # Verificar cada tipo
    for tipo, words in keywords.items():
        if any(word in query_lower for word in words):
            return tipo
    
    return 'general'


def extraer_termino_tratamiento(query: str) -> str:
    """
    Extrae término de búsqueda de tratamiento.
    
    Returns:
        Término limpio o cadena vacía
    """
    query_lower = query.lower()
    
    # Quitar palabras comunes
    stop_words = ['cuánto', 'cuesta', 'precio', 'de', 'el', 'la', 'los', 'las', 'un', 'una',
                  'tratamiento', 'servicio', 'para', 'qué', 'es']
    
    words = query_lower.split()
    filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
    
    if filtered_words:
        return filtered_words[0]
    
    return ""


def extraer_dia_semana(query: str) -> int:
    """
    Extrae día de la semana de la consulta.
    
    Returns:
        0-6 (0=Domingo) o None si no se detecta
    """
    query_lower = query.lower()
    
    dias = {
        'domingo': 0,
        'lunes': 1,
        'martes': 2,
        'miércoles': 3,
        'miercoles': 3,
        'jueves': 4,
        'viernes': 5,
        'sábado': 6,
        'sabado': 6
    }
    
    for dia, num in dias.items():
        if dia in query_lower:
            return num
    
    # Si dice "hoy", calcular día actual
    if 'hoy' in query_lower:
        from datetime import datetime
        return datetime.now().weekday() + 1 if datetime.now().weekday() < 6 else 0
    
    return None
