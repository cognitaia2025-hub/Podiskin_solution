"""
Router FastAPI - Módulo de Tratamientos
========================================

Endpoints REST para tratamientos, signos vitales y diagnósticos.
"""

import logging
from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query
from pydantic import ValidationError

from .models import (
    TratamientoCreate,
    TratamientoUpdate,
    TratamientoResponse,
    SignosVitalesCreate,
    SignosVitalesResponse,
    DiagnosticoCreate,
    DiagnosticoResponse,
    CIE10Response,
    PodologoInfo,
)
from .database import execute_query, execute_mutation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tratamientos"])


# ============================================================================
# HELPERS
# ============================================================================


def calcular_imc(peso_kg: Decimal, talla_cm: Decimal) -> tuple[Decimal, str]:
    """
    Calcula el IMC y su clasificación.
    
    Args:
        peso_kg: Peso en kilogramos
        talla_cm: Talla en centímetros
        
    Returns:
        Tupla con (IMC, clasificación)
    """
    # Convertir talla a metros
    talla_m = talla_cm / 100
    
    # Calcular IMC: peso / (talla^2)
    imc = peso_kg / (talla_m ** 2)
    
    # Redondear a 2 decimales
    imc = round(imc, 2)
    
    # Clasificar IMC
    if imc < 18.5:
        clasificacion = "Bajo peso"
    elif imc < 25:
        clasificacion = "Normal"
    elif imc < 30:
        clasificacion = "Sobrepeso"
    else:
        clasificacion = "Obesidad"
    
    return imc, clasificacion


# ============================================================================
# TRATAMIENTOS - CRUD
# ============================================================================


@router.get("/tratamientos", response_model=List[TratamientoResponse])
async def listar_tratamientos(
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo")
):
    """Lista todos los tratamientos."""
    try:
        if activo is not None:
            query = """
                SELECT id, codigo_servicio, nombre_servicio, descripcion,
                       precio_base, duracion_minutos, requiere_consentimiento,
                       activo, fecha_registro
                FROM tratamientos
                WHERE activo = %s
                ORDER BY nombre_servicio
            """
            params = (activo,)
        else:
            query = """
                SELECT id, codigo_servicio, nombre_servicio, descripcion,
                       precio_base, duracion_minutos, requiere_consentimiento,
                       activo, fecha_registro
                FROM tratamientos
                ORDER BY nombre_servicio
            """
            params = ()
        
        tratamientos = await execute_query(query, params)
        return tratamientos or []
        
    except Exception as e:
        logger.error(f"Error listando tratamientos: {e}")
        raise HTTPException(status_code=500, detail="Error al listar tratamientos")


@router.post("/tratamientos", response_model=TratamientoResponse, status_code=201)
async def crear_tratamiento(tratamiento: TratamientoCreate):
    """Crea un nuevo tratamiento."""
    try:
        query = """
            INSERT INTO tratamientos (
                codigo_servicio, nombre_servicio, descripcion,
                precio_base, duracion_minutos, requiere_consentimiento, activo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, codigo_servicio, nombre_servicio, descripcion,
                      precio_base, duracion_minutos, requiere_consentimiento,
                      activo, fecha_registro
        """
        params = (
            tratamiento.codigo_servicio,
            tratamiento.nombre_servicio,
            tratamiento.descripcion,
            tratamiento.precio_base,
            tratamiento.duracion_minutos,
            tratamiento.requiere_consentimiento,
            tratamiento.activo,
        )
        
        result = await execute_mutation(query, params, returning=True)
        
        if not result:
            raise HTTPException(status_code=500, detail="Error al crear tratamiento")
        
        return result
        
    except Exception as e:
        logger.error(f"Error creando tratamiento: {e}")
        if "duplicate key" in str(e).lower():
            raise HTTPException(
                status_code=400, 
                detail="El código de servicio ya existe"
            )
        raise HTTPException(status_code=500, detail="Error al crear tratamiento")


@router.get("/tratamientos/{tratamiento_id}", response_model=TratamientoResponse)
async def obtener_tratamiento(tratamiento_id: int):
    """Obtiene un tratamiento por ID."""
    try:
        query = """
            SELECT id, codigo_servicio, nombre_servicio, descripcion,
                   precio_base, duracion_minutos, requiere_consentimiento,
                   activo, fecha_registro
            FROM tratamientos
            WHERE id = %s
        """
        
        tratamiento = await execute_query(query, (tratamiento_id,), fetch_one=True)
        
        if not tratamiento:
            raise HTTPException(status_code=404, detail="Tratamiento no encontrado")
        
        return tratamiento
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo tratamiento: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener tratamiento")


@router.put("/tratamientos/{tratamiento_id}", response_model=TratamientoResponse)
async def actualizar_tratamiento(tratamiento_id: int, tratamiento: TratamientoUpdate):
    """Actualiza un tratamiento existente."""
    try:
        # Verificar que el tratamiento existe
        existing = await execute_query(
            "SELECT id FROM tratamientos WHERE id = %s",
            (tratamiento_id,),
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Tratamiento no encontrado")
        
        # Construir query dinámicamente solo con campos proporcionados
        updates = []
        params = []
        
        if tratamiento.codigo_servicio is not None:
            updates.append("codigo_servicio = %s")
            params.append(tratamiento.codigo_servicio)
        
        if tratamiento.nombre_servicio is not None:
            updates.append("nombre_servicio = %s")
            params.append(tratamiento.nombre_servicio)
        
        if tratamiento.descripcion is not None:
            updates.append("descripcion = %s")
            params.append(tratamiento.descripcion)
        
        if tratamiento.precio_base is not None:
            updates.append("precio_base = %s")
            params.append(tratamiento.precio_base)
        
        if tratamiento.duracion_minutos is not None:
            updates.append("duracion_minutos = %s")
            params.append(tratamiento.duracion_minutos)
        
        if tratamiento.requiere_consentimiento is not None:
            updates.append("requiere_consentimiento = %s")
            params.append(tratamiento.requiere_consentimiento)
        
        if tratamiento.activo is not None:
            updates.append("activo = %s")
            params.append(tratamiento.activo)
        
        if not updates:
            raise HTTPException(
                status_code=400, 
                detail="No se proporcionaron campos para actualizar"
            )
        
        params.append(tratamiento_id)
        
        query = f"""
            UPDATE tratamientos
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, codigo_servicio, nombre_servicio, descripcion,
                      precio_base, duracion_minutos, requiere_consentimiento,
                      activo, fecha_registro
        """
        
        result = await execute_mutation(query, tuple(params), returning=True)
        
        if not result:
            raise HTTPException(status_code=500, detail="Error al actualizar tratamiento")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando tratamiento: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar tratamiento")


@router.delete("/tratamientos/{tratamiento_id}", status_code=204)
async def eliminar_tratamiento(tratamiento_id: int):
    """Desactiva un tratamiento (soft delete)."""
    try:
        # Verificar que el tratamiento existe
        existing = await execute_query(
            "SELECT id FROM tratamientos WHERE id = %s",
            (tratamiento_id,),
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Tratamiento no encontrado")
        
        # Soft delete: marcar como inactivo
        query = "UPDATE tratamientos SET activo = false WHERE id = %s"
        await execute_mutation(query, (tratamiento_id,), returning=False)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando tratamiento: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar tratamiento")


# ============================================================================
# SIGNOS VITALES
# ============================================================================


@router.post("/citas/{cita_id}/signos-vitales", response_model=SignosVitalesResponse, status_code=201)
async def crear_signos_vitales(cita_id: int, signos: SignosVitalesCreate):
    """Crea signos vitales para una cita con cálculo automático de IMC."""
    try:
        # Verificar que la cita existe
        cita = await execute_query(
            "SELECT id FROM citas WHERE id = %s",
            (cita_id,),
            fetch_one=True
        )
        
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        
        # Calcular IMC si se proporcionan peso y talla
        imc = None
        imc_clasificacion = None
        
        if signos.peso_kg is not None and signos.talla_cm is not None:
            imc, imc_clasificacion = calcular_imc(signos.peso_kg, signos.talla_cm)
        
        # Insertar signos vitales
        query = """
            INSERT INTO signos_vitales (
                id_cita, peso_kg, talla_cm, imc,
                ta_sistolica, ta_diastolica,
                frecuencia_cardiaca, frecuencia_respiratoria,
                temperatura_c, saturacion_o2, glucosa_capilar,
                fecha_registro
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id, id_cita, peso_kg, talla_cm, imc,
                      ta_sistolica, ta_diastolica,
                      frecuencia_cardiaca, frecuencia_respiratoria,
                      temperatura_c, saturacion_o2, glucosa_capilar,
                      fecha_registro
        """
        
        params = (
            cita_id,
            signos.peso_kg,
            signos.talla_cm,
            imc,
            signos.presion_sistolica,
            signos.presion_diastolica,
            signos.frecuencia_cardiaca,
            signos.frecuencia_respiratoria,
            signos.temperatura_celsius,
            signos.saturacion_oxigeno,
            signos.glucosa_capilar,
        )
        
        result = await execute_mutation(query, params, returning=True)
        
        if not result:
            raise HTTPException(status_code=500, detail="Error al crear signos vitales")
        
        # Formatear respuesta según especificación
        response = {
            "id": result["id"],
            "id_cita": result["id_cita"],
            "peso_kg": result["peso_kg"],
            "talla_cm": result["talla_cm"],
            "imc": result["imc"],
            "imc_clasificacion": imc_clasificacion,
            "presion_arterial": None,
            "frecuencia_cardiaca": result["frecuencia_cardiaca"],
            "frecuencia_respiratoria": result["frecuencia_respiratoria"],
            "temperatura_celsius": result["temperatura_c"],
            "saturacion_oxigeno": result["saturacion_o2"],
            "glucosa_capilar": result["glucosa_capilar"],
            "fecha_medicion": result["fecha_registro"],
        }
        
        # Formatear presión arterial
        if result["ta_sistolica"] and result["ta_diastolica"]:
            response["presion_arterial"] = f"{result['ta_sistolica']}/{result['ta_diastolica']}"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando signos vitales: {e}")
        raise HTTPException(status_code=500, detail="Error al crear signos vitales")


# ============================================================================
# DIAGNÓSTICOS
# ============================================================================


@router.post("/citas/{cita_id}/diagnosticos", response_model=DiagnosticoResponse, status_code=201)
async def crear_diagnostico(cita_id: int, diagnostico: DiagnosticoCreate):
    """Crea un diagnóstico para una cita."""
    try:
        # Verificar que la cita existe y obtener el podólogo
        cita = await execute_query(
            """
            SELECT c.id, c.id_podologo, u.username as podologo_nombre
            FROM citas c
            JOIN podologos p ON c.id_podologo = p.id
            JOIN usuarios u ON p.id_usuario = u.id
            WHERE c.id = %s
            """,
            (cita_id,),
            fetch_one=True
        )
        
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        
        # Buscar descripción del código CIE-10 si se proporciona
        codigo_cie10_descripcion = None
        if diagnostico.codigo_cie10:
            cie10 = await execute_query(
                "SELECT descripcion FROM catalogo_cie10 WHERE codigo = %s AND activo = true",
                (diagnostico.codigo_cie10,),
                fetch_one=True
            )
            if cie10:
                codigo_cie10_descripcion = cie10["descripcion"]
        
        # Insertar diagnóstico en nota_clinica (simplificado)
        # Nota: En producción deberías insertar en diagnosticos_tratamiento
        # pero como no tenemos id_detalle_cita, usamos nota_clinica como referencia
        
        # Por ahora, crear un registro temporal que cumple con la API
        # En producción, esto debería estar mejor estructurado
        query = """
            INSERT INTO nota_clinica (
                id_cita, 
                motivo_consulta, 
                diagnostico_presuntivo,
                diagnostico_definitivo,
                codigo_cie10_presuntivo_manual,
                codigo_cie10_definitivo_manual,
                elaborado_por
            )
            VALUES (%s, %s, 
                    CASE WHEN %s = 'Presuntivo' THEN %s ELSE NULL END,
                    CASE WHEN %s = 'Definitivo' THEN %s ELSE NULL END,
                    CASE WHEN %s = 'Presuntivo' THEN %s ELSE NULL END,
                    CASE WHEN %s = 'Definitivo' THEN %s ELSE NULL END,
                    %s
            )
            ON CONFLICT (id_cita) DO UPDATE SET
                diagnostico_presuntivo = CASE WHEN %s = 'Presuntivo' THEN %s ELSE nota_clinica.diagnostico_presuntivo END,
                diagnostico_definitivo = CASE WHEN %s = 'Definitivo' THEN %s ELSE nota_clinica.diagnostico_definitivo END,
                codigo_cie10_presuntivo_manual = CASE WHEN %s = 'Presuntivo' THEN %s ELSE nota_clinica.codigo_cie10_presuntivo_manual END,
                codigo_cie10_definitivo_manual = CASE WHEN %s = 'Definitivo' THEN %s ELSE nota_clinica.codigo_cie10_definitivo_manual END
            RETURNING id, id_cita, fecha_elaboracion
        """
        
        params = (
            cita_id,
            diagnostico.descripcion,  # motivo_consulta
            diagnostico.tipo.value,
            diagnostico.descripcion,
            diagnostico.tipo.value,
            diagnostico.descripcion,
            diagnostico.tipo.value,
            diagnostico.codigo_cie10,
            diagnostico.tipo.value,
            diagnostico.codigo_cie10,
            cita["id_podologo"],
            # Para el UPDATE
            diagnostico.tipo.value,
            diagnostico.descripcion,
            diagnostico.tipo.value,
            diagnostico.descripcion,
            diagnostico.tipo.value,
            diagnostico.codigo_cie10,
            diagnostico.tipo.value,
            diagnostico.codigo_cie10,
        )
        
        result = await execute_mutation(query, params, returning=True)
        
        if not result:
            raise HTTPException(status_code=500, detail="Error al crear diagnóstico")
        
        # Formatear respuesta
        response = {
            "id": result["id"],
            "id_cita": result["id_cita"],
            "tipo": diagnostico.tipo.value,
            "descripcion": diagnostico.descripcion,
            "codigo_cie10": diagnostico.codigo_cie10,
            "codigo_cie10_descripcion": codigo_cie10_descripcion,
            "diagnosticado_por": {
                "id": cita["id_podologo"],
                "nombre": cita["podologo_nombre"],
            },
            "fecha_diagnostico": result["fecha_elaboracion"],
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando diagnóstico: {e}")
        raise HTTPException(status_code=500, detail="Error al crear diagnóstico")


# ============================================================================
# CATÁLOGO CIE-10
# ============================================================================


@router.get("/diagnosticos/cie10", response_model=List[CIE10Response])
async def buscar_cie10(
    search: str = Query(..., min_length=1, description="Término de búsqueda")
):
    """Busca códigos CIE-10 por código o descripción."""
    try:
        query = """
            SELECT id, codigo, descripcion, categoria, subcategoria
            FROM catalogo_cie10
            WHERE activo = true
              AND (
                  codigo ILIKE %s
                  OR descripcion ILIKE %s
                  OR categoria ILIKE %s
              )
            ORDER BY codigo
            LIMIT 50
        """
        
        search_pattern = f"%{search}%"
        params = (search_pattern, search_pattern, search_pattern)
        
        resultados = await execute_query(query, params)
        return resultados or []
        
    except Exception as e:
        logger.error(f"Error buscando CIE-10: {e}")
        raise HTTPException(status_code=500, detail="Error al buscar códigos CIE-10")
