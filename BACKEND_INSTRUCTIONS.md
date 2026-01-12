# 📋 Instrucciones para el Backend - Sistema de Registro de Pacientes Podoskin

## 🎯 Resumen del Sistema

Este documento contiene las especificaciones técnicas para implementar el backend del sistema de registro e identificación de pacientes de Podoskin Solutions.

El frontend genera un **ID parcial** basado en los datos del paciente y el backend es responsable de:
1. Completar el ID con un contador secuencial único
2. Almacenar la información del paciente
3. Proporcionar endpoints de búsqueda y registro
4. Enriquecer las respuestas del chatbot con contexto del paciente

---

## 📊 Estructura de la Base de Datos

### Tabla: `patients`

```sql
CREATE TABLE patients (
    -- Identificación
    patient_id VARCHAR(20) PRIMARY KEY,              -- Ej: "VA-AM-0504-0009"
    partial_id VARCHAR(15) NOT NULL,                 -- Ej: "VA-AM-0504"
    counter INTEGER NOT NULL,                        -- Ej: 9
    
    -- Información Personal
    first_name VARCHAR(100) NOT NULL,
    second_name VARCHAR(100),
    first_last_name VARCHAR(100) NOT NULL,
    second_last_name VARCHAR(100),
    birth_date DATE NOT NULL,
    
    -- Metadata
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_visit_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',             -- active, inactive, archived
    
    -- Indices
    INDEX idx_partial_id (partial_id),
    INDEX idx_names (first_name, first_last_name, birth_date),
    UNIQUE INDEX idx_unique_counter (partial_id, counter)
);
```

### Tabla: `chat_sessions`

```sql
CREATE TABLE chat_sessions (
    session_id VARCHAR(36) PRIMARY KEY,              -- UUID v4
    patient_id VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);
```

### Tabla: `chat_messages` (Opcional - Para historial)

```sql
CREATE TABLE chat_messages (
    message_id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    patient_id VARCHAR(20),
    sender VARCHAR(10) NOT NULL,                     -- 'user' o 'bot'
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    INDEX idx_session (session_id),
    INDEX idx_patient (patient_id)
);
```

---

## 🔌 Endpoints a Implementar

### 1. POST `/api/patient/register`

**Propósito:** Registrar un nuevo paciente y generar su ID completo

**Request Body:**
```json
{
  "first_name": "Abraham",
  "second_name": "Salvador",
  "first_last_name": "Córdova",
  "second_last_name": "Soto",
  "birth_date": "1996-04-05",
  "partial_id": "VA-AM-0504"
}
```

**Lógica del Backend:**

```python
def register_patient(data):
    # 1. Validar datos
    if not data.first_name or not data.first_last_name or not data.birth_date:
        return {"success": False, "message": "Campos requeridos faltantes"}, 400
    
    # 2. Buscar el último contador para este partial_id
    last_patient = db.query("""
        SELECT MAX(counter) as max_counter
        FROM patients
        WHERE partial_id = ?
    """, [data.partial_id])
    
    # 3. Generar nuevo contador (empezar en 1 si no existe ninguno)
    new_counter = (last_patient.max_counter or 0) + 1
    
    # 4. Formatear contador con ceros: 0001, 0002, etc.
    counter_str = str(new_counter).zfill(4)
    
    # 5. Crear ID completo
    full_patient_id = f"{data.partial_id}-{counter_str}"
    
    # 6. Verificar que no exista (por si acaso)
    existing = db.query("SELECT patient_id FROM patients WHERE patient_id = ?", [full_patient_id])
    if existing:
        return {"success": False, "message": "Error: ID ya existe"}, 500
    
    # 7. Insertar en base de datos
    db.execute("""
        INSERT INTO patients (
            patient_id, partial_id, counter,
            first_name, second_name, first_last_name, second_last_name,
            birth_date, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
    """, [
        full_patient_id, data.partial_id, new_counter,
        data.first_name, data.second_name, data.first_last_name, data.second_last_name,
        data.birth_date
    ])
    
    # 8. Retornar respuesta
    return {
        "success": True,
        "patient_id": full_patient_id,
        "message": "Paciente registrado exitosamente"
    }, 201
```

**Response Exitosa (201):**
```json
{
  "success": true,
  "patient_id": "VA-AM-0504-0009",
  "message": "Paciente registrado exitosamente"
}
```

**Response Error (400/500):**
```json
{
  "success": false,
  "message": "Descripción del error"
}
```

---

### 2. POST `/api/patient/lookup`

**Propósito:** Buscar un paciente existente por ID o datos personales

**Request Body (Opción 1 - Búsqueda por ID):**
```json
{
  "patient_id": "VA-AM-0504-0009"
}
```

**Request Body (Opción 2 - Búsqueda por Datos):**
```json
{
  "first_name": "Abraham",
  "first_last_name": "Córdova",
  "birth_date": "1996-04-05"
}
```

**Lógica del Backend:**

```python
def lookup_patient(data):
    # Opción 1: Búsqueda por ID
    if data.patient_id:
        patient = db.query("""
            SELECT patient_id, first_name, first_last_name, registration_date, status
            FROM patients
            WHERE patient_id = ? AND status = 'active'
        """, [data.patient_id])
        
        if patient:
            return {
                "found": True,
                "patient_id": patient.patient_id,
                "first_name": patient.first_name,
                "first_last_name": patient.first_last_name,
                "registration_date": patient.registration_date.isoformat()
            }, 200
        else:
            return {"found": False}, 404
    
    # Opción 2: Búsqueda por datos personales
    elif data.first_name and data.first_last_name and data.birth_date:
        patient = db.query("""
            SELECT patient_id, first_name, first_last_name, registration_date, status
            FROM patients
            WHERE LOWER(first_name) = LOWER(?)
              AND LOWER(first_last_name) = LOWER(?)
              AND birth_date = ?
              AND status = 'active'
            LIMIT 1
        """, [data.first_name, data.first_last_name, data.birth_date])
        
        if patient:
            return {
                "found": True,
                "patient_id": patient.patient_id,
                "first_name": patient.first_name,
                "first_last_name": patient.first_last_name,
                "registration_date": patient.registration_date.isoformat()
            }, 200
        else:
            return {"found": False}, 404
    
    else:
        return {"found": False, "message": "Parámetros insuficientes"}, 400
```

**Response Encontrado (200):**
```json
{
  "found": true,
  "patient_id": "VA-AM-0504-0009",
  "first_name": "Abraham",
  "first_last_name": "Córdova",
  "registration_date": "2025-12-20T10:30:00.000Z"
}
```

**Response No Encontrado (404):**
```json
{
  "found": false
}
```

---

### 3. POST `/api/chatbot/message`

**Propósito:** Procesar mensajes del chat y responder con contexto del paciente

**Request Body:**
```json
{
  "message": "¿Cuánto cuesta el tratamiento de pie de atleta?",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-01-12T10:00:00.000Z",
  "patient_info": {
    "patient_id": "VA-AM-0504-0009",
    "first_name": "Abraham",
    "first_last_name": "Córdova",
    "is_registered": true,
    "partial_id": "VA-AM-0504"
  },
  "user_context": {
    "page": "/",
    "previous_messages": 5,
    "user_agent": "Mozilla/5.0..."
  }
}
```

**Nota:** El campo `patient_info` puede ser `null` o no estar presente si el usuario aún no se ha identificado.

**Lógica del Backend:**

```python
def handle_chatbot_message(data):
    # 1. Registrar o actualizar sesión
    session = update_or_create_session(data.session_id, data.patient_info)
    
    # 2. Guardar mensaje del usuario (opcional)
    if SAVE_CHAT_HISTORY:
        save_message(data.session_id, data.patient_info.patient_id, 'user', data.message)
    
    # 3. Procesar mensaje con IA/LLM
    # Incluir contexto del paciente si está disponible
    context = build_context(data.patient_info) if data.patient_info else None
    bot_response = process_with_ai(data.message, context, session)
    
    # 4. Guardar respuesta del bot (opcional)
    if SAVE_CHAT_HISTORY:
        save_message(data.session_id, data.patient_info.patient_id, 'bot', bot_response)
    
    # 5. Actualizar última actividad de la sesión
    update_session_activity(data.session_id)
    
    # 6. Retornar respuesta
    return {
        "response": bot_response,
        "session_id": data.session_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "patient_id": data.patient_info.patient_id if data.patient_info else None,
        "suggestions": generate_suggestions(data.message, context)
    }, 200
```

**Response Exitosa (200):**
```json
{
  "response": "El tratamiento para pie de atleta tiene un costo de $800 MXN por sesión. Incluye consulta, medicamentos y seguimiento. ¿Te gustaría agendar una cita, Abraham?",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-01-12T10:00:05.000Z",
  "patient_id": "VA-AM-0504-0009",
  "actions": [
    {
      "type": "schedule_appointment",
      "label": "Agendar Cita",
      "data": {
        "service": "pie-atleta",
        "available_dates": ["2026-01-15", "2026-01-16"]
      }
    }
  ],
  "suggestions": [
    "¿Cuántas sesiones necesito?",
    "¿Dónde están ubicados?",
    "¿Tienen disponibilidad esta semana?"
  ]
}
```

---

## 🔐 Seguridad y Validaciones

### Validaciones Requeridas:

1. **Registro de Paciente:**
   - Validar que `first_name` y `first_last_name` tengan al menos 2 caracteres
   - Validar formato de fecha (YYYY-MM-DD)
   - Validar que la fecha de nacimiento sea razonable (1900 - presente)
   - Sanitizar inputs para prevenir SQL injection
   - Verificar unicidad del ID completo antes de insertar

2. **Búsqueda de Paciente:**
   - Sanitizar inputs
   - Usar búsquedas case-insensitive para nombres
   - Solo retornar pacientes con status 'active'

3. **Chatbot:**
   - Validar que `session_id` sea un UUID válido
   - Limitar longitud de mensajes (ej: max 1000 caracteres)
   - Rate limiting por session_id (ej: max 10 mensajes/minuto)

### Headers Requeridos:

```
Content-Type: application/json
X-Client-Type: web
X-Session-ID: {session_id}
```

---

## 🚀 Recomendaciones de Implementación

### Stack Recomendado:

**Opción 1 - Python (FastAPI):**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uvicorn

app = FastAPI()

class PatientRegistration(BaseModel):
    first_name: str
    second_name: str | None = None
    first_last_name: str
    second_last_name: str | None = None
    birth_date: str
    partial_id: str

@app.post("/api/patient/register")
async def register_patient(data: PatientRegistration):
    # Implementar lógica aquí
    pass
```

**Opción 2 - Node.js (Express):**
```javascript
const express = require('express');
const app = express();
app.use(express.json());

app.post('/api/patient/register', async (req, res) => {
    // Implementar lógica aquí
});
```

### Base de Datos Recomendadas:
- **PostgreSQL** (Recomendado) - Excelente para datos relacionales
- **MySQL** - Alternativa sólida
- **SQLite** - Para desarrollo/testing

### Consideraciones de Rendimiento:
- Crear índices en `partial_id`, `patient_id`, y combinación de nombres
- Usar transacciones para el registro (evitar race conditions)
- Implementar caché para búsquedas frecuentes (Redis)
- Considerar paginación para listados de pacientes

---

## 📝 Ejemplos de Uso

### Flujo Completo: Nuevo Paciente

**1. Frontend genera ID parcial:**
```
Nombre: Abraham Córdova
Fecha: 05/04/1996
ID Parcial: "VA-AM-0504"
```

**2. Frontend envía registro:**
```bash
POST /api/patient/register
{
  "first_name": "Abraham",
  "first_last_name": "Córdova",
  "birth_date": "1996-04-05",
  "partial_id": "VA-AM-0504"
}
```

**3. Backend procesa:**
- Busca último contador para "VA-AM-0504" → encuentra 8
- Genera nuevo contador → 9
- Crea ID completo → "VA-AM-0504-0009"
- Guarda en DB

**4. Backend responde:**
```json
{
  "success": true,
  "patient_id": "VA-AM-0504-0009",
  "message": "Paciente registrado exitosamente"
}
```

**5. Frontend guarda en localStorage y habilita chat**

---

## 🧪 Testing

### Casos de Prueba Requeridos:

1. **Registro:**
   - ✅ Primer paciente con ID parcial nuevo (debe ser -0001)
   - ✅ Segundo paciente con mismo ID parcial (debe ser -0002)
   - ✅ Registro con campos opcionales vacíos
   - ❌ Registro sin campos requeridos
   - ❌ Fecha de nacimiento inválida

2. **Búsqueda:**
   - ✅ Búsqueda por ID existente
   - ✅ Búsqueda por datos personales exactos
   - ❌ Búsqueda con ID no existente
   - ❌ Búsqueda con datos incorrectos
   - ✅ Búsqueda case-insensitive de nombres

3. **Chatbot:**
   - ✅ Mensaje con paciente registrado
   - ✅ Mensaje sin paciente (anónimo)
   - ✅ Sesión nueva vs sesión existente
   - ❌ Mensaje vacío o muy largo

---

## 📊 Monitoreo y Logs

### Métricas a Rastrear:
- Registros de pacientes por día/semana/mes
- Tiempo de respuesta de endpoints
- Errores y excepciones
- Distribución de IDs parciales (detectar colisiones)

### Logs Importantes:
```python
logger.info(f"Paciente registrado: {patient_id}")
logger.warning(f"Búsqueda fallida para ID: {search_id}")
logger.error(f"Error al generar ID: {error}")
```

---

## 🔄 Migración y Mantenimiento

### Scripts de Mantenimiento:

**1. Verificar integridad de contadores:**
```sql
SELECT partial_id, COUNT(*) as total, MAX(counter) as max_counter
FROM patients
GROUP BY partial_id
HAVING total != max_counter;
```

**2. Limpiar sesiones antiguas:**
```sql
DELETE FROM chat_sessions
WHERE last_activity < NOW() - INTERVAL '7 days';
```

---

## 📞 Soporte

Para dudas o problemas con la integración:
- Revisar este documento primero
- Verificar logs del backend
- Probar endpoints con Postman/curl
- Contactar al equipo de frontend si el formato de datos no coincide

---

**Última actualización:** Enero 12, 2026
**Versión del documento:** 1.0
