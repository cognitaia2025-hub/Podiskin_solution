# Software Requirements Specification (SRS)

## Podoskin Solution - Especificación Técnica Detallada

---

**Versión**: 1.0  
**Fecha**: 25 de Diciembre, 2024  
**Equipo Técnico**: Desarrollo Podoskin  
**Propósito**: Documentación técnica para implementación por agentes de IA

---

## 1. Introducción

### 1.1 Propósito del Documento

Este SRS define las especificaciones técnicas detalladas para implementar Podoskin Solution. Cada sección está diseñada para ser asignada a agentes de IA especializados.

### 1.2 Alcance del Sistema

Sistema web full-stack con IA integrada para gestión clínica de podología.

### 1.3 Definiciones y Acrónimos

- **API**: Application Programming Interface
- **CRUD**: Create, Read, Update, Delete
- **DTO**: Data Transfer Object
- **JWT**: JSON Web Token
- **ORM**: Object-Relational Mapping
- **REST**: Representational State Transfer
- **SPA**: Single Page Application
- **SSE**: Server-Sent Events
- **WebSocket**: Protocolo de comunicación bidireccional

---

## 2. Arquitectura del Sistema

### 2.1 Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                     CAPA DE PRESENTACIÓN                     │
│  React 18.3 + TypeScript + Vite + Tailwind CSS              │
│  - Componentes reutilizables                                │
│  - Context API para estado global                           │
│  - React Router para navegación                             │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     CAPA DE APLICACIÓN                       │
│  FastAPI (Python 3.11+)                                      │
│  - Endpoints REST                                            │
│  - Middleware de autenticación                               │
│  - Validación con Pydantic                                   │
│  - Manejo de errores centralizado                            │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ CAPA NEGOCIO │  │  CAPA IA     │  │ CAPA MENSAJ. │
│              │  │              │  │              │
│ - Servicios  │  │ - LangGraph  │  │ - WhatsApp   │
│ - Validación │  │ - Claude API │  │   Bridge     │
│ - Lógica     │  │ - Gemini API │  │ - Node.js    │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └────────────────┬┴─────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                     CAPA DE DATOS                            │
│  PostgreSQL 16 + pgvector                                    │
│  - 42 tablas relacionales                                    │
│  - 24 vistas materializadas                                  │
│  - 15+ funciones almacenadas                                 │
│  - Índices optimizados                                       │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Patrones de Diseño

**Backend**:

- **Repository Pattern**: Abstracción de acceso a datos
- **Service Layer**: Lógica de negocio separada
- **Dependency Injection**: FastAPI dependencies
- **Factory Pattern**: Creación de agentes LangGraph
- **Strategy Pattern**: Diferentes estrategias de IA según contexto

**Frontend**:

- **Component Composition**: Componentes reutilizables
- **Context Provider Pattern**: Estado global
- **Custom Hooks**: Lógica reutilizable
- **Render Props**: Componentes flexibles

---

## 3. Especificaciones de Base de Datos

### 3.1 Esquema de Base de Datos

#### 3.1.1 Tablas de Usuarios y Autenticación

**Tabla: `usuarios`**

```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('admin', 'podologo', 'recepcion')),
    activo BOOLEAN DEFAULT true,
    ultimo_acceso TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_username ON usuarios(username);
```

**Tabla: `podologos`**

```sql
CREATE TABLE podologos (
    id SERIAL PRIMARY KEY,
    id_usuario INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    cedula_profesional VARCHAR(20) UNIQUE NOT NULL,
    especialidad VARCHAR(100),
    telefono VARCHAR(15),
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_podologos_cedula ON podologos(cedula_profesional);
```

#### 3.1.2 Tablas de Pacientes

**Tabla: `pacientes`**

```sql
CREATE TABLE pacientes (
    id SERIAL PRIMARY KEY,
    primer_nombre VARCHAR(50) NOT NULL,
    segundo_nombre VARCHAR(50),
    primer_apellido VARCHAR(50) NOT NULL,
    segundo_apellido VARCHAR(50),
    fecha_nacimiento DATE NOT NULL,
    sexo CHAR(1) CHECK (sexo IN ('M', 'F', 'O')),
    curp VARCHAR(18) UNIQUE,
    telefono_principal VARCHAR(15) NOT NULL,
    telefono_secundario VARCHAR(15),
    email VARCHAR(100),
    calle VARCHAR(100),
    numero_exterior VARCHAR(10),
    numero_interior VARCHAR(10),
    colonia VARCHAR(100),
    ciudad VARCHAR(100),
    estado VARCHAR(50),
    codigo_postal VARCHAR(10),
    ocupacion VARCHAR(100),
    estado_civil VARCHAR(20),
    referencia VARCHAR(255),
    activo BOOLEAN DEFAULT true,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pacientes_nombre ON pacientes(primer_nombre, primer_apellido);
CREATE INDEX idx_pacientes_telefono ON pacientes(telefono_principal);
CREATE INDEX idx_pacientes_curp ON pacientes(curp);
CREATE INDEX idx_pacientes_activo ON pacientes(activo);
```

**Tabla: `alergias`**

```sql
CREATE TABLE alergias (
    id SERIAL PRIMARY KEY,
    id_paciente INTEGER REFERENCES pacientes(id) ON DELETE CASCADE,
    tipo VARCHAR(50) CHECK (tipo IN ('Medicamento', 'Alimento', 'Ambiental', 'Material', 'Otro')),
    nombre VARCHAR(100) NOT NULL,
    reaccion TEXT,
    severidad VARCHAR(20) CHECK (severidad IN ('Leve', 'Moderada', 'Grave', 'Mortal')),
    fecha_diagnostico DATE,
    notas TEXT,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alergias_paciente ON alergias(id_paciente);
CREATE INDEX idx_alergias_activo ON alergias(activo);
```

#### 3.1.3 Tablas de Citas

**Tabla: `citas`**

```sql
CREATE TABLE citas (
    id SERIAL PRIMARY KEY,
    id_paciente INTEGER REFERENCES pacientes(id) ON DELETE RESTRICT,
    id_podologo INTEGER REFERENCES podologos(id) ON DELETE RESTRICT,
    fecha_hora_inicio TIMESTAMP NOT NULL,
    fecha_hora_fin TIMESTAMP NOT NULL,
    tipo_cita VARCHAR(20) CHECK (tipo_cita IN ('Consulta', 'Seguimiento', 'Urgencia')),
    estado VARCHAR(20) DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente', 'Confirmada', 'En_Curso', 'Completada', 'Cancelada', 'No_Asistio')),
    motivo_consulta TEXT,
    notas_recepcion TEXT,
    motivo_cancelacion TEXT,
    es_primera_vez BOOLEAN DEFAULT false,
    recordatorio_24h_enviado BOOLEAN DEFAULT false,
    recordatorio_2h_enviado BOOLEAN DEFAULT false,
    creado_por INTEGER REFERENCES usuarios(id),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_fecha_fin CHECK (fecha_hora_fin > fecha_hora_inicio)
);

CREATE INDEX idx_citas_paciente ON citas(id_paciente);
CREATE INDEX idx_citas_podologo ON citas(id_podologo);
CREATE INDEX idx_citas_fecha ON citas(fecha_hora_inicio);
CREATE INDEX idx_citas_estado ON citas(estado);
CREATE INDEX idx_citas_recordatorios ON citas(recordatorio_24h_enviado, recordatorio_2h_enviado) WHERE estado = 'Confirmada';
```

**Tabla: `signos_vitales`**

```sql
CREATE TABLE signos_vitales (
    id SERIAL PRIMARY KEY,
    id_cita INTEGER REFERENCES citas(id) ON DELETE CASCADE,
    peso_kg DECIMAL(5,2),
    talla_cm DECIMAL(5,2),
    imc DECIMAL(5,2) GENERATED ALWAYS AS (peso_kg / POWER(talla_cm/100, 2)) STORED,
    presion_sistolica INTEGER,
    presion_diastolica INTEGER,
    frecuencia_cardiaca INTEGER,
    frecuencia_respiratoria INTEGER,
    temperatura_celsius DECIMAL(4,2),
    saturacion_oxigeno INTEGER,
    glucosa_capilar INTEGER,
    medido_por INTEGER REFERENCES usuarios(id),
    fecha_medicion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_signos_vitales_cita ON signos_vitales(id_cita);
```

#### 3.1.4 Tablas de Diagnósticos y Tratamientos

**Tabla: `diagnosticos`**

```sql
CREATE TABLE diagnosticos (
    id SERIAL PRIMARY KEY,
    id_cita INTEGER REFERENCES citas(id) ON DELETE CASCADE,
    tipo VARCHAR(20) CHECK (tipo IN ('Presuntivo', 'Definitivo', 'Diferencial')),
    descripcion TEXT NOT NULL,
    codigo_cie10 VARCHAR(10),
    diagnosticado_por INTEGER REFERENCES podologos(id),
    notas TEXT,
    fecha_diagnostico TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_diagnosticos_cita ON diagnosticos(id_cita);
CREATE INDEX idx_diagnosticos_cie10 ON diagnosticos(codigo_cie10);
```

**Tabla: `tratamientos`**

```sql
CREATE TABLE tratamientos (
    id SERIAL PRIMARY KEY,
    codigo_servicio VARCHAR(20) UNIQUE NOT NULL,
    nombre_servicio VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio_base DECIMAL(10,2) NOT NULL,
    duracion_minutos INTEGER DEFAULT 30,
    requiere_consentimiento BOOLEAN DEFAULT false,
    activo BOOLEAN DEFAULT true,
    categoria VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tratamientos_codigo ON tratamientos(codigo_servicio);
CREATE INDEX idx_tratamientos_activo ON tratamientos(activo);
```

**Tabla: `detalle_cita`**

```sql
CREATE TABLE detalle_cita (
    id SERIAL PRIMARY KEY,
    id_cita INTEGER REFERENCES citas(id) ON DELETE CASCADE,
    id_tratamiento INTEGER REFERENCES tratamientos(id),
    precio_aplicado DECIMAL(10,2) NOT NULL,
    descuento_porcentaje DECIMAL(5,2) DEFAULT 0,
    precio_final DECIMAL(10,2) GENERATED ALWAYS AS (precio_aplicado * (1 - descuento_porcentaje/100)) STORED,
    notas TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_detalle_cita_cita ON detalle_cita(id_cita);
CREATE INDEX idx_detalle_cita_tratamiento ON detalle_cita(id_tratamiento);
```

#### 3.1.5 Tablas de CRM y Chatbot

**Tabla: `conversaciones`**

```sql
CREATE TABLE conversaciones (
    id SERIAL PRIMARY KEY,
    id_contacto INTEGER REFERENCES contactos(id) ON DELETE CASCADE,
    canal VARCHAR(20) CHECK (canal IN ('WhatsApp', 'Telegram', 'Facebook', 'Web')),
    estado VARCHAR(20) DEFAULT 'Activa' CHECK (estado IN ('Activa', 'Cerrada', 'Archivada')),
    categoria VARCHAR(50),
    embedding VECTOR(384),
    resumen_ia TEXT,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultimo_mensaje TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_cierre TIMESTAMP
);

CREATE INDEX idx_conversaciones_contacto ON conversaciones(id_contacto);
CREATE INDEX idx_conversaciones_estado ON conversaciones(estado);
CREATE INDEX idx_conversaciones_embedding ON conversaciones USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

**Tabla: `mensajes`**

```sql
CREATE TABLE mensajes (
    id SERIAL PRIMARY KEY,
    id_conversacion INTEGER REFERENCES conversaciones(id) ON DELETE CASCADE,
    rol VARCHAR(20) CHECK (rol IN ('usuario', 'asistente', 'sistema')),
    contenido TEXT NOT NULL,
    metadata JSONB,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mensajes_conversacion ON mensajes(id_conversacion);
CREATE INDEX idx_mensajes_fecha ON mensajes(fecha_envio);
CREATE INDEX idx_mensajes_metadata ON mensajes USING gin(metadata);
```

**Tabla: `dudas_pendientes`**

```sql
CREATE TABLE dudas_pendientes (
    id SERIAL PRIMARY KEY,
    paciente_chat_id TEXT NOT NULL,
    paciente_nombre TEXT,
    paciente_telefono TEXT,
    duda TEXT NOT NULL,
    contexto TEXT,
    estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'respondida', 'expirada')),
    respuesta_admin TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_respuesta TIMESTAMP,
    fecha_expiracion TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
    admin_chat_id TEXT
);

CREATE INDEX idx_dudas_estado ON dudas_pendientes(estado);
CREATE INDEX idx_dudas_expiracion ON dudas_pendientes(fecha_expiracion) WHERE estado = 'pendiente';
```

**Tabla: `knowledge_base`**

```sql
CREATE TABLE knowledge_base (
    id SERIAL PRIMARY KEY,
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    pregunta_embedding BYTEA,
    categoria VARCHAR(50),
    veces_consultada INTEGER DEFAULT 0,
    confianza FLOAT DEFAULT 1.0,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP,
    origen VARCHAR(20) DEFAULT 'admin' CHECK (origen IN ('admin', 'sistema'))
);

CREATE INDEX idx_kb_categoria ON knowledge_base(categoria);
CREATE INDEX idx_kb_consultada ON knowledge_base(veces_consultada DESC);
```

#### 3.1.6 Tablas de Asistente de Voz

**Tabla: `sesiones_voz`**

```sql
CREATE TABLE sesiones_voz (
    id SERIAL PRIMARY KEY,
    id_cita INTEGER REFERENCES citas(id) ON DELETE CASCADE,
    id_podologo INTEGER REFERENCES podologos(id),
    estado VARCHAR(20) DEFAULT 'activa' CHECK (estado IN ('activa', 'pausada', 'finalizada')),
    duracion_segundos INTEGER,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP
);

CREATE INDEX idx_sesiones_cita ON sesiones_voz(id_cita);
CREATE INDEX idx_sesiones_estado ON sesiones_voz(estado);
```

**Tabla: `acciones_ia`**

```sql
CREATE TABLE acciones_ia (
    id SERIAL PRIMARY KEY,
    id_sesion INTEGER REFERENCES sesiones_voz(id) ON DELETE CASCADE,
    funcion_llamada VARCHAR(50) NOT NULL,
    parametros JSONB,
    resultado JSONB,
    exito BOOLEAN,
    mensaje_error TEXT,
    fecha_ejecucion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_acciones_sesion ON acciones_ia(id_sesion);
CREATE INDEX idx_acciones_funcion ON acciones_ia(funcion_llamada);
CREATE INDEX idx_acciones_exito ON acciones_ia(exito);
```

#### 3.1.7 Tablas de Inventario

**Tabla: `productos_inventario`**

```sql
CREATE TABLE productos_inventario (
    id SERIAL PRIMARY KEY,
    codigo_producto VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    categoria VARCHAR(50),
    stock_actual INTEGER DEFAULT 0,
    stock_minimo INTEGER DEFAULT 10,
    precio_compra DECIMAL(10,2),
    precio_venta DECIMAL(10,2),
    fecha_caducidad DATE,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_productos_codigo ON productos_inventario(codigo_producto);
CREATE INDEX idx_productos_stock_bajo ON productos_inventario(stock_actual) WHERE stock_actual <= stock_minimo;
CREATE INDEX idx_productos_caducidad ON productos_inventario(fecha_caducidad) WHERE fecha_caducidad IS NOT NULL;
```

**Tabla: `movimientos_inventario`**

```sql
CREATE TABLE movimientos_inventario (
    id SERIAL PRIMARY KEY,
    id_producto INTEGER REFERENCES productos_inventario(id) ON DELETE RESTRICT,
    tipo_movimiento VARCHAR(20) CHECK (tipo_movimiento IN ('entrada', 'salida', 'ajuste')),
    cantidad INTEGER NOT NULL,
    costo_unitario DECIMAL(10,2),
    referencia VARCHAR(100),
    id_cita INTEGER REFERENCES citas(id),
    realizado_por INTEGER REFERENCES usuarios(id),
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_movimientos_producto ON movimientos_inventario(id_producto);
CREATE INDEX idx_movimientos_tipo ON movimientos_inventario(tipo_movimiento);
CREATE INDEX idx_movimientos_fecha ON movimientos_inventario(fecha_movimiento);
```

### 3.2 Vistas Materializadas

**Vista: `dashboard_ejecutivo`**

```sql
CREATE MATERIALIZED VIEW dashboard_ejecutivo AS
SELECT 
    DATE_TRUNC('month', CURRENT_DATE) as mes,
    COUNT(DISTINCT c.id_paciente) as pacientes_atendidos,
    COUNT(c.id) as total_citas,
    COUNT(c.id) FILTER (WHERE c.estado = 'Completada') as citas_completadas,
    COUNT(c.id) FILTER (WHERE c.estado = 'Cancelada') as citas_canceladas,
    ROUND(COUNT(c.id) FILTER (WHERE c.estado = 'Cancelada')::NUMERIC / NULLIF(COUNT(c.id), 0) * 100, 2) as tasa_cancelacion,
    COALESCE(SUM(p.monto_pagado), 0) as ingresos_mes,
    COALESCE(AVG(p.monto_pagado), 0) as ticket_promedio
FROM citas c
LEFT JOIN pagos p ON c.id = p.id_cita
WHERE c.fecha_hora_inicio >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY DATE_TRUNC('month', CURRENT_DATE);

CREATE UNIQUE INDEX idx_dashboard_mes ON dashboard_ejecutivo(mes);
```

### 3.3 Funciones Almacenadas

**Función: `obtener_horarios_disponibles`**

```sql
CREATE OR REPLACE FUNCTION obtener_horarios_disponibles(
    p_id_podologo INTEGER,
    p_fecha DATE
)
RETURNS TABLE (
    hora_slot TIME,
    disponible BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    WITH slots AS (
        SELECT generate_series(
            '09:00'::TIME,
            '18:00'::TIME,
            '30 minutes'::INTERVAL
        )::TIME as hora
    ),
    citas_dia AS (
        SELECT 
            fecha_hora_inicio::TIME as hora_inicio,
            fecha_hora_fin::TIME as hora_fin
        FROM citas
        WHERE id_podologo = p_id_podologo
        AND fecha_hora_inicio::DATE = p_fecha
        AND estado NOT IN ('Cancelada', 'No_Asistio')
    )
    SELECT 
        s.hora,
        NOT EXISTS (
            SELECT 1 FROM citas_dia c
            WHERE s.hora >= c.hora_inicio 
            AND s.hora < c.hora_fin
        ) as disponible
    FROM slots s
    ORDER BY s.hora;
END;
$$ LANGUAGE plpgsql;
```

---

## 4. Especificaciones de API REST

### 4.1 Estructura de Endpoints

**Base URL**: `https://api.podoskin.com/v1`

### 4.2 Autenticación

**Endpoint**: `POST /auth/login`

**Request**:

```json
{
  "username": "string",
  "password": "string"
}
```

**Response 200**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "dr.santiago",
    "email": "santiago@podoskin.com",
    "rol": "podologo"
  }
}
```

**Implementación**:

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["autenticación"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    access_token = create_access_token(data={"sub": user.username, "rol": user.rol})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "rol": user.rol
        }
    }
```

### 4.3 Endpoints de Pacientes

**GET /pacientes**

- Listar pacientes con paginación y filtros
- Query params: `page`, `limit`, `search`, `activo`

**GET /pacientes/{id}**

- Obtener paciente por ID con expediente completo

**POST /pacientes**

- Crear nuevo paciente

**PUT /pacientes/{id}**

- Actualizar paciente existente

**DELETE /pacientes/{id}**

- Desactivar paciente (soft delete)

**Modelo Pydantic**:

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional

class PacienteCreate(BaseModel):
    primer_nombre: str = Field(..., min_length=1, max_length=50)
    segundo_nombre: Optional[str] = Field(None, max_length=50)
    primer_apellido: str = Field(..., min_length=1, max_length=50)
    segundo_apellido: Optional[str] = Field(None, max_length=50)
    fecha_nacimiento: date
    sexo: str = Field(..., regex="^[MFO]$")
    curp: Optional[str] = Field(None, regex="^[A-Z]{4}[0-9]{6}[HM][A-Z]{5}[0-9]{2}$")
    telefono_principal: str = Field(..., min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    
    class Config:
        schema_extra = {
            "example": {
                "primer_nombre": "Juan",
                "primer_apellido": "Pérez",
                "fecha_nacimiento": "1990-05-15",
                "sexo": "M",
                "telefono_principal": "6861234567"
            }
        }
```

### 4.4 Endpoints de Citas

**GET /citas**

- Listar citas con filtros
- Query params: `fecha_inicio`, `fecha_fin`, `id_podologo`, `estado`

**GET /citas/{id}**

- Obtener cita por ID

**POST /citas**

- Crear nueva cita con validación de disponibilidad

**PUT /citas/{id}**

- Actualizar cita

**DELETE /citas/{id}**

- Cancelar cita

**GET /citas/disponibilidad**

- Obtener horarios disponibles
- Query params: `id_podologo`, `fecha`

**Implementación de Validación**:

```python
@router.post("/citas")
async def crear_cita(cita: CitaCreate, db: AsyncSession = Depends(get_db)):
    # Validar disponibilidad
    disponibilidad = await db.execute(
        select(func.obtener_horarios_disponibles(
            cita.id_podologo,
            cita.fecha_hora_inicio.date()
        ))
    )
    
    hora_solicitada = cita.fecha_hora_inicio.time()
    slots = disponibilidad.fetchall()
    
    if not any(slot.disponible for slot in slots if slot.hora_slot == hora_solicitada):
        raise HTTPException(
            status_code=409,
            detail="Horario no disponible"
        )
    
    # Crear cita
    nueva_cita = Cita(**cita.dict())
    db.add(nueva_cita)
    await db.commit()
    await db.refresh(nueva_cita)
    
    return nueva_cita
```

### 4.5 Endpoints de Asistente de Voz

**POST /voz/sesion/iniciar**

- Iniciar sesión de voz para una cita

**POST /voz/sesion/{id}/finalizar**

- Finalizar sesión de voz

**POST /voz/funcion**

- Ejecutar función del asistente

**Modelo de Función**:

```python
class FuncionVozRequest(BaseModel):
    id_sesion: int
    funcion: str = Field(..., regex="^(update_vital_signs|add_diagnosis|query_patient_data|search_cie10|add_treatment|generate_summary|save_consultation)$")
    parametros: dict

class FuncionVozResponse(BaseModel):
    exito: bool
    resultado: dict
    mensaje: str
```

### 4.6 Endpoints de Chatbot WhatsApp

**POST /webhook/whatsapp**

- Recibir mensajes de WhatsApp

**POST /webhook/notify_admin**

- Notificar administrador de duda escalada

**POST /webhook/clear/{chat_id}**

- Limpiar conversación

---

## 5. Especificaciones de Agentes de IA

### 5.1 Agente LangGraph para WhatsApp

**Archivo**: `backend/agents/sub_agent_whatsApp/graph.py`

**Estado del Agente**:

```python
from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages

class WhatsAppAgentState(TypedDict):
    # Identificación
    conversation_id: str
    contact_id: int
    patient_id: int | None
    whatsapp_number: str
    
    # Mensajes
    messages: Annotated[List, add_messages]
    
    # Contexto RAG
    retrieved_context: List[str]
    patient_info: dict | None
    appointment_history: List[dict]
    
    # Clasificación
    intent: str
    confidence: float
    entities: dict
    
    # Control
    next_action: str
    requires_human: bool
    escalation_reason: str | None
```

**Nodos del Grafo**:

1. **classify_intent**: Clasificar intención del usuario
2. **retrieve_context**: Buscar contexto en RAG
3. **check_patient**: Verificar si es paciente registrado
4. **handle_appointment**: Gestionar agendamiento
5. **handle_query**: Manejar consultas generales
6. **handle_cancellation**: Procesar cancelaciones
7. **generate_response**: Generar respuesta con LLM
8. **post_process_escalation**: Detectar y escalar dudas

**Implementación de Nodo**:

```python
async def classify_intent_node(state: WhatsAppAgentState) -> WhatsAppAgentState:
    """Clasifica la intención del mensaje usando Claude"""
    
    last_message = state["messages"][-1].content
    
    prompt = f"""Analiza el siguiente mensaje de WhatsApp y clasifica su intención.

Mensaje: "{last_message}"

Intenciones posibles:
- agendar: Quiere agendar una cita nueva
- consulta: Pregunta sobre tratamientos, precios, horarios
- cancelar: Quiere cancelar o reagendar una cita existente
- info: Pide información general de la clínica
- emergencia: Situación urgente
- otro: Otro tipo de mensaje

Responde en formato JSON:
{{
  "intent": "nombre_de_la_intencion",
  "confidence": 0.95,
  "entities": {{
    "fecha": "2025-12-21" (si menciona),
    "hora": "14:00" (si menciona),
    "nombre": "Juan" (si menciona)
  }}
}}
"""
    
    response = await llm.ainvoke(prompt)
    result = json.loads(response.content)
    
    return {
        **state,
        "intent": result["intent"],
        "confidence": result["confidence"],
        "entities": result.get("entities", {})
    }
```

### 5.2 Embeddings y RAG

**Servicio de Embeddings**:

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
    
    def encode_single(self, text: str) -> np.ndarray:
        """Codifica un texto individual"""
        return self.model.encode(text, convert_to_numpy=True)
    
    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """Codifica múltiples textos"""
        return self.model.encode(texts, batch_size=32, show_progress_bar=False)
    
    def serialize_embedding(self, embedding: np.ndarray) -> bytes:
        """Serializa embedding para almacenar en PostgreSQL"""
        return embedding.tobytes()
    
    def deserialize_embedding(self, data: bytes) -> np.ndarray:
        """Deserializa embedding desde PostgreSQL"""
        return np.frombuffer(data, dtype=np.float32)
```

**Búsqueda Semántica**:

```python
async def search_knowledge_base(query: str, threshold: float = 0.85) -> List[dict]:
    """Busca en knowledge base usando similitud semántica"""
    
    # Generar embedding de la consulta
    embedding_service = EmbeddingService()
    query_embedding = embedding_service.encode_single(query)
    query_bytes = embedding_service.serialize_embedding(query_embedding)
    
    # Buscar en base de datos
    async with get_db() as db:
        result = await db.execute("""
            SELECT 
                id,
                pregunta,
                respuesta,
                veces_consultada,
                1 - (pregunta_embedding <-> $1::bytea) as similarity
            FROM knowledge_base
            WHERE 1 - (pregunta_embedding <-> $1::bytea) > $2
            ORDER BY similarity DESC
            LIMIT 5
        """, query_bytes, threshold)
        
        rows = result.fetchall()
        
        # Incrementar contador si hay match
        if rows:
            await db.execute("""
                UPDATE knowledge_base
                SET veces_consultada = veces_consultada + 1
                WHERE id = $1
            """, rows[0].id)
            await db.commit()
        
        return [dict(row) for row in rows]
```

---

## 6. Especificaciones de Frontend

### 6.1 Estructura de Componentes

```
src/
├── components/
│   ├── common/              # Componentes reutilizables
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   └── Table.tsx
│   ├── medical/             # Componentes médicos
│   │   ├── Header.tsx
│   │   ├── PatientSidebar.tsx
│   │   ├── MedicalRecordForm.tsx
│   │   ├── MayaAssistant.tsx
│   │   └── fields/
│   │       ├── FormField.tsx
│   │       └── HelpTooltip.tsx
│   └── appointments/        # Componentes de citas
│       ├── Calendar.tsx
│       ├── AppointmentForm.tsx
│       └── TimeSlotPicker.tsx
├── context/
│   ├── AuthContext.tsx
│   ├── MedicalFormContext.tsx
│   └── AppointmentContext.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── usePatients.ts
│   ├── useAppointments.ts
│   └── useVoiceAssistant.ts
├── services/
│   ├── api.ts
│   ├── authService.ts
│   ├── patientService.ts
│   └── appointmentService.ts
├── types/
│   ├── medical.ts
│   ├── appointment.ts
│   └── user.ts
└── utils/
    ├── validators.ts
    ├── formatters.ts
    └── constants.ts
```

### 6.2 Servicio de API

**Archivo**: `src/services/api.ts`

```typescript
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/v1',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para agregar token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Interceptor para manejar errores
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }
}

export const api = new ApiService();
```

### 6.3 Hook de Pacientes

**Archivo**: `src/hooks/usePatients.ts`

```typescript
import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { Patient, PaginatedResponse } from '../types/medical';

export function usePatients(page: number = 1, limit: number = 20) {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchPatients();
  }, [page, limit]);

  const fetchPatients = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get<PaginatedResponse<Patient>>(
        `/pacientes?page=${page}&limit=${limit}`
      );
      setPatients(response.items);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar pacientes');
    } finally {
      setLoading(false);
    }
  };

  const createPatient = async (data: Partial<Patient>) => {
    try {
      const newPatient = await api.post<Patient>('/pacientes', data);
      setPatients([...patients, newPatient]);
      return newPatient;
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Error al crear paciente');
    }
  };

  const updatePatient = async (id: number, data: Partial<Patient>) => {
    try {
      const updated = await api.put<Patient>(`/pacientes/${id}`, data);
      setPatients(patients.map(p => p.id === id ? updated : p));
      return updated;
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Error al actualizar paciente');
    }
  };

  return {
    patients,
    loading,
    error,
    total,
    fetchPatients,
    createPatient,
    updatePatient,
  };
}
```

---

## 7. Especificaciones de Seguridad

### 7.1 Autenticación y Autorización

**JWT Token Structure**:

```json
{
  "sub": "dr.santiago",
  "rol": "podologo",
  "exp": 1735689600,
  "iat": 1735686000
}
```

**Middleware de Autorización**:

```python
from functools import wraps
from fastapi import HTTPException, Depends

def require_role(allowed_roles: List[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user = Depends(get_current_user), **kwargs):
            if current_user.rol not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail="No tiene permisos para esta acción"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Uso
@router.post("/pacientes")
@require_role(["admin", "podologo", "recepcion"])
async def crear_paciente(paciente: PacienteCreate, current_user = Depends(get_current_user)):
    # ...
```

### 7.2 Validación de Datos

**Pydantic Validators**:

```python
from pydantic import BaseModel, validator, Field
import re

class PacienteCreate(BaseModel):
    telefono_principal: str = Field(..., min_length=10, max_length=15)
    
    @validator('telefono_principal')
    def validate_telefono(cls, v):
        # Solo números
        if not re.match(r'^\d{10,15}$', v):
            raise ValueError('Teléfono debe contener solo números (10-15 dígitos)')
        return v
    
    @validator('curp')
    def validate_curp(cls, v):
        if v and not re.match(r'^[A-Z]{4}\d{6}[HM][A-Z]{5}\d{2}$', v):
            raise ValueError('CURP inválido')
        return v
```

### 7.3 Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    # ...
```

---

## 8. Especificaciones de Rendimiento

### 8.1 Optimizaciones de Base de Datos

**Índices Compuestos**:

```sql
-- Para búsquedas frecuentes de citas por podólogo y fecha
CREATE INDEX idx_citas_podologo_fecha ON citas(id_podologo, fecha_hora_inicio);

-- Para búsquedas de pacientes por nombre completo
CREATE INDEX idx_pacientes_nombre_completo ON pacientes(primer_nombre, primer_apellido);

-- Para consultas de inventario con stock bajo
CREATE INDEX idx_productos_stock_categoria ON productos_inventario(categoria, stock_actual) 
WHERE stock_actual <= stock_minimo;
```

**Connection Pooling**:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

### 8.2 Caching

**Redis Cache**:

```python
from redis import asyncio as aioredis
import json

redis_client = await aioredis.from_url("redis://localhost:6379")

async def get_cached_patient(patient_id: int):
    cached = await redis_client.get(f"patient:{patient_id}")
    if cached:
        return json.loads(cached)
    
    # Fetch from DB
    patient = await db.get(Patient, patient_id)
    
    # Cache for 1 hour
    await redis_client.setex(
        f"patient:{patient_id}",
        3600,
        json.dumps(patient.dict())
    )
    
    return patient
```

---

## 9. Especificaciones de Testing

### 9.1 Tests Unitarios (Backend)

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_crear_paciente():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/pacientes",
            json={
                "primer_nombre": "Juan",
                "primer_apellido": "Pérez",
                "fecha_nacimiento": "1990-05-15",
                "sexo": "M",
                "telefono_principal": "6861234567"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["primer_nombre"] == "Juan"
        assert "id" in data
```

### 9.2 Tests de Integración

```python
@pytest.mark.asyncio
async def test_flujo_agendamiento_completo():
    # 1. Crear paciente
    paciente = await crear_paciente_test()
    
    # 2. Verificar disponibilidad
    disponibilidad = await verificar_disponibilidad(
        id_podologo=1,
        fecha="2025-12-26"
    )
    assert len(disponibilidad) > 0
    
    # 3. Agendar cita
    cita = await agendar_cita(
        id_paciente=paciente.id,
        id_podologo=1,
        fecha_hora="2025-12-26 10:00:00"
    )
    assert cita.estado == "Confirmada"
    
    # 4. Verificar recordatorios programados
    assert cita.recordatorio_24h_enviado == False
```

---

## 10. Deployment y DevOps

### 10.1 Docker Compose

```yaml
version: '3.8'

services:
  db:
    image: pgvector/pgvector:pg16
    container_name: podoskin_db
    environment:
      POSTGRES_DB: podoskin_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./data:/docker-entrypoint-initdb.d

  backend:
    build: ./backend
    container_name: podoskin_backend
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@db:5432/podoskin_db
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      GEMINI_API_KEY: ${GEMINI_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - db
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    container_name: podoskin_frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules

  whatsapp:
    build: ./whatsapp-web-js
    container_name: podoskin_whatsapp
    ports:
      - "3000:3000"
    volumes:
      - ./whatsapp-web-js:/app
      - whatsapp_auth:/app/.wwebjs_auth

volumes:
  postgres_data:
  whatsapp_auth:
```

### 10.2 Variables de Entorno

```env
# Base de datos
DATABASE_URL=postgresql://postgres:password@localhost:5432/podoskin_db

# APIs de IA
ANTHROPIC_API_KEY=sk-ant-api03-...
GEMINI_API_KEY=AIzaSy...

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# WhatsApp
ADMIN_PHONE=526861892910
BRIDGE_API_URL=http://localhost:8000

# Redis (opcional)
REDIS_URL=redis://localhost:6379
```

---

## 11. Tareas para Agentes de IA

### 11.1 División de Tareas

**Agente 1: Database Setup**

- Crear todas las tablas (42)
- Crear vistas materializadas (24)
- Crear funciones almacenadas (15+)
- Crear índices optimizados
- Scripts de migración

**Agente 2: Backend API - Auth & Users**

- Implementar autenticación JWT
- Endpoints de usuarios
- Middleware de autorización
- Rate limiting

**Agente 3: Backend API - Pacientes**

- CRUD de pacientes
- Endpoints de alergias
- Endpoints de antecedentes
- Validaciones Pydantic

**Agente 4: Backend API - Citas**

- CRUD de citas
- Validación de disponibilidad
- Sistema de recordatorios
- Endpoints de horarios

**Agente 5: Backend API - Tratamientos**

- CRUD de tratamientos
- Diagnósticos con CIE-10
- Signos vitales
- Notas clínicas

**Agente 6: LangGraph WhatsApp Agent** (SubAgente Independiente)

- Grafo LangGraph completo (8 nodos)
- Sistema de escalamiento con `interrupt`/`resume`
- Base de conocimiento con aprendizaje (`validated` flag)
- Patrones:
  - `WhatsAppState(TypedDict)` → Estado aislado
  - `checkpointer` persistente (Redis/Postgres)
  - `save_faq(q, a, meta)` para aprendizaje
  - `audit_logs` obligatorios

**Agente 7: Gemini Live + Orquestador**

> **Referencia**: [gemini-live-voice-controller/](file:///c:/Users/Salva/OneDrive/Documentos/Database/gemini-live-voice-controller) + [recomendacionesLangGraph.md](file:///c:/Users/Salva/OneDrive/Documentos/Database/recomendacionesLangGraph.md)

1. **Frontend Gemini Live**:
   - 8 funciones de voz
   - Audio: resampleo 16kHz PCM16
   - NO exponer API key en cliente

2. **Backend Sessions** (SEGURIDAD):
   - `POST /api/live/session/start` → Sesión segura
   - `POST /api/live/tool/call` → Tools críticas en backend
   - Tokens efímeros con TTL

3. **Agente Padre Orquestador**:
   - Recibe consultas complejas de Gemini Live
   - Delega a SubAgentes: Resúmenes, Análisis Clínico, Financiero
   - Modelo: Claude Sonnet 3.7

4. **SubAgentes de Producción**:
   - SubAgente Resúmenes (consultas + WhatsApp)
   - SubAgente Análisis Clínico (evolución, seguimientos)
   - SubAgente Análisis Financiero (reportes, anomalías)

**Agente 8: Frontend - Auth & Layout**

- Login/Logout
- Layout principal
- Navegación
- Context de autenticación

**Agente 9: Frontend - Pacientes**

- Lista de pacientes
- Formulario de creación/edición
- Búsqueda y filtros
- Expediente médico

**Agente 10: Frontend - Citas**

- Calendario de citas
- Formulario de agendamiento
- Selector de horarios
- Vista de disponibilidad

**Agente 11: Frontend - Dashboard**

- KPIs principales
- Gráficas
- Reportes
- Alertas

**Agente 12: Testing & QA**

- Tests unitarios backend
- Tests de integración
- Tests E2E frontend
- Documentación de APIs

---

**Fin del SRS**
