# Sistema de Autenticación - Podoskin Solution

## Descripción

Sistema completo de autenticación para el frontend React/TypeScript de Podoskin Solution, integrado con el backend FastAPI.

## Estructura de Archivos

```
Frontend/src/auth/
├── AuthContext.tsx       # Context Provider de autenticación
├── authService.ts        # Servicios de API (login, logout, token management)
├── LoginPage.tsx         # Página de inicio de sesión
├── ProtectedRoute.tsx    # HOC para proteger rutas
└── index.ts             # Exports del módulo
```

## Componentes

### 1. AuthContext (AuthContext.tsx)

Context Provider que maneja el estado global de autenticación:

- **Estado:**
  - `user`: Información del usuario autenticado (User | null)
  - `token`: Token JWT (string | null)
  - `isAuthenticated`: Estado de autenticación (boolean)
  - `isLoading`: Estado de carga (boolean)

- **Métodos:**
  - `login(username, password)`: Inicia sesión
  - `logout()`: Cierra sesión
  - `checkAuth()`: Verifica token almacenado

**Uso:**
```typescript
import { useAuth } from './auth/AuthContext';

const { user, isAuthenticated, login, logout } = useAuth();
```

### 2. authService (authService.ts)

Servicio de API para autenticación:

- `login(credentials)`: POST a /auth/login
- `logout()`: POST a /auth/logout
- `getStoredToken()`: Lee token de localStorage
- `setStoredToken(token)`: Guarda token en localStorage
- `removeStoredToken()`: Elimina token de localStorage

**Manejo de Errores:**
- 401: "Usuario o contraseña incorrectos"
- 403: "No tienes permisos para acceder"
- 429: "Demasiados intentos"
- Otros: Mensaje del backend o error genérico

### 3. LoginPage (LoginPage.tsx)

Página de inicio de sesión con:

- Formulario de login (usuario y contraseña)
- Validación de campos:
  - Username: mínimo 3 caracteres
  - Password: mínimo 8 caracteres
- Estados de carga
- Manejo de errores
- Diseño con Tailwind CSS
- Logo dinámico (DynamicLogo)
- Redirección automática después del login

### 4. ProtectedRoute (ProtectedRoute.tsx)

Higher-Order Component para proteger rutas:

- Verifica autenticación antes de renderizar
- Muestra spinner mientras carga
- Redirige a /login si no está autenticado
- Guarda la ruta intentada para redirigir después del login

**Uso:**
```typescript
<Route element={<ProtectedRoute><Component /></ProtectedRoute>}>
  {/* Rutas protegidas */}
</Route>
```

## Integración en App.tsx

```typescript
import { AuthProvider } from './auth/AuthContext';
import ProtectedRoute from './auth/ProtectedRoute';
import LoginPage from './auth/LoginPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Ruta pública */}
          <Route path="/login" element={<LoginPage />} />

          {/* Rutas protegidas */}
          <Route element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
            <Route path="/calendar" element={<Calendar />} />
            {/* ... más rutas */}
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}
```

## Integración en AppShell.tsx

El componente AppShell ahora muestra:
- Nombre del usuario autenticado
- Rol del usuario
- Avatar con iniciales
- Menú desplegable con:
  - Información del usuario
  - Botón de cerrar sesión

## Variables de Entorno

Archivo `.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENV=development
```

## API Backend

El sistema espera los siguientes endpoints:

### POST /auth/login
**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "rol": "string",
    "nombre_completo": "string"
  }
}
```

### POST /auth/logout
**Headers:**
```
Authorization: Bearer {token}
```

## Flujo de Autenticación

1. **Carga Inicial:**
   - AuthContext verifica si hay token en localStorage
   - Si existe, marca al usuario como autenticado
   - Si no existe, permanece no autenticado

2. **Login:**
   - Usuario ingresa credenciales en LoginPage
   - LoginPage llama a `authService.login()`
   - authService hace POST a /auth/login
   - Si es exitoso:
     - Token se guarda en localStorage
     - User data se guarda en AuthContext
     - Usuario es redirigido a /calendar (o ruta intentada)
   - Si falla:
     - Muestra error en LoginPage

3. **Navegación:**
   - ProtectedRoute verifica autenticación
   - Si autenticado → renderiza componente
   - Si no autenticado → redirige a /login

4. **Logout:**
   - Usuario hace clic en "Cerrar Sesión"
   - AppShell llama a `logout()`
   - authService hace POST a /auth/logout
   - Token se elimina de localStorage
   - Usuario es redirigido a /login

## Seguridad

- Token almacenado en localStorage (clave: 'token')
- Token enviado en header Authorization: Bearer {token}
- Rutas protegidas por ProtectedRoute
- Validación de campos en cliente
- Manejo de errores del backend (401, 403, 429)

## Testing

Para probar el sistema:

1. Iniciar el backend:
```bash
cd Backend
uvicorn main:app --reload
```

2. Iniciar el frontend:
```bash
cd Frontend
npm run dev
```

3. Navegar a http://localhost:5173
4. Intentar acceder a una ruta protegida → redirige a /login
5. Ingresar credenciales válidas
6. Verificar redirección a la aplicación
7. Verificar que el nombre del usuario aparece en el header
8. Probar logout

## Credenciales de Prueba

(Estas deben ser configuradas en el backend)

Ejemplo:
- Usuario: `admin`
- Contraseña: `admin123456`

## Próximos Pasos

1. ✅ Estructura base de autenticación
2. ✅ Integración con App.tsx y AppShell
3. ⏳ Validación de token con el backend
4. ⏳ Refresh token automático
5. ⏳ Persistencia de sesión mejorada
6. ⏳ Recuperación de contraseña
7. ⏳ Registro de usuarios

## Notas de Desarrollo

- El sistema usa axios para peticiones HTTP
- Los tipos TypeScript están completamente tipados
- El diseño usa Tailwind CSS para consistencia
- El logo usa el componente DynamicLogo existente
- Compatible con el sistema de rutas de React Router v6

## Troubleshooting

### Error: "Cannot read property 'user' of undefined"
- Asegúrate de que el componente está dentro de `<AuthProvider>`

### Token no persiste después de recargar
- Verifica que localStorage esté habilitado en el navegador
- Verifica que el token se guarda correctamente en authService

### Redirección infinita a /login
- Verifica que el token sea válido
- Revisa la lógica de checkAuth() en AuthContext

### Errores CORS
- Configura CORS en el backend para permitir el origen del frontend
- Verifica que VITE_API_URL esté configurado correctamente
