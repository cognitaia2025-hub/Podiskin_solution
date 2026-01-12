"""
Generate Response Node
======================

Genera respuesta usando Claude con System Prompt dinámico que incluye behavior rules.

Referencias:
- https://docs.anthropic.com/claude/docs/system-prompts
- https://docs.langchain.com/oss/python/langchain/chat-models
"""

import logging
from typing import Dict, Any
import os

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

from ..state import AgentState

logger = logging.getLogger(__name__)

# Configuración del modelo
MODEL = os.getenv("AGENT_MODEL", "claude-3-5-sonnet-20241022")
MAX_TOKENS = int(os.getenv("AGENT_MAX_TOKENS", "1024"))


async def node_generate_response(state: AgentState) -> Dict[str, Any]:
    """
    Genera respuesta usando Claude con System Prompt dinámico.
    
    Flujo:
    1. Construir system_prompt con behavior rules
    2. Incluir contexto recuperado
    3. Llamar a Claude
    4. Extraer respuesta
    5. Actualizar state
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con respuesta generada
    """
    message = state.get('message', '')
    retrieved_context = state.get('retrieved_context', '')
    fuente = state.get('fuente', '')
    behavior_rules = state.get('behavior_rules', [])
    
    logger.info(f"🤖 [Generate Response] Generando respuesta (fuente: {fuente})")
    
    try:
        # 1. Construir System Prompt dinámico
        system_prompt = build_system_prompt(state)
        
        # 2. Construir mensaje del usuario
        user_message = f"""Pregunta del paciente: {message}

Contexto recuperado (fuente: {fuente}):
{retrieved_context if retrieved_context else 'No se encontró información específica.'}

Responde de manera natural, profesional y empática."""
        
        # 3. Llamar a Claude
        llm = ChatAnthropic(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=0.7
        )
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = await llm.ainvoke(messages)
        respuesta = response.content
        
        logger.info(f"✅ [Generate Response] Respuesta generada ({len(respuesta)} chars)")
        
        # 4. Actualizar state
        return {
            **state,
            'respuesta_generada': respuesta,
            'metadata': {
                **state.get('metadata', {}),
                'model': MODEL,
                'tokens_used': len(respuesta.split()),
                'system_prompt_length': len(system_prompt)
            }
        }
    
    except Exception as e:
        logger.error(f"❌ [Generate Response] Error generando respuesta: {e}", exc_info=True)
        
        # Fallback: respuesta genérica
        return {
            **state,
            'respuesta_generada': "Disculpe, tengo problemas técnicos temporales. Un miembro de nuestro equipo le responderá pronto.",
            'debe_escalar': True,
            'escalation_reason': f"Error generando respuesta: {str(e)}"
        }


def build_system_prompt(state: AgentState) -> str:
    """
    Construye System Prompt dinámico con behavior rules.
    
    Estructura:
    - Rol del asistente
    - Reglas de comportamiento activas (inyectadas dinámicamente)
    - Contexto recuperado
    - Instrucciones generales
    
    Args:
        state: Estado actual con behavior_rules
        
    Returns:
        System prompt completo
    """
    behavior_rules = state.get('behavior_rules', [])
    retrieved_context = state.get('retrieved_context', '')
    fuente = state.get('fuente', '')
    
    # Sección: Rol
    prompt = """Eres Maya, asistente virtual de Clínica Podoskin, una clínica especializada en podología en Mexicali, Baja California.

Tu objetivo es ayudar a los pacientes con consultas sobre servicios, precios, horarios, citas y procedimientos médicos.

"""
    
    # Sección: Reglas de Comportamiento Activas
    if behavior_rules:
        prompt += "## Reglas de Comportamiento Activas\n\n"
        prompt += "**IMPORTANTE:** Sigue estas reglas en orden de prioridad:\n\n"
        
        for i, rule in enumerate(behavior_rules[:10], 1):  # Top 10 reglas
            prompt += f"{i}. [Prioridad {rule.get('prioridad', 5)}] **{rule.get('pattern', '')}**\n"
            prompt += f"   {rule.get('correction_logic', '')}\n\n"
    
    # Sección: Contexto Recuperado
    if retrieved_context and fuente:
        prompt += f"## Contexto Recuperado\n\n"
        prompt += f"**Fuente:** {fuente}\n\n"
        
        if fuente == 'sql_estructurado':
            prompt += "Los siguientes datos provienen directamente de la base de datos (FUENTE DE VERDAD):\n\n"
        elif fuente == 'knowledge_base_validated':
            prompt += "La siguiente información fue validada por el equipo de la clínica:\n\n"
        elif fuente == 'contexto_conversacional':
            prompt += "Contexto de conversaciones previas con este paciente:\n\n"
        
        prompt += f"```\n{retrieved_context}\n```\n\n"
    
    # Sección: Instrucciones Generales
    prompt += """## Instrucciones Generales

1. **Tono:** Profesional, empático y amigable. Usa español mexicano.
2. **Honestidad:** Si no tienes información, di "No tengo esa información en este momento. Permíteme comunicar a un miembro del equipo para ayudarte."
3. **Precios:** SIEMPRE basar precios en datos de la base de datos. NUNCA inventar precios.
4. **Horarios:** SIEMPRE basar horarios en datos de la base de datos. Los horarios pueden cambiar.
5. **Formato:** Respuestas claras y concisas. Usa emojis con moderación (📅 🕐 💰).
6. **Privacidad:** Nunca compartir información de otros pacientes.

Responde de manera natural y conversacional."""
    
    return prompt
