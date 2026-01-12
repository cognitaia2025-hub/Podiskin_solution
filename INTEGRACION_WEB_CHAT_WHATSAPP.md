# Integración Web Chat + WhatsApp - Agente Unificado Maya

## 📋 Resumen

Esta integración permite que **el mismo agente Maya** que atiende WhatsApp también procese mensajes desde el chat web del sitio podoskin-website.

### ✅ Características Clave

- **Agente Unificado**: Maya (`whatsapp_medico`) atiende ambos canales
- **Tablas Compartidas**: Reutiliza `pacientes`, `contactos`, `conversaciones`, `mensajes`
- **ID Único de Paciente**: Formato `[AP]-[NO]-[MMDD]-[####]` autogenerado
- **Sesiones Independientes**: Thread IDs separados por canal (`web_*` vs `whatsapp_*`)
- **Sin Duplicación**: Una sola tabla de pacientes para todos los canales

---

## 🗄️ Arquitectura de Base de Datos (REUTILIZACIÓN)

### Tablas EXISTENTES - NO se crean nuevas

#### 1. `pacientes` - Tabla Principal ✅ MODIFICADA
```sql
-- COLUMNAS EXISTENTES:
id BIGINT PRIMARY KEY (auto-increment)
primer_nombre TEXT NOT NULL
segundo_nombre TEXT
primer_apellido TEXT NOT NULL
segundo_apellido TEXT
fecha_nacimiento DATE NOT NULL
telefono_principal TEXT
email TEXT
activo BOOLEAN DEFAULT true
fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP

-- COLUMNAS NUEVAS AGREGADAS:
patient_id VARCHAR(20) UNIQUE          -- VA-AM-0504-0009 (autogenerado)
partial_id VARCHAR(15)                 -- VA-AM-0504
id_counter INTEGER DEFAULT 1           -- 9
```

**Trigger agregado:**
```sql
CREATE OR REPLACE FUNCTION generate_patient_id()
RETURNS TRIGGER AS $$
DECLARE
    last_name_part VARCHAR(2);
    first_name_part VARCHAR(2);
    date_part VARCHAR(4);
    counter_part VARCHAR(4);
    base_id VARCHAR(15);
    max_counter INTEGER;
BEGIN
    -- Extraer últimas 2 letras del apellido
    last_name_part := UPPER(SUBSTRING(REGEXP_REPLACE(NEW.primer_apellido, '[^a-zA-Z]', '', 'g') FROM '.{2}$'));
    
    -- Extraer últimas 2 letras del nombre
    first_name_part := UPPER(SUBSTRING(REGEXP_REPLACE(NEW.primer_nombre, '[^a-zA-Z]', '', 'g') FROM '.{2}$'));
    
    -- Extraer MMDD de fecha de nacimiento
    date_part := TO_CHAR(NEW.fecha_nacimiento, 'MMDD');
    
    -- Crear ID parcial
    base_id := last_name_part || '-' || first_name_part || '-' || date_part;
    NEW.partial_id := base_id;
    
    -- Buscar contador máximo para este base_id
    SELECT COALESCE(MAX(id_counter), 0) + 1 INTO max_counter
    FROM pacientes
    WHERE partial_id = base_id;
    
    NEW.id_counter := max_counter;
    counter_part := LPAD(max_counter::TEXT, 4, '0');
    
    -- Generar patient_id completo
    NEW.patient_id := base_id || '-' || counter_part;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_generate_patient_id
BEFORE INSERT ON pacientes
FOR EACH ROW
WHEN (NEW.patient_id IS NULL)
EXECUTE FUNCTION generate_patient_id();
```

#### 2. `contactos` - Relación Canal-Paciente ✅ SIN CAMBIOS
```sql
CREATE TABLE contactos (
    id BIGINT PRIMARY KEY,
    whatsapp_id TEXT,                  -- Para canal WhatsApp
    telegram_id TEXT,                  -- Para canal Telegram  
    facebook_id TEXT,                  -- Para canal Facebook
    id_paciente BIGINT REFERENCES pacientes(id),
    nombre TEXT,
    email TEXT,
    tipo TEXT,                         -- 'Prospecto', 'Lead_Calificado', 'Paciente_Convertido'
    origen TEXT,                       -- 'web', 'whatsapp', 'telegram', etc.
    activo BOOLEAN DEFAULT true,
    fecha_primer_contacto TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultima_interaccion TIMESTAMP
);
```

**Uso:**
- WhatsApp: `whatsapp_id = "+526861083647"`, `origen = 'whatsapp'`
- Web: `origen = 'web'` (sin campo específico de canal)
- Ambos canales comparten `id_paciente` → **MISMO PACIENTE**

#### 3. `conversaciones` - Sesiones Multi-Canal ✅ MODIFICADA
```sql
-- COLUMNAS EXISTENTES:
id BIGINT PRIMARY KEY
id_contacto BIGINT REFERENCES contactos(id)
canal TEXT CHECK (canal IN ('whatsapp', 'telegram', 'facebook', 'web', 'sms'))
estado TEXT DEFAULT 'Activa'
fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
fecha_ultima_actividad TIMESTAMP DEFAULT CURRENT_TIMESTAMP
numero_mensajes INTEGER DEFAULT 0
numero_mensajes_bot INTEGER DEFAULT 0
numero_mensajes_humano INTEGER DEFAULT 0

-- COLUMNA NUEVA AGREGADA:
session_id UUID DEFAULT gen_random_uuid()  -- Para frontend web
```

**Diferenciación por canal:**
- WhatsApp: `canal = 'whatsapp'`, sin `session_id` necesario
- Web: `canal = 'web'`, `session_id = UUID` para frontend

#### 4. `mensajes` - Historial de Mensajes ✅ SIN CAMBIOS
```sql
CREATE TABLE mensajes (
    id BIGINT PRIMARY KEY,
    id_conversacion BIGINT REFERENCES conversaciones(id),
    direccion TEXT CHECK (direccion IN ('Entrante', 'Saliente')),
    enviado_por_tipo TEXT CHECK (enviado_por_tipo IN ('Contacto', 'Bot', 'Usuario_Sistema')),
    tipo_contenido TEXT DEFAULT 'Texto',
    contenido TEXT NOT NULL,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_entrega TEXT DEFAULT 'Enviado'
);
```

**Uso sin cambios:**
- Mensajes web: `enviado_por_tipo = 'Contacto'` (usuario) o `'Bot'` (Maya)
- Canal se determina por `conversaciones.canal` (JOIN)

---

## 🔧 Componentes Backend

### Archivo: `backend/api/web_chat_api.py` ✅ CORREGIDO

#### Endpoints Principales

##### 1. POST `/api/chatbot/message`
Procesa mensajes del chat web usando el agente Maya.

**Request:**
```json
{
  "message": "¿Cuáles son los horarios?",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-12T10:30:00Z",
  "patient_info": {
    "patient_id": "VA-AM-0504-0009",
    "first_name": "Amelia",
    "first_last_name": "Vargas",
    "is_registered": true
  }
}
```

**Response:**
```json
{
  "response": "¡Hola Amelia! 😊 Nuestros horarios son...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-12T10:30:02Z",
  "patient_id": "VA-AM-0504-0009",
  "suggestions": [
    "Agendar una cita",
    "Ver servicios",
    "Hablar con un asesor"
  ]
}
```

**Flujo Interno (usando tablas existentes):**
```python
1. Buscar paciente en `pacientes` por `patient_id`
   └─> SELECT id FROM pacientes WHERE patient_id = 'VA-AM-0504-0009'

2. Buscar/crear contacto en `contactos`
   └─> INSERT INTO contactos (id_paciente, origen, nombre, tipo) 
       VALUES (123, 'web', 'Amelia Vargas', 'Lead_Calificado')
       ON CONFLICT (id_paciente) DO UPDATE SET fecha_ultima_interaccion = NOW()

3. Buscar/crear conversación en `conversaciones`
   └─> INSERT INTO conversaciones (id_contacto, canal, session_id, estado)
       VALUES (456, 'web', '550e8400...', 'Activa')
       ON CONFLICT (session_id) DO UPDATE SET fecha_ultima_actividad = NOW()

4. Guardar mensaje usuario en `mensajes`
   └─> INSERT INTO mensajes (id_conversacion, direccion, enviado_por_tipo, contenido)
       VALUES (789, 'Entrante', 'Contacto', '¿Cuáles son los horarios?')

5. Ejecutar agente Maya
   └─> thread_id = "web_550e8400..."
       config = {"configurable": {"thread_id": thread_id}}
       result = await whatsapp_graph.ainvoke(initial_state, config=config)

6. Guardar respuesta bot en `mensajes`
   └─> INSERT INTO mensajes (id_conversacion, direccion, enviado_por_tipo, contenido)
       VALUES (789, 'Saliente', 'Bot', 'Nuestros horarios son...')

7. Actualizar contadores en `conversaciones`
   └─> UPDATE conversaciones SET numero_mensajes_bot = numero_mensajes_bot + 1
       WHERE id = 789
```

##### 2. POST `/api/patient/register`
Registra un nuevo paciente (trigger genera `patient_id` automáticamente).

**Request:**
```json
{
  "first_name": "Amelia",
  "second_name": null,
  "first_last_name": "Vargas",
  "second_last_name": "Mendoza",
  "birth_date": "1995-05-04"
}
```

**Response:**
```json
{
  "success": true,
  "patient_id": "VA-AM-0504-0009",
  "message": "Paciente registrado exitosamente"
}
```

**Flujo Interno:**
```python
# Backend NO calcula el ID, solo inserta datos básicos
INSERT INTO pacientes (
    primer_nombre, segundo_nombre, primer_apellido, segundo_apellido,
    fecha_nacimiento, activo
) 
VALUES ('Amelia', NULL, 'Vargas', 'Mendoza', '1995-05-04', true)
RETURNING id, patient_id;

# Trigger genera automáticamente:
# - partial_id = "VA-AM-0504"
# - id_counter = 9 (siguiente disponible)
# - patient_id = "VA-AM-0504-0009"
```

##### 3. POST `/api/patient/lookup`
Busca un paciente existente.

**Request (por ID):**
```json
{
  "patient_id": "VA-AM-0504-0009"
}
```

**Request (por datos):**
```json
{
  "first_name": "Amelia",
  "first_last_name": "Vargas",
  "birth_date": "1995-05-04"
}
```

**Response:**
```json
{
  "found": true,
  "patient_id": "VA-AM-0504-0009",
  "first_name": "Amelia",
  "first_last_name": "Vargas",
  "registration_date": "2025-01-10T08:00:00Z"
}
```

**Flujo Interno:**
```python
# Opción 1: Búsqueda por patient_id
SELECT id, patient_id, primer_nombre, primer_apellido, fecha_creacion
FROM pacientes
WHERE patient_id = 'VA-AM-0504-0009';

# Opción 2: Búsqueda por datos personales
SELECT id, patient_id, primer_nombre, primer_apellido, fecha_creacion
FROM pacientes
WHERE LOWER(primer_nombre) = LOWER('Amelia')
  AND LOWER(primer_apellido) = LOWER('Vargas')
  AND fecha_nacimiento = '1995-05-04'
LIMIT 1;
```

---

## 🔄 Flujo de Integración Completo

### Escenario 1: Usuario Nuevo (Web Chat)

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Usuario visita podoskin-website                             │
│    └─> Frontend genera session_id (UUID): "550e8400..."        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. Usuario escribe: "Hola, ¿cuáles son sus precios?"           │
│    └─> POST /api/chatbot/message                               │
│        - session_id: "550e8400..."                             │
│        - patient_info: null (no registrado)                     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. Backend (web_chat_api.py)                                   │
│    ├─> INSERT conversaciones (canal='web', session_id)         │
│    ├─> INSERT mensajes (enviado_por_tipo='Contacto')           │
│    ├─> Ejecuta Maya: thread_id="web_550e8400..."               │
│    ├─> Maya consulta knowledge_base                             │
│    ├─> INSERT mensajes (enviado_por_tipo='Bot')                │
│    └─> Response: "¡Hola! 😊 Nuestros precios varían..."         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. Maya sugiere registro después de N mensajes                 │
│    "Para darte mejor servicio, ¿me compartes tu nombre?"       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. Usuario proporciona: "Amelia Vargas, 04/05/1995"            │
│    └─> Frontend llama POST /api/patient/lookup                 │
│        - first_name: "Amelia"                                   │
│        - first_last_name: "Vargas"                              │
│        - birth_date: "1995-05-04"                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. Backend busca en `pacientes`                                 │
│    └─> SELECT * FROM pacientes                                 │
│        WHERE LOWER(primer_nombre) = 'amelia'                    │
│        AND LOWER(primer_apellido) = 'vargas'                    │
│        AND fecha_nacimiento = '1995-05-04'                      │
│    └─> Result: {found: false}                                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. Frontend llama POST /api/patient/register                   │
│    └─> Backend ejecuta:                                        │
│        INSERT INTO pacientes (                                  │
│            primer_nombre, primer_apellido, fecha_nacimiento     │
│        ) VALUES ('Amelia', 'Vargas', '1995-05-04')              │
│        RETURNING id, patient_id;                                │
│                                                                 │
│    └─> Trigger genera patient_id: "VA-AM-0504-0009"            │
│        - partial_id: "VA-AM-0504"                               │
│        - id_counter: 9                                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. Frontend actualiza estado                                   │
│    patient_info.patient_id = "VA-AM-0504-0009"                  │
│    patient_info.is_registered = true                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 9. Mensajes subsecuentes incluyen patient_id                   │
│    └─> Backend vincula conversación con paciente:              │
│        - Busca paciente: id = 123                               │
│        - Crea contacto: INSERT contactos (id_paciente=123)      │
│        - Actualiza conversación: UPDATE conversaciones          │
│          SET id_contacto = 456 WHERE session_id = '550e8400...' │
└─────────────────────────────────────────────────────────────────┘
```

### Escenario 2: Usuario Existente (WhatsApp → Web)

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. Paciente "Amelia Vargas" ya registrado vía WhatsApp          │
│    TABLA: pacientes                                              │
│    └─> id: 123, patient_id: "VA-AM-0504-0009"                   │
│        primer_nombre: "Amelia", primer_apellido: "Vargas"        │
│                                                                  │
│    TABLA: contactos                                              │
│    └─> id: 456, id_paciente: 123                                │
│        whatsapp_id: "+526861083647", origen: 'whatsapp'          │
│                                                                  │
│    TABLA: conversaciones                                         │
│    └─> id: 789, id_contacto: 456, canal: 'whatsapp'             │
│        (Historial de conversaciones WhatsApp)                    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ 2. Amelia visita podoskin-website                               │
│    └─> Frontend genera nuevo session_id: "770e9500..."          │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ 3. Amelia proporciona datos en el chat web                      │
│    └─> POST /api/patient/lookup                                 │
│        - first_name: "Amelia"                                    │
│        - first_last_name: "Vargas"                               │
│        - birth_date: "1995-05-04"                                │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ 4. Backend ENCUENTRA paciente existente                         │
│    └─> SELECT * FROM pacientes WHERE ...                        │
│        Result: {found: true, patient_id: "VA-AM-0504-0009"}      │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ 5. Frontend guarda patient_id en estado local                   │
│    patient_info.patient_id = "VA-AM-0504-0009"                   │
│    patient_info.is_registered = true                             │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ 6. Mensajes subsecuentes incluyen patient_id                    │
│    POST /api/chatbot/message                                     │
│    - session_id: "770e9500..."                                   │
│    - patient_info: {patient_id: "VA-AM-0504-0009"}               │
│    - message: "Quiero agendar una cita"                          │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ 7. Backend vincula web con paciente existente                   │
│    ├─> Busca paciente: id = 123 (MISMO que WhatsApp)            │
│    ├─> Busca/crea contacto web:                                 │
│    │   INSERT INTO contactos (id_paciente=123, origen='web')    │
│    │   ON CONFLICT DO NOTHING                                    │
│    │   └─> id: 900 (nuevo contacto web)                         │
│    ├─> Crea conversación web:                                   │
│    │   INSERT INTO conversaciones (                              │
│    │       id_contacto=900, canal='web', session_id='770e9500...'│
│    │   )                                                          │
│    │   └─> id: 1000 (nueva conversación web)                    │
│    └─> Maya tiene ACCESO COMPLETO al historial:                 │
│        - Conversación WhatsApp (id: 789)                         │
│        - Conversación Web (id: 1000)                             │
│        - Todos los mensajes de ambos canales                     │
│                                                                  │
│    ✅ VENTAJA: Maya puede decir:                                 │
│       "Hola Amelia! Vi que me escribiste por WhatsApp ayer       │
│        sobre los precios. ¿Quieres agendar tu cita ahora?"       │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Instalación y Configuración

### 1. Aplicar Migración SQL

```bash
cd /workspaces/Podiskin_solution
psql -U postgres -d podoskin_db -f data/migrations/20_web_chat_integration.sql
```

**Verifica:**
```sql
-- Verificar columnas nuevas en pacientes
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'pacientes' 
  AND column_name IN ('patient_id', 'partial_id', 'id_counter');

-- Resultado esperado:
-- patient_id   | character varying | YES
-- partial_id   | character varying | YES
-- id_counter   | integer           | YES

-- Verificar trigger
SELECT trigger_name, event_object_table, action_timing, event_manipulation
FROM information_schema.triggers
WHERE trigger_name = 'trigger_generate_patient_id';

-- Resultado esperado:
-- trigger_generate_patient_id | pacientes | BEFORE | INSERT

-- Verificar vistas
SELECT table_name, view_definition 
FROM information_schema.views 
WHERE table_name IN ('web_chat_sessions', 'web_chat_messages');

-- Resultado esperado:
-- web_chat_sessions  | SELECT c.id, c.session_id, ...
-- web_chat_messages  | SELECT m.id, c.session_id, ...

-- Probar trigger con INSERT de prueba
INSERT INTO pacientes (
    primer_nombre, primer_apellido, fecha_nacimiento, activo
) 
VALUES ('TEST', 'USER', '2000-01-01', false)
RETURNING id, patient_id, partial_id, id_counter;

-- Resultado esperado:
-- id  | patient_id      | partial_id | id_counter
-- 999 | ER-ST-0101-0001 | ER-ST-0101 | 1

-- Limpiar registro de prueba
DELETE FROM pacientes WHERE primer_nombre = 'TEST' AND primer_apellido = 'USER';
```

### 2. Verificar Router en main.py

El router ya debe estar registrado desde las correcciones anteriores:

```python
# backend/main.py
from api.web_chat_api import router as web_chat_router

app.include_router(web_chat_router)
```

### 3. Probar Endpoints

```bash
# Health check
curl http://localhost:8000/api/chatbot/health

# Resultado esperado:
{
  "status": "ok",
  "message": "Web Chat API funcionando correctamente",
  "agent": "whatsapp_medico (Maya)",
  "channel": "web",
  "timestamp": "2025-01-12T10:00:00Z"
}

# Buscar paciente (no existe)
curl -X POST http://localhost:8000/api/patient/lookup \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Amelia",
    "first_last_name": "Vargas",
    "birth_date": "1995-05-04"
  }'

# Resultado esperado:
{
  "found": false,
  "patient_id": null,
  "first_name": null,
  "first_last_name": null,
  "registration_date": null
}

# Registrar paciente
curl -X POST http://localhost:8000/api/patient/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Amelia",
    "first_last_name": "Vargas",
    "birth_date": "1995-05-04"
  }'

# Resultado esperado:
{
  "success": true,
  "patient_id": "VA-AM-0504-0001",
  "message": "Paciente registrado exitosamente"
}

# Buscar paciente (ahora existe)
curl -X POST http://localhost:8000/api/patient/lookup \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "VA-AM-0504-0001"
  }'

# Resultado esperado:
{
  "found": true,
  "patient_id": "VA-AM-0504-0001",
  "first_name": "Amelia",
  "first_last_name": "Vargas",
  "registration_date": "2025-01-12T10:05:00Z"
}
```

---

## 📝 Resumen de Cambios

### Archivos Modificados:

1. **`data/migrations/20_web_chat_integration.sql`** ✅ CORREGIDO
   - Extiende tabla `pacientes` con columnas `patient_id`, `partial_id`, `id_counter`
   - Agrega trigger `generate_patient_id()` para autogenerar IDs
   - Extiende tabla `conversaciones` con columna `session_id`
   - Crea vistas `web_chat_sessions` y `web_chat_messages`
   - Crea funciones auxiliares (`get_or_create_web_contact`, `find_patient_by_name_and_birthdate`, `cleanup_old_web_sessions`)

2. **`backend/api/web_chat_api.py`** ✅ CORREGIDO
   - Usa tabla `pacientes` (no `patients`)
   - Usa tabla `contactos` (no crea nueva)
   - Usa tabla `conversaciones` (no `chat_sessions`)
   - Usa tabla `mensajes` (no `chat_messages`)
   - Mapea nombres de campos en español (`primer_nombre`, `primer_apellido`, etc.)
   - Ejecuta agente Maya con thread_id único por canal

3. **`backend/main.py`** ✅ YA REGISTRADO (correcciones anteriores)
   - Router `web_chat_router` incluido

---

## ✅ Ventajas de Reutilizar Tablas

1. **Una sola fuente de verdad**: Un paciente es el mismo en web y WhatsApp
2. **Historial completo**: Maya puede ver todas las interacciones sin importar el canal
3. **No duplicación**: `patient_id` único para todos los canales
4. **Mantenimiento simplificado**: Cambios en estructura afectan todos los canales
5. **Reportes unificados**: Estadísticas y analytics consolidados
6. **Escalabilidad**: Agregar nuevos canales (Telegram, Facebook) reutiliza la misma estructura

---

## 🎯 Próximos Pasos

1. **Frontend (podoskin-website)**:
   - Integrar llamadas a `/api/chatbot/message`
   - Implementar flujo de registro/búsqueda de paciente
   - Mostrar sugerencias contextuales

2. **Testing**:
   - Probar flujo completo web → registro → chat
   - Probar flujo WhatsApp → web (mismo paciente)
   - Verificar que historial se comparte entre canales

3. **Monitoreo**:
   - Agregar métricas de uso por canal
   - Monitorear performance de búsquedas
   - Alertas de errores en conversaciones

---

## 📚 Referencias

- Agente WhatsApp: `backend/agents/whatsapp_medico/`
- Tablas base de datos: `data/03_pacientes.sql`, `data/05_chatbot_crm.sql`
- Documentación LangGraph: https://python.langchain.com/docs/langgraph
