# -*- coding: utf-8 -*-
"""
Script de prueba simple para el Sub-Agente de Operaciones
=========================================================

Prueba básica del flujo del agente (sin emojis para Windows).
"""

import asyncio
from datetime import datetime
from agents.sub_agent_operator import run_agent
from agents.sub_agent_operator.state import OperationsAgentState


async def test_basic_flow():
    """Prueba básica del flujo del agente."""

    print("=" * 60)
    print("PRUEBA BASICA - SUB-AGENTE DE OPERACIONES")
    print("=" * 60)

    # Crear estado inicial
    state = OperationsAgentState(
        session_id="test_001",
        user_id="user_test",
        user_name="Dr. Test",
        current_message="Cuantas citas tengo hoy?",
        messages=[],
        timestamp=datetime.now().isoformat(),
        processing_stage="init",
    )

    print(f"\nMensaje: {state['current_message']}")
    print("\nProcesando...")

    # Ejecutar agente
    result = await run_agent(state)

    # Mostrar resultados
    print("\n" + "=" * 60)
    print("RESULTADOS")
    print("=" * 60)
    print(f"\nIntencion: {result.get('intent', 'N/A')}")
    print(f"Confianza: {result.get('confidence', 0):.2f}")
    print(f"Entidades: {result.get('entities', {})}")
    print(f"\nRespuesta:\n{result.get('response', 'N/A')}")
    print(f"\nEstado: {result.get('processing_stage', 'N/A')}")

    if result.get("error"):
        print(f"\nError: {result['error']}")

    print("\n" + "=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_basic_flow())
