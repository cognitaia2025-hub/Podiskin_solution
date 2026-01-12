"""
Servicios para gestión de aprendizajes del agente
=================================================

Maneja CRUD de aprendizajes y búsqueda.
NO incluye integración con LangGraph (eso se manejará por separado).
"""

import asyncpg
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from db import get_pool
from .models import (
    AprendizajeAvanzadoItem,
    AprendizajeAvanzadoCreate,
    AprendizajeAvanzadoUpdate,
    AprendizajesResponse,
    EstadisticasAprendizaje,
    OrigenAprendizaje,
)

logger = logging.getLogger(__name__)

# ============================================================================
# FUNCIONES DE APRENDIZAJES
# ============================================================================


async def get_aprendizajes(
    page: int = 1,
    per_page: int = 20,
    categoria: Optional[str] = None,
    solo_validados: bool = False,
) -> Dict[str, Any]:
    """
    Obtiene lista paginada de aprendizajes.

    Args:
        page: Número de página
        per_page: Items por página
        categoria: Filtrar por categoría
        solo_validados: Si True, solo retorna aprendizajes validados

    Returns:
        Dict con aprendizajes y metadata de paginación
    """
    pool = get_pool()

    offset = (page - 1) * per_page

    query = """
        SELECT 
            id,
            pregunta_original,
            contexto_trigger,
            palabras_clave,
            respuesta_sugerida,
            respuesta_admin,
            tono_cliente,
            intencion_cliente,
            tono_respuesta,
            resumen_aprendizaje,
            categoria,
            tags,
            veces_utilizado,
            efectividad,
            validado,
            version,
            origen,
            fecha_creacion,
            fecha_actualizacion,
            fecha_ultimo_uso
        FROM aprendizajes_agente
        WHERE ($1::text IS NULL OR categoria = $1)
        AND ($2 = false OR validado = true)
        ORDER BY fecha_creacion DESC
        LIMIT $3 OFFSET $4
    """

    count_query = """
        SELECT COUNT(*) as total
        FROM aprendizajes_agente
        WHERE ($1::text IS NULL OR categoria = $1)
        AND ($2 = false OR validado = true)
    """

    try:
        rows = await pool.fetch(query, categoria, solo_validados, per_page, offset)
        count_row = await pool.fetchrow(count_query, categoria, solo_validados)

        aprendizajes = [AprendizajeAvanzadoItem(**dict(row)) for row in rows]
        total = count_row["total"]
        total_pages = (total + per_page - 1) // per_page

        return {
            "aprendizajes": aprendizajes,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
        }
    except Exception as e:
        logger.error(f"Error obteniendo aprendizajes: {e}", exc_info=True)
        raise


async def get_aprendizaje_by_id(
    aprendizaje_id: int,
) -> Optional[AprendizajeAvanzadoItem]:
    """
    Obtiene un aprendizaje por ID.

    Args:
        aprendizaje_id: ID del aprendizaje

    Returns:
        Aprendizaje o None si no existe
    """
    pool = get_pool()

    query = """
        SELECT 
            id,
            pregunta_original,
            contexto_trigger,
            palabras_clave,
            respuesta_sugerida,
            respuesta_admin,
            tono_cliente,
            intencion_cliente,
            tono_respuesta,
            resumen_aprendizaje,
            categoria,
            tags,
            veces_utilizado,
            efectividad,
            validado,
            version,
            origen,
            fecha_creacion,
            fecha_actualizacion,
            fecha_ultimo_uso
        FROM aprendizajes_agente
        WHERE id = $1
    """

    try:
        row = await pool.fetchrow(query, aprendizaje_id)

        if not row:
            return None

        return AprendizajeAvanzadoItem(**dict(row))
    except Exception as e:
        logger.error(
            f"Error obteniendo aprendizaje {aprendizaje_id}: {e}", exc_info=True
        )
        raise


async def create_aprendizaje(
    data: AprendizajeAvanzadoCreate,
    user_id: Optional[int] = None,
    id_conversacion: Optional[int] = None,
    id_duda: Optional[int] = None,
) -> AprendizajeAvanzadoItem:
    """
    Crea un nuevo aprendizaje.

    Args:
        data: Datos del aprendizaje
        user_id: ID del usuario que crea
        id_conversacion: ID de conversación relacionada
        id_duda: ID de duda pendiente relacionada

    Returns:
        Aprendizaje creado
    """
    pool = get_pool()

    try:
        query = """
            INSERT INTO aprendizajes_agente (
                pregunta_original,
                contexto_trigger,
                palabras_clave,
                respuesta_sugerida,
                respuesta_admin,
                tono_cliente,
                intencion_cliente,
                tono_respuesta,
                resumen_aprendizaje,
                categoria,
                tags,
                id_conversacion,
                id_duda_pendiente,
                origen,
                creado_por
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            RETURNING 
                id,
                pregunta_original,
                contexto_trigger,
                palabras_clave,
                respuesta_sugerida,
                respuesta_admin,
                tono_cliente,
                intencion_cliente,
                tono_respuesta,
                resumen_aprendizaje,
                categoria,
                tags,
                veces_utilizado,
                efectividad,
                validado,
                version,
                origen,
                fecha_creacion,
                fecha_actualizacion,
                fecha_ultimo_uso
        """

        origen = OrigenAprendizaje.ESCALAMIENTO if id_duda else OrigenAprendizaje.MANUAL

        row = await pool.fetchrow(
            query,
            data.pregunta_original,
            data.contexto_trigger,
            data.palabras_clave,
            data.respuesta_sugerida,
            data.respuesta_admin,
            data.tono_cliente.value if data.tono_cliente else None,
            data.intencion_cliente.value if data.intencion_cliente else None,
            data.tono_respuesta.value if data.tono_respuesta else None,
            data.resumen_aprendizaje,  # Si es None, el trigger lo auto-genera
            data.categoria,
            data.tags,
            id_conversacion,
            id_duda,
            origen.value,
            user_id,
        )

        # Actualizar duda pendiente si existe
        if id_duda:
            await pool.execute(
                """
                UPDATE dudas_pendientes
                SET aprendizaje_generado = true,
                    id_aprendizaje = $1
                WHERE id = $2
            """,
                row["id"],
                id_duda,
            )

        logger.info(f"Aprendizaje creado: {row['id']}")

        return AprendizajeAvanzadoItem(**dict(row))

    except Exception as e:
        logger.error(f"Error creando aprendizaje: {e}", exc_info=True)
        raise


async def update_aprendizaje(
    aprendizaje_id: int, data: AprendizajeAvanzadoUpdate, user_id: Optional[int] = None
) -> Optional[AprendizajeAvanzadoItem]:
    """
    Actualiza un aprendizaje existente.

    Args:
        aprendizaje_id: ID del aprendizaje
        data: Datos a actualizar
        user_id: ID del usuario que actualiza

    Returns:
        Aprendizaje actualizado o None si no existe
    """
    pool = get_pool()

    try:
        # Construir query dinámicamente
        updates = []
        params = []
        param_count = 1

        if data.contexto_trigger is not None:
            updates.append(f"contexto_trigger = ${param_count}")
            params.append(data.contexto_trigger)
            param_count += 1

        if data.respuesta_sugerida is not None:
            updates.append(f"respuesta_sugerida = ${param_count}")
            params.append(data.respuesta_sugerida)
            param_count += 1

        if data.resumen_aprendizaje is not None:
            updates.append(f"resumen_aprendizaje = ${param_count}")
            params.append(data.resumen_aprendizaje)
            param_count += 1

        if data.categoria is not None:
            updates.append(f"categoria = ${param_count}")
            params.append(data.categoria)
            param_count += 1

        if data.tags is not None:
            updates.append(f"tags = ${param_count}")
            params.append(data.tags)
            param_count += 1

        if data.palabras_clave is not None:
            updates.append(f"palabras_clave = ${param_count}")
            params.append(data.palabras_clave)
            param_count += 1

        if data.tono_cliente is not None:
            updates.append(f"tono_cliente = ${param_count}")
            params.append(data.tono_cliente.value)
            param_count += 1

        if data.intencion_cliente is not None:
            updates.append(f"intencion_cliente = ${param_count}")
            params.append(data.intencion_cliente.value)
            param_count += 1

        if data.tono_respuesta is not None:
            updates.append(f"tono_respuesta = ${param_count}")
            params.append(data.tono_respuesta.value)
            param_count += 1

        if data.validado is not None:
            updates.append(f"validado = ${param_count}")
            params.append(data.validado)
            param_count += 1

            if data.validado and user_id:
                updates.append(f"validado_por = ${param_count}")
                params.append(user_id)
                param_count += 1
                updates.append("fecha_validacion = CURRENT_TIMESTAMP")

        if user_id and data.validado is None:
            updates.append(f"modificado_por = ${param_count}")
            params.append(user_id)
            param_count += 1

        if not updates:
            # No hay nada que actualizar
            return await get_aprendizaje_by_id(aprendizaje_id)

        # El trigger se encarga de actualizar fecha_actualizacion
        params.append(aprendizaje_id)

        query = f"""
            UPDATE aprendizajes_agente
            SET {', '.join(updates)}
            WHERE id = ${param_count}
            RETURNING 
                id,
                pregunta_original,
                contexto_trigger,
                palabras_clave,
                respuesta_sugerida,
                respuesta_admin,
                tono_cliente,
                intencion_cliente,
                tono_respuesta,
                resumen_aprendizaje,
                categoria,
                tags,
                veces_utilizado,
                efectividad,
                validado,
                version,
                origen,
                fecha_creacion,
                fecha_actualizacion,
                fecha_ultimo_uso
        """

        row = await pool.fetchrow(query, *params)

        if not row:
            return None

        logger.info(f"Aprendizaje {aprendizaje_id} actualizado")

        return AprendizajeAvanzadoItem(**dict(row))

    except Exception as e:
        logger.error(
            f"Error actualizando aprendizaje {aprendizaje_id}: {e}", exc_info=True
        )
        raise


async def delete_aprendizaje(aprendizaje_id: int) -> bool:
    """
    Elimina un aprendizaje.

    Args:
        aprendizaje_id: ID del aprendizaje

    Returns:
        True si se eliminó correctamente
    """
    pool = get_pool()

    try:
        query = "DELETE FROM aprendizajes_agente WHERE id = $1"
        await pool.execute(query, aprendizaje_id)
        logger.info(f"Aprendizaje {aprendizaje_id} eliminado")
        return True
    except Exception as e:
        logger.error(
            f"Error eliminando aprendizaje {aprendizaje_id}: {e}", exc_info=True
        )
        raise


async def get_estadisticas_aprendizaje() -> EstadisticasAprendizaje:
    """
    Obtiene estadísticas generales de aprendizajes.

    Returns:
        Estadísticas agregadas
    """
    pool = get_pool()

    try:
        # Estadísticas generales
        stats_query = """
            SELECT 
                COUNT(*) as total_aprendizajes,
                COUNT(*) FILTER (WHERE validado = true) as aprendizajes_validados,
                COUNT(*) FILTER (WHERE efectividad >= 0.6 AND validado = true) as aprendizajes_efectivos,
                AVG(efectividad) FILTER (WHERE validado = true) as promedio_efectividad
            FROM aprendizajes_agente
        """

        stats_row = await pool.fetchrow(stats_query)

        # Categorías
        cat_query = """
            SELECT categoria, COUNT(*) as count
            FROM aprendizajes_agente
            WHERE categoria IS NOT NULL
            GROUP BY categoria
            ORDER BY count DESC
        """

        cat_rows = await pool.fetch(cat_query)
        categorias = {row["categoria"]: row["count"] for row in cat_rows}

        # Tonos más comunes
        tono_query = """
            SELECT tono_cliente, COUNT(*) as count
            FROM aprendizajes_agente
            WHERE tono_cliente IS NOT NULL
            GROUP BY tono_cliente
            ORDER BY count DESC
        """

        tono_rows = await pool.fetch(tono_query)
        tonos_mas_comunes = {row["tono_cliente"]: row["count"] for row in tono_rows}

        return EstadisticasAprendizaje(
            total_aprendizajes=stats_row["total_aprendizajes"],
            aprendizajes_validados=stats_row["aprendizajes_validados"],
            aprendizajes_efectivos=stats_row["aprendizajes_efectivos"],
            promedio_efectividad=float(stats_row["promedio_efectividad"] or 0.0),
            categorias=categorias,
            tonos_mas_comunes=tonos_mas_comunes,
        )

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}", exc_info=True)
        raise


async def registrar_uso_aprendizaje(aprendizaje_id: int, fue_util: bool = True) -> None:
    """
    Registra el uso de un aprendizaje y actualiza su efectividad.

    Args:
        aprendizaje_id: ID del aprendizaje
        fue_util: Si el aprendizaje fue útil
    """
    pool = get_pool()

    try:
        # Usar la función de BD para actualizar uso
        await pool.execute("SELECT actualizar_uso_aprendizaje($1)", aprendizaje_id)

        # Calcular efectividad
        await pool.execute(
            "SELECT calcular_efectividad_aprendizaje($1, $2)", aprendizaje_id, fue_util
        )

        logger.info(
            f"Uso registrado para aprendizaje {aprendizaje_id}, útil: {fue_util}"
        )

    except Exception as e:
        logger.error(f"Error registrando uso de aprendizaje: {e}", exc_info=True)
        raise

