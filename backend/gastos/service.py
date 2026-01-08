"""Servicio de Gastos - Lógica de negocio."""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional, Dict, Any
from datetime import datetime
import os


class GastosService:
    def __init__(self):
        self.conn = None

    def _get_connection(self):
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "127.0.0.1"),
                port=int(os.getenv("DB_PORT", "5432")),
                database=os.getenv("DB_NAME", "podoskin_db"),
                user=os.getenv("DB_USER", "podoskin_user"),
                password=os.getenv("DB_PASSWORD", "podoskin_password_123"),
            )
        return self.conn

    def get_all(
        self, categoria: str = None, desde: datetime = None, hasta: datetime = None
    ) -> List[Dict[str, Any]]:
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            query = """
                SELECT id, categoria, concepto, monto, fecha_gasto,
                       metodo_pago, factura_disponible, folio_factura,
                       registrado_por, notas, fecha_registro
                FROM gastos WHERE 1=1
            """
            params = []
            if categoria:
                query += " AND categoria = %s"
                params.append(categoria)
            if desde:
                query += " AND fecha_gasto >= %s"
                params.append(desde)
            if hasta:
                query += " AND fecha_gasto <= %s"
                params.append(hasta)
            query += " ORDER BY fecha_gasto DESC"
            cur.execute(query, params)
            columns = [
                "id",
                "categoria",
                "concepto",
                "monto",
                "fecha_gasto",
                "metodo_pago",
                "factura_disponible",
                "folio_factura",
                "registrado_por",
                "notas",
                "fecha_registro",
            ]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            # Si la tabla no existe o hay error, retornar array vacío
            print(f"Error en get_all gastos: {e}")
            return []

    def get_resumen(self) -> List[Dict[str, Any]]:
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT categoria, COUNT(*) as cantidad, SUM(monto) as total
                FROM gastos GROUP BY categoria ORDER BY total DESC
            """
            )
            return [
                {
                    "categoria": r[0],
                    "cantidad": r[1],
                    "total": float(r[2]) if r[2] else 0,
                }
                for r in cur.fetchall()
            ]
        except Exception as e:
            print(f"Error en get_resumen gastos: {e}")
            return []

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO gastos (categoria, concepto, monto, fecha_gasto,
                metodo_pago, factura_disponible, folio_factura,
                registrado_por, notas)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """,
            (
                data["categoria"],
                data["concepto"],
                data["monto"],
                data.get("fecha_gasto", datetime.now()),
                data["metodo_pago"],
                data.get("factura_disponible", False),
                data.get("folio_factura"),
                data.get("registrado_por"),
                data.get("notas"),
            ),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        return {"id": new_id, **data}


gastos_service = GastosService()
