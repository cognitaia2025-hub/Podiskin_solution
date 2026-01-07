"""
Router de Permisos Granulares
==============================
Endpoints para gestión de permisos personalizados
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import logging
import psycopg
from psycopg.rows import dict_row

from .models import User
from .middleware import get_current_user
from .permission_models import (
    UserModulePermissionCreate,
    UserModulePermissionUpdate,
    UserPatientAccessCreate,
    UserPatientAccessUpdate,
    PermissionsResponse,
    PatientAccessCheck,
    AccessLevel
)
from .granular_permissions import (
    get_effective_permissions,
    check_patient_access,
    grant_patient_access,
    revoke_patient_access
)
from .database import CONNINFO  # ✅ Importar connection string

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/permissions", tags=["Permisos Granulares"])

# ========================================================================
# HELPER PARA CONEXIÓN A BD (mismo patrón que patients_router.py)
# ========================================================================

async def get_db_connection():
    """
    Obtiene una conexión a la base de datos.
    Usa el mismo CONNINFO que auth/database.py
    """
    return await psycopg.AsyncConnection.connect(CONNINFO)

# ========================================================================
# ENDPOINTS DE CONSULTA
# ========================================================================

@router.get("/me", response_model=PermissionsResponse)
async def get_my_permissions(
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene permisos completos del usuario actual.
    
    Incluye:
    - Permisos base del rol
    - Permisos personalizados
    - Permisos efectivos (combinación)
    - Acceso a pacientes específicos
    """
    conn = None
    try:
        conn = await get_db_connection()
        permissions = await get_effective_permissions(
            conn,
            current_user.id,
            current_user.rol
        )
        return permissions
    finally:
        if conn:
            await conn.close()

@router.get("/check-patient/{patient_id}", response_model=PatientAccessCheck)
async def check_my_patient_access(
    patient_id: int,
    required_level: AccessLevel = AccessLevel.READ,
    current_user: User = Depends(get_current_user)
):
    """
    Verifica si el usuario actual tiene acceso a un paciente específico.
    
    Query params:
    - required_level: Nivel de acceso requerido (read, write, full)
    """
    conn = None
    try:
        conn = await get_db_connection()
        access_check = await check_patient_access(
            conn,
            current_user.id,
            patient_id,
            required_level
        )
        return access_check
    finally:
        if conn:
            await conn.close()

# ========================================================================
# ENDPOINTS DE ADMINISTRACIÓN (Solo Admin)
# ========================================================================

@router.post("/grant-patient-access")
async def grant_access_to_patient(
    access_request: UserPatientAccessCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Otorga acceso de un usuario a un paciente específico.
    
    **Solo Admin puede otorgar accesos.**
    """
    if current_user.rol != 'Admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Admin puede otorgar accesos a pacientes"
        )
    
    conn = None
    try:
        conn = await get_db_connection()
        access = await grant_patient_access(
            conn,
            access_request.user_id,
            access_request.patient_id,
            access_request.access_level,
            current_user.id,
            access_request.expires_at,
            access_request.notes
        )
        
        logger.info(
            f"Admin {current_user.nombre_usuario} otorgó acceso {access_request.access_level} "
            f"de usuario {access_request.user_id} a paciente {access_request.patient_id}"
        )
        
        return {
            "message": "Acceso otorgado correctamente",
            "access": access
        }
    finally:
        if conn:
            await conn.close()

@router.delete("/revoke-patient-access/{user_id}/{patient_id}")
async def revoke_access_to_patient(
    user_id: int,
    patient_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Revoca acceso de un usuario a un paciente.
    
    **Solo Admin puede revocar accesos.**
    """
    if current_user.rol != 'Admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Admin puede revocar accesos"
        )
    
    conn = None
    try:
        conn = await get_db_connection()
        revoked = await revoke_patient_access(conn, user_id, patient_id)
        
        if not revoked:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró acceso para revocar"
            )
        
        logger.info(
            f"Admin {current_user.nombre_usuario} revocó acceso "
            f"de usuario {user_id} a paciente {patient_id}"
        )
        
        return {"message": "Acceso revocado correctamente"}
    finally:
        if conn:
            await conn.close()

@router.get("/user/{user_id}", response_model=PermissionsResponse)
async def get_user_permissions(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene permisos de cualquier usuario.
    
    **Solo Admin puede consultar permisos de otros usuarios.**
    """
    if current_user.rol != 'Admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Admin puede consultar permisos de otros usuarios"
        )
    
    conn = None
    try:
        conn = await get_db_connection()
        
        # Obtener rol del usuario
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT rol FROM usuarios WHERE id = $1",
                (user_id,)
            )
            user = await cur.fetchone()
        
        await conn.rollback()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        permissions = await get_effective_permissions(
            conn,
            user_id,
            user['rol']
        )
        return permissions
    finally:
        if conn:
            await conn.close()
