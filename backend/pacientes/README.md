# Backend Pacientes Module

REST API endpoints for patient management in the Podoskin system.

## Overview

This module provides complete CRUD operations for:
- **Pacientes** (Patients)
- **Alergias** (Allergies)
- **Antecedentes Médicos** (Medical History)

## Architecture

```
backend/pacientes/
├── __init__.py       # Module initialization
├── database.py       # Database connection utilities
├── models.py         # Pydantic schemas (request/response)
├── service.py        # Business logic and database operations
└── router.py         # FastAPI endpoints
```

## Setup

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=podoskin

# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=true
LOG_LEVEL=info

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Running the Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000/api
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Pacientes (Patients)

#### 1. GET /api/pacientes - List Patients

Get paginated list of patients with optional search and filters.

**Query Parameters:**
- `page` (int): Page number, default 1
- `limit` (int): Items per page, default 20, max 100
- `search` (string): Search by name or phone
- `activo` (bool): Filter by active status, default true
- `orden` (string): Order by field (nombre, fecha_registro, fecha_nacimiento)
- `direccion` (string): Sort direction (asc, desc)

**Example Request:**
```bash
curl "http://localhost:8000/api/pacientes?page=1&limit=20&search=Juan&activo=true"
```

**Example Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "nombre_completo": "Juan Pérez García",
      "telefono_principal": "6861234567",
      "email": "juan@email.com",
      "fecha_nacimiento": "1990-05-15",
      "edad": 34,
      "ultima_cita": "2024-12-20T10:00:00",
      "total_citas": 5,
      "activo": true
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20,
  "pages": 8
}
```

#### 2. GET /api/pacientes/{id} - Get Patient Details

Get complete information for a specific patient.

**Example Request:**
```bash
curl "http://localhost:8000/api/pacientes/1"
```

**Example Response (200):**
```json
{
  "id": 1,
  "primer_nombre": "Juan",
  "segundo_nombre": null,
  "primer_apellido": "Pérez",
  "segundo_apellido": "García",
  "nombre_completo": "Juan Pérez García",
  "fecha_nacimiento": "1990-05-15",
  "edad": 34,
  "sexo": "M",
  "curp": "PEGJ900515HBCRRS09",
  "telefono_principal": "6861234567",
  "telefono_secundario": null,
  "email": "juan@email.com",
  "calle": "Av. Principal",
  "numero_exterior": "123",
  "numero_interior": null,
  "colonia": "Centro",
  "ciudad": "Hermosillo",
  "estado": "Sonora",
  "cp": "83000",
  "ocupacion": "Ingeniero",
  "estado_civil": "Soltero",
  "referencia_como_nos_conocio": "Recomendación",
  "activo": true,
  "fecha_registro": "2024-01-15T10:30:00",
  "fecha_modificacion": null,
  "ultima_cita": "2024-12-20T10:00:00",
  "total_citas": 5
}
```

**Error Responses:**
- `404 Not Found`: Patient not found

#### 3. POST /api/pacientes - Create Patient

Create a new patient record.

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/pacientes" \
  -H "Content-Type: application/json" \
  -d '{
    "primer_nombre": "María",
    "primer_apellido": "González",
    "fecha_nacimiento": "1985-03-20",
    "sexo": "F",
    "telefono_principal": "6861234568",
    "email": "maria@email.com",
    "ciudad": "Hermosillo",
    "estado": "Sonora"
  }'
```

**Example Response (201 Created):**
```json
{
  "id": 42,
  "nombre_completo": "María González",
  "primer_nombre": "María",
  "primer_apellido": "González",
  ...
  "fecha_registro": "2024-12-25T10:30:00"
}
```

**Error Responses:**
- `400 Bad Request`: Validation error (invalid CURP, future birth date, etc.)
- `409 Conflict`: Duplicate CURP

#### 4. PUT /api/pacientes/{id} - Update Patient

Update an existing patient record.

**Example Request:**
```bash
curl -X PUT "http://localhost:8000/api/pacientes/1" \
  -H "Content-Type: application/json" \
  -d '{
    "telefono_principal": "6869999999",
    "email": "newemail@email.com"
  }'
```

**Example Response (200):**
```json
{
  "id": 1,
  "nombre_completo": "Juan Pérez García",
  ...
  "telefono_principal": "6869999999",
  "email": "newemail@email.com",
  "fecha_modificacion": "2024-12-25T15:45:00"
}
```

**Error Responses:**
- `404 Not Found`: Patient not found
- `409 Conflict`: Duplicate CURP

#### 5. DELETE /api/pacientes/{id} - Delete Patient

Soft delete a patient (sets activo = false).

**Example Request:**
```bash
curl -X DELETE "http://localhost:8000/api/pacientes/1"
```

**Example Response (204 No Content)**

**Error Responses:**
- `404 Not Found`: Patient not found or already inactive

---

### Alergias (Allergies)

#### 6. GET /api/pacientes/{id}/alergias - Get Patient Allergies

Get all active allergies for a patient.

**Example Request:**
```bash
curl "http://localhost:8000/api/pacientes/1/alergias"
```

**Example Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "id_paciente": 1,
      "tipo_alergeno": "Medicamento",
      "nombre_alergeno": "Penicilina",
      "reaccion": "Rash cutáneo",
      "severidad": "Moderada",
      "fecha_diagnostico": "2020-03-15",
      "notas": "Confirmar con familia",
      "activo": true,
      "fecha_registro": "2024-01-15T10:30:00"
    }
  ],
  "total": 1
}
```

**Error Responses:**
- `404 Not Found`: Patient not found

#### 7. POST /api/pacientes/{id}/alergias - Create Allergy

Create a new allergy record for a patient.

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/pacientes/1/alergias" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_alergeno": "Medicamento",
    "nombre_alergeno": "Aspirina",
    "reaccion": "Urticaria",
    "severidad": "Leve",
    "fecha_diagnostico": "2023-06-10"
  }'
```

**Example Response (201 Created):**
```json
{
  "id": 2,
  "id_paciente": 1,
  "tipo_alergeno": "Medicamento",
  "nombre_alergeno": "Aspirina",
  "reaccion": "Urticaria",
  "severidad": "Leve",
  "fecha_diagnostico": "2023-06-10",
  "notas": null,
  "activo": true,
  "fecha_registro": "2024-12-25T10:30:00"
}
```

**Error Responses:**
- `404 Not Found`: Patient not found

---

### Antecedentes Médicos (Medical History)

#### 8. GET /api/pacientes/{id}/antecedentes - Get Medical History

Get all active medical history entries for a patient.

**Example Request:**
```bash
curl "http://localhost:8000/api/pacientes/1/antecedentes"
```

**Example Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "id_paciente": 1,
      "tipo_categoria": "Patologico",
      "nombre_enfermedad": "Diabetes Mellitus Tipo 2",
      "parentesco": null,
      "fecha_inicio": "2018-01-15",
      "descripcion_temporal": "5 años de evolución",
      "tratamiento_actual": "Metformina 850mg c/12h",
      "controlado": true,
      "notas": "HbA1c: 6.5%",
      "activo": true,
      "fecha_registro": "2024-01-15T10:30:00"
    },
    {
      "id": 2,
      "id_paciente": 1,
      "tipo_categoria": "Heredofamiliar",
      "nombre_enfermedad": "Hipertensión Arterial",
      "parentesco": "Padre",
      "fecha_inicio": null,
      "descripcion_temporal": null,
      "tratamiento_actual": null,
      "controlado": null,
      "notas": null,
      "activo": true,
      "fecha_registro": "2024-01-15T10:30:00"
    }
  ],
  "total": 2
}
```

**Error Responses:**
- `404 Not Found`: Patient not found

#### 9. POST /api/pacientes/{id}/antecedentes - Create Medical History Entry

Create a new medical history entry for a patient.

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/pacientes/1/antecedentes" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_categoria": "Quirurgico",
    "nombre_enfermedad": "Apendicectomía",
    "fecha_inicio": "2015-08-20",
    "descripcion_temporal": "Hace 9 años",
    "notas": "Sin complicaciones"
  }'
```

**Example Response (201 Created):**
```json
{
  "id": 3,
  "id_paciente": 1,
  "tipo_categoria": "Quirurgico",
  "nombre_enfermedad": "Apendicectomía",
  "parentesco": null,
  "fecha_inicio": "2015-08-20",
  "descripcion_temporal": "Hace 9 años",
  "tratamiento_actual": null,
  "controlado": null,
  "notas": "Sin complicaciones",
  "activo": true,
  "fecha_registro": "2024-12-25T10:30:00"
}
```

**Error Responses:**
- `404 Not Found`: Patient not found

---

## Data Models

### Patient Fields

**Required:**
- `primer_nombre` (string, 1-50 chars)
- `primer_apellido` (string, 1-50 chars)
- `fecha_nacimiento` (date, YYYY-MM-DD, cannot be future)
- `sexo` (enum: "M", "F", "O")
- `telefono_principal` (string, 10-15 digits)

**Optional:**
- `segundo_nombre` (string, max 50 chars)
- `segundo_apellido` (string, max 50 chars)
- `curp` (string, 18 chars, format: 4 letters + 6 digits + H/M + 5 letters + 2 digits)
- `telefono_secundario` (string, 10-15 digits)
- `email` (valid email format)
- Address fields: `calle`, `numero_exterior`, `numero_interior`, `colonia`, `ciudad`, `estado`, `cp`
- `ocupacion` (string)
- `estado_civil` (string)
- `referencia_como_nos_conocio` (string, max 255 chars)

### Allergy Fields

**Required:**
- `tipo_alergeno` (enum: "Medicamento", "Alimento", "Ambiental", "Material", "Otro")
- `nombre_alergeno` (string, 1-100 chars)
- `severidad` (enum: "Leve", "Moderada", "Grave", "Mortal")

**Optional:**
- `reaccion` (string)
- `fecha_diagnostico` (date)
- `notas` (string)

### Medical History Fields

**Required:**
- `tipo_categoria` (enum: "Heredofamiliar", "Patologico", "Quirurgico", "Traumatico", "Transfusional")
- `nombre_enfermedad` (string, 1-200 chars)

**Optional:**
- `parentesco` (string, max 50 chars)
- `fecha_inicio` (date)
- `descripcion_temporal` (string)
- `tratamiento_actual` (string)
- `controlado` (boolean)
- `notas` (string)

---

## Error Handling

All endpoints return standard HTTP status codes:

- **200 OK**: Successful GET/PUT request
- **201 Created**: Successful POST request
- **204 No Content**: Successful DELETE request
- **400 Bad Request**: Validation error
- **404 Not Found**: Resource not found
- **409 Conflict**: Duplicate constraint violation
- **500 Internal Server Error**: Server error

Error response format:
```json
{
  "detail": "Error message description"
}
```

---

## Database Schema

The module uses the following PostgreSQL tables defined in `data/03_pacientes.sql`:

- `pacientes`: Main patient information
- `alergias`: Patient allergies
- `antecedentes_medicos`: Medical history
- `estilo_vida`: Lifestyle information
- `historia_ginecologica`: Gynecological history (for female patients)
- `signos_vitales`: Vital signs

---

## Testing

### Manual Testing with curl

See the examples above for each endpoint.

### Testing with API Docs

Navigate to http://localhost:8000/docs for interactive API documentation where you can test all endpoints.

### Integration Testing

Create test scripts in `backend/tests/test_pacientes.py` using pytest:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_pacientes():
    response = client.get("/api/pacientes")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
```

---

## Notes

- All DELETE operations are **soft deletes** (set `activo = false`)
- Patient ages are calculated dynamically from `fecha_nacimiento`
- CURP validation follows Mexican standard format
- Phone numbers should contain only digits (+ and - are allowed but stripped)
- Search is case-insensitive and searches across name and phone fields
- Pagination max limit is 100 items per page

---

## Dependencies

See `backend/requirements.txt` for full list. Key dependencies:

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `asyncpg` - PostgreSQL async driver
- `pydantic` - Data validation
- `python-dotenv` - Environment variables

---

## Future Enhancements

- [ ] Authentication and authorization
- [ ] Audit logging
- [ ] Batch operations
- [ ] Export to PDF/Excel
- [ ] Photo upload for patients
- [ ] Advanced search filters
- [ ] Soft delete recovery endpoint
- [ ] Pagination cursor-based alternative
