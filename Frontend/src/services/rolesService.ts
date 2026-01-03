/**
 * Roles Service
 * Servicio para gestión de roles y permisos.
 */

import { API_BASE_URL } from './api';

export interface Role {
  id: number;
  nombre_rol: string;
  descripcion: string;
  permisos?: Record<string, any>;
  activo: boolean;
}

export interface RoleCreate {
  nombre_rol: string;
  descripcion: string;
  permisos?: Record<string, any>;
  activo?: boolean;
}

/**
 * Obtiene todos los roles.
 */
export async function getRoles(): Promise<Role[]> {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No hay token de autenticación');

  const response = await fetch(`${API_BASE_URL}/roles`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Error al obtener roles');
  }

  return response.json();
}

/**
 * Crea un nuevo rol.
 */
export async function createRole(data: RoleCreate): Promise<Role> {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No hay token de autenticación');

  const response = await fetch(`${API_BASE_URL}/roles`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al crear rol');
  }

  return response.json();
}

/**
 * Actualiza un rol existente.
 */
export async function updateRole(id: number, data: Partial<RoleCreate>): Promise<Role> {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No hay token de autenticación');

  const response = await fetch(`${API_BASE_URL}/roles/${id}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al actualizar rol');
  }

  return response.json();
}

/**
 * Elimina un rol.
 */
export async function deleteRole(id: number): Promise<void> {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No hay token de autenticación');

  const response = await fetch(`${API_BASE_URL}/roles/${id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al eliminar rol');
  }
}
