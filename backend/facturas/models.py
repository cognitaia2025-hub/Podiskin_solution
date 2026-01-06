"""
Modelos Pydantic para el módulo de Facturas
===========================================
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


# ============================================================================
# REQUEST MODELS
# ============================================================================

class FacturaCreate(BaseModel):
    """Modelo para solicitar generación de factura."""
    id_pago: int = Field(..., description="ID del pago a facturar")
    rfc_receptor: str = Field(..., min_length=12, max_length=13, description="RFC del receptor")
    nombre_receptor: str = Field(..., description="Nombre o razón social")
    uso_cfdi: str = Field("G03", description="Uso del CFDI (G03=Gastos generales)")


class FacturaCancel(BaseModel):
    """Modelo para cancelar una factura."""
    motivo: str = Field(..., description="Motivo de cancelación")


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class FacturaResponse(BaseModel):
    """Modelo de respuesta para una factura."""
    id: int
    id_pago: int
    folio_fiscal: str
    serie: Optional[str]
    folio: Optional[int]
    rfc_emisor: str
    rfc_receptor: str
    nombre_receptor: Optional[str]
    uso_cfdi: str
    metodo_pago: str
    forma_pago: str
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    fecha_emision: datetime
    fecha_timbrado: Optional[datetime]
    uuid_sat: Optional[str]
    estado_factura: str
    xml_url: Optional[str]
    pdf_url: Optional[str]
    generado_por: Optional[int]
    generado_por_nombre: Optional[str] = None
    notas: Optional[str]
    fecha_registro: datetime
    
    # Información del pago asociado
    monto_pagado: Optional[Decimal] = None
    metodo_pago_original: Optional[str] = None

    class Config:
        from_attributes = True


class FacturaListResponse(BaseModel):
    """Modelo de respuesta para lista de facturas."""
    facturas: list[FacturaResponse]
    total: int
    limit: int
    offset: int
