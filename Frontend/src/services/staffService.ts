/**
 * Staff Management Service
 * 
 * Service for managing system users (staff members).
 * Consumes the real API endpoints from /auth/users
 */

import api from './api';

// ============================================================================
// TYPES
// ============================================================================

export interface StaffMember {
  id: number;
  nombre_usuario: string;
  nombre_completo: string;
  email: string;
  rol: string | null;
  id_rol?: number;
  activo: boolean;
  ultimo_login: string | null;
  fecha_registro: string | null;
}

export interface CreateStaffRequest {
  nombre_usuario: string;
  password: string;
  nombre_completo: string;
  email: string;
  id_rol: number;
  cedula_profesional?: string;  // Opcional, solo para Podólogos
}

export interface UpdateStaffRequest {
  nombre_completo?: string;
  email?: string;
  id_rol?: number;
  activo?: boolean;
}

export interface Role {
  id: number;
  nombre_rol: string;
  descripcion: string | null;
  permisos: Record<string, any> | null;
  activo: boolean;
  fecha_creacion: string | null;
}

// ============================================================================
// SERVICE
// ============================================================================

class StaffService {
  /**
   * Lista todos los usuarios del sistema
   */
  async getAllStaff(activoOnly: boolean = true): Promise<StaffMember[]> {
    try {
      const response = await api.get('/api/users', {
        params: { activo_only: activoOnly }
      });
      return response.data;
    } catch (error: any) {
      console.error('Error fetching staff:', error);
      throw new Error(
        error.response?.data?.detail || 'Error al cargar el personal'
      );
    }
  }

  /**
   * Obtiene un usuario por ID
   */
  async getStaffById(userId: number): Promise<StaffMember> {
    try {
      const response = await api.get(`/auth/users/${userId}`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching staff member:', error);
      throw new Error(
        error.response?.data?.detail || 'Error al cargar el usuario'
      );
    }
  }

  /**
   * Crea un nuevo usuario
   */
  async createStaff(data: CreateStaffRequest): Promise<StaffMember> {
    try {
      const response = await api.post('/api/users', data);
      return response.data;
    } catch (error: any) {
      console.error('Error creating staff member:', error);
      throw new Error(
        error.response?.data?.detail || 'Error al crear el usuario'
      );
    }
  }

  /**
   * Actualiza un usuario existente
   */
  async updateStaff(userId: number, data: UpdateStaffRequest): Promise<StaffMember> {
    try {
      const response = await api.put(`/auth/users/${userId}`, data);
      return response.data;
    } catch (error: any) {
      console.error('Error updating staff member:', error);
      throw new Error(
        error.response?.data?.detail || 'Error al actualizar el usuario'
      );
    }
  }

  /**
   * Desactiva un usuario (soft delete)
   */
  async deleteStaff(userId: number): Promise<void> {
    try {
      await api.delete(`/auth/users/${userId}`);
    } catch (error: any) {
      console.error('Error deleting staff member:', error);
      throw new Error(
        error.response?.data?.detail || 'Error al desactivar el usuario'
      );
    }
  }

  /**
   * Obtiene la lista de roles disponibles
   */
  async getRoles(): Promise<Role[]> {
    try {
      const response = await api.get('/api/roles');
      return response.data;
    } catch (error: any) {
      console.error('Error fetching roles:', error);
      throw new Error(
        error.response?.data?.detail || 'Error al cargar los roles'
      );
    }
  }
}

export const staffService = new StaffService();

// Export convenience functions
export const getStaff = () => staffService.getStaff();
export const createStaff = (data: CreateStaffRequest) => staffService.createStaff(data);
export const updateStaff = (id: number, data: UpdateStaffRequest) => staffService.updateStaff(id, data);
export const deleteStaff = (id: number) => staffService.deleteStaff(id);
