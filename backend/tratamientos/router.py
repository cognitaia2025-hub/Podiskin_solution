"""
Router FastAPI - Módulo de Tratamientos
========================================

Endpoints REST para tratamientos, signos vitales y diagnósticos.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from .models import (
    TratamientoCreate,
    TratamientoUpdate,
    TratamientoResponse,
    SignosVitalesCreate,
    SignosVitalesResponse,
    DiagnosticoCreate,
    DiagnosticoResponse,
    CIE10Response,
)
from . import service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tratamientos"])


# ============================================================================
# TRATAMIENTOS - CRUD
# ============================================================================


@router.get("/tratamientos", response_model=List[TratamientoResponse])
async def listar_tratamientos(
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo")
):
    """Lista todos los tratamientos."""
    try:
        tratamientos = await service.get_tratamientos(activo=activo)
        return tratamientos
    except Exception as e:
        logger.error(f"Error listando tratamientos: {e}")
        raise HTTPException(status_code=500, detail="Error al listar tratamientos")


@router.post("/tratamientos", response_model=TratamientoResponse, status_code=201)
async def crear_tratamiento(tratamiento: TratamientoCreate):
    """Crea un nuevo tratamiento."""
    try:
        result = await service.create_tratamiento(
            codigo_servicio=tratamiento.codigo_servicio,
            nombre_servicio=tratamiento.nombre_servicio,
            descripcion=tratamiento.descripcion,
            precio_base=tratamiento.precio_base,
            duracion_minutos=tratamiento.duracion_minutos,
            requiere_consentimiento=tratamiento.requiere_consentimiento,
            activo=tratamiento.activo,
        )
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
        tratamiento = await service.get_tratamiento(tratamiento_id)
        
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
        # Construir diccionario con campos a actualizar
        updates = tratamiento.model_dump(exclude_unset=True)
        
        if not updates:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron campos para actualizar"
            )
        
        result = await service.update_tratamiento(tratamiento_id, updates)
        
        if not result:
            raise HTTPException(status_code=404, detail="Tratamiento no encontrado")
        
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error actualizando tratamiento: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar tratamiento")


@router.delete("/tratamientos/{tratamiento_id}", status_code=204)
async def eliminar_tratamiento(tratamiento_id: int):
    """Desactiva un tratamiento (soft delete)."""
    try:
        deleted = await service.delete_tratamiento(tratamiento_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Tratamiento no encontrado")
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
        # Calcular IMC si se proporcionan peso y talla
        imc = None
        imc_clasificacion = None
        
        if signos.peso_kg is not None and signos.talla_cm is not None:
            imc = service.calcular_imc(signos.peso_kg, signos.talla_cm)
            imc_clasificacion = service.clasificar_imc(imc)
        
        # Crear signos vitales
        result = await service.create_signos_vitales(
            cita_id=cita_id,
            peso_kg=signos.peso_kg,
            talla_cm=signos.talla_cm,
            imc=imc,
            presion_sistolica=signos.presion_sistolica,
            presion_diastolica=signos.presion_diastolica,
            frecuencia_cardiaca=signos.frecuencia_cardiaca,
            frecuencia_respiratoria=signos.frecuencia_respiratoria,
            temperatura_celsius=signos.temperatura_celsius,
            saturacion_oxigeno=signos.saturacion_oxigeno,
            glucosa_capilar=signos.glucosa_capilar,
        )
        
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
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
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
        # Obtener información de la cita y podólogo
        cita = await service.get_cita_con_podologo(cita_id)
        
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        
        # Buscar descripción del código CIE-10 si se proporciona
        codigo_cie10_descripcion = None
        if diagnostico.codigo_cie10:
            codigo_cie10_descripcion = await service.get_cie10_descripcion(diagnostico.codigo_cie10)
        
        # Crear diagnóstico
        result = await service.create_diagnostico(
            cita_id=cita_id,
            tipo=diagnostico.tipo.value,
            descripcion=diagnostico.descripcion,
            codigo_cie10=diagnostico.codigo_cie10,
            id_podologo=cita["id_podologo"]
        )
        
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
        resultados = await service.search_cie10(search=search, limit=50)
        return resultados
    except Exception as e:
        logger.error(f"Error buscando CIE-10: {e}")
        raise HTTPException(status_code=500, detail="Error al buscar códigos CIE-10")
