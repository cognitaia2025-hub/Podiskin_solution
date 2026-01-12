"""Router de Horarios - Endpoints REST API."""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from .models import HorarioCreate, HorarioUpdate, HorarioResponse
from .service import horarios_service
from auth.middleware import get_current_user

router = APIRouter(prefix="/horarios", tags=["Horarios"])

@router.get("", response_model=List[HorarioResponse])
async def get_horarios(
    id_podologo: Optional[int] = None,
    activo: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene todos los horarios de trabajo.
    
    **Filtros opcionales:**
    - id_podologo: Filtrar por podólogo específico
    - activo: Filtrar por estado (true/false)
    """
    try:
        horarios = horarios_service.get_all(id_podologo=id_podologo, activo=activo)
        return horarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{horario_id}", response_model=HorarioResponse)
async def get_horario(
    horario_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Obtiene un horario específico por ID."""
    horario = horarios_service.get_by_id(horario_id)
    if not horario:
        raise HTTPException(status_code=404, detail=f"Horario con ID {horario_id} no encontrado")
    return horario

@router.post("", response_model=HorarioResponse, status_code=status.HTTP_201_CREATED)
async def create_horario(
    horario: HorarioCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Crea un nuevo horario de trabajo.
    
    **Validaciones:**
    - El podólogo debe existir y estar activo
    - La hora de fin debe ser posterior a la hora de inicio
    - Solo usuarios con rol 'Admin' pueden crear horarios
    """
    # Verificar que el usuario es Admin
    if current_user.get("rol") != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden crear horarios"
        )
    
    try:
        horario_dict = horario.model_dump()
        nuevo_horario = horarios_service.create(
            horario_data=horario_dict,
            creado_por=current_user["id"]
        )
        return nuevo_horario
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{horario_id}", response_model=HorarioResponse)
async def update_horario(
    horario_id: int,
    horario: HorarioUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Actualiza un horario existente.
    
    **Restricciones:**
    - Solo usuarios con rol 'Admin' pueden actualizar horarios
    """
    # Verificar que el usuario es Admin
    if current_user.get("rol") != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden actualizar horarios"
        )
    
    try:
        updates = {k: v for k, v in horario.model_dump().items() if v is not None}
        horario_actualizado = horarios_service.update(horario_id, updates)
        return horario_actualizado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{horario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_horario(
    horario_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Desactiva un horario (soft delete).
    
    **Restricciones:**
    - Solo usuarios con rol 'Admin' pueden eliminar horarios
    """
    # Verificar que el usuario es Admin
    if current_user.get("rol") != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden eliminar horarios"
        )
    
    try:
        success = horarios_service.delete(horario_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Horario con ID {horario_id} no encontrado")
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
