/**
 * Hook para gestión de permisos de usuario
 * =========================================
 * Permite verificar permisos del usuario actual para diferentes módulos
 */

import { useContext, useMemo } from 'react';
import { AuthContext } from '../auth/AuthContext';
import type { UserPermissions, Permission } from '../types/billing';
import { PERMISSION_TEMPLATES } from '../types/billing';

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
  const authContext = useContext(AuthContext);
  const user = authContext?.user;

  // Calcular permisos basados en el rol del usuario
  const permissions = useMemo((): UserPermissions | null => {
    if (!user?.rol) return null;

    // Si el usuario tiene permisos explícitos, usarlos
    if (user.permissions) {
      return user.permissions;
    }

    // Buscar template de permisos según el rol
    const roleLowerCase = user.rol.toLowerCase();
    const template = PERMISSION_TEMPLATES.find(
      (t) => t.name === roleLowerCase || t.label === user.rol
    );

    if (template) {
      return template.permissions;
    }

    // Si no hay template, retornar permisos vacíos
    console.warn(`No se encontró template de permisos para rol: ${user.rol}`);
    return null;
  }, [user?.rol, user?.permissions]);

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
  const isAdmin = user?.rol === 'Admin' || hasPermission('administracion', 'read');

  return {
    hasPermission,
    permissions,
    canRead,
    canWrite,
    isAdmin,
    isLoading: !user,
  };
};
