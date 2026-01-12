"""
Router FastAPI para gestión de citas
=====================================

Define los endpoints REST para el módulo de citas.
"""

import logging
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status, Depends
from fastapi.responses import JSONResponse
from auth.middleware import get_current_user
from auth.models import User

from .models import (
    CitaCreate,
    CitaUpdate,
    CitaCancel,
    CitaResponse,
    CitaListResponse,
    DisponibilidadResponse,
    PacienteInfo,
    PodologoInfo,
)
from . import service

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(
    prefix="/citas",
    tags=["citas"],
    responses={
        404: {"description": "Recurso no encontrado"},
        409: {"description": "Conflicto de horario"},
        422: {"description": "Error de validación"},
    },
)


# ============================================================================
# UTILIDADES
# ============================================================================


def format_cita_response(cita_data: dict) -> CitaResponse:
    """
    Formatea los datos de una cita del formato de base de datos al modelo de respuesta.
    
    Args:
        cita_data: Diccionario con datos de la cita desde la BD
        
    Returns:
        CitaResponse con los datos formateados
    """
    # Construir objetos relacionados
    paciente = None
    if cita_data.get("paciente_nombre"):
        paciente = PacienteInfo(
            id=cita_data["id_paciente"],
            nombre_completo=cita_data["paciente_nombre"]
        )
    
    podologo = None
    if cita_data.get("podologo_nombre"):
        podologo = PodologoInfo(
            id=cita_data["id_podologo"],
            nombre_completo=cita_data["podologo_nombre"]
        )
    
    return CitaResponse(
        id=cita_data["id"],
        id_paciente=cita_data["id_paciente"],
        id_podologo=cita_data["id_podologo"],
        fecha_hora_inicio=cita_data["fecha_hora_inicio"],
        fecha_hora_fin=cita_data["fecha_hora_fin"],
        tipo_cita=cita_data["tipo_cita"],
        estado=cita_data["estado"],
        motivo_consulta=cita_data.get("motivo_consulta"),
        notas_recepcion=cita_data.get("notas_recepcion"),
        motivo_cancelacion=cita_data.get("motivo_cancelacion"),
        es_primera_vez=cita_data["es_primera_vez"],
        recordatorio_24h_enviado=cita_data["recordatorio_24h_enviado"],
        recordatorio_2h_enviado=cita_data["recordatorio_2h_enviado"],
        fecha_creacion=cita_data["fecha_creacion"],
        fecha_actualizacion=cita_data["fecha_actualizacion"],
        paciente=paciente,
        podologo=podologo,
    )


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get("/disponibilidad", response_model=DisponibilidadResponse)
async def obtener_disponibilidad(
    id_podologo: int = Query(..., gt=0, description="ID del podólogo"),
    fecha: date = Query(..., description="Fecha a consultar (YYYY-MM-DD)")
):
    """
    Obtiene los horarios disponibles para un podólogo en una fecha específica.
    
    Genera slots cada 30 minutos y verifica disponibilidad.
    
    **Ejemplo de uso:**
    ```
    GET /citas/disponibilidad?id_podologo=1&fecha=2024-12-26
    ```
    """
    try:
        disponibilidad = await service.obtener_disponibilidad(id_podologo, fecha)
        return disponibilidad
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error obteniendo disponibilidad: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("", response_model=CitaListResponse)
async def listar_citas(
    id_paciente: Optional[int] = Query(None, gt=0, description="Filtrar por ID de paciente"),
    id_podologo: Optional[int] = Query(None, gt=0, description="Filtrar por ID de podólogo"),
    fecha_inicio: Optional[date] = Query(None, description="Filtrar desde esta fecha"),
    fecha_fin: Optional[date] = Query(None, description="Filtrar hasta esta fecha"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    limit: int = Query(100, gt=0, le=1000, description="Número máximo de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación")
):
    """
    Lista citas con filtros opcionales.
    
    **Ejemplo de uso:**
    ```
    GET /citas?id_paciente=42&estado=Confirmada&limit=10
    ```
    """
    try:
        citas, total = await service.obtener_citas(
            id_paciente=id_paciente,
            id_podologo=id_podologo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado=estado,
            limit=limit,
            offset=offset
        )
        
        # Formatear respuestas
        citas_formateadas = [format_cita_response(cita) for cita in citas]
        
        return CitaListResponse(
            total=total,
            citas=citas_formateadas
        )
    except Exception as e:
        logger.error(f"Error listando citas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/{id_cita}", response_model=CitaResponse)
async def obtener_cita(id_cita: int):
    """
    Obtiene una cita por su ID.
    
    **Ejemplo de uso:**
    ```
    GET /citas/123
    ```
    """
    try:
        cita = await service.obtener_cita_por_id(id_cita)
        
        if not cita:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cita con ID {id_cita} no encontrada"
            )
        
        return format_cita_response(cita)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo cita {id_cita}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("", response_model=CitaResponse, status_code=status.HTTP_201_CREATED)
async def crear_cita(cita: CitaCreate, current_user: User = Depends(get_current_user)):
    """
    Crea una nueva cita.
    
    **Validaciones:**
    - Paciente y podólogo deben existir y estar activos
    - Fecha debe ser al menos 1 hora en el futuro
    - No debe haber conflicto de horario
    - Paciente no debe tener otra cita el mismo día
    
    **Ejemplo de uso:**
    ```json
    POST /citas
    {
      "id_paciente": 42,
      "id_podologo": 1,
      "fecha_hora_inicio": "2024-12-26T10:00:00",
      "tipo_cita": "Consulta",
      "motivo_consulta": "Dolor en el talón"
    }
    ```
    """
    try:
        cita_creada = await service.crear_cita_smart(
            id_paciente=cita.id_paciente,
            nuevo_paciente=(cita.nuevo_paciente.model_dump() if cita.nuevo_paciente else None),
            id_podologo=cita.id_podologo,
            fecha_hora_inicio=cita.fecha_hora_inicio,
            fecha_hora_fin=cita.fecha_hora_fin,
            tipo_cita=cita.tipo_cita.value,
            motivo_consulta=cita.motivo_consulta,
            notas_recepcion=cita.notas_recepcion,
            color_hex=cita.color_hex,
            creado_por=getattr(current_user, 'id', None),
        )
        
        return format_cita_response(cita_creada)
    except ValueError as e:
        # Errores de validación (conflictos, datos inválidos)
        error_msg = str(e)
        
        # Determinar el código de estado apropiado
        if "conflicto" in error_msg.lower():
            status_code = status.HTTP_409_CONFLICT
        else:
            status_code = status.HTTP_400_BAD_REQUEST
        
        raise HTTPException(status_code=status_code, detail=error_msg)
    except Exception as e:
        logger.error(f"Error creando cita: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.put("/{id_cita}", response_model=CitaResponse)
async def actualizar_cita(id_cita: int, cita_update: CitaUpdate):
    """
    Actualiza una cita existente.
    
    Solo se actualizan los campos proporcionados.
    No se pueden actualizar citas completadas o canceladas.
    
    **Ejemplo de uso:**
    ```json
    PUT /citas/123
    {
      "fecha_hora_inicio": "2024-12-26T11:00:00",
      "notas_recepcion": "Paciente solicitó cambio de horario"
    }
    ```
    """
    try:
        # Convertir tipos de enum a string si están presentes
        tipo_cita_str = cita_update.tipo_cita.value if cita_update.tipo_cita else None
        estado_str = cita_update.estado.value if cita_update.estado else None
        
        cita_actualizada = await service.actualizar_cita(
            id_cita=id_cita,
            fecha_hora_inicio=cita_update.fecha_hora_inicio,
            tipo_cita=tipo_cita_str,
            motivo_consulta=cita_update.motivo_consulta,
            notas_recepcion=cita_update.notas_recepcion,
            estado=estado_str,
        )
        
        if not cita_actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cita con ID {id_cita} no encontrada"
            )
        
        return format_cita_response(cita_actualizada)
    except HTTPException:
        raise
    except ValueError as e:
        # Errores de validación
        error_msg = str(e)
        
        if "conflicto" in error_msg.lower():
            status_code = status.HTTP_409_CONFLICT
        else:
            status_code = status.HTTP_400_BAD_REQUEST
        
        raise HTTPException(status_code=status_code, detail=error_msg)
    except Exception as e:
        logger.error(f"Error actualizando cita {id_cita}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.delete("/{id_cita}", response_model=CitaResponse)
async def cancelar_cita_endpoint(id_cita: int, cancelacion: CitaCancel):
    """
    Cancela una cita (soft delete).
    
    Cambia el estado a 'Cancelada' y registra el motivo.
    No se pueden cancelar citas ya completadas o canceladas.
    
    **Ejemplo de uso:**
    ```json
    DELETE /citas/123
    {
      "motivo_cancelacion": "Paciente solicitó cancelación por motivos personales"
    }
    ```
    """
    try:
        cita_cancelada = await service.cancelar_cita(
            id_cita=id_cita,
            motivo_cancelacion=cancelacion.motivo_cancelacion
        )
        
        if not cita_cancelada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cita con ID {id_cita} no encontrada"
            )
        
        return format_cita_response(cita_cancelada)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error cancelando cita {id_cita}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/healthcheck")
async def healthcheck():
    """
    Endpoint de healthcheck para verificar que el módulo de citas esté funcionando.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "module": "citas",
            "timestamp": datetime.now().isoformat()
        }
    )
