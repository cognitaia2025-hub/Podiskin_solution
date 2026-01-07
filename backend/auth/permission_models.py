"""
Modelos de Permisos Granulares
===============================
Modelos para gestión de permisos personalizados por usuario
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class AccessLevel(str, Enum):
    """Niveles de acceso a pacientes"""
    READ = "read"
    WRITE = "write"
    FULL = "full"

class UserModulePermission(BaseModel):
    """Permiso de módulo personalizado para usuario"""
    id: Optional[int] = None
    user_id: int
    module_name: str = Field(..., max_length=50)
    can_read: bool = False
    can_write: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserModulePermissionCreate(BaseModel):
    """Request para crear permiso de módulo"""
    user_id: int
    module_name: str
    can_read: bool = True
    can_write: bool = False

class UserModulePermissionUpdate(BaseModel):
    """Request para actualizar permiso de módulo"""
    can_read: Optional[bool] = None
    can_write: Optional[bool] = None

class UserPatientAccess(BaseModel):
    """Acceso de usuario a paciente específico"""
    id: Optional[int] = None
    user_id: int
    patient_id: int
    access_level: AccessLevel = AccessLevel.READ
    granted_by: Optional[int] = None
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    notes: Optional[str] = None

class UserPatientAccessCreate(BaseModel):
    """Request para otorgar acceso a paciente"""
    user_id: int
    patient_id: int
    access_level: AccessLevel = AccessLevel.READ
    expires_at: Optional[datetime] = None
    notes: Optional[str] = None

class UserPatientAccessUpdate(BaseModel):
    """Request para actualizar acceso a paciente"""
    access_level: Optional[AccessLevel] = None
    expires_at: Optional[datetime] = None
    notes: Optional[str] = None

class PermissionsResponse(BaseModel):
    """Respuesta con permisos completos del usuario"""
    # Permisos de módulos (heredados del rol)
    role_permissions: dict
    
    # Permisos personalizados (sobrescriben los del rol)
    custom_permissions: List[UserModulePermission] = []
    
    # Permisos finales (combinación de rol + custom)
    effective_permissions: dict
    
    # Acceso a pacientes específicos
    patient_access: List[int] = []  # IDs de pacientes accesibles

class PatientAccessCheck(BaseModel):
    """Resultado de verificación de acceso a paciente"""
    has_access: bool
    access_level: Optional[AccessLevel] = None
    reason: str
