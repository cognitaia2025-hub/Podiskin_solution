# Módulo de Citas - Podoskin Solution

## 📋 Descripción

Módulo backend para gestión completa de citas (appointments) en el sistema Podoskin. Implementa CRUD completo con validaciones robustas, detección de conflictos y gestión de disponibilidad.

## 🏗️ Arquitectura

### Estructura de Archivos

```
backend/citas/
├── __init__.py          # Punto de entrada del módulo
├── models.py            # Modelos Pydantic (request/response)
├── service.py           # Lógica de negocio y acceso a datos
├── router.py            # Endpoints REST (FastAPI)
├── demo_validacion.py   # Script de demostración
└── README.md            # Esta documentación
```

### Componentes

- **Models**: Esquemas de validación con Pydantic
- **Service**: Lógica programática (no IA) para:
  - Validaciones de datos
  - Cálculos automáticos (duración, primera vez)
  - Detección de conflictos
  - Operaciones CRUD en base de datos
- **Router**: Endpoints REST expuestos por FastAPI

## 🚀 Endpoints REST

### 1. GET /citas/disponibilidad

Obtiene horarios disponibles para un podólogo en una fecha específica.

**Query Parameters:**
- `id_podologo` (int, required): ID del podólogo
- `fecha` (date, required): Fecha a consultar (YYYY-MM-DD)

**Response 200:**
```json
{
  "fecha": "2024-12-26",
  "podologo": {
    "id": 1,
    "nombre_completo": "Dr. Santiago Ornelas"
  },
  "slots": [
    { "hora": "09:00", "disponible": true },
    { "hora": "09:30", "disponible": true },
    { "hora": "10:00", "disponible": false, "motivo": "Cita agendada" }
  ]
}
```

### 2. GET /citas

Lista citas con filtros opcionales.

**Query Parameters:**
- `id_paciente` (int, optional): Filtrar por paciente
- `id_podologo` (int, optional): Filtrar por podólogo
- `fecha_inicio` (date, optional): Desde esta fecha
- `fecha_fin` (date, optional): Hasta esta fecha
- `estado` (string, optional): Filtrar por estado
- `limit` (int, default=100): Número de resultados
- `offset` (int, default=0): Paginación

**Response 200:**
```json
{
  "total": 150,
  "citas": [...]
}
```

### 3. GET /citas/{id}

Obtiene una cita por su ID.

**Response 200:**
```json
{
  "id": 123,
  "id_paciente": 42,
  "id_podologo": 1,
  "fecha_hora_inicio": "2024-12-26T10:00:00",
  "fecha_hora_fin": "2024-12-26T10:30:00",
  "tipo_cita": "Consulta",
  "estado": "Confirmada",
  "es_primera_vez": true,
  "paciente": {
    "id": 42,
    "nombre_completo": "Juan Pérez"
  },
  "podologo": {
    "id": 1,
    "nombre_completo": "Dr. Santiago Ornelas"
  }
}
```

### 4. POST /citas

Crea una nueva cita.

**Request Body:**
```json
{
  "id_paciente": 42,
  "id_podologo": 1,
  "fecha_hora_inicio": "2024-12-26T10:00:00",
  "tipo_cita": "Consulta",
  "motivo_consulta": "Dolor en el talón",
  "notas_recepcion": "Primera consulta"
}
```

**Response 201:** (mismo formato que GET /citas/{id})

### 5. PUT /citas/{id}

Actualiza una cita existente.

**Request Body** (todos los campos son opcionales):
```json
{
  "fecha_hora_inicio": "2024-12-26T11:00:00",
  "tipo_cita": "Seguimiento",
  "motivo_consulta": "Actualizado",
  "notas_recepcion": "Cambio de horario solicitado",
  "estado": "Confirmada"
}
```

**Response 200:** (mismo formato que GET /citas/{id})

### 6. DELETE /citas/{id}

Cancela una cita (soft delete).

**Request Body:**
```json
{
  "motivo_cancelacion": "Paciente solicitó cancelación"
}
```

**Response 200:** (mismo formato que GET /citas/{id} con estado "Cancelada")

## ✅ Validaciones Implementadas

### Validaciones de Datos

1. **Paciente activo**: Verifica que el paciente exista y esté activo
2. **Podólogo activo**: Verifica que el podólogo exista y esté activo
3. **Fecha futura**: La cita debe agendarse con al menos 1 hora de anticipación
4. **Formatos correctos**: Validación de tipos de datos con Pydantic

### Validaciones de Conflictos

1. **Conflicto de horario**: Detecta si el podólogo ya tiene una cita en ese horario
2. **Una cita por día**: El paciente no puede tener múltiples citas el mismo día
3. **Estado válido**: No se pueden actualizar/cancelar citas completadas

### Cálculos Automáticos

1. **Duración**: `fecha_hora_fin = fecha_hora_inicio + 30 minutos`
2. **Primera vez**: Query a la tabla para determinar si es la primera cita completada
3. **Estado inicial**: Las citas se crean con estado "Confirmada"

## 🔧 Configuración

### Variables de Entorno

```bash
DATABASE_URL=postgresql://usuario:password@host:5432/podoskin
```

### Inicialización

```python
from citas import service

# Inicializar pool de conexiones
service.init_db_pool(database_url)

# Al finalizar
service.close_db_pool()
```

### Integración con FastAPI

```python
from fastapi import FastAPI
from citas import router as citas_router

app = FastAPI()

# Registrar router
app.include_router(citas_router)
```

## 📊 Esquema de Base de Datos

### Tabla: `citas`

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
```

### Índices

```sql
CREATE INDEX idx_citas_paciente ON citas(id_paciente);
CREATE INDEX idx_citas_podologo ON citas(id_podologo);
CREATE INDEX idx_citas_fecha ON citas(fecha_hora_inicio);
CREATE INDEX idx_citas_estado ON citas(estado);
```

## 🧪 Pruebas

### Ejecutar Demo de Validación

```bash
cd backend
python citas/demo_validacion.py
```

Este script demuestra:
1. ✅ Consulta de disponibilidad
2. ✅ Creación de cita exitosa
3. ✅ Detección de conflictos de horario
4. ✅ Cancelación de cita

### Pruebas Manuales con curl

```bash
# 1. Obtener disponibilidad
curl "http://localhost:8000/citas/disponibilidad?id_podologo=1&fecha=2024-12-26"

# 2. Crear cita
curl -X POST http://localhost:8000/citas \
  -H "Content-Type: application/json" \
  -d '{
    "id_paciente": 1,
    "id_podologo": 1,
    "fecha_hora_inicio": "2024-12-26T10:00:00",
    "tipo_cita": "Consulta",
    "motivo_consulta": "Dolor en el talón"
  }'

# 3. Listar citas
curl "http://localhost:8000/citas?id_paciente=1&limit=10"

# 4. Obtener cita específica
curl "http://localhost:8000/citas/123"

# 5. Actualizar cita
curl -X PUT http://localhost:8000/citas/123 \
  -H "Content-Type: application/json" \
  -d '{
    "notas_recepcion": "Cambio de horario solicitado"
  }'

# 6. Cancelar cita
curl -X DELETE http://localhost:8000/citas/123 \
  -H "Content-Type: application/json" \
  -d '{
    "motivo_cancelacion": "Paciente canceló"
  }'
```

## 🔐 Seguridad

- ✅ Validación de entrada con Pydantic
- ✅ SQL injection prevention (prepared statements)
- ✅ Soft delete (no eliminación física)
- ✅ Auditoría (fecha_creacion, fecha_actualizacion)
- ✅ Restricciones de integridad referencial

## 📝 Notas Técnicas

### Lógica Programática (No IA)

Este módulo implementa **lógica determinística tradicional**, no utiliza modelos de lenguaje ni toma decisiones probabilísticas:

- Validaciones basadas en reglas
- Queries SQL directas
- Cálculos matemáticos simples
- Condicionales y bucles estándar

### Patrones de Diseño

- **Repository Pattern**: Service layer abstrae el acceso a datos
- **DTO Pattern**: Modelos Pydantic separan representación de datos
- **Dependency Injection**: Compatible con FastAPI dependencies
- **Connection Pooling**: Reutilización eficiente de conexiones DB

### Gestión de Errores

```python
try:
    cita = await service.crear_cita(...)
except ValueError as e:
    # Error de validación (400/409)
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    # Error interno (500)
    logger.error(f"Error: {e}")
    raise HTTPException(status_code=500, detail="Error interno")
```

## 📚 Referencias

- **FSD**: Sección 2.4 - Especificación de endpoints de citas
- **SRS**: Sección 3.1.3 - Esquema de base de datos de citas
- **Repositorio**: `/backend/citas/`

## 👥 Autor

Implementado por: DEV Backend Citas Agent  
Fecha: Diciembre 2024  
Proyecto: Podoskin Solution
