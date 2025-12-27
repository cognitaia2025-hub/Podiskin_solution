"""
Ejemplo de Uso SIN Base de Datos
================================

Prueba el agente de WhatsApp sin necesidad de PostgreSQL.
"""

import asyncio
import logging
from agents.sub_agent_whatsApp.state import create_initial_state
from agents.sub_agent_whatsApp.config import config

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_classification():
    """Prueba la clasificación de intenciones."""
    from langchain_anthropic import ChatAnthropic
    from agents.sub_agent_whatsApp.config import SYSTEM_PROMPT_CLASSIFIER
    import json

    llm = ChatAnthropic(
        model=config.llm_model,
        temperature=config.classifier_temperature,
        max_tokens=config.classifier_max_tokens,
    )

    test_messages = [
        "Hola, quiero agendar una cita para mañana a las 2pm",
        "¿Cuánto cuestan las plantillas ortopédicas?",
        "Necesito cancelar mi cita del viernes",
        "¿A qué hora abren?",
        "Me duele mucho el pie, es urgente",
        "Gracias por la atención",
    ]

    print("\n" + "=" * 70)
    print("PRUEBA DE CLASIFICACIÓN DE INTENCIONES")
    print("=" * 70 + "\n")

    for msg in test_messages:
        prompt = f"{SYSTEM_PROMPT_CLASSIFIER}\n\nMensaje del usuario: {msg}"

        try:
            response = await llm.ainvoke(prompt)
            content = response.content

            # Intentar parsear JSON
            try:
                # Buscar JSON en la respuesta
                start = content.find("{")
                end = content.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = content[start:end]
                    result = json.loads(json_str)
                    intent = result.get("intent", "desconocido")
                    confidence = result.get("confidence", 0)
                    print(f"📩 '{msg[:40]}...'")
                    print(f"   → Intención: {intent} (confianza: {confidence})")
                    print()
            except json.JSONDecodeError:
                print(f"📩 '{msg[:40]}...'")
                print(f"   → Respuesta: {content[:100]}...")
                print()

        except Exception as e:
            print(f"❌ Error: {e}")

    print("=" * 70 + "\n")


async def test_response_generation():
    """Prueba la generación de respuestas."""
    from langchain_anthropic import ChatAnthropic
    from agents.sub_agent_whatsApp.config import SYSTEM_PROMPT_MAIN

    llm = ChatAnthropic(
        model=config.llm_model,
        temperature=config.llm_temperature,
        max_tokens=config.llm_max_tokens,
    )

    test_scenarios = [
        {
            "intent": "agendar",
            "message": "Quiero una cita para mañana",
            "context": "El paciente Juan Pérez está preguntando por primera vez.",
        },
        {
            "intent": "consulta",
            "message": "¿Cuánto cuestan las plantillas?",
            "context": "Paciente nuevo interesado en plantillas ortopédicas.",
        },
        {
            "intent": "info",
            "message": "¿Cuál es su dirección?",
            "context": "El paciente quiere visitar la clínica.",
        },
    ]

    print("\n" + "=" * 70)
    print("PRUEBA DE GENERACIÓN DE RESPUESTAS")
    print("=" * 70 + "\n")

    for scenario in test_scenarios:
        prompt = f"""{SYSTEM_PROMPT_MAIN}

Contexto: {scenario['context']}
Intención detectada: {scenario['intent']}

Mensaje del usuario: {scenario['message']}

Genera una respuesta apropiada:"""

        try:
            response = await llm.ainvoke(prompt)
            print(f"📩 Usuario: {scenario['message']}")
            print(f"🎯 Intención: {scenario['intent']}")
            print(f"🤖 Respuesta: {response.content}")
            print("-" * 50)
            print()

        except Exception as e:
            print(f"❌ Error: {e}")

    print("=" * 70 + "\n")


async def test_embeddings():
    """Prueba el servicio de embeddings."""
    from agents.sub_agent_whatsApp.utils.embeddings import get_embeddings_service

    print("\n" + "=" * 70)
    print("PRUEBA DE EMBEDDINGS")
    print("=" * 70 + "\n")

    test_texts = [
        "Quiero agendar una cita",
        "¿Cuánto cuesta la consulta?",
        "Me duele el pie derecho",
    ]

    embeddings_service = get_embeddings_service()

    for text in test_texts:
        try:
            embedding = embeddings_service.embed_query(text)
            print(f"📝 Texto: '{text}'")
            print(f"   → Dimensiones: {len(embedding)}")
            print(f"   → Primeros 5 valores: {embedding[:5]}")
            print()
        except Exception as e:
            print(f"❌ Error: {e}")

    print("=" * 70 + "\n")


async def test_state():
    """Prueba la creación de estado."""
    print("\n" + "=" * 70)
    print("PRUEBA DE ESTADO")
    print("=" * 70 + "\n")

    state = create_initial_state(
        conversation_id="test-123",
        contact_id=1,
        whatsapp_number="+523331234567",
        contact_name="Juan Pérez",
        message="Hola, quiero una cita",
        patient_id=None,
    )

    print("✅ Estado creado correctamente:")
    print(f"   - Conversation ID: {state['conversation_id']}")
    print(f"   - Contact ID: {state['contact_id']}")
    print(f"   - WhatsApp: {state['whatsapp_number']}")
    print(f"   - Nombre: {state['contact_name']}")
    print(f"   - Mensajes: {len(state.get('messages', []))}")
    print(f"   - Todos los campos: {list(state.keys())}")
    print()
    print("=" * 70 + "\n")


async def main():
    """Ejecuta todas las pruebas."""
    print("\n" + "🚀" * 35)
    print("\n  PRUEBAS DEL SUB-AGENTE WHATSAPP (SIN BASE DE DATOS)")
    print("\n" + "🚀" * 35 + "\n")

    # 1. Probar estado
    await test_state()

    # 2. Probar embeddings
    await test_embeddings()

    # 3. Probar clasificación (requiere API key de Anthropic)
    try:
        await test_classification()
    except Exception as e:
        print(f"⚠️ Error en clasificación (¿API key configurada?): {e}\n")

    # 4. Probar generación de respuestas
    try:
        await test_response_generation()
    except Exception as e:
        print(f"⚠️ Error en generación (¿API key configurada?): {e}\n")

    print("\n" + "✅" * 35)
    print("\n  ¡PRUEBAS COMPLETADAS!")
    print("\n" + "✅" * 35 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
