/**
 * Proveedores Service
 * Servicio para gestión de proveedores.
 */

import { API_BASE_URL } from './api';

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
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No hay token de autenticación');

  const params = new URLSearchParams();
  if (activo !== undefined) params.append('activo', activo.toString());

  const url = `${API_BASE_URL}/proveedores${params.toString() ? '?' + params.toString() : ''}`;

  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Error al obtener proveedores');
  }

  return response.json();
}

/**
 * Obtiene un proveedor por ID.
 */
export async function getProveedorById(id: number): Promise<Proveedor> {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No hay token de autenticación');

  const response = await fetch(`${API_BASE_URL}/proveedores/${id}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Error al obtener proveedor');
  }

  return response.json();
}

/**
 * Crea un nuevo proveedor.
 */
export async function createProveedor(data: ProveedorCreate): Promise<Proveedor> {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No hay token de autenticación');

  const response = await fetch(`${API_BASE_URL}/proveedores`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al crear proveedor');
  }

  return response.json();
}

/**
 * Actualiza un proveedor existente.
 */
export async function updateProveedor(id: number, data: Partial<ProveedorCreate>): Promise<Proveedor> {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No hay token de autenticación');

  const response = await fetch(`${API_BASE_URL}/proveedores/${id}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al actualizar proveedor');
  }

  return response.json();
}

/**
 * Desactiva un proveedor.
 */
export async function deleteProveedor(id: number): Promise<void> {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No hay token de autenticación');

  const response = await fetch(`${API_BASE_URL}/proveedores/${id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al eliminar proveedor');
  }
}
