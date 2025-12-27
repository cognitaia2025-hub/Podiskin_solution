# Sub-Agente WhatsApp - Podoskin Solution

Agente conversacional para atención al cliente via WhatsApp, construido con LangGraph y Anthropic Claude.

## 🚀 Características

- **Maya** - Asistente virtual con personalidad natural y amigable
- **Clasificación de intenciones** - Detecta automáticamente qué necesita el paciente
- **Agendamiento de citas** - Flujo conversacional para agendar citas
- **Consulta de tratamientos** - Información desde base de datos PostgreSQL
- **Análisis de sentimiento** - Detecta urgencias y ajusta el tono

## 📁 Estructura

```
sub_agent_whatsApp/
├── __init__.py          # Exports del paquete
├── config.py            # Configuración y prompts de Maya
├── state.py             # Estado del agente (TypedDict)
├── graph.py             # Grafo LangGraph
├── nodes/               # Nodos del grafo
│   ├── classify_intent.py
│   ├── retrieve_context.py
│   ├── check_patient.py
│   ├── handle_appointment.py
│   ├── handle_query.py
│   ├── handle_cancellation.py
│   ├── escalate_human.py
│   └── generate_response.py
├── tools/               # Herramientas LangChain
│   ├── patient_tools.py
│   ├── appointment_tools.py
│   └── query_tools.py
└── utils/               # Utilidades
    ├── database.py
    ├── sentiment.py
    ├── conversation_memory.py
    └── metrics.py
```

## ⚙️ Configuración

### Variables de entorno (.env)

```env
DATABASE_URL=postgresql://postgres:password@127.0.0.1:5432/podoskin_db
ANTHROPIC_API_KEY=sk-ant-...
```

### Datos de la clínica (config.py)

```python
clinic_name = "Podoskin Solution"
clinic_phone = "686-108-3647"
clinic_address = "Av. Electricistas 1978, Col. Libertad, Mexicali B.C."
```

## 🧪 Probar el agente

```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Ejecutar simulador de chat
python chat_simulator.py
```

### Comandos del simulador

| Comando | Acción |
|---------|--------|
| `/salir` | Terminar chat |
| `/limpiar` | Nueva conversación |
| `/metricas` | Ver métricas |

## 🔧 Tratamientos disponibles

Los tratamientos se cargan desde la tabla `tratamientos` en PostgreSQL:

| Código | Tratamiento | Precio |
|--------|-------------|--------|
| ONI001 | Onicomicosis (láser) | $800 MXN |
| PIE001 | Pie de Atleta | $500 MXN |
| PED001 | Pedicure Clínico | $400 MXN |
| UNA001 | Uñas Enterradas | $600 MXN |
| CAL001 | Callosidades | $350 MXN |
| VER001 | Verrugas Plantares | $700 MXN |

## 📊 Flujo del grafo

```
┌─────────────┐
│  CLASSIFY   │ ← Entrada del usuario
└──────┬──────┘
       │
   ┌───┴───┐
   │ route │
   └───┬───┘
       │
┌──────┴──────┬──────────┬──────────┐
│             │          │          │
▼             ▼          ▼          ▼
CHECK      RETRIEVE   HANDLE    GENERATE
PATIENT    CONTEXT    QUERY     RESPONSE
│             │          │          │
▼             ▼          ▼          │
HANDLE     HANDLE       │          │
APPT       QUERY        │          │
│             │          │          │
└─────────────┴──────────┴──────────┘
                    │
                    ▼
              ┌──────────┐
              │ GENERATE │ → Respuesta al usuario
              └──────────┘
```

## 📝 Personalidad de Maya

Maya está configurada para:

- Respuestas **cortas** (1-2 oraciones)
- Presentarse siempre en el primer mensaje
- **No hacer listas** largas
- Pedir datos **uno a la vez** para citas
- **No hablar** de temas fuera de podología
- **No mencionar** que es IA/Claude/Anthropic

## 🔗 Integración con WhatsApp

Para conectar con WhatsApp real, se requiere:

1. Cuenta de Meta Business
2. API de WhatsApp Business o Twilio
3. Webhook para recibir mensajes

---
*Desarrollado para Podoskin Solution - Clínica de Podología*
