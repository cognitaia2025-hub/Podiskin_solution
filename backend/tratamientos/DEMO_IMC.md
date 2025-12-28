# 📊 Demostración de Cálculo de IMC

Este documento muestra el funcionamiento del **cálculo automático de IMC** implementado en el módulo de tratamientos.

## 🧮 Implementación

El cálculo del IMC se realiza de forma **programática y determinística** (no usa IA/LLM), según lo especificado en las instrucciones del agente.

### Fórmula Matemática

```
IMC = peso (kg) / (talla (m))²
```

### Código Python

```python
def calcular_imc(peso_kg: Decimal, talla_cm: Decimal) -> tuple[Decimal, str]:
    """
    Calcula el IMC y su clasificación.
    
    Args:
        peso_kg: Peso en kilogramos
        talla_cm: Talla en centímetros
        
    Returns:
        Tupla con (IMC, clasificación)
    """
    # Convertir talla a metros
    talla_m = talla_cm / 100
    
    # Calcular IMC: peso / (talla^2)
    imc = peso_kg / (talla_m ** 2)
    
    # Redondear a 2 decimales
    imc = round(imc, 2)
    
    # Clasificar IMC
    if imc < 18.5:
        clasificacion = "Bajo peso"
    elif imc < 25:
        clasificacion = "Normal"
    elif imc < 30:
        clasificacion = "Sobrepeso"
    else:
        clasificacion = "Obesidad"
    
    return imc, clasificacion
```

## ✅ Pruebas Ejecutadas

Se ejecutaron 5 casos de prueba que verifican diferentes clasificaciones de IMC:

```
============================================================
PRUEBA DE CÁLCULO DE IMC
============================================================

Caso 1:
  Peso: 75.5 kg
  Talla: 170 cm
  IMC calculado: 26.12
  Clasificación: Sobrepeso
  Clasificación esperada: Sobrepeso
  ✓ OK

Caso 2:
  Peso: 60 kg
  Talla: 170 cm
  IMC calculado: 20.76
  Clasificación: Normal
  Clasificación esperada: Normal
  ✓ OK

Caso 3:
  Peso: 90 kg
  Talla: 170 cm
  IMC calculado: 31.14
  Clasificación: Obesidad
  Clasificación esperada: Obesidad
  ✓ OK

Caso 4:
  Peso: 50 kg
  Talla: 170 cm
  IMC calculado: 17.30
  Clasificación: Bajo peso
  Clasificación esperada: Bajo peso
  ✓ OK

Caso 5:
  Peso: 85 kg
  Talla: 180 cm
  IMC calculado: 26.23
  Clasificación: Sobrepeso
  Clasificación esperada: Sobrepeso
  ✓ OK
```

**Resultado: 5/5 casos pasaron correctamente ✓**

## 📋 Tabla de Clasificación OMS

| IMC (kg/m²) | Clasificación |
|-------------|---------------|
| < 18.5      | Bajo peso     |
| 18.5 - 24.9 | Normal        |
| 25.0 - 29.9 | Sobrepeso     |
| ≥ 30.0      | Obesidad      |

## 🔗 Integración en el Endpoint

El cálculo se ejecuta automáticamente cuando se envían signos vitales:

### Request
```http
POST /api/citas/123/signos-vitales
Content-Type: application/json

{
  "peso_kg": 75.5,
  "talla_cm": 170,
  "presion_sistolica": 120,
  "presion_diastolica": 80,
  "frecuencia_cardiaca": 72
}
```

### Response
```json
{
  "id": 1,
  "id_cita": 123,
  "peso_kg": 75.5,
  "talla_cm": 170,
  "imc": 26.12,
  "imc_clasificacion": "Sobrepeso",
  "presion_arterial": "120/80",
  "frecuencia_cardiaca": 72,
  "fecha_medicion": "2024-12-26T10:05:00"
}
```

## 📊 Ejemplo Detallado

### Caso: Paciente con Sobrepeso

**Datos de entrada:**
- Peso: 75.5 kg
- Talla: 170 cm

**Proceso de cálculo:**
1. Convertir talla a metros: `170 cm ÷ 100 = 1.70 m`
2. Calcular IMC: `75.5 kg ÷ (1.70 m)²`
3. Elevar al cuadrado: `(1.70)² = 2.89`
4. División: `75.5 ÷ 2.89 = 26.12`
5. Clasificar: `26.12 está entre 25-30` → **Sobrepeso**

**Resultado:**
- IMC: **26.12**
- Clasificación: **Sobrepeso**

## 🔍 Validaciones Implementadas

Según la especificación del FSD (sección 2.5), se implementaron las siguientes validaciones:

- **peso_kg**: 0.1 - 500 kg
- **talla_cm**: 30 - 250 cm
- **presion_sistolica**: 60 - 250 mmHg
- **presion_diastolica**: 40 - 150 mmHg
- **frecuencia_cardiaca**: 30 - 200 bpm
- **frecuencia_respiratoria**: 8 - 60 rpm
- **temperatura_celsius**: 34 - 42 °C
- **saturacion_oxigeno**: 70 - 100 %
- **glucosa_capilar**: 30 - 600 mg/dL

## ✨ Características

- ✅ **Cálculo automático**: No requiere intervención manual
- ✅ **Clasificación automática**: Según estándares OMS
- ✅ **Programático**: Usa fórmula matemática, no IA/LLM
- ✅ **Determinístico**: Mismo input = mismo output
- ✅ **Validado**: Rangos según especificación médica
- ✅ **Probado**: 5/5 casos de prueba pasados

## 📚 Referencias

- **FSD_Podoskin_Solution.md** - Sección 2.5: Signos Vitales
- **SRS_Podoskin_Solution.md** - Sección 3.1.3: Tabla signos_vitales
- **OMS**: Organización Mundial de la Salud - Estándares de IMC

---

**Nota**: Este cálculo es para referencia clínica. En un entorno de producción, se debería considerar factores adicionales como edad, sexo, masa muscular, etc., para una evaluación médica completa.
