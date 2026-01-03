/**
 * Roles Service
 * Servicio para gestión de roles y permisos.
 */

import api from './api';

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
  const { data } = await api.get('/api/roles');
  return data;
}

/**
 * Crea un nuevo rol.
 */
export async function createRole(roleData: RoleCreate): Promise<Role> {
  const { data } = await api.post('/api/roles', roleData);
  return data;
}

/**
 * Actualiza un rol existente.
 */
export async function updateRole(id: number, roleData: Partial<RoleCreate>): Promise<Role> {
  const { data } = await api.put(`/api/roles/${id}`, roleData);
  return data;
}

/**
 * Elimina un rol.
 */
export async function deleteRole(id: number): Promise<void> {
  await api.delete(`/api/roles/${id}`);
}
