# Sistema de Autenticación - Podoskin Solution

## 📋 Descripción

Sistema completo y mejorado de autenticación para el frontend React/TypeScript de Podoskin Solution, integrado con el backend FastAPI. Incluye funcionalidades avanzadas como recuperación de contraseña, RBAC (Role-Based Access Control), auto-refresh de tokens, y una UI/UX mejorada.

## 🏗️ Estructura de Archivos

```
Frontend/src/auth/
├── AuthContext.tsx              # Context Provider con auto-refresh y gestión de sesión
├── authService.ts               # Servicios de API (login, logout, password recovery, etc.)
├── LoginPage.tsx                # Página de inicio de sesión mejorada
├── RecoverPasswordPage.tsx      # Página para solicitar recuperación de contraseña
├── ResetPasswordPage.tsx        # Página para restablecer contraseña con token
├── ChangePasswordModal.tsx      # Modal para cambiar contraseña (usuario autenticado)
├── ProtectedRoute.tsx           # HOC para proteger rutas
├── RoleGuard.tsx                # Componente para restricciones por rol (RBAC)
├── hooks/
│   └── useAuthGuard.ts         # Hook personalizado para verificar acceso por rol
└── index.ts                     # Exports del módulo
```

## 🎯 Características Principales

### AuthContext (AuthContext.tsx)

**Mejoras implementadas:**
- ✅ Auto-refresh de token cada 25 minutos (token expira en 30)
- ✅ Función `refreshToken()` para renovar token manualmente
- ✅ Función `updateUser()` para actualizar datos del usuario
- ✅ Event listener `beforeunload` para persistir estado
- ✅ Logging detallado de eventos de autenticación
- ✅ Verificación de token al cargar la aplicación

**Estado gestionado:**
- `user`: Información del usuario autenticado (User | null)
- `token`: Token JWT (string | null)
- `isAuthenticated`: Estado de autenticación (boolean)
- `isLoading`: Estado de carga (boolean)

**Métodos disponibles:**
```typescript
interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string, rememberMe?: boolean) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => void;
  refreshToken: () => Promise<void>;
  updateUser: (userData: Partial<User>) => void;
}
```

**Ejemplo de uso:**
```typescript
import { useAuth } from './auth/AuthContext';

const MyComponent = () => {
  const { user, isAuthenticated, login, logout, updateUser } = useAuth();

  // Actualizar datos del usuario
  const handleUpdateProfile = () => {
    updateUser({ nombre_completo: 'Nuevo Nombre' });
  };

  return (
    <div>
      {isAuthenticated ? (
        <>
          <p>Bienvenido, {user?.nombre_completo}</p>
          <button onClick={logout}>Cerrar Sesión</button>
        </>
      ) : (
        <p>No autenticado</p>
      )}
    </div>
  );
};
```

### LoginPage (LoginPage.tsx)

**Nuevas características:**
- ✅ Checkbox "Recordar sesión" para persistir login
- ✅ Link "¿Olvidaste tu contraseña?" que redirige a recuperación
- ✅ Mostrar/ocultar contraseña con icono de ojo
- ✅ CAPTCHA matemático simple después de 3 intentos fallidos
- ✅ Feedback visual en campos (verde=válido, rojo=error)
- ✅ Animaciones de entrada (fadeIn + slideUp)
- ✅ Animación shake en mensajes de error
- ✅ ARIA labels para accesibilidad
- ✅ Loading state con spinner animado
- ✅ Transiciones suaves en todos los elementos

**Validaciones:**
- Username: mínimo 3 caracteres
- Password: mínimo 8 caracteres
- CAPTCHA: respuesta matemática correcta (si aplica)

### authService (authService.ts)

**Funciones disponibles:**

```typescript
// Login
login(credentials: LoginCredentials): Promise<LoginResponse>

// Logout
logout(): Promise<void>

// Refresh token
refreshToken(): Promise<LoginResponse>

// Verify token
verifyToken(): Promise<boolean>

// Solicitar recuperación de contraseña
requestPasswordReset(email: string): Promise<{ message: string }>

// Restablecer contraseña con token
resetPassword(token: string, newPassword: string): Promise<{ message: string }>

// Cambiar contraseña (usuario autenticado)
changePassword(currentPassword: string, newPassword: string): Promise<{ message: string }>

// Token management
getStoredToken(): string | null
setStoredToken(token: string): void
removeStoredToken(): void
```

**Manejo de errores mejorado:**
- 401: "Usuario o contraseña incorrectos" / "Contraseña actual incorrecta"
- 403: "No tienes permisos para acceder"
- 422: "La contraseña no cumple con los requisitos mínimos"
- 429: "Demasiados intentos"
- 400: "Token inválido o expirado"
- Otros: Mensaje del backend o error genérico

### RecoverPasswordPage (RecoverPasswordPage.tsx)

Página para solicitar recuperación de contraseña.

**Flujo:**
1. Usuario ingresa su email
2. POST a `/auth/request-password-reset`
3. Muestra mensaje de confirmación
4. Usuario recibe email con link que contiene token
5. Link redirige a `/auth/reset-password?token=xxx`

**Características:**
- Validación de formato de email
- Animaciones de transición entre estados
- Mensaje de éxito con instrucciones claras
- Link para volver al login

**Ejemplo de uso:**
```typescript
// En App.tsx
<Route path="/auth/recover-password" element={<RecoverPasswordPage />} />
```

### ResetPasswordPage (ResetPasswordPage.tsx)

Página para restablecer contraseña usando el token recibido por email.

**Flujo:**
1. Usuario hace clic en link del email
2. Página lee token de URL query params
3. Usuario ingresa nueva contraseña y confirmación
4. POST a `/auth/reset-password` con token y nueva contraseña
5. Muestra mensaje de éxito y redirige a login

**Validaciones:**
- Token presente en URL
- Nueva contraseña mínimo 8 caracteres
- Debe contener mayúsculas, minúsculas y números
- Confirmación debe coincidir con nueva contraseña

**Características:**
- Mostrar/ocultar contraseñas
- Indicadores visuales de requisitos de seguridad
- Manejo de token inválido o expirado
- Redirección automática después de 3 segundos

**Ejemplo de uso:**
```typescript
// En App.tsx
<Route path="/auth/reset-password" element={<ResetPasswordPage />} />
```

### ChangePasswordModal (ChangePasswordModal.tsx)

Modal para que un usuario autenticado cambie su contraseña.

**Validaciones:**
- Contraseña actual correcta
- Nueva contraseña mínimo 8 caracteres
- Debe contener mayúsculas, minúsculas y números
- Nueva contraseña diferente a la actual
- Confirmación debe coincidir

**Características:**
- Modal con overlay oscuro
- Click fuera del modal para cerrar
- Mostrar/ocultar todas las contraseñas
- Indicadores visuales de requisitos
- Cierre automático después de éxito

**Ejemplo de uso:**
```typescript
import { ChangePasswordModal } from './auth';

const ProfilePage = () => {
  const [showModal, setShowModal] = useState(false);

  return (
    <div>
      <button onClick={() => setShowModal(true)}>
        Cambiar contraseña
      </button>
      
      <ChangePasswordModal 
        isOpen={showModal} 
        onClose={() => setShowModal(false)} 
      />
    </div>
  );
};
```

### RoleGuard (RoleGuard.tsx)

Componente para restricciones por rol (RBAC).

**Props:**
- `allowedRoles`: Array de roles que tienen acceso
- `children`: Contenido a renderizar si tiene acceso
- `fallback`: (Opcional) Componente a renderizar si no tiene acceso
- `redirectTo`: (Opcional) Ruta a la que redirigir si no tiene acceso

**Ejemplo de uso:**
```typescript
import { RoleGuard } from './auth';

// Solo Admin y Podologo pueden ver este componente
<RoleGuard allowedRoles={['Admin', 'Podologo']}>
  <AdminPanel />
</RoleGuard>

// Con fallback personalizado
<RoleGuard 
  allowedRoles={['Admin']} 
  fallback={<div>Solo administradores</div>}
>
  <SuperSecretContent />
</RoleGuard>
```

### useAuthGuard Hook (hooks/useAuthGuard.ts)

Hook personalizado para verificar acceso por rol programáticamente.

**Parámetros:**
- `requiredRoles`: (Opcional) Array de roles requeridos. Si no se proporciona, solo verifica autenticación.

**Retorna:**
```typescript
{
  hasAccess: boolean;    // Si el usuario tiene acceso
  user: User | null;     // Datos del usuario
  isAuthenticated: boolean; // Si está autenticado
}
```

**Ejemplo de uso:**
```typescript
import { useAuthGuard } from './auth/hooks/useAuthGuard';

const AdminComponent = () => {
  const { hasAccess, user } = useAuthGuard(['Admin', 'Podologo']);

  if (!hasAccess) {
    return <div>No tienes permisos para ver esto</div>;
  }

  return (
    <div>
      <h1>Panel de Administración</h1>
      <p>Bienvenido, {user?.nombre_completo}</p>
    </div>
  );
};
```

## 🔐 Seguridad

### Token JWT
- Almacenado en `localStorage` con clave `token`
- Enviado en header `Authorization: Bearer {token}`
- Expira en 30 minutos (configurado en backend)
- Auto-refresh cada 25 minutos para sesiones activas
- Validación de token al cargar aplicación

### Password Requirements
- Mínimo 8 caracteres
- Al menos una letra mayúscula
- Al menos una letra minúscula
- Al menos un número
- No puede ser igual a la contraseña anterior

### Rate Limiting
- Backend limita intentos de login (5 por minuto)
- Frontend muestra CAPTCHA después de 3 intentos fallidos

### RBAC (Role-Based Access Control)
- Roles definidos en backend: Admin, Podologo, Recepcionista, Paciente
- Frontend verifica roles con RoleGuard y useAuthGuard
- Contenido sensible protegido por rol

## 🎨 UI/UX

### Animaciones
- **fadeIn**: Aparición suave de elementos (0.3s)
- **slideUp**: Deslizamiento desde abajo (0.3s)
- **shake**: Vibración de errores (0.5s)
- **spin**: Loading spinner
- **hover:scale**: Efecto hover en botones

### Accesibilidad
- ARIA labels en todos los inputs
- ARIA roles en alertas y modales
- Navegación por teclado
- Focus indicators visibles
- Error messages con aria-live="assertive"

### Feedback Visual
- ✅ Verde: Campo válido
- ❌ Rojo: Campo con error
- 🔵 Azul: Información
- ⚪ Gris: Estado neutral
- Loading states en todos los botones

## 🚀 Integración en App.tsx

```typescript
import { AuthProvider } from './auth/AuthContext';
import { 
  ProtectedRoute, 
  LoginPage, 
  RecoverPasswordPage, 
  ResetPasswordPage 
} from './auth';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Rutas públicas */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/recover-password" element={<RecoverPasswordPage />} />
          <Route path="/auth/reset-password" element={<ResetPasswordPage />} />

          {/* Rutas protegidas */}
          <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
            <Route path="/calendar" element={<Calendar />} />
            <Route path="/medical" element={<MedicalAttention />} />
            {/* ... más rutas */}
          </Route>

          <Route path="/" element={<Navigate to="/calendar" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
```

## 🌐 API Backend

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
  "expires_in": 1800,
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
**Headers:** `Authorization: Bearer {token}`

**Response:** `{ "message": "Sesión cerrada exitosamente" }`

### POST /auth/refresh
**Headers:** `Authorization: Bearer {token}`

**Response:** Mismo formato que login

### GET /auth/verify
**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK` si token válido, `401` si inválido

### POST /auth/request-password-reset
**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Si el email existe, recibirás instrucciones"
}
```

### POST /auth/reset-password
**Request:**
```json
{
  "token": "string",
  "new_password": "string"
}
```

**Response:**
```json
{
  "message": "Contraseña restablecida exitosamente"
}
```

### POST /auth/change-password
**Headers:** `Authorization: Bearer {token}`

**Request:**
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

**Response:**
```json
{
  "message": "Contraseña cambiada exitosamente"
}
```

## 🔄 Flujo de Autenticación

### 1. Login
```
Usuario → LoginPage → authService.login() → Backend /auth/login
       ← Token + User ← Response
       → localStorage.setItem('token', token)
       → AuthContext.setUser(user)
       → Navigate to /calendar
```

### 2. Auto-Refresh (cada 25 minutos)
```
AuthContext → setTimeout(25 min) → refreshToken()
           → POST /auth/refresh
           ← New Token
           → Update localStorage
           → Setup next refresh
```

### 3. Protected Route Access
```
User navigates → ProtectedRoute → useAuth()
              → isAuthenticated? 
              → Yes: Render component
              → No: Navigate to /login (save attempted route)
```

### 4. Password Recovery
```
User → RecoverPasswordPage → Enter email
    → POST /auth/request-password-reset
    → Success message
    
Email → User clicks link
     → ResetPasswordPage (with token in URL)
     → Enter new password
     → POST /auth/reset-password
     → Success → Redirect to /login
```

### 5. Change Password (Authenticated)
```
User → Opens ChangePasswordModal
    → Enters current + new password
    → POST /auth/change-password (with token in header)
    → Success → Modal closes
```

## 📝 Variables de Entorno

Archivo `.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENV=development
```

## 🧪 Testing

Para probar el sistema:

1. **Iniciar el backend:**
```bash
cd backend
uvicorn main:app --reload
```

2. **Iniciar el frontend:**
```bash
cd Frontend
npm run dev
```

3. **Flujo de pruebas:**
   - [ ] Intentar acceder a ruta protegida sin login → Redirige a /login
   - [ ] Login con credenciales incorrectas → Muestra error
   - [ ] Login con credenciales correctas → Redirige a /calendar
   - [ ] Verificar nombre de usuario en header
   - [ ] Intentar 3 logins fallidos → Muestra CAPTCHA
   - [ ] Probar "Recordar sesión" → Persiste después de cerrar navegador
   - [ ] Click en "Olvidé contraseña" → Redirige a RecoverPasswordPage
   - [ ] Enviar email de recuperación → Mensaje de éxito
   - [ ] Usar link con token → ResetPasswordPage
   - [ ] Restablecer contraseña → Redirige a login
   - [ ] Login con nueva contraseña → Exitoso
   - [ ] Abrir modal de cambio de contraseña → ChangePasswordModal
   - [ ] Cambiar contraseña → Modal cierra con éxito
   - [ ] Esperar 25 minutos → Token se refresca automáticamente
   - [ ] Probar RoleGuard con rol no permitido → Muestra mensaje de acceso denegado
   - [ ] Logout → Redirige a /login

## 🐛 Troubleshooting

### Error: "Cannot read property 'user' of undefined"
**Solución:** Asegúrate de que el componente está dentro de `<AuthProvider>`

### Token no persiste después de recargar
**Solución:** 
- Verifica que localStorage esté habilitado
- Revisa la consola del navegador para errores
- Verifica que `getStoredToken()` retorna el token correctamente

### Redirección infinita a /login
**Solución:**
- Verifica que el token sea válido
- Revisa la función `verifyToken()` en authService
- Chequea la implementación de `checkAuth()` en AuthContext

### CAPTCHA no aparece después de 3 intentos
**Solución:**
- Verifica el estado `failedAttempts` en LoginPage
- Asegúrate de que `setFailedAttempts` se incrementa en el catch del login

### Auto-refresh no funciona
**Solución:**
- Verifica que el backend tenga el endpoint `/auth/refresh`
- Revisa los logs de la consola para errores
- Asegúrate de que `setupAutoRefresh()` se llama después del login

### Errores CORS
**Solución:**
- Configura CORS en el backend para permitir el origen del frontend
- Verifica que `VITE_API_URL` esté configurado correctamente
- En desarrollo, usa proxy en vite.config.ts

## 📊 Resumen de Cambios

### ✅ Componentes Mejorados
- **AuthContext**: Auto-refresh, updateUser, logging, beforeunload
- **LoginPage**: Remember me, forgot password, CAPTCHA, show/hide password, animaciones, ARIA
- **authService**: refreshToken, verifyToken, password recovery functions

### ✅ Componentes Nuevos
- **RecoverPasswordPage**: Solicitar recuperación de contraseña
- **ResetPasswordPage**: Restablecer contraseña con token
- **ChangePasswordModal**: Modal para cambiar contraseña
- **RoleGuard**: RBAC component
- **useAuthGuard**: Custom hook para RBAC

### ✅ Mejoras de UI/UX
- Animaciones: fadeIn, slideUp, shake
- Feedback visual en campos (verde/rojo)
- Transiciones suaves
- Loading states
- ARIA labels y accesibilidad

### ✅ Seguridad
- Auto-refresh de tokens
- Validación de token al cargar
- Password strength requirements
- CAPTCHA después de intentos fallidos
- RBAC implementation

## 🎓 Ejemplos de Uso

### Ejemplo 1: Proteger una página por rol
```typescript
import { RoleGuard } from './auth';

const AdminPage = () => (
  <RoleGuard allowedRoles={['Admin']}>
    <div>
      <h1>Panel de Administración</h1>
      <p>Solo administradores pueden ver esto</p>
    </div>
  </RoleGuard>
);
```

### Ejemplo 2: Verificar acceso programáticamente
```typescript
import { useAuthGuard } from './auth/hooks/useAuthGuard';

const Dashboard = () => {
  const { hasAccess, user } = useAuthGuard(['Admin', 'Podologo']);

  const handleAdminAction = () => {
    if (!hasAccess) {
      alert('No tienes permisos');
      return;
    }
    // Ejecutar acción de admin
  };

  return (
    <div>
      <h1>Dashboard</h1>
      <button onClick={handleAdminAction}>
        Acción de Admin
      </button>
    </div>
  );
};
```

### Ejemplo 3: Actualizar perfil de usuario
```typescript
import { useAuth } from './auth';

const ProfilePage = () => {
  const { user, updateUser } = useAuth();
  const [name, setName] = useState(user?.nombre_completo || '');

  const handleSave = () => {
    updateUser({ nombre_completo: name });
    alert('Perfil actualizado');
  };

  return (
    <div>
      <input 
        value={name} 
        onChange={(e) => setName(e.target.value)} 
      />
      <button onClick={handleSave}>Guardar</button>
    </div>
  );
};
```

## 📞 Soporte

Para más información o ayuda:
- Revisa los comentarios en el código
- Consulta la documentación del backend
- Verifica los logs de la consola del navegador
- Usa las herramientas de desarrollo de React

---

**© 2024 Podoskin Solution. Powered by Cognita IA.**
