"""
FastAPI router for the pacientes module.
Defines REST API endpoints for patients, allergies, and medical history.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
import asyncpg
import logging

from .database import get_db_connection
from .models import (
    PacienteCreate,
    PacienteUpdate,
    PacienteResponse,
    PacienteListResponse,
    PacienteListItem,
    AlergiaCreate,
    AlergiaResponse,
    AlergiaListResponse,
    AntecedenteCreate,
    AntecedenteResponse,
    AntecedenteListResponse,
)
from .service import PacientesService, AlergiasService, AntecedentesService

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


# ============================================================================
# PACIENTES ENDPOINTS
# ============================================================================


@router.get("", response_model=PacienteListResponse)
async def get_pacientes(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    search: Optional[str] = Query(None, description="Search by name or phone"),
    activo: Optional[bool] = Query(True, description="Filter by active status"),
    orden: str = Query(
        "nombre",
        description="Field to order by (nombre, fecha_registro, fecha_nacimiento)",
    ),
    direccion: str = Query("asc", description="Sort direction (asc, desc)"),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Get paginated list of patients.

    **Query Parameters:**
    - `page`: Page number (1-indexed), default 1
    - `limit`: Items per page, default 20, max 100
    - `search`: Search term for name or phone number
    - `activo`: Filter by active status, default true
    - `orden`: Field to order by (nombre, fecha_registro, fecha_nacimiento)
    - `direccion`: Sort direction (asc, desc)

    **Returns:**
    - Paginated list of patients with metadata
    """
    try:
        return await PacientesService.get_pacientes(
            conn=conn,
            page=page,
            limit=limit,
            search=search,
            activo=activo,
            orden=orden,
            direccion=direccion,
        )
    except Exception as e:
        logger.error(f"Error retrieving patients: {e}")
        # Return empty list instead of error
        return {"items": [], "total": 0, "page": page, "limit": limit, "total_pages": 0}


@router.get("/search", response_model=List[PacienteListItem])
async def search_pacientes(
    q: str = Query(..., min_length=2, description="Texto a buscar (nombre o teléfono)"),
    limit: int = Query(10, ge=1, le=50),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Búsqueda optimizada para autocompletado: busca por nombre parcial o teléfono.
    """
    try:
        pattern = f"%{q}%"
        rows = await conn.fetch(
            """
            SELECT id, codigo_paciente, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, telefono_principal
            FROM pacientes
            WHERE (
                primer_nombre ILIKE $1 OR 
                primer_apellido ILIKE $1 OR 
                segundo_apellido ILIKE $1 OR 
                telefono_principal LIKE $1 OR
                codigo_paciente ILIKE $1
            )
            AND activo = TRUE
            ORDER BY primer_apellido, primer_nombre
            LIMIT $2
            """,
            pattern,
            limit,
        )

        results = []
        for r in rows:
            nombre = " ".join(
                filter(
                    None,
                    [
                        r["primer_nombre"],
                        r.get("segundo_nombre"),
                        r["primer_apellido"],
                        r.get("segundo_apellido"),
                    ],
                )
            )
            results.append(
                PacienteListItem(
                    id=r["id"],
                    codigo_paciente=r.get("codigo_paciente"),
                    nombre_completo=nombre,
                    telefono_principal=r["telefono_principal"],
                    email=None,
                    fecha_nacimiento=None,
                    edad=0,
                    ultima_cita=None,
                    total_citas=0,
                    activo=True,
                )
            )

        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{paciente_id}", response_model=PacienteResponse)
async def get_paciente(
    paciente_id: int, conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Get patient by ID.

    **Path Parameters:**
    - `paciente_id`: Patient ID

    **Returns:**
    - Complete patient information

    **Raises:**
    - 404: Patient not found
    """
    try:
        paciente = await PacientesService.get_paciente_by_id(conn, paciente_id)

        if not paciente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with id {paciente_id} not found",
            )

        return paciente
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving patient: {str(e)}",
        )


@router.post("", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
async def create_paciente(
    paciente: PacienteCreate, conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Create a new patient.

    **Request Body:**
    - Patient data following PacienteCreate schema

    **Returns:**
    - Created patient with ID and timestamps

    **Raises:**
    - 400: Validation error (invalid CURP, future birth date, etc.)
    - 409: Conflict (duplicate CURP)
    """
    try:
        # Check for duplicate CURP if provided
        if paciente.curp:
            exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM pacientes WHERE curp = $1)", paciente.curp
            )
            if exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Patient with CURP {paciente.curp} already exists",
                )

        return await PacientesService.create_paciente(conn, paciente)

    except HTTPException:
        raise
    except asyncpg.UniqueViolationError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient with this CURP already exists",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating patient: {str(e)}",
        )


@router.put("/{paciente_id}", response_model=PacienteResponse)
async def update_paciente(
    paciente_id: int,
    paciente: PacienteUpdate,
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Update an existing patient.

    **Path Parameters:**
    - `paciente_id`: Patient ID

    **Request Body:**
    - Patient data following PacienteUpdate schema (all fields optional)

    **Returns:**
    - Updated patient information

    **Raises:**
    - 404: Patient not found
    - 409: Conflict (duplicate CURP)
    """
    try:
        # Check for duplicate CURP if being updated
        if paciente.curp:
            exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM pacientes WHERE curp = $1 AND id != $2)",
                paciente.curp,
                paciente_id,
            )
            if exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Another patient with CURP {paciente.curp} already exists",
                )

        updated = await PacientesService.update_paciente(conn, paciente_id, paciente)

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with id {paciente_id} not found",
            )

        return updated

    except HTTPException:
        raise
    except asyncpg.UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Another patient with this CURP already exists",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating patient: {str(e)}",
        )


@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paciente(
    paciente_id: int, conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Soft delete a patient (set activo = false).

    **Path Parameters:**
    - `paciente_id`: Patient ID

    **Returns:**
    - 204 No Content on success

    **Raises:**
    - 404: Patient not found or already inactive
    """
    try:
        deleted = await PacientesService.delete_paciente(conn, paciente_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with id {paciente_id} not found or already inactive",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting patient: {str(e)}",
        )


# ============================================================================
# ALERGIAS ENDPOINTS
# ============================================================================


@router.get("/{paciente_id}/alergias", response_model=AlergiaListResponse)
async def get_alergias(
    paciente_id: int, conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Get all allergies for a patient.

    **Path Parameters:**
    - `paciente_id`: Patient ID

    **Returns:**
    - List of active allergies for the patient
    """
    try:
        # Verify patient exists
        patient_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pacientes WHERE id = $1)", paciente_id
        )

        if not patient_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with id {paciente_id} not found",
            )

        return await AlergiasService.get_alergias(conn, paciente_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving allergies: {str(e)}",
        )


@router.post(
    "/{paciente_id}/alergias",
    response_model=AlergiaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_alergia(
    paciente_id: int,
    alergia: AlergiaCreate,
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Create a new allergy for a patient.

    **Path Parameters:**
    - `paciente_id`: Patient ID

    **Request Body:**
    - Allergy data following AlergiaCreate schema

    **Returns:**
    - Created allergy with ID and timestamps

    **Raises:**
    - 404: Patient not found
    """
    try:
        return await AlergiasService.create_alergia(conn, paciente_id, alergia)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating allergy: {str(e)}",
        )


# ============================================================================
# ANTECEDENTES MEDICOS ENDPOINTS
# ============================================================================


@router.get("/{paciente_id}/antecedentes", response_model=AntecedenteListResponse)
async def get_antecedentes(
    paciente_id: int, conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Get all medical history entries for a patient.

    **Path Parameters:**
    - `paciente_id`: Patient ID

    **Returns:**
    - List of active medical history entries for the patient
    """
    try:
        # Verify patient exists
        patient_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pacientes WHERE id = $1)", paciente_id
        )

        if not patient_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with id {paciente_id} not found",
            )

        return await AntecedentesService.get_antecedentes(conn, paciente_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving medical history: {str(e)}",
        )


@router.post(
    "/{paciente_id}/antecedentes",
    response_model=AntecedenteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_antecedente(
    paciente_id: int,
    antecedente: AntecedenteCreate,
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Create a new medical history entry for a patient.

    **Path Parameters:**
    - `paciente_id`: Patient ID

    **Request Body:**
    - Medical history data following AntecedenteCreate schema

    **Returns:**
    - Created medical history entry with ID and timestamps

    **Raises:**
    - 404: Patient not found
    """
    try:
        return await AntecedentesService.create_antecedente(
            conn, paciente_id, antecedente
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating medical history entry: {str(e)}",
        )
