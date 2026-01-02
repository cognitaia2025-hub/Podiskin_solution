# Plan Frontend: Menú Usuario (Ajustes, Admin, Perfil)

## Contexto

Se requiere implementar un menú desplegable en el avatar del usuario con 4 opciones: Ajustes, Admin, Perfil, Cerrar Sesión. El backend se desarrollará en paralelo, por lo que **usarás datos mock inicialmente**.

---

## Archivos Existentes a Reutilizar

### Dropdown Existente

- `src/components/AppShell.tsx` líneas 78-111
- Ya tiene lógica de `showUserMenu` y `handleLogout`

### Componentes Dashboard Reutilizables

```
src/components/dashboard/
├── KPICard.tsx                    → Para métricas
├── AppointmentTrendChart.tsx      → Gráficos línea
├── AppointmentsByStatusChart.tsx  → Gráficos pastel
├── RevenueChart.tsx               → Gráficos barras
└── TopTreatmentsTable.tsx         → Tablas de datos
```

---

## Tarea 1: Modificar AppShell.tsx (L78-111)

Agregar 3 opciones antes de "Cerrar Sesión":

```tsx
{/* Dentro del dropdown, después del header con info usuario */}

{/* Solo visible para rol Admin */}
{user?.rol === 'Admin' && (
  <>
    <button onClick={() => { navigate('/ajustes'); setShowUserMenu(false); }}
      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2">
      <span>⚙️</span><span>Ajustes</span>
    </button>
    <button onClick={() => { navigate('/admin'); setShowUserMenu(false); }}
      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2">
      <span>📊</span><span>Admin</span>
    </button>
  </>
)}

{/* Visible para todos */}
<button onClick={() => { navigate('/perfil'); setShowUserMenu(false); }}
  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2">
  <span>👤</span><span>Perfil</span>
</button>

<div className="border-t border-gray-200" />

{/* Cerrar sesión existente */}
```

---

## Tarea 2: Crear Página Ajustes

### Archivo: `src/pages/AjustesPage.tsx`

**Estructura con Tabs:**

- Tab 1: Roles y Permisos
- Tab 2: Usuarios/Personal
- Tab 3: Proveedores
- Tab 4: Productos/Inventario
- Tab 5: Horarios

**Datos Mock (usar mientras backend no está listo):**

```tsx
const mockRoles = [
  { id: 1, nombre_rol: 'Admin', descripcion: 'Administrador completo' },
  { id: 2, nombre_rol: 'Podologo', descripcion: 'Acceso clínico' },
  { id: 3, nombre_rol: 'Recepcionista', descripcion: 'Citas y pagos' },
  { id: 4, nombre_rol: 'Asistente', descripcion: 'Solo lectura' },
];

const mockProveedores = [
  { id: 1, nombre_comercial: 'Farmacéutica Regional', telefono: '686-555-1234', activo: true },
  { id: 2, nombre_comercial: 'Instrumentos Médicos del Norte', telefono: '686-555-5678', activo: true },
];

const mockProductos = [
  { id: 1, nombre: 'Gasa estéril', categoria: 'Material_Curacion', stock_actual: 50, precio_venta: 15.00 },
  { id: 2, nombre: 'Bisturí desechable', categoria: 'Instrumental', stock_actual: 20, precio_venta: 45.00 },
];
```

**Componente sugerido:**

```tsx
<Tabs defaultValue="roles">
  <TabsList>
    <TabsTrigger value="roles">Roles</TabsTrigger>
    <TabsTrigger value="usuarios">Personal</TabsTrigger>
    <TabsTrigger value="proveedores">Proveedores</TabsTrigger>
    <TabsTrigger value="productos">Productos</TabsTrigger>
    <TabsTrigger value="horarios">Horarios</TabsTrigger>
  </TabsList>
  <TabsContent value="roles"><RolesTable data={mockRoles} /></TabsContent>
  ...
</Tabs>
```

---

## Tarea 3: Crear Página Admin

### Archivo: `src/pages/AdminPage.tsx`

**Estructura:**

- Header con DateRangePicker (filtro de fechas)
- Grid de KPICards (ingresos, gastos, citas, pacientes)
- Sección gráficos (reusar componentes existentes)
- Tabla de datos filtrados

**Datos Mock:**

```tsx
const mockKPIs = {
  ingresos: 45000.00,
  gastos: 12500.00,
  citas_mes: 87,
  pacientes_nuevos: 12,
};

const mockGastos = [
  { id: 1, categoria: 'Renta', concepto: 'Local comercial', monto: 8000, fecha: '2025-12-01' },
  { id: 2, categoria: 'Servicios', concepto: 'Luz y agua', monto: 1500, fecha: '2025-12-05' },
];

const mockCortesCaja = [
  { id: 1, fecha_corte: '2025-12-30', total_ingresos: 4500, gastos_dia: 200, saldo_final: 4300 },
  { id: 2, fecha_corte: '2025-12-31', total_ingresos: 3800, gastos_dia: 150, saldo_final: 3650 },
];
```

**Reutilizar:**

- `<KPICard />` para métricas
- `<RevenueChart />` adaptado para ingresos vs gastos

---

## Tarea 4: Crear Página Perfil

### Archivo: `src/pages/PerfilPage.tsx`

**Formulario con campos:**

- Nombre completo
- Email
- Teléfono (si es podólogo)
- Cambiar contraseña (modal separado)
- Foto de perfil (opcional)

**Usar datos del contexto Auth:**

```tsx
const { user } = useAuth();
// user.nombre_completo, user.email, user.rol
```

---

## Tarea 5: Agregar Rutas

### Archivo: `src/App.tsx`

```tsx
import AjustesPage from './pages/AjustesPage';
import AdminPage from './pages/AdminPage';
import PerfilPage from './pages/PerfilPage';

// Dentro del Router, rutas protegidas:
<Route path="/ajustes" element={<ProtectedRoute><AjustesPage /></ProtectedRoute>} />
<Route path="/admin" element={<ProtectedRoute><AdminPage /></ProtectedRoute>} />
<Route path="/perfil" element={<ProtectedRoute><PerfilPage /></ProtectedRoute>} />
```

---

## Servicios Mock (para desarrollo paralelo)

### Archivo: `src/services/mockData.ts`

Crear archivo centralizado con todos los datos mock. Después el backend proporcionará script para cambiar a datos reales.

```tsx
// src/services/mockData.ts
export const USE_MOCK = true; // Cambiar a false cuando backend esté listo

export const mockRoles = [...];
export const mockProveedores = [...];
export const mockGastos = [...];
// etc.
```

---

## Checklist

- [ ] Modificar `AppShell.tsx` - agregar opciones al dropdown
- [ ] Crear `src/pages/AjustesPage.tsx` con tabs
- [ ] Crear `src/pages/AdminPage.tsx` con gráficos
- [ ] Crear `src/pages/PerfilPage.tsx` con formulario
- [ ] Crear `src/services/mockData.ts` centralizado
- [ ] Agregar rutas en `App.tsx`
- [ ] Verificar que solo Admin vea Ajustes/Admin
- [ ] Estilos consistentes con tema actual

---

## Notas Técnicas

- **Permisos**: Usar `user.rol === 'Admin'` del contexto Auth
- **Navegación**: Ya existe `useNavigate` en AppShell
- **Estilos**: Mantener clases Tailwind del proyecto
- **Íconos**: Usar emojis por ahora, después reemplazar con Lucide/Heroicons

---

## Después (Backend integrará)

El backend creará un script que:

1. Cambiará `USE_MOCK = false`
2. Conectará a endpoints reales (`/api/roles`, `/api/proveedores`, etc.)
3. Actualizará los servicios para usar fetch/axios
