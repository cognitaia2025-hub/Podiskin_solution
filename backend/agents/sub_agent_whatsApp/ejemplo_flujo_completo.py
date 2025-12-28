"""
Ejemplo de Uso Completo - SubAgente WhatsApp con Patrones LangGraph
===================================================================

Este ejemplo demuestra los flujos completos implementados:
1. Flujo normal: mensaje → FAQ hit → respuesta
2. Flujo escalado: mensaje → no FAQ → ticket → interrupt → resume → aprende

NOTA: Este es un ejemplo didáctico con mocks. Para uso real se necesita:
- BD PostgreSQL configurada
- API key de Anthropic
- Variables de entorno correctas
"""

import asyncio
from datetime import datetime
from typing import Dict

# ============================================================================
# EJEMPLO 1: Flujo Normal - FAQ Hit
# ============================================================================


async def ejemplo_flujo_normal():
    """
    Demuestra el flujo cuando hay un FAQ match.
    
    Usuario pregunta → Se busca en KB → Se encuentra → Se responde
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 1: Flujo Normal con FAQ Hit")
    print("=" * 70 + "\n")
    
    # Simular que tenemos la FAQ en la base
    print("📚 Knowledge Base contiene:")
    print("  Q: ¿Cuánto cuesta el tratamiento de hongos?")
    print("  A: Ofrecemos tratamiento de onicomicosis por $800 MXN")
    print()
    
    # Usuario hace una pregunta similar
    user_question = "¿Qué precio tiene el tratamiento para hongos en las uñas?"
    print(f"👤 Usuario: {user_question}")
    print()
    
    # El agente busca en KB y encuentra match
    print("🤖 Agente:")
    print("  1. Clasificando intención... → consulta (confidence: 0.95)")
    print("  2. Buscando en knowledge base...")
    print("     - Generando embedding de la pregunta")
    print("     - Comparando con embeddings en BD")
    print("     - Match encontrado! (similarity: 0.91)")
    print("  3. Generando respuesta...")
    print()
    
    response = "Ofrecemos tratamiento de onicomicosis por $800 MXN. ¿Le gustaría agendar una cita?"
    print(f"💬 Respuesta: {response}")
    print()
    
    print("✅ Flujo completado sin escalamiento")
    print("   - No se creó ticket")
    print("   - No se requirió intervención humana")
    print("   - Se incrementó contador de veces_consultada en KB")


# ============================================================================
# EJEMPLO 2: Flujo Escalado Completo
# ============================================================================


async def ejemplo_flujo_escalado():
    """
    Demuestra el flujo completo de escalamiento con interrupt/resume.
    
    Usuario pregunta → No hay FAQ → Escalar → interrupt() → 
    [Espera admin] → Admin responde → resume() → save_faq() → Responde al usuario
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Flujo Escalado con Interrupt/Resume")
    print("=" * 70 + "\n")
    
    # Usuario hace una pregunta que no está en FAQ
    user_question = "¿Hacen cirugía de juanetes?"
    print(f"👤 Usuario: {user_question}")
    print()
    
    # El agente intenta responder pero no encuentra información
    print("🤖 Agente:")
    print("  1. Clasificando intención... → consulta (confidence: 0.92)")
    print("  2. Buscando en knowledge base...")
    print("     - Generando embedding")
    print("     - Buscando matches...")
    print("     - ❌ No se encontró respuesta similar (best: 0.65 < threshold 0.85)")
    print("  3. Generando respuesta...")
    print("     - Confianza baja en respuesta")
    print("     - ⚠️  Detectada necesidad de escalamiento")
    print()
    
    print("📋 Creando ticket de escalamiento:")
    print("  - Guardando en tabla dudas_pendientes")
    print("  - ticket_id = 456")
    print("  - estado = 'pendiente'")
    print("  - pregunta = '¿Hacen cirugía de juanetes?'")
    print()
    
    print("📧 Notificando al administrador:")
    print("  WhatsApp → Admin (+52 686-108-3647)")
    print("  Mensaje:")
    print("    🔔 DUDA #456")
    print("    Paciente: Juan Pérez (+52 331-234-5678)")
    print("    Pregunta: ¿Hacen cirugía de juanetes?")
    print("    Responder con: #RESPUESTA_456 [tu respuesta]")
    print()
    
    print("💬 Respuesta al paciente:")
    response = "Disculpe, no tengo esa información pero déjeme consultarlo con el personal..."
    print(f"  {response}")
    print()
    
    print("⏸️  INTERRUPT EJECUTADO:")
    print("  - interrupt('waiting_admin_response:456')")
    print("  - Estado guardado en checkpointer")
    print("  - Grafo pausado en nodo: post_process_escalation")
    print("  - processing_stage = 'waiting_admin'")
    print("  - escalation_ticket_id = 456")
    print()
    
    print("⏳ Esperando respuesta del administrador...")
    print("   (puede ser minutos, horas o días)")
    print()
    
    # Simular que pasa el tiempo y el admin responde
    await asyncio.sleep(1)  # Simulando el tiempo de espera
    
    print("=" * 70)
    print("⏰ [2 horas después]")
    print("=" * 70)
    print()
    
    print("👨‍💼 Admin responde:")
    admin_reply = "No, no realizamos cirugías. Solo tratamientos conservadores de podología."
    print(f"  {admin_reply}")
    print()
    
    print("📡 Backend recibe respuesta del admin:")
    print("  1. Actualiza tabla dudas_pendientes:")
    print("     UPDATE dudas_pendientes")
    print(f"     SET respuesta = '{admin_reply[:40]}...'")
    print("         estado = 'respondida'")
    print("         fecha_respuesta = NOW()")
    print("     WHERE id = 456")
    print()
    
    print("▶️  REANUDANDO GRAFO:")
    print("  - Llamando a resume_agent_with_admin_reply()")
    print("  - thread_id = 'conv_12345'")
    print(f"  - admin_reply = '{admin_reply[:40]}...'")
    print("  - ticket_id = 456")
    print()
    
    print("🤖 Agente reanuda procesamiento:")
    print("  1. Estado recuperado del checkpointer")
    print("  2. Procesando respuesta del admin en post_process_escalation")
    print("  3. Guardando en knowledge base (APRENDIZAJE):")
    print("     - Pregunta: '¿Hacen cirugía de juanetes?'")
    print(f"     - Respuesta: '{admin_reply[:40]}...'")
    print("     - Generando embedding y guardando en pgvector")
    print("     - kb_id = 789")
    print("     - validado = TRUE")
    print("  4. Actualizando dudas_pendientes:")
    print("     - aprendida = TRUE")
    print("     - fecha_aprendizaje = NOW()")
    print("  5. Registrando en audit_logs:")
    print("     - accion = 'resume_after_admin'")
    print("     - detalles = 'Reanudado después de respuesta admin (ticket #456)'")
    print()
    
    print("💬 Respuesta final al paciente:")
    print(f"  {admin_reply}")
    print()
    
    print("✅ Flujo completado exitosamente!")
    print("   - ✓ Ticket #456 resuelto")
    print("   - ✓ FAQ aprendida (kb_id: 789)")
    print("   - ✓ Auditoría completa")
    print("   - ✓ Próxima vez → respuesta automática")


# ============================================================================
# EJEMPLO 3: Próxima Consulta Similar (Después del Aprendizaje)
# ============================================================================


async def ejemplo_despues_aprendizaje():
    """
    Demuestra que después del aprendizaje, preguntas similares
    se responden automáticamente.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Consulta Similar Después del Aprendizaje")
    print("=" * 70 + "\n")
    
    print("📚 Knowledge Base ahora contiene (aprendido de ticket #456):")
    print("  Q: ¿Hacen cirugía de juanetes?")
    print("  A: No, no realizamos cirugías. Solo tratamientos conservadores...")
    print()
    
    # Otro usuario hace una pregunta similar
    user_question = "¿Operan juanetes?"
    print(f"👤 Usuario (diferente): {user_question}")
    print()
    
    print("🤖 Agente:")
    print("  1. Clasificando intención... → consulta (confidence: 0.94)")
    print("  2. Buscando en knowledge base...")
    print("     - Generando embedding")
    print("     - Comparando con KB (incluyendo FAQ aprendida)")
    print("     - ✅ Match encontrado! (similarity: 0.89)")
    print("     - Usando respuesta aprendida del ticket #456")
    print("  3. Generando respuesta...")
    print()
    
    response = "No, no realizamos cirugías. Solo tratamientos conservadores de podología."
    print(f"💬 Respuesta: {response}")
    print()
    
    print("✅ Flujo completado sin escalamiento")
    print("   - Respuesta automática gracias al aprendizaje previo")
    print("   - No se creó nuevo ticket")
    print("   - No se requirió intervención humana")
    print("   - El sistema aprendió de la experiencia anterior")


# ============================================================================
# EJEMPLO 4: Código Real (Pseudo-código)
# ============================================================================


async def ejemplo_codigo_real():
    """
    Muestra cómo se usaría el código real (con imports reales).
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 4: Código Real de Uso")
    print("=" * 70 + "\n")
    
    codigo = """
# ============================================================================
# Iniciar Nueva Conversación
# ============================================================================
from backend.agents.sub_agent_whatsApp.graph import run_agent
from backend.agents.sub_agent_whatsApp.state import create_initial_state

# Crear estado inicial
state = create_initial_state(
    conversation_id="conv_12345",
    contact_id=1,
    whatsapp_number="+523311234567",
    contact_name="Juan Pérez",
    message="¿Hacen cirugía de juanetes?"
)

# Ejecutar agente (con persistencia)
result = await run_agent(state, thread_id="conv_12345")

# Si se escaló, el grafo se pausó con interrupt()
# Estado quedó guardado en checkpointer esperando respuesta del admin


# ============================================================================
# Cuando Admin Responde (horas/días después)
# ============================================================================
from backend.agents.sub_agent_whatsApp.graph import resume_agent_with_admin_reply

# Backend recibe respuesta del admin (vía webhook, UI, etc.)
admin_reply = "No, no realizamos cirugías. Solo tratamientos conservadores."
ticket_id = 456

# Reanudar el grafo
result = await resume_agent_with_admin_reply(
    thread_id="conv_12345",
    admin_reply=admin_reply,
    ticket_id=ticket_id
)

# El grafo:
# 1. Envía la respuesta al paciente
# 2. Guarda Q&A en knowledge_base (aprendizaje)
# 3. Registra auditoría completa
# 4. Completa el flujo


# ============================================================================
# Verificar Estado de un Thread
# ============================================================================
from backend.agents.sub_agent_whatsApp.graph import get_agent_state

state = await get_agent_state(thread_id="conv_12345")

if state and state.get("processing_stage") == "waiting_admin":
    ticket_id = state.get("escalation_ticket_id")
    print(f"Thread pausado esperando admin (ticket #{ticket_id})")
"""
    
    print("Código de ejemplo:")
    print(codigo)


# ============================================================================
# MAIN
# ============================================================================


async def main():
    """Ejecuta todos los ejemplos."""
    print("\n" + "=" * 70)
    print("DEMOSTRACIÓN: SubAgente WhatsApp con Patrones LangGraph")
    print("=" * 70)
    print()
    print("Este script demuestra los flujos implementados:")
    print("1. Flujo normal con FAQ hit")
    print("2. Flujo escalado con interrupt/resume")
    print("3. Consulta similar después del aprendizaje")
    print("4. Código real de uso")
    print()
    
    await ejemplo_flujo_normal()
    await asyncio.sleep(2)
    
    await ejemplo_flujo_escalado()
    await asyncio.sleep(2)
    
    await ejemplo_despues_aprendizaje()
    await asyncio.sleep(2)
    
    await ejemplo_codigo_real()
    
    print("\n" + "=" * 70)
    print("✨ DEMOSTRACIÓN COMPLETA")
    print("=" * 70)
    print()
    print("📖 Para más información, ver:")
    print("  - backend/agents/sub_agent_whatsApp/PATRONES_LANGGRAPH.md")
    print("  - backend/agents/sub_agent_whatsApp/README.md")
    print()
    print("🧪 Para ejecutar tests:")
    print("  pytest backend/agents/sub_agent_whatsApp/tests/ -v")
    print()


if __name__ == "__main__":
    asyncio.run(main())
