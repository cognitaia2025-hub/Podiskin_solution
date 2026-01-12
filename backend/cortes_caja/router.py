"""Router Cortes de Caja."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
from .service import cortes_caja_service

router = APIRouter(prefix="/cortes-caja", tags=["Cortes de Caja"])


class CorteCreate(BaseModel):
    fecha: date
    realizado_por: int
    notas: Optional[str] = None


@router.get("")
async def listar_cortes():
    """Lista todos los cortes de caja."""
    return cortes_caja_service.get_all()


@router.get("/{fecha}")
async def obtener_corte(fecha: date):
    """Obtiene el corte de una fecha específica."""
    corte = cortes_caja_service.get_by_fecha(fecha)
    if not corte:
        raise HTTPException(404, "No hay corte para esa fecha")
    return corte


@router.post("", status_code=201)
async def crear_corte(corte: CorteCreate):
    """Crea el corte de caja del día."""
    existente = cortes_caja_service.get_by_fecha(corte.fecha)
    if existente:
        raise HTTPException(400, "Ya existe un corte para esta fecha")
    return cortes_caja_service.crear_corte(
        fecha=corte.fecha, realizado_por=corte.realizado_por, notas=corte.notas
    )
