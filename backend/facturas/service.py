"""
Servicio de Facturas - Estructura base para integración SAT
===========================================================
NOTA: Este módulo está preparado para integración futura con el SAT.
Por ahora solo registra solicitudes de factura sin timbrado.
"""

import psycopg
from psycopg.rows import dict_row
from typing import Optional
from datetime import datetime
from decimal import Decimal
import os
import logging

from facturas.models import FacturaCreate
from audit.service import log_action

logger = logging.getLogger(__name__)


class FacturasService:
    """Servicio para gestión de facturas."""
    
    def __init__(self):
        self.conn = None
    
    def _get_connection(self):
        """Obtiene conexión a la base de datos."""
        if self.conn is None or self.conn.closed:
            self.conn = psycopg.connect(
                host=os.getenv("DB_HOST", "127.0.0.1"),
                port=int(os.getenv("DB_PORT", "5432")),
                dbname=os.getenv("DB_NAME", "podoskin_db"),
                user=os.getenv("DB_USER", "podoskin_user"),
                password=os.getenv("DB_PASSWORD", "podoskin_password_123"),
                row_factory=dict_row
            )
        return self.conn
    
    def get_all(
        self,
        id_pago: Optional[int] = None,
        rfc_receptor: Optional[str] = None,
        estado: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> dict:
        """Obtiene lista de facturas con filtros."""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                # Construir query dinámicamente
                conditions = []
                params = []
                
                if id_pago:
                    conditions.append("f.id_pago = %s")
                    params.append(id_pago)
                
                if rfc_receptor:
                    conditions.append("f.rfc_receptor = %s")
                    params.append(rfc_receptor)
                
                if estado:
                    conditions.append("f.estado_factura = %s")
                    params.append(estado)
                
                if fecha_desde:
                    conditions.append("f.fecha_emision >= %s")
                    params.append(fecha_desde)
                
                if fecha_hasta:
                    conditions.append("f.fecha_emision <= %s")
                    params.append(fecha_hasta)
                
                where_clause = " AND ".join(conditions) if conditions else "1=1"
                
                # Query principal
                query = f"""
                    SELECT 
                        f.*,
                        u.nombre as generado_por_nombre,
                        p.monto_pagado,
                        p.metodo_pago as metodo_pago_original
                    FROM facturas f
                    LEFT JOIN usuarios u ON f.generado_por = u.id
                    LEFT JOIN pagos p ON f.id_pago = p.id
                    WHERE {where_clause}
                    ORDER BY f.fecha_emision DESC
                    LIMIT %s OFFSET %s
                """
                
                params.extend([limit, offset])
                cur.execute(query, params)
                facturas = cur.fetchall()
                
                # Contar total
                count_query = f"SELECT COUNT(*) as total FROM facturas f WHERE {where_clause}"
                cur.execute(count_query, params[:-2])
                total = cur.fetchone()['total']
                
                return {
                    "facturas": [dict(f) for f in facturas],
                    "total": total,
                    "limit": limit,
                    "offset": offset
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo facturas: {e}")
            raise
    
    def get_by_id(self, factura_id: int) -> Optional[dict]:
        """Obtiene una factura por ID."""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        f.*,
                        u.nombre as generado_por_nombre,
                        p.monto_pagado,
                        p.metodo_pago as metodo_pago_original
                    FROM facturas f
                    LEFT JOIN usuarios u ON f.generado_por = u.id
                    LEFT JOIN pagos p ON f.id_pago = p.id
                    WHERE f.id = %s
                """, (factura_id,))
                
                result = cur.fetchone()
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"Error obteniendo factura {factura_id}: {e}")
            raise
    
    def create_placeholder(
        self,
        factura_data: FacturaCreate,
        usuario_id: int,
        ip_address: Optional[str] = None
    ) -> dict:
        """
        Crea registro de factura pendiente de timbrado SAT.
        
        NOTA: Este método solo registra la solicitud. La integración
        con el SAT para timbrado se implementará en el futuro.
        """
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                # Verificar que el pago existe
                cur.execute("""
                    SELECT id, monto_pagado, metodo_pago, saldo_pendiente
                    FROM pagos
                    WHERE id = %s
                """, (factura_data.id_pago,))
                
                pago = cur.fetchone()
                if not pago:
                    raise ValueError(f"Pago {factura_data.id_pago} no encontrado")
                
                # Verificar que el pago esté completado
                if pago['saldo_pendiente'] > 0:
                    raise ValueError("No se puede facturar un pago con saldo pendiente")
                
                # Verificar si ya existe factura para este pago
                cur.execute(
                    "SELECT id FROM facturas WHERE id_pago = %s AND estado_factura != 'Cancelada'",
                    (factura_data.id_pago,)
                )
                if cur.fetchone():
                    raise ValueError("Ya existe una factura activa para este pago")
                
                # Calcular subtotal e IVA (16%)
                total = pago['monto_pagado']
                subtotal = total / Decimal('1.16')
                iva = total - subtotal
                
                # RFC del emisor (TODO: Obtener de configuración)
                rfc_emisor = "AAA010101AAA"  # Placeholder
                
                # Generar folio fiscal temporal
                folio_fiscal = f"TEMP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{factura_data.id_pago}"
                
                # Mapear método de pago a clave SAT
                metodo_pago_sat = {
                    "Efectivo": "01",
                    "Tarjeta_Credito": "04",
                    "Tarjeta_Debito": "28",
                    "Transferencia": "03",
                    "Cheque": "02",
                    "Otro": "99"
                }.get(pago['metodo_pago'], "99")
                
                # Insertar factura pendiente
                cur.execute("""
                    INSERT INTO facturas (
                        id_pago, folio_fiscal, rfc_emisor, rfc_receptor,
                        nombre_receptor, uso_cfdi, metodo_pago, forma_pago,
                        subtotal, iva, total, fecha_emision, estado_factura,
                        generado_por, notas
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    factura_data.id_pago,
                    folio_fiscal,
                    rfc_emisor,
                    factura_data.rfc_receptor,
                    factura_data.nombre_receptor,
                    factura_data.uso_cfdi,
                    metodo_pago_sat,
                    pago['metodo_pago'],
                    subtotal,
                    iva,
                    total,
                    datetime.now(),
                    "Pendiente_Timbrado",
                    usuario_id,
                    "⚠️ FACTURA PENDIENTE DE TIMBRADO SAT - Funcionalidad en desarrollo"
                ))
                
                factura_id = cur.fetchone()['id']
                
                # Actualizar pago para marcar factura solicitada
                cur.execute("""
                    UPDATE pagos
                    SET factura_solicitada = true
                    WHERE id = %s
                """, (factura_data.id_pago,))
                
                conn.commit()
                
                # Obtener factura completa
                factura = self.get_by_id(factura_id)
                
                # Registrar en auditoría
                log_action(
                    usuario_id=usuario_id,
                    accion="crear",
                    modulo="facturas",
                    descripcion=f"Factura solicitada (pendiente timbrado SAT) - Pago #{factura_data.id_pago}",
                    datos_nuevos=factura,
                    ip_address=ip_address
                )
                
                logger.info(f"Factura {factura_id} creada (pendiente timbrado SAT)")
                return factura
                
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error creando factura: {e}")
            raise
    
    def cancel(self, factura_id: int, motivo: str, usuario_id: int, ip_address: Optional[str] = None) -> dict:
        """Cancela una factura."""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                # Obtener factura actual
                factura_anterior = self.get_by_id(factura_id)
                if not factura_anterior:
                    raise ValueError(f"Factura {factura_id} no encontrada")
                
                if factura_anterior['estado_factura'] == 'Cancelada':
                    raise ValueError("La factura ya está cancelada")
                
                # Cancelar factura
                cur.execute("""
                    UPDATE facturas
                    SET estado_factura = 'Cancelada',
                        notas = COALESCE(notas, '') || '\nCANCELADA: ' || %s
                    WHERE id = %s
                """, (motivo, factura_id))
                
                conn.commit()
                
                # Obtener factura actualizada
                factura_cancelada = self.get_by_id(factura_id)
                
                # Registrar en auditoría
                log_action(
                    usuario_id=usuario_id,
                    accion="cancelar",
                    modulo="facturas",
                    descripcion=f"Factura #{factura_id} cancelada: {motivo}",
                    datos_anteriores=factura_anterior,
                    datos_nuevos=factura_cancelada,
                    ip_address=ip_address
                )
                
                logger.info(f"Factura {factura_id} cancelada")
                return factura_cancelada
                
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error cancelando factura {factura_id}: {e}")
            raise


# Instancia global del servicio
facturas_service = FacturasService()
