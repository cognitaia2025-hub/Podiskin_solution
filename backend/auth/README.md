# Backend Authentication - Podoskin Solution

Sistema de autenticación JWT con middleware RBAC para FastAPI.

## 📁 Estructura de Archivos

```
backend/auth/
├── __init__.py          # Exports del módulo
├── models.py            # Modelos Pydantic (LoginRequest, LoginResponse, etc.)
├── utils.py             # JWT y password hashing utilities
├── database.py          # Funciones de acceso a datos de usuarios
├── middleware.py        # Middleware de autenticación y autorización RBAC
└── router.py            # Endpoints REST (/auth/login, etc.)
```

## 🔐 Endpoints Implementados

### POST /auth/login

Autentica un usuario y retorna un JWT token.

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

**Rate Limit:** 5 intentos por minuto por IP

**Errores:**
- `401 Unauthorized`: Credenciales incorrectas
- `403 Forbidden`: Usuario inactivo
- `429 Too Many Requests`: Rate limit excedido

## 🛡️ Middleware de Autenticación

### `get_current_user`

Dependency que verifica JWT y retorna el usuario actual.

**Uso:**
```python
from backend.auth import get_current_user, CurrentUser

@app.get("/protected")
async def protected_route(current_user: CurrentUser = Depends(get_current_user)):
    return {"user": current_user.username}
```

**Verifica:**
- ✅ Token JWT válido
- ✅ Token no expirado
- ✅ Usuario existe en BD
- ✅ Usuario activo

## 🔒 Middleware RBAC (Autorización)

### `RoleChecker`

Dependency para verificar roles de usuario.

**Roles disponibles:**
- `Admin`: Acceso total
- `Podologo`: Acceso clínico completo
- `Recepcionista`: Gestión de citas y pacientes
- `Asistente`: Acceso limitado

**Uso:**
```python
from backend.auth import require_podologo, CurrentUser

@app.post("/pacientes")
async def crear_paciente(
    current_user: CurrentUser = Depends(require_podologo())
):
    # Solo Admin y Podologo pueden acceder
    pass
```

**Helpers disponibles:**
- `require_admin()`: Solo Admin
- `require_podologo()`: Admin o Podologo
- `require_recepcion()`: Admin, Podologo o Recepcionista
- `require_any_authenticated()`: Cualquier usuario autenticado

**Custom roles:**
```python
from backend.auth import RoleChecker

@app.delete("/usuarios/{id}")
async def delete_user(
    current_user: CurrentUser = Depends(RoleChecker(["Admin"]))
):
    # Solo Admin
    pass
```

## 🚀 Cómo Usar

### 1. Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Crear archivo `.env`:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/podoskin

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
```

### 3. Iniciar servidor

```bash
# Desde el directorio backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

O directamente:

```bash
python -m backend.main
```

### 4. Probar endpoints

Acceder a la documentación interactiva:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📝 Ejemplos de Uso

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dr.santiago",
    "password": "password123"
  }'
```

### Acceder a ruta protegida

```bash
curl http://localhost:8000/protected \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Python Client

```python
import httpx

# Login
response = httpx.post(
    "http://localhost:8000/auth/login",
    json={
        "username": "dr.santiago",
        "password": "password123"
    }
)
token = response.json()["access_token"]

# Acceder a recurso protegido
response = httpx.get(
    "http://localhost:8000/protected",
    headers={"Authorization": f"Bearer {token}"}
)
```

## 🔧 Configuración

### JWT Settings

En `backend/auth/utils.py`:

```python
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
```

### Rate Limiting

En `backend/auth/router.py`:

```python
@limiter.limit("5/minute")  # Ajustar según necesidad
async def login(...):
    pass
```

## 🔐 Seguridad

- ✅ Passwords hasheados con bcrypt
- ✅ JWT con expiration time
- ✅ Rate limiting en login (5/min)
- ✅ Validación de formato de username
- ✅ Usuario debe estar activo
- ✅ Logs de intentos fallidos
- ⚠️ **IMPORTANTE**: Cambiar `JWT_SECRET_KEY` en producción

## 📊 Estructura de BD

El sistema usa la tabla `usuarios`:

```sql
CREATE TABLE usuarios (
    id bigint PRIMARY KEY,
    nombre_usuario text UNIQUE NOT NULL,
    password_hash text NOT NULL,
    nombre_completo text NOT NULL,
    email text UNIQUE NOT NULL,
    rol text NOT NULL CHECK (rol IN ('Admin', 'Podologo', 'Recepcionista', 'Asistente')),
    activo boolean DEFAULT true,
    ultimo_login timestamp,
    fecha_registro timestamp DEFAULT CURRENT_TIMESTAMP
);
```

## 🧪 Testing

Para crear un usuario de prueba:

```sql
-- Password: "password123"
INSERT INTO usuarios (nombre_usuario, password_hash, nombre_completo, email, rol)
VALUES (
    'dr.santiago',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYL3GGvCHYe',
    'Dr. Santiago Ornelas',
    'santiago@podoskin.com',
    'Podologo'
);
```

## 📚 Referencias

- FSD Section 2.1: POST /auth/login specification
- SRS Section 7: Security specifications
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- JWT: https://jwt.io/

## ⚡ Performance

- Connection pooling en database.py (si se migra a pool)
- Rate limiting para prevenir abuso
- Bcrypt rounds optimizados para balance seguridad/performance

## 🐛 Troubleshooting

**Error: "Token inválido o expirado"**
- Verificar que el token no haya expirado (1 hora)
- Verificar formato: `Bearer {token}`

**Error: "Usuario no encontrado"**
- Verificar que el usuario existe en la tabla `usuarios`
- Verificar que `nombre_usuario` coincide exactamente

**Error: "Usuario inactivo"**
- Verificar campo `activo = true` en la BD

**Error: "No tiene permisos para esta acción"**
- Verificar que el rol del usuario está en los roles permitidos
- Admin > Podologo > Recepcionista > Asistente
