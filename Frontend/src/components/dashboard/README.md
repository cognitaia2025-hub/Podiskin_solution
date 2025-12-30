# Dashboard Components

Componentes del dashboard para visualizar métricas y estadísticas de la clínica.

## Componentes

### 1. DashboardPage (`/pages/DashboardPage.tsx`)

Página principal del dashboard que integra todos los componentes.

**Características:**
- Carga datos al montar el componente
- Botón de actualización con loading state
- Manejo de estados de loading y error
- Layout responsive con grids adaptativos
- Actualmente usa datos mock (comentarios indican donde usar API real)

**Uso:**
```tsx
<Route path="/dashboard" element={<DashboardPage />} />
```

### 2. KPICard (`KPICard.tsx`)

Tarjeta para mostrar métricas clave (KPI).

**Props:**
- `title`: Título del KPI
- `value`: Valor a mostrar (string o number)
- `icon`: Ícono de React (de lucide-react)
- `color`: Color del tema ('blue' | 'green' | 'purple' | 'orange')
- `trend` (opcional): Objeto con `value` (porcentaje) y `isPositive` (boolean)

**Ejemplo:**
```tsx
<KPICard
  title="Total Pacientes"
  value={248}
  icon={<Users className="w-6 h-6" />}
  color="blue"
  trend={{ value: 12, isPositive: true }}
/>
```

### 3. DashboardHeader (`DashboardHeader.tsx`)

Header con título y botón de actualización.

**Props:**
- `onRefresh`: Función async para refrescar datos
- `lastUpdated` (opcional): Fecha de última actualización

**Ejemplo:**
```tsx
<DashboardHeader 
  onRefresh={loadDashboardData} 
  lastUpdated={new Date()}
/>
```

### 4. AppointmentTrendChart (`AppointmentTrendChart.tsx`)

Gráfica de líneas mostrando tendencia de citas en los últimos 30 días.

**Props:**
- `data`: Array de `AppointmentTrend` (fecha, cantidad, completadas, canceladas)

**Características:**
- Tres líneas: Total, Completadas, Canceladas
- Colores: Azul (total), Verde (completadas), Rojo (canceladas)
- Formato de fechas en español
- Tooltip con información detallada

### 5. AppointmentsByStatusChart (`AppointmentsByStatusChart.tsx`)

Gráfica de pie (pastel) mostrando distribución de citas por estado.

**Props:**
- `data`: Objeto con contadores por estado (pendiente, confirmada, completada, cancelada, no_asistio)

**Características:**
- Colores por estado:
  - Pendiente: Amarillo (#fbbf24)
  - Confirmada: Azul (#3b82f6)
  - Completada: Verde (#10b981)
  - Cancelada: Rojo (#ef4444)
  - No asistió: Naranja (#f97316)
- Muestra porcentajes en las etiquetas
- Filtra automáticamente valores en cero

### 6. RevenueChart (`RevenueChart.tsx`)

Gráfica de área mostrando ingresos mensuales.

**Props:**
- `data`: Array de `RevenueTrend` (mes, ingresos)

**Características:**
- Color púrpura (#8b5cf6)
- Formato de moneda en español (es-MX)
- Eje Y muestra valores en miles (K)
- Gradiente de relleno

### 7. TopTreatmentsTable (`TopTreatmentsTable.tsx`)

Tabla mostrando los tratamientos más comunes.

**Props:**
- `data`: Array de objetos con `nombre` y `cantidad`

**Características:**
- Numeración automática
- Columna de porcentaje calculado
- Hover effect en filas
- Responsive

## Servicios (`dashboardService.ts`)

### Interfaces

```typescript
interface DashboardStats {
  total_patients: number;
  active_patients: number;
  new_patients_this_month: number;
  total_appointments_today: number;
  total_appointments_week: number;
  total_appointments_month: number;
  appointments_by_status: { ... };
  revenue_today: number;
  revenue_week: number;
  revenue_month: number;
  revenue_year: number;
  top_treatments: Array<{ nombre: string; cantidad: number }>;
  ocupacion_porcentaje: number;
  upcoming_appointments: number;
}

interface AppointmentTrend {
  fecha: string;
  cantidad: number;
  completadas: number;
  canceladas: number;
}

interface RevenueTrend {
  mes: string;
  ingresos: number;
}
```

### Funciones

#### API Real (Pendiente implementación en backend)

```typescript
getDashboardStats(): Promise<DashboardStats>
getAppointmentTrend(days?: number): Promise<AppointmentTrend[]>
getRevenueTrend(): Promise<RevenueTrend[]>
```

#### Funciones Mock (Para desarrollo)

```typescript
getMockDashboardStats(): DashboardStats
getMockAppointmentTrend(): AppointmentTrend[]
getMockRevenueTrend(): RevenueTrend[]
```

## Agregar Nuevos KPIs

Para agregar un nuevo KPI al dashboard:

1. Actualizar la interfaz `DashboardStats` en `dashboardService.ts`
2. Agregar un nuevo `<KPICard>` en `DashboardPage.tsx`
3. Elegir un ícono de lucide-react
4. Elegir un color: 'blue', 'green', 'purple', 'orange'

**Ejemplo:**
```tsx
<KPICard
  title="Nuevos Pacientes"
  value={stats.new_patients_this_month}
  icon={<UserPlus className="w-6 h-6" />}
  color="green"
  trend={{ value: 15, isPositive: true }}
/>
```

## Personalizar Colores

Los colores están definidos en cada componente. Para cambiarlos:

### KPICard
Editar `colorClasses` en `KPICard.tsx`:
```typescript
const colorClasses = {
  blue: 'bg-blue-100 text-blue-600',
  // ... agregar más colores
};
```

### Gráficas
Los colores de las gráficas se definen en las props de Recharts:
- `stroke`: Color de línea/borde
- `fill`: Color de relleno

## Endpoints Backend Necesarios

Para usar datos reales, el backend debe implementar estos endpoints:

### GET `/stats/dashboard`
Retorna `DashboardStats` completo.

### GET `/stats/appointments-trend?days=30`
Retorna array de `AppointmentTrend` para los últimos N días.

### GET `/stats/revenue-trend`
Retorna array de `RevenueTrend` para los últimos 12 meses.

## Dependencias

- **recharts**: Librería de gráficas
- **lucide-react**: Íconos
- **react-toastify**: Notificaciones
- **tailwindcss**: Estilos

## Layout Responsive

El dashboard usa grids de Tailwind CSS:

```tsx
// 1 columna en móvil, 2 en tablet, 4 en desktop
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

// 1 columna en móvil, 2 en desktop
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
```

## Próximas Mejoras

- [ ] Conectar a API real del backend
- [ ] Agregar filtros por período (día, semana, mes, año)
- [ ] Exportar reportes a PDF/Excel
- [ ] Agregar más tipos de gráficas (barras, radar)
- [ ] Sistema de alertas en tiempo real
- [ ] Comparativas período anterior
- [ ] Gráficas interactivas con drill-down
