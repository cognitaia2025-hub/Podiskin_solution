from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from catalog.models import ServiceCreate, ServiceUpdate, ServiceResponse
from catalog import service

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("/", response_model=List[ServiceResponse])
async def list_services():
    return await service.get_services()


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: int):
    return await service.get_service(service_id)


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(service_in: ServiceCreate):
    return await service.create_service(service_in)


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(service_id: int, service_in: ServiceUpdate):
    return await service.update_service(service_id, service_in)


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(service_id: int):
    await service.delete_service(service_id)
    return None
