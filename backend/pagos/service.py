"""
Servicio de Pagos - Lógica de negocio para gestión de pagos
===========================================================
Migrado a AsyncPG con pool centralizado
"""

from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import logging

from pagos.models import PagoCreate, PagoUpdate, PagoResponse, PagoStats
from audit.service import log_action
from db import get_connection, release_connection

logger = logging.getLogger(__name__)


class PagosService:
    """Servicio para gestión de pagos usando pool centralizado AsyncPG."""

    async def get_all(
        self,
        id_cita: Optional[int] = None,
        id_paciente: Optional[int] = None,
        estado_pago: Optional[str] = None,
        metodo_pago: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        factura_solicitada: Optional[bool] = None,
        factura_emitida: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """
        Obtiene lista de pagos con filtros.

        Returns:
            dict: Lista de pagos y total de registros
        """
        conn = await get_connection()
        try:
            # Construir query dinámicamente
            conditions = []
            params = []
            param_idx = 1

            if id_cita:
                conditions.append(f"p.id_cita = ${param_idx}")
                params.append(id_cita)
                param_idx += 1

            if id_paciente:
                conditions.append(f"c.id_paciente = ${param_idx}")
                params.append(id_paciente)
                param_idx += 1

            if estado_pago:
                conditions.append(f"p.estado_pago = ${param_idx}")
                params.append(estado_pago)
                param_idx += 1

            if metodo_pago:
                conditions.append(f"p.metodo_pago = ${param_idx}")
                params.append(metodo_pago)
                param_idx += 1

            if fecha_desde:
                conditions.append(f"p.fecha_pago >= ${param_idx}")
                params.append(fecha_desde)
                param_idx += 1

            if fecha_hasta:
                conditions.append(f"p.fecha_pago <= ${param_idx}")
                params.append(fecha_hasta)
                param_idx += 1

            if factura_solicitada is not None:
                conditions.append(f"p.factura_solicitada = ${param_idx}")
                params.append(factura_solicitada)
                param_idx += 1

            if factura_emitida is not None:
                conditions.append(f"p.factura_emitida = ${param_idx}")
                params.append(factura_emitida)
                param_idx += 1

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            # Query principal con JOINs
            query = f"""
                SELECT 
                    p.*,
                    u.nombre_completo as recibo_por_nombre,
                    c.id_paciente as paciente_id,
                    pac.primer_nombre || ' ' || pac.primer_apellido as paciente_nombre,
                    c.id_podologo as podologo_id,
                    pod.nombre_completo as podologo_nombre,
                    c.fecha_hora_inicio as fecha_cita
                FROM pagos p
                LEFT JOIN usuarios u ON p.recibo_por = u.id
                LEFT JOIN citas c ON p.id_cita = c.id
                LEFT JOIN pacientes pac ON c.id_paciente = pac.id
                LEFT JOIN podologos pod ON c.id_podologo = pod.id
                WHERE {where_clause}
                ORDER BY p.fecha_pago DESC
                LIMIT ${param_idx} OFFSET ${param_idx + 1}
            """

            params.extend([limit, offset])
            pagos_rows = await conn.fetch(query, *params)
            pagos = [dict(row) for row in pagos_rows]

            # Contar total
            count_query = f"""
                SELECT COUNT(*) as total
                FROM pagos p
                LEFT JOIN citas c ON p.id_cita = c.id
                WHERE {where_clause}
            """
            count_row = await conn.fetchrow(count_query, *params[:-2])  # Sin limit y offset
            total = count_row["total"]

            return {
                "pagos": pagos,
                "total": total,
                "limit": limit,
                "offset": offset,
            }

        except Exception as e:
            logger.error(f"Error obteniendo pagos: {e}", exc_info=True)
            raise
        finally:
            await release_connection(conn)

    async def get_by_id(self, pago_id: int) -> Optional[dict]:
        """Obtiene un pago por ID con información extendida."""
        conn = await get_connection()
        try:
            query = """
                SELECT 
                    p.*,
                    u.nombre_completo as recibo_por_nombre,
                    c.id_paciente as paciente_id,
                    pac.primer_nombre || ' ' || pac.primer_apellido as paciente_nombre,
                    c.id_podologo as podologo_id,
                    pod.nombre_completo as podologo_nombre,
                    c.fecha_hora_inicio as fecha_cita
                FROM pagos p
                LEFT JOIN usuarios u ON p.recibo_por = u.id
                LEFT JOIN citas c ON p.id_cita = c.id
                LEFT JOIN pacientes pac ON c.id_paciente = pac.id
                LEFT JOIN podologos pod ON c.id_podologo = pod.id
                WHERE p.id = $1
            """
            
            result = await conn.fetchrow(query, pago_id)
            return dict(result) if result else None

        except Exception as e:
            logger.error(f"Error obteniendo pago {pago_id}: {e}", exc_info=True)
            raise
        finally:
            await release_connection(conn)

    async def get_by_cita(self, id_cita: int) -> List[dict]:
        """Obtiene todos los pagos de una cita específica."""
        conn = await get_connection()
        try:
            query = """
                SELECT 
                    p.*,
                    u.nombre_completo as recibo_por_nombre
                FROM pagos p
                LEFT JOIN usuarios u ON p.recibo_por = u.id
                WHERE p.id_cita = $1
                ORDER BY p.fecha_pago DESC
            """
            
            pagos_rows = await conn.fetch(query, id_cita)
            return [dict(pago) for pago in pagos_rows]

        except Exception as e:
            logger.error(f"Error obteniendo pagos de cita {id_cita}: {e}", exc_info=True)
            raise
        finally:
            await release_connection(conn)

    async def create(
        self, pago_data: PagoCreate, usuario_id: int, ip_address: Optional[str] = None
    ) -> dict:
        """
        Crea un nuevo pago.

        Args:
            pago_data: Datos del pago
            usuario_id: ID del usuario que crea el pago
            ip_address: IP del usuario (para auditoría)

        Returns:
            dict: Pago creado
        """
        conn = await get_connection()
        try:
            # Validar que la cita existe
            cita_check = await conn.fetchrow("SELECT id FROM citas WHERE id = $1", pago_data.id_cita)
            if not cita_check:
                raise ValueError(f"La cita {pago_data.id_cita} no existe")

            # El trigger calcular_saldo() calculará automáticamente saldo_pendiente
            query = """
                INSERT INTO pagos (
                    id_cita, fecha_pago, monto_total, monto_pagado,
                    metodo_pago, referencia_pago, factura_solicitada,
                    rfc_factura, estado_pago, recibo_por, notas
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING id
            """
            
            pago_id = await conn.fetchval(
                query,
                pago_data.id_cita,
                pago_data.fecha_pago,
                pago_data.monto_total,
                pago_data.monto_pagado,
                pago_data.metodo_pago,
                pago_data.referencia_pago,
                pago_data.factura_solicitada,
                pago_data.rfc_factura,
                pago_data.estado_pago,
                pago_data.recibo_por,
                pago_data.notas,
            )

            # Obtener pago completo con información extendida
            pago = await self.get_by_id(pago_id)

            # Registrar en auditoría
            log_action(
                usuario_id=usuario_id,
                accion="crear",
                modulo="pagos",
                descripcion=f"Pago creado: ${pago['monto_pagado']} ({pago['metodo_pago']}) - Cita #{pago_data.id_cita}",
                datos_nuevos=pago,
                ip_address=ip_address,
            )

            logger.info(f"Pago {pago_id} creado exitosamente")
            return pago

        except Exception as e:
            logger.error(f"Error creando pago: {e}", exc_info=True)
            raise
        finally:
            await release_connection(conn)

    async def update(
        self,
        pago_id: int,
        pago_data: PagoUpdate,
        usuario_id: int,
        ip_address: Optional[str] = None,
    ) -> dict:
        """
        Actualiza un pago existente.

        Args:
            pago_id: ID del pago a actualizar
            pago_data: Datos a actualizar
            usuario_id: ID del usuario que actualiza
            ip_address: IP del usuario (para auditoría)

        Returns:
            dict: Pago actualizado
        """
        conn = await get_connection()
        try:
            # Obtener datos anteriores para auditoría
            pago_anterior = await self.get_by_id(pago_id)
            if not pago_anterior:
                raise ValueError(f"Pago {pago_id} no encontrado")

            # Construir UPDATE dinámicamente solo con campos proporcionados
            updates = []
            params = []
            param_idx = 1

            if pago_data.monto_pagado is not None:
                updates.append(f"monto_pagado = ${param_idx}")
                params.append(pago_data.monto_pagado)
                param_idx += 1

            if pago_data.metodo_pago:
                updates.append(f"metodo_pago = ${param_idx}")
                params.append(pago_data.metodo_pago)
                param_idx += 1

            if pago_data.referencia_pago is not None:
                updates.append(f"referencia_pago = ${param_idx}")
                params.append(pago_data.referencia_pago)
                param_idx += 1

            if pago_data.factura_solicitada is not None:
                updates.append(f"factura_solicitada = ${param_idx}")
                params.append(pago_data.factura_solicitada)
                param_idx += 1

            if pago_data.factura_emitida is not None:
                updates.append(f"factura_emitida = ${param_idx}")
                params.append(pago_data.factura_emitida)
                param_idx += 1

            if pago_data.rfc_factura is not None:
                updates.append(f"rfc_factura = ${param_idx}")
                params.append(pago_data.rfc_factura)
                param_idx += 1

            if pago_data.folio_factura is not None:
                updates.append(f"folio_factura = ${param_idx}")
                params.append(pago_data.folio_factura)
                param_idx += 1

            if pago_data.estado_pago:
                updates.append(f"estado_pago = ${param_idx}")
                params.append(pago_data.estado_pago)
                param_idx += 1

            if pago_data.notas is not None:
                updates.append(f"notas = ${param_idx}")
                params.append(pago_data.notas)
                param_idx += 1

            if not updates:
                return pago_anterior  # No hay nada que actualizar

            params.append(pago_id)
            query = f"""
                UPDATE pagos
                SET {', '.join(updates)}
                WHERE id = ${param_idx}
            """

            await conn.execute(query, *params)

            # Obtener pago actualizado
            pago_actualizado = await self.get_by_id(pago_id)

            # Registrar en auditoría
            log_action(
                usuario_id=usuario_id,
                accion="actualizar",
                modulo="pagos",
                descripcion=f"Pago #{pago_id} actualizado",
                datos_anteriores=pago_anterior,
                datos_nuevos=pago_actualizado,
                ip_address=ip_address,
            )

            logger.info(f"Pago {pago_id} actualizado exitosamente")
            return pago_actualizado

        except Exception as e:
            logger.error(f"Error actualizando pago {pago_id}: {e}", exc_info=True)
            raise
        finally:
            await release_connection(conn)

    async def get_pendientes(self) -> List[dict]:
        """Obtiene pagos pendientes o parciales."""
        conn = await get_connection()
        try:
            query = """
                SELECT 
                    p.*,
                    u.nombre_completo as recibo_por_nombre,
                    c.id_paciente as paciente_id,
                    pac.primer_nombre || ' ' || pac.primer_apellido as paciente_nombre,
                    c.fecha_hora_inicio as fecha_cita
                FROM pagos p
                LEFT JOIN usuarios u ON p.recibo_por = u.id
                LEFT JOIN citas c ON p.id_cita = c.id
                LEFT JOIN pacientes pac ON c.id_paciente = pac.id
                WHERE p.estado_pago IN ('Pendiente', 'Parcial')
                ORDER BY p.fecha_pago DESC
            """
            
            pagos_rows = await conn.fetch(query)
            return [dict(pago) for pago in pagos_rows]

        except Exception as e:
            logger.error(f"Error obteniendo pagos pendientes: {e}", exc_info=True)
            raise
        finally:
            await release_connection(conn)

    async def get_stats(
        self,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
    ) -> dict:
        """
        Obtiene estadísticas de pagos.

        Args:
            fecha_desde: Fecha inicio para filtrar
            fecha_hasta: Fecha fin para filtrar

        Returns:
            dict: Estadísticas de pagos
        """
        conn = await get_connection()
        try:
            # Construir filtros de fecha
            date_conditions = []
            params = []
            param_idx = 1

            if fecha_desde:
                date_conditions.append(f"fecha_pago >= ${param_idx}")
                params.append(fecha_desde)
                param_idx += 1

            if fecha_hasta:
                date_conditions.append(f"fecha_pago <= ${param_idx}")
                params.append(fecha_hasta)
                param_idx += 1

            date_filter = " AND " + " AND ".join(date_conditions) if date_conditions else ""

            # Estadísticas generales
            query = f"""
                SELECT 
                    SUM(CASE WHEN estado_pago = 'Pagado' THEN monto_pagado ELSE 0 END) as total_cobrado,
                    SUM(CASE WHEN estado_pago IN ('Pendiente', 'Parcial') THEN saldo_pendiente ELSE 0 END) as total_pendiente,
                    SUM(CASE WHEN estado_pago = 'Parcial' THEN monto_pagado ELSE 0 END) as total_parcial,
                    AVG(monto_pagado) as promedio_por_pago,
                    COUNT(*) as total_pagos,
                    COUNT(CASE WHEN estado_pago = 'Pagado' THEN 1 END) as pagos_completos,
                    COUNT(CASE WHEN estado_pago = 'Parcial' THEN 1 END) as pagos_parciales,
                    COUNT(CASE WHEN estado_pago = 'Pendiente' THEN 1 END) as pagos_pendientes,
                    SUM(CASE WHEN metodo_pago = 'Efectivo' THEN monto_pagado ELSE 0 END) as efectivo,
                    SUM(CASE WHEN metodo_pago = 'Tarjeta_Debito' THEN monto_pagado ELSE 0 END) as tarjeta_debito,
                    SUM(CASE WHEN metodo_pago = 'Tarjeta_Credito' THEN monto_pagado ELSE 0 END) as tarjeta_credito,
                    SUM(CASE WHEN metodo_pago = 'Transferencia' THEN monto_pagado ELSE 0 END) as transferencia,
                    SUM(CASE WHEN metodo_pago IN ('Cheque', 'Otro') THEN monto_pagado ELSE 0 END) as otros,
                    COUNT(CASE WHEN factura_solicitada = true THEN 1 END) as facturas_solicitadas,
                    COUNT(CASE WHEN factura_emitida = true THEN 1 END) as facturas_emitidas
                FROM pagos
                WHERE 1=1 {date_filter}
            """
            
            stats_row = await conn.fetchrow(query, *params)
            result = dict(stats_row)

            # Convertir None a 0 para campos numéricos
            for key in result:
                if result[key] is None:
                    result[key] = 0 if key != "promedio_por_pago" else Decimal("0.00")

            return result

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de pagos: {e}", exc_info=True)
            # Retornar estructura vacía en lugar de error para evitar 500
            return {
                "total_cobrado": 0,
                "total_pendiente": 0,
                "total_parcial": 0,
                "promedio_por_pago": Decimal("0.00"),
                "total_pagos": 0,
                "pagos_completos": 0,
                "pagos_parciales": 0,
                "pagos_pendientes": 0,
                "efectivo": 0,
                "tarjeta_debito": 0,
                "tarjeta_credito": 0,
                "transferencia": 0,
                "otros": 0,
                "facturas_solicitadas": 0,
                "facturas_emitidas": 0,
            }
        finally:
            await release_connection(conn)


# Instancia global del servicio
pagos_service = PagosService()
