from typing import List, Optional
from fastapi import HTTPException
from db import database
from catalog.models import ServiceCreate, ServiceUpdate, ServiceResponse


async def get_services(
    tipo: Optional[str] = None,
    categoria: Optional[str] = None,
    activo: Optional[bool] = None,
    orden: str = "id",
    direccion: str = "asc"
) -> List[ServiceResponse]:
    """Obtiene servicios con filtros y ordenamiento."""
    
    # Validar ordenamiento
    valid_orders = ["id", "nombre", "precio", "duracion_minutos"]
    if orden not in valid_orders:
        orden = "id"
    if direccion.lower() not in ["asc", "desc"]:
        direccion = "asc"
    
    # Construir query con filtros
    conditions = []
    values = {}
    
    if tipo:
        conditions.append("tipo = :tipo")
        values["tipo"] = tipo
    if categoria:
        conditions.append("categoria = :categoria")
        values["categoria"] = categoria
    if activo is not None:
        conditions.append("activo = :activo")
        values["activo"] = activo
    
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    
    query = f"""
        SELECT id, nombre, descripcion, precio, duracion_minutos, tipo, categoria, activo 
        FROM catalogo_servicios 
        {where_clause}
        ORDER BY {orden} {direccion.upper()}
    """
    
    rows = await database.fetch_all(query, values=values)
    return [ServiceResponse(**dict(row)) for row in rows]


async def get_service(service_id: int) -> ServiceResponse:
    query = "SELECT id, nombre, descripcion, precio, duracion_minutos, tipo, categoria, activo FROM catalogo_servicios WHERE id = :id"
    row = await database.fetch_one(query, values={"id": service_id})
    if not row:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return ServiceResponse(**dict(row))


async def create_service(service: ServiceCreate) -> ServiceResponse:
    query = """
        INSERT INTO catalogo_servicios (nombre, descripcion, precio, duracion_minutos, tipo, categoria, activo)
        VALUES (:nombre, :descripcion, :precio, :duracion_minutos, :tipo, :categoria, :activo)
        RETURNING id, nombre, descripcion, precio, duracion_minutos, tipo, categoria, activo
    """
    values = service.model_dump()
    row = await database.fetch_one(query, values=values)
    return ServiceResponse(**dict(row))


async def update_service(service_id: int, service: ServiceUpdate) -> ServiceResponse:
    # Obtener valores actuales
    current = await get_service(service_id)
    
    # Mezclar con nuevos valores (solo los que no son None)
    update_data = service.model_dump(exclude_unset=True)
    current_data = current.model_dump()
    current_data.update(update_data)
    
    query = """
        UPDATE catalogo_servicios
        SET nombre = :nombre, descripcion = :descripcion, precio = :precio, 
            duracion_minutos = :duracion_minutos, tipo = :tipo, categoria = :categoria, activo = :activo
        WHERE id = :id
        RETURNING id, nombre, descripcion, precio, duracion_minutos, tipo, categoria, activo
    """
    current_data["id"] = service_id
    row = await database.fetch_one(query, values=current_data)
    if not row:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return ServiceResponse(**dict(row))


async def delete_service(service_id: int) -> None:
    query = "DELETE FROM catalogo_servicios WHERE id = :id"
    result = await database.execute(query, values={"id": service_id})
    if result == 0:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
