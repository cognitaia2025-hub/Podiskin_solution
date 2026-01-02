# Informe de Cambios - 01 de Enero 2026

## Resumen Ejecutivo

Se implementó la infraestructura completa para el menú de usuario con opciones de Ajustes, Admin, Perfil y Cerrar Sesión, incluyendo backend (endpoints CRUD) y frontend (páginas y componentes).

---

## 1. Cambios en Base de Datos (PostgreSQL Docker)

### 1.1 Tablas Nuevas Creadas

| Tabla | Descripción | Estado |
|-------|-------------|--------|
| `roles` | Catálogo de roles del sistema | ✅ Creada |
| `proveedores` | Catálogo de proveedores de inventario | ✅ Creada |
| `gastos` | Registro de gastos operativos | ✅ Creada |
| `cortes_caja` | Cierres de caja diarios | ✅ Creada |
| `facturas` | Facturas fiscales | ✅ Creada |

**Total de tablas en BD: 49**

### 1.2 Vistas SQL Creadas

| Vista | Propósito |
|-------|-----------|
| `resumen_gastos_mensual` | Agrupa gastos por categoría y mes |
| `balance_financiero` | Ingresos agregados por mes |
| `alertas_inventario` | Productos con stock bajo mínimo |

### 1.3 Datos Iniciales Insertados

```sql
-- 4 roles predeterminados
INSERT INTO roles (nombre_rol, descripcion, permisos) VALUES
('Admin', 'Administrador completo', '{"all":true}'),
('Podologo', 'Acceso clinico', '{"citas":true,"pacientes":true,"tratamientos":true}'),
('Recepcionista', 'Citas y pagos', '{"citas":true,"pagos":true}'),
('Asistente', 'Solo lectura', '{"lectura":true}');
```

### 1.4 Script SQL

- **Archivo**: `backend/init_menu_usuario.sql`
- **Contenido**: Inserts de roles + creación de vistas

---

## 2. Cambios en Backend (FastAPI)

### 2.1 Nuevos Módulos Creados

#### Módulo `roles/`

| Archivo | Descripción |
|---------|-------------|
| `__init__.py` | Exporta router y service |
| `service.py` | CRUD con psycopg2 |
| `router.py` | Endpoints REST |

**Endpoints:**

- `GET /api/roles` - Lista todos los roles
- `GET /api/roles/{id}` - Obtiene un rol
- `POST /api/roles` - Crea un rol
- `PUT /api/roles/{id}` - Actualiza un rol
- `DELETE /api/roles/{id}` - Soft delete

#### Módulo `proveedores/`

| Archivo | Descripción |
|---------|-------------|
| `__init__.py` | Exporta router y service |
| `service.py` | CRUD con psycopg2 |
| `router.py` | Endpoints REST |

**Endpoints:**

- `GET /api/proveedores` - Lista proveedores
- `GET /api/proveedores/{id}` - Obtiene proveedor
- `POST /api/proveedores` - Crea proveedor
- `PUT /api/proveedores/{id}` - Actualiza proveedor
- `DELETE /api/proveedores/{id}` - Soft delete

#### Módulo `gastos/`

| Archivo | Descripción |
|---------|-------------|
| `__init__.py` | Exporta router y service |
| `service.py` | CRUD + resumen por categoría |
| `router.py` | Endpoints REST |

**Endpoints:**

- `GET /api/gastos` - Lista gastos con filtros (categoría, desde, hasta)
- `GET /api/gastos/resumen` - Resumen por categoría
- `POST /api/gastos` - Registra un gasto

#### Módulo `cortes_caja/`

| Archivo | Descripción |
|---------|-------------|
| `__init__.py` | Exporta router y service |
| `service.py` | Lógica de cierre de caja |
| `router.py` | Endpoints REST |

**Endpoints:**

- `GET /api/cortes-caja` - Lista todos los cortes
- `GET /api/cortes-caja/{fecha}` - Corte de una fecha específica
- `POST /api/cortes-caja` - Crea el corte del día

### 2.2 Endpoints de Perfil de Usuario

**Archivo modificado**: `auth/router.py` (líneas 240-350)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/auth/me` | GET | Obtiene perfil del usuario actual |
| `/auth/me` | PUT | Actualiza nombre/email del perfil |
| `/auth/me/password` | PUT | Cambia la contraseña |

### 2.3 Funciones de Base de Datos Agregadas

**Archivo modificado**: `auth/database.py`

```python
async def update_user_profile(user_id: int, updates: dict) -> bool
async def update_user_password(user_id: int, password_hash: str) -> bool
```

### 2.4 Corrección Crítica en Autenticación

**Archivo**: `auth/database.py` (línea 93-106)

**Problema**: El query hacía `JOIN roles r ON u.id_rol = r.id` pero la tabla `usuarios` tiene columna `rol` (texto), NO `id_rol`.

**Antes (incorrecto):**

```sql
SELECT u.id, r.nombre_rol as rol, ...
FROM usuarios u
INNER JOIN roles r ON u.id_rol = r.id
WHERE u.nombre_usuario = %s
```

**Después (correcto):**

```sql
SELECT id, rol, ...
FROM usuarios
WHERE nombre_usuario = %s
```

### 2.5 Registro en main.py

**Archivo modificado**: `main.py`

```python
# Imports agregados
from roles import router as roles_router
from proveedores import router as proveedores_router
from gastos import router as gastos_router
from cortes_caja import router as cortes_caja_router

# Registros agregados
app.include_router(roles_router, prefix="/api")
app.include_router(proveedores_router, prefix="/api")
app.include_router(gastos_router, prefix="/api")
app.include_router(cortes_caja_router, prefix="/api")
```

---

## 3. Cambios en Frontend (React/TypeScript)

### 3.1 Corrección de Loop Infinito

**Archivo**: `hooks/useAppointments.ts`

**Problema**: El `useEffect` se disparaba infinitamente porque `doctorIds` (array) cambiaba en cada render.

**Solución**:

```typescript
// Convertir array a string para comparación estable
const doctorIdsKey = doctorIds.join(',');

const fetchData = useCallback(async () => {
  // ...
}, [startDate?.getTime(), endDate?.getTime(), doctorIdsKey, patientId, status]);
```

### 3.2 Corrección de Formato de Respuesta

**Archivo**: `hooks/useAppointments.ts` (línea 72-78)

**Problema**: El backend devuelve `{total, citas}` pero el frontend esperaba un array `[]`.

**Solución**:

```typescript
const data = await fetchAppointments(params);
// Handle both formats
const appointmentsArray = Array.isArray(data) ? data : (data.citas || []);
const mappedData = appointmentsArray.map((appt) => ({...}));
```

### 3.3 Páginas Creadas por Agente Frontend

| Página | Archivo | Tamaño | Descripción |
|--------|---------|--------|-------------|
| Ajustes | `pages/AjustesPage.tsx` | 23.8 KB | Tabs: Roles, Personal, Proveedores, Productos, Horarios |
| Admin | `pages/AdminPage.tsx` | 15.7 KB | KPIs, gráficos, historial de cortes |
| Perfil | `pages/PerfilPage.tsx` | 18 KB | Editar datos, cambiar contraseña |

### 3.4 Menú Dropdown en AppShell

**Archivo modificado**: `components/AppShell.tsx` (líneas 77-150)

- Dropdown al hacer clic en foto de perfil
- Opciones Admin-only: Ajustes, Admin (condición `user?.rol === 'Admin'`)
- Opción para todos: Perfil
- Cerrar Sesión

---

## 4. 🔴 ERROR PENDIENTE - Para Otro Agente

### Descripción del Problema

El menú dropdown en `AppShell.tsx` **solo muestra "Cerrar Sesión"**. Las opciones de Ajustes, Admin y Perfil **no se renderizan** a pesar de que:

1. El backend devuelve `"rol": "Admin"` correctamente en el login
2. El localStorage contiene `{..., "rol": "Admin", ...}`
3. La condición en el código es `user?.rol === 'Admin'`

### Ubicación del Código

**Archivo**: `Frontend/src/components/AppShell.tsx`
**Líneas**: 92-126

```tsx
{/* Admin-only options */}
{user?.rol === 'Admin' && (
    <>
        <button onClick={() => navigate('/ajustes')}>Ajustes</button>
        <button onClick={() => navigate('/admin')}>Admin</button>
    </>
)}

{/* Profile - visible for all users */}
<button onClick={() => navigate('/perfil')}>Perfil</button>
```

### Hipótesis

1. El objeto `user` del contexto `useAuth()` no tiene la propiedad `rol` actualizada
2. El componente AppShell no se re-renderiza después del login
3. Problema con el AuthContext que no propaga el usuario correctamente

### Pasos de Debugging Sugeridos

1. Agregar `console.log('User in AppShell:', user)` antes del return
2. Verificar si `user` es null o tiene el rol
3. Verificar que `AuthProvider` envuelve a `AppShell`
4. Probar con `{user?.rol?.toLowerCase() === 'admin'}` por si hay diferencia de case

---

## 5. Credenciales de Prueba

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `dr.santiago` | `password123` | Admin |
| `ivette.martinez` | `password123` | Recepcionista |

---

## 6. Comandos para Iniciar

```powershell
# Backend
cd backend
.\venv\Scripts\uvicorn.exe main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd Frontend
npm run dev
```

---

## 7. Archivos Modificados (Resumen)

### Backend

- `backend/main.py` - Imports y registros de routers
- `backend/auth/router.py` - Endpoints /me
- `backend/auth/database.py` - Query corregido + funciones update
- `backend/init_menu_usuario.sql` - Script SQL nuevo
- `backend/roles/` - Módulo nuevo
- `backend/proveedores/` - Módulo nuevo
- `backend/gastos/` - Módulo nuevo
- `backend/cortes_caja/` - Módulo nuevo

### Frontend

- `Frontend/src/hooks/useAppointments.ts` - Loop fix + formato respuesta
- `Frontend/src/components/AppShell.tsx` - Menú dropdown (creado por otro agente)
- `Frontend/src/pages/AjustesPage.tsx` - Nueva página (creado por otro agente)
- `Frontend/src/pages/AdminPage.tsx` - Nueva página (creado por otro agente)
- `Frontend/src/pages/PerfilPage.tsx` - Nueva página (creado por otro agente)

---

**Fecha**: 01 de Enero de 2026
**Autor**: Antigravity AI Agent
