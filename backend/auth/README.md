# 🔐 Módulo de Autenticación - Podoskin Solution

Sistema completo de autenticación y autorización REST para FastAPI con JWT y RBAC.

## 📋 Características

### ✅ Autenticación
- Login con username/password
- Tokens JWT con expiración (1 hora por defecto)
- Password hashing con bcrypt
- Rate limiting (5 intentos por minuto)
- Actualización de último acceso

### ✅ Middleware de Autenticación
- Validación automática de JWT tokens
- Extracción del usuario actual
- Verificación de usuario activo
- Dependencies de FastAPI reutilizables

### ✅ Autorización RBAC
- Control de acceso basado en roles
- Decorators para requerir roles específicos
- Role checkers como dependencies
- Roles soportados: Admin, Podologo, Recepcionista, Asistente

### ✅ Base de Datos
- Pool de conexiones PostgreSQL
- Operaciones asíncronas
- Consultas preparadas para seguridad

---

## 🚀 Instalación

### 1. Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Copiar `.env.example` a `.env`:

```bash
cp .env.example .env
```

Editar `.env` con tus valores:

```env
JWT_SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=postgresql://postgres:password@localhost:5432/podoskin_db
```

**IMPORTANTE**: Genera una clave secreta segura:

```bash
python -c "import secrets; print(secrets.token_urlsec(32))"
```

### 3. Verificar Base de Datos

Asegúrate de que la base de datos esté corriendo y tenga la tabla `usuarios`:

```bash
# Con Docker
cd ..
docker-compose up -d

# Verificar
docker logs -f podoskin_db
```

---

## 📖 Uso

### Iniciar el Servidor

```bash
python main.py
```

O con uvicorn directamente:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Probar la API

Abrir en navegador: http://localhost:8000/docs

---

## 🔑 Endpoints de Autenticación

### POST /auth/login

**Request:**

```json
{
  "username": "dr.santiago",
  "password": "password123"
}
```

**Response 200:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "dr.santiago",
    "email": "santiago@podoskin.com",
    "rol": "Podologo",
    "nombre_completo": "Dr. Santiago Ornelas"
  }
}
```

**Errores:**

- `401`: Credenciales incorrectas
- `403`: Usuario inactivo
- `422`: Error de validación
- `429`: Demasiados intentos

---

## 🛡️ Proteger Endpoints

### Opción 1: Usar Dependency

```python
from fastapi import Depends
from auth import get_current_user, User

@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hola {current_user.nombre_completo}"}
```

### Opción 2: Usar Decorator

```python
from auth import require_role, get_current_user

@app.post("/pacientes")
@require_role(["Admin", "Podologo", "Recepcionista"])
async def crear_paciente(current_user: User = Depends(get_current_user)):
    # Solo estos roles pueden acceder
    return {"status": "created"}
```

### Opción 3: Usar RoleChecker

```python
from auth import AdminOnly, PodologoOrAdmin, StaffOnly

@app.delete("/usuarios/{id}")
async def eliminar_usuario(
    id: int,
    current_user: User = Depends(AdminOnly)
):
    # Solo Admin puede eliminar usuarios
    return {"status": "deleted"}
```

---

## 🎯 Ejemplos de Autorización

### Solo Administradores

```python
from auth import require_admin, get_current_user

@app.delete("/usuarios/{id}")
@require_admin()
async def eliminar_usuario(
    id: int,
    current_user: User = Depends(get_current_user)
):
    return {"status": "deleted"}
```

### Podólogos o Admin

```python
from auth import require_podologo, get_current_user

@app.post("/diagnosticos")
@require_podologo()
async def crear_diagnostico(
    diagnostico: DiagnosticoCreate,
    current_user: User = Depends(get_current_user)
):
    return {"status": "created"}
```

### Cualquier Staff

```python
from auth import require_staff, get_current_user

@app.get("/agenda")
@require_staff()
async def ver_agenda(current_user: User = Depends(get_current_user)):
    return {"agenda": [...]}
```

### Roles Personalizados

```python
from auth import require_role, get_current_user

@app.post("/citas")
@require_role(["Admin", "Recepcionista"])
async def crear_cita(
    cita: CitaCreate,
    current_user: User = Depends(get_current_user)
):
    return {"status": "created"}
```

---

## 📦 Estructura del Módulo

```
backend/auth/
├── __init__.py          # Exports del módulo
├── models.py            # Modelos Pydantic
├── jwt_handler.py       # Generación y validación de JWT
├── database.py          # Acceso a base de datos
├── middleware.py        # Middleware de autenticación
├── authorization.py     # RBAC y decorators
└── router.py            # Endpoints REST
```

---

## 🔒 Seguridad

### Password Hashing

- Usa bcrypt con salt automático
- Verifica contraseñas sin exponer el hash
- Nunca almacena contraseñas en texto plano

```python
from auth import get_password_hash, verify_password

# Crear usuario nuevo
hashed = get_password_hash("password123")

# Verificar contraseña
is_valid = verify_password("password123", hashed)
```

### Rate Limiting

- Máximo 5 intentos de login por minuto por usuario
- En producción, usar Redis para rate limiting distribuido

### JWT Tokens

- Firmados con HS256
- Expiran en 1 hora
- Incluyen: username (sub), rol, timestamps

**Estructura del token:**

```json
{
  "sub": "dr.santiago",
  "rol": "Podologo",
  "exp": 1735689600,
  "iat": 1735686000
}
```

---

## 🧪 Testing

### Con curl

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"dr.santiago","password":"password123"}'

# Usar token
TOKEN="eyJhbGciOiJIUzI1NiIs..."
curl -X GET http://localhost:8000/protected \
  -H "Authorization: Bearer $TOKEN"
```

### Con Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "dr.santiago", "password": "password123"}
)

data = response.json()
token = data["access_token"]

# Usar token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/protected",
    headers=headers
)

print(response.json())
```

---

## 🐛 Troubleshooting

### Error: "Failed to initialize auth database pool"

**Solución:** Verificar que PostgreSQL esté corriendo y que DATABASE_URL sea correcto.

```bash
# Verificar conexión
psql postgresql://postgres:password@localhost:5432/podoskin_db -c "SELECT 1"
```

### Error: "Token inválido o expirado"

**Solución:** El token expiró (1 hora). Hacer login nuevamente.

### Error: "Usuario inactivo"

**Solución:** El usuario existe pero está marcado como inactivo en la BD.

```sql
-- Activar usuario
UPDATE usuarios SET activo = true WHERE nombre_usuario = 'dr.santiago';
```

### Error: "No tiene permisos para esta acción"

**Solución:** El usuario no tiene el rol requerido. Verificar roles en la BD.

```sql
-- Ver roles de usuarios
SELECT nombre_usuario, rol, activo FROM usuarios;
```

---

## 📚 Referencia de API

### Models

- `LoginRequest`: Credenciales de login
- `LoginResponse`: Respuesta con token y usuario
- `UserResponse`: Datos públicos del usuario
- `TokenData`: Payload del JWT token
- `User`: Modelo completo de usuario
- `ErrorResponse`: Respuesta de error
- `RateLimitResponse`: Respuesta de rate limit

### Functions

- `verify_password()`: Verifica contraseña con hash
- `get_password_hash()`: Genera hash de contraseña
- `create_access_token()`: Genera JWT token
- `decode_access_token()`: Decodifica JWT token
- `verify_token()`: Valida JWT token
- `get_current_user()`: Dependency para obtener usuario
- `require_role()`: Decorator RBAC
- `check_user_permission()`: Verifica permisos

---

## 🔄 Próximos Pasos

1. ✅ Autenticación básica con JWT
2. ✅ RBAC con decorators
3. ✅ Rate limiting simple
4. ⬜ Refresh tokens
5. ⬜ Blacklist de tokens
6. ⬜ Rate limiting con Redis
7. ⬜ 2FA (Two-Factor Authentication)
8. ⬜ OAuth2 (Google, Facebook)

---

**Desarrollado para**: Podoskin Solution  
**Versión**: 1.0.0  
**Fecha**: Diciembre 2024
