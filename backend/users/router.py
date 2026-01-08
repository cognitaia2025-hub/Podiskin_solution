"""
Users Router
============
REST API endpoints for user management (CRUD operations).
Separated from auth router for clean architecture.

Prefix: /api/users
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from auth.middleware import get_current_user
from auth.jwt_handler import get_password_hash
from auth.database import (
    get_all_users,
    get_user_by_id,
    create_user,
    update_user,
    delete_user
)

router = APIRouter(
    prefix="/users",
    tags=["User Management"],
    responses={404: {"description": "Not found"}},
)


# ============================================================================
# MODELS
# ============================================================================

class UserListResponse(BaseModel):
    """Response model for user list"""
    id: int
    nombre_usuario: str
    nombre_completo: str
    email: str
    rol: Optional[str] = None
    id_rol: Optional[int] = None
    activo: bool
    ultimo_login: Optional[datetime] = None
    fecha_registro: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    """Request model for creating a new user"""
    nombre_usuario: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    nombre_completo: str = Field(..., min_length=3)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    rol: str = Field(..., pattern=r'^(Admin|Podologo|Recepcionista|Asistente)$')
    cedula_profesional: Optional[str] = Field(None, description="Requerido solo para Podólogos")


class UserUpdateRequest(BaseModel):
    """Request model for updating a user"""
    nombre_completo: Optional[str] = Field(None, min_length=3)
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    rol: Optional[str] = Field(None, pattern=r'^(Admin|Podologo|Recepcionista|Asistente)$')
    activo: Optional[bool] = None


# ============================================================================
# HELPER FUNCTION
# ============================================================================

def require_admin(current_user):
    """Verify current user is admin, raise 403 if not."""
    if current_user.rol != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden realizar esta operación"
        )


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get(
    "",
    response_model=List[UserListResponse],
    summary="Listar usuarios",
    description="Obtiene la lista de todos los usuarios del sistema. Solo administradores.",
)
async def list_users(
    activo_only: bool = True,
    current_user=Depends(get_current_user)
):
    """Lista todos los usuarios del sistema."""
    require_admin(current_user)
    
    users = await get_all_users(activo_only=activo_only)
    return users


@router.post(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario en el sistema. Solo administradores.",
)
async def create_user_endpoint(
    user_data: UserCreateRequest,
    current_user=Depends(get_current_user)
):
    """Crea un nuevo usuario."""
    require_admin(current_user)
    
    # Validar que si es Podologo, tenga cedula_profesional
    if user_data.rol == "Podologo" and not user_data.cedula_profesional:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cédula profesional es requerida para podólogos"
        )
    
    # Hash de la contraseña
    password_hash = get_password_hash(user_data.password)
    
    # Crear usuario
    new_user = await create_user(
        nombre_usuario=user_data.nombre_usuario,
        password_hash=password_hash,
        nombre_completo=user_data.nombre_completo,
        email=user_data.email,
        rol=user_data.rol,
        creado_por=current_user.id
    )
    
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear usuario. El nombre de usuario o email puede estar duplicado."
        )
    
    # Si es Podologo, crear registro en tabla podologos
    if user_data.rol == "Podologo" and user_data.cedula_profesional:
        from podologos.service import create_podologo_from_user
        try:
            await create_podologo_from_user(
                id_usuario=new_user['id'],
                cedula_profesional=user_data.cedula_profesional,
                nombre_completo=user_data.nombre_completo,
                email=user_data.email
            )
        except Exception as e:
            # Log error pero no fallar la creación del usuario
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating podologo record: {e}")
    
    return new_user


@router.get(
    "/{user_id}",
    response_model=UserListResponse,
    summary="Obtener usuario",
    description="Obtiene un usuario por su ID. Solo administradores.",
)
async def get_user_endpoint(
    user_id: int,
    current_user=Depends(get_current_user)
):
    """Obtiene un usuario por ID."""
    require_admin(current_user)
    
    user = await get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user


@router.put(
    "/{user_id}",
    response_model=UserListResponse,
    summary="Actualizar usuario",
    description="Actualiza un usuario existente. Solo administradores.",
)
async def update_user_endpoint(
    user_id: int,
    user_data: UserUpdateRequest,
    current_user=Depends(get_current_user)
):
    """Actualiza un usuario existente."""
    require_admin(current_user)
    
    updated_user = await update_user(
        user_id=user_id,
        nombre_completo=user_data.nombre_completo,
        email=user_data.email,
        rol=user_data.rol,
        activo=user_data.activo
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return updated_user


@router.delete(
    "/{user_id}",
    summary="Desactivar usuario",
    description="Desactiva un usuario (soft delete). Solo administradores.",
)
async def delete_user_endpoint(
    user_id: int,
    current_user=Depends(get_current_user)
):
    """Desactiva un usuario (soft delete)."""
    require_admin(current_user)
    
    # No permitir que un admin se desactive a sí mismo
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta"
        )
    
    success = await delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return {"message": "Usuario desactivado correctamente", "id": user_id}
