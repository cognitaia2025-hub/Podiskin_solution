"""
Demo: Integración Completa del Sistema de Voz
Demostración visual sin dependencias
"""

import asyncio


async def print_with_delay(text, delay=0.3):
    """Print text with delay for visual effect"""
    print(text)
    await asyncio.sleep(delay)


async def demo_simple_flow():
    """
    Demostración de flujo simple:
    update_vital_signs → Endpoint REST directo
    """
    print("\n" + "="*60)
    print("DEMO 1: FLUJO SIMPLE - Actualizar Signos Vitales")
    print("="*60)
    await asyncio.sleep(0.5)
    
    await print_with_delay("\n📱 Usuario dice: 'Peso 75 kilos y medio, talla 175'")
    
    await print_with_delay("\n🔧 Gemini Live detecta tool call:")
    await print_with_delay("   Función: update_vital_signs")
    await print_with_delay("   Args: {peso_kg: 75.5, talla_cm: 175, ta_sistolica: 120, ta_diastolica: 80}")
    
    await print_with_delay("\n🚀 Frontend → POST /api/citas/456/signos-vitales")
    await print_with_delay("   Body: {peso_kg: 75.5, talla_cm: 175, ...}")
    
    await print_with_delay("\n💾 Backend → Database UPDATE")
    await print_with_delay("   INSERT INTO signos_vitales (...)")
    await print_with_delay("   Calculando IMC: 75.5 / (1.75)² = 24.65")
    
    await print_with_delay("\n✅ Backend responde (200 OK):")
    await print_with_delay("   {")
    await print_with_delay("     id: 1,")
    await print_with_delay("     peso_kg: 75.5,")
    await print_with_delay("     talla_cm: 175,")
    await print_with_delay("     imc: 24.65,")
    await print_with_delay("     imc_clasificacion: 'Normal',")
    await print_with_delay("     presion_arterial: '120/80'")
    await print_with_delay("   }")
    
    await print_with_delay("\n🎤 Gemini Live responde (audio):")
    await print_with_delay("   'He registrado peso de 75.5 kg y talla de 175 cm.'")
    await print_with_delay("   'Su IMC es 24.65, clasificado como Normal'")
    
    await print_with_delay("\n⏱️  Tiempo total: ~500ms", 0.5)


async def demo_complex_flow():
    """
    Demostración de flujo complejo:
    generate_summary → Orquestador → SubAgente Resúmenes
    """
    print("\n" + "="*60)
    print("DEMO 2: FLUJO COMPLEJO - Generar Resumen")
    print("="*60)
    await asyncio.sleep(0.5)
    
    await print_with_delay("\n📱 Usuario dice: 'Genera un resumen de la consulta'")
    
    await print_with_delay("\n🔧 Gemini Live detecta tool call:")
    await print_with_delay("   Función: generate_summary")
    await print_with_delay("   Args: {tipo_resumen: 'consulta_actual', formato: 'breve'}")
    
    await print_with_delay("\n🚀 Frontend → POST /api/orchestrator/execute")
    
    print("\n" + "-"*60)
    await print_with_delay("🎯 AGENTE PADRE ORQUESTADOR - Procesando...")
    print("-"*60)
    
    await print_with_delay("\n   [Nodo 1] classify_query:")
    await print_with_delay("            ✓ Función: generate_summary")
    await print_with_delay("            ✓ Tipo: COMPLEJA (requiere SubAgente)")
    await print_with_delay("            ✓ Target: summaries")
    await print_with_delay("            ✓ Complexity Score: 0.8")
    
    await print_with_delay("\n   [Nodo 2] route_to_subagent:")
    await print_with_delay("            ✓ SubAgente configurado: summaries")
    await print_with_delay("            ✓ Preparando request para SubAgente...")
    await print_with_delay("            ✓ Invocando SubAgente Resúmenes...")
    
    print("\n" + " "*6 + "-"*50)
    await print_with_delay(" "*6 + "🤖 SUBAGENTE RESÚMENES - Ejecutando...")
    print(" "*6 + "-"*50)
    
    await print_with_delay("\n         [Nodo 1] fetch_patient_data:")
    await print_with_delay("                  ✓ Consultando paciente ID 123...")
    await print_with_delay("                  ✓ Datos del paciente obtenidos")
    await print_with_delay("                  ✓ Citas encontradas: 1")
    await print_with_delay("                  ✓ Notas clínicas: 1")
    await print_with_delay("                  ✓ Signos vitales: 1")
    
    await print_with_delay("\n         [Nodo 2] search_history:")
    await print_with_delay("                  ⊘ No aplica (función es generate_summary)")
    await print_with_delay("                  ⊘ Saltando nodo...")
    
    await print_with_delay("\n         [Nodo 3] generate_summary:")
    await print_with_delay("                  ✓ Template: consulta_actual/breve")
    await print_with_delay("                  ✓ Preparando datos para LLM...")
    await print_with_delay("                  ✓ Llamada a LLM (Claude Haiku)...")
    await print_with_delay("                  ✓ Resumen generado: 450 caracteres")
    
    await print_with_delay("\n         [Nodo 4] validate_summary:")
    await print_with_delay("                  ✓ Verificando longitud: 450 > 50 ✓")
    await print_with_delay("                  ✓ Verificando longitud: 450 < 5000 ✓")
    await print_with_delay("                  ✓ Sin contenido vacío ✓")
    await print_with_delay("                  ✓ Sin datos sensibles ✓")
    await print_with_delay("                  ✓ Validación PASADA")
    
    await print_with_delay("\n         [Nodo 5] build_response:")
    await print_with_delay("                  ✓ Formateando respuesta...")
    await print_with_delay("                  ✓ Status: success")
    await print_with_delay("                  ✓ Tiempo de ejecución: 850ms")
    
    print("\n" + " "*6 + "-"*50)
    await print_with_delay(" "*6 + "🤖 SubAgente retorna resultado")
    print(" "*6 + "-"*50)
    
    await print_with_delay("\n   [Nodo 3] validate_response:")
    await print_with_delay("            ✓ Respuesta del SubAgente recibida")
    await print_with_delay("            ✓ Status: success")
    await print_with_delay("            ✓ Sin errores de validación")
    await print_with_delay("            ✓ Validación PASADA")
    
    await print_with_delay("\n   [Nodo 4] build_response:")
    await print_with_delay("            ✓ Construyendo respuesta final...")
    await print_with_delay("            ✓ Agregando metadata")
    await print_with_delay("            ✓ Agregando audit log")
    await print_with_delay("            ✓ Respuesta lista")
    
    print("\n" + "-"*60)
    await print_with_delay("🎯 Orquestador completado")
    print("-"*60)
    
    await print_with_delay("\n✅ Backend responde (200 OK):")
    await print_with_delay("   {")
    await print_with_delay("     status: 'success',")
    await print_with_delay("     message: 'Resumen generado exitosamente',")
    await print_with_delay("     execution_time_ms: 1250,")
    await print_with_delay("     data: {")
    await print_with_delay("       content: '## Resumen de Consulta...',")
    await print_with_delay("       sections: {...},")
    await print_with_delay("       metadata: {...}")
    await print_with_delay("     }")
    await print_with_delay("   }")
    
    await print_with_delay("\n📄 Resumen generado:")
    await print_with_delay("   ┌─────────────────────────────────────────┐")
    await print_with_delay("   │ ## Resumen de Consulta                  │")
    await print_with_delay("   │                                         │")
    await print_with_delay("   │ **Fecha:** 2024-12-20                   │")
    await print_with_delay("   │ **Paciente:** Juan Pérez                │")
    await print_with_delay("   │ **Motivo:** Dolor en talón derecho      │")
    await print_with_delay("   │                                         │")
    await print_with_delay("   │ **Hallazgos:**                          │")
    await print_with_delay("   │ Dolor a la palpación de fascia plantar  │")
    await print_with_delay("   │                                         │")
    await print_with_delay("   │ **Plan:**                               │")
    await print_with_delay("   │ Plantillas ortopédicas,                 │")
    await print_with_delay("   │ antiinflamatorios                       │")
    await print_with_delay("   └─────────────────────────────────────────┘")
    
    await print_with_delay("\n🎤 Gemini Live responde (audio):")
    await print_with_delay("   'He generado el resumen de la consulta.'")
    await print_with_delay("   'Puedes verlo en la pantalla.'")
    
    await print_with_delay("\n⏱️  Tiempo total: ~1250ms", 0.5)


async def demo_search_flow():
    """
    Demostración de búsqueda semántica en historial
    """
    print("\n" + "="*60)
    print("DEMO 3: BÚSQUEDA SEMÁNTICA - Historial del Paciente")
    print("="*60)
    await asyncio.sleep(0.5)
    
    await print_with_delay("\n📱 Usuario dice: '¿Cuándo tratamos hongos en las uñas?'")
    
    await print_with_delay("\n🔧 Gemini Live detecta tool call:")
    await print_with_delay("   Función: search_patient_history")
    await print_with_delay("   Args: {query: 'tratamientos hongos uñas', limite: 5}")
    
    await print_with_delay("\n🚀 Frontend → POST /api/orchestrator/execute")
    await print_with_delay("\n🎯 Orquestador → SubAgente Resúmenes")
    
    await print_with_delay("\n   🔍 Búsqueda semántica en progreso...")
    await print_with_delay("      • Generando embedding del query...")
    await print_with_delay("      • Modelo: all-MiniLM-L6-v2")
    await print_with_delay("      • Vector: [0.123, -0.456, 0.789, ...]")
    await print_with_delay("      • Consultando pgvector...")
    await print_with_delay("      • Query: SELECT * FROM historial_embeddings")
    await print_with_delay("      •        WHERE patient_id = 123")
    await print_with_delay("      •        ORDER BY embedding <=> query_vector")
    await print_with_delay("      • Rankeando por similitud coseno...")
    
    await print_with_delay("\n✅ Resultados encontrados: 3")
    await print_with_delay("\n   1. 📅 2024-11-15 (nota_clinica) - Score: 0.85")
    await print_with_delay("      'Tratamiento para onicomicosis en uña del pie derecho'")
    
    await print_with_delay("\n   2. 📅 2024-09-20 (tratamiento) - Score: 0.78")
    await print_with_delay("      'Aplicación de láser para hongos en uñas'")
    
    await print_with_delay("\n   3. 📅 2024-07-10 (consulta) - Score: 0.72")
    await print_with_delay("      'Seguimiento de tratamiento onicomicosis'")
    
    await print_with_delay("\n🎤 Gemini Live responde (audio):")
    await print_with_delay("   'Encontré 3 tratamientos relacionados con hongos.'")
    await print_with_delay("   'El más reciente fue en noviembre 2024,")
    await print_with_delay("    tratamiento para onicomicosis.'")
    await print_with_delay("   'En septiembre aplicamos láser.'")
    
    await print_with_delay("\n⏱️  Tiempo total: ~980ms", 0.5)


async def main():
    """Run all demos"""
    print("\n" + "="*70)
    print(" "*15 + "SISTEMA DE VOZ PODOSKIN")
    print(" "*10 + "Gemini Live + Orquestador + SubAgentes")
    print("="*70)
    await asyncio.sleep(1)
    
    # Demo 1: Flujo Simple
    await demo_simple_flow()
    await asyncio.sleep(2)
    
    # Demo 2: Flujo Complejo
    await demo_complex_flow()
    await asyncio.sleep(2)
    
    # Demo 3: Búsqueda Semántica
    await demo_search_flow()
    await asyncio.sleep(1)
    
    print("\n" + "="*70)
    print(" "*25 + "FIN DE DEMOS")
    print("="*70)
    
    print("\n📊 RESUMEN DE ARQUITECTURA:")
    print("\n   Frontend (TypeScript/React):")
    print("   ├─ VoiceController.tsx      - UI principal")
    print("   ├─ SecureLiveManager.ts     - Gemini Live + seguridad")
    print("   ├─ SecureSession.ts         - Tokens efímeros")
    print("   └─ audioUtils.ts            - Resampling 16kHz PCM16")
    
    print("\n   Backend API (FastAPI/Python):")
    print("   ├─ /api/live/session/*      - Gestión de sesiones")
    print("   └─ /api/orchestrator/execute - Endpoint del orquestador")
    
    print("\n   Agente Padre Orquestador:")
    print("   ├─ classify_query           - Clasificar simple/compleja")
    print("   ├─ route_to_subagent        - Delegar a SubAgente")
    print("   ├─ validate_response        - Validar respuesta")
    print("   └─ build_response           - Construir respuesta final")
    
    print("\n   SubAgente Resúmenes:")
    print("   ├─ fetch_patient_data       - Obtener datos de DB")
    print("   ├─ search_history           - Búsqueda semántica")
    print("   ├─ generate_summary         - Generar con LLM")
    print("   ├─ validate_summary         - Validar calidad")
    print("   └─ build_response           - Formatear respuesta")
    
    print("\n💡 Funciones Médicas:")
    print("   Simples (6):  update_vital_signs, create_clinical_note,")
    print("                 query_patient_data, add_allergy,")
    print("                 navigate_to_section, schedule_followup")
    print("   Complejas (2): search_patient_history, generate_summary")
    
    print("\n🔒 Seguridad:")
    print("   ✓ API keys en backend")
    print("   ✓ Tokens efímeros (TTL: 1 hora)")
    print("   ✓ Auto-refresh antes de expirar")
    print("   ✓ Validación en cada request")
    print("   ✓ Audit logs completos")
    
    print("\n📚 Documentación:")
    print("   • Frontend/src/voice/README.md")
    print("   • backend/agents/orchestrator/README.md")
    print("   • backend/agents/summaries/README.md")
    print("   • VOICE_ARCHITECTURE.md")
    print()


if __name__ == "__main__":
    asyncio.run(main())
