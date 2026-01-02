"""
Router de Roles
================
Endpoints REST para gestión de roles.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from .service import roles_service

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    responses={404: {"description": "No encontrado"}},
)


# ============================================================================
# MODELOS
# ============================================================================


class RolBase(BaseModel):
    nombre_rol: str = Field(..., min_length=2, max_length=50)
    descripcion: Optional[str] = None
    permisos: Optional[Dict[str, Any]] = None


class RolCreate(RolBase):
    pass


class RolUpdate(BaseModel):
    nombre_rol: Optional[str] = Field(None, min_length=2, max_length=50)
    descripcion: Optional[str] = None
    permisos: Optional[Dict[str, Any]] = None
    activo: Optional[bool] = None


class RolResponse(BaseModel):
    id: int
    nombre_rol: str
    descripcion: Optional[str]
    permisos: Optional[Dict[str, Any]]
    activo: bool
    fecha_creacion: Optional[str]


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get("/")
async def listar_roles():
    """
    Lista todos los roles del sistema.

    **Uso:**
    ```
    GET /api/roles
    ```
    """
    roles = roles_service.get_all()
    # Convertir datetime a string
    for rol in roles:
        if rol.get("fecha_creacion"):
            rol["fecha_creacion"] = str(rol["fecha_creacion"])
    return roles


@router.get("/{id}", response_model=RolResponse)
async def obtener_rol(id: int):
    """
    Obtiene un rol por su ID.

    **Uso:**
    ```
    GET /api/roles/1
    ```
    """
    rol = roles_service.get_by_id(id)
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return rol


@router.post("/", response_model=RolResponse, status_code=201)
async def crear_rol(rol: RolCreate):
    """
    Crea un nuevo rol.

    **Ejemplo:**
    ```json
    POST /api/roles
    {
        "nombre_rol": "Supervisor",
        "descripcion": "Supervisa operaciones",
        "permisos": {"lectura": true, "reportes": true}
    }
    ```
    """
    try:
        nuevo_rol = roles_service.create(
            nombre_rol=rol.nombre_rol,
            descripcion=rol.descripcion,
            permisos=rol.permisos,
        )
        return nuevo_rol
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{id}", response_model=RolResponse)
async def actualizar_rol(id: int, rol: RolUpdate):
    """
    Actualiza un rol existente.

    Solo se actualizan los campos proporcionados.
    """
    rol_actualizado = roles_service.update(
        id=id,
        nombre_rol=rol.nombre_rol,
        descripcion=rol.descripcion,
        permisos=rol.permisos,
        activo=rol.activo,
    )
    if not rol_actualizado:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return rol_actualizado


@router.delete("/{id}")
async def eliminar_rol(id: int):
    """
    Elimina un rol (soft delete).

    El rol se marca como inactivo pero no se borra.
    """
    resultado = roles_service.delete(id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return {"message": "Rol eliminado correctamente", "id": id}
