from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from catalog.models import (
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
    TIPOS_DISPONIBLES,
    CATEGORIAS_DISPONIBLES,
)
from catalog import service

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=List[ServiceResponse])
async def list_services(
    tipo: Optional[str] = Query(
        None, description="Filtrar por tipo: servicio o tratamiento"
    ),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    orden: str = Query(
        "nombre", description="Ordenar por: id, nombre, precio, duracion_minutos"
    ),
    direccion: str = Query("asc", description="Dirección: asc o desc"),
):
    """Lista servicios con filtros y ordenamiento."""
    return await service.get_services(
        tipo=tipo, categoria=categoria, activo=activo, orden=orden, direccion=direccion
    )


@router.get("/tipos", response_model=List[str])
async def get_tipos():
    """Obtiene los tipos disponibles."""
    return TIPOS_DISPONIBLES


@router.get("/categorias", response_model=List[str])
async def get_categorias():
    """Obtiene las categorías disponibles."""
    return CATEGORIAS_DISPONIBLES


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: int):
    return await service.get_service(service_id)


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(service_in: ServiceCreate):
    return await service.create_service(service_in)


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(service_id: int, service_in: ServiceUpdate):
    return await service.update_service(service_id, service_in)


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(service_id: int):
    await service.delete_service(service_id)
    return None
