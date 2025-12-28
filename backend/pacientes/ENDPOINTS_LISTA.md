# Endpoints Implementados - Backend Pacientes

## 📋 Lista Completa de Endpoints REST

### Pacientes (Patients)

#### 1. GET /api/pacientes
**Descripción:** Lista paginada de pacientes con búsqueda y filtros

**Parámetros de Query:**
- `page` (int): Número de página, default 1
- `limit` (int): Items por página, default 20, máx 100
- `search` (string): Búsqueda por nombre o teléfono
- `activo` (bool): Filtrar por estado activo
- `orden` (string): Campo de ordenamiento
- `direccion` (string): Dirección de ordenamiento (asc/desc)

**Ejemplo Response:**
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

---

#### 2. GET /api/pacientes/{id}
**Descripción:** Obtener detalle completo de un paciente

**Path Parameters:**
- `id` (int): ID del paciente

**Response:** Objeto PacienteResponse con toda la información

---

#### 3. POST /api/pacientes
**Descripción:** Crear nuevo paciente

**Request Body (campos requeridos):**
```json
{
  "primer_nombre": "María",
  "primer_apellido": "González",
  "fecha_nacimiento": "1985-03-20",
  "sexo": "F",
  "telefono_principal": "6861234568"
}
```

**Response:** Objeto PacienteResponse del paciente creado (201 Created)

---

#### 4. PUT /api/pacientes/{id}
**Descripción:** Actualizar paciente existente

**Path Parameters:**
- `id` (int): ID del paciente

**Request Body (todos opcionales):**
```json
{
  "telefono_principal": "6869999999",
  "email": "newemail@email.com"
}
```

**Response:** Objeto PacienteResponse actualizado

---

#### 5. DELETE /api/pacientes/{id}
**Descripción:** Eliminación suave de paciente (soft delete)

**Path Parameters:**
- `id` (int): ID del paciente

**Response:** 204 No Content

---

### Alergias (Allergies)

#### 6. GET /api/pacientes/{id}/alergias
**Descripción:** Obtener todas las alergias de un paciente

**Path Parameters:**
- `id` (int): ID del paciente

**Ejemplo Response:**
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

---

#### 7. POST /api/pacientes/{id}/alergias
**Descripción:** Registrar nueva alergia para un paciente

**Path Parameters:**
- `id` (int): ID del paciente

**Request Body:**
```json
{
  "tipo_alergeno": "Medicamento",
  "nombre_alergeno": "Aspirina",
  "reaccion": "Urticaria",
  "severidad": "Leve",
  "fecha_diagnostico": "2023-06-10",
  "notas": "Reacción moderada"
}
```

**Valores permitidos:**
- `tipo_alergeno`: "Medicamento" | "Alimento" | "Ambiental" | "Material" | "Otro"
- `severidad`: "Leve" | "Moderada" | "Grave" | "Mortal"

**Response:** Objeto AlergiaResponse creado (201 Created)

---

### Antecedentes Médicos (Medical History)

#### 8. GET /api/pacientes/{id}/antecedentes
**Descripción:** Obtener historial médico de un paciente

**Path Parameters:**
- `id` (int): ID del paciente

**Ejemplo Response:**
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

---

#### 9. POST /api/pacientes/{id}/antecedentes
**Descripción:** Registrar nuevo antecedente médico

**Path Parameters:**
- `id` (int): ID del paciente

**Request Body:**
```json
{
  "tipo_categoria": "Quirurgico",
  "nombre_enfermedad": "Apendicectomía",
  "fecha_inicio": "2015-08-20",
  "descripcion_temporal": "Hace 9 años",
  "notas": "Sin complicaciones"
}
```

**Valores permitidos para tipo_categoria:**
- "Heredofamiliar" - Antecedentes familiares (requiere `parentesco`)
- "Patologico" - Enfermedades previas o actuales
- "Quirurgico" - Cirugías previas
- "Traumatico" - Traumatismos o lesiones
- "Transfusional" - Historial de transfusiones

**Response:** Objeto AntecedenteResponse creado (201 Created)

---

## 🔧 Características Técnicas

### Validaciones Implementadas

**CURP:**
- Formato: 4 letras + 6 dígitos + H/M + 5 letras + 2 dígitos
- Ejemplo: PEGJ900515HBCRRS09
- Único en el sistema

**Fecha de Nacimiento:**
- No puede ser futura
- Se calcula edad automáticamente

**Teléfonos:**
- Solo dígitos (se permiten + - espacios pero se eliminan)
- Longitud: 10-15 caracteres

**Email:**
- Formato válido de email

**Sexo:**
- M = Masculino
- F = Femenino
- O = Otro

### Códigos de Estado HTTP

- **200 OK** - Operación exitosa (GET, PUT)
- **201 Created** - Recurso creado (POST)
- **204 No Content** - Eliminación exitosa (DELETE)
- **400 Bad Request** - Error de validación
- **404 Not Found** - Recurso no encontrado
- **409 Conflict** - Violación de restricción única (CURP duplicado)
- **500 Internal Server Error** - Error del servidor

### Formato de Errores

```json
{
  "detail": "Mensaje descriptivo del error"
}
```

---

## 📝 Ejemplos de Uso con curl

### Crear Paciente
```bash
curl -X POST "http://localhost:8000/api/pacientes" \
  -H "Content-Type: application/json" \
  -d '{
    "primer_nombre": "Juan",
    "primer_apellido": "Pérez",
    "fecha_nacimiento": "1990-05-15",
    "sexo": "M",
    "telefono_principal": "6861234567",
    "email": "juan@email.com",
    "ciudad": "Hermosillo",
    "estado": "Sonora"
  }'
```

### Buscar Pacientes
```bash
curl "http://localhost:8000/api/pacientes?search=Juan&page=1&limit=20"
```

### Actualizar Teléfono
```bash
curl -X PUT "http://localhost:8000/api/pacientes/1" \
  -H "Content-Type: application/json" \
  -d '{
    "telefono_principal": "6869999999"
  }'
```

### Agregar Alergia
```bash
curl -X POST "http://localhost:8000/api/pacientes/1/alergias" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_alergeno": "Medicamento",
    "nombre_alergeno": "Penicilina",
    "severidad": "Moderada",
    "reaccion": "Rash cutáneo"
  }'
```

### Agregar Antecedente
```bash
curl -X POST "http://localhost:8000/api/pacientes/1/antecedentes" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_categoria": "Patologico",
    "nombre_enfermedad": "Diabetes Mellitus Tipo 2",
    "fecha_inicio": "2018-01-15",
    "tratamiento_actual": "Metformina 850mg",
    "controlado": true
  }'
```

---

## 🚀 Acceso a Documentación Interactiva

**Swagger UI (recomendado):**
```
http://localhost:8000/docs
```
- Interfaz interactiva
- Probar endpoints directamente
- Ver schemas de request/response

**ReDoc:**
```
http://localhost:8000/redoc
```
- Documentación estática más detallada
- Mejor para lectura

---

## 💡 Notas Importantes

1. **Soft Delete**: El endpoint DELETE no elimina físicamente registros, solo marca `activo = false`
2. **Edad Calculada**: La edad se calcula dinámicamente desde `fecha_nacimiento`
3. **Búsqueda**: Case-insensitive, busca en nombre y teléfono
4. **Paginación**: Límite máximo de 100 items por página
5. **CURP Opcional**: No es obligatorio pero debe ser único si se proporciona
6. **Timestamps**: `fecha_registro` y `fecha_modificacion` son automáticos

---

## ✅ Estado del Módulo

**Implementación:** ✅ COMPLETA  
**Testing:** ⏳ Manual disponible (Swagger UI)  
**Documentación:** ✅ COMPLETA  
**Listo para:** Integración con Frontend, Testing Automatizado, Producción (con Auth)

---

**Fecha:** Diciembre 2024  
**Versión:** 1.0.0  
**Autor:** AGENTE-3 (Backend Pacientes)
