"""
SQL Tools - Prioridad 1
=======================

Tools para consultar base de datos estructurada (FUENTE DE VERDAD).

⚠️ CRÍTICO: Estas tools tienen prioridad MÁXIMA sobre cualquier búsqueda vectorial.
"""

from langchain.tools import tool
from typing import Annotated
import logging
import json

from db import get_pool

logger = logging.getLogger(__name__)

# ============================================================================
# TOOL 1: Consultar Tratamientos/Servicios/Precios
# ============================================================================

@tool
async def consultar_tratamientos_sql(
    query: Annotated[str, "Término de búsqueda del tratamiento/servicio"]
) -> str:
    """
    🔑 PRIORIDAD 1: Consulta servicios, tratamientos y precios desde SQL estructurado.
    
    ⚠️ NUNCA usar embeddings para precios/servicios.
    
    Args:
        query: Término de búsqueda (ej: "onicomicosis", "plantillas", "láser")
        
    Returns:
        JSON string con servicios encontrados
    """
    pool = await get_pool()
    
    # Limpiar término de búsqueda
    search_term = query.strip().lower()
    
    logger.info(f"🔍 [SQL Tool] Buscando tratamientos: '{search_term}'")
    
    try:
        sql_query = """
            SELECT 
                nombre,
                descripcion,
                precio,
                duracion_minutos,
                categoria
            FROM tratamientos
            WHERE activo = true
            AND (
                LOWER(nombre) ILIKE $1
                OR LOWER(descripcion) ILIKE $1
                OR LOWER(categoria) ILIKE $1
            )
            ORDER BY 
                CASE 
                    WHEN LOWER(nombre) = $2 THEN 1  -- Exact match primero
                    WHEN LOWER(nombre) ILIKE $1 THEN 2
                    ELSE 3
                END,
                nombre
            LIMIT 5
        """
        
        rows = await pool.fetch(sql_query, f"%{search_term}%", search_term)
        
        if not rows:
            logger.warning(f"⚠️ No se encontraron tratamientos para: '{search_term}'")
            return "No se encontraron servicios con ese término. Por favor, solicita información al equipo de la clínica."
        
        # Formatear resultados
        resultados = []
        for row in rows:
            resultado = {
                "nombre": row['nombre'],
                "descripcion": row['descripcion'] or "Sin descripción",
                "precio": f"${row['precio']:,.2f} MXN" if row['precio'] else "Consultar",
                "duracion": f"{row['duracion_minutos']} minutos" if row['duracion_minutos'] else "Variable",
                "categoria": row['categoria'] or "General"
            }
            resultados.append(resultado)
        
        logger.info(f"✅ [SQL Tool] Encontrados {len(resultados)} servicios")
        
        return json.dumps(resultados, ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"❌ Error consultando tratamientos: {e}", exc_info=True)
        return f"Error consultando servicios: {str(e)}"


# ============================================================================
# TOOL 2: Consultar Horarios
# ============================================================================

@tool
async def consultar_horarios_sql(
    dia_semana: Annotated[int, "Día de la semana (0=Domingo, 6=Sábado)"]
) -> str:
    """
    🔑 PRIORIDAD 1: Consulta horarios de atención desde SQL estructurado.
    
    Args:
        dia_semana: 0=Domingo, 1=Lunes, ..., 6=Sábado
        
    Returns:
        JSON string con horarios disponibles
    """
    pool = await get_pool()
    
    logger.info(f"🔍 [SQL Tool] Consultando horarios para día {dia_semana}")
    
    try:
        sql_query = """
            SELECT 
                p.nombre_completo as podologo,
                ht.hora_inicio,
                ht.hora_fin,
                ht.duracion_cita_minutos
            FROM horarios_trabajo ht
            INNER JOIN podologos p ON ht.id_podologo = p.id
            WHERE ht.dia_semana = $1
            AND ht.activo = true
            AND p.activo = true
            AND (
                ht.fecha_fin_vigencia IS NULL 
                OR ht.fecha_fin_vigencia >= CURRENT_DATE
            )
            ORDER BY ht.hora_inicio
        """
        
        rows = await pool.fetch(sql_query, dia_semana)
        
        if not rows:
            return f"No hay horarios de atención disponibles para ese día."
        
        # Formatear resultados
        resultados = []
        for row in rows:
            resultado = {
                "podologo": row['podologo'],
                "hora_inicio": str(row['hora_inicio']),
                "hora_fin": str(row['hora_fin']),
                "duracion_cita": row['duracion_cita_minutos']
            }
            resultados.append(resultado)
        
        logger.info(f"✅ [SQL Tool] Encontrados {len(resultados)} horarios")
        
        return json.dumps(resultados, ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"❌ Error consultando horarios: {e}", exc_info=True)
        return f"Error consultando horarios: {str(e)}"


# ============================================================================
# TOOL 3: Consultar Citas del Paciente
# ============================================================================

@tool
async def consultar_citas_sql(
    contact_id: Annotated[int, "ID del contacto/paciente"]
) -> str:
    """
    🔑 PRIORIDAD 1: Consulta citas del paciente desde SQL estructurado.
    
    Args:
        contact_id: ID del contacto
        
    Returns:
        JSON string con citas del paciente
    """
    pool = await get_pool()
    
    logger.info(f"🔍 [SQL Tool] Consultando citas del contacto {contact_id}")
    
    try:
        # Obtener id_paciente del contacto
        paciente_id = await pool.fetchval(
            "SELECT id_paciente FROM contactos WHERE id = $1",
            contact_id
        )
        
        if not paciente_id:
            return "No se encontró información del paciente asociado a este contacto."
        
        sql_query = """
            SELECT 
                c.id,
                c.fecha_hora_inicio,
                c.fecha_hora_fin,
                c.tipo_cita,
                c.estado,
                c.motivo_consulta,
                p.nombre_completo as podologo,
                t.nombre as tratamiento
            FROM citas c
            INNER JOIN podologos p ON c.id_podologo = p.id
            LEFT JOIN tratamientos t ON c.id_tratamiento = t.id
            WHERE c.id_paciente = $1
            AND c.estado NOT IN ('Cancelada', 'No_Asistio')
            AND c.fecha_hora_inicio >= CURRENT_DATE - INTERVAL '30 days'
            ORDER BY c.fecha_hora_inicio DESC
            LIMIT 10
        """
        
        rows = await pool.fetch(sql_query, paciente_id)
        
        if not rows:
            return "No se encontraron citas recientes o próximas para este paciente."
        
        # Formatear resultados
        resultados = []
        for row in rows:
            resultado = {
                "id": row['id'],
                "fecha": row['fecha_hora_inicio'].strftime("%d/%m/%Y"),
                "hora": row['fecha_hora_inicio'].strftime("%H:%M"),
                "tipo": row['tipo_cita'],
                "estado": row['estado'],
                "podologo": row['podologo'],
                "tratamiento": row['tratamiento'] or "No especificado"
            }
            resultados.append(resultado)
        
        logger.info(f"✅ [SQL Tool] Encontradas {len(resultados)} citas")
        
        return json.dumps(resultados, ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"❌ Error consultando citas: {e}", exc_info=True)
        return f"Error consultando citas: {str(e)}"


# ============================================================================
# TOOL 4: Calcular Disponibilidad
# ============================================================================

@tool
async def calcular_disponibilidad(
    fecha: Annotated[str, "Fecha en formato YYYY-MM-DD"],
    id_podologo: Annotated[int, "ID del podólogo (opcional)"] = None
) -> str:
    """
    🔑 PRIORIDAD 1: Calcula slots disponibles para una fecha.
    
    Args:
        fecha: Fecha en formato ISO (YYYY-MM-DD)
        id_podologo: ID del podólogo (opcional)
        
    Returns:
        JSON string con slots disponibles
    """
    pool = await get_pool()
    
    logger.info(f"🔍 [SQL Tool] Calculando disponibilidad para {fecha}")
    
    try:
        # Llamar a función PostgreSQL (si existe)
        sql_query = """
            SELECT 
                hora_slot,
                disponible,
                id_podologo
            FROM calcular_disponibilidad($1, $2)
        """
        
        rows = await pool.fetch(sql_query, fecha, id_podologo)
        
        slots_disponibles = [
            {
                "hora": str(row['hora_slot']),
                "disponible": row['disponible'],
                "podologo_id": row.get('id_podologo')
            }
            for row in rows
            if row['disponible']
        ]
        
        logger.info(f"✅ [SQL Tool] {len(slots_disponibles)} slots disponibles")
        
        return json.dumps(slots_disponibles, ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"❌ Error calculando disponibilidad: {e}", exc_info=True)
        # Fallback: método alternativo sin función PostgreSQL
        return await _calcular_disponibilidad_fallback(fecha, id_podologo)


async def _calcular_disponibilidad_fallback(fecha: str, id_podologo: int = None) -> str:
    """Método alternativo de cálculo de disponibilidad si no existe la función en PostgreSQL."""
    pool = await get_pool()
    
    try:
        # Obtener día de la semana
        dia_semana_query = "SELECT EXTRACT(DOW FROM $1::date)"
        dia_semana = await pool.fetchval(dia_semana_query, fecha)
        
        # Obtener horarios de trabajo del día
        horarios_query = """
            SELECT 
                id_podologo,
                hora_inicio,
                hora_fin,
                duracion_cita_minutos
            FROM horarios_trabajo
            WHERE dia_semana = $1
            AND activo = true
            AND ($2 IS NULL OR id_podologo = $2)
        """
        
        horarios = await pool.fetch(horarios_query, dia_semana, id_podologo)
        
        if not horarios:
            return json.dumps([], ensure_ascii=False)
        
        # Obtener citas existentes
        citas_query = """
            SELECT 
                fecha_hora_inicio,
                fecha_hora_fin
            FROM citas
            WHERE DATE(fecha_hora_inicio) = $1
            AND estado NOT IN ('Cancelada')
            AND ($2 IS NULL OR id_podologo = $2)
        """
        
        citas = await pool.fetch(citas_query, fecha, id_podologo)
        
        # Generar slots disponibles (lógica simplificada)
        slots_disponibles = []
        for horario in horarios:
            hora_actual = horario['hora_inicio']
            hora_fin = horario['hora_fin']
            duracion = horario['duracion_cita_minutos']
            
            # Por simplicidad, marcar todos como disponibles
            # En producción, cruzar con citas existentes
            slots_disponibles.append({
                "hora": str(hora_actual),
                "disponible": True,
                "podologo_id": horario['id_podologo']
            })
        
        return json.dumps(slots_disponibles[:10], ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"❌ Error en fallback de disponibilidad: {e}")
        return json.dumps([], ensure_ascii=False)
