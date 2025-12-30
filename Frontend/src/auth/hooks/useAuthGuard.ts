import { useMemo } from 'react';
import { useAuth } from '../AuthContext';

/**
 * Custom hook for role-based access control
 * 
 * @param requiredRoles - Array of roles that have access. If undefined, any authenticated user has access.
 * @returns Object with hasAccess boolean and user data
 * 
 * @example
 * ```tsx
 * const { hasAccess, user } = useAuthGuard(['Admin', 'Podologo']);
 * 
 * if (!hasAccess) {
 *   return <div>No tienes permisos</div>;
 * }
 * 
 * return <AdminPanel />;
 * ```
 */
export const useAuthGuard = (requiredRoles?: string[]) => {
  const { user, isAuthenticated } = useAuth();

  const hasAccess = useMemo(() => {
    // User must be authenticated
    if (!isAuthenticated || !user) {
      return false;
    }

    // If no specific roles required, any authenticated user has access
    if (!requiredRoles || requiredRoles.length === 0) {
      return true;
    }

    // Check if user's role is in the required roles list
    return requiredRoles.includes(user.rol);
  }, [user, isAuthenticated, requiredRoles]);

  return {
    hasAccess,
    user,
    isAuthenticated,
  };
};

export default useAuthGuard;
