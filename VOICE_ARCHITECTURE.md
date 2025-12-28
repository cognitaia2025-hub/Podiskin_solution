# Arquitectura del Sistema de Voz - Gemini Live + Orquestador

Sistema completo de asistente de voz para consultas médicas en Podoskin Solution.

## Visión General

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GEMINI LIVE FRONTEND                         │
│                     (Frontend/src/voice/)                           │
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐        │
│  │VoiceController│───→│SecureLiveManager│───→│AudioUtils   │        │
│  │   (UI)        │    │  (Session)   │    │(16kHz PCM16) │        │
│  └──────────────┘    └──────────────┘    └──────────────┘        │
│         │                    │                                      │
│         └────────────────────┴──────────────────────────────────── │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │ HTTPS (Secure Tokens)
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND API LAYER                              │
│                      (backend/api/)                                 │
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐                             │
│  │live_sessions │    │ orchestrator │                             │
│  │   (Auth)     │    │   (Router)   │                             │
│  └──────────────┘    └──────────────┘                             │
│         │                    │                                      │
└─────────┼────────────────────┼──────────────────────────────────────┘
          │                    │
          │                    ▼
          │      ┌─────────────────────────────────┐
          │      │   AGENTE PADRE ORQUESTADOR      │
          │      │  (backend/agents/orchestrator/) │
          │      │                                 │
          │      │  ┌──────────────────────────┐  │
          │      │  │  classify_query          │  │
          │      │  │  ↓                        │  │
          │      │  │  route_to_subagent       │  │
          │      │  │  ↓                        │  │
          │      │  │  validate_response       │  │
          │      │  │  ↓                        │  │
          │      │  │  build_response          │  │
          │      │  └──────────────────────────┘  │
          │      └─────────────────┬───────────────┘
          │                        │
          │      ┌─────────────────┼─────────────────┐
          │      │                 │                 │
          │      ▼                 ▼                 ▼
          │  ┌─────────┐     ┌─────────┐     ┌─────────┐
          │  │SubAgente│     │SubAgente│     │SubAgente│
          │  │Resúmenes│     │WhatsApp │     │Análisis │
          │  │         │     │         │     │(Futuro) │
          │  └─────────┘     └─────────┘     └─────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATABASE LAYER                              │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │Pacientes │  │  Citas   │  │ Notas    │  │  Audit   │          │
│  │          │  │          │  │Clínicas  │  │   Logs   │          │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │
│                                                                     │
│  ┌──────────┐  ┌──────────┐                                       │
│  │Embeddings│  │Checkpoints│                                       │
│  │(pgvector)│  │(LangGraph)│                                       │
│  └──────────┘  └──────────┘                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Flujo de Datos

### Flujo 1: Función Simple (Directo)

```
Usuario dice: "Peso 75 kilos"
    ↓
Gemini Live transcribe y detecta función
    ↓
Tool Call: update_vital_signs({peso_kg: 75})
    ↓
Frontend → POST /api/citas/{id}/signos-vitales
    ↓
Database → UPDATE signos_vitales
    ↓
Response → "Peso registrado: 75 kg"
    ↓
Gemini Live → Audio "He registrado el peso de 75 kilogramos"
```

**Tiempo estimado**: 500-800ms

### Flujo 2: Función Compleja (Orquestador → SubAgente)

```
Usuario dice: "Genera un resumen de la consulta"
    ↓
Gemini Live transcribe y detecta función
    ↓
Tool Call: generate_summary({tipo: "consulta_actual", formato: "breve"})
    ↓
Frontend → POST /api/orchestrator/execute
    ↓
ORQUESTADOR:
  1. classify_query → "complex" → requires SubAgente Resúmenes
  2. route_to_subagent → Invoca SubAgente
     ↓
     SUBAGENTE RESÚMENES:
       1. fetch_patient_data → Consulta DB
       2. generate_summary → LLM genera resumen
       3. validate_summary → Verifica calidad
       4. build_response → Formatea respuesta
     ↓
  3. validate_response → Verifica respuesta de SubAgente
  4. build_response → Formatea respuesta final
    ↓
Response → {content: "## Resumen...", status: "success"}
    ↓
Gemini Live → Audio "He generado el resumen de la consulta"
```

**Tiempo estimado**: 1500-3000ms

## Componentes Principales

### 1. Frontend - Sistema de Voz

**Ubicación**: `Frontend/src/voice/`

**Componentes**:
- `VoiceController.tsx` - Componente React principal
- `SecureLiveManager.ts` - Gestión de Gemini Live con seguridad
- `SecureSession.ts` - Manejo de sesiones y tokens
- `audioUtils.ts` - Resampling y conversión de audio
- `constants.ts` - 8 funciones médicas

**Responsabilidades**:
- Capturar audio del micrófono
- Resamplear a 16kHz PCM16
- Enviar a Gemini Live
- Manejar tool calls
- Reproducir respuestas de audio
- Gestionar sesiones seguras

### 2. Backend - API Layer

**Ubicación**: `backend/api/`

**Endpoints**:

#### Live Sessions (`live_sessions.py`)
- `POST /api/live/session/start` - Crear sesión
- `POST /api/live/session/stop` - Cerrar sesión
- `POST /api/live/session/refresh` - Renovar token
- `GET /api/live/session/{id}/credentials` - Obtener API key temporal
- `POST /api/live/tool/call` - Ejecutar tool crítica

#### Orchestrator (`orchestrator.py`)
- `POST /api/orchestrator/execute` - Ejecutar función compleja
- `GET /api/orchestrator/health` - Health check

### 3. Agente Padre Orquestador

**Ubicación**: `backend/agents/orchestrator/`

**Grafo LangGraph**:
```
START → classify_query → route_to_subagent → validate_response → build_response → END
```

**Funciones**:
- Clasificar consultas (simple vs compleja)
- Delegar a SubAgentes
- Validar respuestas
- Auditar operaciones

**Estado**: `OrchestratorState` (TypedDict)

### 4. SubAgente Resúmenes

**Ubicación**: `backend/agents/summaries/`

**Grafo LangGraph**:
```
START → fetch_patient_data → search_history → generate_summary → validate_summary → build_response → END
```

**Funciones**:
- `generate_summary` - Resúmenes de consultas
- `search_patient_history` - Búsqueda semántica

**Tipos de Resumen**:
- Consulta actual (breve, detallado, para paciente)
- Evolución de tratamiento
- Historial completo

**Estado**: `SummaryState` (TypedDict)

## Seguridad

### 1. Tokens Efímeros

```python
# Backend crea token con TTL
token = {
    "token": "secure_random_token",
    "sessionId": "uuid",
    "expiresAt": "2024-12-28T12:00:00",
    "ttl": 3600  # 1 hora
}
```

### 2. Validación

- Todos los endpoints validan token en header
- Tokens se renuevan automáticamente antes de expirar
- Tokens se revocan al cerrar sesión

### 3. API Keys

⚠️ **NUNCA** exponer en cliente

Opciones:
1. **Backend Proxy** (Recomendado) - Backend mantiene API key
2. **Tokens Temporales** - Backend genera keys con scope limitado
3. **Session Credentials** - Endpoint devuelve credenciales temporales

### 4. Auditoría

Todas las operaciones se registran:
```python
audit_log = {
    "timestamp": "2024-12-28T10:30:00",
    "user_id": "789",
    "patient_id": "123",
    "function_name": "generate_summary",
    "status": "success",
    "execution_time_ms": 1250
}
```

## Funciones Médicas

### Clasificación

**Funciones Simples** (6) - Endpoint REST directo:
1. `update_vital_signs` - Actualizar signos vitales
2. `create_clinical_note` - Crear nota clínica
3. `query_patient_data` - Consultar datos
4. `add_allergy` - Registrar alergia
5. `navigate_to_section` - Navegar UI
6. `schedule_followup` - Programar seguimiento

**Funciones Complejas** (2) - Orquestador → SubAgente:
7. `search_patient_history` - Búsqueda semántica
8. `generate_summary` - Generar resumen

### Decisión de Routing

```python
def classify_query(state):
    if function_name in SIMPLE_FUNCTIONS:
        # No requiere orquestador
        return "simple"
    elif function_name in COMPLEX_FUNCTIONS_MAPPING:
        # Requiere SubAgente
        target = COMPLEX_FUNCTIONS_MAPPING[function_name]["subagent"]
        return "complex", target
```

## Persistencia (Checkpointers)

### LangGraph Checkpointers

Permiten pausar y reanudar ejecuciones:

```python
# Memory (Development)
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()

# Postgres (Production)
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver(connection_string)

# Redis (Production - Alternative)
from langgraph.checkpoint.redis import RedisSaver
checkpointer = RedisSaver(redis_client)
```

### Uso

```python
# Compilar con checkpointer
graph.compile(checkpointer=checkpointer)

# Pausar ejecución
interrupt("waiting_for_validation")

# Reanudar ejecución
graph.invoke(state, config={"thread_id": "session_123"})
```

## Observabilidad

### LangSmith Tracing

```bash
export LANGSMITH_TRACING_V2=true
export LANGSMITH_API_KEY=your_key
export LANGSMITH_PROJECT=podoskin-orchestrator
```

Permite ver:
- Ejecución de nodos
- Tiempos de respuesta
- Llamadas a LLM
- Errores y excepciones

### Métricas

```python
metrics = {
    "execution_time_ms": 1250,
    "subagent_time_ms": 850,
    "validation_time_ms": 100,
    "total_tokens": 500,
    "status": "success"
}
```

## Testing

### Test de Flujo Simple

```python
@pytest.mark.asyncio
async def test_simple_flow():
    # Simular tool call
    result = await execute_tool(
        "update_vital_signs",
        {"peso_kg": 75, "talla_cm": 175}
    )
    assert result["success"] == True
```

### Test de Flujo Complejo

```python
@pytest.mark.asyncio
async def test_complex_flow():
    # Simular función compleja
    result = await execute_orchestrator(
        "generate_summary",
        {"tipo_resumen": "consulta_actual"},
        patient_id="123",
        user_id="789"
    )
    assert result["status"] == "success"
    assert "content" in result["data"]
```

## Deployment

### Variables de Entorno

```bash
# Database
DATABASE_URL=postgresql://user:pass@host/podoskin

# Gemini API
GEMINI_API_KEY=your_api_key

# LLM Models
ORCHESTRATOR_LLM_MODEL=claude-3-5-haiku-20241022
SUMMARIES_LLM_MODEL=claude-3-5-haiku-20241022

# Checkpointer
CHECKPOINTER_TYPE=postgres
CHECKPOINTER_URL=postgresql://user:pass@host/podoskin

# Security
SESSION_TTL=3600
TOKEN_REFRESH_THRESHOLD=300

# LangSmith
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_key
LANGSMITH_PROJECT=podoskin-production
```

### Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://postgres:pass@db/podoskin
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - db
      
  frontend:
    build: ./Frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8000
      
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: podoskin
      POSTGRES_PASSWORD: pass
    volumes:
      - pgdata:/var/lib/postgresql/data
```

## Próximos Pasos

- [ ] Integrar con base de datos real
- [ ] Implementar búsqueda semántica con embeddings
- [ ] Añadir SubAgente de Análisis Clínico
- [ ] Migrar a AudioWorklet (reemplazo de ScriptProcessor)
- [ ] Implementar cache de resúmenes frecuentes
- [ ] Añadir tests end-to-end
- [ ] Deploy a producción

## Referencias

- [Frontend Voice README](../Frontend/src/voice/README.md)
- [Orchestrator README](../backend/agents/orchestrator/README.md)
- [Summaries README](../backend/agents/summaries/README.md)
- [FSD Podoskin](./FSD_Podoskin_Solution.md) - Sección 3.3
- [GEMINI_LIVE_FUNCTIONS](./data/GEMINI_LIVE_FUNCTIONS.md)
- [recomendacionesLangGraph](./recomendacionesLangGraph.md)
