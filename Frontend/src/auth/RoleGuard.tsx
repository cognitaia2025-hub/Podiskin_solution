import React from 'react';
import { useAuth } from './AuthContext';
import { ShieldOff } from 'lucide-react';

interface RoleGuardProps {
  allowedRoles: string[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
  redirectTo?: string;
}

const RoleGuard: React.FC<RoleGuardProps> = ({ 
  allowedRoles, 
  children, 
  fallback,
}) => {
  const { user, isAuthenticated } = useAuth();

  // If not authenticated, don't render anything (ProtectedRoute handles this)
  if (!isAuthenticated || !user) {
    return null;
  }

  // Check if user has required role
  const hasAccess = allowedRoles.includes(user.rol);

  if (!hasAccess) {
    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full">
          <div className="text-center">
            <ShieldOff className="mx-auto h-16 w-16 text-red-500 mb-4" aria-hidden="true" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Acceso denegado
            </h2>
            <p className="text-gray-600 mb-6">
              No tienes permisos para acceder a este contenido.
            </p>
            <p className="text-sm text-gray-500">
              Tu rol: <strong>{user.rol}</strong>
            </p>
            <p className="text-sm text-gray-500">
              Roles requeridos: <strong>{allowedRoles.join(', ')}</strong>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default RoleGuard;
