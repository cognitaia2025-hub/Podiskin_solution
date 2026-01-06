"""
Modelos Pydantic para el módulo de Pagos
=========================================
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


# ============================================================================
# ENUMS
# ============================================================================

ESTADOS_PAGO = ["Pagado", "Parcial", "Pendiente", "Cancelado"]
METODOS_PAGO = ["Efectivo", "Tarjeta_Debito", "Tarjeta_Credito", "Transferencia", "Cheque", "Otro"]


# ============================================================================
# REQUEST MODELS
# ============================================================================

class PagoCreate(BaseModel):
    """Modelo para crear un nuevo pago."""
    id_cita: int = Field(..., gt=0, description="ID de la cita asociada")
    fecha_pago: datetime = Field(default_factory=datetime.now, description="Fecha del pago")
    monto_total: Decimal = Field(..., gt=0, description="Monto total a pagar")
    monto_pagado: Decimal = Field(..., ge=0, description="Monto efectivamente pagado")
    metodo_pago: str = Field(..., description="Método de pago")
    referencia_pago: Optional[str] = Field(None, max_length=200, description="Referencia o folio")
    factura_solicitada: bool = Field(False, description="Si requiere factura")
    rfc_factura: Optional[str] = Field(None, max_length=13, description="RFC para facturación")
    estado_pago: str = Field("Pendiente", description="Estado del pago")
    recibo_por: Optional[int] = Field(None, description="ID del usuario que recibe el pago")
    notas: Optional[str] = Field(None, description="Notas adicionales")
    
    @field_validator('metodo_pago')
    @classmethod
    def validate_metodo_pago(cls, v):
        if v not in METODOS_PAGO:
            raise ValueError(f"Método de pago debe ser uno de: {', '.join(METODOS_PAGO)}")
        return v
    
    @field_validator('estado_pago')
    @classmethod
    def validate_estado_pago(cls, v):
        if v not in ESTADOS_PAGO:
            raise ValueError(f"Estado de pago debe ser uno de: {', '.join(ESTADOS_PAGO)}")
        return v
    
    @field_validator('monto_pagado')
    @classmethod
    def validate_monto_pagado(cls, v, info):
        if 'monto_total' in info.data and v > info.data['monto_total']:
            raise ValueError("El monto pagado no puede ser mayor al monto total")
        return v


class PagoUpdate(BaseModel):
    """Modelo para actualizar un pago existente."""
    monto_pagado: Optional[Decimal] = Field(None, ge=0, description="Nuevo monto pagado")
    metodo_pago: Optional[str] = Field(None, description="Método de pago")
    referencia_pago: Optional[str] = Field(None, max_length=200)
    factura_solicitada: Optional[bool] = None
    factura_emitida: Optional[bool] = None
    rfc_factura: Optional[str] = Field(None, max_length=13)
    folio_factura: Optional[str] = Field(None, max_length=100)
    estado_pago: Optional[str] = None
    notas: Optional[str] = None
    
    @field_validator('metodo_pago')
    @classmethod
    def validate_metodo_pago(cls, v):
        if v and v not in METODOS_PAGO:
            raise ValueError(f"Método de pago debe ser uno de: {', '.join(METODOS_PAGO)}")
        return v
    
    @field_validator('estado_pago')
    @classmethod
    def validate_estado_pago(cls, v):
        if v and v not in ESTADOS_PAGO:
            raise ValueError(f"Estado de pago debe ser uno de: {', '.join(ESTADOS_PAGO)}")
        return v


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class PagoResponse(BaseModel):
    """Modelo de respuesta para un pago."""
    id: int
    id_cita: int
    fecha_pago: datetime
    monto_total: Decimal
    monto_pagado: Decimal
    saldo_pendiente: Decimal
    metodo_pago: str
    referencia_pago: Optional[str]
    factura_solicitada: bool
    factura_emitida: bool
    rfc_factura: Optional[str]
    folio_factura: Optional[str]
    estado_pago: str
    recibo_por: Optional[int]
    recibo_por_nombre: Optional[str] = None
    notas: Optional[str]
    fecha_registro: datetime
    
    # Información adicional de la cita
    paciente_id: Optional[int] = None
    paciente_nombre: Optional[str] = None
    podologo_id: Optional[int] = None
    podologo_nombre: Optional[str] = None
    fecha_cita: Optional[datetime] = None

    class Config:
        from_attributes = True


class PagoListResponse(BaseModel):
    """Modelo de respuesta para lista de pagos."""
    pagos: list[PagoResponse]
    total: int
    limit: int
    offset: int


class PagoStats(BaseModel):
    """Estadísticas de pagos."""
    total_cobrado: Decimal
    total_pendiente: Decimal
    total_parcial: Decimal
    promedio_por_pago: Decimal
    total_pagos: int
    pagos_completos: int
    pagos_parciales: int
    pagos_pendientes: int
    
    # Por método de pago
    efectivo: Decimal
    tarjeta_debito: Decimal
    tarjeta_credito: Decimal
    transferencia: Decimal
    otros: Decimal
    
    # Facturas
    facturas_solicitadas: int
    facturas_emitidas: int


# ============================================================================
# FILTER MODELS
# ============================================================================

class PagoFilters(BaseModel):
    """Filtros para búsqueda de pagos."""
    id_cita: Optional[int] = None
    id_paciente: Optional[int] = None
    estado_pago: Optional[str] = None
    metodo_pago: Optional[str] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    factura_solicitada: Optional[bool] = None
    factura_emitida: Optional[bool] = None
