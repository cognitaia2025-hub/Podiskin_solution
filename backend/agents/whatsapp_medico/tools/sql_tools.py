"""
SQL Tools - Grupo A (12 Herramientas de Automatización)
========================================================

Herramientas que consultan base de datos directamente SIN interpretación semántica.
Estas son la FUENTE DE VERDAD para datos estructurados.

CRÍTICO: NUNCA inventar datos. Solo retornar lo que existe en BD.
"""

from langchain.tools import tool
from typing import Annotated, Optional
import logging
import json
from datetime import datetime, timedelta
import pytz  # 🔥 FIX CRÍTICO

from db import get_pool

logger = logging.getLogger(__name__)

# Definir zona horaria de la clínica
CLINICA_TZ = pytz.timezone("America/Tijuana")  # Mexicali usa esta misma zona


# ============================================================================
# A1: consultar_disponibilidad_horarios
# ============================================================================


@tool
async def consultar_disponibilidad_horarios(
    fecha: Annotated[str, "Fecha en formato YYYY-MM-DD"],
    id_podologo: Annotated[int, "ID del podólogo (opcional)"] = None,
) -> str:
    """
    Consulta horarios disponibles en una fecha específica.

    CRÍTICO: Esta es la FUENTE DE VERDAD para disponibilidad.
    NO inventar horarios. Solo retornar lo que la BD dice.

    NUEVO: Usa bloques_horario (granular) en lugar de horarios_trabajo.

    Args:
        fecha: Fecha en formato YYYY-MM-DD
        id_podologo: ID opcional del podólogo específico

    Returns:
        JSON con lista de horarios disponibles
    """
    pool = await get_pool()

    logger.info("=" * 80)
    logger.info("🔧 [TOOL A1] consultar_disponibilidad_horarios (BLOQUES GRANULARES)")
    logger.info("=" * 80)
    logger.info(f"📅 Fecha solicitada: {fecha}")
    logger.info(f"👤 Podólogo ID: {id_podologo if id_podologo else 'Cualquiera'}")

    try:
        # Convertir fecha string a date object
        from datetime import datetime as dt

        fecha_obj = dt.strptime(fecha, "%Y-%m-%d").date()

        # Query para generar slots de tiempo desde bloques_horario
        query = """
            WITH time_slots AS (
                -- Generar slots de tiempo desde bloques_horario
                SELECT
                    b.id_podologo,
                    u.nombre_completo as podologo_nombre,
                    b.duracion_slot_minutos,
                    generate_series(
                        lower(b.periodo),
                        upper(b.periodo) - (b.duracion_slot_minutos || ' minutes')::interval,
                        (b.duracion_slot_minutos || ' minutes')::interval
                    ) as slot_inicio
                FROM bloques_horario b
                INNER JOIN podologos p ON b.id_podologo = p.id
                INNER JOIN usuarios u ON p.id_usuario = u.id
                WHERE b.fecha = $1
                  AND b.tipo = 'trabajo'  -- Solo bloques de trabajo
                  AND p.activo = true
                  AND ($2::int IS NULL OR b.id_podologo = $2::int)
            )
            SELECT
                ts.slot_inicio::time as hora_inicio,
                (ts.slot_inicio + (ts.duracion_slot_minutos || ' minutes')::interval)::time as hora_fin,
                ts.duracion_slot_minutos,
                ts.id_podologo,
                ts.podologo_nombre
            FROM time_slots ts
            LEFT JOIN citas c ON (
                c.id_podologo = ts.id_podologo
                AND c.fecha_hora_inicio = ts.slot_inicio
                AND c.estado NOT IN ('Cancelada', 'No_Asistio')
            )
            WHERE c.id IS NULL  -- Solo slots sin citas
            ORDER BY ts.slot_inicio ASC
        """

        rows = await pool.fetch(query, fecha_obj, id_podologo)

        logger.info(f"📊 [QUERY EJECUTADO] Resultado:")
        logger.info(f"   - Fuente: bloques_horario (granular)")
        logger.info(
            f"   - Parámetros: fecha_str={fecha}, fecha_obj={fecha_obj}, id_podologo={id_podologo}"
        )
        logger.info(f"   - Filas retornadas: {len(rows)}")

        # DEBUG: Ver qué hay en bloques_horario
        debug_bloques = await pool.fetch(
            "SELECT COUNT(*) as total FROM bloques_horario WHERE fecha = $1", fecha_obj
        )
        logger.warning(
            f"🔍 DEBUG: Bloques en BD para fecha {fecha_obj}: {debug_bloques[0]['total']}"
        )

        if not rows:
            logger.warning("=" * 80)
            logger.warning("⚠️ [SIN RESULTADOS] No hay horarios disponibles")
            logger.warning("=" * 80)
            return json.dumps(
                {
                    "disponibles": [],
                    "mensaje": "No hay horarios disponibles para esta fecha",
                    "fecha": fecha,
                },
                ensure_ascii=False,
            )

        # Formatear resultados
        disponibles = []
        logger.info("📋 [HORARIOS DISPONIBLES]:")

        # ⚠️ FILTRO TEMPORAL CORREGIDO
        ahora_local = datetime.now(CLINICA_TZ)
        fecha_hoy = ahora_local.date()
        hora_actual = ahora_local.time()

        # Margen de seguridad (15 min)
        hora_limite_dt = ahora_local + timedelta(minutes=15)
        hora_limite = hora_limite_dt.time()

        es_hoy = str(fecha_hoy) == fecha

        logger.warning(f"⏰ [ZONA HORARIA] Mexicali: {ahora_local}")
        logger.warning(
            f"📅 ¿Es hoy?: {es_hoy} | Fecha Hoy: {fecha_hoy} | Solicitada: {fecha}"
        )
        logger.warning("=" * 80)

        if es_hoy:
            logger.warning("🔥 FILTRO TEMPORAL ACTIVADO - Filtrando horarios pasados")
        else:
            logger.warning(f"ℹ️ No es hoy, mostrando todos los horarios")

        for i, row in enumerate(rows, 1):
            hora_inicio_str = str(row["hora_inicio"])

            # Si es HOY, verificar que el horario no haya pasado (con margen de 15 min)
            if es_hoy:
                # Convertir hora_inicio a time object para comparar
                hora_parts = hora_inicio_str.split(":")
                hora_inicio_time = datetime.strptime(hora_inicio_str, "%H:%M:%S").time()

                # Filtrar horarios que ya pasaron O están a menos de 15 min
                if hora_inicio_time < hora_limite:
                    logger.warning(
                        f"   ⏭️ FILTRADO: {hora_inicio_str} < {hora_limite} (ya pasó o muy cercano)"
                    )
                    continue  # Saltar este horario
                else:
                    logger.warning(
                        f"   ✅ INCLUIDO: {hora_inicio_str} >= {hora_limite} (disponible)"
                    )

            horario = {
                "hora_inicio": hora_inicio_str,
                "hora_fin": str(row["hora_fin"]),
                "duracion_minutos": row["duracion_slot_minutos"],
                "podologo_id": row["id_podologo"],
                "podologo_nombre": row["podologo_nombre"],
            }
            disponibles.append(horario)
            logger.info(
                f"   {len(disponibles)}. {horario['hora_inicio']}-{horario['hora_fin']} con {horario['podologo_nombre']}"
            )

        # Si después del filtro no quedan horarios
        if not disponibles and es_hoy:
            return json.dumps(
                {
                    "disponibles": [],
                    "mensaje": f"Ya no hay citas disponibles para hoy {fecha}. La última cita fue antes de las {hora_actual}. Sugiere citas para el día de mañana.",
                    "es_hoy": True,
                    "clinica_cerrada": True,
                },
                ensure_ascii=False,
            )

        # Si después del filtro no quedan horarios (y no es HOY, o es caso raro)
        if not disponibles:
            logger.warning("=" * 80)
            logger.warning("⚠️ [SIN HORARIOS DISPONIBLES] Filtro no dejó nada")
            logger.warning("=" * 80)
            return json.dumps(
                {
                    "disponibles": [],
                    "mensaje": "No hay horarios disponibles para esta fecha",
                    "fecha": fecha,
                    "es_hoy": es_hoy,
                    "hora_actual": str(hora_actual) if es_hoy else None,
                    "hora_limite": str(hora_limite) if es_hoy else None,
                    "margen_minutos": 15 if es_hoy else 0,
                },
                ensure_ascii=False,
            )

        resultado = {
            "disponibles": disponibles,
            "fecha": fecha,
            "total": len(disponibles),
            "es_hoy": es_hoy,
            "hora_actual": str(hora_actual) if es_hoy else None,
            "hora_limite": str(hora_limite) if es_hoy else None,
            "margen_minutos": 15 if es_hoy else 0,
        }

        logger.info("=" * 80)
        logger.info(
            f"✅ [RESULTADO] {len(disponibles)} horarios disponibles (después de filtro temporal)"
        )
        logger.info("=" * 80)
        logger.info(
            f"JSON retornado:\n{json.dumps(resultado, ensure_ascii=False, indent=2)}"
        )

        return json.dumps(resultado, ensure_ascii=False)

    except Exception as e:
        logger.error("=" * 80)
        logger.error("❌ [ERROR TOOL A1]")
        logger.error("=" * 80)
        logger.error(f"Error: {str(e)}")
        import traceback

        logger.error(f"Traceback:\n{traceback.format_exc()}")
        return json.dumps(
            {
                "error": True,
                "mensaje": "Error al consultar disponibilidad. Notificar al administrador.",
            },
            ensure_ascii=False,
        )


# ============================================================================
# A2: verificar_cita_programada
# ============================================================================


@tool
async def verificar_cita_programada(
    telefono: Annotated[str, "Teléfono del paciente"],
) -> str:
    """
    Verifica si el paciente tiene cita programada HOY.

    Uso: Cuando el paciente dice "voy tarde" o "estoy cerca",
    primero VERIFICAR si realmente tiene cita.

    Args:
        telefono: Teléfono del paciente

    Returns:
        JSON con datos de la cita o null si no tiene
    """
    pool = await get_pool()

    logger.info(f"[A2] Verificando cita hoy para teléfono: {telefono}")

    try:
        query = """
            SELECT
                c.id,
                c.fecha_hora_inicio,
                c.fecha_hora_fin,
                c.tipo_cita,
                c.estado,
                p.id as paciente_id,
                p.primer_nombre,
                p.segundo_nombre,
                p.primer_apellido,
                p.segundo_apellido,
                u.nombre_completo as podologo_nombre,
                c.notas_recepcion
            FROM citas c
            INNER JOIN pacientes p ON c.id_paciente = p.id
            INNER JOIN usuarios u ON c.id_podologo = u.id
            WHERE p.telefono_principal = $1
              AND DATE(c.fecha_hora_inicio) = CURRENT_DATE
              AND c.estado NOT IN ('Cancelada', 'No_Asistio')
            ORDER BY c.fecha_hora_inicio ASC
            LIMIT 1
        """

        row = await pool.fetchrow(query, telefono)

        if not row:
            logger.info(f"[A2] No tiene cita hoy: {telefono}")
            return json.dumps(
                {
                    "tiene_cita": False,
                    "cita": None,
                    "mensaje": "No tiene cita programada para hoy",
                },
                ensure_ascii=False,
            )

        # Formatear cita
        nombre_completo_paciente = f"{row['primer_nombre']} {row['segundo_nombre'] or ''} {row['primer_apellido']} {row['segundo_apellido'] or ''}".strip()

        cita = {
            "id": row["id"],
            "fecha": row["fecha_hora_inicio"].strftime("%d/%m/%Y"),
            "hora_inicio": row["fecha_hora_inicio"].strftime("%H:%M"),
            "hora_fin": row["fecha_hora_fin"].strftime("%H:%M"),
            "tipo": row["tipo_cita"],
            "estado": row["estado"],
            "paciente_id": row["paciente_id"],
            "paciente_nombre": nombre_completo_paciente,
            "podologo": row["podologo_nombre"],
            "notas": row["notas_recepcion"],
        }

        logger.info(f"[A2] Cita encontrada: ID={row['id']}, Hora={cita['hora_inicio']}")

        return json.dumps({"tiene_cita": True, "cita": cita}, ensure_ascii=False)

    except Exception as e:
        logger.error(f"[A2] Error: {e}", exc_info=True)
        return json.dumps(
            {
                "error": True,
                "mensaje": "Error al verificar cita. Notificar al administrador.",
            },
            ensure_ascii=False,
        )


# ============================================================================
# A3: consultar_precio_servicio
# ============================================================================


@tool
async def consultar_precio_servicio(
    termino_busqueda: Annotated[str, "Término del servicio a buscar"],
) -> str:
    """
    Consulta precio EXACTO desde catalogo_servicios.

    CRÍTICO: NUNCA inventar precios. Solo retornar lo que está en BD.
    Si no se encuentra, retornar mensaje claro.

    Args:
        termino_busqueda: Nombre o descripción del servicio

    Returns:
        JSON con datos del servicio encontrado
    """
    pool = await get_pool()

    search_term = termino_busqueda.strip().lower()

    logger.info("=" * 80)
    logger.info("🔧 [TOOL A3] consultar_precio_servicio")
    logger.info("=" * 80)
    logger.info(f"🔍 Término de búsqueda: '{search_term}'")

    try:
        query = """
            SELECT
                id,
                nombre_servicio as nombre,
                precio_base as precio,
                descripcion,
                duracion_minutos,
                requiere_consentimiento,
                codigo_servicio
            FROM tratamientos
            WHERE activo = true
              AND (
                  LOWER(nombre_servicio) ILIKE $1
                  OR LOWER(descripcion) ILIKE $1
                  OR LOWER(codigo_servicio) ILIKE $1
              )
            ORDER BY
                CASE
                    WHEN LOWER(nombre_servicio) = $2 THEN 1
                    WHEN LOWER(nombre_servicio) ILIKE $1 THEN 2
                    ELSE 3
                END
            LIMIT 1
        """

        rows = await pool.fetch(query, f"%{search_term}%", search_term)
        row = rows[0] if rows else None

        # --- INTENTO 2: Búsqueda por palabras clave (Fallback) ---
        if not row:
            logger.info("⚠️ [INTENTO 1 FALLIDO] Probando búsqueda por palabras clave...")
            keywords = [
                k for k in search_term.split() if len(k) > 3
            ]  # Ignorar palabras cortas (de, la, con)

            if keywords:
                # Construir query dinámico OR ...
                conditions = []
                params = []
                for i, key in enumerate(keywords, start=1):
                    conditions.append(
                        f"(LOWER(nombre_servicio) ILIKE ${i} OR LOWER(descripcion) ILIKE ${i})"
                    )
                    params.append(f"%{key}%")

                if conditions:
                    fallback_query = f"""
                        SELECT
                            id, nombre_servicio as nombre, precio_base as precio, descripcion,
                            duracion_minutos, requiere_consentimiento, codigo_servicio
                        FROM tratamientos
                        WHERE activo = true AND ({" OR ".join(conditions)})
                        LIMIT 1
                    """
                    rows_fallback = await pool.fetch(fallback_query, *params)
                    if rows_fallback:
                        row = rows_fallback[0]
                        logger.info(
                            f"✅ [INTENTO 2 ÉXITO] Match por keywords: {[r['nombre'] for r in rows_fallback]}"
                        )

        logger.info(f"📊 [QUERY EJECUTADO]")
        logger.info(f"   - Filas retornadas: {1 if row else 0}")

        if not row:
            logger.warning("=" * 80)
            logger.warning("⚠️ [SIN RESULTADOS] Servicio NO encontrado")
            logger.warning("=" * 80)
            logger.warning(f"❌ Término buscado: '{termino_busqueda}'")
            logger.warning("🔺 ESCALAMIENTO FORZADO - Debe consultar admin")
            return json.dumps(
                {
                    "encontrado": False,
                    "debe_escalar": True,
                    "mensaje": "No se encontró información sobre este servicio en la base de datos. ESCALAMIENTO REQUERIDO.",
                    "razon_escalamiento": "Consulta de servicio no registrado en sistema",
                },
                ensure_ascii=False,
            )

        # Formatear servicio
        servicio = {
            "id": row["id"],
            "nombre": row["nombre"],
            "precio": float(row["precio"]) if row["precio"] else None,
            "descripcion": row["descripcion"] or "",
            "duracion_minutos": row["duracion_minutos"],
            "requiere_consentimiento": row["requiere_consentimiento"],
            "codigo": row["codigo_servicio"] or "",
        }

        logger.info("=" * 80)
        logger.info("✅ [SERVICIO ENCONTRADO]")
        logger.info("=" * 80)
        logger.info(f"📦 Nombre: {servicio['nombre']}")
        logger.info(f"💰 Precio: ${servicio['precio']}")
        logger.info(f"⏱️ Duración: {servicio['duracion_minutos']} min")
        logger.info(f"📝 Descripción: {servicio['descripcion'][:100]}...")

        resultado = {"encontrado": True, "servicio": servicio}
        logger.info(
            f"JSON retornado:\n{json.dumps(resultado, ensure_ascii=False, indent=2)}"
        )

        return json.dumps(resultado, ensure_ascii=False)

    except Exception as e:
        logger.error("=" * 80)
        logger.error("❌ [ERROR TOOL A3]")
        logger.error("=" * 80)
        logger.error(f"Error: {str(e)}")
        import traceback

        logger.error(f"Traceback:\n{traceback.format_exc()}")
        return json.dumps(
            {
                "error": True,
                "debe_escalar": True,
                "mensaje": "Error al consultar servicio. ESCALAMIENTO REQUERIDO.",
                "razon_escalamiento": "Error técnico en consulta de base de datos",
            },
            ensure_ascii=False,
        )


# ============================================================================
# A4: buscar_paciente_por_telefono
# ============================================================================


@tool
async def buscar_paciente_por_telefono(
    telefono: Annotated[str, "Teléfono del paciente"],
) -> str:
    """
    Busca si el paciente ya existe en la base de datos.

    Uso: Para determinar si es paciente nuevo o recurrente.

    Args:
        telefono: Teléfono del paciente

    Returns:
        JSON con datos del paciente o indicador de nuevo
    """
    pool = await get_pool()

    logger.info(f"[A4] Buscando paciente por teléfono: {telefono}")

    try:
        query = """
            SELECT
                p.id,
                p.primer_nombre,
                p.segundo_nombre,
                p.primer_apellido,
                p.segundo_apellido,
                p.email,
                p.fecha_registro,
                p.fecha_nacimiento,
                (SELECT COUNT(*) FROM citas WHERE id_paciente = p.id) as total_citas,
                (
                    SELECT COUNT(*)
                    FROM citas
                    WHERE id_paciente = p.id
                    AND estado = 'Completada'
                ) as citas_completadas
            FROM pacientes p
            WHERE p.telefono_principal = $1
            LIMIT 1
        """

        row = await pool.fetchrow(query, telefono)

        if not row:
            logger.info(f"[A4] Paciente nuevo (no existe): {telefono}")
            return json.dumps(
                {"existe": False, "paciente": None, "es_nuevo": True},
                ensure_ascii=False,
            )

        # Formatear nombre completo
        nombre_completo = f"{row['primer_nombre']} {row['segundo_nombre'] or ''} {row['primer_apellido']} {row['segundo_apellido'] or ''}".strip()

        # Formatear paciente
        paciente = {
            "id": row["id"],
            "nombre_completo": nombre_completo,
            "email": row["email"],
            "fecha_registro": (
                row["fecha_registro"].strftime("%d/%m/%Y")
                if row["fecha_registro"]
                else None
            ),
            "edad": None,
            "total_citas": row["total_citas"],
            "citas_completadas": row["citas_completadas"],
        }

        # Calcular edad si tiene fecha de nacimiento
        if row["fecha_nacimiento"]:
            today = datetime.now().date()
            edad = today.year - row["fecha_nacimiento"].year
            if today.month < row["fecha_nacimiento"].month or (
                today.month == row["fecha_nacimiento"].month
                and today.day < row["fecha_nacimiento"].day
            ):
                edad -= 1
            paciente["edad"] = edad

        logger.info(
            f"[A4] Paciente encontrado: {paciente['id']} - {paciente['nombre_completo']}"
        )

        return json.dumps(
            {"existe": True, "paciente": paciente, "es_nuevo": False},
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"[A4] Error: {e}", exc_info=True)
        return json.dumps(
            {
                "error": True,
                "mensaje": "Error al buscar paciente. Notificar al administrador.",
            },
            ensure_ascii=False,
        )


# ============================================================================
# A5: obtener_datos_facturacion
# ============================================================================


@tool
async def obtener_datos_facturacion(
    id_paciente: Annotated[str, "ID del paciente"],
) -> str:
    """
    Obtiene datos fiscales del paciente para facturación.

    Args:
        id_paciente: ID del paciente

    Returns:
        JSON con datos fiscales o null si no tiene
    """
    pool = await get_pool()

    logger.info(f"[A5] Obteniendo datos de facturación para: {id_paciente}")

    try:
        # NOTA: La funcionalidad de facturación está pendiente de implementación
        # en el schema de la BD. Por ahora, retornar mensaje indicando esto.

        # Verificar que el paciente existe
        exists = await pool.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pacientes WHERE id = $1)", int(id_paciente)
        )

        if not exists:
            logger.warning(f"[A5] Paciente no existe: {id_paciente}")
            return json.dumps(
                {
                    "tiene_datos": False,
                    "datos_fiscales": None,
                    "mensaje": "Paciente no encontrado",
                },
                ensure_ascii=False,
            )

        logger.info(f"[A5] Funcionalidad de facturación pendiente para: {id_paciente}")

        return json.dumps(
            {
                "tiene_datos": False,
                "datos_fiscales": None,
                "mensaje": "La funcionalidad de facturación está pendiente de implementación. Por favor contacta al administrador para registrar datos fiscales.",
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"[A5] Error: {e}", exc_info=True)
        return json.dumps(
            {"error": True, "mensaje": "Error al obtener datos fiscales."},
            ensure_ascii=False,
        )


# ============================================================================
# A6: consultar_metodos_pago
# ============================================================================


@tool
async def consultar_metodos_pago() -> str:
    """
    Obtiene métodos de pago aceptados en la clínica.

    Returns:
        JSON con métodos de pago disponibles
    """
    pool = await get_pool()

    logger.info("[A6] Consultando métodos de pago")

    try:
        # En la BD Podoskin, esta info podría estar en una tabla de configuración
        # Por ahora, retornar info fija basada en el conocimiento del negocio

        metodos = {
            "efectivo": {
                "disponible": True,
                "descripcion": "Pago en efectivo en el consultorio",
            },
            "tarjeta": {
                "disponible": True,
                "descripcion": "Tarjeta de crédito o débito (Visa, MasterCard)",
            },
            "transferencia": {
                "disponible": True,
                "descripcion": "Transferencia bancaria",
                "banco": "BBVA",
                "clabe": "012180015123456789",
                "titular": "Clínica Podológica Podoskin",
            },
        }

        logger.info("[A6] Métodos de pago retornados exitosamente")

        return json.dumps({"metodos_pago": metodos}, ensure_ascii=False)

    except Exception as e:
        logger.error(f"[A6] Error: {e}", exc_info=True)
        return json.dumps(
            {"error": True, "mensaje": "Error al consultar métodos de pago."},
            ensure_ascii=False,
        )


# ============================================================================
# A7: obtener_ubicacion_consultorio
# ============================================================================


@tool
async def obtener_ubicacion_consultorio() -> str:
    """
    Obtiene dirección física del consultorio.

    Returns:
        JSON con dirección y link de Google Maps
    """
    pool = await get_pool()

    logger.info("[A7] Consultando ubicación del consultorio")

    try:
        # Información fija del consultorio (basada en conocimiento del negocio)
        ubicacion = {
            "direccion_completa": "Consultar en recepción",
            "referencias": "Consultar en recepción",
            "maps_link": "Consultar en recepción",
            "telefono_consultorio": "Consultar en recepción",
            "horarios": {
                "lunes_viernes": "09:00 - 19:00",
                "sabado": "09:00 - 14:00",
                "domingo": "Cerrado",
            },
        }

        logger.info("[A7] Ubicación retornada exitosamente")

        return json.dumps({"ubicacion": ubicacion}, ensure_ascii=False)

    except Exception as e:
        logger.error(f"[A7] Error: {e}", exc_info=True)
        return json.dumps(
            {"error": True, "mensaje": "Error al consultar ubicación."},
            ensure_ascii=False,
        )


# ============================================================================
# A8: verificar_disponibilidad_podologo
# ============================================================================


@tool
async def verificar_disponibilidad_podologo(
    id_podologo: Annotated[int, "ID del podólogo"],
    fecha: Annotated[str, "Fecha en formato YYYY-MM-DD"],
    hora: Annotated[str, "Hora en formato HH:MM"],
) -> str:
    """
    Verifica si un podólogo específico está libre en fecha/hora.

    Args:
        id_podologo: ID del podólogo
        fecha: Fecha YYYY-MM-DD
        hora: Hora HH:MM

    Returns:
        JSON con disponibilidad del podólogo
    """
    pool = await get_pool()

    logger.info(
        f"[A8] Verificando disponibilidad: Podologo={id_podologo}, Fecha={fecha}, Hora={hora}"
    )

    try:
        # Construir timestamp completo
        fecha_hora_str = f"{fecha} {hora}:00"
        fecha_hora = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")

        # Verificar si tiene cita en ese horario
        query = """
            SELECT COUNT(*) as ocupado
            FROM citas
            WHERE id_podologo = $1
              AND fecha_hora_inicio = $2::timestamp
              AND estado NOT IN ('Cancelada', 'No_Asistio')
        """

        count = await pool.fetchval(query, id_podologo, fecha_hora)

        disponible = count == 0

        logger.info(f"[A8] Resultado: disponible={disponible}")

        return json.dumps(
            {
                "disponible": disponible,
                "podologo_id": id_podologo,
                "fecha": fecha,
                "hora": hora,
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"[A8] Error: {e}", exc_info=True)
        return json.dumps(
            {
                "error": True,
                "mensaje": "Error al verificar disponibilidad del podólogo.",
            },
            ensure_ascii=False,
        )


# ============================================================================
# A9: consultar_duracion_tratamiento
# ============================================================================


@tool
async def consultar_duracion_tratamiento(
    nombre_servicio: Annotated[str, "Nombre del servicio/tratamiento"],
) -> str:
    """
    Obtiene duración estimada de un tratamiento.

    Args:
        nombre_servicio: Nombre del tratamiento

    Returns:
        JSON con duración en minutos
    """
    pool = await get_pool()

    search_term = nombre_servicio.strip().lower()
    logger.info(f"[A9] Consultando duración de: '{search_term}'")

    try:
        query = """
            SELECT
                nombre_servicio as nombre,
                duracion_minutos,
                1 as sesiones_estimadas
            FROM tratamientos
            WHERE activo = true
              AND LOWER(nombre_servicio) ILIKE $1
            LIMIT 1
        """

        row = await pool.fetchrow(query, f"%{search_term}%")

        if not row:
            logger.warning(f"[A9] No se encontró servicio: '{nombre_servicio}'")
            return json.dumps(
                {"encontrado": False, "mensaje": "No se encontró el servicio"},
                ensure_ascii=False,
            )

        duracion = {
            "nombre": row["nombre"],
            "duracion_minutos": row["duracion_minutos"],
            "sesiones_estimadas": row["sesiones_estimadas"] or 1,
        }

        logger.info(f"[A9] Duración encontrada: {duracion['duracion_minutos']} min")

        return json.dumps(
            {"encontrado": True, "duracion": duracion}, ensure_ascii=False
        )

    except Exception as e:
        logger.error(f"[A9] Error: {e}", exc_info=True)
        return json.dumps(
            {"error": True, "mensaje": "Error al consultar duración."},
            ensure_ascii=False,
        )


# ============================================================================
# A10: verificar_confirmacion_cita
# ============================================================================


@tool
async def verificar_confirmacion_cita(id_cita: Annotated[int, "ID de la cita"]) -> str:
    """
    Verifica si una cita está confirmada.

    Args:
        id_cita: ID de la cita

    Returns:
        JSON con estado de confirmación
    """
    pool = await get_pool()

    logger.info(f"[A10] Verificando confirmación de cita: {id_cita}")

    try:
        query = """
            SELECT
                id,
                estado,
                fecha_hora_inicio
            FROM citas
            WHERE id = $1
        """

        row = await pool.fetchrow(query, id_cita)

        if not row:
            logger.warning(f"[A10] Cita no encontrada: {id_cita}")
            return json.dumps(
                {"encontrada": False, "mensaje": "Cita no encontrada"},
                ensure_ascii=False,
            )

        confirmada = row["estado"] == "Confirmada"

        cita_info = {
            "id": row["id"],
            "estado": row["estado"],
            "fecha_hora": row["fecha_hora_inicio"].strftime("%d/%m/%Y %H:%M"),
            "confirmada": confirmada,
            "requiere_confirmacion": row["estado"] == "Pendiente",
        }

        logger.info(f"[A10] Cita {id_cita}: confirmada={confirmada}")

        return json.dumps({"encontrada": True, "cita": cita_info}, ensure_ascii=False)

    except Exception as e:
        logger.error(f"[A10] Error: {e}", exc_info=True)
        return json.dumps(
            {"error": True, "mensaje": "Error al verificar confirmación."},
            ensure_ascii=False,
        )


# ============================================================================
# A11: consultar_resultados_laboratorio
# ============================================================================


@tool
async def consultar_resultados_laboratorio(
    id_paciente: Annotated[str, "ID del paciente"],
) -> str:
    """
    Obtiene resultados de estudios/cultivos del paciente.

    Args:
        id_paciente: ID del paciente

    Returns:
        JSON con resultados de laboratorio
    """
    pool = await get_pool()

    logger.info(f"[A11] Consultando resultados de laboratorio: {id_paciente}")

    try:
        # Nota: Esta tabla puede no existir en el schema actual
        # Implementar cuando esté disponible

        # Por ahora, retornar que no hay resultados
        logger.info(f"[A11] Funcionalidad pendiente de implementación")

        return json.dumps(
            {
                "tiene_resultados": False,
                "mensaje": "No hay resultados de laboratorio disponibles",
                "nota": "Esta funcionalidad está pendiente de implementación",
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"[A11] Error: {e}", exc_info=True)
        return json.dumps(
            {"error": True, "mensaje": "Error al consultar resultados."},
            ensure_ascii=False,
        )


# ============================================================================
# A12: consultar_cobros_pendientes
# ============================================================================


@tool
async def consultar_cobros_pendientes(
    id_paciente: Annotated[str, "ID del paciente"],
) -> str:
    """
    Obtiene pagos pendientes del paciente.

    Args:
        id_paciente: ID del paciente

    Returns:
        JSON con lista de pagos pendientes
    """
    pool = await get_pool()

    logger.info(f"[A12] Consultando cobros pendientes: {id_paciente}")

    try:
        query = """
            SELECT 
                p.id,
                p.saldo_pendiente,
                c.motivo_consulta,
                c.fecha_hora_inicio
            FROM pagos p
            JOIN citas c ON p.id_cita = c.id
            WHERE c.id_paciente = $1
              AND p.saldo_pendiente > 0
            ORDER BY c.fecha_hora_inicio ASC
        """

        rows = await pool.fetch(query, int(id_paciente))

        if not rows:
            logger.info(f"[A12] Sin cobros pendientes: {id_paciente}")
            return json.dumps(
                {"tiene_pendientes": False, "cobros": [], "total": 0},
                ensure_ascii=False,
            )

        cobros = []
        total = 0

        for row in rows:
            cobro = {
                "id": row["id"],
                "monto": float(row["saldo_pendiente"]),
                "concepto": row["motivo_consulta"] or "Servicio Podológico",
                "fecha_servicio": row["fecha_hora_inicio"].strftime("%d/%m/%Y"),
            }
            cobros.append(cobro)
            total += cobro["monto"]

        logger.info(f"[A12] {len(cobros)} cobros pendientes, total: ${total}")

        return json.dumps(
            {"tiene_pendientes": True, "cobros": cobros, "total": total},
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"[A12] Error: {e}", exc_info=True)
        return json.dumps(
            {"error": True, "mensaje": "Error al consultar cobros pendientes."},
            ensure_ascii=False,
        )


# ============================================================================
# A13: crear_cita_medica
# ============================================================================


@tool
async def crear_cita_medica(
    id_paciente: Annotated[int, "ID del paciente en la base de datos"],
    fecha: Annotated[str, "Fecha en formato YYYY-MM-DD"],
    hora: Annotated[str, "Hora en formato HH:MM (24 horas)"],
    id_servicio: Annotated[int, "ID del servicio desde catalogo_servicios"],
    motivo: Annotated[str, "Motivo de la consulta"] = "Consulta general",
    id_podologo: Annotated[
        Optional[int], "ID del podólogo (None = asignación automática)"
    ] = None,
) -> str:
    """
    Crea una nueva cita médica en el sistema.

    LÓGICA DE ASIGNACIÓN DE PODÓLOGO:
    - Si id_podologo es proporcionado: usar ese
    - Si id_podologo es None:
        * 1 podólogo disponible → asignar automáticamente
        * 2+ podólogos disponibles → crear ticket para admin
        * 0 podólogos disponibles → retornar error

    Returns:
        JSON con:
        - status: "success" | "pendiente_admin" | "no_disponible"
        - cita_id: ID de la cita creada (si success)
        - message: Mensaje descriptivo
        - notification_id: ID de notificación (si pendiente_admin)
    """
    pool = await get_pool()

    logger.info(
        f"[A13] Creando cita: paciente={id_paciente}, fecha={fecha}, hora={hora}, servicio={id_servicio}, podologo={id_podologo}"
    )

    try:
        # 1. Validar que el paciente existe y está activo
        paciente_existe = await pool.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pacientes WHERE id = $1 AND activo = true)",
            id_paciente,
        )

        if not paciente_existe:
            return json.dumps(
                {
                    "status": "error",
                    "message": "El paciente no existe o no está activo",
                },
                ensure_ascii=False,
            )

        # 2. Validar que el servicio existe y está activo, obtener duración
        servicio = await pool.fetchrow(
            "SELECT duracion_minutos FROM tratamientos WHERE id = $1 AND activo = true",
            id_servicio,
        )

        if not servicio:
            return json.dumps(
                {
                    "status": "error",
                    "message": "El servicio no existe o no está activo",
                },
                ensure_ascii=False,
            )

        duracion_minutos = servicio["duracion_minutos"] or 30

        # 3. Parsear fecha y hora, calcular fecha_hora_fin
        try:
            fecha_hora_inicio = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
            fecha_hora_fin = fecha_hora_inicio + timedelta(minutes=duracion_minutos)
        except ValueError as e:
            return json.dumps(
                {"status": "error", "message": f"Formato de fecha/hora inválido: {e}"},
                ensure_ascii=False,
            )

        # 4. Si id_podologo es None, determinar cuál asignar
        requires_admin_confirmation = False
        if id_podologo is None:
            # Obtener día de la semana (0=Domingo, 6=Sábado)
            dia_semana = await pool.fetchval(
                "SELECT EXTRACT(DOW FROM TO_DATE($1, 'YYYY-MM-DD'))::int", fecha
            )

            # Buscar podólogos que trabajan ese día/hora
            query_disponibles = """
                SELECT DISTINCT h.id_podologo, u.nombre_completo
                FROM horarios_trabajo h
                INNER JOIN usuarios u ON h.id_podologo = u.id
                WHERE h.activo = true
                  AND h.dia_semana = $1
                  AND u.activo = true
                  AND $2::time >= h.hora_inicio
                  AND $2::time < h.hora_fin
                  AND (h.fecha_fin_vigencia IS NULL OR h.fecha_fin_vigencia >= $3::date)
                  AND NOT EXISTS (
                      SELECT 1 FROM citas c
                      WHERE c.id_podologo = h.id_podologo
                        AND c.estado NOT IN ('Cancelada', 'No_Asistio')
                        AND c.fecha_hora_inicio < $5::timestamp
                        AND c.fecha_hora_fin > $4::timestamp
                  )
            """

            podologos_disponibles = await pool.fetch(
                query_disponibles,
                dia_semana,
                hora,
                fecha,
                fecha_hora_inicio,
                fecha_hora_fin,
            )

            num_disponibles = len(podologos_disponibles)

            # 0 disponibles → error
            if num_disponibles == 0:
                return json.dumps(
                    {
                        "status": "no_disponible",
                        "message": f"No hay podólogos disponibles para {fecha} a las {hora}",
                    },
                    ensure_ascii=False,
                )

            # 1 disponible → asignar automáticamente
            elif num_disponibles == 1:
                id_podologo = podologos_disponibles[0]["id_podologo"]
                logger.info(f"[A13] Asignación automática: podólogo {id_podologo}")

            # 2+ disponibles → Dejar id_podologo en None (Asignación genérica)
            else:
                id_podologo = None
                requires_admin_confirmation = False

                logger.info(
                    f"[A13] {num_disponibles} podólogos disponibles. Asignación genérica (id_podologo=NULL)."
                )

        # 5. Si se seleccionó un podólogo, validar que existe
        if id_podologo is not None:
            podologo_existe = await pool.fetchval(
                "SELECT EXISTS(SELECT 1 FROM usuarios WHERE id = $1 AND activo = true)",
                id_podologo,
            )

            if not podologo_existe:
                return json.dumps(
                    {
                        "status": "error",
                        "message": "El podólogo no existe o no está activo",
                    },
                    ensure_ascii=False,
                )

            # 6. Verificar que no haya conflicto de horario (solo si hay podólogo asignado)
            conflicto = await pool.fetchrow(
                """
                SELECT id FROM citas
                WHERE id_podologo = $1
                  AND estado NOT IN ('Cancelada', 'No_Asistio')
                  AND fecha_hora_inicio < $2
                  AND fecha_hora_fin > $3
                LIMIT 1
                """,
                id_podologo,
                fecha_hora_fin,
                fecha_hora_inicio,
            )

            if conflicto:
                return json.dumps(
                    {
                        "status": "error",
                        "message": "Conflicto de horario: el podólogo ya tiene una cita en ese horario",
                    },
                    ensure_ascii=False,
                )

        # 7. Crear la cita en la base de datos
        # Nota: id_podologo puede ser NULL
        cita_id = await pool.fetchval(
            """
            INSERT INTO citas (
                id_paciente, id_podologo, fecha_hora_inicio, fecha_hora_fin,
                id_servicio, estado, motivo_consulta, creado_por
            )
            VALUES ($1, $2, $3, $4, $5, 'Programada', $6, NULL)
            RETURNING id
            """,
            id_paciente,
            id_podologo,
            fecha_hora_inicio,
            fecha_hora_fin,
            id_servicio,
            motivo,
        )

        logger.info(f"[A13] ✅ Cita creada exitosamente: ID={cita_id}")

        # 8. Notificar admin (Cita confirmada estándar)
        from agents.whatsapp_medico.utils_helpers import notificar_admin_cita_creada

        # Si hay podólogo asignado, se notifica con nombre. Si no, pasamos None/0
        await notificar_admin_cita_creada(cita_id, id_podologo or 0, id_paciente)

        mensaje_retorno = f"Cita confirmada exitosamente para el {fecha} a las {hora}."
        status_retorno = "success"

        return json.dumps(
            {
                "status": status_retorno,
                "cita_id": cita_id,
                "message": mensaje_retorno,
                "id_podologo": id_podologo,
                "fecha_hora_inicio": fecha_hora_inicio.strftime("%Y-%m-%d %H:%M"),
                "fecha_hora_fin": fecha_hora_fin.strftime("%Y-%m-%d %H:%M"),
                "requires_admin_confirmation": False,
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"[A13] Error: {e}", exc_info=True)
        return json.dumps(
            {"status": "error", "message": f"Error al crear la cita: {str(e)}"},
            ensure_ascii=False,
        )


# ============================================================================
# A14 - CREAR PACIENTE NUEVO
# ============================================================================


@tool
async def crear_paciente_nuevo(
    nombre_completo: Annotated[str, "Nombre completo del paciente"],
    telefono: Annotated[str, "Teléfono principal del paciente (10 dígitos)"],
    email: Annotated[Optional[str], "Email del paciente (opcional)"] = None,
    sexo: Annotated[
        Optional[str], "Sexo biológico: 'M' (Maculino), 'F' (Femenino) u 'O'"
    ] = None,
) -> str:
    """
    Crea un nuevo paciente en el sistema.

    IMPORTANTE: Solo usar cuando el paciente confirme que es su PRIMERA VEZ en la clínica.

    Args:
        nombre_completo: Nombre completo del paciente (ej: "Juan Pérez García")
        telefono: Teléfono principal (10 dígitos, ej: "6861234567")
        email: Email del paciente (opcional)

    Returns:
        JSON con:
        - status: "success" o "error"
        - id_paciente: ID del paciente creado
        - patient_id: UUID del paciente
        - mensaje: Confirmación o error

    Ejemplo de retorno exitoso:
    {
        "status": "success",
        "id_paciente": 123,
        "patient_id": "P-2026-00123",
        "nombre": "Juan Pérez García",
        "mensaje": "Paciente Juan Pérez García registrado exitosamente"
    }
    """
    pool = await get_pool()

    logger.info("=" * 80)
    logger.info("🔧 [TOOL A14] crear_paciente_nuevo")
    logger.info("=" * 80)
    logger.info(f"📝 Nombre: {nombre_completo}")
    logger.info(f"📞 Teléfono: {telefono}")
    logger.info(f"📧 Email: {email or 'No proporcionado'}")

    try:
        # Separar nombre en partes (asumiendo formato: Nombre(s) Apellido(s))
        partes_nombre = nombre_completo.strip().split()

        if len(partes_nombre) < 2:
            logger.warning("⚠️ Nombre incompleto, usando solo primer nombre")
            primer_nombre = (
                partes_nombre[0] if len(partes_nombre) > 0 else nombre_completo
            )
            primer_apellido = ""
        else:
            primer_nombre = partes_nombre[0]
            primer_apellido = partes_nombre[1]

        segundo_nombre = partes_nombre[2] if len(partes_nombre) > 2 else None
        segundo_apellido = partes_nombre[3] if len(partes_nombre) > 3 else None

        # Limpiar teléfono (quitar espacios, guiones, paréntesis)
        telefono_limpio = (
            telefono.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        )

        logger.info(
            f"🔍 Parsed - Nombre: {primer_nombre} {segundo_nombre or ''} {primer_apellido} {segundo_apellido or ''}"
        )
        logger.info(f"🔍 Teléfono limpio: {telefono_limpio}")

        # Verificar que el teléfono no esté ya registrado
        existe = await pool.fetchval(
            "SELECT COUNT(*) FROM pacientes WHERE telefono_principal = $1",
            telefono_limpio,
        )

        if existe > 0:
            logger.warning(f"⚠️ Teléfono {telefono_limpio} ya está registrado")
            return json.dumps(
                {
                    "status": "error",
                    "mensaje": f"El teléfono {telefono} ya está registrado. ¿Ya te has consultado antes? Usa tu teléfono para buscarte.",
                },
                ensure_ascii=False,
            )

        # Normalizar sexo
        sexo_val = "O"
        if sexo:
            s = sexo.lower().strip()
            if s in ["m", "hombre", "masculino", "male"]:
                sexo_val = "M"
            elif s in ["f", "mujer", "femenino", "female"]:
                sexo_val = "F"

        # Insertar paciente
        query = """
            INSERT INTO pacientes (
                primer_nombre, segundo_nombre, primer_apellido, segundo_apellido,
                telefono_principal, email, sexo, fecha_registro, fecha_nacimiento
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), CURRENT_DATE)
            RETURNING id, patient_id
        """

        row = await pool.fetchrow(
            query,
            primer_nombre,
            segundo_nombre,
            primer_apellido,
            segundo_apellido,
            telefono_limpio,
            email,
            sexo_val,
        )

        logger.info("=" * 80)
        logger.info("✅ [PACIENTE CREADO EXITOSAMENTE]")
        logger.info("=" * 80)
        logger.info(f"🆔 ID Interno: {row['id']}")
        logger.info(f"🎫 Patient ID: {row['patient_id']}")
        logger.info(f"👤 Nombre: {nombre_completo}")

        resultado = {
            "status": "success",
            "id_paciente": row["id"],
            "patient_id": row["patient_id"],
            "nombre": nombre_completo,
            "mensaje": f"¡Bienvenido a Podoskin, {primer_nombre}! Tu registro se ha completado exitosamente.",
        }

        return json.dumps(resultado, ensure_ascii=False)

    except Exception as e:
        logger.error("=" * 80)
        logger.error("❌ [ERROR TOOL A14]")
        logger.error("=" * 80)
        logger.error(f"Error: {str(e)}")
        import traceback

        logger.error(f"Traceback:\n{traceback.format_exc()}")

        return json.dumps(
            {"status": "error", "mensaje": f"Error al registrar paciente: {str(e)}"},
            ensure_ascii=False,
        )


# ============================================================================
# A15 - ESCALAR CASO A ADMIN
# ============================================================================


@tool
async def escalar_caso_a_admin(
    motivo: Annotated[
        str, "Motivo breve del escalamiento (ej: 'Error técnico', 'Usuario molesto')"
    ],
    resumen: Annotated[str, "Descripción detallada de lo que necesita el paciente"],
    telefono_paciente: Annotated[
        Optional[str], "Teléfono del paciente si se tiene"
    ] = None,
) -> str:
    """
    Notifica INMEDIATAMENTE al administrador humano sobre un problema o solicitud especial.

    Uso:
    - Cuando ocurre un error técnico repetido (como 'no se puede consultar disponibilidad').
    - Cuando el usuario pide hablar con un humano.
    - Cuando el usuario tiene una duda médica compleja que el bot no puede resolver.

    Args:
        motivo: Título breve del problema
        resumen: Explicación completa del contexto
        telefono_paciente: Teléfono del paciente (opcional)

    Returns:
        JSON confirmando el envío
    """
    logger.info("=" * 80)
    logger.info("🚨 [TOOL A15] escalar_caso_a_admin")
    logger.info("=" * 80)
    logger.info(f"⚠️ Motivo: {motivo}")

    try:
        from agents.whatsapp_medico.utils_helpers import crear_notificacion_admin

        # Crear notificación real
        notification_id = await crear_notificacion_admin(
            tipo="escalamiento",
            data={
                "motivo": motivo,
                "resumen": resumen,
                "telefono": telefono_paciente,
                "urgente": True,
            },
        )

        logger.info(f"✅ Notificación de escalamiento creada: ID={notification_id}")

        return json.dumps(
            {
                "status": "success",
                "mensaje": "Se ha notificado al administrador. Responderemos lo antes posible.",
                "notification_id": notification_id,
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"Error escalando caso: {e}")
        return json.dumps(
            {"status": "error", "mensaje": "Error interno al intentar notificar."},
            ensure_ascii=False,
        )


# ============================================================================
# LISTA DE TODAS LAS HERRAMIENTAS (para exportar)
# ============================================================================

ALL_SQL_TOOLS = [
    consultar_disponibilidad_horarios,  # A1
    verificar_cita_programada,  # A2
    consultar_precio_servicio,  # A3
    buscar_paciente_por_telefono,  # A4
    obtener_datos_facturacion,  # A5
    consultar_metodos_pago,  # A6
    obtener_ubicacion_consultorio,  # A7
    verificar_disponibilidad_podologo,  # A8
    consultar_duracion_tratamiento,  # A9
    verificar_confirmacion_cita,  # A10
    consultar_resultados_laboratorio,  # A11
    consultar_cobros_pendientes,  # A12
    crear_cita_medica,  # A13
    crear_paciente_nuevo,  # A14
    escalar_caso_a_admin,  # A15
]
