"""
Tool: Query Paciente Data
=========================

Consulta datos del paciente desde la base de datos.
"""

import logging
from typing import Dict, Any
from db import get_pool

logger = logging.getLogger(__name__)


async def query_paciente_data(paciente_id: int) -> Dict[str, Any]:
    """
    Obtiene datos completos del paciente.

    Args:
        paciente_id: ID del paciente

    Returns:
        Dict con los datos del paciente
    """
    pool = get_pool()

    try:
        async with pool.acquire() as conn:
            # Datos básicos
            paciente = await conn.fetchrow(
                """
                SELECT 
                    id, nombre, apellido_paterno, apellido_materno,
                    telefono, email, fecha_nacimiento, genero
                FROM pacientes
                WHERE id = $1
                """,
                paciente_id,
            )

            if not paciente:
                return {"error": "Paciente no encontrado"}

            # Alergias
            alergias = await conn.fetch(
                """
                SELECT tipo_alergia, descripcion
                FROM alergias
                WHERE id_paciente = $1 AND activa = true
                """,
                paciente_id,
            )

            # Última cita
            ultima_cita = await conn.fetchrow(
                """
                SELECT fecha_hora, tipo_cita, estado
                FROM citas
                WHERE id_paciente = $1
                ORDER BY fecha_hora DESC
                LIMIT 1
                """,
                paciente_id,
            )

            return {
                "id": paciente["id"],
                "nombre_completo": (
                    f"{paciente['nombre']} "
                    f"{paciente['apellido_paterno']} "
                    f"{paciente['apellido_materno']}"
                ),
                "telefono": paciente["telefono"],
                "email": paciente["email"],
                "alergias": [
                    f"{a['tipo_alergia']}: {a['descripcion']}" for a in alergias
                ],
                "ultima_cita": (
                    {
                        "fecha": ultima_cita["fecha_hora"] if ultima_cita else None,
                        "tipo": ultima_cita["tipo_cita"] if ultima_cita else None,
                        "estado": ultima_cita["estado"] if ultima_cita else None,
                    }
                    if ultima_cita
                    else None
                ),
            }

    except Exception as e:
        logger.error(f"Error consultando paciente: {e}", exc_info=True)
        return {"error": str(e)}
