# Lista de Endpoints Creados - Backend Authentication

## ✅ Endpoints REST Implementados

### 1. POST /auth/login
**Descripción**: Endpoint REST para autenticación de usuarios que valida credenciales y retorna JWT token.

**URL**: `POST /auth/login`

**Request Body**:
```json
{
  "username": "dr.santiago",
  "password": "password123"
}
```

**Response 200** (Éxito):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
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

**Response 401** (Credenciales incorrectas):
```json
{
  "detail": "Credenciales incorrectas"
}
```

**Response 403** (Usuario inactivo):
```json
{
  "detail": "Usuario inactivo"
}
```

**Response 429** (Rate limit excedido):
```json
{
  "detail": "Too Many Requests"
}
```

**Características**:
- ✅ Validación de credenciales con bcrypt
- ✅ Generación de JWT con expiration de 1 hora
- ✅ Rate limiting: 5 intentos por minuto por IP
- ✅ Actualización de `ultimo_login` en BD
- ✅ Verificación de usuario activo
- ✅ Logging de intentos fallidos

---

### 2. GET /auth/test
**Descripción**: Endpoint de prueba para verificar que el router de autenticación funciona.

**URL**: `GET /auth/test`

**Response 200**:
```json
{
  "status": "ok",
  "message": "Auth router is working",
  "endpoints": [
    "POST /auth/login - Login de usuario"
  ]
}
```

---

## 🛡️ Middleware de Autenticación

### get_current_user
**Descripción**: Dependency que verifica JWT token y retorna el usuario actual autenticado.

**Uso en endpoints**:
```python
from backend.auth import get_current_user, CurrentUser

@app.get("/protected")
async def protected_route(current_user: CurrentUser = Depends(get_current_user)):
    return {"user": current_user.username}
```

**Verificaciones**:
- ✅ Token JWT válido y no expirado
- ✅ Usuario existe en base de datos
- ✅ Usuario está activo (campo `activo = true`)

**Excepciones**:
- `401 Unauthorized`: Token inválido, expirado o usuario no encontrado
- `403 Forbidden`: Usuario inactivo

---

## 🔒 Middleware RBAC (Autorización por Roles)

### RoleChecker
**Descripción**: Middleware para verificar roles de usuario (Role-Based Access Control).

**Roles disponibles**:
- `Admin`: Acceso total al sistema
- `Podologo`: Acceso clínico completo
- `Recepcionista`: Gestión de citas y pacientes
- `Asistente`: Acceso limitado

### Helpers de Autorización

#### 1. require_admin()
**Descripción**: Solo permite acceso a usuarios con rol "Admin".

**Uso**:
```python
@app.delete("/usuarios/{id}")
async def delete_user(current_user: CurrentUser = Depends(require_admin())):
    # Solo Admin puede eliminar usuarios
    pass
```

#### 2. require_podologo()
**Descripción**: Permite acceso a usuarios con rol "Admin" o "Podologo".

**Uso**:
```python
@app.get("/pacientes")
async def get_pacientes(current_user: CurrentUser = Depends(require_podologo())):
    # Admin y Podologo pueden ver pacientes
    pass
```

#### 3. require_recepcion()
**Descripción**: Permite acceso a usuarios con rol "Admin", "Podologo" o "Recepcionista".

**Uso**:
```python
@app.post("/citas")
async def crear_cita(current_user: CurrentUser = Depends(require_recepcion())):
    # Admin, Podologo y Recepcionista pueden crear citas
    pass
```

#### 4. require_any_authenticated()
**Descripción**: Permite acceso a cualquier usuario autenticado (cualquier rol).

**Uso**:
```python
@app.get("/dashboard")
async def dashboard(current_user: CurrentUser = Depends(require_any_authenticated())):
    # Cualquier usuario autenticado puede acceder
    pass
```

#### 5. RoleChecker (Custom)
**Descripción**: Permite especificar roles personalizados.

**Uso**:
```python
@app.get("/special")
async def special_route(
    current_user: CurrentUser = Depends(RoleChecker(["Admin", "Podologo"]))
):
    # Solo Admin y Podologo pueden acceder
    pass
```

---

## 📦 Modelos Pydantic

### 1. LoginRequest
```python
{
  "username": "string (3-50 chars, alphanumeric + _)",
  "password": "string (8-100 chars)"
}
```

### 2. LoginResponse
```python
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": UserResponse
}
```

### 3. UserResponse
```python
{
  "id": int,
  "username": "string",
  "email": "string",
  "rol": "string",
  "nombre_completo": "string"
}
```

### 4. CurrentUser
```python
{
  "id": int,
  "username": "string",
  "email": "string",
  "rol": "string",
  "nombre_completo": "string",
  "activo": bool
}
```

### 5. TokenPayload
```python
{
  "sub": "string (username)",
  "rol": "string",
  "exp": int (expiration timestamp),
  "iat": int (issued at timestamp)
}
```

---

## 🚀 Ejemplo de Flujo Completo

### 1. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dr.santiago",
    "password": "password123"
  }'
```

**Respuesta**:
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

### 2. Acceder a Ruta Protegida
```bash
curl http://localhost:8000/protected \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

### 3. Acceder a Ruta con Rol Específico
```bash
curl http://localhost:8000/podologo/pacientes \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

---

## 🔐 Seguridad Implementada

✅ **Password Hashing**: Bcrypt con salt automático
✅ **JWT Tokens**: HS256 con expiration (1 hora)
✅ **Rate Limiting**: 5 intentos/minuto en login
✅ **Input Validation**: Pydantic validators
✅ **User Active Check**: Verificación de usuario activo
✅ **Logging**: Logs de seguridad
✅ **RBAC**: Control de acceso por roles

---

## 📝 Notas Importantes

1. **JWT Secret Key**: En producción, cambiar la variable de entorno `JWT_SECRET_KEY`
2. **Database Connection**: Configurar `DATABASE_URL` en .env
3. **Token Expiration**: Los tokens expiran en 1 hora (3600 segundos)
4. **Rate Limiting**: Limitar a 5 intentos de login por minuto por IP
5. **CORS**: En producción, configurar orígenes permitidos específicos

---

## 📚 Archivos de Documentación

- `backend/auth/README.md` - Documentación completa del módulo
- `backend/AUTHENTICATION_SUMMARY.md` - Resumen de implementación
- `backend/example_usage.py` - Ejemplos de código
- `backend/test_auth.py` - Suite de tests

---

## 🎯 Conformidad con Especificaciones

✅ **FSD Section 2.1**: POST /auth/login implementado según especificación
✅ **SRS Section 7**: Todos los requisitos de seguridad implementados
✅ **JWT Structure**: Estructura de token conforme a especificación
✅ **RBAC Middleware**: Middleware de autorización implementado
✅ **Rate Limiting**: Implementado según especificación
✅ **Pydantic Models**: Todos los modelos implementados
