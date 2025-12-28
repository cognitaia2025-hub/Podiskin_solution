"""
Demo: Integración Completa del Sistema de Voz
Ejemplo de cómo integrar todos los componentes
"""

import asyncio
from datetime import datetime

# ==========================================
# 1. BACKEND SETUP
# ==========================================

# Importar componentes backend
from backend.agents.orchestrator import execute_orchestrator
from backend.agents.summaries import execute_summaries
from backend.api.live_sessions import start_session, stop_session


# ==========================================
# 2. DEMO: FLUJO SIMPLE
# ==========================================

async def demo_simple_flow():
    """
    Demostración de flujo simple:
    update_vital_signs → Endpoint REST directo
    """
    print("\n" + "="*60)
    print("DEMO 1: FLUJO SIMPLE - Actualizar Signos Vitales")
    print("="*60)
    
    # Simular datos
    patient_id = "123"
    appointment_id = "456"
    user_id = "789"
    
    # Tool call de Gemini Live
    tool_call = {
        "name": "update_vital_signs",
        "args": {
            "peso_kg": 75.5,
            "talla_cm": 175,
            "ta_sistolica": 120,
            "ta_diastolica": 80
        }
    }
    
    print(f"\n📱 Usuario dice: 'Peso 75 kilos y medio, talla 175'")
    print(f"\n🔧 Gemini Live detecta tool call:")
    print(f"   Función: {tool_call['name']}")
    print(f"   Args: {tool_call['args']}")
    
    print(f"\n🚀 Frontend → POST /api/citas/{appointment_id}/signos-vitales")
    
    # Simular respuesta
    response = {
        "id": 1,
        "peso_kg": 75.5,
        "talla_cm": 175,
        "imc": 24.65,
        "imc_clasificacion": "Normal",
        "presion_arterial": "120/80"
    }
    
    print(f"\n✅ Backend responde:")
    print(f"   IMC: {response['imc']} ({response['imc_clasificacion']})")
    print(f"   Presión: {response['presion_arterial']}")
    
    print(f"\n🎤 Gemini Live responde:")
    print(f"   'He registrado peso de 75.5 kg y talla de 175 cm.'")
    print(f"   'Su IMC es {response['imc']}, clasificado como {response['imc_clasificacion']}'")
    
    print(f"\n⏱️  Tiempo total: ~500ms")


# ==========================================
# 3. DEMO: FLUJO COMPLEJO
# ==========================================

async def demo_complex_flow():
    """
    Demostración de flujo complejo:
    generate_summary → Orquestador → SubAgente Resúmenes
    """
    print("\n" + "="*60)
    print("DEMO 2: FLUJO COMPLEJO - Generar Resumen")
    print("="*60)
    
    # Simular datos
    patient_id = "123"
    appointment_id = "456"
    user_id = "789"
    
    # Tool call de Gemini Live
    tool_call = {
        "name": "generate_summary",
        "args": {
            "tipo_resumen": "consulta_actual",
            "formato": "breve"
        }
    }
    
    print(f"\n📱 Usuario dice: 'Genera un resumen de la consulta'")
    print(f"\n🔧 Gemini Live detecta tool call:")
    print(f"   Función: {tool_call['name']}")
    print(f"   Args: {tool_call['args']}")
    
    print(f"\n🚀 Frontend → POST /api/orchestrator/execute")
    
    print(f"\n🎯 ORQUESTADOR - Procesando...")
    print(f"   [Nodo 1] classify_query:")
    print(f"            ✓ Función compleja detectada")
    print(f"            ✓ Requiere SubAgente: summaries")
    
    print(f"\n   [Nodo 2] route_to_subagent:")
    print(f"            ✓ Invocando SubAgente Resúmenes...")
    
    print(f"\n      🤖 SUBAGENTE RESÚMENES - Ejecutando...")
    print(f"         [Nodo 1] fetch_patient_data:")
    print(f"                  ✓ Datos del paciente obtenidos")
    print(f"                  ✓ Citas: 1, Notas: 1")
    
    print(f"\n         [Nodo 2] search_history:")
    print(f"                  ⊘ No aplica (es generate_summary)")
    
    print(f"\n         [Nodo 3] generate_summary:")
    print(f"                  ✓ Template cargado: consulta_actual/breve")
    print(f"                  ✓ Resumen generado (450 caracteres)")
    
    print(f"\n         [Nodo 4] validate_summary:")
    print(f"                  ✓ Longitud OK (450 > 50)")
    print(f"                  ✓ Sin datos sensibles")
    print(f"                  ✓ Validación pasada")
    
    print(f"\n         [Nodo 5] build_response:")
    print(f"                  ✓ Respuesta construida")
    
    print(f"\n      🤖 SubAgente retorna resultado (tiempo: 850ms)")
    
    print(f"\n   [Nodo 3] validate_response:")
    print(f"            ✓ Respuesta del SubAgente validada")
    print(f"            ✓ Sin errores de validación")
    
    print(f"\n   [Nodo 4] build_response:")
    print(f"            ✓ Respuesta final construida")
    
    print(f"\n✅ Orquestador responde:")
    
    # Simular respuesta
    response = {
        "data": {
            "content": """## Resumen de Consulta

**Fecha:** 2024-12-20
**Paciente:** Juan Pérez
**Motivo:** Dolor en talón derecho

**Hallazgos:**
Dolor a la palpación de fascia plantar

**Plan:**
Plantillas ortopédicas, antiinflamatorios""",
            "sections": {
                "tipo": "consulta_actual",
                "formato": "breve"
            }
        },
        "message": "Resumen generado exitosamente",
        "status": "success",
        "execution_time_ms": 1250
    }
    
    print(f"   Status: {response['status']}")
    print(f"   Tiempo: {response['execution_time_ms']}ms")
    print(f"\n   Contenido:")
    for line in response['data']['content'].split('\n'):
        print(f"   {line}")
    
    print(f"\n🎤 Gemini Live responde:")
    print(f"   'He generado el resumen de la consulta.'")
    print(f"   'Puedes verlo en la pantalla.'")
    
    print(f"\n⏱️  Tiempo total: ~{response['execution_time_ms']}ms")


# ==========================================
# 4. DEMO: CÓDIGO REAL
# ==========================================

async def demo_real_execution():
    """
    Ejecución real del orquestador y subagente
    (Requiere que el código esté instalado)
    """
    print("\n" + "="*60)
    print("DEMO 3: EJECUCIÓN REAL")
    print("="*60)
    
    try:
        # Ejecutar orquestador con función compleja
        print(f"\n🚀 Ejecutando generate_summary...")
        
        result = await execute_orchestrator(
            function_name="generate_summary",
            args={
                "tipo_resumen": "consulta_actual",
                "formato": "breve"
            },
            patient_id="123",
            user_id="789",
            appointment_id="456"
        )
        
        print(f"\n✅ Resultado:")
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        print(f"   Execution Time: {result.get('execution_time_ms')}ms")
        
        if result['status'] == 'success':
            print(f"\n   Contenido generado:")
            content = result['data'].get('content', '')
            for line in content.split('\n')[:10]:  # Primeras 10 líneas
                print(f"   {line}")
        
        print(f"\n📝 Logs de ejecución:")
        for msg in result.get('messages', [])[:5]:
            print(f"   • {msg}")
        
        print(f"\n📊 Audit Log:")
        for entry in result.get('audit_log', [])[:3]:
            print(f"   • {entry['step']}: {entry.get('success', 'N/A')}")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print(f"   (Normal si el backend no está corriendo)")


# ==========================================
# 5. DEMO: BÚSQUEDA SEMÁNTICA
# ==========================================

async def demo_search_flow():
    """
    Demostración de búsqueda semántica en historial
    """
    print("\n" + "="*60)
    print("DEMO 4: BÚSQUEDA SEMÁNTICA")
    print("="*60)
    
    print(f"\n📱 Usuario dice: '¿Cuándo tratamos hongos en las uñas?'")
    
    tool_call = {
        "name": "search_patient_history",
        "args": {
            "query": "tratamientos hongos uñas",
            "limite_resultados": 5
        }
    }
    
    print(f"\n🔧 Gemini Live detecta tool call:")
    print(f"   Función: {tool_call['name']}")
    print(f"   Query: {tool_call['args']['query']}")
    
    print(f"\n🚀 Frontend → POST /api/orchestrator/execute")
    print(f"\n🎯 Orquestador → SubAgente Resúmenes")
    print(f"\n   🔍 Búsqueda semántica en progreso...")
    print(f"      • Generando embedding del query")
    print(f"      • Consultando pgvector")
    print(f"      • Rankeando por similitud")
    
    # Simular resultados
    results = [
        {
            "fecha": "2024-11-15",
            "tipo": "nota_clinica",
            "contenido": "Tratamiento para onicomicosis en uña del pie derecho",
            "relevancia": 0.85
        },
        {
            "fecha": "2024-09-20",
            "tipo": "tratamiento",
            "contenido": "Aplicación de láser para hongos en uñas",
            "relevancia": 0.78
        },
        {
            "fecha": "2024-07-10",
            "tipo": "consulta",
            "contenido": "Seguimiento de tratamiento onicomicosis",
            "relevancia": 0.72
        }
    ]
    
    print(f"\n✅ Resultados encontrados: {len(results)}")
    for i, result in enumerate(results, 1):
        print(f"\n   {i}. {result['fecha']} ({result['tipo']}) - Score: {result['relevancia']}")
        print(f"      {result['contenido']}")
    
    print(f"\n🎤 Gemini Live responde:")
    print(f"   'Encontré 3 tratamientos relacionados con hongos en las uñas.'")
    print(f"   'El más reciente fue en noviembre de 2024, tratamiento para onicomicosis.'")
    print(f"   'En septiembre aplicamos láser para hongos.'")


# ==========================================
# 6. MAIN
# ==========================================

async def main():
    """Run all demos"""
    print("\n" + "="*70)
    print(" "*15 + "SISTEMA DE VOZ PODOSKIN")
    print(" "*10 + "Gemini Live + Orquestador + SubAgentes")
    print("="*70)
    
    # Demo 1: Flujo Simple
    await demo_simple_flow()
    await asyncio.sleep(1)
    
    # Demo 2: Flujo Complejo
    await demo_complex_flow()
    await asyncio.sleep(1)
    
    # Demo 4: Búsqueda Semántica
    await demo_search_flow()
    await asyncio.sleep(1)
    
    # Demo 3: Ejecución Real (comentado por defecto)
    # await demo_real_execution()
    
    print("\n" + "="*70)
    print(" "*25 + "FIN DE DEMOS")
    print("="*70)
    print("\n💡 Para ejecutar con código real:")
    print("   1. Instalar dependencias: pip install -r backend/requirements.txt")
    print("   2. Configurar .env con DATABASE_URL y GEMINI_API_KEY")
    print("   3. Descomentar demo_real_execution() en main()")
    print("   4. Ejecutar: python demo_integration.py")
    print()


if __name__ == "__main__":
    asyncio.run(main())
