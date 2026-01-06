"""
WhatsApp Chat Simulator - Sub-Agente WhatsApp
===============================================

Simulador de chat interactivo para probar el agente en modo conversacional.
"""

import asyncio
import logging
import sys
from datetime import datetime

from agents.sub_agent_whatsApp.graph import run_agent, whatsapp_agent
from agents.sub_agent_whatsApp.utils import (
    init_db_pool,
    close_db_pool,
    get_or_create_contact,
    get_or_create_conversation,
    save_message,
    get_metrics_collector,
)
from langchain_core.messages import HumanMessage, AIMessage

# Configurar logging mínimo para mejor experiencia de chat
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class ChatSimulator:
    """Simulador de chat WhatsApp interactivo."""

    def __init__(self, user_name: str = "Usuario", phone: str = "+521234567890"):
        self.user_name = user_name
        self.phone = phone
        self.contact_id = None
        self.conversation_id = None
        self.messages = []
        self.metrics = get_metrics_collector()

    async def initialize(self):
        """Inicializa la conexión y crea/obtiene contacto."""
        await init_db_pool()

        # Obtener o crear contacto
        contact = await get_or_create_contact(
            telefono=self.phone, nombre=self.user_name, whatsapp_id=f"wa_{self.phone}"
        )
        self.contact_id = contact["id"]

        # Crear nueva conversación
        conversation = await get_or_create_conversation(
            contact_id=self.contact_id,
            whatsapp_chat_id=f"sim_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        )
        self.conversation_id = conversation["id"]

        print(f"\n{'='*60}")
        print(f"   🟢 SIMULADOR DE WHATSAPP - PODOSKIN")
        print(f"{'='*60}")
        print(f"   Usuario: {self.user_name}")
        print(f"   Teléfono: {self.phone}")
        print(f"   Conversación ID: {self.conversation_id}")
        print(f"{'='*60}")
        print("\n   Escribe tu mensaje y presiona Enter.")
        print("   Comandos especiales:")
        print("     /salir    - Terminar chat")
        print("     /limpiar  - Nueva conversación")
        print("     /metricas - Ver métricas del agente")
        print(f"\n{'='*60}\n")

    async def send_message(self, user_message: str) -> str:
        """Envía un mensaje y obtiene respuesta del agente."""

        # Guardar mensaje del usuario
        await save_message(
            conversation_id=self.conversation_id, rol="user", contenido=user_message
        )

        # Agregar mensaje a la lista
        self.messages.append(HumanMessage(content=user_message))

        # Crear estado inicial
        state = {
            "messages": self.messages.copy(),
            "conversation_id": str(self.conversation_id),
            "contact_id": self.contact_id,
            "patient_id": None,
            "intent": None,
            "confidence": 0.0,
            "entities": {},
            "requires_human": False,
            "escalation_reason": None,
            "retrieved_context": [],
            "appointment_history": [],
            "pending_appointment": None,
            "suggested_slots": [],
            "patient_info": None,
            "next_action": None,
            "processing_stage": "classify",
            "error": None,
        }

        # Ejecutar agente
        self.metrics.record_message()
        result = await run_agent(state=state, thread_id=f"sim_{self.conversation_id}")

        # Obtener respuesta
        last_msg = result["messages"][-1]
        response = (
            last_msg.content
            if hasattr(last_msg, "content")
            else last_msg.get("content", "")
        )

        # Agregar respuesta a la lista
        self.messages.append(AIMessage(content=response))

        # Guardar respuesta
        await save_message(
            conversation_id=self.conversation_id, rol="assistant", contenido=response
        )

        return response, result.get("intent", "?"), result.get("sentiment", {})

    async def new_conversation(self):
        """Inicia una nueva conversación."""
        self.messages = []
        conversation = await get_or_create_conversation(
            contact_id=self.contact_id,
            whatsapp_chat_id=f"sim_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        )
        self.conversation_id = conversation["id"]
        print(f"\n   🔄 Nueva conversación iniciada (ID: {self.conversation_id})\n")

    def show_metrics(self):
        """Muestra métricas del agente."""
        m = self.metrics.get_metrics()
        print(f"\n{'='*50}")
        print("   📊 MÉTRICAS DEL AGENTE")
        print(f"{'='*50}")
        print(f"   Mensajes procesados: {m['summary']['total_messages']}")
        print(f"   Tasa de éxito: {m['summary']['success_rate']}%")
        print(f"   Tiempo promedio: {m['timing']['avg_processing_ms']}ms")
        print(f"   Intenciones: {m['intents']}")
        print(f"{'='*50}\n")

    async def run(self):
        """Loop principal del chat."""
        await self.initialize()

        try:
            while True:
                # Leer input del usuario
                try:
                    user_input = input(f"💬 {self.user_name}: ").strip()
                except EOFError:
                    break

                if not user_input:
                    continue

                # Comandos especiales
                if user_input.lower() == "/salir":
                    print("\n   👋 ¡Hasta luego!\n")
                    break
                elif user_input.lower() == "/limpiar":
                    await self.new_conversation()
                    continue
                elif user_input.lower() == "/metricas":
                    self.show_metrics()
                    continue

                # Enviar mensaje al agente
                print("   ⏳ Procesando...")

                try:
                    response, intent, sentiment = await self.send_message(user_input)

                    # Mostrar respuesta
                    sent_label = (
                        sentiment.get("sentiment", "neutral")
                        if sentiment
                        else "neutral"
                    )
                    print(f"\n🤖 Podoskin: {response}\n")
                    # Debug info oculto (descomentar para desarrollo)
                    # print(f"   [intent: {intent} | sentiment: {sent_label}]\n")

                except Exception as e:
                    print(f"\n   ❌ Error: {str(e)}\n")
                    logger.error(f"Error processing message: {e}", exc_info=True)

        finally:
            await close_db_pool()
            print("   📴 Conexión cerrada.")


async def main():
    """Punto de entrada principal."""
    print("\n" + "=" * 60)
    print("   BIENVENIDO AL SIMULADOR DE CHAT PODOSKIN")
    print("=" * 60)

    # Obtener nombre del usuario
    name = input("\n   ¿Cuál es tu nombre? [Usuario]: ").strip() or "Usuario"
    phone = input("   ¿Tu teléfono? [+521234567890]: ").strip() or "+521234567890"

    # Crear e iniciar simulador
    simulator = ChatSimulator(user_name=name, phone=phone)
    await simulator.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n   👋 Chat cancelado por el usuario.\n")
