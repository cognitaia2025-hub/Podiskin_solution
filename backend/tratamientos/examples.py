"""
Script de Ejemplo - Uso de API de Tratamientos
==============================================

Ejemplos de cómo usar los endpoints de la API.
"""

import asyncio
import json
from decimal import Decimal

print("=" * 70)
print("EJEMPLOS DE USO - API DE TRATAMIENTOS")
print("=" * 70)
print()

# ============================================================================
# TRATAMIENTOS - CRUD
# ============================================================================

print("1. CREAR TRATAMIENTO")
print("-" * 70)
print("POST /api/tratamientos")
print()
print("Request Body:")
ejemplo_crear = {
    "codigo_servicio": "CONS001",
    "nombre_servicio": "Consulta General",
    "descripcion": "Consulta podológica general de primera vez",
    "precio_base": 500.00,
    "duracion_minutos": 30,
    "requiere_consentimiento": False,
    "activo": True
}
print(json.dumps(ejemplo_crear, indent=2, ensure_ascii=False))
print()

print("curl -X POST http://localhost:8000/api/tratamientos \\")
print('  -H "Content-Type: application/json" \\')
print(f'  -d \'{json.dumps(ejemplo_crear)}\'')
print()
print("=" * 70)
print()

# ============================================================================

print("2. LISTAR TRATAMIENTOS")
print("-" * 70)
print("GET /api/tratamientos")
print()
print("curl http://localhost:8000/api/tratamientos")
print()
print("GET /api/tratamientos?activo=true")
print()
print("curl http://localhost:8000/api/tratamientos?activo=true")
print()
print("=" * 70)
print()

# ============================================================================

print("3. OBTENER TRATAMIENTO POR ID")
print("-" * 70)
print("GET /api/tratamientos/1")
print()
print("curl http://localhost:8000/api/tratamientos/1")
print()
print("=" * 70)
print()

# ============================================================================

print("4. ACTUALIZAR TRATAMIENTO")
print("-" * 70)
print("PUT /api/tratamientos/1")
print()
print("Request Body (solo campos a actualizar):")
ejemplo_actualizar = {
    "precio_base": 550.00,
    "duracion_minutos": 45
}
print(json.dumps(ejemplo_actualizar, indent=2))
print()
print("curl -X PUT http://localhost:8000/api/tratamientos/1 \\")
print('  -H "Content-Type: application/json" \\')
print(f'  -d \'{json.dumps(ejemplo_actualizar)}\'')
print()
print("=" * 70)
print()

# ============================================================================

print("5. ELIMINAR TRATAMIENTO (Soft Delete)")
print("-" * 70)
print("DELETE /api/tratamientos/1")
print()
print("curl -X DELETE http://localhost:8000/api/tratamientos/1")
print()
print("=" * 70)
print()

# ============================================================================
# SIGNOS VITALES
# ============================================================================

print("6. CREAR SIGNOS VITALES CON CÁLCULO DE IMC")
print("-" * 70)
print("POST /api/citas/123/signos-vitales")
print()
print("Request Body:")
ejemplo_signos = {
    "peso_kg": 75.5,
    "talla_cm": 170,
    "presion_sistolica": 120,
    "presion_diastolica": 80,
    "frecuencia_cardiaca": 72,
    "frecuencia_respiratoria": 16,
    "temperatura_celsius": 36.5,
    "saturacion_oxigeno": 98,
    "glucosa_capilar": 95
}
print(json.dumps(ejemplo_signos, indent=2))
print()
print("curl -X POST http://localhost:8000/api/citas/123/signos-vitales \\")
print('  -H "Content-Type: application/json" \\')
print(f'  -d \'{json.dumps(ejemplo_signos)}\'')
print()
print("Respuesta esperada:")
respuesta_signos = {
    "id": 1,
    "id_cita": 123,
    "peso_kg": 75.5,
    "talla_cm": 170,
    "imc": 26.12,
    "imc_clasificacion": "Sobrepeso",
    "presion_arterial": "120/80",
    "frecuencia_cardiaca": 72,
    "frecuencia_respiratoria": 16,
    "temperatura_celsius": 36.5,
    "saturacion_oxigeno": 98,
    "glucosa_capilar": 95,
    "fecha_medicion": "2024-12-26T10:05:00"
}
print(json.dumps(respuesta_signos, indent=2))
print()
print("=" * 70)
print()

# ============================================================================
# DEMOSTRACIÓN DE CÁLCULO DE IMC
# ============================================================================

print("7. CÁLCULO DE IMC - DEMOSTRACIÓN")
print("-" * 70)
print()
print("Fórmula: IMC = peso (kg) / (talla (m))²")
print()
print("Ejemplo del endpoint:")
print(f"  Peso: 75.5 kg")
print(f"  Talla: 170 cm = 1.70 m")
print(f"  IMC = 75.5 / (1.70)²")
print(f"  IMC = 75.5 / 2.89")
print(f"  IMC = 26.12")
print(f"  Clasificación: Sobrepeso")
print()
print("Tabla de clasificación:")
print("  < 18.5  → Bajo peso")
print("  18.5-25 → Normal")
print("  25-30   → Sobrepeso")
print("  ≥ 30    → Obesidad")
print()
print("=" * 70)
print()

# ============================================================================
# DIAGNÓSTICOS
# ============================================================================

print("8. CREAR DIAGNÓSTICO")
print("-" * 70)
print("POST /api/citas/123/diagnosticos")
print()
print("Request Body:")
ejemplo_diagnostico = {
    "tipo": "Definitivo",
    "descripcion": "Fascitis plantar bilateral",
    "codigo_cie10": "M72.2",
    "notas": "Requiere fisioterapia y control en 2 semanas"
}
print(json.dumps(ejemplo_diagnostico, indent=2, ensure_ascii=False))
print()
print("curl -X POST http://localhost:8000/api/citas/123/diagnosticos \\")
print('  -H "Content-Type: application/json" \\')
print(f'  -d \'{json.dumps(ejemplo_diagnostico)}\'')
print()
print("Respuesta esperada:")
respuesta_diagnostico = {
    "id": 1,
    "id_cita": 123,
    "tipo": "Definitivo",
    "descripcion": "Fascitis plantar bilateral",
    "codigo_cie10": "M72.2",
    "codigo_cie10_descripcion": "Fibromatosis de la aponeurosis plantar",
    "diagnosticado_por": {
        "id": 1,
        "nombre": "Dr. Santiago Ornelas"
    },
    "fecha_diagnostico": "2024-12-26T10:15:00"
}
print(json.dumps(respuesta_diagnostico, indent=2, ensure_ascii=False))
print()
print("=" * 70)
print()

# ============================================================================
# BÚSQUEDA CIE-10
# ============================================================================

print("9. BUSCAR CÓDIGOS CIE-10")
print("-" * 70)
print("GET /api/diagnosticos/cie10?search=fascitis")
print()
print("curl 'http://localhost:8000/api/diagnosticos/cie10?search=fascitis'")
print()
print("GET /api/diagnosticos/cie10?search=M72")
print()
print("curl 'http://localhost:8000/api/diagnosticos/cie10?search=M72'")
print()
print("Respuesta esperada:")
respuesta_cie10 = [
    {
        "id": 1,
        "codigo": "M72.2",
        "descripcion": "Fibromatosis de la aponeurosis plantar",
        "categoria": "Trastornos del tejido blando",
        "subcategoria": "Fibromatosis"
    }
]
print(json.dumps(respuesta_cie10, indent=2, ensure_ascii=False))
print()
print("=" * 70)
print()

# ============================================================================
# PYTHON REQUESTS
# ============================================================================

print("10. EJEMPLO CON PYTHON (requests)")
print("-" * 70)
print()
codigo_python = '''
import requests

# Crear tratamiento
response = requests.post(
    "http://localhost:8000/api/tratamientos",
    json={
        "codigo_servicio": "CONS001",
        "nombre_servicio": "Consulta General",
        "precio_base": 500.00,
        "duracion_minutos": 30
    }
)
print(response.json())

# Crear signos vitales con IMC
response = requests.post(
    "http://localhost:8000/api/citas/123/signos-vitales",
    json={
        "peso_kg": 75.5,
        "talla_cm": 170,
        "presion_sistolica": 120,
        "presion_diastolica": 80,
        "frecuencia_cardiaca": 72
    }
)
signos = response.json()
print(f"IMC: {signos['imc']} - {signos['imc_clasificacion']}")

# Buscar CIE-10
response = requests.get(
    "http://localhost:8000/api/diagnosticos/cie10",
    params={"search": "fascitis"}
)
print(response.json())
'''
print(codigo_python)
print()
print("=" * 70)
print()

# ============================================================================
# DOCUMENTACIÓN
# ============================================================================

print("11. DOCUMENTACIÓN INTERACTIVA")
print("-" * 70)
print()
print("Swagger UI:")
print("  http://localhost:8000/docs")
print()
print("ReDoc:")
print("  http://localhost:8000/redoc")
print()
print("OpenAPI JSON:")
print("  http://localhost:8000/openapi.json")
print()
print("=" * 70)
print()

print("Para ejecutar la aplicación de ejemplo:")
print("  cd backend/tratamientos")
print("  uvicorn app_example:app --reload --port 8000")
print()
print("=" * 70)
