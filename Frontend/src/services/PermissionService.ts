export type PermissionLevel = 'view_free_busy' | 'view_details' | 'edit' | 'admin';

export interface UserPermission {
    userId: string;
    resourceId: string; // Doctor ID or Calendar ID
    level: PermissionLevel;
}

// Mock permissions service
export const getPermissions = (userId: string): UserPermission[] => {
    // In a real app, this would fetch from API
    // Mocking current user having full access to everything for demo purposes
    return [
        { userId: 'current-user', resourceId: '1', level: 'admin' }, // Full access to Dr. Alejandro
        { userId: 'current-user', resourceId: '2', level: 'view_details' }, // Can view details of Dra. María
        { userId: 'current-user', resourceId: '3', level: 'view_free_busy' }, // Can only see free/busy of Dr. Carlos
    ];
};

export const hasPermission = (permissions: UserPermission[], resourceId: string, requiredLevel: PermissionLevel): boolean => {
    const permission = permissions.find(p => p.resourceId === resourceId);
    if (!permission) return false;

    const levels = ['view_free_busy', 'view_details', 'edit', 'admin'];
    return levels.indexOf(permission.level) >= levels.indexOf(requiredLevel);
};
