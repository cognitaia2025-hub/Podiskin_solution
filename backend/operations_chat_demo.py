# -*- coding: utf-8 -*-
"""
Operations Chat Simulator - MODO DEMO
=====================================

Simulador con datos mock para probar sin conexión a BD.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Configurar modo demo
os.environ["DEMO_MODE"] = "true"

from agents.sub_agent_operator import run_agent
from agents.sub_agent_operator.state import OperationsAgentState

# Configurar logging mínimo
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class DemoChatSimulator:
    """Simulador de chat en modo demo (sin BD)."""

    def __init__(self, user_name: str = "Dr. Usuario", user_id: str = "user_001"):
        self.user_name = user_name
        self.user_id = user_id
        self.session_id = f"demo_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.messages = []
        self.message_count = 0

    def initialize(self):
        """Inicializa el simulador."""
        print(f"\n{'='*60}")
        print(f"   SIMULADOR DE OPERACIONES - MODO DEMO")
        print(f"{'='*60}")
        print(f"   Usuario: {self.user_name}")
        print(f"   ID: {self.user_id}")
        print(f"   Sesion: {self.session_id}")
        print(f"\n   MODO DEMO ACTIVO")
        print(f"   - Usando datos de prueba en memoria")
        print(f"   - NO se conecta a base de datos real")
        print(f"   - Las acciones NO se guardan")
        print(f"{'='*60}")
        print("\n   Escribe tu mensaje y presiona Enter.")
        print("   Comandos especiales:")
        print("     /salir    - Terminar chat")
        print("     /limpiar  - Nueva sesion")
        print("     /ayuda    - Ver capacidades del agente")
        print("     /datos    - Ver datos de prueba disponibles")
        print(f"\n{'='*60}\n")

    async def send_message(self, user_message: str) -> tuple:
        """Envía un mensaje y obtiene respuesta del agente."""

        # Crear estado
        state = OperationsAgentState(
            session_id=self.session_id,
            user_id=self.user_id,
            user_name=self.user_name,
            current_message=user_message,
            messages=self.messages.copy(),
            timestamp=datetime.now().isoformat(),
            processing_stage="init",
        )

        # Ejecutar agente
        self.message_count += 1
        result = await run_agent(state)

        # Obtener respuesta
        response = result.get("response", "Sin respuesta")
        intent = result.get("intent", "desconocido")
        confidence = result.get("confidence", 0.0)

        # Guardar en historial
        self.messages.append(
            {
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.messages.append(
            {
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return response, intent, confidence, result

    def new_session(self):
        """Inicia una nueva sesión."""
        self.messages = []
        self.session_id = f"demo_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.message_count = 0
        print(f"\n   Nueva sesion iniciada (ID: {self.session_id})\n")

    def show_help(self):
        """Muestra capacidades del agente."""
        print(f"\n{'='*60}")
        print("   CAPACIDADES DEL AGENTE (MODO DEMO)")
        print(f"{'='*60}")
        print("\n   CONSULTAS:")
        print("   - Cuantas citas tengo hoy?")
        print("   - Cuantas citas tengo manana?")
        print("   - Busca al paciente Maria Fernandez")
        print("   - Mostrame el historial de Juan Ramirez")
        print("\n   REPORTES:")
        print("   - Dame estadisticas de la semana")
        print("   - Cuantos pacientes tenemos?")
        print("\n   NOTA: En modo demo, solo hay datos limitados")
        print(f"{'='*60}\n")

    def show_demo_data(self):
        """Muestra datos de prueba disponibles."""
        print(f"\n{'='*60}")
        print("   DATOS DE PRUEBA DISPONIBLES")
        print(f"{'='*60}")
        print("\n   PACIENTES (5):")
        print("   - Maria Fernandez")
        print("   - Juan Ramirez")
        print("   - Sofia Gomez")
        print("   - Pedro Diaz")
        print("   - Ana Lopez")
        print("\n   CITAS:")
        print("   - Hoy: 2 citas")
        print("   - Manana: 3 citas")
        print("   - Pasadas: 1 cita")
        print(f"\n{'='*60}\n")

    async def run(self):
        """Loop principal del chat."""
        self.initialize()

        try:
            while True:
                # Leer input del usuario
                try:
                    user_input = input(f"{self.user_name}: ").strip()
                except EOFError:
                    break

                if not user_input:
                    continue

                # Comandos especiales
                if user_input.lower() == "/salir":
                    print("\n   Hasta luego!\n")
                    break
                elif user_input.lower() == "/limpiar":
                    self.new_session()
                    continue
                elif user_input.lower() == "/ayuda":
                    self.show_help()
                    continue
                elif user_input.lower() == "/datos":
                    self.show_demo_data()
                    continue

                # Enviar mensaje al agente
                print("   Procesando...")

                try:
                    response, intent, confidence, result = await self.send_message(
                        user_input
                    )

                    # Mostrar respuesta
                    print(f"\nAgente: {response}\n")

                except Exception as e:
                    print(f"\n   Error: {str(e)}\n")
                    logger.error(f"Error processing message: {e}", exc_info=True)

        except KeyboardInterrupt:
            print("\n\n   Chat cancelado.\n")


async def main():
    """Punto de entrada principal."""
    print("\n" + "=" * 60)
    print("   SIMULADOR DE OPERACIONES - MODO DEMO")
    print("=" * 60)
    print("\n   Este simulador usa datos de prueba en memoria.")
    print("   NO se conecta a la base de datos real.")
    print("   Las acciones NO se guardan.")

    # Obtener nombre del usuario
    name = input("\n   Cual es tu nombre? [Dr. Usuario]: ").strip() or "Dr. Usuario"
    user_id = input("   Tu ID de usuario? [user_001]: ").strip() or "user_001"

    # Crear e iniciar simulador
    simulator = DemoChatSimulator(user_name=name, user_id=user_id)
    await simulator.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n   Chat cancelado por el usuario.\n")
