/**
 * Mock Data Service for Admin Pages
 * 
 * Centralized mock data for development. Switch USE_MOCK to false
 * when backend endpoints are ready.
 */

export const USE_MOCK = true; // Cambiar a false cuando backend esté listo

// ========== ROLES ==========
export interface Role {
    id: number;
    nombre_rol: string;
    descripcion: string;
    permisos?: string[];
}

export const mockRoles: Role[] = [
    { id: 1, nombre_rol: 'Admin', descripcion: 'Administrador completo con acceso a todas las funciones', permisos: ['all'] },
    { id: 2, nombre_rol: 'Podologo', descripcion: 'Acceso clínico y gestión de pacientes', permisos: ['patients', 'appointments', 'medical'] },
    { id: 3, nombre_rol: 'Recepcionista', descripcion: 'Gestión de citas y pagos', permisos: ['appointments', 'billing'] },
    { id: 4, nombre_rol: 'Asistente', descripcion: 'Solo lectura de información básica', permisos: ['read_only'] },
];

// ========== USUARIOS/PERSONAL ==========
export interface Personal {
    id: number;
    nombre_completo: string;
    email: string;
    telefono: string;
    rol: string;
    activo: boolean;
    fecha_ingreso: string;
}

export const mockPersonal: Personal[] = [
    { id: 1, nombre_completo: 'Dr. Carlos Mendoza', email: 'carlos@podoskin.com', telefono: '686-555-1001', rol: 'Podologo', activo: true, fecha_ingreso: '2023-01-15' },
    { id: 2, nombre_completo: 'Dra. María García', email: 'maria@podoskin.com', telefono: '686-555-1002', rol: 'Podologo', activo: true, fecha_ingreso: '2023-03-20' },
    { id: 3, nombre_completo: 'Ana López', email: 'ana@podoskin.com', telefono: '686-555-1003', rol: 'Recepcionista', activo: true, fecha_ingreso: '2023-06-10' },
    { id: 4, nombre_completo: 'Juan Pérez', email: 'juan@podoskin.com', telefono: '686-555-1004', rol: 'Asistente', activo: false, fecha_ingreso: '2024-01-05' },
];

// ========== PROVEEDORES ==========
export interface Proveedor {
    id: number;
    nombre_comercial: string;
    razon_social?: string;
    telefono: string;
    email?: string;
    direccion?: string;
    activo: boolean;
}

export const mockProveedores: Proveedor[] = [
    { id: 1, nombre_comercial: 'Farmacéutica Regional', razon_social: 'Farmacéutica Regional S.A. de C.V.', telefono: '686-555-1234', email: 'ventas@farmaregional.com', activo: true },
    { id: 2, nombre_comercial: 'Instrumentos Médicos del Norte', razon_social: 'IMN S.A.', telefono: '686-555-5678', email: 'contacto@imn.com', activo: true },
    { id: 3, nombre_comercial: 'Distribuidora de Medicamentos BC', telefono: '686-555-9012', activo: true },
    { id: 4, nombre_comercial: 'Suministros Clínicos Plus', telefono: '686-555-3456', activo: false },
];

// ========== PRODUCTOS/INVENTARIO ==========
export type CategoriaProducto = 'Material_Curacion' | 'Instrumental' | 'Medicamento' | 'Ortesis' | 'Consumible';

export interface Producto {
    id: number;
    nombre: string;
    categoria: CategoriaProducto;
    stock_actual: number;
    stock_minimo: number;
    precio_compra: number;
    precio_venta: number;
    proveedor_id?: number;
}

export const mockProductos: Producto[] = [
    { id: 1, nombre: 'Gasa estéril 10x10', categoria: 'Material_Curacion', stock_actual: 50, stock_minimo: 20, precio_compra: 8.00, precio_venta: 15.00, proveedor_id: 1 },
    { id: 2, nombre: 'Bisturí desechable #15', categoria: 'Instrumental', stock_actual: 20, stock_minimo: 10, precio_compra: 25.00, precio_venta: 45.00, proveedor_id: 2 },
    { id: 3, nombre: 'Vendaje elástico 5cm', categoria: 'Material_Curacion', stock_actual: 35, stock_minimo: 15, precio_compra: 12.00, precio_venta: 25.00, proveedor_id: 1 },
    { id: 4, nombre: 'Solución antiséptica 500ml', categoria: 'Medicamento', stock_actual: 15, stock_minimo: 5, precio_compra: 45.00, precio_venta: 80.00, proveedor_id: 3 },
    { id: 5, nombre: 'Plantilla ortopédica básica', categoria: 'Ortesis', stock_actual: 8, stock_minimo: 5, precio_compra: 150.00, precio_venta: 350.00, proveedor_id: 2 },
    { id: 6, nombre: 'Guantes nitrilo M (caja 100)', categoria: 'Consumible', stock_actual: 10, stock_minimo: 5, precio_compra: 180.00, precio_venta: 250.00, proveedor_id: 1 },
];

// ========== HORARIOS ==========
export interface Horario {
    id: number;
    podologo_id: number;
    podologo_nombre: string;
    dia_semana: string;
    hora_inicio: string;
    hora_fin: string;
    activo: boolean;
}

export const mockHorarios: Horario[] = [
    { id: 1, podologo_id: 1, podologo_nombre: 'Dr. Carlos Mendoza', dia_semana: 'Lunes', hora_inicio: '09:00', hora_fin: '14:00', activo: true },
    { id: 2, podologo_id: 1, podologo_nombre: 'Dr. Carlos Mendoza', dia_semana: 'Martes', hora_inicio: '09:00', hora_fin: '14:00', activo: true },
    { id: 3, podologo_id: 1, podologo_nombre: 'Dr. Carlos Mendoza', dia_semana: 'Miércoles', hora_inicio: '15:00', hora_fin: '20:00', activo: true },
    { id: 4, podologo_id: 2, podologo_nombre: 'Dra. María García', dia_semana: 'Lunes', hora_inicio: '15:00', hora_fin: '20:00', activo: true },
    { id: 5, podologo_id: 2, podologo_nombre: 'Dra. María García', dia_semana: 'Jueves', hora_inicio: '09:00', hora_fin: '14:00', activo: true },
    { id: 6, podologo_id: 2, podologo_nombre: 'Dra. María García', dia_semana: 'Viernes', hora_inicio: '09:00', hora_fin: '14:00', activo: true },
];

// ========== KPIs ADMIN ==========
export interface AdminKPIs {
    ingresos_mes: number;
    gastos_mes: number;
    citas_mes: number;
    pacientes_nuevos: number;
    ingresos_tendencia: number; // porcentaje
    gastos_tendencia: number;
    citas_tendencia: number;
    pacientes_tendencia: number;
}

export const mockKPIs: AdminKPIs = {
    ingresos_mes: 45000.00,
    gastos_mes: 12500.00,
    citas_mes: 87,
    pacientes_nuevos: 12,
    ingresos_tendencia: 8.5,
    gastos_tendencia: -3.2,
    citas_tendencia: 12.0,
    pacientes_tendencia: 15.5,
};

// ========== GASTOS ==========
export type CategoriaGasto = 'Renta' | 'Servicios' | 'Nomina' | 'Insumos' | 'Mantenimiento' | 'Marketing' | 'Otros';

export interface Gasto {
    id: number;
    categoria: CategoriaGasto;
    concepto: string;
    monto: number;
    fecha: string;
    proveedor_id?: number;
}

export const mockGastos: Gasto[] = [
    { id: 1, categoria: 'Renta', concepto: 'Local comercial - Diciembre', monto: 8000, fecha: '2025-12-01' },
    { id: 2, categoria: 'Servicios', concepto: 'Luz y agua', monto: 1500, fecha: '2025-12-05' },
    { id: 3, categoria: 'Insumos', concepto: 'Material de curación', monto: 2500, fecha: '2025-12-10', proveedor_id: 1 },
    { id: 4, categoria: 'Nomina', concepto: 'Pago quincenal personal', monto: 15000, fecha: '2025-12-15' },
    { id: 5, categoria: 'Mantenimiento', concepto: 'Servicio equipo', monto: 800, fecha: '2025-12-18' },
];

// ========== CORTES DE CAJA ==========
export interface CorteCaja {
    id: number;
    fecha_corte: string;
    total_ingresos: number;
    gastos_dia: number;
    saldo_inicial: number;
    saldo_final: number;
    usuario_cierre: string;
    notas?: string;
}

export const mockCortesCaja: CorteCaja[] = [
    { id: 1, fecha_corte: '2025-12-30', total_ingresos: 4500, gastos_dia: 200, saldo_inicial: 1000, saldo_final: 5300, usuario_cierre: 'Ana López' },
    { id: 2, fecha_corte: '2025-12-31', total_ingresos: 3800, gastos_dia: 150, saldo_inicial: 5300, saldo_final: 8950, usuario_cierre: 'Ana López' },
    { id: 3, fecha_corte: '2026-01-01', total_ingresos: 2100, gastos_dia: 0, saldo_inicial: 8950, saldo_final: 11050, usuario_cierre: 'Ana López' },
];

// ========== INGRESOS POR MES ==========
export interface IngresoMensual {
    mes: string;
    ingresos: number;
    gastos: number;
}

export const mockIngresosMensuales: IngresoMensual[] = [
    { mes: 'Jul', ingresos: 38000, gastos: 11000 },
    { mes: 'Ago', ingresos: 42000, gastos: 12500 },
    { mes: 'Sep', ingresos: 39500, gastos: 11800 },
    { mes: 'Oct', ingresos: 44000, gastos: 13000 },
    { mes: 'Nov', ingresos: 41000, gastos: 12000 },
    { mes: 'Dic', ingresos: 45000, gastos: 12500 },
];

// ========== HELPER FUNCTIONS ==========
export function getProveedorNombre(id: number): string {
    const proveedor = mockProveedores.find(p => p.id === id);
    return proveedor?.nombre_comercial || 'Sin proveedor';
}

export function getCategoriaColor(categoria: CategoriaProducto | CategoriaGasto): string {
    const colors: Record<string, string> = {
        // Productos
        'Material_Curacion': 'bg-blue-100 text-blue-800',
        'Instrumental': 'bg-purple-100 text-purple-800',
        'Medicamento': 'bg-green-100 text-green-800',
        'Ortesis': 'bg-orange-100 text-orange-800',
        'Consumible': 'bg-gray-100 text-gray-800',
        // Gastos
        'Renta': 'bg-red-100 text-red-800',
        'Servicios': 'bg-yellow-100 text-yellow-800',
        'Nomina': 'bg-indigo-100 text-indigo-800',
        'Insumos': 'bg-cyan-100 text-cyan-800',
        'Mantenimiento': 'bg-pink-100 text-pink-800',
        'Marketing': 'bg-teal-100 text-teal-800',
        'Otros': 'bg-gray-100 text-gray-800',
    };
    return colors[categoria] || 'bg-gray-100 text-gray-800';
}
