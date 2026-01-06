
```markdown
# Solución:  Problemas Pendientes Backend (Login + Appointments)

**Proyecto**: Podoskin Solution  
**Fecha**: 31 de Diciembre, 2025  
**Estado**: Conexión PostgreSQL ✅ | Login ⚠️ | Appointments ⚠️

---

## CONTEXTO

El backend se conecta correctamente a PostgreSQL en Docker, pero hay 2 problemas pendientes: 

1. **Login falla (500)**:  Bug de bcrypt en Windows con Python 3.13+
2. **GET /appointments retorna 404**: Router no maneja query params correctamente

---

## PROBLEMA 1: ARREGLAR LOGIN (bcrypt → pbkdf2_sha256)

### Paso 1.1: Modificar auth/utils.py

**Ubicación**: `backend/auth/utils.py`

**ANTES:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

**DESPUÉS:**

```python
from passlib.context import CryptContext

# PBKDF2 funciona correctamente en Windows (bcrypt tiene bugs en Python 3.13+)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
```

---

### Paso 1.2: Modificar auth/jwt_handler.py

**Ubicación**: `backend/auth/jwt_handler.py`

**Buscar líneas similares a:**

```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

**Cambiar por:**

```python
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
```

**Si el archivo NO tiene pwd_context**, verificar que importa desde `auth/utils.py`:

```python
from auth.utils import pwd_context  # Debe usar el de utils. py
```

---

### Paso 1.3: Regenerar Hash del Usuario de Prueba

**Opción A - Script Python:**

Crear archivo temporal `backend/fix_password_hash.py`:

```python
"""
Script para regenerar hash de password del usuario de prueba
"""
import psycopg
from passlib.context import CryptContext

# Configurar PBKDF2 (igual que en auth/utils.py)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Conectar a la base de datos
conn = psycopg.connect("postgresql://podoskin_user@localhost:5432/podoskin_db")
cursor = conn.cursor()

# Password de prueba
plain_password = "Admin123!"  # ← Cambiar si usas otro password
username = "admin"            # ← Cambiar si usas otro usuario

# Generar nuevo hash
new_hash = pwd_context.hash(plain_password)

# Actualizar en base de datos
cursor.execute(
    "UPDATE usuarios SET password_hash = %s WHERE username = %s",
    (new_hash, username)
)

# Verificar
cursor.execute("SELECT username, password_hash FROM usuarios WHERE username = %s", (username,))
result = cursor.fetchone()

print(f"✅ Password actualizado para usuario:  {result[0]}")
print(f"   Nuevo hash: {result[1][: 50]}...")

conn.commit()
conn.close()
```

**Ejecutar:**

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python fix_password_hash.py
```

---

**Opción B - SQL directo:**

Si prefieres hacerlo manualmente:

```powershell
# Conectar a PostgreSQL
docker exec -it podoskin_postgres psql -U podoskin_user -d podoskin_db
```

```sql
-- Generar hash manualmente (desde Python primero)
-- En Python: 
-- from passlib.context import CryptContext
-- pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
-- print(pwd_context.hash("Admin123!"))

-- Luego actualizar en SQL: 
UPDATE usuarios 
SET password_hash = '$pbkdf2-sha256$.. .'  -- ← Pegar el hash generado
WHERE username = 'admin';

-- Verificar
SELECT username, password_hash FROM usuarios WHERE username = 'admin';
```

---

### Paso 1.4: Probar Login

```powershell
# Desde PowerShell (o usar Postman/Insomnia)
$body = @{
    username = "admin"
    password = "Admin123!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

**Respuesta esperada (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.. .",
  "token_type":  "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@podoskin.com",
    "rol": "Admin",
    "nombre_completo": "Administrador Sistema"
  }
}
```

---

## PROBLEMA 2: ARREGLAR GET /appointments (404)

### Paso 2.1: Verificar Router Montado

**Archivo**: `backend/main.py`

**Verificar que existe:**

```python
from citas.router import router as citas_router

app.include_router(citas_router, prefix="/appointments", tags=["Citas"])
```

**Si NO existe**, agregarlo:

```python
# En la sección de imports
from citas.router import router as citas_router

# En la sección de routers
app.include_router(citas_router, prefix="/appointments", tags=["Citas"])
```

---

### Paso 2.2: Verificar Endpoint en citas/router.py

**Archivo**: `backend/citas/router.py`

**Buscar endpoint GET en raíz:**

```python
@router.get("/")
async def listar_citas(
    start_date:  Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    doctor_id: Optional[str] = Query(None),
    patient_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar citas con filtros opcionales
    """
    # ...  implementación
```

**Si NO existe**, agregarlo:

```python
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from auth.middleware import get_current_user

router = APIRouter()

@router.get("/")
async def listar_citas(
    start_date: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    end_date: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    doctor_id: Optional[str] = Query(None, description="IDs de doctores separados por coma"),
    patient_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar citas con filtros opcionales. 
    
    Query params:
    - start_date: Filtrar desde esta fecha
    - end_date: Filtrar hasta esta fecha  
    - doctor_id:  Filtrar por doctor(es), ej: "1,2,3"
    - patient_id:  Filtrar por paciente
    - status: Filtrar por estado
    """
    try:
        # Parsear doctor_ids si vienen como "1,2,3"
        doctor_ids = None
        if doctor_id:
            doctor_ids = [int(id. strip()) for id in doctor_id.split(",")]
        
        # Llamar al servicio (debes tener esta función en citas/service.py)
        from citas.service import obtener_citas
        
        citas = await obtener_citas(
            start_date=start_date,
            end_date=end_date,
            doctor_ids=doctor_ids,
            patient_id=patient_id,
            status=status
        )
        
        return citas
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Paso 2.3: Verificar Servicio en citas/service.py

**Archivo**: `backend/citas/service.py`

**Verificar que existe la función `obtener_citas`:**

```python
async def obtener_citas(
    start_date: Optional[str] = None,
    end_date:  Optional[str] = None,
    doctor_ids: Optional[list[int]] = None,
    patient_id: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Obtener citas con filtros opcionales
    """
    # Implementación de lógica de negocio
    # ...
```

**Si NO existe**, agregar implementación básica:

```python
from typing import Optional
import psycopg
from citas.database import get_db_connection

async def obtener_citas(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    doctor_ids:  Optional[list[int]] = None,
    patient_id: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Obtener citas con filtros opcionales
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query base
    query = """
        SELECT 
            c.id_cita,
            c.id_paciente,
            c.id_podologo,
            c.fecha_hora_inicio,
            c.fecha_hora_fin,
            c.tipo_cita,
            c. estado,
            c.motivo_consulta,
            c.notas_recepcion,
            c.es_primera_vez,
            p.nombre_completo as nombre_paciente,
            u.nombre_completo as nombre_doctor
        FROM citas c
        LEFT JOIN pacientes p ON c.id_paciente = p.id_paciente
        LEFT JOIN usuarios u ON c.id_podologo = u.id_usuario
        WHERE 1=1
    """
    
    params = []
    
    # Agregar filtros dinámicamente
    if start_date: 
        query += " AND c.fecha_hora_inicio >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND c.fecha_hora_fin <= %s"
        params. append(end_date)
    
    if doctor_ids: 
        placeholders = ",".join(["%s"] * len(doctor_ids))
        query += f" AND c.id_podologo IN ({placeholders})"
        params.extend(doctor_ids)
    
    if patient_id:
        query += " AND c.id_paciente = %s"
        params.append(patient_id)
    
    if status:
        query += " AND c.estado = %s"
        params.append(status)
    
    query += " ORDER BY c.fecha_hora_inicio DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Convertir a diccionarios
    citas = []
    for row in rows:
        citas.append({
            "id":  row[0],
            "id_paciente": row[1],
            "id_podologo": row[2],
            "fecha_hora_inicio": row[3]. isoformat() if row[3] else None,
            "fecha_hora_fin": row[4].isoformat() if row[4] else None,
            "tipo_cita": row[5],
            "estado": row[6],
            "motivo_consulta": row[7],
            "notas_recepcion": row[8],
            "es_primera_vez": row[9],
            "nombre_paciente": row[10],
            "nombre_doctor": row[11]
        })
    
    conn.close()
    return citas
```

---

### Paso 2.4: Probar Endpoint

```powershell
# Primero hacer login para obtener token
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body (@{username="admin"; password="Admin123!"} | ConvertTo-Json)

$token = $loginResponse.access_token

# Probar GET /appointments
Invoke-RestMethod -Uri "http://localhost:8000/appointments?doctor_id=1,2,3" `
    -Method GET `
    -Headers @{ Authorization = "Bearer $token" }
```

**Respuesta esperada (200 OK):**

```json
[
  {
    "id":  1,
    "id_paciente": 5,
    "id_podologo": 2,
    "fecha_hora_inicio": "2025-01-02T10:00:00",
    "fecha_hora_fin": "2025-01-02T11:00:00",
    "tipo_cita": "Consulta",
    "estado": "Confirmada",
    "nombre_paciente": "Juan Pérez",
    "nombre_doctor": "Dr. García"
  }
]
```

---

## VALIDACIONES FINALES

### Checklist

- [ ] `auth/utils.py` usa `pbkdf2_sha256` en lugar de `bcrypt`
- [ ] `auth/jwt_handler.py` usa el mismo esquema
- [ ] Hash de password regenerado en base de datos
- [ ] POST `/auth/login` retorna 200 con token JWT
- [ ] `main.py` incluye `citas_router` en `/appointments`
- [ ] `citas/router.py` tiene endpoint `GET /` con query params
- [ ] `citas/service.py` tiene función `obtener_citas`
- [ ] GET `/appointments?doctor_id=1,2,3` retorna 200 con array de citas

---

## COMANDOS ÚTILES

### Reiniciar backend después de cambios

```powershell
# Ctrl+C en la terminal de uvicorn
# Luego: 
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Ver logs en tiempo real

```powershell
# Los logs aparecen en la terminal donde corre uvicorn
# Buscar líneas con ERROR o WARNING
```

### Verificar endpoints disponibles

```
http://localhost:8000/docs
```

En Swagger UI deberías ver:

- `POST /auth/login`
- `GET /appointments`

---

## RESULTADO ESPERADO

Al completar estos pasos:

✅ Login funcional (retorna token JWT)  
✅ Frontend puede autenticarse  
✅ GET /appointments retorna lista de citas  
✅ Frontend carga calendario sin errores 404  
✅ CRUD de citas funcionando  

---

## TROUBLESHOOTING

### Login sigue fallando después de cambiar a pbkdf2

```powershell
# Verificar que el hash se actualizó
docker exec -it podoskin_postgres psql -U podoskin_user -d podoskin_db -c "SELECT username, LEFT(password_hash, 20) FROM usuarios WHERE username='admin';"

# Debe empezar con:  $pbkdf2-sha256$
# Si empieza con $2b$ es bcrypt viejo
```

### GET /appointments sigue retornando 404

```powershell
# Verificar rutas registradas
# En main.py, agregar después de crear app: 
print(app.routes)

# O ver en http://localhost:8000/openapi. json
# Buscar "/appointments" en el JSON
```

### Error 500 en /appointments

```powershell
# Ver el error completo en la terminal de uvicorn
# Probablemente falta la función obtener_citas en service.py
```

---

**Ejecuta este prompt paso a paso y reporta cualquier error que encuentres.**

```

---

