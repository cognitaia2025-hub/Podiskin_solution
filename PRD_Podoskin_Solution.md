# Product Requirements Document (PRD)

## Podoskin Solution - Sistema de Gestión Clínica con IA

---

**Versión**: 1.0  
**Fecha**: 25 de Diciembre, 2024  
**Product Owner**: Dr. Santiago de Jesús Ornelas Reynoso  
**Equipo**: Desarrollo Podoskin

---

## 1. Visión del Producto

### 1.1 Propósito

Sistema integral de gestión clínica para podología que combina expedientes médicos digitales, asistencia por IA (voz y chat), CRM automatizado vía WhatsApp, y control operacional completo.

### 1.2 Objetivos del Producto

- Reducir 60% el tiempo de captura de datos en consulta
- Automatizar 80% de consultas de pacientes vía WhatsApp
- Cumplir 100% con normativas COFEPRIS
- Incrementar 20% los ingresos por paciente

### 1.3 Usuarios Objetivo

| Persona | Rol | Necesidades Principales |
|---------|-----|------------------------|
| Dr. Santiago | Podólogo | Captura rápida, historial completo, análisis de negocio |
| María (Recepción) | Administrativa | Agendamiento simple, cobros, reportes |
| Juan (Paciente) | Usuario final | Agendar fácil, respuestas rápidas, información clara |

---

## 2. Alcance del Producto

### 2.1 En Alcance (MVP)

✅ Expediente médico digital completo  
✅ Asistente de voz con Gemini Live (8 funciones)  
✅ Chatbot WhatsApp con escalamiento inteligente  
✅ Sistema de citas con recordatorios automáticos  
✅ Control de inventario básico  
✅ Gestión de pagos y facturación  
✅ Dashboard con KPIs principales  
✅ Generación de documentos COFEPRIS  

### 2.2 Fuera de Alcance (Futuro)

❌ App móvil nativa  
❌ Telemedicina con videollamadas  
❌ Integración con laboratorios externos  
❌ Sistema multi-clínica  

---

## 3. Requisitos Funcionales

### 3.1 Módulo: Expediente Médico Digital

#### RF-001: Captura de Datos del Paciente

**Prioridad**: Alta  
**Historia de Usuario**: Como podólogo, quiero capturar el expediente completo del paciente en menos de 10 minutos para optimizar mi tiempo de consulta.

**Criterios de Aceptación**:

- [ ] Sistema permite captura de 150+ campos estructurados
- [ ] Validación en tiempo real de campos obligatorios
- [ ] Auto-guardado cada 30 segundos
- [ ] Modo guiado (paso a paso) y modo libre (acordeón)
- [ ] Cálculo automático de IMC al ingresar peso/talla
- [ ] Búsqueda de paciente por nombre/teléfono en < 2 segundos

**Campos Clave**:

- Ficha de identificación (nombre, CURP, fecha nacimiento, contacto)
- Alergias con severidad
- Antecedentes médicos (heredofamiliares, patológicos, quirúrgicos)
- Estilo de vida (dieta, ejercicio, hábitos)
- Historia ginecológica (condicional para mujeres)

#### RF-002: Registro de Consulta Médica

**Prioridad**: Alta  
**Historia de Usuario**: Como podólogo, quiero registrar la consulta completa incluyendo diagnósticos y tratamientos para cumplir con COFEPRIS.

**Criterios de Aceptación**:

- [ ] Captura de signos vitales con cálculo automático de IMC
- [ ] Exploración física con campos estructurados
- [ ] Diagnósticos múltiples (presuntivo, definitivo, diferencial)
- [ ] Búsqueda de códigos CIE-10 (catálogo 30+ códigos)
- [ ] Plan de tratamiento con servicios del catálogo
- [ ] Indicaciones y pronóstico
- [ ] Generación automática de nota clínica

#### RF-003: Evolución del Tratamiento

**Prioridad**: Media  
**Historia de Usuario**: Como podólogo, quiero dar seguimiento a la evolución del tratamiento por fases para evaluar resultados.

**Criterios de Aceptación**:

- [ ] Registro de fases de evolución con fechas
- [ ] Clasificación de resultado (mejoría, sin cambios, empeoramiento)
- [ ] Indicaciones para siguiente fase
- [ ] Historial completo de evoluciones por paciente

---

### 3.2 Módulo: Asistente de Voz (Gemini Live)

#### RF-004: Captura por Voz en Consulta

**Prioridad**: Alta  
**Historia de Usuario**: Como podólogo, quiero dictar datos durante la consulta para no interrumpir la atención al paciente.

**Criterios de Aceptación**:

- [ ] Transcripción en tiempo real con latencia < 1 segundo
- [ ] Precisión de reconocimiento > 95%
- [ ] 8 funciones disponibles vía voice commands
- [ ] Confirmación verbal de acciones ejecutadas
- [ ] Auditoría completa de acciones de IA

**Funciones Implementadas**:

1. `update_vital_signs()` - Actualizar signos vitales
2. `update_physical_exam()` - Registrar exploración física
3. `add_diagnosis()` - Agregar diagnóstico
4. `query_patient_data()` - Consultar historial
5. `search_cie10()` - Buscar códigos CIE-10
6. `add_treatment()` - Agregar tratamiento
7. `generate_summary()` - Generar resumen
8. `save_consultation()` - Guardar consulta

**Ejemplo de Uso**:

```
Doctor: "Peso 75 kilos, talla 170, presión 120 sobre 80"
IA: "Registrado. Peso 75kg, talla 170cm, presión 120/80. IMC calculado: 25.95"

Doctor: "¿Tiene alergias este paciente?"
IA: "Sí, alergia a penicilina registrada desde marzo 2020, severidad moderada"
```

---

### 3.3 Módulo: Chatbot WhatsApp (Maya)

#### RF-005: Atención Automatizada 24/7

**Prioridad**: Alta  
**Historia de Usuario**: Como paciente, quiero obtener respuestas inmediatas a mis consultas en cualquier momento sin esperar horario de oficina.

**Criterios de Aceptación**:

- [ ] Respuesta en < 3 segundos
- [ ] Clasificación automática de intenciones (agendar, consulta, cancelar, info)
- [ ] 80% de consultas resueltas sin intervención humana
- [ ] Respuestas concisas (máx 2 oraciones)
- [ ] Simulación de escritura (typing indicator)

**Intenciones Soportadas**:

- **Agendar**: Validar disponibilidad y crear cita
- **Consulta**: Responder sobre servicios, precios, horarios
- **Cancelar**: Procesar cancelación/reagendamiento
- **Info**: Información general de la clínica
- **Emergencia**: Escalar a humano inmediatamente

#### RF-006: Sistema de Escalamiento Inteligente

**Prioridad**: Alta  
**Historia de Usuario**: Como administrador, quiero recibir notificaciones de dudas que el bot no puede resolver para responderlas y enriquecer la base de conocimiento.

**Criterios de Aceptación**:

- [ ] Detección automática de dudas no resueltas
- [ ] Notificación al admin con formato estructurado
- [ ] Respuesta del admin con formato `#RESPUESTA_XXX`
- [ ] Guardado automático en knowledge base
- [ ] Expiración de dudas pendientes (24 horas)

**Flujo de Escalamiento**:

```
1. Usuario: "¿Colocan uña postiza?"
2. Maya detecta que no sabe → Escala automáticamente
3. Admin recibe: "🔔 DUDA #1 de Santiago: ¿Colocan uña postiza?"
4. Admin responde: "#RESPUESTA_1\nSí, colocamos uña postiza temporal"
5. Sistema guarda en KB y responde al paciente
6. Próxima consulta similar se resuelve automáticamente
```

#### RF-007: Base de Conocimiento Auto-Aprendiente

**Prioridad**: Media  
**Historia de Usuario**: Como sistema, quiero aprender de las respuestas del administrador para mejorar automáticamente.

**Criterios de Aceptación**:

- [ ] Embeddings semánticos con all-MiniLM-L6-v2
- [ ] Búsqueda por similitud con threshold 0.85
- [ ] Auto-guardado de respuestas del admin
- [ ] Contador de veces consultada cada pregunta
- [ ] Categorización automática de preguntas

---

### 3.4 Módulo: Sistema de Citas

#### RF-008: Agendamiento con Validación

**Prioridad**: Alta  
**Historia de Usuario**: Como recepcionista, quiero agendar citas sin conflictos de horario para evitar sobrecupos.

**Criterios de Aceptación**:

- [ ] Validación automática de disponibilidad
- [ ] Bloqueos de agenda (vacaciones, días festivos)
- [ ] Duración configurable por tipo de servicio
- [ ] Asignación de podólogo
- [ ] Cero conflictos de horarios

#### RF-009: Recordatorios Automáticos

**Prioridad**: Alta  
**Historia de Usuario**: Como clínica, quiero enviar recordatorios automáticos para reducir no-shows en 30%.

**Criterios de Aceptación**:

- [ ] Recordatorio 24 horas antes vía WhatsApp
- [ ] Recordatorio 2 horas antes vía WhatsApp
- [ ] Confirmación de asistencia del paciente
- [ ] 100% de recordatorios enviados automáticamente

---

### 3.5 Módulo: Control de Inventario

#### RF-010: Gestión de Stock

**Prioridad**: Media  
**Historia de Usuario**: Como administrador, quiero controlar el inventario para evitar faltantes de materiales.

**Criterios de Aceptación**:

- [ ] Catálogo de productos con stock mínimo
- [ ] Alertas de stock bajo enviadas diariamente
- [ ] Descuento automático al completar cita
- [ ] Movimientos de entrada/salida registrados
- [ ] Valor del inventario en tiempo real

---

### 3.6 Módulo: Pagos y Facturación

#### RF-011: Procesamiento de Pagos

**Prioridad**: Alta  
**Historia de Usuario**: Como recepcionista, quiero registrar pagos rápidamente para no hacer esperar al paciente.

**Criterios de Aceptación**:

- [ ] Registro de pago en < 30 segundos
- [ ] Múltiples métodos (efectivo, tarjeta, transferencia)
- [ ] Pagos parciales con saldo pendiente
- [ ] Generación automática de nota de cobro
- [ ] Facturación electrónica con RFC

---

### 3.7 Módulo: Dashboard y KPIs

#### RF-012: Dashboard Ejecutivo

**Prioridad**: Media  
**Historia de Usuario**: Como propietario, quiero ver métricas clave del negocio en tiempo real para tomar decisiones.

**Criterios de Aceptación**:

- [ ] Dashboard carga en < 2 segundos
- [ ] KPIs principales: ingresos, pacientes, ocupación, cancelaciones
- [ ] Gráficas de tendencias mensuales
- [ ] Top tratamientos más solicitados
- [ ] Alertas del sistema (stock bajo, citas pendientes)

---

### 3.8 Módulo: Documentos COFEPRIS

#### RF-013: Generación de Documentos

**Prioridad**: Alta  
**Historia de Usuario**: Como podólogo, quiero generar documentos médicos automáticamente para cumplir con COFEPRIS.

**Criterios de Aceptación**:

- [ ] Generación en < 5 segundos
- [ ] Historial médico completo imprimible
- [ ] Notas clínicas con firmas digitales
- [ ] Consentimientos informados
- [ ] Control de archivo físico

---

## 4. Requisitos No Funcionales

### 4.1 Rendimiento

- **RNF-001**: Tiempo de respuesta de API < 500ms (p95)
- **RNF-002**: Dashboard carga en < 2 segundos
- **RNF-003**: Búsqueda de paciente en < 2 segundos
- **RNF-004**: Chatbot responde en < 3 segundos

### 4.2 Seguridad

- **RNF-005**: Encriptación de datos sensibles en reposo
- **RNF-006**: Autenticación con JWT tokens
- **RNF-007**: Control de acceso basado en roles (RBAC)
- **RNF-008**: Auditoría completa de acciones médicas
- **RNF-009**: Backup automático diario de base de datos

### 4.3 Usabilidad

- **RNF-010**: Interfaz responsive (desktop, tablet)
- **RNF-011**: Máximo 3 clics para funciones principales
- **RNF-012**: Mensajes de error claros y accionables
- **RNF-013**: Auto-guardado cada 30 segundos

### 4.4 Escalabilidad

- **RNF-014**: Soporte para 100+ pacientes simultáneos
- **RNF-015**: Base de datos soporta 10,000+ pacientes
- **RNF-016**: Chatbot maneja 50+ conversaciones simultáneas

### 4.5 Disponibilidad

- **RNF-017**: Uptime 99.5% (excluye mantenimiento programado)
- **RNF-018**: Chatbot disponible 24/7
- **RNF-019**: Tiempo de recuperación < 1 hora

---

## 5. Especificaciones Técnicas

### 5.1 Stack Tecnológico

**Frontend**

- React 18.3 + TypeScript
- Vite (build tool)
- Tailwind CSS
- React Router DOM
- React Hook Form + Zod

**Backend**

- FastAPI (Python 3.11+)
- LangGraph + LangChain
- Claude Haiku 3 (Anthropic)
- asyncio + asyncpg

**Base de Datos**

- PostgreSQL 16
- pgvector (embeddings)
- 42 tablas, 24 vistas, 15+ funciones

**IA y ML**

- Gemini Live (Google) - Asistente de voz
- Claude Haiku 3 (Anthropic) - Chatbot
- all-MiniLM-L6-v2 - Embeddings locales (384 dim)

**Mensajería**

- whatsapp-web.js (Node.js)
- LocalAuth (autenticación persistente)

### 5.2 Arquitectura

```
┌─────────────┐
│   Frontend  │ (React + TypeScript)
│   (Vite)    │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────┐
│  Backend    │ (FastAPI)
│  API REST   │
└──────┬──────┘
       │
   ┌───┴───┬────────┬─────────┐
   ▼       ▼        ▼         ▼
┌──────┐ ┌────┐ ┌──────┐ ┌────────┐
│ DB   │ │ IA │ │ RAG  │ │WhatsApp│
│ PG16 │ │LLM │ │Vector│ │ Bridge │
└──────┘ └────┘ └──────┘ └────────┘
```

### 5.3 Modelo de Datos (Resumen)

**42 Tablas Principales**:

- Usuarios y autenticación (2)
- Pacientes y expediente (6)
- Citas y tratamientos (8)
- CRM y chatbot (10)
- Asistente de voz (7)
- Inventario (3)
- Horarios (2)
- Documentos (2)
- Otras (2)

**24 Vistas**:

- Dashboard y KPIs (9)
- Reportes médicos (4)
- Inventario (4)
- Análisis (7)

---

## 6. Casos de Uso Detallados

### 6.1 UC-001: Consulta Médica con Asistente de Voz

**Actor**: Podólogo  
**Precondiciones**: Paciente registrado, sesión de voz iniciada  
**Flujo Principal**:

1. Podólogo dice: "Abrir expediente de Juan Pérez"
2. IA muestra expediente y confirma verbalmente
3. Podólogo dice: "Peso 80 kilos, talla 175, presión 130 sobre 85"
4. IA registra signos vitales y calcula IMC (26.12)
5. Podólogo pregunta: "¿Tiene alergias?"
6. IA responde: "Sí, alergia a ibuprofeno desde 2021"
7. Podólogo dice: "Diagnóstico: fascitis plantar, código M72.2"
8. IA registra diagnóstico con código CIE-10
9. Podólogo dice: "Guardar consulta"
10. IA genera resumen y guarda todo

**Postcondiciones**: Consulta guardada, nota clínica generada

### 6.2 UC-002: Agendamiento vía WhatsApp

**Actor**: Paciente  
**Precondiciones**: Paciente tiene WhatsApp  
**Flujo Principal**:

1. Paciente: "Hola, quiero agendar una cita"
2. Maya: "¿Para qué día te gustaría agendar?"
3. Paciente: "Mañana a las 3 pm"
4. Maya verifica disponibilidad
5. Maya: "Perfecto, te agendé para mañana 15:00. Te enviaré recordatorios"
6. Sistema crea cita en base de datos
7. Sistema programa recordatorios automáticos

**Postcondiciones**: Cita agendada, recordatorios programados

### 6.3 UC-003: Escalamiento de Duda

**Actor**: Paciente, Administrador  
**Precondiciones**: Maya no conoce la respuesta  
**Flujo Principal**:

1. Paciente: "¿Hacen cirugía de juanetes?"
2. Maya detecta que no sabe la respuesta
3. Maya: "Déjame consultarlo con el personal..."
4. Sistema crea duda en tabla `dudas_pendientes`
5. Sistema notifica al admin vía WhatsApp
6. Admin recibe: "🔔 DUDA #5: ¿Hacen cirugía de juanetes?"
7. Admin responde: "#RESPUESTA_5\nNo realizamos cirugías, solo tratamientos conservadores"
8. Sistema guarda en knowledge base
9. Sistema envía respuesta al paciente
10. Paciente recibe respuesta del admin

**Postcondiciones**: Duda respondida, knowledge base actualizada

---

## 7. Métricas de Éxito

### 7.1 KPIs del Producto

| Métrica | Baseline | Objetivo | Medición |
|---------|----------|----------|----------|
| Tiempo de captura de expediente | 25 min | < 10 min | Por consulta |
| Tiempo de agendamiento | 5 min | < 2 min | Por cita |
| Tasa de resolución chatbot | 50% | > 80% | Mensajes sin escalamiento |
| Precisión de IA (voz) | N/A | > 95% | Transcripciones correctas |
| Reducción de no-shows | Baseline | -30% | Comparado con mes anterior |
| Satisfacción del paciente | 3.5/5 | > 4.5/5 | Encuestas mensuales |

### 7.2 Métricas de Adopción

- **Semana 1**: 20% de consultas usan asistente de voz
- **Mes 1**: 50% de consultas usan asistente de voz
- **Mes 3**: 80% de consultas usan asistente de voz
- **Mes 6**: 90% de agendamientos vía WhatsApp

---

## 8. Plan de Lanzamiento

### 8.1 Fase 1: Alpha (Interno) - 2 semanas

- Pruebas con Dr. Santiago únicamente
- Validación de flujos principales
- Ajustes de usabilidad

### 8.2 Fase 2: Beta (Limitado) - 4 semanas

- 10 pacientes piloto para chatbot
- Personal administrativo usa sistema completo
- Recolección de feedback

### 8.3 Fase 3: Producción - Rollout gradual

- Semana 1: Expediente médico + asistente de voz
- Semana 2: Chatbot WhatsApp (50 pacientes)
- Semana 3: Sistema completo (todos los pacientes)
- Semana 4: Optimización y ajustes

---

## 9. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Baja precisión de voz | Media | Alto | Entrenamiento con casos reales, fallback a texto |
| Resistencia al cambio | Alta | Medio | Capacitación intensiva, soporte 24/7 |
| Costos de IA escalables | Baja | Medio | Monitoreo de uso, optimización de prompts |
| Fallas de WhatsApp API | Media | Alto | Sistema de reintentos, notificaciones alternativas |
| Pérdida de datos | Baja | Crítico | Backups automáticos diarios, redundancia |

---

## 10. Dependencias

### 10.1 Dependencias Externas

- API de Gemini Live (Google Cloud)
- API de Claude (Anthropic)
- WhatsApp Web (Meta)
- Servidor PostgreSQL

### 10.2 Dependencias Internas

- Catálogo de tratamientos completo
- Códigos CIE-10 actualizados
- Plantillas de documentos COFEPRIS
- Capacitación de personal

---

## 11. Criterios de Aceptación del Producto

### 11.1 Funcionales

- ✅ Todos los RF-001 a RF-013 implementados
- ✅ 8 funciones de voz operativas
- ✅ Chatbot con 80% de resolución automática
- ✅ Cero conflictos de horarios en agendamiento
- ✅ Documentos COFEPRIS generados correctamente

### 11.2 No Funcionales

- ✅ Todos los RNF-001 a RNF-019 cumplidos
- ✅ Rendimiento < 500ms en p95
- ✅ Uptime > 99.5%
- ✅ Seguridad: auditoría completa, encriptación

### 11.3 Negocio

- ✅ ROI > 200% en primer año
- ✅ Reducción 60% en tiempo de captura
- ✅ Incremento 20% en ingresos por paciente
- ✅ Satisfacción > 4.5/5

---

## 11. Mapeo de Requisitos a Agentes de Implementación

> **Nota**: Esta sección alinea los requisitos del PRD con la división de agentes del SRS para facilitar la asignación de tareas.

### 11.1 Agente 1: Database Setup

**Responsabilidad**: Infraestructura de datos

**Requisitos Asignados**:

- Base para todos los RF (RF-001 a RF-013)
- RNF-014, RNF-015: Escalabilidad de BD
- RNF-008: Auditoría de acciones
- RNF-009: Backup automático

**Entregables**:

- 42 tablas con esquemas completos
- 24 vistas materializadas
- 15+ funciones almacenadas
- Índices optimizados
- Scripts de migración

**Dependencias**: Ninguna (primer agente)

---

### 11.2 Agente 2: Backend API - Auth & Users

**Responsabilidad**: Autenticación y gestión de usuarios

**Requisitos Asignados**:

- RNF-005: Encriptación de datos
- RNF-006: Autenticación JWT
- RNF-007: Control de acceso (RBAC)

**Entregables**:

- Endpoints de login/logout
- Middleware de autenticación
- Sistema de roles y permisos
- Gestión de tokens JWT

**Dependencias**: Agente 1 (Database)

---

### 11.3 Agente 3: Backend API - Pacientes

**Responsabilidad**: Gestión de pacientes y expediente médico

**Requisitos Asignados**:

- RF-001: Captura de datos del paciente
- RF-002: Registro de consulta médica (parcial)
- RF-003: Evolución del tratamiento
- RNF-003: Búsqueda de paciente < 2s

**Entregables**:

- CRUD completo de pacientes
- Endpoints de alergias y antecedentes
- Validaciones Pydantic
- Búsqueda optimizada

**Dependencias**: Agente 1, Agente 2

---

### 11.4 Agente 4: Backend API - Citas

**Responsabilidad**: Sistema de agendamiento

**Requisitos Asignados**:

- RF-008: Agendamiento con validación
- RF-009: Recordatorios automáticos
- RNF-002: Dashboard carga < 2s (parcial)

**Entregables**:

- CRUD de citas
- Validación de disponibilidad
- Sistema de recordatorios
- Endpoints de horarios disponibles

**Dependencias**: Agente 1, Agente 2, Agente 3

---

### 11.5 Agente 5: Backend API - Tratamientos

**Responsabilidad**: Diagnósticos y tratamientos

**Requisitos Asignados**:

- RF-002: Registro de consulta médica (completar)
- RF-010: Gestión de stock (parcial)
- RF-011: Procesamiento de pagos
- RF-013: Generación de documentos (parcial)

**Entregables**:

- CRUD de tratamientos
- Diagnósticos con códigos CIE-10
- Signos vitales
- Notas clínicas
- Integración con inventario

**Dependencias**: Agente 1, Agente 2, Agente 4

---

### 11.6 Agente 6: LangGraph WhatsApp Agent

**Responsabilidad**: Chatbot inteligente (SubAgente independiente)

**Requisitos Asignados**:

- RF-005: Atención automatizada 24/7
- RF-006: Sistema de escalamiento inteligente
- RF-007: Base de conocimiento auto-aprendiente
- RNF-004: Chatbot responde < 3s
- RNF-016: 50+ conversaciones simultáneas
- RNF-018: Chatbot disponible 24/7

**Entregables**:

1. **Grafo LangGraph** (8 nodos):
   - `classify_intent`, `check_faq`, `check_patient`
   - `handle_appointment`, `handle_query`, `handle_cancellation`
   - `generate_response`, `post_process_escalation`

2. **Patrones LangGraph** (recomendaciones incorporadas):
   - `WhatsAppState(TypedDict)` → Estado tipado aislado
   - `checkpointer` persistente (MemorySaver → Redis/Postgres en prod)
   - `interrupt("waiting_admin_response:{ticket_id}")` para escalamiento
   - `Command(resume=...)` para reanudar tras respuesta admin

3. **Sistema de Aprendizaje**:
   - Cuando admin responde → guardar Q→A en pgvector
   - Campo `validated=true` para respuestas aprobadas
   - `save_faq(question, answer, meta)` tool

4. **Auditoría**:
   - Cada interacción registrada en `audit_logs`
   - Escalamientos con `ticket_id`, `admin_id`, `timestamp`

**Dependencias**: Agente 1, Agente 3, Agente 4

**Referencia**: [recomendacionesLangGraph.md](file:///c:/Users/Salva/OneDrive/Documentos/Database/recomendacionesLangGraph.md) (líneas 1-265)

---

### 11.7 Agente 7: Gemini Live + Orquestador

**Responsabilidad**: Asistente de voz + Orquestador de SubAgentes

**Requisitos Asignados**:

- RF-004: Captura por voz en consulta
- RNF-001: Tiempo de respuesta API < 500ms
- RNF-013: Auto-guardado cada 30s

**Entregables**:

1. **Frontend Gemini Live**:
   - 8 funciones de voz implementadas
   - Transcripción en tiempo real
   - Audio: resampleo a 16kHz PCM16, evitar feedback
   - NO exponer API key en cliente

2. **Backend Sessions (SEGURIDAD)**:
   - `POST /api/live/session/start` → Crea sesión segura
   - `POST /api/live/session/stop` → Cierra sesión
   - `POST /api/live/tool/call` → Ejecuta tools críticas en backend
   - Tokens efímeros con TTL y revocación

3. **Agente Padre Orquestador** (para consultas complejas):
   - Recibe peticiones complejas de Gemini Live
   - Delega a SubAgentes: Resúmenes, Análisis Clínico, Análisis Financiero
   - Valida respuestas antes de retornar
   - Modelo: Claude Sonnet 3.7

4. **SubAgentes de Producción** (grafos LangGraph independientes):
   - SubAgente Resúmenes: Genera resúmenes de consultas y WhatsApp
   - SubAgente Análisis Clínico: Evolución de pacientes, seguimientos
   - SubAgente Análisis Financiero: Reportes, anomalías, métricas

5. **Patrones LangGraph**:
   - `TypedDict` por SubAgente (estado aislado)
   - `checkpointer` persistente (Redis/Postgres)
   - `interrupt`/`resume` para validación humana
   - `audit_logs` obligatorios

**Dependencias**: Agente 1, Agente 2, Agente 3, Agente 5, Agente 6

**Implementación de Referencia**: [gemini-live-voice-controller/](file:///c:/Users/Salva/OneDrive/Documentos/Database/gemini-live-voice-controller) + [recomendacionesLangGraph.md](file:///c:/Users/Salva/OneDrive/Documentos/Database/recomendacionesLangGraph.md)

---

### 11.8 Agente 8: Frontend - Auth & Layout

**Responsabilidad**: Estructura base del frontend

**Requisitos Asignados**:

- RNF-010: Interfaz responsive
- RNF-011: Máximo 3 clics para funciones principales
- RNF-012: Mensajes de error claros

**Entregables**:

- Sistema de login/logout
- Layout principal con navegación
- Context de autenticación
- Componentes comunes reutilizables
- Routing con React Router

**Dependencias**: Agente 2 (Backend Auth)

---

### 11.9 Agente 9: Frontend - Pacientes

**Responsabilidad**: UI de gestión de pacientes

**Requisitos Asignados**:

- RF-001: Captura de datos del paciente (UI)
- RF-002: Registro de consulta médica (UI)
- RF-003: Evolución del tratamiento (UI)

**Entregables**:

- Lista de pacientes con búsqueda
- Formulario de expediente médico
- Modo guiado y modo libre
- Componentes de campos médicos
- Validación en tiempo real

**Dependencias**: Agente 3 (Backend Pacientes), Agente 8 (Frontend Auth)

---

### 11.10 Agente 10: Frontend - Citas

**Responsabilidad**: UI de agendamiento

**Requisitos Asignados**:

- RF-008: Agendamiento con validación (UI)
- RF-009: Recordatorios automáticos (UI)

**Entregables**:

- Calendario de citas
- Formulario de agendamiento
- Selector de horarios disponibles
- Vista de disponibilidad
- Confirmación de citas

**Dependencias**: Agente 4 (Backend Citas), Agente 8 (Frontend Auth)

---

### 11.11 Agente 11: Frontend - Dashboard

**Responsabilidad**: Visualización de métricas

**Requisitos Asignados**:

- RF-012: Dashboard ejecutivo
- RNF-002: Dashboard carga < 2s

**Entregables**:

- Dashboard con KPIs principales
- Gráficas de tendencias
- Reportes exportables
- Alertas del sistema
- Actualización en tiempo real

**Dependencias**: Agente 3, Agente 4, Agente 5, Agente 8

---

### 11.12 Agente 12: Testing & QA

**Responsabilidad**: Calidad y pruebas

**Requisitos Asignados**:

- Todos los RNF (validación)
- Criterios de aceptación (secciones 11.1, 11.2, 11.3)

**Entregables**:

- Tests unitarios (backend)
- Tests de integración
- Tests E2E (frontend)
- Documentación de APIs
- Reportes de cobertura

**Dependencias**: Todos los agentes anteriores

---

### 11.13 Orden de Implementación Sugerido

**Fase 1: Fundamentos** (Semanas 1-2)

1. ✅ Agente 1: Database Setup
2. ✅ Agente 2: Backend API - Auth & Users

**Fase 2: Backend Core** (Semanas 3-4)
3. ✅ Agente 3: Backend API - Pacientes
4. ✅ Agente 4: Backend API - Citas
5. ✅ Agente 5: Backend API - Tratamientos

**Fase 3: IA** (Semanas 5-6)
6. ✅ Agente 6: LangGraph WhatsApp Agent
7. ✅ Agente 7: Gemini Live Integration

**Fase 4: Frontend** (Semanas 7-8)
8. ✅ Agente 8: Frontend - Auth & Layout
9. ✅ Agente 9: Frontend - Pacientes
10. ✅ Agente 10: Frontend - Citas
11. ✅ Agente 11: Frontend - Dashboard

**Fase 5: QA** (Semanas 9-10)
12. ✅ Agente 12: Testing & QA

---

### 11.14 Criterios de Completitud por Agente

Cada agente debe cumplir:

- ✅ Cobertura de tests > 80%
- ✅ Documentación completa de APIs/componentes
- ✅ Code review aprobado
- ✅ Sin errores críticos de linting
- ✅ Integración exitosa con dependencias
- ✅ Todos los requisitos asignados implementados

---

## 12. Apéndices

### A. Glosario

- **CIE-10**: Clasificación Internacional de Enfermedades
- **COFEPRIS**: Comisión Federal para la Protección contra Riesgos Sanitarios
- **IMC**: Índice de Masa Corporal
- **LLM**: Large Language Model
- **RAG**: Retrieval-Augmented Generation
- **RF**: Requisito Funcional
- **RNF**: Requisito No Funcional

### B. Referencias

- [BRD_Podoskin_Solution.md](file:///c:/Users/Salva/OneDrive/Documentos/Database/BRD_Podoskin_Solution.md)
- [INFORME_TECNICO_AGENTE_LANGGRAPH.md](file:///c:/Users/Salva/OneDrive/Documentos/Database/Docs/INFORME_TECNICO_AGENTE_LANGGRAPH.md)
- [SISTEMA_WHATSAPP.md](file:///c:/Users/Salva/OneDrive/Documentos/Database/Docs/SISTEMA_WHATSAPP.md)

---

**Fin del PRD**
