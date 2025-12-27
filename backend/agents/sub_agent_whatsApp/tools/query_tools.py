"""
Query Tools - Sub-Agente WhatsApp
==================================

Herramientas para consultas de información - AHORA DESDE BD.
"""

import logging
from typing import Dict, Any, Optional
from langchain_core.tools import tool
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:KKrauser969271@127.0.0.1:5432/podoskin_db"
)


def _get_db_connection():
    """Obtiene conexión a la BD."""
    return psycopg2.connect(DATABASE_URL)


@tool
def get_treatments_from_db() -> Dict[str, Any]:
    """
    Obtiene los tratamientos disponibles desde la base de datos.

    Returns:
        Diccionario con los tratamientos y sus precios
    """
    logger.info("Fetching treatments from database")

    try:
        conn = _get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT nombre_servicio, descripcion, precio_base, duracion_minutos
                FROM tratamientos 
                WHERE activo = true
                ORDER BY nombre_servicio
            """
            )
            treatments = cur.fetchall()
        conn.close()

        if not treatments:
            return {
                "encontrados": False,
                "mensaje": "No hay tratamientos disponibles actualmente.",
            }

        # Formato simple para Maya
        lista = [
            f"{t['nombre_servicio']}: ${t['precio_base']:.0f} MXN" for t in treatments
        ]

        return {
            "encontrados": True,
            "cantidad": len(treatments),
            "tratamientos": [dict(t) for t in treatments],
            "lista_simple": lista,
        }

    except Exception as e:
        logger.error(f"Error fetching treatments: {e}")
        return {"encontrados": False, "error": str(e)}


@tool
def search_treatment(query: str) -> Dict[str, Any]:
    """
    Busca un tratamiento específico en la base de datos.

    Args:
        query: Término de búsqueda (ej: "uñas", "hongos", "callos")

    Returns:
        Información del tratamiento si se encuentra
    """
    logger.info(f"Searching treatment: {query}")

    try:
        conn = _get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT nombre_servicio, descripcion, precio_base, duracion_minutos
                FROM tratamientos 
                WHERE activo = true
                  AND (LOWER(nombre_servicio) LIKE LOWER(%s) 
                       OR LOWER(descripcion) LIKE LOWER(%s))
            """,
                (f"%{query}%", f"%{query}%"),
            )
            results = cur.fetchall()
        conn.close()

        if not results:
            return {
                "encontrado": False,
                "mensaje": f"No encontré tratamiento para '{query}'.",
            }

        t = results[0]  # Primer resultado
        return {
            "encontrado": True,
            "nombre": t["nombre_servicio"],
            "descripcion": t["descripcion"],
            "precio": f"${t['precio_base']:.0f} MXN",
            "duracion": f"{t['duracion_minutos']} minutos",
        }

    except Exception as e:
        logger.error(f"Error searching treatment: {e}")
        return {"encontrado": False, "error": str(e)}


@tool
def get_business_hours() -> Dict[str, Any]:
    """
    Obtiene los horarios de atención del negocio.

    Returns:
        Diccionario con los horarios de atención
    """
    logger.info("Getting business hours")

    return {
        "clinica": "Podoskin Solution",
        "horarios": {
            "lunes_viernes": "9:00 AM - 6:00 PM",
            "sabado": "10:00 AM - 2:00 PM",
            "domingo": "Cerrado",
        },
        "telefono": "686-108-3647",
    }


@tool
def get_location_info() -> Dict[str, Any]:
    """
    Obtiene la ubicación y datos de contacto del negocio.

    Returns:
        Diccionario con ubicación y contacto
    """
    logger.info("Getting location info")

    return {
        "clinica": "Podoskin Solution",
        "telefono": "686-108-3647",
        "direccion": "Av. Electricistas 1978, Col. Libertad, Mexicali B.C.",
        "google_maps": "https://maps.app.goo.gl/1yCChxYUkUHejBHW8",
    }
