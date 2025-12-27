# Sub-Agente de Operaciones - Podoskin Solution

## 📋 Descripción

Sub-agente de IA especializado en gestión operativa para el **personal de la clínica** Podoskin Solution. Diseñado para asistir a recepcionistas, doctores y administradores en tareas diarias.

> **IMPORTANTE**: Este agente es para uso exclusivo del personal de la clínica, NO para pacientes. Para atención a pacientes, usar el Sub-Agente de WhatsApp (Maya).

## ✨ Funcionalidades

### 📅 Gestión de Citas

- Consultar citas por fecha, paciente, estado o tratamiento
- Agendar nuevas citas con validación de disponibilidad
- Reagendar citas existentes
- Cancelar citas con razón opcional
- Verificar disponibilidad de horarios

### 👤 Gestión de Pacientes

- Buscar pacientes por nombre o teléfono
- Ver historial de citas de un paciente
- Crear nuevos pacientes
- Actualizar datos de pacientes existentes
- Detectar pacientes duplicados

### 📊 Reportes Operativos

- Estadísticas de citas por período
- Reportes por estado (pendiente, cancelada, completada)
- Tratamientos más solicitados
- Estadísticas de pacientes nuevos
- Reportes personalizados

### 🔍 Búsquedas Avanzadas

- Filtros múltiples combinados
- Búsquedas complejas con criterios específicos
- Ordenamiento personalizado

## 🏗️ Arquitectura

### Nodos Implementados (12/12)

1. **classify_intent_node** - Clasifica la intención del mensaje
2. **generate_response_node** - Genera respuestas estructuradas
3. **query_appointments_node** - Consulta citas
4. **query_patients_node** - Consulta pacientes
5. **create_appointment_node** - Crea citas
6. **reschedule_appointment_node** - Reagenda citas
7. **cancel_appointment_node** - Cancela citas
8. **update_patient_node** - Actualiza pacientes
9. **execute_action_node** - Ejecuta acciones confirmadas
10. **clarify_node** - Pide clarificación
11. **generate_report_node** - Genera reportes
12. **complex_search_node** - Búsquedas avanzadas

### Tools Disponibles (15+)

**Consultas:**

- `search_appointments()` - Buscar citas con filtros
- `get_appointment_by_id()` - Obtener cita por ID
- `check_availability()` - Verificar disponibilidad
- `search_patients()` - Buscar pacientes
- `get_patient_by_id()` - Obtener paciente por ID
- `get_patient_history()` - Historial de paciente

**Acciones:**

- `create_appointment()` - Crear cita
- `update_appointment()` - Actualizar cita
- `cancel_appointment()` - Cancelar cita
- `create_patient()` - Crear paciente
- `update_patient()` - Actualizar paciente

**Reportes:**

- `generate_appointment_stats()` - Estadísticas de citas
- `generate_patient_stats()` - Estadísticas de pacientes

**Validaciones:**

- `validate_appointment_data()` - Validar datos de cita
- `validate_patient_data()` - Validar datos de paciente
- `check_business_hours()` - Validar horario de atención
- `detect_duplicate_patient()` - Detectar duplicados

## 🚀 Uso

### Instalación de Dependencias

```bash
pip install langgraph langchain-anthropic pydantic-settings psycopg2
```

### Configuración

Crear archivo `.env` con:

```env
ANTHROPIC_API_KEY=tu_clave_api
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

### Ejemplo Básico

```python
from agents.sub_agent_operator import run_agent
from agents.sub_agent_operator.state import OperationsAgentState
from datetime import datetime

# Crear estado inicial
state = OperationsAgentState(
    session_id="session_001",
    user_id="user_123",
    user_name="Dr. García",
    current_message="¿Cuántas citas tengo hoy?",
    messages=[],
    timestamp=datetime.now().isoformat(),
    processing_stage="init",
)

# Ejecutar agente
result = await run_agent(state)

# Ver respuesta
print(result["response"])
```

## 📝 Ejemplos de Uso

### Consultar Citas

```
Usuario: "¿Cuántas citas tengo hoy?"
Agente: "Citas de hoy (5):
  • 9:00 AM - Juan Pérez (Onicomicosis)
  • 10:30 AM - María García (Pedicure)
  ..."
```

### Agendar Cita

```
Usuario: "Agenda a Juan Pérez para mañana a las 10 AM"
Agente: "¿Confirmar agendamiento?
  Paciente: Juan Pérez
  Fecha: 2024-12-24
  Hora: 10:00 AM
  Tratamiento: [especificar]
  
  Responde SÍ para confirmar."
```

### Generar Reporte

```
Usuario: "Dame un resumen de la semana"
Agente: "Resumen Semanal (18-24 Dic):
  Citas totales: 42
  ├─ Atendidas: 35 (83%)
  ├─ Canceladas: 5 (12%)
  └─ No-show: 2 (5%)"
```

## ⚙️ Configuración

### Horario de Atención

- **Lunes, Jueves, Viernes**: 8:30 AM - 6:30 PM
- **Sábado, Domingo**: 10:30 AM - 4:30 PM
- **Martes y Miércoles**: CERRADO

### Duración de Citas

- **Estándar**: 30-45 minutos
- **Mínimo**: 15 minutos
- **Máximo**: 120 minutos

### Formato de Respuestas

- Texto plano estructurado con viñetas
- Emojis para claridad visual
- Diagramas cuando sea necesario
- Conciso pero completo

## 🔒 Validaciones

El agente valida automáticamente:

- ✅ Datos requeridos completos
- ✅ Formatos de fecha y hora correctos
- ✅ Horarios dentro del horario de atención
- ✅ Disponibilidad de horarios
- ✅ No permitir fechas pasadas
- ✅ Detección de pacientes duplicados
- ✅ Formatos de teléfono y email

## 🛠️ Desarrollo

### Estructura del Proyecto

```
sub_agent_operator/
├── __init__.py
├── config.py          # Configuración
├── state.py           # Estado del agente
├── graph.py           # Grafo de LangGraph
├── nodes/             # Nodos del grafo
│   ├── classify_intent.py
│   ├── generate_response.py
│   ├── query_appointments.py
│   ├── query_patients.py
│   ├── create_appointment.py
│   ├── reschedule_appointment.py
│   ├── cancel_appointment.py
│   ├── update_patient.py
│   ├── execute_action.py
│   ├── clarify.py
│   ├── generate_report.py
│   └── complex_search.py
├── tools/             # Herramientas
│   ├── appointment_tools.py
│   ├── patient_tools.py
│   ├── action_tools.py
│   ├── patient_action_tools.py
│   └── report_tools.py
└── utils/             # Utilidades
    ├── database.py
    ├── validators.py
    └── formatters.py
```

### Agregar Nuevo Nodo

1. Crear archivo en `nodes/nuevo_nodo.py`
2. Implementar función async que reciba `OperationsAgentState`
3. Importar en `graph.py`
4. Agregar al grafo con `workflow.add_node()`
5. Conectar con edges apropiados

### Agregar Nuevo Tool

1. Crear función en `tools/categoria_tools.py`
2. Documentar parámetros y retorno
3. Manejar errores con try/except
4. Usar pool de conexiones para BD
5. Importar en nodo correspondiente

## 📊 Estado del Proyecto

- ✅ **Nodos**: 12/12 (100%)
- ✅ **Tools**: 15+ implementados
- ✅ **Validaciones**: Completas
- ✅ **Formatters**: Completos
- ✅ **Documentación**: Completa

## 🐛 Troubleshooting

### Error de Conexión a BD

```python
# Verificar DATABASE_URL en .env
# Verificar que PostgreSQL esté corriendo
# Verificar permisos de usuario
```

### Error de API Key

```python
# Verificar ANTHROPIC_API_KEY en .env
# Verificar que la key sea válida
```

### Clasificación Incorrecta

```python
# Revisar SYSTEM_PROMPT_CLASSIFIER en config.py
# Ajustar umbral de confianza (intent_confidence_threshold)
```

## 📚 Referencias

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Anthropic API](https://docs.anthropic.com/)
- [PostgreSQL](https://www.postgresql.org/docs/)

## 👥 Contacto

Para soporte o preguntas, contactar al equipo de desarrollo.

---

**Versión**: 1.0.0  
**Última actualización**: Diciembre 2024
