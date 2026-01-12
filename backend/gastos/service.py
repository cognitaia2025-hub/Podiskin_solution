"""Servicio de Gastos - Lógica de negocio 100% async."""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GastosService:
    """Servicio asíncrono para gestión de gastos."""

    async def get_all(
        self,
        categoria: str = None,
        desde: datetime = None,
        hasta: datetime = None,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los gastos con filtros opcionales.

        Args:
            categoria: Filtrar por categoría
            desde: Fecha inicio
            hasta: Fecha fin

        Returns:
            Lista de gastos
        """
        from db import get_connection, release_connection

        conn = None
        try:
            conn = await get_connection()

            query = """
                SELECT id, categoria, concepto, monto, fecha_gasto,
                       metodo_pago, factura_disponible, folio_factura,
                       registrado_por, notas, fecha_registro
                FROM gastos WHERE 1=1
            """
            params = []

            if categoria:
                query += " AND categoria = $" + str(len(params) + 1)
                params.append(categoria)
            if desde:
                query += " AND fecha_gasto >= $" + str(len(params) + 1)
                params.append(desde)
            if hasta:
                query += " AND fecha_gasto <= $" + str(len(params) + 1)
                params.append(hasta)

            query += " ORDER BY fecha_gasto DESC"

            gastos = await conn.fetch(query, *params)
            return [dict(g) for g in gastos] if gastos else []

        except Exception as e:
            logger.error(f"Error en get_all gastos: {e}", exc_info=True)
            raise RuntimeError(f"Error obteniendo lista de gastos: {e}") from e
        finally:
            if conn:
                await release_connection(conn)

    async def get_resumen(self) -> List[Dict[str, Any]]:
        """
        Obtiene resumen de gastos por categoría.

        Returns:
            Lista con resumen por categoría
        """
        from db import get_connection, release_connection

        conn = None
        try:
            conn = await get_connection()

            resumen = await conn.fetch(
                """
                SELECT categoria, COUNT(*) as cantidad, SUM(monto) as total
                FROM gastos GROUP BY categoria ORDER BY total DESC
            """
            )

            return [dict(r) for r in resumen] if resumen else []

        except Exception as e:
            logger.error(f"Error en get_resumen gastos: {e}", exc_info=True)
            raise RuntimeError(f"Error obteniendo resumen de gastos: {e}") from e
        finally:
            if conn:
                await release_connection(conn)

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un nuevo gasto.

        Args:
            data: Datos del gasto

        Returns:
            Gasto creado

        Raises:
            Exception: Si hay error en la creación
        """
        from db import get_connection, release_connection

        conn = None
        try:
            conn = await get_connection()

            new_gasto = await conn.fetchrow(
                """
                INSERT INTO gastos (categoria, concepto, monto, fecha_gasto,
                    metodo_pago, factura_disponible, folio_factura,
                    registrado_por, notas)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id, categoria, concepto, monto, fecha_gasto,
                          metodo_pago, factura_disponible, folio_factura,
                          registrado_por, notas, fecha_registro
                """,
                data["categoria"],
                data["concepto"],
                data["monto"],
                data.get("fecha_gasto", datetime.now()),
                data["metodo_pago"],
                data.get("factura_disponible", False),
                data.get("folio_factura"),
                data.get("registrado_por"),
                data.get("notas"),
            )

            return dict(new_gasto) if new_gasto else None

        except Exception as e:
            logger.error(f"Error creating gasto: {e}")
            raise
        finally:
            if conn:
                await release_connection(conn)


# Instancia global del servicio
gastos_service = GastosService()
