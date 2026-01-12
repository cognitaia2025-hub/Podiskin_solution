"""
Service layer for the pacientes module.
Contains business logic and database operations.
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
import asyncpg
from .models import (
    PacienteCreate,
    PacienteUpdate,
    PacienteResponse,
    PacienteListItem,
    PacienteListResponse,
    AlergiaCreate,
    AlergiaResponse,
    AlergiaListResponse,
    AntecedenteCreate,
    AntecedenteResponse,
    AntecedenteListResponse,
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def calculate_age(birth_date: date) -> int:
    """Calculate age from birth date."""
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def build_nombre_completo(
    primer_nombre: str,
    segundo_nombre: Optional[str],
    primer_apellido: str,
    segundo_apellido: Optional[str],
) -> str:
    """Build full name from name components."""
    parts = [primer_nombre]
    if segundo_nombre:
        parts.append(segundo_nombre)
    parts.append(primer_apellido)
    if segundo_apellido:
        parts.append(segundo_apellido)
    return " ".join(parts)


# ============================================================================
# PACIENTES SERVICE
# ============================================================================


class PacientesService:
    """Service class for patient operations."""

    @staticmethod
    async def get_pacientes(
        conn: asyncpg.Connection,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        activo: Optional[bool] = True,
        orden: str = "nombre",
        direccion: str = "asc",
    ) -> PacienteListResponse:
        """
        Get paginated list of patients.

        Args:
            conn: Database connection
            page: Page number (1-indexed)
            limit: Items per page (max 100)
            search: Search term for name or phone
            activo: Filter by active status
            orden: Field to order by
            direccion: Sort direction (asc/desc)

        Returns:
            PacienteListResponse with paginated results
        """
        # Validate and limit page size
        limit = min(limit, 100)
        offset = (page - 1) * limit

        # Build WHERE clause
        where_conditions = []
        params = []
        param_count = 1

        if activo is not None:
            where_conditions.append(f"activo = ${param_count}")
            params.append(activo)
            param_count += 1

        if search:
            where_conditions.append(
                f"(primer_nombre ILIKE ${param_count} OR "
                f"primer_apellido ILIKE ${param_count} OR "
                f"segundo_apellido ILIKE ${param_count} OR "
                f"telefono_principal LIKE ${param_count})"
            )
            params.append(f"%{search}%")
            param_count += 1

        where_clause = (
            " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        )

        # Build ORDER BY clause
        orden_map = {
            "nombre": "primer_apellido, segundo_apellido, primer_nombre",
            "fecha_registro": "fecha_registro",
            "fecha_nacimiento": "fecha_nacimiento",
        }
        orden_field = orden_map.get(orden, "primer_apellido, primer_nombre")
        direccion_sql = "ASC" if direccion.lower() == "asc" else "DESC"

        # Get total count
        count_query = f"SELECT COUNT(*) FROM pacientes{where_clause}"
        total = await conn.fetchval(count_query, *params)

        # Get paginated results
        query = f"""
            SELECT 
                p.id,
                p.primer_nombre,
                p.segundo_nombre,
                p.primer_apellido,
                p.segundo_apellido,
                p.telefono_principal,
                p.email,
                p.fecha_nacimiento,
                p.activo,
                (
                    SELECT MAX(c.fecha_hora_inicio)
                    FROM citas c
                    WHERE c.id_paciente = p.id
                ) as ultima_cita,
                (
                    SELECT COUNT(*)
                    FROM citas c
                    WHERE c.id_paciente = p.id
                ) as total_citas
            FROM pacientes p
            {where_clause}
            ORDER BY {orden_field} {direccion_sql}
            LIMIT ${param_count} OFFSET ${param_count + 1}
        """
        params.extend([limit, offset])

        rows = await conn.fetch(query, *params)

        # Build response items
        items = []
        for row in rows:
            nombre_completo = build_nombre_completo(
                row["primer_nombre"],
                row["segundo_nombre"],
                row["primer_apellido"],
                row["segundo_apellido"],
            )
            edad = calculate_age(row["fecha_nacimiento"])

            items.append(
                PacienteListItem(
                    id=row["id"],
                    codigo_paciente=row.get("codigo_paciente"),
                    nombre_completo=nombre_completo,
                    telefono_principal=row["telefono_principal"],
                    email=row["email"],
                    fecha_nacimiento=row["fecha_nacimiento"],
                    edad=edad,
                    ultima_cita=row["ultima_cita"],
                    total_citas=row["total_citas"] or 0,
                    activo=row["activo"],
                )
            )

        pages = (total + limit - 1) // limit  # Ceiling division

        return PacienteListResponse(
            items=items, total=total, page=page, limit=limit, pages=pages
        )

    @staticmethod
    async def get_paciente_by_id(
        conn: asyncpg.Connection, paciente_id: int
    ) -> Optional[PacienteResponse]:
        """
        Get patient by ID.

        Args:
            conn: Database connection
            paciente_id: Patient ID

        Returns:
            PacienteResponse or None if not found
        """
        query = """
            SELECT 
                p.*,
                (
                    SELECT MAX(c.fecha_hora_inicio)
                    FROM citas c
                    WHERE c.id_paciente = p.id
                ) as ultima_cita,
                (
                    SELECT COUNT(*)
                    FROM citas c
                    WHERE c.id_paciente = p.id
                ) as total_citas
            FROM pacientes p
            WHERE p.id = $1
        """

        row = await conn.fetchrow(query, paciente_id)

        if not row:
            return None

        nombre_completo = build_nombre_completo(
            row["primer_nombre"],
            row["segundo_nombre"],
            row["primer_apellido"],
            row["segundo_apellido"],
        )
        edad = calculate_age(row["fecha_nacimiento"])

        return PacienteResponse(
            id=row["id"],
            codigo_paciente=row.get("codigo_paciente"),
            primer_nombre=row["primer_nombre"],
            segundo_nombre=row["segundo_nombre"],
            primer_apellido=row["primer_apellido"],
            segundo_apellido=row["segundo_apellido"],
            nombre_completo=nombre_completo,
            fecha_nacimiento=row["fecha_nacimiento"],
            edad=edad,
            sexo=row["sexo"],
            curp=row["curp"],
            telefono_principal=row["telefono_principal"],
            telefono_secundario=row["telefono_secundario"],
            email=row["email"],
            calle=row["calle"],
            numero_exterior=row["numero_exterior"],
            numero_interior=row["numero_interior"],
            colonia=row["colonia"],
            ciudad=row["ciudad"],
            estado=row["estado"],
            cp=row["cp"],
            ocupacion=row["ocupacion"],
            estado_civil=row["estado_civil"],
            referencia_como_nos_conocio=row["referencia_como_nos_conocio"],
            activo=row["activo"],
            fecha_registro=row["fecha_registro"],
            fecha_modificacion=row["fecha_modificacion"],
            ultima_cita=row["ultima_cita"],
            total_citas=row["total_citas"] or 0,
        )

    @staticmethod
    async def create_paciente(
        conn: asyncpg.Connection,
        paciente: PacienteCreate,
        creado_por: Optional[int] = None,
    ) -> PacienteResponse:
        """
        Create a new patient.

        Args:
            conn: Database connection
            paciente: Patient data
            creado_por: ID of user creating the patient

        Returns:
            Created PacienteResponse
        """
        # Generate codigo_paciente using PostgreSQL function
        codigo = await conn.fetchval(
            "SELECT generar_codigo_paciente($1, $2, CURRENT_TIMESTAMP)",
            paciente.primer_nombre,
            paciente.primer_apellido,
        )

        query = """
            INSERT INTO pacientes (
                codigo_paciente,
                primer_nombre, segundo_nombre, primer_apellido, segundo_apellido,
                fecha_nacimiento, sexo, curp, telefono_principal, telefono_secundario,
                email, calle, numero_exterior, numero_interior, colonia, ciudad, estado,
                cp, ocupacion, estado_civil, referencia_como_nos_conocio, creado_por
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16,
                $17, $18, $19, $20, $21, $22
            )
            RETURNING id, fecha_registro
        """

        row = await conn.fetchrow(
            query,
            codigo,
            paciente.primer_nombre,
            paciente.segundo_nombre,
            paciente.primer_apellido,
            paciente.segundo_apellido,
            paciente.fecha_nacimiento,
            paciente.sexo,
            paciente.curp,
            paciente.telefono_principal,
            paciente.telefono_secundario,
            paciente.email,
            paciente.calle,
            paciente.numero_exterior,
            paciente.numero_interior,
            paciente.colonia,
            paciente.ciudad,
            paciente.estado,
            paciente.cp,
            paciente.ocupacion,
            paciente.estado_civil,
            paciente.referencia_como_nos_conocio,
            creado_por,
        )

        # Get the created patient
        return await PacientesService.get_paciente_by_id(conn, row["id"])

    @staticmethod
    async def update_paciente(
        conn: asyncpg.Connection,
        paciente_id: int,
        paciente: PacienteUpdate,
        modificado_por: Optional[int] = None,
    ) -> Optional[PacienteResponse]:
        """
        Update an existing patient.

        Args:
            conn: Database connection
            paciente_id: Patient ID
            paciente: Updated patient data
            modificado_por: ID of user modifying the patient

        Returns:
            Updated PacienteResponse or None if not found
        """
        # Check if patient exists
        existing = await PacientesService.get_paciente_by_id(conn, paciente_id)
        if not existing:
            return None

        # Build update fields dynamically
        update_fields = []
        params = []
        param_count = 1

        update_data = paciente.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            update_fields.append(f"{field} = ${param_count}")
            params.append(value)
            param_count += 1

        if not update_fields:
            # No fields to update
            return existing

        # Always update fecha_modificacion and modificado_por
        update_fields.append(f"fecha_modificacion = ${param_count}")
        params.append(datetime.now())
        param_count += 1

        if modificado_por:
            update_fields.append(f"modificado_por = ${param_count}")
            params.append(modificado_por)
            param_count += 1

        params.append(paciente_id)

        query = f"""
            UPDATE pacientes
            SET {", ".join(update_fields)}
            WHERE id = ${param_count}
        """

        await conn.execute(query, *params)

        # Get the updated patient
        return await PacientesService.get_paciente_by_id(conn, paciente_id)

    @staticmethod
    async def delete_paciente(conn: asyncpg.Connection, paciente_id: int) -> bool:
        """
        Soft delete a patient (set activo = false).

        Args:
            conn: Database connection
            paciente_id: Patient ID

        Returns:
            True if deleted, False if not found
        """
        query = """
            UPDATE pacientes
            SET activo = false, fecha_modificacion = $1
            WHERE id = $2 AND activo = true
        """

        result = await conn.execute(query, datetime.now(), paciente_id)

        # Check if any row was updated
        return result.split()[-1] != "0"


# ============================================================================
# ALERGIAS SERVICE
# ============================================================================


class AlergiasService:
    """Service class for allergy operations."""

    @staticmethod
    async def get_alergias(
        conn: asyncpg.Connection, paciente_id: int
    ) -> AlergiaListResponse:
        """
        Get all allergies for a patient.

        Args:
            conn: Database connection
            paciente_id: Patient ID

        Returns:
            AlergiaListResponse with all allergies
        """
        query = """
            SELECT *
            FROM alergias
            WHERE id_paciente = $1 AND activo = true
            ORDER BY fecha_registro DESC
        """

        rows = await conn.fetch(query, paciente_id)

        items = [
            AlergiaResponse(
                id=row["id"],
                id_paciente=row["id_paciente"],
                tipo_alergeno=row["tipo_alergeno"],
                nombre_alergeno=row["nombre_alergeno"],
                reaccion=row["reaccion"],
                severidad=row["severidad"],
                fecha_diagnostico=row["fecha_diagnostico"],
                notas=row["notas"],
                activo=row["activo"],
                fecha_registro=row["fecha_registro"],
            )
            for row in rows
        ]

        return AlergiaListResponse(items=items, total=len(items))

    @staticmethod
    async def create_alergia(
        conn: asyncpg.Connection, paciente_id: int, alergia: AlergiaCreate
    ) -> AlergiaResponse:
        """
        Create a new allergy for a patient.

        Args:
            conn: Database connection
            paciente_id: Patient ID
            alergia: Allergy data

        Returns:
            Created AlergiaResponse
        """
        # Verify patient exists
        patient_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pacientes WHERE id = $1)", paciente_id
        )

        if not patient_exists:
            raise ValueError(f"Patient with id {paciente_id} not found")

        query = """
            INSERT INTO alergias (
                id_paciente, tipo_alergeno, nombre_alergeno, reaccion,
                severidad, fecha_diagnostico, notas
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, fecha_registro
        """

        row = await conn.fetchrow(
            query,
            paciente_id,
            alergia.tipo_alergeno,
            alergia.nombre_alergeno,
            alergia.reaccion,
            alergia.severidad,
            alergia.fecha_diagnostico,
            alergia.notas,
        )

        return AlergiaResponse(
            id=row["id"],
            id_paciente=paciente_id,
            tipo_alergeno=alergia.tipo_alergeno,
            nombre_alergeno=alergia.nombre_alergeno,
            reaccion=alergia.reaccion,
            severidad=alergia.severidad,
            fecha_diagnostico=alergia.fecha_diagnostico,
            notas=alergia.notas,
            activo=True,
            fecha_registro=row["fecha_registro"],
        )


# ============================================================================
# ANTECEDENTES MEDICOS SERVICE
# ============================================================================


class AntecedentesService:
    """Service class for medical history operations."""

    @staticmethod
    async def get_antecedentes(
        conn: asyncpg.Connection, paciente_id: int
    ) -> AntecedenteListResponse:
        """
        Get all medical history entries for a patient.

        Args:
            conn: Database connection
            paciente_id: Patient ID

        Returns:
            AntecedenteListResponse with all entries
        """
        query = """
            SELECT *
            FROM antecedentes_medicos
            WHERE id_paciente = $1 AND activo = true
            ORDER BY tipo_categoria, fecha_registro DESC
        """

        rows = await conn.fetch(query, paciente_id)

        items = [
            AntecedenteResponse(
                id=row["id"],
                id_paciente=row["id_paciente"],
                tipo_categoria=row["tipo_categoria"],
                nombre_enfermedad=row["nombre_enfermedad"],
                parentesco=row["parentesco"],
                fecha_inicio=row["fecha_inicio"],
                descripcion_temporal=row["descripcion_temporal"],
                tratamiento_actual=row["tratamiento_actual"],
                controlado=row["controlado"],
                notas=row["notas"],
                activo=row["activo"],
                fecha_registro=row["fecha_registro"],
            )
            for row in rows
        ]

        return AntecedenteListResponse(items=items, total=len(items))

    @staticmethod
    async def create_antecedente(
        conn: asyncpg.Connection, paciente_id: int, antecedente: AntecedenteCreate
    ) -> AntecedenteResponse:
        """
        Create a new medical history entry for a patient.

        Args:
            conn: Database connection
            paciente_id: Patient ID
            antecedente: Medical history data

        Returns:
            Created AntecedenteResponse
        """
        # Verify patient exists
        patient_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pacientes WHERE id = $1)", paciente_id
        )

        if not patient_exists:
            raise ValueError(f"Patient with id {paciente_id} not found")

        query = """
            INSERT INTO antecedentes_medicos (
                id_paciente, tipo_categoria, nombre_enfermedad, parentesco,
                fecha_inicio, descripcion_temporal, tratamiento_actual, controlado, notas
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id, fecha_registro
        """

        row = await conn.fetchrow(
            query,
            paciente_id,
            antecedente.tipo_categoria,
            antecedente.nombre_enfermedad,
            antecedente.parentesco,
            antecedente.fecha_inicio,
            antecedente.descripcion_temporal,
            antecedente.tratamiento_actual,
            antecedente.controlado,
            antecedente.notas,
        )

        return AntecedenteResponse(
            id=row["id"],
            id_paciente=paciente_id,
            tipo_categoria=antecedente.tipo_categoria,
            nombre_enfermedad=antecedente.nombre_enfermedad,
            parentesco=antecedente.parentesco,
            fecha_inicio=antecedente.fecha_inicio,
            descripcion_temporal=antecedente.descripcion_temporal,
            tratamiento_actual=antecedente.tratamiento_actual,
            controlado=antecedente.controlado,
            notas=antecedente.notas,
            activo=True,
            fecha_registro=row["fecha_registro"],
        )
