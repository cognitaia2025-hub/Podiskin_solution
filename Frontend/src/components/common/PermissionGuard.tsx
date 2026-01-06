/**
 * Componente PermissionGuard
 * ==========================
 * Protege contenido que requiere permisos específicos
 */

import React from 'react';
import { usePermissions } from '../../hooks/usePermissions';
import { AlertCircle } from 'lucide-react';

interface PermissionGuardProps {
  module: string;
  action: 'read' | 'write';
  children: React.ReactNode;
  fallback?: React.ReactNode;
  hideIfNoPermission?: boolean;
}

/**
 * Componente que muestra contenido solo si el usuario tiene los permisos necesarios
 */
export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  module,
  action,
  children,
  fallback,
  hideIfNoPermission = false,
}) => {
  const { hasPermission, isLoading } = usePermissions();

  // Mientras carga, no mostrar nada
  if (isLoading) {
    return null;
  }

  // Verificar permiso
  const hasRequiredPermission = hasPermission(module, action);

  if (!hasRequiredPermission) {
    // Si se solicita ocultar, no mostrar nada
    if (hideIfNoPermission) {
      return null;
    }

    // Si hay fallback personalizado, mostrarlo
    if (fallback) {
      return <>{fallback}</>;
    }

    // Mostrar mensaje de permiso denegado
    return (
      <div className="flex items-center justify-center p-8 bg-red-50 rounded-lg border border-red-200">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-red-900 mb-2">
            Acceso Denegado
          </h3>
          <p className="text-red-700">
            No tienes permisos para {action === 'read' ? 'ver' : 'modificar'} esta sección
          </p>
        </div>
      </div>
    );
  }

  // Si tiene permiso, mostrar el contenido
  return <>{children}</>;
};

/**
 * HOC para proteger componentes completos
 */
export const withPermission = (
  Component: React.ComponentType<any>,
  module: string,
  action: 'read' | 'write'
) => {
  return (props: any) => (
    <PermissionGuard module={module} action={action}>
      <Component {...props} />
    </PermissionGuard>
  );
};
