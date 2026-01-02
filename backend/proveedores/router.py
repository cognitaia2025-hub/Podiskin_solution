"""
Router de Proveedores
======================
Endpoints REST para gestión de proveedores.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from .service import proveedores_service

router = APIRouter(
    prefix="/proveedores",
    tags=["Proveedores"],
    responses={404: {"description": "No encontrado"}},
)


class ProveedorBase(BaseModel):
    nombre_comercial: str = Field(..., min_length=2, max_length=100)
    razon_social: Optional[str] = None
    rfc: Optional[str] = Field(None, max_length=13)
    tipo_proveedor: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    codigo_postal: Optional[str] = None
    contacto_principal: Optional[str] = None
    dias_credito: Optional[int] = 0
    notas: Optional[str] = None


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    nombre_comercial: Optional[str] = None
    razon_social: Optional[str] = None
    rfc: Optional[str] = None
    tipo_proveedor: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    codigo_postal: Optional[str] = None
    contacto_principal: Optional[str] = None
    dias_credito: Optional[int] = None
    activo: Optional[bool] = None
    notas: Optional[str] = None


@router.get("/")
async def listar_proveedores(activo: Optional[bool] = None):
    """Lista todos los proveedores."""
    return proveedores_service.get_all(activo=activo)


@router.get("/{id}")
async def obtener_proveedor(id: int):
    """Obtiene un proveedor por ID."""
    proveedor = proveedores_service.get_by_id(id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return proveedor


@router.post("/", status_code=201)
async def crear_proveedor(proveedor: ProveedorCreate):
    """Crea un nuevo proveedor."""
    try:
        return proveedores_service.create(proveedor.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{id}")
async def actualizar_proveedor(id: int, proveedor: ProveedorUpdate):
    """Actualiza un proveedor existente."""
    data = {k: v for k, v in proveedor.dict().items() if v is not None}
    resultado = proveedores_service.update(id, data)
    if not resultado:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return resultado


@router.delete("/{id}")
async def eliminar_proveedor(id: int):
    """Elimina un proveedor (soft delete)."""
    if not proveedores_service.delete(id):
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return {"message": "Proveedor eliminado", "id": id}
