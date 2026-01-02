"""Router de Gastos - Endpoints REST."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .service import gastos_service

router = APIRouter(prefix="/gastos", tags=["Gastos"])

CATEGORIAS = [
    "Renta",
    "Servicios",
    "Insumos",
    "Marketing",
    "Mantenimiento",
    "Capacitacion",
    "Papeleria",
    "Limpieza",
    "Varios",
]

METODOS_PAGO = [
    "Efectivo",
    "Transferencia",
    "Tarjeta_Debito",
    "Tarjeta_Credito",
    "Cheque",
]


class GastoCreate(BaseModel):
    categoria: str = Field(..., description="Categoría del gasto")
    concepto: str = Field(..., min_length=3)
    monto: float = Field(..., gt=0)
    fecha_gasto: Optional[datetime] = None
    metodo_pago: str = Field(...)
    factura_disponible: bool = False
    folio_factura: Optional[str] = None
    registrado_por: Optional[int] = None
    notas: Optional[str] = None


@router.get("/")
async def listar_gastos(
    categoria: Optional[str] = Query(None, enum=CATEGORIAS),
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
):
    """Lista gastos con filtros opcionales."""
    return gastos_service.get_all(categoria=categoria, desde=desde, hasta=hasta)


@router.get("/resumen")
async def resumen_gastos():
    """Obtiene resumen de gastos por categoría."""
    return gastos_service.get_resumen()


@router.post("/", status_code=201)
async def crear_gasto(gasto: GastoCreate):
    """Registra un nuevo gasto."""
    if gasto.categoria not in CATEGORIAS:
        raise HTTPException(400, f"Categoría inválida. Use: {CATEGORIAS}")
    if gasto.metodo_pago not in METODOS_PAGO:
        raise HTTPException(400, f"Método de pago inválido. Use: {METODOS_PAGO}")
    return gastos_service.create(gasto.dict())
