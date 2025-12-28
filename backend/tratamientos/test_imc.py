"""
Aplicación de Prueba - Módulo de Tratamientos
==============================================

Script para probar los endpoints de tratamientos.
"""

import asyncio
from decimal import Decimal

# Importar función de cálculo de IMC
import sys
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from tratamientos import service


def test_calculo_imc():
    """Prueba el cálculo de IMC con diferentes valores."""
    
    print("=" * 60)
    print("PRUEBA DE CÁLCULO DE IMC")
    print("=" * 60)
    print()
    
    # Casos de prueba
    casos = [
        {"peso": Decimal("75.5"), "talla": Decimal("170"), "esperado": "Sobrepeso"},
        {"peso": Decimal("60"), "talla": Decimal("170"), "esperado": "Normal"},
        {"peso": Decimal("90"), "talla": Decimal("170"), "esperado": "Obesidad"},
        {"peso": Decimal("50"), "talla": Decimal("170"), "esperado": "Bajo peso"},
        {"peso": Decimal("85"), "talla": Decimal("180"), "esperado": "Sobrepeso"},
    ]
    
    for i, caso in enumerate(casos, 1):
        peso = caso["peso"]
        talla = caso["talla"]
        esperado = caso["esperado"]
        
        imc = service.calcular_imc(peso, talla)
        clasificacion = service.clasificar_imc(imc)
        
        print(f"Caso {i}:")
        print(f"  Peso: {peso} kg")
        print(f"  Talla: {talla} cm")
        print(f"  IMC calculado: {imc}")
        print(f"  Clasificación: {clasificacion}")
        print(f"  Clasificación esperada: {esperado}")
        print(f"  ✓ OK" if clasificacion == esperado else f"  ✗ ERROR")
        print()
    
    print("=" * 60)
    print("FÓRMULA DEL IMC")
    print("=" * 60)
    print()
    print("IMC = peso (kg) / (talla (m))²")
    print()
    print("Ejemplo:")
    print("  Peso: 75.5 kg")
    print("  Talla: 170 cm = 1.70 m")
    print("  IMC = 75.5 / (1.70)²")
    print("  IMC = 75.5 / 2.89")
    print("  IMC = 26.12")
    print()
    print("Clasificación:")
    print("  < 18.5  → Bajo peso")
    print("  18.5-25 → Normal")
    print("  25-30   → Sobrepeso")
    print("  ≥ 30    → Obesidad")
    print()
    print("=" * 60)


if __name__ == "__main__":
    test_calculo_imc()
