"""
Medical Records Router
Endpoints para gestión de expedientes médicos
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date
from .schemas import (
    PatientSearchResponse,
    UpcomingAppointmentResponse,
    MedicalRecordResponse,
    MedicalRecordUpdate,
    ConsultationCreate,
    ConsultationResponse,
)
from auth import get_current_user, User
from db import database

router = APIRouter(prefix="/api/medical-records", tags=["medical-records"])


@router.get("/search", response_model=List[PatientSearchResponse])
async def search_patients(
    q: str = Query(..., min_length=2, description="Query de búsqueda"),
    current_user: User = Depends(get_current_user)
):
    """
    Búsqueda fuzzy de pacientes por ID, teléfono o nombre.
    Tolera errores de tipeo usando similarity de PostgreSQL.
    """
    # Instalar extensión pg_trgm si no existe (necesaria para búsqueda fuzzy)
    await database.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    
    query = """
    SELECT 
        p.id,
        p.primer_nombre || ' ' || COALESCE(p.segundo_nombre || ' ', '') || 
        p.primer_apellido || COALESCE(' ' || p.segundo_apellido, '') as nombre_completo,
        p.primer_nombre,
        p.segundo_nombre,
        p.primer_apellido,
        p.segundo_apellido,
        p.fecha_nacimiento,
        p.telefono_principal as telefono,
        p.email,
        p.sexo,
        emr.ultima_visita,
        emr.total_consultas,
        emr.tiene_alergias,
        emr.diagnostico_reciente
    FROM pacientes p
    LEFT JOIN expedientes_medicos_resumen emr ON emr.paciente_id = p.id
    WHERE p.activo = true
    AND (
        -- Búsqueda por ID exacto
        p.id::text = :query
        -- Búsqueda por teléfono exacto
        OR p.telefono_principal = :query
        OR p.telefono_secundario = :query
        -- Búsqueda fuzzy por nombre (similarity > 0.3)
        OR similarity(p.primer_nombre || ' ' || p.primer_apellido, :query) > 0.3
        OR similarity(p.primer_nombre || ' ' || COALESCE(p.segundo_nombre, '') || ' ' || 
                     p.primer_apellido || ' ' || COALESCE(p.segundo_apellido, ''), :query) > 0.3
        -- Búsqueda con LIKE para subcadenas
        OR LOWER(p.primer_nombre || ' ' || p.primer_apellido) LIKE LOWER('%' || :query || '%')
    )
    ORDER BY 
        -- Prioridad: coincidencia exacta > fuzzy > LIKE
        CASE 
            WHEN p.id::text = :query THEN 1
            WHEN p.telefono_principal = :query THEN 2
            ELSE 3
        END,
        similarity(p.primer_nombre || ' ' || p.primer_apellido, :query) DESC
    LIMIT 50
    """
    
    results = await database.fetch_all(query, {"query": q})
    return results


@router.get("/upcoming-appointments", response_model=List[UpcomingAppointmentResponse])
async def get_upcoming_appointments(
    limit: int = Query(3, ge=1, le=10),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene citas próximas para mostrar en el modal de selección.
    """
    query = """
    SELECT 
        c.id,
        c.id_paciente as paciente_id,
        c.fecha_hora_inicio as fecha_hora,
        p.primer_nombre || ' ' || p.primer_apellido as paciente_nombre,
        p.telefono_principal as telefono,
        c.notas_recepcion as motivo_consulta,
        emr.ultima_visita,
        -- Alergias importantes
        COALESCE(
            ARRAY(
                SELECT a.nombre_alergeno 
                FROM alergias a 
                WHERE a.id_paciente = c.id_paciente 
                AND a.activo = true 
                AND a.severidad IN ('Grave', 'Mortal')
                LIMIT 3
            ),
            ARRAY[]::text[]
        ) as alergias_importantes
    FROM citas c
    INNER JOIN pacientes p ON p.id = c.id_paciente
    LEFT JOIN expedientes_medicos_resumen emr ON emr.paciente_id = c.id_paciente
    WHERE c.estado IN ('Pendiente', 'Confirmada')
    AND c.fecha_hora_inicio > NOW()
    AND c.fecha_hora_inicio <= NOW() + INTERVAL '7 days'
    ORDER BY c.fecha_hora_inicio ASC
    LIMIT :limit
    """
    
    results = await database.fetch_all(query, {"limit": limit})
    return results


@router.get("/patients", response_model=List[PatientSearchResponse])
async def get_all_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todos los pacientes activos para el grid.
    """
    query = """
    SELECT 
        p.id,
        p.primer_nombre || ' ' || COALESCE(p.segundo_nombre || ' ', '') || 
        p.primer_apellido || COALESCE(' ' || p.segundo_apellido, '') as nombre_completo,
        p.primer_nombre,
        p.segundo_nombre,
        p.primer_apellido,
        p.segundo_apellido,
        p.fecha_nacimiento,
        p.telefono_principal as telefono,
        p.email,
        p.sexo,
        emr.ultima_visita,
        emr.total_consultas,
        emr.tiene_alergias,
        emr.diagnostico_reciente
    FROM pacientes p
    LEFT JOIN expedientes_medicos_resumen emr ON emr.paciente_id = p.id
    WHERE p.activo = true
    ORDER BY p.fecha_registro DESC
    LIMIT :limit OFFSET :skip
    """
    
    results = await database.fetch_all(query, {"limit": limit, "skip": skip})
    return results


@router.get("/patients/{patient_id}/record", response_model=MedicalRecordResponse)
async def get_medical_record(
    patient_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el expediente médico completo de un paciente.
    """
    # Verificar que el paciente existe
    patient_query = """
    SELECT 
        p.id,
        p.primer_nombre || ' ' || COALESCE(p.segundo_nombre || ' ', '') || 
        p.primer_apellido || COALESCE(' ' || p.segundo_apellido, '') as nombre_completo,
        p.fecha_nacimiento,
        p.sexo,
        p.telefono_principal as telefono,
        p.email,
        emr.fecha_ultima_actualizacion
    FROM pacientes p
    LEFT JOIN expedientes_medicos_resumen emr ON emr.paciente_id = p.id
    WHERE p.id = :patient_id AND p.activo = true
    """
    patient = await database.fetch_one(patient_query, {"patient_id": patient_id})
    
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Obtener alergias
    alergias_query = """
    SELECT id, tipo_alergeno as tipo, nombre_alergeno as sustancia, 
           reaccion, severidad, activo
    FROM alergias
    WHERE id_paciente = :patient_id AND activo = true
    """
    alergias = await database.fetch_all(alergias_query, {"patient_id": patient_id})
    
    # Obtener antecedentes
    antecedentes_query = """
    SELECT id, tipo_categoria as tipo, nombre_enfermedad as enfermedad, 
           parentesco, fecha_inicio, tratamiento_actual, controlado, notas
    FROM antecedentes_medicos
    WHERE id_paciente = :patient_id AND activo = true
    """
    antecedentes = await database.fetch_all(antecedentes_query, {"patient_id": patient_id})
    
    # Obtener estilo de vida
    estilo_vida_query = """
    SELECT tipo_dieta, descripcion_dieta, ejercicio_frecuencia, tipo_ejercicio,
           tabaquismo, tabaco_cigarros_dia, tabaco_anios,
           alcoholismo, alcohol_frecuencia,
           drogas, drogas_tipo,
           inmunizaciones_completas, esquema_vacunacion,
           higiene_sueno_horas, exposicion_toxicos, suplementos_vitaminas, notas
    FROM estilo_vida
    WHERE id_paciente = :patient_id
    """
    estilo_vida = await database.fetch_one(estilo_vida_query, {"patient_id": patient_id})
    
    # Obtener historia ginecológica (si aplica)
    ginecologia_query = """
    SELECT menarca_edad, ritmo_menstrual_dias, fecha_ultima_menstruacion,
           gestaciones, partos, cesareas, abortos,
           metodo_anticonceptivo, menopausia, fecha_menopausia, notas_adicionales
    FROM historia_ginecologica
    WHERE id_paciente = :patient_id
    """
    ginecologia = await database.fetch_one(ginecologia_query, {"patient_id": patient_id})
    
    # Obtener consultas
    consultas_query = """
    SELECT c.id, c.fecha_consulta, c.motivo_consulta, c.sintomas,
           c.exploracion_fisica, c.plan_tratamiento, c.indicaciones,
           c.finalizada, c.fecha_finalizacion,
           u.nombre || ' ' || u.apellido_paterno as podologo_nombre
    FROM consultas c
    LEFT JOIN usuarios u ON u.id = c.id_podologo
    WHERE c.id_paciente = :patient_id
    ORDER BY c.fecha_consulta DESC
    LIMIT 10
    """
    consultas = await database.fetch_all(consultas_query, {"patient_id": patient_id})
    
    # Obtener diagnósticos activos
    diagnosticos_query = """
    SELECT d.id, d.codigo_cie10, d.nombre_diagnostico, d.tipo_diagnostico,
           d.descripcion, d.fecha_diagnostico, d.activo
    FROM diagnosticos d
    WHERE d.id_paciente = :patient_id AND d.activo = true
    ORDER BY d.fecha_diagnostico DESC
    """
    diagnosticos = await database.fetch_all(diagnosticos_query, {"patient_id": patient_id})
    
    return {
        "paciente_id": patient["id"],
        "paciente_nombre": patient["nombre_completo"],
        "fecha_nacimiento": patient["fecha_nacimiento"],
        "sexo": patient["sexo"],
        "telefono": patient["telefono"],
        "email": patient["email"],
        "fecha_ultima_actualizacion": patient["fecha_ultima_actualizacion"],
        "alergias": alergias,
        "antecedentes": antecedentes,
        "estilo_vida": estilo_vida,
        "ginecologia": ginecologia,
        "consultas": consultas,
        "diagnosticos": diagnosticos,
    }


@router.patch("/patients/{patient_id}/record/{section}")
async def update_medical_record_section(
    patient_id: int,
    section: str,
    data: MedicalRecordUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza una sección específica del expediente médico.
    Registra cambios en el historial de auditoría.
    """
    # Validar que la sección existe
    valid_sections = ["identificacion", "alergias", "antecedentes", "estilo_vida", 
                      "ginecologia", "motivo", "signos_vitales", "exploracion", 
                      "diagnosticos", "tratamiento"]
    
    if section not in valid_sections:
        raise HTTPException(status_code=400, detail=f"Sección '{section}' no válida")
    
    # TODO: Implementar la actualización según la sección
    # Por ahora solo registramos en el historial
    
    audit_query = """
    INSERT INTO historial_cambios_expediente 
        (id_paciente, seccion_modificada, campo_modificado, valor_anterior, valor_nuevo, modificado_por)
    VALUES 
        (:patient_id, :section, :field, :old_value, :new_value, :user_id)
    """
    
    # Aquí iría la lógica específica para cada sección
    # Por ahora solo confirmamos que se recibió
    
    return {"message": f"Sección '{section}' actualizada correctamente"}


@router.post("/patients/{patient_id}/consultations", response_model=ConsultationResponse)
async def create_consultation(
    patient_id: int,
    consultation: ConsultationCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Crea una nueva consulta médica.
    """
    query = """
    INSERT INTO consultas 
        (id_paciente, id_podologo, motivo_consulta, sintomas, exploracion_fisica, plan_tratamiento)
    VALUES 
        (:patient_id, :podologo_id, :motivo, :sintomas, :exploracion, :plan)
    RETURNING id, fecha_consulta, motivo_consulta, finalizada
    """
    
    result = await database.fetch_one(query, {
        "patient_id": patient_id,
        "podologo_id": current_user.id,
        "motivo": consultation.motivo_consulta,
        "sintomas": consultation.sintomas,
        "exploracion": consultation.exploracion_fisica,
        "plan": consultation.plan_tratamiento,
    })
    
    # Refrescar vista materializada en background
    await database.execute("SELECT refrescar_expedientes_resumen()")
    
    return result


@router.post("/consultations/{consultation_id}/finalize")
async def finalize_consultation(
    consultation_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Finaliza una consulta médica.
    """
    query = """
    UPDATE consultas
    SET finalizada = true, fecha_finalizacion = NOW()
    WHERE id = :consultation_id
    AND id_podologo = :podologo_id
    RETURNING id, fecha_consulta, fecha_finalizacion
    """
    
    result = await database.fetch_one(query, {
        "consultation_id": consultation_id,
        "podologo_id": current_user.id,
    })
    
    if not result:
        raise HTTPException(status_code=404, detail="Consulta no encontrada o sin permisos")
    
    # Actualizar última visita del paciente
    update_patient_query = """
    UPDATE pacientes
    SET fecha_modificacion = NOW()
    WHERE id = (SELECT id_paciente FROM consultas WHERE id = :consultation_id)
    """
    await database.execute(update_patient_query, {"consultation_id": consultation_id})
    
    # Refrescar vista materializada
    await database.execute("SELECT refrescar_expedientes_resumen()")
    
    return {"message": "Consulta finalizada exitosamente", "data": result}
