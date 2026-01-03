/**
 * Proveedores Service
 * Servicio para gestión de proveedores.
 */

import api from './api';

export interface Proveedor {
  id: number;
  nombre_comercial: string;
  razon_social?: string;
  rfc?: string;
  telefono: string;
  email?: string;
  direccion?: string;
  ciudad?: string;
  estado?: string;
  codigo_postal?: string;
  contacto_principal?: string;
  activo: boolean;
}

export interface ProveedorCreate {
  nombre_comercial: string;
  razon_social?: string;
  rfc?: string;
  telefono: string;
  email?: string;
  direccion?: string;
  ciudad?: string;
  estado?: string;
  codigo_postal?: string;
  contacto_principal?: string;
  activo?: boolean;
}

/**
 * Obtiene todos los proveedores.
 */
export async function getProveedores(activo?: boolean): Promise<Proveedor[]> {
  const params = activo !== undefined ? { activo } : {};
  const { data } = await api.get('/api/proveedores', { params });
  return data;
}

/**
 * Obtiene un proveedor por ID.
 */
export async function getProveedorById(id: number): Promise<Proveedor> {
  const { data } = await api.get(`/api/proveedores/${id}`);
  return data;
}

/**
 * Crea un nuevo proveedor.
 */
export async function createProveedor(proveedorData: ProveedorCreate): Promise<Proveedor> {
  const { data } = await api.post('/api/proveedores', proveedorData);
  return data;
}

/**
 * Actualiza un proveedor existente.
 */
export async function updateProveedor(id: number, proveedorData: Partial<ProveedorCreate>): Promise<Proveedor> {
  const { data } = await api.put(`/api/proveedores/${id}`, proveedorData);
  return data;
}

/**
 * Desactiva un proveedor.
 */
export async function deleteProveedor(id: number): Promise<void> {
  await api.delete(`/api/proveedores/${id}`);
}
