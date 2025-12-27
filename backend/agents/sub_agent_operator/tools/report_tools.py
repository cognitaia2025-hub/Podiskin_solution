"""
Tools de Reportes
=================

Funciones para generar reportes operativos.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, date, timedelta

from ..utils.database import _get_connection, _put_connection

logger = logging.getLogger(__name__)


def generate_appointment_stats(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Genera estadísticas de citas.

    Args:
        start_date: Fecha inicio (YYYY-MM-DD)
        end_date: Fecha fin (YYYY-MM-DD)

    Returns:
        Diccionario con estadísticas
    """
    conn = None
    try:
        # Defaults: última semana
        if not start_date:
            start_date = (date.today() - timedelta(days=7)).isoformat()
        if not end_date:
            end_date = date.today().isoformat()

        conn = _get_connection()
        cursor = conn.cursor()

        # Total de citas
        cursor.execute(
            "SELECT COUNT(*) FROM citas WHERE fecha BETWEEN %s AND %s",
            (start_date, end_date),
        )
        total = cursor.fetchone()[0]

        # Por estado
        cursor.execute(
            """
            SELECT estado, COUNT(*) 
            FROM citas 
            WHERE fecha BETWEEN %s AND %s
            GROUP BY estado
            """,
            (start_date, end_date),
        )
        by_status = dict(cursor.fetchall())

        # Por tratamiento
        cursor.execute(
            """
            SELECT tratamiento, COUNT(*) 
            FROM citas 
            WHERE fecha BETWEEN %s AND %s
            GROUP BY tratamiento
            ORDER BY COUNT(*) DESC
            LIMIT 5
            """,
            (start_date, end_date),
        )
        by_treatment = dict(cursor.fetchall())

        cursor.close()

        return {
            "success": True,
            "period": {"start": start_date, "end": end_date},
            "total": total,
            "by_status": by_status,
            "by_treatment": by_treatment,
        }

    except Exception as e:
        logger.error(f"Error generating stats: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

    finally:
        if conn:
            _put_connection(conn)


def generate_patient_stats() -> Dict[str, Any]:
    """
    Genera estadísticas de pacientes.

    Returns:
        Diccionario con estadísticas
    """
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        # Total de pacientes
        cursor.execute("SELECT COUNT(*) FROM pacientes")
        total = cursor.fetchone()[0]

        # Pacientes nuevos (último mes)
        cursor.execute(
            """
            SELECT COUNT(*) FROM pacientes 
            WHERE fecha_registro >= CURRENT_DATE - INTERVAL '30 days'
            """
        )
        new_last_month = cursor.fetchone()[0]

        cursor.close()

        return {
            "success": True,
            "total": total,
            "new_last_month": new_last_month,
        }

    except Exception as e:
        logger.error(f"Error generating patient stats: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

    finally:
        if conn:
            _put_connection(conn)
