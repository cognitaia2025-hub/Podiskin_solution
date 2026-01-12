"""
Servicio de Facturas - Estructura base para integración SAT
===========================================================
NOTA: Este módulo está preparado para integración futura con el SAT.
Por ahora solo registra solicitudes de factura sin timbrado.

Migrado a AsyncPG con pool centralizado.
"""

from typing import Optional
from datetime import datetime
from decimal import Decimal
import logging

from facturas.models import FacturaCreate
from audit.service import log_action
from db import get_connection, release_connection

logger = logging.getLogger(__name__)


class FacturasService:
    """Servicio para gestión de facturas usando pool centralizado AsyncPG."""
    
    async def get_all(
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
        conn = await get_connection()
        try:
            # Construir query dinámicamente
            conditions = []
            params = []
            param_idx = 1
            
            if id_pago:
                conditions.append(f"f.id_pago = ${param_idx}")
                params.append(id_pago)
                param_idx += 1
            
            if rfc_receptor:
                conditions.append(f"f.rfc_receptor = ${param_idx}")
                params.append(rfc_receptor)
                param_idx += 1
            
            if estado:
                conditions.append(f"f.estado_factura = ${param_idx}")
                params.append(estado)
                param_idx += 1
            
            if fecha_desde:
                conditions.append(f"f.fecha_emision >= ${param_idx}")
                params.append(fecha_desde)
                param_idx += 1
            
            if fecha_hasta:
                conditions.append(f"f.fecha_emision <= ${param_idx}")
                params.append(fecha_hasta)
                param_idx += 1
            
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
                LIMIT ${param_idx} OFFSET ${param_idx + 1}
            """
            
            params.extend([limit, offset])
            facturas_rows = await conn.fetch(query, *params)
            facturas = [dict(row) for row in facturas_rows]
            
            # Contar total
            count_query = f"SELECT COUNT(*) as total FROM facturas f WHERE {where_clause}"
            count_row = await conn.fetchrow(count_query, *params[:-2])
            total = count_row['total']
            
            return {
                "facturas": facturas,
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo facturas: {e}", exc_info=True)
            raise
        finally:
            await release_connection(conn)
    
    async def get_by_id(self, factura_id: int) -> Optional[dict]:
        """Obtiene una factura por ID."""
        conn = await get_connection()
        try:
            query = """
                SELECT 
                    f.*,
                    u.nombre as generado_por_nombre,
                    p.monto_pagado,
                    p.metodo_pago as metodo_pago_original
                FROM facturas f
                LEFT JOIN usuarios u ON f.generado_por = u.id
                LEFT JOIN pagos p ON f.id_pago = p.id
                WHERE f.id = $1
            """
            
            result = await conn.fetchrow(query, factura_id)
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"Error obteniendo factura {factura_id}: {e}", exc_info=True)
            raise
        finally:
            await release_connection(conn)
    
    async def create_placeholder(
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
        conn = await get_connection()
        try:
            # Verificar que el pago existe
            pago = await conn.fetchrow("""
                SELECT id, monto_pagado, metodo_pago, saldo_pendiente
                FROM pagos
                WHERE id = $1
            """, factura_data.id_pago)
            
            if not pago:
                raise ValueError(f"Pago {factura_data.id_pago} no encontrado")
            
            # Verificar que el pago esté completado
            if pago['saldo_pendiente'] > 0:
                raise ValueError("No se puede facturar un pago con saldo pendiente")
            
            # Verificar si ya existe factura para este pago
            existe = await conn.fetchrow(
                "SELECT id FROM facturas WHERE id_pago = $1 AND estado_factura != 'Cancelada'",
                factura_data.id_pago
            )
            if existe:
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
            factura_id = await conn.fetchval("""
                INSERT INTO facturas (
                    id_pago, folio_fiscal, rfc_emisor, rfc_receptor,
                    nombre_receptor, uso_cfdi, metodo_pago, forma_pago,
                    subtotal, iva, total, fecha_emision, estado_factura,
                    generado_por, notas
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                RETURNING id
            """, 
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
            )
            
            # Actualizar pago para marcar factura solicitada
            await conn.execute("""
                UPDATE pagos
                SET factura_solicitada = true
                WHERE id = $1
            """, factura_data.id_pago)
            
            # Obtener factura completa
            factura = await self.get_by_id(factura_id)
            
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
            logger.error(f"Error creando factura: {e}", exc_info=True)
            raise
        finally:
            await release_connection(conn)
    
    async def cancel(self, factura_id: int, motivo: str, usuario_id: int, ip_address: Optional[str] = None) -> dict:
        """Cancela una factura."""
        conn = await get_connection()
        try:
            # Obtener factura actual
            factura_anterior = await self.get_by_id(factura_id)
            if not factura_anterior:
                raise ValueError(f"Factura {factura_id} no encontrada")
            
            if factura_anterior['estado_factura'] == 'Cancelada':
                raise ValueError("La factura ya está cancelada")
            
            # Cancelar factura
            await conn.execute("""
                UPDATE facturas
                SET estado_factura = 'Cancelada',
                    notas = COALESCE(notas, '') || '\nCANCELADA: ' || $1
                WHERE id = $2
            """, motivo, factura_id)
            
            # Obtener factura actualizada
            factura_cancelada = await self.get_by_id(factura_id)
            
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
            logger.error(f"Error cancelando factura {factura_id}: {e}", exc_info=True)
            raise
        finally:
            await release_connection(conn)


# Instancia global del servicio
facturas_service = FacturasService()
