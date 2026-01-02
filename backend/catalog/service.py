from typing import List, Optional
from fastapi import HTTPException
from db import database
from catalog.models import ServiceCreate, ServiceUpdate, ServiceResponse


async def get_services() -> List[ServiceResponse]:
    query = "SELECT id, nombre, descripcion, precio, duracion_minutos, activo FROM catalogo_servicios ORDER BY id"
    rows = await database.fetch_all(query)
    return [ServiceResponse(**dict(row)) for row in rows]


async def get_service(service_id: int) -> ServiceResponse:
    query = "SELECT id, nombre, descripcion, precio, duracion_minutos, activo FROM catalogo_servicios WHERE id = :id"
    row = await database.fetch_one(query, values={"id": service_id})
    if not row:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return ServiceResponse(**dict(row))


async def create_service(service: ServiceCreate) -> ServiceResponse:
    query = """
        INSERT INTO catalogo_servicios (nombre, descripcion, precio, duracion_minutos, activo)
        VALUES (:nombre, :descripcion, :precio, :duracion_minutos, :activo)
        RETURNING id, nombre, descripcion, precio, duracion_minutos, activo
    """
    values = service.dict()
    row = await database.fetch_one(query, values=values)
    return ServiceResponse(**dict(row))


async def update_service(service_id: int, service: ServiceUpdate) -> ServiceResponse:
    query = """
        UPDATE catalogo_servicios
        SET nombre = :nombre, descripcion = :descripcion, precio = :precio, duracion_minutos = :duracion_minutos, activo = :activo
        WHERE id = :id
        RETURNING id, nombre, descripcion, precio, duracion_minutos, activo
    """
    values = service.dict()
    values["id"] = service_id
    row = await database.fetch_one(query, values=values)
    if not row:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return ServiceResponse(**dict(row))


async def delete_service(service_id: int) -> None:
    query = "DELETE FROM catalogo_servicios WHERE id = :id"
    result = await database.execute(query, values={"id": service_id})
    if result == 0:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
