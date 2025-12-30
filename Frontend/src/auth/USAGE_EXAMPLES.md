# 📘 Ejemplos de Uso - Sistema de Autenticación

Este documento proporciona ejemplos prácticos de cómo usar cada componente y hook del sistema de autenticación.

---

## 1. useAuth Hook

### Ejemplo Básico
```typescript
import { useAuth } from './auth';

function Header() {
  const { user, isAuthenticated, logout } = useAuth();

  if (!isAuthenticated) {
    return <div>No autenticado</div>;
  }

  return (
    <div className="header">
      <span>Bienvenido, {user?.nombre_completo}</span>
      <span>Rol: {user?.rol}</span>
      <button onClick={logout}>Cerrar Sesión</button>
    </div>
  );
}
```

### Actualizar Usuario
```typescript
import { useAuth } from './auth';

function ProfileEditor() {
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
}
```

### Refresh Token Manual
```typescript
import { useAuth } from './auth';

function TokenRefreshButton() {
  const { refreshToken } = useAuth();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await refreshToken();
      alert('Token renovado exitosamente');
    } catch (error) {
      alert('Error al renovar token');
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <button onClick={handleRefresh} disabled={isRefreshing}>
      {isRefreshing ? 'Renovando...' : 'Renovar Token'}
    </button>
  );
}
```

---

## 2. ProtectedRoute Component

### Proteger Rutas Individuales
```typescript
import { ProtectedRoute } from './auth';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
      </Routes>
    </Router>
  );
}
```

### Proteger Grupo de Rutas
```typescript
import { ProtectedRoute } from './auth';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        {/* Todas estas rutas están protegidas */}
        <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </Router>
  );
}
```

---

## 3. RoleGuard Component

### Restringir por Rol Único
```typescript
import { RoleGuard } from './auth';

function AdminPanel() {
  return (
    <RoleGuard allowedRoles={['Admin']}>
      <div>
        <h1>Panel de Administración</h1>
        <p>Solo administradores pueden ver esto</p>
        <button>Eliminar Usuario</button>
        <button>Modificar Permisos</button>
      </div>
    </RoleGuard>
  );
}
```

### Restringir por Múltiples Roles
```typescript
import { RoleGuard } from './auth';

function MedicalRecords() {
  return (
    <RoleGuard allowedRoles={['Admin', 'Podologo', 'Recepcionista']}>
      <div>
        <h1>Expedientes Médicos</h1>
        <PatientList />
      </div>
    </RoleGuard>
  );
}
```

### Con Fallback Personalizado
```typescript
import { RoleGuard } from './auth';

function PremiumFeature() {
  return (
    <RoleGuard 
      allowedRoles={['Admin', 'Premium']}
      fallback={
        <div className="upgrade-message">
          <h2>Función Premium</h2>
          <p>Actualiza tu cuenta para acceder</p>
          <button>Actualizar Ahora</button>
        </div>
      }
    >
      <PremiumContent />
    </RoleGuard>
  );
}
```

---

## 4. useAuthGuard Hook

### Verificar Acceso Programáticamente
```typescript
import { useAuthGuard } from './auth/hooks/useAuthGuard';

function AdminButton() {
  const { hasAccess } = useAuthGuard(['Admin']);

  const handleClick = () => {
    if (!hasAccess) {
      alert('No tienes permisos de administrador');
      return;
    }
    
    // Ejecutar acción de admin
    deleteUser();
  };

  return (
    <button 
      onClick={handleClick}
      className={hasAccess ? 'btn-danger' : 'btn-disabled'}
      disabled={!hasAccess}
    >
      Eliminar Usuario
    </button>
  );
}
```

### Mostrar/Ocultar Elementos Condicionalmente
```typescript
import { useAuthGuard } from './auth/hooks/useAuthGuard';

function Toolbar() {
  const { hasAccess: canEdit } = useAuthGuard(['Admin', 'Podologo']);
  const { hasAccess: canDelete } = useAuthGuard(['Admin']);

  return (
    <div className="toolbar">
      <button>Ver</button>
      
      {canEdit && <button>Editar</button>}
      
      {canDelete && <button>Eliminar</button>}
    </div>
  );
}
```

### Diferentes Acciones por Rol
```typescript
import { useAuthGuard } from './auth/hooks/useAuthGuard';

function PatientCard({ patient }) {
  const { hasAccess: isAdmin } = useAuthGuard(['Admin']);
  const { hasAccess: isDoctor } = useAuthGuard(['Podologo']);
  const { hasAccess: isReceptionist } = useAuthGuard(['Recepcionista']);

  return (
    <div className="patient-card">
      <h3>{patient.name}</h3>
      
      {isAdmin && (
        <>
          <button>Editar Todo</button>
          <button>Eliminar</button>
        </>
      )}
      
      {isDoctor && !isAdmin && (
        <>
          <button>Ver Historial</button>
          <button>Agregar Nota</button>
        </>
      )}
      
      {isReceptionist && !isDoctor && !isAdmin && (
        <>
          <button>Ver Contacto</button>
          <button>Agendar Cita</button>
        </>
      )}
    </div>
  );
}
```

---

## 5. ChangePasswordModal Component

### Uso Básico
```typescript
import { useState } from 'react';
import { ChangePasswordModal } from './auth';

function ProfilePage() {
  const [showModal, setShowModal] = useState(false);

  return (
    <div>
      <h1>Mi Perfil</h1>
      
      <button onClick={() => setShowModal(true)}>
        Cambiar Contraseña
      </button>
      
      <ChangePasswordModal 
        isOpen={showModal} 
        onClose={() => setShowModal(false)} 
      />
    </div>
  );
}
```

### En Menú Desplegable
```typescript
import { useState } from 'react';
import { ChangePasswordModal } from './auth';
import { useAuth } from './auth';

function UserMenu() {
  const [showModal, setShowModal] = useState(false);
  const { user, logout } = useAuth();

  return (
    <div className="dropdown">
      <button className="user-avatar">
        {user?.nombre_completo[0]}
      </button>
      
      <div className="dropdown-menu">
        <div className="user-info">
          <p>{user?.nombre_completo}</p>
          <p className="text-sm">{user?.email}</p>
        </div>
        
        <button onClick={() => setShowModal(true)}>
          Cambiar Contraseña
        </button>
        
        <button onClick={logout}>
          Cerrar Sesión
        </button>
      </div>
      
      <ChangePasswordModal 
        isOpen={showModal} 
        onClose={() => setShowModal(false)} 
      />
    </div>
  );
}
```

---

## 6. authService Functions

### Login con Remember Me
```typescript
import { login } from './auth/authService';

async function handleLogin(username: string, password: string, rememberMe: boolean) {
  try {
    const response = await login({ username, password });
    
    if (rememberMe) {
      localStorage.setItem('rememberMe', 'true');
    }
    
    console.log('Login exitoso:', response.user);
    return response;
  } catch (error) {
    console.error('Error en login:', error.message);
    throw error;
  }
}
```

### Verificar Token Válido
```typescript
import { verifyToken } from './auth/authService';

async function checkTokenValidity() {
  const isValid = await verifyToken();
  
  if (!isValid) {
    console.log('Token inválido, redirigiendo a login...');
    window.location.href = '/login';
  } else {
    console.log('Token válido');
  }
}
```

### Solicitar Recuperación de Contraseña
```typescript
import { requestPasswordReset } from './auth/authService';

async function handleForgotPassword(email: string) {
  try {
    const response = await requestPasswordReset(email);
    alert(response.message);
    return true;
  } catch (error) {
    alert('Error: ' + error.message);
    return false;
  }
}
```

### Cambiar Contraseña
```typescript
import { changePassword } from './auth/authService';

async function handleChangePassword(
  currentPassword: string, 
  newPassword: string
) {
  try {
    const response = await changePassword(currentPassword, newPassword);
    alert('Contraseña cambiada exitosamente');
    return true;
  } catch (error) {
    if (error.message.includes('incorrecta')) {
      alert('La contraseña actual es incorrecta');
    } else if (error.message.includes('requisitos')) {
      alert('La nueva contraseña no cumple los requisitos');
    } else {
      alert('Error al cambiar contraseña');
    }
    return false;
  }
}
```

---

## 7. Flujos Completos

### Flujo de Login Completo
```typescript
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './auth';

function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(username, password, rememberMe);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      
      <input 
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Usuario"
      />
      
      <input 
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Contraseña"
      />
      
      <label>
        <input 
          type="checkbox"
          checked={rememberMe}
          onChange={(e) => setRememberMe(e.target.checked)}
        />
        Recordar sesión
      </label>
      
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Iniciando...' : 'Iniciar Sesión'}
      </button>
    </form>
  );
}
```

### Flujo de Recuperación de Contraseña
```typescript
import { useState } from 'react';
import { requestPasswordReset } from './auth/authService';

function ForgotPasswordForm() {
  const [email, setEmail] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await requestPasswordReset(email);
      setIsSuccess(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (isSuccess) {
    return (
      <div className="success-message">
        <h2>¡Correo enviado!</h2>
        <p>Revisa tu bandeja de entrada en {email}</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      
      <input 
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="tu@ejemplo.com"
      />
      
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Enviando...' : 'Enviar Instrucciones'}
      </button>
    </form>
  );
}
```

### Sistema de Permisos Complejo
```typescript
import { useAuthGuard } from './auth/hooks/useAuthGuard';

function DocumentActions({ document }) {
  const { hasAccess: canView } = useAuthGuard();
  const { hasAccess: canEdit } = useAuthGuard(['Admin', 'Podologo']);
  const { hasAccess: canDelete } = useAuthGuard(['Admin']);
  const { hasAccess: canApprove } = useAuthGuard(['Admin']);
  const { user } = useAuthGuard();
  
  // El creador siempre puede editar sus propios documentos
  const isCreator = document.createdBy === user?.id;
  const canEditThisDoc = canEdit || isCreator;

  return (
    <div className="document-actions">
      {canView && (
        <button onClick={() => viewDocument(document)}>
          Ver
        </button>
      )}
      
      {canEditThisDoc && (
        <button onClick={() => editDocument(document)}>
          Editar
        </button>
      )}
      
      {canApprove && !document.approved && (
        <button onClick={() => approveDocument(document)}>
          Aprobar
        </button>
      )}
      
      {canDelete && (
        <button onClick={() => deleteDocument(document)}>
          Eliminar
        </button>
      )}
    </div>
  );
}
```

---

## 8. Patrones Comunes

### Loading State Pattern
```typescript
import { useState } from 'react';
import { useAuth } from './auth';

function AsyncButton({ action, children }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleClick = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      await action();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <button onClick={handleClick} disabled={isLoading}>
        {isLoading ? 'Cargando...' : children}
      </button>
      {error && <span className="error">{error}</span>}
    </div>
  );
}
```

### Protected Component Pattern
```typescript
import { useAuthGuard } from './auth/hooks/useAuthGuard';

function withRoleGuard(Component, allowedRoles) {
  return function ProtectedComponent(props) {
    const { hasAccess } = useAuthGuard(allowedRoles);

    if (!hasAccess) {
      return <div>No tienes permisos</div>;
    }

    return <Component {...props} />;
  };
}

// Uso
const ProtectedAdminPanel = withRoleGuard(AdminPanel, ['Admin']);
```

### Auth State Pattern
```typescript
import { useAuth } from './auth';

function useAuthState() {
  const { isAuthenticated, isLoading, user } = useAuth();

  const authState = {
    isAuthenticated,
    isLoading,
    isGuest: !isAuthenticated && !isLoading,
    isAdmin: user?.rol === 'Admin',
    isPodologo: user?.rol === 'Podologo',
    isRecepcionista: user?.rol === 'Recepcionista',
    isPaciente: user?.rol === 'Paciente',
  };

  return authState;
}

// Uso
function MyComponent() {
  const auth = useAuthState();

  if (auth.isLoading) return <Spinner />;
  if (auth.isGuest) return <LoginPrompt />;
  if (auth.isAdmin) return <AdminView />;
  if (auth.isPodologo) return <DoctorView />;
  
  return <DefaultView />;
}
```

---

## 📚 Referencias

- **README.md**: Documentación completa del sistema
- **VISUAL_DEMO.md**: Demostración visual de mejoras
- **IMPLEMENTATION_SUMMARY.md**: Resumen ejecutivo

---

**Nota:** Todos estos ejemplos asumen que has importado los componentes/hooks correctamente y que el AuthProvider envuelve tu aplicación.
