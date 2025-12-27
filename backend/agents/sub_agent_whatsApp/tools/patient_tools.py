"""
Patient Tools - Sub-Agente WhatsApp
====================================

Herramientas para gestión de pacientes.
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.tools import tool

from ..utils import fetch, fetchrow, execute

load_dotenv()
logger = logging.getLogger(__name__)


@tool
async def search_patient(
    phone: Optional[str] = None, name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Busca un paciente por teléfono o nombre.

    Args:
        phone: Número de teléfono del paciente
        name: Nombre del paciente (búsqueda parcial)

    Returns:
        Diccionario con información del paciente encontrado o mensaje de no encontrado
    """
    logger.info(f"Searching patient: phone={phone}, name={name}")

    try:
        if phone:
            query = """
            SELECT p.*, c.telefono, c.nombre as contact_name
            FROM pacientes p
            JOIN contactos c ON c.id = p.id_contacto
            WHERE c.telefono = %s
            LIMIT 1
            """
            patient = await fetchrow(query, phone)
        elif name:
            query = """
            SELECT p.*, c.telefono, c.nombre as contact_name
            FROM pacientes p
            JOIN contactos c ON c.id = p.id_contacto
            WHERE LOWER(p.nombre_completo) LIKE LOWER(%s)
            LIMIT 5
            """
            patients = await fetch(query, f"%{name}%")
            if patients:
                return {
                    "found": True,
                    "count": len(patients),
                    "patients": [
                        {
                            "id": p["id"],
                            "nombre": p["nombre_completo"],
                            "telefono": p["telefono"],
                        }
                        for p in patients
                    ],
                }
            return {"found": False, "message": "No se encontraron pacientes"}
        else:
            return {"error": "Debe proporcionar teléfono o nombre"}

        if patient:
            return {
                "found": True,
                "patient": {
                    "id": patient["id"],
                    "nombre": patient["nombre_completo"],
                    "telefono": patient["telefono"],
                    "email": patient.get("email"),
                    "fecha_registro": (
                        patient["fecha_registro"].isoformat()
                        if patient.get("fecha_registro")
                        else None
                    ),
                },
            }
        return {"found": False, "message": "Paciente no encontrado"}

    except Exception as e:
        logger.error(f"Error searching patient: {e}")
        return {"error": str(e)}


@tool
async def get_patient_info(patient_id: int) -> Dict[str, Any]:
    """
    Obtiene información completa de un paciente.

    Args:
        patient_id: ID del paciente

    Returns:
        Diccionario con información completa del paciente
    """
    logger.info(f"Getting patient info: {patient_id}")

    try:
        # Información del paciente
        patient_query = """
        SELECT p.*, c.telefono, c.email as contact_email, c.nombre as contact_name
        FROM pacientes p
        JOIN contactos c ON c.id = p.id_contacto
        WHERE p.id = %s
        """
        patient = await fetchrow(patient_query, patient_id)

        if not patient:
            return {"found": False, "message": "Paciente no encontrado"}

        # Historial de citas
        appointments_query = """
        SELECT id, fecha_hora, estado, tipo_servicio, notas
        FROM citas
        WHERE id_paciente = %s
        ORDER BY fecha_hora DESC
        LIMIT 5
        """
        appointments = await fetch(appointments_query, patient_id)

        return {
            "found": True,
            "patient": {
                "id": patient["id"],
                "nombre": patient["nombre_completo"],
                "telefono": patient["telefono"],
                "email": patient.get("contact_email"),
                "fecha_nacimiento": (
                    patient["fecha_nacimiento"].isoformat()
                    if patient.get("fecha_nacimiento")
                    else None
                ),
                "alergias": patient.get("alergias"),
                "condiciones": patient.get("condiciones_medicas"),
                "notas": patient.get("notas_clinicas"),
            },
            "citas_recientes": [
                {
                    "id": a["id"],
                    "fecha": a["fecha_hora"].isoformat(),
                    "estado": a["estado"],
                    "servicio": a["tipo_servicio"],
                }
                for a in appointments
            ],
        }

    except Exception as e:
        logger.error(f"Error getting patient info: {e}")
        return {"error": str(e)}


@tool
async def register_patient(
    contact_id: int,
    nombre_completo: str,
    fecha_nacimiento: Optional[str] = None,
    alergias: Optional[str] = None,
    condiciones_medicas: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Registra un nuevo paciente en el sistema.

    Args:
        contact_id: ID del contacto existente
        nombre_completo: Nombre completo del paciente
        fecha_nacimiento: Fecha de nacimiento (YYYY-MM-DD)
        alergias: Alergias conocidas
        condiciones_medicas: Condiciones médicas relevantes

    Returns:
        Diccionario con información del paciente registrado
    """
    logger.info(f"Registering patient: {nombre_completo}")

    try:
        # Verificar que el contacto existe
        contact = await fetchrow(
            "SELECT id, nombre FROM contactos WHERE id = %s", contact_id
        )

        if not contact:
            return {"success": False, "error": "Contacto no encontrado"}

        # Verificar que no existe ya como paciente
        existing = await fetchrow(
            "SELECT id FROM pacientes WHERE id_contacto = %s", contact_id
        )

        if existing:
            return {
                "success": False,
                "error": "El contacto ya está registrado como paciente",
                "patient_id": existing["id"],
            }

        # Parsear fecha si se proporciona
        birth_date = None
        if fecha_nacimiento:
            try:
                birth_date = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
            except ValueError:
                pass

        # Insertar paciente
        query = """
        INSERT INTO pacientes (
            id_contacto, nombre_completo, fecha_nacimiento,
            alergias, condiciones_medicas, fecha_registro
        ) VALUES (%s, %s, %s, %s, %s, NOW())
        RETURNING id
        """

        result = await fetchrow(
            query,
            contact_id,
            nombre_completo,
            birth_date,
            alergias,
            condiciones_medicas,
        )

        # Actualizar tipo de contacto
        await execute(
            "UPDATE contactos SET tipo = 'Paciente' WHERE id = %s", contact_id
        )

        logger.info(f"Patient registered: {result['id']}")

        return {
            "success": True,
            "patient_id": result["id"],
            "message": f"Paciente {nombre_completo} registrado exitosamente",
        }

    except Exception as e:
        logger.error(f"Error registering patient: {e}")
        return {"success": False, "error": str(e)}
