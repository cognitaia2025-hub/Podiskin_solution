# CLAUDE.md - Fuente Única de Verdad

## Podoskin Solution - Technical Specification Document (TSD)

> **Última actualización:** 11 de enero de 2026
> **Supervisor:** Claude Opus 4.5
> **Desarrollador:** Salvador Cordova Soto
> **Cliente:** Santiago de Jesús Ornelas Reynoso (Clínica Podológica)

---

## 1. INFORMACIÓN DEL PROYECTO

| Campo | Valor |
|-------|-------|
| **Nombre** | Podoskin Solution |
| **Tipo** | Sistema de Gestión Clínica Podológica |
| **Usuario Final** | Santiago (Podólogo/Dueño), Ibeth (Recepcionista/Podologa) |
| **Estado** | En desarrollo - Preparando MVP |

---

## 2. STACK TECNOLÓGICO APROBADO

### 2.1 Frontend

| Tecnología | Versión | Propósito | Estado |
|------------|---------|-----------|--------|
| React | 18.x | Framework UI | ✅ Aprobado |
| TypeScript | 5.x | Tipado estático | ✅ Aprobado |
| Vite | 5.x | Build tool | ✅ Aprobado |
| Tailwind CSS | 3.x | Estilos | ✅ Aprobado |
| Recharts | 2.x | Gráficas/Dashboard | ✅ Aprobado |
| React Hook Form | 7.x | Formularios | ✅ Aprobado |
| Zod | 3.x | Validación | ✅ Aprobado |
| date-fns | 3.x | Manejo de fechas | ✅ Aprobado |
| lucide-react | latest | Iconos | ✅ Aprobado |
| @dnd-kit | 6.x | Drag & Drop | ✅ Aprobado |

### 2.2 Backend

| Tecnología | Versión | Propósito | Estado |
|------------|---------|-----------|--------|
| Python | 3.11+ | Lenguaje backend | ✅ Aprobado |
| FastAPI | 0.109+ | Framework API | ✅ Aprobado |
| AsyncPG | 0.29+ | Driver PostgreSQL (ÚNICO) | ✅ Aprobado |
| Pydantic | 2.x | Validación/Schemas | ✅ Aprobado |
| python-jose | 3.x | JWT tokens | ✅ Aprobado |
| passlib[bcrypt] | 1.7+ | Hash contraseñas | ✅ Aprobado |
| httpx | 0.27+ | HTTP client async | ✅ Aprobado |
| websockets | 11.x | WebSocket server | ✅ Aprobado |

### 2.3 Base de Datos

| Tecnología | Versión | Propósito | Estado |
|------------|---------|-----------|--------|
| PostgreSQL | 14+ | Base de datos principal | ✅ Aprobado |
| pgvector | 0.5+ | Embeddings/Vector search | ✅ Aprobado |
| Redis | 7.x | Cache/Sesiones | ✅ Aprobado |

### 2.4 Inteligencia Artificial

| Tecnología | Propósito | Estado |
|------------|-----------|--------|
| **Claude Haiku 3** | Agentes backend (lógica negocio) | ✅ Aprobado - Principal |
| **Gemini 2.0 Flash** | Procesos complejos / Alternativa económica | ✅ Aprobado - Secundario |
| **Gemini Live** | Control de voz frontend (MAYA) | ✅ Aprobado |
| LangChain | 0.1+ | Framework agentes | ✅ Aprobado |
| LangGraph | 0.0.x | Orquestación multi-agente | ✅ Aprobado |
| Sentence-Transformers | latest | Embeddings locales | ✅ Aprobado |

### 2.5 Integraciones

| Tecnología | Propósito | Estado |
|------------|-----------|--------|
| **Twilio WhatsApp API** | WhatsApp (producción) | 🎯 Target - Por implementar |

### 2.6 Infraestructura

| Tecnología | Propósito | Estado |
|------------|-----------|--------|
| Docker | Containerización | ✅ Aprobado |
| Docker Compose | Orquestación local | ✅ Aprobado |
| Railway / Render / Fly.io | Hosting producción | 🔄 Por definir |

---

## 3. TECNOLOGÍAS PROHIBIDAS / DEPRECADAS

> ⛔ **NO USAR** estas tecnologías en nuevos desarrollos:

| Tecnología | Razón | Reemplazo |
|------------|-------|-----------|
| psycopg2 | Migración a AsyncPG | AsyncPG |
| psycopg3 (sync) | Migración a AsyncPG | AsyncPG |
| SQLAlchemy ORM | Queries directos con AsyncPG | Raw SQL + AsyncPG |
| requests | No async | httpx |
| Flask | No es el framework del proyecto | FastAPI |
| axios | Usar fetch nativo o similar | fetch API |
| moment.js | Deprecado/pesado | date-fns |
| Material UI | No es el sistema de diseño | Tailwind CSS |
| Redux | Overengineering para este proyecto | React Context |

---

## 4. ARQUITECTURA DEL SISTEMA

### 4.1 Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                             │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    MAYA (Gemini Live)                        │    │
│  │   - Control de navegación por voz                           │    │
│  │   - Llenado de formularios por dictado                      │    │
│  │   - Transcripción tiempo real                               │    │
│  │   - NO conecta con backend, solo controla UI                │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  Páginas: Dashboard | Calendario | Pacientes | Finanzas | WhatsApp  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP/WebSocket
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI + AsyncPG)                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              ORQUESTADOR (LangGraph + Claude)                │    │
│  │                                                              │    │
│  │   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │    │
│  │   │   Agente     │ │   Agente     │ │   Agente     │        │    │
│  │   │  WhatsApp    │ │  Calendario  │ │  Finanzas    │        │    │
│  │   │  (Haiku 3)   │ │  (Haiku 3)   │ │  (Haiku 3)   │        │    │
│  │   └──────────────┘ └──────────────┘ └──────────────┘        │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  Routers: /citas | /pacientes | /pagos | /whatsapp-bridge | etc.    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   PostgreSQL     │  │      Redis       │  │  WhatsApp Node   │
│   + pgvector     │  │     (Cache)      │  │    Service       │
│                  │  │                  │  │  (whatsapp-web)  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

### 4.2 Arquitectura de Agentes IA

```
                    ┌─────────────────────────┐
                    │   ORQUESTADOR PADRE     │
                    │   (Enruta consultas)    │
                    └───────────┬─────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│ SUB-AGENTE    │      │ SUB-AGENTE    │      │ SUB-AGENTE    │
│ WHATSAPP      │      │ OPERADOR      │      │ RESÚMENES     │
│               │      │               │      │               │
│ - Clasificar  │      │ - Crear citas │      │ - Generar     │
│   intención   │      │ - Consultar   │      │   resúmenes   │
│ - Responder   │      │ - Reagendar   │      │ - Búsqueda    │
│ - Escalar     │      │ - Cancelar    │      │   semántica   │
└───────────────┘      └───────────────┘      └───────────────┘
```

### 4.3 Arquitectura MAYA (Asistente de Voz)

```
┌─────────────────────────────────────────────────────────────────┐
│                    MAYA - Gemini Live                            │
│                                                                  │
│  CAPACIDADES:                                                    │
│  ├─ Escuchar conversación Doctor ↔ Paciente                     │
│  ├─ Distinguir cuando le hablan directamente vs. conversación   │
│  ├─ Transcribir en tiempo real                                  │
│  ├─ Llenar formularios por dictado                              │
│  ├─ Navegar interfaz por comandos de voz                        │
│  ├─ Generar resúmenes de consulta                               │
│  └─ Responder preguntas sobre datos del paciente                │
│                                                                  │
│  LIMITACIONES (por diseño):                                      │
│  ├─ NO conecta directamente al backend                          │
│  ├─ Solo controla el frontend                                   │
│  └─ Usa datos ya cargados en la UI                              │
│                                                                  │
│  INTEGRACIÓN:                                                    │
│  └─ Function Calling con JSON para controlar componentes React  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. PRIORIDADES MVP (Para Santiago)

### 5.1 Crítico - Sprint 1

| # | Funcionalidad | Descripción | Estado |
|---|---------------|-------------|--------|
| 1 | **Calendario de Citas** | Agendar, ver, editar citas. Vistas día/semana/mes | 🔄 En progreso |
| 2 | **Control de No-Show** | Identificar citas canceladas/no asistidas para seguimiento | 🔄 En progreso |
| 3 | **Agente WhatsApp** | Responder consultas, agendar citas automáticamente | 🔄 En progreso |

### 5.2 Importante - Sprint 2

| # | Funcionalidad | Descripción | Estado |
|---|---------------|-------------|--------|
| 4 | **Gestión de Pacientes** | CRUD pacientes, historial, contacto | ✅ Funcional |
| 5 | **Recordatorios WhatsApp** | Enviar recordatorios de citas automáticos | ⏸️ Pendiente |

### 5.3 Deseable - Sprint 3

| # | Funcionalidad | Descripción | Estado |
|---|---------------|-------------|--------|
| 6 | **MAYA Voz** | Asistente de voz para consultas médicas | ⏸️ Pendiente |
| 7 | **Transcripción Tiempo Real** | MAYA escucha y toma notas de consulta | ⏸️ Pendiente |
| 8 | **Dashboard Analytics** | KPIs y métricas de la clínica | ⏸️ Pendiente |

---

## 6. ESTRUCTURA DE CARPETAS APROBADA

```
PodoskiSolution/
├── Frontend/
│   ├── src/
│   │   ├── components/          # Componentes reutilizables
│   │   │   ├── medical/         # Componentes médicos
│   │   │   ├── whatsapp/        # Componentes WhatsApp
│   │   │   └── maya/            # Componentes MAYA (voz) [CREAR]
│   │   ├── pages/               # Páginas principales
│   │   ├── services/            # Llamadas API
│   │   ├── hooks/               # Custom hooks
│   │   ├── context/             # Estado global
│   │   ├── types/               # TypeScript types
│   │   └── utils/               # Utilidades
│   └── package.json
│
├── backend/
│   ├── agents/
│   │   ├── orchestrator/        # Agente orquestador
│   │   ├── whatsapp_medico/     # Agente WhatsApp ✅
│   │   ├── sub_agent_operator/  # Sub-agente operador
│   │   └── summaries/           # Agente resúmenes
│   ├── auth/                    # Autenticación JWT
│   ├── citas/                   # Módulo citas
│   ├── pacientes/               # Módulo pacientes
│   ├── tratamientos/            # Módulo tratamientos
│   ├── horarios/                # Módulo horarios
│   ├── gastos/                  # Módulo gastos
│   ├── pagos/                   # Módulo pagos
│   ├── facturas/                # Módulo facturas
│   ├── whatsapp_bridge/         # Bridge con Node.js
│   ├── whatsapp_management/     # UI management WhatsApp
│   ├── ws_notifications/        # WebSocket notifications
│   ├── db.py                    # Pool AsyncPG (ÚNICO)
│   ├── main.py                  # Entry point
│   └── requirements.txt
│
├── whatsapp-web-js/             # Servicio Node.js WhatsApp
├── gemini-live-voice-controller/ # ⚠️ SOLO INSPIRACIÓN/REFERENCIA (no producción)
├── data/                        # Scripts SQL
│   └── migrations/              # Migraciones DB
├── docker-compose.yml
└── CLAUDE.md                    # Este archivo
```

---

## 7. CÓDIGO OBSOLETO / POR ELIMINAR

> ⚠️ Las siguientes carpetas/archivos están identificados como obsoletos o en transición:

### 7.1 Ya Eliminados (Git staged for deletion)

```
❌ backend/agents/sub_agent_whatsApp/    # Reemplazado por whatsapp_medico/
   - Toda la carpeta fue eliminada
   - Usar: backend/agents/whatsapp_medico/
```

### 7.2 Por Migrar/Revisar

| Archivo/Carpeta | Problema | Acción |
|-----------------|----------|--------|
| `backend/citas/database.py` | Posible uso de psycopg2 | Migrar a AsyncPG |
| `backend/inventory/service.py` | Conexiones legacy | Migrar a AsyncPG |
| `backend/stats/router.py` | Funciones legacy DB | Migrar a AsyncPG |
| Cualquier `get_db_connection()` | Patrón viejo | Usar pool de `db.py` |
| Cualquier `psycopg2` import | Deprecado | Eliminar |

### 7.3 Archivos de Documentación Eliminados

```
❌ backend/agents/sub_agent_whatsApp/BORRADORES.py
❌ backend/agents/sub_agent_whatsApp/ESTRUCTURA.txt
❌ backend/agents/sub_agent_whatsApp/HERRAMIENTAS_COMPLETADAS.md
❌ backend/agents/sub_agent_whatsApp/IMPLEMENTACION_COMPLETA.md
❌ backend/agents/sub_agent_whatsApp/PATRONES_LANGGRAPH.md
❌ backend/agents/sub_agent_whatsApp/PROGRESO.md
❌ backend/agents/sub_agent_whatsApp/README.md
❌ backend/agents/sub_agent_whatsApp/RESUMEN_IMPLEMENTACION.md
```

### 7.4 Carpetas de Referencia (No Producción)

| Carpeta | Propósito | Nota |
|---------|-----------|------|
| `gemini-live-voice-controller/` | Inspiración para MAYA | Solo referencia, NO copiar directamente. Implementación de MAYA será nueva en `Frontend/src/components/maya/` |

---

## 8. PATRONES DE CÓDIGO APROBADOS

### 8.1 Conexión a Base de Datos (AsyncPG)

```python
# ✅ CORRECTO - Usar pool centralizado
from db import get_pool

async def get_patients():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM pacientes")
        return [dict(row) for row in rows]

# ❌ INCORRECTO - No crear conexiones individuales
import psycopg2  # NO USAR
conn = psycopg2.connect(...)  # NO USAR
```

### 8.2 Endpoints FastAPI

```python
# ✅ CORRECTO
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/recurso", tags=["recurso"])

class RecursoCreate(BaseModel):
    nombre: str

@router.post("/")
async def crear_recurso(data: RecursoCreate):
    # lógica async
    pass
```

### 8.3 Componentes React

```typescript
// ✅ CORRECTO - Functional components con TypeScript
interface Props {
  pacienteId: number;
  onClose: () => void;
}

export const PacienteModal: React.FC<Props> = ({ pacienteId, onClose }) => {
  // hooks, lógica, render
};
```

---

## 9. REGLAS DE DESARROLLO

### 9.1 Reglas Generales

1. **Todo código nuevo DEBE usar AsyncPG** - No psycopg2/psycopg3
2. **No crear archivos .md innecesarios** - Solo actualizar CLAUDE.md
3. **No sobre-ingeniar** - Soluciones simples primero
4. **No agregar dependencias sin aprobación** - Consultar primero
5. **Mantener separación Frontend (MAYA) / Backend (Agentes)**

### 9.2 Para Otros Modelos de IA
>
> Cuando trabajes con otros modelos (GPT, Gemini, etc.), verificar que:

- [ ] No agreguen librerías fuera del stack aprobado
- [ ] No usen psycopg2 o conexiones síncronas
- [ ] No mezclen lógica de MAYA con agentes backend
- [ ] No creen archivos de documentación innecesarios
- [ ] Usen los patrones de código aprobados
- [ ] No instalen dependencias sin agregarlas aquí primero

### 9.3 Checklist de Revisión

```
□ ¿Usa AsyncPG para base de datos?
□ ¿Sigue la estructura de carpetas aprobada?
□ ¿No agrega dependencias nuevas no aprobadas?
□ ¿El código es async donde debe serlo?
□ ¿Mantiene separación MAYA (frontend) / Agentes (backend)?
□ ¿No crea archivos de documentación innecesarios?
```

---

## 10. DISEÑO DE MIGRACIÓN WHATSAPP

### 10.1 Fase Actual: whatsapp-web.js

```
Paciente → WhatsApp → whatsapp-web.js (Node) → Backend Python → Respuesta
```

### 10.2 Fase Producción: Twilio

```
Paciente → WhatsApp → Twilio API → Backend Python → Respuesta
```

### 10.3 Preparación para Migración

El código debe diseñarse con una **capa de abstracción** para que el cambio sea mínimo:

```python
# backend/whatsapp_bridge/provider.py

class WhatsAppProvider(ABC):
    @abstractmethod
    async def send_message(self, to: str, message: str): pass

    @abstractmethod
    async def get_status(self): pass

class WhatsAppWebJSProvider(WhatsAppProvider):
    # Implementación actual

class TwilioProvider(WhatsAppProvider):
    # Implementación futura
```

---

## 11. VARIABLES DE ENTORNO REQUERIDAS

```env
# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5432/podoskin
REDIS_URL=redis://localhost:6379

# Autenticación
JWT_SECRET_KEY=tu-clave-secreta
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# IA - Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# IA - Google (para MAYA y Gemini Flash)
GOOGLE_API_KEY=...

# WhatsApp (actual)
WHATSAPP_SERVICE_URL=http://localhost:3000

# WhatsApp (futuro - Twilio)
# TWILIO_ACCOUNT_SID=...
# TWILIO_AUTH_TOKEN=...
# TWILIO_WHATSAPP_NUMBER=...
```

---

## 12. HISTORIAL DE CAMBIOS

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-01-11 | Creación inicial del documento | Claude Opus 4.5 |

---

## 13. NOTAS DE SUPERVISIÓN

> Esta sección se actualiza cada vez que reviso trabajo de otros modelos de IA

### Revisiones Pendientes

- [ ] Verificar migración completa a AsyncPG
- [ ] Revisar integración Gemini Live con frontend
- [ ] Validar abstracción WhatsApp para migración Twilio
- [x] **CRÍTICO** - Sistema QR WhatsApp desconectado (ver `PLAN_CORRECCION_WHATSAPP_QR.md`)

### Planes de Corrección Activos

| Plan | Archivo | Estado | Prioridad |
|------|---------|--------|-----------|
| Flujo QR WhatsApp | `PLAN_CORRECCION_WHATSAPP_QR.md` | ✅ IMPLEMENTADO | CRÍTICA |

### Alertas

- **2026-01-11:** ~~Sistema QR tiene dos implementaciones paralelas desconectadas.~~ **RESUELTO** - Plan ejecutado, pendiente prueba en runtime.

---

**Este documento es la FUENTE ÚNICA DE VERDAD del proyecto.**
**Cualquier cambio de stack, arquitectura o dependencias DEBE reflejarse aquí.**
