"""Servicio Cortes de Caja."""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
from datetime import date
import os


class CortesCajaService:
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

    def get_all(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, fecha_corte, ingresos_efectivo, ingresos_tarjeta,
                   ingresos_transferencia, total_ingresos, gastos_dia,
                   saldo_final, realizado_por, notas, fecha_registro
            FROM cortes_caja ORDER BY fecha_corte DESC
        """
        )
        columns = [
            "id",
            "fecha_corte",
            "ingresos_efectivo",
            "ingresos_tarjeta",
            "ingresos_transferencia",
            "total_ingresos",
            "gastos_dia",
            "saldo_final",
            "realizado_por",
            "notas",
            "fecha_registro",
        ]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

    def get_by_fecha(self, fecha: date) -> Dict[str, Any]:
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, fecha_corte, ingresos_efectivo, ingresos_tarjeta,
                   ingresos_transferencia, total_ingresos, gastos_dia,
                   saldo_final, realizado_por, notas, fecha_registro
            FROM cortes_caja WHERE fecha_corte = %s
        """,
            (fecha,),
        )
        row = cur.fetchone()
        if row:
            columns = [
                "id",
                "fecha_corte",
                "ingresos_efectivo",
                "ingresos_tarjeta",
                "ingresos_transferencia",
                "total_ingresos",
                "gastos_dia",
                "saldo_final",
                "realizado_por",
                "notas",
                "fecha_registro",
            ]
            return dict(zip(columns, row))
        return None

    def crear_corte(self, fecha: date, realizado_por: int, notas: str = None):
        conn = self._get_connection()
        cur = conn.cursor()

        # Calcular ingresos del día por método de pago
        cur.execute(
            """
            SELECT 
                SUM(CASE WHEN metodo_pago = 'Efectivo' THEN monto_total ELSE 0 END),
                SUM(CASE WHEN metodo_pago IN ('Tarjeta_Credito', 'Tarjeta_Debito') THEN monto_total ELSE 0 END),
                SUM(CASE WHEN metodo_pago = 'Transferencia' THEN monto_total ELSE 0 END),
                SUM(monto_total)
            FROM pagos WHERE DATE(fecha_pago) = %s
        """,
            (fecha,),
        )
        pagos = cur.fetchone()

        # Calcular gastos del día
        cur.execute(
            "SELECT COALESCE(SUM(monto), 0) FROM gastos WHERE DATE(fecha_gasto) = %s",
            (fecha,),
        )
        gastos = cur.fetchone()[0]

        efectivo = float(pagos[0] or 0)
        tarjeta = float(pagos[1] or 0)
        transferencia = float(pagos[2] or 0)
        total_ingresos = float(pagos[3] or 0)
        gastos_dia = float(gastos or 0)
        saldo = total_ingresos - gastos_dia

        cur.execute(
            """
            INSERT INTO cortes_caja (fecha_corte, ingresos_efectivo, ingresos_tarjeta,
                ingresos_transferencia, total_ingresos, gastos_dia, saldo_final,
                realizado_por, notas)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """,
            (
                fecha,
                efectivo,
                tarjeta,
                transferencia,
                total_ingresos,
                gastos_dia,
                saldo,
                realizado_por,
                notas,
            ),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        return self.get_by_fecha(fecha)


cortes_caja_service = CortesCajaService()
