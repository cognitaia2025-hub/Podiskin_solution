"""
Router de Gestión de Pacientes por Podólogo
============================================
Endpoints para gestionar pacientes asignados y podólogos interinos
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from auth.middleware import get_current_user
from auth.models import User
from db import get_pool, get_connection, release_connection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/podologos", tags=["Gestión de Pacientes por Podólogo"])


# ========================================================================
# HELPER PARA CONEXIÓN A BD (usando pool centralizado AsyncPG)
# ========================================================================


async def get_db_connection():
    """
    Obtiene una conexión a la base de datos desde el pool centralizado.
    """
    pool = get_pool()
    return await pool.acquire()


# ========================================================================
# MODELOS
# ========================================================================


class PatientWithInterino(BaseModel):
    """Paciente con información de podólogo interino"""

    paciente_id: int
    nombre_completo: str
    telefono: Optional[str]
    ultimo_tratamiento: Optional[str]
    fecha_ultimo_tratamiento: Optional[str]
    tiene_interino: bool
    podologo_interino_id: Optional[int]
    podologo_interino_nombre: Optional[str]


class AvailablePodologo(BaseModel):
    """Podólogo disponible para asignación"""

    id: int
    nombre_completo: str
    rol: str


class AssignInterinoRequest(BaseModel):
    """Request para asignar podólogo interino"""

    paciente_id: int
    podologo_interino_id: Optional[int]  # None para quitar
    fecha_fin: Optional[datetime] = None
    motivo: Optional[str] = None


# ========================================================================
# ENDPOINTS
# ========================================================================


@router.get("/{podologo_id}/patients", response_model=List[PatientWithInterino])
async def get_podologo_patients(
    podologo_id: int, current_user: User = Depends(get_current_user)
):
    """
    Obtiene todos los pacientes asignados a un podólogo.

    Incluye información sobre podólogos interinos asignados.

    **Permisos:** Admin o el mismo podólogo
    """
    # Validar permisos
    if current_user.rol != "Admin" and current_user.id != podologo_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver pacientes de otro podólogo",
        )

    conn = None
    try:
        conn = await get_db_connection()
        
        # Usar función de BD con AsyncPG (nota: %s lo cambiamos a $1)
        rows = await conn.fetch(
            "SELECT * FROM get_pacientes_podologo($1)", podologo_id
        )

        patients = [
            PatientWithInterino(
                paciente_id=row["paciente_id"],
                nombre_completo=row["nombre_completo"],
                telefono=row["telefono"],
                ultimo_tratamiento=row["ultimo_tratamiento"],
                fecha_ultimo_tratamiento=(
                    row["fecha_ultimo_tratamiento"].isoformat()
                    if row["fecha_ultimo_tratamiento"]
                    else None
                ),
                tiene_interino=row["tiene_interino"],
                podologo_interino_id=row["podologo_interino_id"],
                podologo_interino_nombre=row["podologo_interino_nombre"],
            )
            for row in rows
        ]

        logger.info(f"Retrieved {len(patients)} patients for podologo {podologo_id}")
        return patients

    except Exception as e:
        logger.error(f"Error fetching patients for podologo {podologo_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener pacientes: {str(e)}",
        )
    finally:
        if conn:
            await release_connection(conn)


@router.get("/available", response_model=List[AvailablePodologo])
async def get_available_podologos(
    exclude_podologo_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene lista de podólogos disponibles para asignación como interinos.

    **Query Params:**
    - exclude_podologo_id: ID del podólogo a excluir (usualmente el oficial)

    **Permisos:** Admin
    """
    if current_user.rol != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Admin puede consultar podólogos disponibles",
        )

    try:
        conn = await get_db_connection()
        
        rows = await conn.fetch(
            """
            SELECT id, nombre_completo, rol
            FROM usuarios
            WHERE rol = 'Podologo'
                AND activo = TRUE
                AND ($1::INTEGER IS NULL OR id != $1)
            ORDER BY nombre_completo
            """,
            exclude_podologo_id,
        )

        podologos = [
            AvailablePodologo(
                id=row["id"], nombre_completo=row["nombre_completo"], rol=row["rol"]
            )
            for row in rows
        ]

        return podologos

    except Exception as e:
        logger.error(f"Error fetching available podologos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener podólogos: {str(e)}",
        )
    finally:
        if conn:
            await release_connection(conn)


@router.post("/{podologo_id}/assign-interino")
async def assign_interino_to_patient(
    podologo_id: int,
    assignment: AssignInterinoRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Asigna un podólogo interino a un paciente específico.

    **Permisos:** Solo Admin
    """
    if current_user.rol != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Admin puede asignar podólogos interinos",
        )

    conn = None
    try:
        conn = await get_db_connection()

        if assignment.podologo_interino_id is None:
            # Quitar podólogo interino
            result = await conn.fetchval(
                "SELECT quitar_podologo_interino($1)", assignment.paciente_id
            )

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No se encontró asignación interina para quitar",
                )

            logger.info(
                f"Admin {current_user.nombre_usuario} quitó interino "
                f"de paciente {assignment.paciente_id}"
            )

            return {
                "message": "Podólogo interino removido correctamente",
                "paciente_id": assignment.paciente_id,
            }
        else:
            # Asignar podólogo interino
            asignacion_id = await conn.fetchval(
                """
                SELECT asignar_podologo_interino($1, $2, $3, $4, $5, $6)
                """,
                assignment.paciente_id,
                podologo_id,
                assignment.podologo_interino_id,
                assignment.fecha_fin,
                assignment.motivo,
                current_user.id,
            )

            logger.info(
                f"Admin {current_user.nombre_usuario} asignó podólogo interino "
                f"{assignment.podologo_interino_id} a paciente {assignment.paciente_id}"
            )

            return {
                "message": "Podólogo interino asignado correctamente",
                "asignacion_id": asignacion_id,
                "paciente_id": assignment.paciente_id,
                "podologo_interino_id": assignment.podologo_interino_id,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error asignando podólogo interino: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    finally:
        if conn:
            await release_connection(conn)
