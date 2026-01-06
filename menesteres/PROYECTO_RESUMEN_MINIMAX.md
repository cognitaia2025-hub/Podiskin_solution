# Podoskin Solution - Resumen Proyecto para MiniMax

## 📁 Estructura del Proyecto

```
Database/
├── 📋 DOCUMENTACIÓN
│   ├── PRD_Podoskin_Solution.md     → Requisitos del producto
│   ├── SRS_Podoskin_Solution.md     → Especificaciones técnicas
│   ├── FSD_Podoskin_Solution.md     → Manual de construcción
│   ├── SUBAGENTES_CONFIG.md         → Configuración 12 agentes DEV
│   └── recomendacionesLangGraph.md  → Patrones LangGraph
│
├── 🗄️ /data - BASE DE DATOS (15 archivos SQL)
│   ├── 00_inicializacion.sql
│   ├── 01_funciones.sql
│   ├── 02_usuarios.sql
│   ├── 03_pacientes.sql
│   ├── 04_citas_tratamientos.sql
│   ├── 05_chatbot_crm.sql
│   ├── 06_vistas.sql
│   ├── 07_asistente_voz_consulta.sql
│   ├── 08_recordatorios_automatizacion.sql
│   ├── 09_inventario_materiales.sql
│   ├── 10_dashboard_kpis.sql
│   ├── 11_horarios_personal.sql
│   ├── 12_documentos_impresion.sql
│   ├── 13_dudas_pendientes.sql
│   ├── 14_knowledge_base.sql
│   └── GEMINI_LIVE_FUNCTIONS.md → 8 funciones de voz
│
├── ⚙️ /backend - PYTHON/FASTAPI
│   ├── whatsapp_bridge.py           → API Bridge para WhatsApp
│   ├── requirements.txt
│   └── /agents
│       ├── /sub_agent_whatsApp      → LangGraph WhatsApp (36 archivos)
│       └── /sub_agent_operator      → LangGraph Operaciones (31 archivos)
│
├── 💬 /whatsapp-web-js - CLIENTE NODE.JS
│   ├── index.js                     → Cliente whatsapp-web.js
│   ├── package.json                 → Deps: whatsapp-web.js, axios
│   └── /session                     → Sesión persistente
│
├── 🎨 /Frontend - REACT/TYPESCRIPT/VITE
│   ├── package.json
│   ├── vite.config.ts
│   └── /src
│       ├── App.tsx                  → Componente principal
│       ├── /components (25 archivos)
│       ├── /pages (5 archivos)
│       ├── /services (4 archivos)
│       ├── /context (3 archivos)
│       └── /types (2 archivos)
│
└── 🎙️ /gemini-live-voice-controller - REFERENCIA GEMINI LIVE
    ├── liveManager.ts
    ├── audioUtils.ts
    ├── constants.ts
    └── App.tsx
```

---

## 🔄 Arquitectura WhatsApp (whatsapp-web-js)

```
📱 WhatsApp Usuario
        ↓
🟢 whatsapp-web-js/index.js (Node.js)
        ↓ POST /webhook/whatsapp
⚡ backend/whatsapp_bridge.py (FastAPI)
        ↓
🤖 backend/agents/sub_agent_whatsApp (LangGraph)
        ↓
📩 Respuesta → simulateTyping → enviar
```

### Flujos implementados

1. **Normal**: Usuario → Maya → Respuesta automática
2. **Escalamiento**: Usuario → Maya → No sabe → Ticket admin → Admin responde → Aprende
3. **Admin Response**: Admin responde ticket → Maya envía al paciente original

---

## 📊 Estado de Desarrollo por Agente

| Agente | Rol | Estado | Archivos |
|--------|-----|--------|----------|
| 1 | Database Setup | ✅ Completo | 15 SQL |
| 2 | Backend Auth | 🔄 Parcial | - |
| 3 | Backend Pacientes | 🔄 Parcial | - |
| 4 | Backend Citas | 🔄 Parcial | - |
| 5 | Backend Clínico | 🔄 Parcial | - |
| 6 | WhatsApp Agent | ✅ Avanzado | 36 archivos |
| 7 | Gemini Live | 📋 Referencia | gemini-live-voice-controller |
| 8 | Frontend Auth | 🔄 Parcial | AuthContext, Login |
| 9 | Frontend Pacientes | 🔄 Parcial | Componentes |
| 10 | Frontend Citas | 🔄 Parcial | Componentes |
| 11 | Frontend Dashboard | 🔄 Parcial | Componentes |
| 12 | Testing | ⚪ Pendiente | - |

---

## 🎯 Prioridad de Trabajo

1. **Agente 2-5**: Completar endpoints REST del backend
2. **Agente 6**: Integrar patrones LangGraph actualizados (interrupt/resume)
3. **Agente 7**: Implementar sesiones seguras y Orquestador
4. **Agente 8-11**: Completar componentes frontend
5. **Agente 12**: Tests E2E

---

## 📝 Instrucciones para Agentes MiniMax

Cada agente activado debe:

1. Leer `SUBAGENTES_CONFIG.md` → Su sección específica
2. Consultar `SRS_Podoskin_Solution.md` y `FSD_Podoskin_Solution.md`
3. **Continuar desde el código existente**, NO empezar de cero
4. Seguir los patrones de `recomendacionesLangGraph.md` para agentes 6 y 7
