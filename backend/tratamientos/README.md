# Módulo de Tratamientos - Backend

Este módulo implementa los endpoints REST para la gestión de tratamientos, signos vitales y diagnósticos médicos.

## 📁 Estructura

```
backend/tratamientos/
├── __init__.py          # Módulo principal
├── models.py            # Modelos Pydantic
├── router.py            # Endpoints FastAPI
├── database.py          # Utilidades de base de datos
├── test_imc.py          # Prueba de cálculo de IMC
└── README.md            # Esta documentación
```

## 🚀 Endpoints Implementados

### CRUD Tratamientos

#### `GET /api/tratamientos`
Lista todos los tratamientos.

**Query Parameters:**
- `activo` (opcional): Filtrar por estado activo (true/false)

**Respuesta:**
```json
[
  {
    "id": 1,
    "codigo_servicio": "CONS001",
    "nombre_servicio": "Consulta General",
    "descripcion": "Consulta podológica general",
    "precio_base": 500.00,
    "duracion_minutos": 30,
    "requiere_consentimiento": false,
    "activo": true,
    "fecha_registro": "2024-12-26T10:00:00"
  }
]
```

#### `POST /api/tratamientos`
Crea un nuevo tratamiento.

**Request Body:**
```json
{
  "codigo_servicio": "CONS001",
  "nombre_servicio": "Consulta General",
  "descripcion": "Consulta podológica general",
  "precio_base": 500.00,
  "duracion_minutos": 30,
  "requiere_consentimiento": false,
  "activo": true
}
```

#### `GET /api/tratamientos/{id}`
Obtiene un tratamiento por ID.

#### `PUT /api/tratamientos/{id}`
Actualiza un tratamiento existente.

**Request Body:** (todos los campos opcionales)
```json
{
  "nombre_servicio": "Consulta General Actualizada",
  "precio_base": 550.00
}
```

#### `DELETE /api/tratamientos/{id}`
Desactiva un tratamiento (soft delete).

### Signos Vitales

#### `POST /api/citas/{id}/signos-vitales`
Crea signos vitales para una cita con **cálculo automático de IMC**.

**Request Body:**
```json
{
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
```

**Respuesta:**
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
  "frecuencia_respiratoria": 16,
  "temperatura_celsius": 36.5,
  "saturacion_oxigeno": 98,
  "glucosa_capilar": 95,
  "fecha_medicion": "2024-12-26T10:05:00"
}
```

### Diagnósticos

#### `POST /api/citas/{id}/diagnosticos`
Crea un diagnóstico para una cita.

**Request Body:**
```json
{
  "tipo": "Definitivo",
  "descripcion": "Fascitis plantar bilateral",
  "codigo_cie10": "M72.2",
  "notas": "Requiere fisioterapia"
}
```

**Respuesta:**
```json
{
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
```

### Catálogo CIE-10

#### `GET /api/diagnosticos/cie10?search={query}`
Busca códigos CIE-10 por código o descripción.

**Query Parameters:**
- `search` (requerido): Término de búsqueda

**Respuesta:**
```json
[
  {
    "id": 1,
    "codigo": "M72.2",
    "descripcion": "Fibromatosis de la aponeurosis plantar",
    "categoria": "Trastornos del tejido blando",
    "subcategoria": "Fibromatosis"
  }
]
```

## 🧮 Cálculo de IMC

El cálculo del IMC se realiza automáticamente cuando se proporcionan peso y talla:

### Fórmula
```
IMC = peso (kg) / (talla (m))²
```

### Clasificación
- **< 18.5**: Bajo peso
- **18.5 - 25**: Normal
- **25 - 30**: Sobrepeso
- **≥ 30**: Obesidad

### Ejemplo
```python
peso = 75.5 kg
talla = 170 cm = 1.70 m
IMC = 75.5 / (1.70)² = 75.5 / 2.89 = 26.12
Clasificación: Sobrepeso
```

## 🧪 Pruebas

Para ejecutar las pruebas del cálculo de IMC:

```bash
cd backend
python tratamientos/test_imc.py
```

Esto ejecutará varios casos de prueba y mostrará los resultados:

```
============================================================
PRUEBA DE CÁLCULO DE IMC
============================================================

Caso 1:
  Peso: 75.5 kg
  Talla: 170 cm
  IMC calculado: 26.12
  Clasificación: Sobrepeso
  ✓ OK
```

## 📦 Dependencias

- `fastapi>=0.104.0` - Framework web
- `pydantic>=2.0.0` - Validación de datos
- `psycopg2-binary>=2.9.0` - Driver PostgreSQL
- `python-dotenv>=1.0.0` - Variables de entorno

## 🔧 Configuración

El módulo se conecta a PostgreSQL usando las siguientes variables de entorno:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/podoskin
# O individualmente:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=podoskin
DB_USER=postgres
DB_PASSWORD=postgres
```

## 📝 Validaciones

### Tratamientos
- `codigo_servicio`: 1-20 caracteres, único
- `nombre_servicio`: 1-100 caracteres
- `precio_base`: >= 0, 2 decimales
- `duracion_minutos`: >= 1

### Signos Vitales
- `peso_kg`: 0.1-500 kg
- `talla_cm`: 30-250 cm
- `presion_sistolica`: 60-250 mmHg
- `presion_diastolica`: 40-150 mmHg
- `frecuencia_cardiaca`: 30-200 bpm
- `frecuencia_respiratoria`: 8-60 rpm
- `temperatura_celsius`: 34-42 °C
- `saturacion_oxigeno`: 70-100 %
- `glucosa_capilar`: 30-600 mg/dL

### Diagnósticos
- `tipo`: Presuntivo | Definitivo | Diferencial
- `descripcion`: 1-500 caracteres
- `codigo_cie10`: Formato [A-Z]\d{2}(.\d{1,2})?

## 🔌 Integración con FastAPI

Para integrar este módulo en tu aplicación FastAPI:

```python
from fastapi import FastAPI
from tratamientos import router as tratamientos_router
from tratamientos.database import init_db_pool, close_db_pool
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db_pool()
    yield
    # Shutdown
    await close_db_pool()

app = FastAPI(lifespan=lifespan)
app.include_router(tratamientos_router)
```

## 📊 Base de Datos

El módulo requiere las siguientes tablas en PostgreSQL:

- `tratamientos` - Catálogo de tratamientos
- `citas` - Citas médicas
- `signos_vitales` - Registro de signos vitales
- `nota_clinica` - Notas clínicas con diagnósticos
- `catalogo_cie10` - Catálogo de códigos CIE-10
- `podologos` - Información de podólogos
- `usuarios` - Usuarios del sistema

Ver `/data/04_citas_tratamientos.sql` y `/data/03_pacientes.sql` para los esquemas completos.

## 📚 Referencias

- **FSD_Podoskin_Solution.md** - Secciones 2.5 y 2.6
- **SRS_Podoskin_Solution.md** - Sección 3.1.4

## ✅ Estado

- [x] CRUD Tratamientos
- [x] Signos Vitales con cálculo de IMC
- [x] Diagnósticos
- [x] Búsqueda CIE-10
- [x] Validaciones
- [x] Pruebas de IMC

## 🐛 Notas

1. Los diagnósticos actualmente se almacenan en `nota_clinica` por simplicidad. En producción, se debería usar la tabla `diagnosticos_tratamiento` con la estructura completa.

2. El cálculo del IMC es **programático y determinístico** (no usa IA/LLM), tal como se especifica en las instrucciones.

3. Todas las validaciones de rangos están implementadas según la especificación del FSD.
