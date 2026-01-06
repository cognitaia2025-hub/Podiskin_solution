# -*- coding: utf-8 -*-
"""
Operations Chat Simulator - Sub-Agente de Operaciones
=====================================================

Simulador de chat interactivo para probar el agente de operaciones.
Diseñado para simular conversaciones del personal de la clínica.
"""

import asyncio
import logging
import sys
from datetime import datetime

from agents.sub_agent_operator import run_agent
from agents.sub_agent_operator.state import OperationsAgentState

# Configurar logging mínimo para mejor experiencia de chat
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class OperationsChatSimulator:
    """Simulador de chat para el agente de operaciones."""

    def __init__(self, user_name: str = "Dr. Usuario", user_id: str = "user_001"):
        self.user_name = user_name
        self.user_id = user_id
        self.session_id = f"sim_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.messages = []
        self.message_count = 0

    def initialize(self):
        """Inicializa el simulador."""
        print(f"\n{'='*60}")
        print(f"   SIMULADOR DE OPERACIONES - PODOSKIN")
        print(f"{'='*60}")
        print(f"   Usuario: {self.user_name}")
        print(f"   ID: {self.user_id}")
        print(f"   Sesion: {self.session_id}")
        print(f"{'='*60}")
        print("\n   Escribe tu mensaje y presiona Enter.")
        print("   Comandos especiales:")
        print("     /salir    - Terminar chat")
        print("     /limpiar  - Nueva sesion")
        print("     /ayuda    - Ver capacidades del agente")
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
        self.session_id = f"sim_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.message_count = 0
        print(f"\n   Nueva sesion iniciada (ID: {self.session_id})\n")

    def show_help(self):
        """Muestra capacidades del agente."""
        print(f"\n{'='*60}")
        print("   CAPACIDADES DEL AGENTE DE OPERACIONES")
        print(f"{'='*60}")
        print("\n   CONSULTAS:")
        print("   - Cuantas citas tengo hoy?")
        print("   - Busca al paciente Juan Perez")
        print("   - Mostrame las citas de manana")
        print("   - Historial de citas de [paciente]")
        print("\n   ACCIONES:")
        print("   - Agenda a Juan para manana a las 10 AM")
        print("   - Reagenda la cita de las 3 PM")
        print("   - Cancela la cita de Juan")
        print("   - Actualiza el telefono de Maria")
        print("\n   REPORTES:")
        print("   - Dame un resumen de la semana")
        print("   - Cuantas citas tuvimos este mes?")
        print("   - Estadisticas de cancelaciones")
        print(f"\n{'='*60}\n")

    def show_stats(self):
        """Muestra estadísticas de la sesión."""
        print(f"\n{'='*60}")
        print("   ESTADISTICAS DE LA SESION")
        print(f"{'='*60}")
        print(f"   Mensajes enviados: {self.message_count}")
        print(f"   Mensajes en historial: {len(self.messages)}")
        print(f"   Sesion ID: {self.session_id}")
        print(f"{'='*60}\n")

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
                elif user_input.lower() == "/stats":
                    self.show_stats()
                    continue

                # Enviar mensaje al agente
                print("   Procesando...")

                try:
                    response, intent, confidence, result = await self.send_message(
                        user_input
                    )

                    # Mostrar respuesta
                    print(f"\nAgente: {response}\n")

                    # Debug info (opcional)
                    # print(f"   [intent: {intent} | confidence: {confidence:.2f}]\n")

                except Exception as e:
                    print(f"\n   Error: {str(e)}\n")
                    logger.error(f"Error processing message: {e}", exc_info=True)

        except KeyboardInterrupt:
            print("\n\n   Chat cancelado.\n")


async def main():
    """Punto de entrada principal."""
    print("\n" + "=" * 60)
    print("   BIENVENIDO AL SIMULADOR DE OPERACIONES PODOSKIN")
    print("=" * 60)

    # Obtener nombre del usuario
    name = input("\n   Cual es tu nombre? [Dr. Usuario]: ").strip() or "Dr. Usuario"
    user_id = input("   Tu ID de usuario? [user_001]: ").strip() or "user_001"

    # Crear e iniciar simulador
    simulator = OperationsChatSimulator(user_name=name, user_id=user_id)
    await simulator.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n   Chat cancelado por el usuario.\n")
