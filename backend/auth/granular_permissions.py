"""
Servicio de Permisos Granulares
================================
Gestión de permisos personalizados y acceso a pacientes
"""

import asyncpg
from typing import List, Dict, Any, Optional
from datetime import datetime

from .permission_models import (
    UserModulePermission,
    UserPatientAccess,
    AccessLevel,
    PermissionsResponse,
    PatientAccessCheck
)
from .router import calculate_permissions_for_role

async def get_user_custom_permissions(
    conn: asyncpg.Connection,
    user_id: int
) -> List[UserModulePermission]:
    """
    Obtiene permisos personalizados de un usuario.
    
    Args:
        conn: Conexión a BD
        user_id: ID del usuario
        
    Returns:
        Lista de permisos personalizados
    """
    query = """
        SELECT *
        FROM user_permissions
        WHERE user_id = $1
        ORDER BY module_name
    """
    
    rows = await conn.fetch(query, user_id)
    
    return [
        UserModulePermission(**dict(row))
        for row in rows
    ]

async def get_user_patient_access(
    conn: asyncpg.Connection,
    user_id: int
) -> List[int]:
    """
    Obtiene IDs de pacientes a los que el usuario tiene acceso.
    
    Args:
        conn: Conexión a BD
        user_id: ID del usuario
        
    Returns:
        Lista de IDs de pacientes accesibles
    """
    query = """
        SELECT patient_id
        FROM user_patient_access
        WHERE user_id = $1
            AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
    """
    
    rows = await conn.fetch(query, user_id)
    
    return [row['patient_id'] for row in rows]

async def get_effective_permissions(
    conn: asyncpg.Connection,
    user_id: int,
    user_role: str
) -> PermissionsResponse:
    """
    Calcula permisos efectivos del usuario.
    
    Combina:
    1. Permisos base del rol
    2. Permisos personalizados (sobrescriben los del rol)
    3. Acceso a pacientes específicos
    
    Args:
        conn: Conexión a BD
        user_id: ID del usuario
        user_role: Rol del usuario
        
    Returns:
        PermissionsResponse con permisos completos
    """
    # 1. Obtener permisos base del rol
    role_permissions = calculate_permissions_for_role(user_role)
    
    # 2. Obtener permisos personalizados
    custom_permissions = await get_user_custom_permissions(conn, user_id)
    
    # 3. Combinar permisos (custom sobrescribe rol)
    effective_permissions = role_permissions.copy()
    
    for custom_perm in custom_permissions:
        if custom_perm.module_name in effective_permissions:
            effective_permissions[custom_perm.module_name] = {
                "read": custom_perm.can_read,
                "write": custom_perm.can_write
            }
    
    # 4. Obtener acceso a pacientes
    patient_access = await get_user_patient_access(conn, user_id)
    
    return PermissionsResponse(
        role_permissions=role_permissions,
        custom_permissions=custom_permissions,
        effective_permissions=effective_permissions,
        patient_access=patient_access
    )

async def check_patient_access(
    conn: asyncpg.Connection,
    user_id: int,
    patient_id: int,
    required_level: AccessLevel = AccessLevel.READ
) -> PatientAccessCheck:
    """
    Verifica si un usuario tiene acceso a un paciente específico.
    
    Reglas:
    1. Admin siempre tiene acceso FULL
    2. Si tiene acceso específico otorgado, verificar nivel
    3. Si no, denegar acceso
    
    Args:
        conn: Conexión a BD
        user_id: ID del usuario
        patient_id: ID del paciente
        required_level: Nivel de acceso requerido
        
    Returns:
        PatientAccessCheck con resultado
    """
    # Obtener información del usuario
    user_query = "SELECT rol FROM usuarios WHERE id = $1"
    user = await conn.fetchrow(user_query, user_id)
    
    if not user:
        return PatientAccessCheck(
            has_access=False,
            reason="Usuario no encontrado"
        )
    
    # Admin siempre tiene acceso total
    if user['rol'] == 'Admin':
        return PatientAccessCheck(
            has_access=True,
            access_level=AccessLevel.FULL,
            reason="Usuario es Admin (acceso total)"
        )
    
    # Verificar acceso específico
    access_query = """
        SELECT access_level
        FROM user_patient_access
        WHERE user_id = $1
            AND patient_id = $2
            AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
    """
    
    access = await conn.fetchrow(access_query, user_id, patient_id)
    
    if not access:
        return PatientAccessCheck(
            has_access=False,
            reason="Sin acceso otorgado a este paciente"
        )
    
    user_level = AccessLevel(access['access_level'])
    
    # Verificar nivel de acceso
    level_hierarchy = {
        AccessLevel.READ: 1,
        AccessLevel.WRITE: 2,
        AccessLevel.FULL: 3
    }
    
    has_sufficient_access = level_hierarchy[user_level] >= level_hierarchy[required_level]
    
    return PatientAccessCheck(
        has_access=has_sufficient_access,
        access_level=user_level,
        reason=f"Acceso {user_level.value}" if has_sufficient_access 
               else f"Requiere nivel {required_level.value}, tiene {user_level.value}"
    )

async def grant_patient_access(
    conn: asyncpg.Connection,
    user_id: int,
    patient_id: int,
    access_level: AccessLevel,
    granted_by: int,
    expires_at: Optional[datetime] = None,
    notes: Optional[str] = None
) -> UserPatientAccess:
    """
    Otorga acceso de un usuario a un paciente.
    
    Args:
        conn: Conexión a BD
        user_id: ID del usuario
        patient_id: ID del paciente
        access_level: Nivel de acceso a otorgar
        granted_by: ID del usuario que otorga el acceso
        expires_at: Fecha de expiración (opcional)
        notes: Notas adicionales
        
    Returns:
        UserPatientAccess creado
    """
    query = """
        INSERT INTO user_patient_access 
            (user_id, patient_id, access_level, granted_by, expires_at, notes)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (user_id, patient_id) 
        DO UPDATE SET
            access_level = EXCLUDED.access_level,
            granted_by = EXCLUDED.granted_by,
            granted_at = CURRENT_TIMESTAMP,
            expires_at = EXCLUDED.expires_at,
            notes = EXCLUDED.notes
        RETURNING *
    """
    
    row = await conn.fetchrow(
        query,
        user_id,
        patient_id,
        access_level.value,
        granted_by,
        expires_at,
        notes
    )
    
    return UserPatientAccess(**dict(row))

async def revoke_patient_access(
    conn: asyncpg.Connection,
    user_id: int,
    patient_id: int
) -> bool:
    """
    Revoca acceso de un usuario a un paciente.
    
    Args:
        conn: Conexión a BD
        user_id: ID del usuario
        patient_id: ID del paciente
        
    Returns:
        True si se revocó, False si no existía
    """
    query = """
        DELETE FROM user_patient_access
        WHERE user_id = $1 AND patient_id = $2
        RETURNING id
    """
    
    result = await conn.fetchrow(query, user_id, patient_id)
    
    return result is not None
