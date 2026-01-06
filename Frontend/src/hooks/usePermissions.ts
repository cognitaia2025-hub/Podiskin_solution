/**
 * Hook para gestión de permisos de usuario
 * =========================================
 * Permite verificar permisos del usuario actual para diferentes módulos
 */

import { useContext } from 'react';
import { AuthContext } from '../auth/AuthContext';
import type { UserPermissions, Permission } from '../types/billing';

export interface PermissionCheck {
  hasPermission: (module: string, action: 'read' | 'write') => boolean;
  permissions: UserPermissions | null;
  canRead: (module: string) => boolean;
  canWrite: (module: string) => boolean;
  isAdmin: boolean;
  isLoading: boolean;
}

/**
 * Hook para verificar permisos del usuario actual
 */
export const usePermissions = (): PermissionCheck => {
  const { user } = useContext(AuthContext);

  // Obtener permisos del usuario (asumiendo que vienen en user.permissions)
  const permissions = (user?.permissions as UserPermissions) || null;

  /**
   * Verifica si el usuario tiene un permiso específico
   */
  const hasPermission = (module: string, action: 'read' | 'write'): boolean => {
    if (!permissions) return false;

    const modulePermissions = permissions[module as keyof UserPermissions] as Permission | undefined;
    
    if (!modulePermissions) return false;

    return modulePermissions[action] === true;
  };

  /**
   * Atajo para verificar permiso de lectura
   */
  const canRead = (module: string): boolean => {
    return hasPermission(module, 'read');
  };

  /**
   * Atajo para verificar permiso de escritura
   */
  const canWrite = (module: string): boolean => {
    return hasPermission(module, 'write');
  };

  /**
   * Verifica si el usuario es administrador
   */
  const isAdmin = hasPermission('administracion', 'read');

  return {
    hasPermission,
    permissions,
    canRead,
    canWrite,
    isAdmin,
    isLoading: !user,
  };
};
