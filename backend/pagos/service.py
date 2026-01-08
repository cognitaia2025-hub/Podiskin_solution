"""
Servicio de Pagos - Lógica de negocio para gestión de pagos
===========================================================
"""

import psycopg
from psycopg.rows import dict_row
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import os
import logging

from pagos.models import PagoCreate, PagoUpdate, PagoResponse, PagoStats
from audit.service import log_action

logger = logging.getLogger(__name__)


class PagosService:
    """Servicio para gestión de pagos."""

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
                row_factory=dict_row,
            )
        return self.conn

    def get_all(
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
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                # Construir query dinámicamente
                conditions = []
                params = []

                if id_cita:
                    conditions.append("p.id_cita = %s")
                    params.append(id_cita)

                if id_paciente:
                    conditions.append("c.id_paciente = %s")
                    params.append(id_paciente)

                if estado_pago:
                    conditions.append("p.estado_pago = %s")
                    params.append(estado_pago)

                if metodo_pago:
                    conditions.append("p.metodo_pago = %s")
                    params.append(metodo_pago)

                if fecha_desde:
                    conditions.append("p.fecha_pago >= %s")
                    params.append(fecha_desde)

                if fecha_hasta:
                    conditions.append("p.fecha_pago <= %s")
                    params.append(fecha_hasta)

                if factura_solicitada is not None:
                    conditions.append("p.factura_solicitada = %s")
                    params.append(factura_solicitada)

                if factura_emitida is not None:
                    conditions.append("p.factura_emitida = %s")
                    params.append(factura_emitida)

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
                    LIMIT %s OFFSET %s
                """

                params.extend([limit, offset])
                cur.execute(query, params)
                pagos = cur.fetchall()

                # Contar total
                count_query = f"""
                    SELECT COUNT(*) as total
                    FROM pagos p
                    LEFT JOIN citas c ON p.id_cita = c.id
                    WHERE {where_clause}
                """
                cur.execute(count_query, params[:-2])  # Sin limit y offset
                total = cur.fetchone()["total"]

                return {
                    "pagos": [dict(pago) for pago in pagos],
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                }

        except Exception as e:
            logger.error(f"Error obteniendo pagos: {e}")
            raise

    def get_by_id(self, pago_id: int) -> Optional[dict]:
        """Obtiene un pago por ID con información extendida."""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
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
                    WHERE p.id = %s
                """,
                    (pago_id,),
                )

                result = cur.fetchone()
                return dict(result) if result else None

        except Exception as e:
            logger.error(f"Error obteniendo pago {pago_id}: {e}")
            raise

    def get_by_cita(self, id_cita: int) -> List[dict]:
        """Obtiene todos los pagos de una cita específica."""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        p.*,
                        u.nombre_completo as recibo_por_nombre
                    FROM pagos p
                    LEFT JOIN usuarios u ON p.recibo_por = u.id
                    WHERE p.id_cita = %s
                    ORDER BY p.fecha_pago DESC
                """,
                    (id_cita,),
                )

                pagos = cur.fetchall()
                return [dict(pago) for pago in pagos]

        except Exception as e:
            logger.error(f"Error obteniendo pagos de cita {id_cita}: {e}")
            raise

    def create(
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
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                # Validar que la cita existe
                cur.execute("SELECT id FROM citas WHERE id = %s", (pago_data.id_cita,))
                if not cur.fetchone():
                    raise ValueError(f"La cita {pago_data.id_cita} no existe")

                # El trigger calcular_saldo() calculará automáticamente saldo_pendiente
                cur.execute(
                    """
                    INSERT INTO pagos (
                        id_cita, fecha_pago, monto_total, monto_pagado,
                        metodo_pago, referencia_pago, factura_solicitada,
                        rfc_factura, estado_pago, recibo_por, notas
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """,
                    (
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
                    ),
                )

                pago_id = cur.fetchone()["id"]
                conn.commit()

                # Obtener pago completo con información extendida
                pago = self.get_by_id(pago_id)

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
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error creando pago: {e}")
            raise

    def update(
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
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                # Obtener datos anteriores para auditoría
                pago_anterior = self.get_by_id(pago_id)
                if not pago_anterior:
                    raise ValueError(f"Pago {pago_id} no encontrado")

                # Construir UPDATE dinámicamente solo con campos proporcionados
                updates = []
                params = []

                if pago_data.monto_pagado is not None:
                    updates.append("monto_pagado = %s")
                    params.append(pago_data.monto_pagado)

                if pago_data.metodo_pago:
                    updates.append("metodo_pago = %s")
                    params.append(pago_data.metodo_pago)

                if pago_data.referencia_pago is not None:
                    updates.append("referencia_pago = %s")
                    params.append(pago_data.referencia_pago)

                if pago_data.factura_solicitada is not None:
                    updates.append("factura_solicitada = %s")
                    params.append(pago_data.factura_solicitada)

                if pago_data.factura_emitida is not None:
                    updates.append("factura_emitida = %s")
                    params.append(pago_data.factura_emitida)

                if pago_data.rfc_factura is not None:
                    updates.append("rfc_factura = %s")
                    params.append(pago_data.rfc_factura)

                if pago_data.folio_factura is not None:
                    updates.append("folio_factura = %s")
                    params.append(pago_data.folio_factura)

                if pago_data.estado_pago:
                    updates.append("estado_pago = %s")
                    params.append(pago_data.estado_pago)

                if pago_data.notas is not None:
                    updates.append("notas = %s")
                    params.append(pago_data.notas)

                if not updates:
                    return pago_anterior  # No hay nada que actualizar

                params.append(pago_id)
                query = f"""
                    UPDATE pagos
                    SET {', '.join(updates)}
                    WHERE id = %s
                """

                cur.execute(query, params)
                conn.commit()

                # Obtener pago actualizado
                pago_actualizado = self.get_by_id(pago_id)

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
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error actualizando pago {pago_id}: {e}")
            raise

    def get_pendientes(self) -> List[dict]:
        """Obtiene pagos pendientes o parciales."""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
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
                )

                pagos = cur.fetchall()
                return [dict(pago) for pago in pagos]

        except Exception as e:
            logger.error(f"Error obteniendo pagos pendientes: {e}")
            raise

    def get_stats(
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
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                # Construir filtros de fecha
                date_filter = ""
                params = []

                if fecha_desde:
                    date_filter += " AND fecha_pago >= %s"
                    params.append(fecha_desde)

                if fecha_hasta:
                    date_filter += " AND fecha_pago <= %s"
                    params.append(fecha_hasta)

                # Estadísticas generales
                cur.execute(
                    f"""
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
                """,
                    params,
                )

                stats = cur.fetchone()

                # Convertir None a 0 para campos numéricos
                result = dict(stats)
                for key in result:
                    if result[key] is None:
                        result[key] = (
                            0 if key != "promedio_por_pago" else Decimal("0.00")
                        )

                return result

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de pagos: {e}")
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


# Instancia global del servicio
pagos_service = PagosService()
