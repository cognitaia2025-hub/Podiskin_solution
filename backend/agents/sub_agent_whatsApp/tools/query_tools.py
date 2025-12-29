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


@tool
def get_treatment_info(treatment_name: str) -> Dict[str, Any]:
    """
    Obtiene información detallada de un tratamiento específico.
    
    Wrapper para search_treatment con nombre más explícito.
    
    Args:
        treatment_name: Nombre del tratamiento a buscar
    
    Returns:
        Diccionario con información del tratamiento
    """
    logger.info(f"Getting treatment info for: {treatment_name}")
    # Reutilizar la función search_treatment
    return search_treatment.invoke({"query": treatment_name})


@tool
def get_clinic_info(info_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Obtiene información de la clínica (horarios, ubicación, contacto).
    
    Wrapper unificado que combina get_business_hours y get_location_info.
    
    Args:
        info_type: Tipo de información ('horarios', 'ubicacion', 'contacto', o None para todo)
    
    Returns:
        Diccionario con información de la clínica
    """
    logger.info(f"Getting clinic info: {info_type}")
    
    if info_type == "horarios":
        return get_business_hours.invoke({})
    elif info_type == "ubicacion":
        return get_location_info.invoke({})
    elif info_type == "contacto":
        return {
            "clinica": "Podoskin Solution",
            "telefono": "686-108-3647",
            "whatsapp": "686-108-3647",
        }
    else:
        # Retornar todo
        return {
            "clinica": "Podoskin Solution",
            "telefono": "686-108-3647",
            "whatsapp": "686-108-3647",
            "direccion": "Av. Electricistas 1978, Col. Libertad, Mexicali B.C.",
            "google_maps": "https://maps.app.goo.gl/1yCChxYUkUHejBHW8",
            "horarios": {
                "lunes_viernes": "9:00 AM - 6:00 PM",
                "sabado": "10:00 AM - 2:00 PM",
                "domingo": "Cerrado",
            },
        }


@tool
def get_prices(service_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Obtiene los precios de servicios/tratamientos.
    
    Args:
        service_name: Nombre del servicio (opcional, si no se proporciona retorna todos)
    
    Returns:
        Diccionario con precios de servicios
    """
    logger.info(f"Getting prices for: {service_name or 'all services'}")
    
    try:
        conn = _get_db_connection()
        
        if service_name:
            # Buscar servicio específico
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT nombre_servicio, precio_base, duracion_minutos, descripcion
                    FROM tratamientos 
                    WHERE activo = true
                      AND (LOWER(nombre_servicio) LIKE LOWER(%s)
                           OR LOWER(descripcion) LIKE LOWER(%s))
                    LIMIT 1
                    """,
                    (f"%{service_name}%", f"%{service_name}%"),
                )
                result = cur.fetchone()
            conn.close()
            
            if not result:
                return {
                    "encontrado": False,
                    "mensaje": f"No se encontró precio para '{service_name}'",
                }
            
            return {
                "encontrado": True,
                "servicio": result["nombre_servicio"],
                "precio": f"${result['precio_base']:.0f} MXN",
                "duracion": f"{result['duracion_minutos']} minutos",
                "descripcion": result["descripcion"],
            }
        else:
            # Retornar todos los precios
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT nombre_servicio, precio_base, duracion_minutos
                    FROM tratamientos 
                    WHERE activo = true
                    ORDER BY nombre_servicio
                    """
                )
                results = cur.fetchall()
            conn.close()
            
            if not results:
                return {
                    "encontrados": False,
                    "mensaje": "No hay precios disponibles",
                }
            
            return {
                "encontrados": True,
                "cantidad": len(results),
                "servicios": [
                    {
                        "nombre": r["nombre_servicio"],
                        "precio": f"${r['precio_base']:.0f} MXN",
                        "duracion": f"{r['duracion_minutos']} min",
                    }
                    for r in results
                ],
            }
            
    except Exception as e:
        logger.error(f"Error getting prices: {e}")
        return {"encontrados": False, "error": str(e)}


@tool
def search_faq(query: str) -> Dict[str, Any]:
    """
    Busca en las preguntas frecuentes (FAQ) / base de conocimiento.
    
    Wrapper para search_knowledge_base con nombre más intuitivo.
    
    Args:
        query: Pregunta o término de búsqueda
    
    Returns:
        Diccionario con respuesta encontrada o mensaje de no encontrado
    """
    logger.info(f"Searching FAQ: {query}")
    
    # Importar aquí para evitar importación circular
    from .knowledge_tools import search_knowledge_base
    
    # Usar la función de knowledge_tools
    result = search_knowledge_base.invoke({"question": query})
    
    # Adaptar el formato de respuesta para que sea más intuitivo
    if result.get("found"):
        return {
            "encontrado": True,
            "pregunta": result.get("pregunta_original"),
            "respuesta": result.get("respuesta"),
            "confianza": result.get("similarity"),
        }
    else:
        return {
            "encontrado": False,
            "mensaje": "No se encontró respuesta en la base de conocimiento",
        }


# Mantener compatibilidad con código existente
_get_db_connection = lambda: psycopg2.connect(DATABASE_URL)
