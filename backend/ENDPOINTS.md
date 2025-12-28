# 📋 Endpoints Creados - Sistema de Autenticación

Este documento lista todos los endpoints REST creados para el módulo de autenticación de Podoskin Solution.

---

## 🔑 Endpoints de Autenticación

### 1. POST /auth/login

**Descripción**: Autentica un usuario con username y password, retorna JWT token.

**URL**: `http://localhost:8000/auth/login`

**Método**: `POST`

**Headers**:
```
Content-Type: application/json
```

**Body**:
```json
{
  "username": "dr.santiago",
  "password": "password123"
}
```

**Respuestas**:

#### ✅ 200 OK - Login exitoso
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

#### ❌ 401 Unauthorized - Credenciales incorrectas
```json
{
  "detail": "Credenciales incorrectas"
}
```

#### ❌ 403 Forbidden - Usuario inactivo
```json
{
  "detail": "Usuario inactivo"
}
```

#### ❌ 422 Unprocessable Entity - Error de validación
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### ❌ 429 Too Many Requests - Rate limit excedido
```json
{
  "detail": "Demasiados intentos. Espere antes de reintentar"
}
```

**Rate Limiting**: Máximo 5 intentos por minuto por usuario.

**Flujo Interno**:
1. Valida formato de credenciales
2. Verifica rate limit (5 intentos/minuto)
3. Busca usuario en base de datos por username
4. Verifica contraseña con bcrypt
5. Verifica que usuario esté activo
6. Genera JWT token (expira en 1 hora)
7. Actualiza timestamp de último acceso
8. Retorna token + datos de usuario

---

### 2. POST /auth/logout

**Descripción**: Endpoint de logout (placeholder para JWT stateless).

**URL**: `http://localhost:8000/auth/logout`

**Método**: `POST`

**Respuesta**:

#### ✅ 200 OK
```json
{
  "message": "Sesión cerrada exitosamente"
}
```

**Nota**: Con JWT stateless, el logout se maneja en el cliente eliminando el token. Este endpoint puede usarse para registrar el evento o implementar blacklist de tokens en el futuro.

---

### 3. GET /auth/health

**Descripción**: Health check del servicio de autenticación.

**URL**: `http://localhost:8000/auth/health`

**Método**: `GET`

**Respuesta**:

#### ✅ 200 OK
```json
{
  "status": "healthy",
  "service": "auth",
  "version": "1.0.0"
}
```

---

## 🛡️ Endpoints Protegidos (Ejemplos)

### 4. GET /protected

**Descripción**: Ejemplo de endpoint que requiere autenticación.

**URL**: `http://localhost:8000/protected`

**Método**: `GET`

**Headers**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Respuesta**:

#### ✅ 200 OK - Token válido
```json
{
  "message": "Hola Dr. Santiago Ornelas",
  "user_id": 1,
  "username": "dr.santiago",
  "rol": "Podologo"
}
```

#### ❌ 401 Unauthorized - Token inválido/expirado
```json
{
  "detail": "Token inválido o expirado"
}
```

#### ❌ 403 Forbidden - Usuario inactivo
```json
{
  "detail": "Usuario inactivo"
}
```

---

### 5. GET /admin-only

**Descripción**: Endpoint que solo puede acceder un administrador.

**URL**: `http://localhost:8000/admin-only`

**Método**: `GET`

**Headers**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Respuesta**:

#### ✅ 200 OK - Usuario es Admin
```json
{
  "message": "Acceso permitido solo para administradores",
  "admin": "Nombre del Admin"
}
```

#### ❌ 403 Forbidden - Usuario no es Admin
```json
{
  "detail": "No tiene permisos para esta acción. Roles requeridos: Admin"
}
```

---

### 6. POST /staff-action

**Descripción**: Endpoint para staff (Admin, Podologo, Recepcionista).

**URL**: `http://localhost:8000/staff-action`

**Método**: `POST`

**Headers**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Respuesta**:

#### ✅ 200 OK - Usuario tiene rol permitido
```json
{
  "message": "Acción de staff ejecutada",
  "user": "Dr. Santiago Ornelas",
  "rol": "Podologo"
}
```

#### ❌ 403 Forbidden - Usuario no tiene rol permitido
```json
{
  "detail": "No tiene permisos para esta acción. Roles requeridos: Admin, Podologo, Recepcionista"
}
```

---

## 🔐 Seguridad

### JWT Token Structure

Los tokens JWT generados incluyen:

```json
{
  "sub": "dr.santiago",       // Username
  "rol": "Podologo",           // Rol del usuario
  "exp": 1735689600,           // Timestamp de expiración
  "iat": 1735686000            // Timestamp de emisión
}
```

### Algoritmo

- **Algoritmo**: HS256 (HMAC with SHA-256)
- **Duración**: 3600 segundos (1 hora)
- **Secret Key**: Configurable via `JWT_SECRET_KEY` en `.env`

### Password Hashing

- **Algoritmo**: bcrypt
- **Rounds**: 12 (por defecto)
- **Salt**: Generado automáticamente

---

## 📊 Roles Soportados

| Rol | Descripción |
|-----|-------------|
| `Admin` | Administrador con acceso total |
| `Podologo` | Podólogo que puede realizar acciones médicas |
| `Recepcionista` | Personal de recepción con acceso limitado |
| `Asistente` | Asistente con acceso básico |

---

## 🧪 Ejemplos de Uso

### Con cURL

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"dr.santiago","password":"password123"}'

# Guardar token
TOKEN="eyJhbGciOiJIUzI1NiIs..."

# Usar token
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
print(f"Token: {token}")
print(f"Usuario: {data['user']['nombre_completo']}")

# Usar token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/protected",
    headers=headers
)

print(response.json())
```

### Con JavaScript (fetch)

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'dr.santiago',
    password: 'password123'
  })
});

const { access_token, user } = await loginResponse.json();
console.log('Token:', access_token);
console.log('Usuario:', user.nombre_completo);

// Usar token
const protectedResponse = await fetch('http://localhost:8000/protected', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});

const data = await protectedResponse.json();
console.log(data);
```

---

## 📖 Documentación Interactiva

FastAPI genera automáticamente documentación interactiva:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Desde allí puedes:
- ✅ Ver todos los endpoints disponibles
- ✅ Probar los endpoints directamente
- ✅ Ver los esquemas de request/response
- ✅ Autenticarte y probar endpoints protegidos

---

## 🔗 Referencias

- [README del módulo auth](./auth/README.md)
- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Especificación JWT (RFC 7519)](https://tools.ietf.org/html/rfc7519)
- [Bcrypt](https://en.wikipedia.org/wiki/Bcrypt)

---

**Desarrollado para**: Podoskin Solution  
**Módulo**: Autenticación REST con JWT y RBAC  
**Versión**: 1.0.0  
**Fecha**: Diciembre 2024
