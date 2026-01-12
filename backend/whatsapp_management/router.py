"""
Router principal para WhatsApp Management
=========================================

Endpoints para la interfaz de gestión de WhatsApp.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
import logging

from auth import get_current_user, User

from .models import (
    # QR
    QRSessionCreate,
    QRSessionInfo,
    QRSessionUpdate,
    # Conversaciones
    ConversacionesResponse,
    ConversacionDetalle,
    DudaPendienteItem,
    RespuestaAdminCreate,
    # Aprendizajes
    AprendizajeAvanzadoItem,
    AprendizajesResponse,
    AprendizajeAvanzadoCreate,
    AprendizajeAvanzadoUpdate,
    EstadisticasAprendizaje,
)

from . import qr_service, conversation_service, learning_service

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp Management"])
logger = logging.getLogger(__name__)

# ============================================================================
# ENDPOINTS DE QR Y SESIÓN
# ============================================================================


@router.post("/qr/generar", response_model=QRSessionInfo)
async def generar_qr_session(
    payload: QRSessionCreate, current_user: User = Depends(get_current_user)
):
    """
    Genera una nueva sesión de QR para sincronización de WhatsApp.

    **Proceso:**
    1. Solicita QR al cliente Node.js
    2. Almacena sesión en BD
    3. Retorna QR para mostrar en UI

    **Returns:**
    - Información de la sesión con QR code
    """
    try:
        sesion = await qr_service.crear_sesion_qr(
            proveedor=payload.proveedor, user_id=current_user.id
        )
        return sesion
    except Exception as e:
        logger.error(f"Error generando QR: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando QR: {str(e)}",
        )


@router.get("/qr/estado/{session_id}", response_model=QRSessionInfo)
async def get_qr_estado(
    session_id: int, current_user: User = Depends(get_current_user)
):
    """
    Obtiene el estado actual de una sesión de QR.

    **Útil para polling:** El frontend puede llamar este endpoint cada 2-3 segundos
    para verificar si el QR fue escaneado.
    """
    try:
        sesion = await qr_service.get_sesion_qr_by_id(session_id)

        if not sesion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sesión de QR no encontrada",
            )

        return sesion
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estado de QR: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/qr/activa", response_model=Optional[QRSessionInfo])
async def get_qr_activa(current_user: User = Depends(get_current_user)):
    """
    Obtiene la sesión de QR activa (pendiente o conectada).

    **Returns:**
    - Sesión activa o `null` si no hay ninguna
    """
    try:
        sesion = await qr_service.get_sesion_qr_activa()
        return sesion
    except Exception as e:
        logger.error(f"Error obteniendo QR activa: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/qr/{session_id}/estado", response_model=QRSessionInfo)
async def actualizar_estado_qr(
    session_id: int,
    payload: QRSessionUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    Actualiza el estado de una sesión de QR.

    **Uso interno:** El cliente Node.js llama este endpoint cuando detecta
    cambios en el estado de la conexión.
    """
    try:
        sesion = await qr_service.actualizar_estado_sesion_qr(session_id, payload)

        if not sesion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sesión de QR no encontrada",
            )

        return sesion
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando estado de QR: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# ============================================================================
# ENDPOINTS DE CONVERSACIONES
# ============================================================================


@router.get("/conversaciones", response_model=ConversacionesResponse)
async def get_conversaciones(
    limit: int = Query(
        50, ge=1, le=100, description="Límite de conversaciones atendidas"
    ),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene conversaciones divididas en atendidas y escaladas.

    **Returns:**
    - `atendidas`: Conversaciones manejadas por el agente
    - `escaladas`: Dudas que requieren atención humana
    """
    try:
        result = await conversation_service.get_conversaciones_y_escaladas(
            limit=limit, estado=estado
        )
        return result
    except Exception as e:
        logger.error(f"Error obteniendo conversaciones: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/conversaciones/{conversacion_id}", response_model=ConversacionDetalle)
async def get_conversacion_detalle(
    conversacion_id: int, current_user: User = Depends(get_current_user)
):
    """
    Obtiene detalle completo de una conversación con todos sus mensajes.

    **Incluye:**
    - Información del contacto
    - Todos los mensajes (con análisis de sentimiento si existe)
    - Notas internas
    """
    try:
        conversacion = await conversation_service.get_conversacion_detalle(
            conversacion_id
        )

        if not conversacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversación no encontrada",
            )

        # Marcar mensajes como leídos
        await conversation_service.marcar_mensajes_como_leidos(conversacion_id)

        return conversacion
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error obteniendo conversación {conversacion_id}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/conversaciones/{conversacion_id}/marcar-atendida")
async def marcar_conversacion_atendida(
    conversacion_id: int,
    notas: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Marca una conversación como atendida.

    **Efecto:**
    - Actualiza `requiere_atencion` a `false`
    - Registra quién atendió y cuándo
    - Opcionalmente agrega notas internas
    """
    try:
        await conversation_service.marcar_conversacion_atendida(
            conversacion_id=conversacion_id, user_id=current_user.id, notas=notas
        )

        return {"success": True, "message": "Conversación marcada como atendida"}
    except Exception as e:
        logger.error(f"Error marcando conversación como atendida: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/conversaciones/{conversacion_id}/notas")
async def actualizar_notas_conversacion(
    conversacion_id: int, notas: str, current_user: User = Depends(get_current_user)
):
    """
    Actualiza las notas internas de una conversación.
    """
    try:
        await conversation_service.actualizar_notas_conversacion(
            conversacion_id=conversacion_id, notas=notas, user_id=current_user.id
        )

        return {"success": True, "message": "Notas actualizadas"}
    except Exception as e:
        logger.error(f"Error actualizando notas: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# ============================================================================
# ENDPOINTS DE DUDAS ESCALADAS
# ============================================================================


@router.get("/dudas-escaladas", response_model=List[DudaPendienteItem])
async def get_dudas_escaladas(
    solo_pendientes: bool = Query(True, description="Solo dudas pendientes"),
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene lista de dudas escaladas.
    """
    try:
        dudas = await conversation_service.get_dudas_escaladas(
            solo_pendientes=solo_pendientes
        )
        return dudas
    except Exception as e:
        logger.error(f"Error obteniendo dudas escaladas: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/dudas-escaladas/{duda_id}/responder")
async def responder_duda(
    duda_id: int,
    payload: RespuestaAdminCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Responde una duda escalada y opcionalmente genera un aprendizaje.

    **Proceso:**
    1. Actualiza la duda con la respuesta del admin
    2. Si `generar_aprendizaje` es `true`, crea un nuevo aprendizaje
    3. Envía la respuesta al paciente (vía LangGraph - se implementará después)

    **NOTA:** La integración con LangGraph para enviar la respuesta
    se implementará en la siguiente fase.
    """
    try:
        # Por ahora solo creamos el aprendizaje si se solicita
        # La integración con LangGraph para enviar la respuesta se hará después

        if payload.generar_aprendizaje:
            # Obtener la duda
            pool = await conversation_service.get_db_pool()
            duda_query = "SELECT * FROM dudas_pendientes WHERE id = $1"
            duda = await pool.fetchrow(duda_query, duda_id)

            if not duda:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Duda no encontrada"
                )

            # Crear aprendizaje
            aprendizaje_data = AprendizajeAvanzadoCreate(
                pregunta_original=duda["duda"],
                contexto_trigger=payload.resumen_aprendizaje
                or f"Cuando el cliente pregunta sobre: {duda['duda'][:100]}",
                respuesta_sugerida=payload.respuesta,
                respuesta_admin=payload.respuesta,
                tono_cliente=payload.tono_cliente,
                intencion_cliente=payload.intencion_cliente,
                tono_respuesta=payload.tono_respuesta,
                resumen_aprendizaje=payload.resumen_aprendizaje,
                categoria=payload.categoria,
                tags=payload.tags,
            )

            aprendizaje = await learning_service.create_aprendizaje(
                data=aprendizaje_data,
                user_id=current_user.id,
                id_conversacion=duda["id_conversacion"],
                id_duda=duda_id,
            )

            # Actualizar duda
            await pool.execute(
                """
                UPDATE dudas_pendientes
                SET estado = 'respondida',
                    respuesta_admin = $1,
                    fecha_respuesta = CURRENT_TIMESTAMP,
                    atendido_por = $2
                WHERE id = $3
            """,
                payload.respuesta,
                current_user.id,
                duda_id,
            )

            return {
                "success": True,
                "message": "Duda respondida y aprendizaje creado",
                "aprendizaje_id": aprendizaje.id,
            }
        else:
            # Solo actualizar la duda
            pool = await conversation_service.get_db_pool()
            await pool.execute(
                """
                UPDATE dudas_pendientes
                SET estado = 'respondida',
                    respuesta_admin = $1,
                    fecha_respuesta = CURRENT_TIMESTAMP,
                    atendido_por = $2
                WHERE id = $3
            """,
                payload.respuesta,
                current_user.id,
                duda_id,
            )

            return {"success": True, "message": "Duda respondida"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error respondiendo duda {duda_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# ============================================================================
# ENDPOINTS DE APRENDIZAJES
# ============================================================================


@router.get("/aprendizajes", response_model=AprendizajesResponse)
async def get_aprendizajes(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    categoria: Optional[str] = None,
    solo_validados: bool = False,
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene lista paginada de aprendizajes del agente.
    """
    try:
        result = await learning_service.get_aprendizajes(
            page=page,
            per_page=per_page,
            categoria=categoria,
            solo_validados=solo_validados,
        )

        return AprendizajesResponse(**result)
    except Exception as e:
        logger.error(f"Error obteniendo aprendizajes: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/aprendizajes", response_model=AprendizajeAvanzadoItem)
async def create_aprendizaje(
    payload: AprendizajeAvanzadoCreate, current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo aprendizaje manualmente.

    **Sistema de dos fases:**
    - **Fase 1:** Contexto/Trigger (cuándo aplicar)
    - **Fase 2:** Respuesta sugerida (qué responder)
    """
    try:
        aprendizaje = await learning_service.create_aprendizaje(
            data=payload, user_id=current_user.id
        )

        return aprendizaje
    except Exception as e:
        logger.error(f"Error creando aprendizaje: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/aprendizajes/{aprendizaje_id}", response_model=AprendizajeAvanzadoItem)
async def update_aprendizaje(
    aprendizaje_id: int,
    payload: AprendizajeAvanzadoUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    Actualiza un aprendizaje existente.
    """
    try:
        aprendizaje = await learning_service.update_aprendizaje(
            aprendizaje_id=aprendizaje_id, data=payload, user_id=current_user.id
        )

        if not aprendizaje:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aprendizaje no encontrado",
            )

        return aprendizaje
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error actualizando aprendizaje {aprendizaje_id}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/aprendizajes/{aprendizaje_id}", response_model=AprendizajeAvanzadoItem)
async def get_aprendizaje(
    aprendizaje_id: int, current_user: User = Depends(get_current_user)
):
    """
    Obtiene un aprendizaje por ID.
    """
    try:
        aprendizaje = await learning_service.get_aprendizaje_by_id(aprendizaje_id)

        if not aprendizaje:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aprendizaje no encontrado",
            )

        return aprendizaje
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error obteniendo aprendizaje {aprendizaje_id}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/aprendizajes/{aprendizaje_id}")
async def delete_aprendizaje(
    aprendizaje_id: int, current_user: User = Depends(get_current_user)
):
    """
    Elimina un aprendizaje.
    """
    try:
        await learning_service.delete_aprendizaje(aprendizaje_id)
        return {"success": True, "message": "Aprendizaje eliminado"}
    except Exception as e:
        logger.error(
            f"Error eliminando aprendizaje {aprendizaje_id}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get(
    "/aprendizajes/estadisticas/general", response_model=EstadisticasAprendizaje
)
async def get_estadisticas_aprendizaje(current_user: User = Depends(get_current_user)):
    """
    Obtiene estadísticas generales de aprendizajes.

    **Incluye:**
    - Total de aprendizajes
    - Aprendizajes validados
    - Aprendizajes efectivos (efectividad >= 0.6)
    - Promedio de efectividad
    - Distribución por categorías
    - Tonos más comunes
    """
    try:
        stats = await learning_service.get_estadisticas_aprendizaje()
        return stats
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/aprendizajes/{aprendizaje_id}/registrar-uso")
async def registrar_uso_aprendizaje(
    aprendizaje_id: int,
    fue_util: bool = True,
    current_user: User = Depends(get_current_user),
):
    """
    Registra el uso de un aprendizaje y actualiza su efectividad.

    **Uso:** El agente llama este endpoint cuando utiliza un aprendizaje
    para responder a un cliente.
    """
    try:
        await learning_service.registrar_uso_aprendizaje(aprendizaje_id, fue_util)
        return {"success": True, "message": "Uso registrado"}
    except Exception as e:
        logger.error(f"Error registrando uso: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
