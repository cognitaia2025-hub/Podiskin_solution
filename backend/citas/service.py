"""
Capa de servicio para gestión de citas
=======================================

Contiene la lógica de negocio y acceso a datos para el módulo de citas.
Implementa validaciones, cálculos automáticos y operaciones CRUD.
"""

import logging
from datetime import datetime, timedelta, date
from typing import List, Optional, Dict, Any, Tuple
import asyncio

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool

logger = logging.getLogger(__name__)

# Pool global de conexiones (reutilizando patrón del backend existente)
_pool: Optional[pool.ThreadedConnectionPool] = None


# ============================================================================
# GESTIÓN DE CONEXIONES
# ============================================================================


def init_db_pool(database_url: str):
    """Inicializa el pool de conexiones a la base de datos."""
    global _pool

    if _pool is not None:
        return

    try:
        _pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=database_url
        )
        logger.info("✅ Database pool initialized for citas module")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database pool: {e}")
        raise


def close_db_pool():
    """Cierra el pool de conexiones."""
    global _pool

    if _pool is None:
        return

    try:
        _pool.closeall()
        _pool = None
        logger.info("Database pool closed")
    except Exception as e:
        logger.error(f"Error closing database pool: {e}")


def _get_connection():
    """Obtiene una conexión del pool."""
    global _pool

    if _pool is None:
        raise Exception("Database pool not initialized. Call init_db_pool() first.")

    return _pool.getconn()


def _put_connection(conn):
    """Devuelve una conexión al pool."""
    global _pool
    if _pool is not None:
        _pool.putconn(conn)


async def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """
    Ejecuta una query SELECT y retorna los resultados como lista de diccionarios.
    
    Args:
        query: Query SQL a ejecutar
        params: Parámetros para la query
        
    Returns:
        Lista de diccionarios con los resultados
    """
    loop = asyncio.get_event_loop()
    
    def _execute():
        conn = _get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                result = cur.fetchall()
                return [dict(row) for row in result]
        finally:
            _put_connection(conn)
    
    return await loop.run_in_executor(None, _execute)


async def execute_query_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """
    Ejecuta una query SELECT y retorna un solo resultado.
    
    Args:
        query: Query SQL a ejecutar
        params: Parámetros para la query
        
    Returns:
        Diccionario con el resultado o None si no hay resultados
    """
    loop = asyncio.get_event_loop()
    
    def _execute():
        conn = _get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                result = cur.fetchone()
                return dict(result) if result else None
        finally:
            _put_connection(conn)
    
    return await loop.run_in_executor(None, _execute)


async def execute_mutation(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """
    Ejecuta una query INSERT/UPDATE/DELETE y retorna el resultado (si tiene RETURNING).
    
    Args:
        query: Query SQL a ejecutar
        params: Parámetros para la query
        
    Returns:
        Diccionario con el resultado si usa RETURNING, None en caso contrario
    """
    loop = asyncio.get_event_loop()
    
    def _execute():
        conn = _get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                conn.commit()
                # Si la query tiene RETURNING, obtener el resultado
                if cur.description:
                    result = cur.fetchone()
                    return dict(result) if result else None
                return None
        except Exception as e:
            conn.rollback()
            raise
        finally:
            _put_connection(conn)
    
    return await loop.run_in_executor(None, _execute)


# ============================================================================
# VALIDACIONES
# ============================================================================


async def validar_paciente_activo(id_paciente: int) -> bool:
    """
    Valida que el paciente exista y esté activo.
    
    Args:
        id_paciente: ID del paciente
        
    Returns:
        True si el paciente existe y está activo
    """
    query = """
        SELECT id FROM pacientes 
        WHERE id = %s AND activo = true
    """
    result = await execute_query_one(query, (id_paciente,))
    return result is not None


async def validar_podologo_activo(id_podologo: int) -> bool:
    """
    Valida que el podólogo exista y esté activo.
    
    Args:
        id_podologo: ID del podólogo
        
    Returns:
        True si el podólogo existe y está activo
    """
    query = """
        SELECT id FROM podologos 
        WHERE id = %s AND activo = true
    """
    result = await execute_query_one(query, (id_podologo,))
    return result is not None


async def verificar_conflicto_horario(
    id_podologo: int,
    fecha_hora_inicio: datetime,
    fecha_hora_fin: datetime,
    excluir_cita_id: Optional[int] = None
) -> bool:
    """
    Verifica si existe un conflicto de horario para el podólogo.
    
    Un conflicto existe si hay una cita que:
    - Es del mismo podólogo
    - NO está cancelada ni marcada como "No asistió"
    - Se solapa con el horario solicitado
    
    Args:
        id_podologo: ID del podólogo
        fecha_hora_inicio: Hora de inicio
        fecha_hora_fin: Hora de fin
        excluir_cita_id: ID de cita a excluir (para actualizaciones)
        
    Returns:
        True si hay conflicto, False si está disponible
    """
    query = """
        SELECT id FROM citas
        WHERE id_podologo = %s
        AND estado NOT IN ('Cancelada', 'No_Asistio')
        AND (
            (fecha_hora_inicio < %s AND fecha_hora_fin > %s)
            OR (fecha_hora_inicio < %s AND fecha_hora_fin > %s)
            OR (fecha_hora_inicio >= %s AND fecha_hora_fin <= %s)
        )
    """
    params = [
        id_podologo,
        fecha_hora_fin, fecha_hora_inicio,  # Conflicto: la cita existente termina después de que inicia la nueva
        fecha_hora_fin, fecha_hora_inicio,  # Conflicto: la cita existente inicia antes de que termine la nueva
        fecha_hora_inicio, fecha_hora_fin    # Conflicto: la cita existente está completamente contenida
    ]
    
    if excluir_cita_id:
        query += " AND id != %s"
        params.append(excluir_cita_id)
    
    result = await execute_query(query, tuple(params))
    return len(result) > 0


async def verificar_cita_paciente_mismo_dia(
    id_paciente: int,
    fecha: date,
    excluir_cita_id: Optional[int] = None
) -> bool:
    """
    Verifica si el paciente ya tiene una cita el mismo día.
    
    Args:
        id_paciente: ID del paciente
        fecha: Fecha a verificar
        excluir_cita_id: ID de cita a excluir (para actualizaciones)
        
    Returns:
        True si ya tiene cita ese día, False si no
    """
    query = """
        SELECT id FROM citas
        WHERE id_paciente = %s
        AND DATE(fecha_hora_inicio) = %s
        AND estado NOT IN ('Cancelada', 'No_Asistio')
    """
    params = [id_paciente, fecha]
    
    if excluir_cita_id:
        query += " AND id != %s"
        params.append(excluir_cita_id)
    
    result = await execute_query(query, tuple(params))
    return len(result) > 0


async def es_primera_vez_paciente(id_paciente: int) -> bool:
    """
    Determina si es la primera vez que el paciente tiene una cita completada.
    
    Args:
        id_paciente: ID del paciente
        
    Returns:
        True si es primera vez (no tiene citas completadas), False si no
    """
    query = """
        SELECT COUNT(*) as count FROM citas
        WHERE id_paciente = %s AND estado = 'Completada'
    """
    result = await execute_query_one(query, (id_paciente,))
    return result["count"] == 0 if result else True


# ============================================================================
# OPERACIONES CRUD
# ============================================================================


async def obtener_citas(
    id_paciente: Optional[int] = None,
    id_podologo: Optional[int] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    estado: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Obtiene una lista de citas con filtros opcionales.
    
    Args:
        id_paciente: Filtrar por ID de paciente
        id_podologo: Filtrar por ID de podólogo
        fecha_inicio: Filtrar desde esta fecha
        fecha_fin: Filtrar hasta esta fecha
        estado: Filtrar por estado
        limit: Número máximo de resultados
        offset: Desplazamiento para paginación
        
    Returns:
        Tupla con (lista de citas, total de registros)
    """
    # Construir WHERE clause dinámicamente
    where_clauses = []
    params = []
    
    if id_paciente:
        where_clauses.append("c.id_paciente = %s")
        params.append(id_paciente)
    
    if id_podologo:
        where_clauses.append("c.id_podologo = %s")
        params.append(id_podologo)
    
    if fecha_inicio:
        where_clauses.append("DATE(c.fecha_hora_inicio) >= %s")
        params.append(fecha_inicio)
    
    if fecha_fin:
        where_clauses.append("DATE(c.fecha_hora_inicio) <= %s")
        params.append(fecha_fin)
    
    if estado:
        where_clauses.append("c.estado = %s")
        params.append(estado)
    
    where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    # Query para contar total
    count_query = f"""
        SELECT COUNT(*) as total
        FROM citas c
        {where_clause}
    """
    
    # Query para obtener datos
    query = f"""
        SELECT 
            c.*,
            p.nombre_completo as paciente_nombre,
            pod.nombre_completo as podologo_nombre
        FROM citas c
        LEFT JOIN pacientes p ON c.id_paciente = p.id
        LEFT JOIN podologos pod ON c.id_podologo = pod.id
        {where_clause}
        ORDER BY c.fecha_hora_inicio DESC
        LIMIT %s OFFSET %s
    """
    
    # Agregar limit y offset a params
    params_with_pagination = params + [limit, offset]
    
    # Ejecutar queries
    count_result = await execute_query_one(count_query, tuple(params))
    citas = await execute_query(query, tuple(params_with_pagination))
    
    total = count_result["total"] if count_result else 0
    
    return citas, total


async def obtener_cita_por_id(id_cita: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene una cita por su ID.
    
    Args:
        id_cita: ID de la cita
        
    Returns:
        Diccionario con los datos de la cita o None si no existe
    """
    query = """
        SELECT 
            c.*,
            p.nombre_completo as paciente_nombre,
            pod.nombre_completo as podologo_nombre
        FROM citas c
        LEFT JOIN pacientes p ON c.id_paciente = p.id
        LEFT JOIN podologos pod ON c.id_podologo = pod.id
        WHERE c.id = %s
    """
    return await execute_query_one(query, (id_cita,))


async def crear_cita(
    id_paciente: int,
    id_podologo: int,
    fecha_hora_inicio: datetime,
    tipo_cita: str,
    motivo_consulta: Optional[str] = None,
    notas_recepcion: Optional[str] = None,
    creado_por: Optional[int] = None
) -> Dict[str, Any]:
    """
    Crea una nueva cita.
    
    Args:
        id_paciente: ID del paciente
        id_podologo: ID del podólogo
        fecha_hora_inicio: Fecha y hora de inicio
        tipo_cita: Tipo de cita (Consulta, Seguimiento, Urgencia)
        motivo_consulta: Motivo de la consulta (opcional)
        notas_recepcion: Notas de recepción (opcional)
        creado_por: ID del usuario que crea la cita (opcional)
        
    Returns:
        Diccionario con los datos de la cita creada
        
    Raises:
        ValueError: Si hay errores de validación
    """
    # Validar que paciente y podólogo existan y estén activos
    if not await validar_paciente_activo(id_paciente):
        raise ValueError("El paciente no existe o no está activo")
    
    if not await validar_podologo_activo(id_podologo):
        raise ValueError("El podólogo no existe o no está activo")
    
    # Validar que la fecha sea al menos 1 hora en el futuro
    ahora = datetime.now()
    if fecha_hora_inicio < ahora + timedelta(hours=1):
        raise ValueError("La cita debe agendarse con al menos 1 hora de anticipación")
    
    # Calcular fecha_hora_fin (30 minutos después)
    fecha_hora_fin = fecha_hora_inicio + timedelta(minutes=30)
    
    # Verificar conflicto de horario
    if await verificar_conflicto_horario(id_podologo, fecha_hora_inicio, fecha_hora_fin):
        raise ValueError("Conflicto de horario: el podólogo ya tiene una cita en ese horario")
    
    # Verificar que el paciente no tenga otra cita el mismo día
    if await verificar_cita_paciente_mismo_dia(id_paciente, fecha_hora_inicio.date()):
        raise ValueError("El paciente ya tiene una cita agendada para ese día")
    
    # Determinar si es primera vez
    es_primera_vez = await es_primera_vez_paciente(id_paciente)
    
    # Insertar la cita
    query = """
        INSERT INTO citas (
            id_paciente, id_podologo, fecha_hora_inicio, fecha_hora_fin,
            tipo_cita, estado, motivo_consulta, notas_recepcion,
            es_primera_vez, creado_por
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    
    params = (
        id_paciente, id_podologo, fecha_hora_inicio, fecha_hora_fin,
        tipo_cita, "Confirmada", motivo_consulta, notas_recepcion,
        es_primera_vez, creado_por
    )
    
    cita = await execute_mutation(query, params)
    
    if not cita:
        raise Exception("Error al crear la cita")
    
    # Obtener la cita con información completa
    return await obtener_cita_por_id(cita["id"])


async def actualizar_cita(
    id_cita: int,
    fecha_hora_inicio: Optional[datetime] = None,
    tipo_cita: Optional[str] = None,
    motivo_consulta: Optional[str] = None,
    notas_recepcion: Optional[str] = None,
    estado: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Actualiza una cita existente.
    
    Args:
        id_cita: ID de la cita a actualizar
        fecha_hora_inicio: Nueva fecha/hora de inicio (opcional)
        tipo_cita: Nuevo tipo de cita (opcional)
        motivo_consulta: Nuevo motivo (opcional)
        notas_recepcion: Nuevas notas (opcional)
        estado: Nuevo estado (opcional)
        
    Returns:
        Diccionario con los datos actualizados o None si no existe
        
    Raises:
        ValueError: Si hay errores de validación
    """
    # Verificar que la cita exista
    cita_actual = await obtener_cita_por_id(id_cita)
    if not cita_actual:
        return None
    
    # No permitir actualizar citas completadas o canceladas
    if cita_actual["estado"] in ["Completada", "Cancelada"]:
        raise ValueError(f"No se puede actualizar una cita en estado {cita_actual['estado']}")
    
    # Construir la actualización dinámicamente
    updates = []
    params = []
    param_count = 1
    
    if fecha_hora_inicio is not None:
        # Validar fecha futura
        ahora = datetime.now()
        if fecha_hora_inicio < ahora + timedelta(hours=1):
            raise ValueError("La cita debe agendarse con al menos 1 hora de anticipación")
        
        fecha_hora_fin = fecha_hora_inicio + timedelta(minutes=30)
        
        # Verificar conflicto (excluyendo la cita actual)
        if await verificar_conflicto_horario(
            cita_actual["id_podologo"],
            fecha_hora_inicio,
            fecha_hora_fin,
            excluir_cita_id=id_cita
        ):
            raise ValueError("Conflicto de horario: el podólogo ya tiene una cita en ese horario")
        
        updates.append(f"fecha_hora_inicio = %s")
        params.append(fecha_hora_inicio)
        param_count += 1
        
        updates.append(f"fecha_hora_fin = %s")
        params.append(fecha_hora_fin)
        param_count += 1
    
    if tipo_cita is not None:
        updates.append(f"tipo_cita = %s")
        params.append(tipo_cita)
        param_count += 1
    
    if motivo_consulta is not None:
        updates.append(f"motivo_consulta = %s")
        params.append(motivo_consulta)
        param_count += 1
    
    if notas_recepcion is not None:
        updates.append(f"notas_recepcion = %s")
        params.append(notas_recepcion)
        param_count += 1
    
    if estado is not None:
        updates.append(f"estado = %s")
        params.append(estado)
        param_count += 1
    
    if not updates:
        # No hay nada que actualizar
        return cita_actual
    
    # Agregar fecha_actualizacion
    updates.append("fecha_actualizacion = CURRENT_TIMESTAMP")
    
    # Construir y ejecutar query
    query = f"""
        UPDATE citas
        SET {', '.join(updates)}
        WHERE id = %s
        RETURNING *
    """
    
    params.append(id_cita)
    
    await execute_mutation(query, tuple(params))
    
    # Retornar la cita actualizada con información completa
    return await obtener_cita_por_id(id_cita)


async def cancelar_cita(id_cita: int, motivo_cancelacion: str) -> Optional[Dict[str, Any]]:
    """
    Cancela una cita (soft delete).
    
    Args:
        id_cita: ID de la cita a cancelar
        motivo_cancelacion: Motivo de la cancelación
        
    Returns:
        Diccionario con los datos de la cita cancelada o None si no existe
        
    Raises:
        ValueError: Si la cita no puede ser cancelada
    """
    # Verificar que la cita exista
    cita = await obtener_cita_por_id(id_cita)
    if not cita:
        return None
    
    # No permitir cancelar citas ya completadas o canceladas
    if cita["estado"] in ["Completada", "Cancelada"]:
        raise ValueError(f"No se puede cancelar una cita en estado {cita['estado']}")
    
    # Actualizar estado a Cancelada
    query = """
        UPDATE citas
        SET estado = 'Cancelada',
            motivo_cancelacion = %s,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING *
    """
    
    await execute_mutation(query, (motivo_cancelacion, id_cita))
    
    # Retornar la cita cancelada
    return await obtener_cita_por_id(id_cita)


# ============================================================================
# DISPONIBILIDAD
# ============================================================================


async def obtener_disponibilidad(
    id_podologo: int,
    fecha: date
) -> Dict[str, Any]:
    """
    Obtiene los slots de disponibilidad para un podólogo en una fecha específica.
    
    Genera slots cada 30 minutos desde las 9:00 hasta las 18:00 (horario por defecto).
    Para cada slot, verifica si hay una cita existente.
    
    Args:
        id_podologo: ID del podólogo
        fecha: Fecha a consultar
        
    Returns:
        Diccionario con fecha, info del podólogo y lista de slots
        
    Raises:
        ValueError: Si el podólogo no existe o la fecha es pasada
    """
    # Validar que el podólogo exista y esté activo
    if not await validar_podologo_activo(id_podologo):
        raise ValueError("El podólogo no existe o no está activo")
    
    # Validar que la fecha no sea pasada
    hoy = date.today()
    if fecha < hoy:
        raise ValueError("No se puede consultar disponibilidad de fechas pasadas")
    
    # Obtener información del podólogo
    query_podologo = """
        SELECT id, nombre_completo
        FROM podologos
        WHERE id = %s
    """
    podologo = await execute_query_one(query_podologo, (id_podologo,))
    
    # Obtener todas las citas del podólogo para esa fecha
    query_citas = """
        SELECT fecha_hora_inicio, fecha_hora_fin, estado
        FROM citas
        WHERE id_podologo = %s
        AND DATE(fecha_hora_inicio) = %s
        AND estado NOT IN ('Cancelada', 'No_Asistio')
    """
    citas = await execute_query(query_citas, (id_podologo, fecha))
    
    # Generar slots cada 30 minutos de 9:00 a 18:00
    slots = []
    hora_inicio = 9  # 9:00 AM
    hora_fin = 18     # 6:00 PM
    
    for hora in range(hora_inicio, hora_fin):
        for minuto in [0, 30]:
            hora_slot = f"{hora:02d}:{minuto:02d}"
            
            # Crear datetime para este slot
            slot_datetime = datetime.combine(fecha, datetime.strptime(hora_slot, "%H:%M").time())
            slot_fin_datetime = slot_datetime + timedelta(minutes=30)
            
            # Verificar si hay una cita en este slot
            disponible = True
            motivo = None
            
            for cita in citas:
                cita_inicio = cita["fecha_hora_inicio"]
                cita_fin = cita["fecha_hora_fin"]
                
                # Verificar solapamiento
                if (slot_datetime < cita_fin and slot_fin_datetime > cita_inicio):
                    disponible = False
                    motivo = "Cita agendada"
                    break
            
            slots.append({
                "hora": hora_slot,
                "disponible": disponible,
                "motivo": motivo
            })
    
    return {
        "fecha": str(fecha),
        "podologo": {
            "id": podologo["id"],
            "nombre_completo": podologo["nombre_completo"]
        },
        "slots": slots
    }
