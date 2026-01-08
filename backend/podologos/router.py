"""
Router de API para Podólogos
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from auth import get_current_user, User
from .models import PodologoCreate, PodologoUpdate, PodologoResponse, PodologoListItem
from . import service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/podologos",
    tags=["Podólogos"],
)


@router.get("", response_model=List[PodologoListItem])
async def get_podologos(
    activo_only: bool = Query(True, description="Filtrar solo podólogos activos"),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener lista de todos los podólogos
    
    - **activo_only**: Si es True, solo devuelve podólogos activos
    """
    try:
        podologos = await service.get_all_podologos(activo_only=activo_only)
        return podologos
    except Exception as e:
        logger.error(f"Error en GET /podologos: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener podólogos: {str(e)}")


@router.get("/disponibles", response_model=List[PodologoListItem])
async def get_podologos_disponibles(
    fecha: Optional[str] = Query(None, description="Fecha en formato YYYY-MM-DD"),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener podólogos disponibles
    
    - **fecha**: Fecha opcional para verificar disponibilidad
    """
    try:
        podologos = await service.get_podologos_disponibles(fecha=fecha)
        return podologos
    except Exception as e:
        logger.error(f"Error en GET /podologos/disponibles: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener podólogos disponibles: {str(e)}")


@router.get("/{podologo_id}", response_model=PodologoResponse)
async def get_podologo(
    podologo_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Obtener un podólogo por ID
    """
    try:
        podologo = await service.get_podologo_by_id(podologo_id)
        if not podologo:
            raise HTTPException(status_code=404, detail=f"Podólogo con ID {podologo_id} no encontrado")
        return podologo
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en GET /podologos/{podologo_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener podólogo: {str(e)}")


@router.post("", response_model=PodologoResponse, status_code=201)
async def create_podologo(
    podologo: PodologoCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Crear un nuevo podólogo
    
    Requiere rol de Administrador o Manager
    """
    # Verificar permisos
    if current_user.rol not in ["Admin", "Manager"]:
        raise HTTPException(
            status_code=403, 
            detail="No tienes permisos para crear podólogos"
        )
    
    try:
        nuevo_podologo = await service.create_podologo(podologo)
        return nuevo_podologo
    except Exception as e:
        logger.error(f"Error en POST /podologos: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear podólogo: {str(e)}")


@router.put("/{podologo_id}", response_model=PodologoResponse)
async def update_podologo(
    podologo_id: int,
    podologo: PodologoUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Actualizar un podólogo existente
    
    Requiere rol de Administrador o Manager
    """
    # Verificar permisos
    if current_user.rol not in ["Admin", "Manager"]:
        raise HTTPException(
            status_code=403, 
            detail="No tienes permisos para actualizar podólogos"
        )
    
    try:
        podologo_actualizado = await service.update_podologo(podologo_id, podologo)
        if not podologo_actualizado:
            raise HTTPException(status_code=404, detail=f"Podólogo con ID {podologo_id} no encontrado")
        return podologo_actualizado
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en PUT /podologos/{podologo_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar podólogo: {str(e)}")


@router.delete("/{podologo_id}", status_code=204)
async def delete_podologo(
    podologo_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Eliminar un podólogo (soft delete - marca como inactivo)
    
    Requiere rol de Administrador
    """
    # Verificar permisos
    if current_user.rol != "Admin":
        raise HTTPException(
            status_code=403, 
            detail="Solo administradores pueden eliminar podólogos"
        )
    
    try:
        eliminado = await service.delete_podologo(podologo_id)
        if not eliminado:
            raise HTTPException(status_code=404, detail=f"Podólogo con ID {podologo_id} no encontrado")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en DELETE /podologos/{podologo_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar podólogo: {str(e)}")
