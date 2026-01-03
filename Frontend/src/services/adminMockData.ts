/**
 * Temporary stubs for AdminMockData
 * TODO: Replace with real API calls to dashboard/stats endpoints
 */

export const mockKPIs = [];
export const mockGastos = [];
export const mockCortesCaja = [];
export const mockIngresosMensuales = [];
export const mockRoles = [];
export const mockPersonal = [];
export const mockProveedores = [];
export const mockProductos = [];
export const mockHorarios = [];

export function getCategoriaColor(_categoria: string): string {
    return 'bg-gray-500';
}

export function getProveedorNombre(_proveedorId: string): string {
    return 'Proveedor';
}

// Type exports for compatibility
export type Role = any;
export type Personal = any;
export type Proveedor = any;
export type Producto = any;
export type Horario = any;
