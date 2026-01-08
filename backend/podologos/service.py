"""
Servicio de lógica de negocio para Podólogos
"""

from typing import List, Optional, Dict, Any
from datetime import datetime as dt, date
from dotenv import load_dotenv
from .models import PodologoCreate, PodologoUpdate, PodologoResponse
import logging
from db import fetch_all, fetch_one, execute_returning

# Import asyncpg database for async operations
from pacientes.database import db as pacientes_db

load_dotenv()
logger = logging.getLogger(__name__)


async def get_all_podologos(activo_only: bool = True) -> List[dict]:
    """
    Obtener todos los podólogos
    
    Args:
        activo_only: Si True, solo devuelve podólogos activos
    
    Returns:
        Lista de podólogos
    """
    try:
        query = """
            SELECT 
                id, 
                cedula_profesional, 
                nombre_completo, 
                especialidad, 
                telefono, 
                email, 
                activo, 
                fecha_contratacion, 
                fecha_registro, 
                id_usuario
            FROM podologos
        """
        
        if activo_only:
            query += " WHERE activo = true"
        
        query += " ORDER BY nombre_completo ASC"
        
        result = await fetch_all(query)
        logger.info(f"Retrieved {len(result)} podólogos (activo_only={activo_only})")
        return result
    
    except Exception as e:
        logger.error(f"Error fetching podólogos: {e}")
        raise


async def get_podologo_by_id(podologo_id: int) -> Optional[dict]:
    """
    Obtener un podólogo por ID
    
    Args:
        podologo_id: ID del podólogo
    
    Returns:
        Datos del podólogo o None si no existe
    """
    try:
        query = """
            SELECT 
                id, 
                cedula_profesional, 
                nombre_completo, 
                especialidad, 
                telefono, 
                email, 
                activo, 
                fecha_contratacion, 
                fecha_registro, 
                id_usuario
            FROM podologos
            WHERE id = $1
        """
        result = await fetch_one(query, podologo_id)
            else:
                logger.warning(f"Podologo with ID {podologo_id} not found")
                return None
    
    except Exception as e:
        logger.error(f"Error fetching podologo {podologo_id}: {e}")
        raise
    finally:
        conn.close()


async def create_podologo(podologo_data: PodologoCreate) -> dict:
    """
    Crear un nuevo podólogo
    
    Args:
        podologo_data: Datos del podólogo a crear
    
    Returns:
        Datos del podólogo creado
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                INSERT INTO podologos (
                    cedula_profesional, 
                    nombre_completo, 
                    especialidad, 
                    telefono, 
                    email, 
                    activo, 
                    fecha_contratacion, 
                    id_usuario
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING 
                    id, 
                    cedula_profesional, 
                    nombre_completo, 
                    especialidad, 
                    telefono, 
                    email, 
                    activo, 
                    fecha_contratacion, 
                    fecha_registro, 
                    id_usuario
                """,
                (
                    podologo_data.cedula_profesional,
                    podologo_data.nombre_completo,
                    podologo_data.especialidad,
                    podologo_data.telefono,
                    podologo_data.email,
                    podologo_data.activo,
                    podologo_data.fecha_contratacion,
                    podologo_data.id_usuario,
                )
            )
            result = cursor.fetchone()
            conn.commit()
            
            logger.info(f"Created new podologo: {result['nombre_completo']}")
            return dict(result)
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating podologo: {e}")
        raise
    finally:
        conn.close()


async def update_podologo(podologo_id: int, podologo_data: PodologoUpdate) -> Optional[dict]:
    """
    Actualizar un podólogo existente
    
    Args:
        podologo_id: ID del podólogo a actualizar
        podologo_data: Datos a actualizar
    
    Returns:
        Datos del podólogo actualizado o None si no existe
    """
    conn = get_db_connection()
    try:
        # Construir query dinámicamente solo con campos proporcionados
        update_fields = []
        params = []
        
        if podologo_data.cedula_profesional is not None:
            update_fields.append("cedula_profesional = %s")
            params.append(podologo_data.cedula_profesional)
        
        if podologo_data.nombre_completo is not None:
            update_fields.append("nombre_completo = %s")
            params.append(podologo_data.nombre_completo)
        
        if podologo_data.especialidad is not None:
            update_fields.append("especialidad = %s")
            params.append(podologo_data.especialidad)
        
        if podologo_data.telefono is not None:
            update_fields.append("telefono = %s")
            params.append(podologo_data.telefono)
        
        if podologo_data.email is not None:
            update_fields.append("email = %s")
            params.append(podologo_data.email)
        
        if podologo_data.activo is not None:
            update_fields.append("activo = %s")
            params.append(podologo_data.activo)
        
        if podologo_data.fecha_contratacion is not None:
            update_fields.append("fecha_contratacion = %s")
            params.append(podologo_data.fecha_contratacion)
        
        if podologo_data.id_usuario is not None:
            update_fields.append("id_usuario = %s")
            params.append(podologo_data.id_usuario)
        
        if not update_fields:
            logger.warning(f"No fields to update for podologo {podologo_id}")
            return await get_podologo_by_id(podologo_id)
        
        params.append(podologo_id)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = f"""
                UPDATE podologos 
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING 
                    id, 
                    cedula_profesional, 
                    nombre_completo, 
                    especialidad, 
                    telefono, 
                    email, 
                    activo, 
                    fecha_contratacion, 
                    fecha_registro, 
                    id_usuario
            """
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                logger.info(f"Updated podologo {podologo_id}")
                return dict(result)
            else:
                logger.warning(f"Podologo {podologo_id} not found for update")
                return None
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating podologo {podologo_id}: {e}")
        raise
    finally:
        conn.close()


async def delete_podologo(podologo_id: int) -> bool:
    """
    Eliminar un podólogo (soft delete - marca como inactivo)
    
    Args:
        podologo_id: ID del podólogo a eliminar
    
    Returns:
        True si se eliminó, False si no existe
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE podologos 
                SET activo = false 
                WHERE id = %s
                """,
                (podologo_id,)
            )
            affected_rows = cursor.rowcount
            conn.commit()
            
            if affected_rows > 0:
                logger.info(f"Soft deleted podologo {podologo_id}")
                return True
            else:
                logger.warning(f"Podologo {podologo_id} not found for deletion")
                return False
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting podologo {podologo_id}: {e}")
        raise
    finally:
        conn.close()


async def get_podologos_disponibles(fecha: Optional[str] = None) -> List[dict]:
    """
    Obtener podólogos disponibles (activos) con verificación de calendario
    
    Args:
        fecha: Fecha opcional para verificar disponibilidad (formato YYYY-MM-DD)
    
    Returns:
        Lista de podólogos disponibles con información de slots
    """
    # Si no se proporciona fecha, usar hoy
    if not fecha:
        fecha_obj = date.today()
    else:
        try:
            fecha_obj = dt.strptime(fecha, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid date format: {fecha}, using today")
            fecha_obj = date.today()
    
    # Obtener día de la semana (0=Domingo, 6=Sábado)
    dia_semana = (fecha_obj.weekday() + 1) % 7  # Python usa 0=Lunes, convertir a 0=Domingo
    
    try:
        async with pacientes_db.get_connection() as conn:
            # Query para obtener podólogos con disponibilidad
            query = """
            WITH podologo_slots AS (
                SELECT 
                    p.id,
                    p.cedula_profesional,
                    p.nombre_completo,
                    p.especialidad,
                    p.telefono,
                    p.email,
                    p.activo,
                    COUNT(DISTINCT h.id) as tiene_horario,
                    COALESCE(
                        SUM(
                            EXTRACT(EPOCH FROM (h.hora_fin - h.hora_inicio)) / 
                            (h.duracion_cita_minutos * 60)
                        ), 0
                    ) as slots_totales,
                    COUNT(DISTINCT c.id) as citas_agendadas
                FROM podologos p
                LEFT JOIN horarios_trabajo h ON p.id = h.id_podologo 
                    AND h.dia_semana = $1
                    AND h.activo = true
                    AND (h.fecha_fin_vigencia IS NULL OR h.fecha_fin_vigencia >= $2)
                LEFT JOIN citas c ON p.id = c.id_podologo
                    AND DATE(c.fecha_hora_inicio) = $2
                    AND c.estado NOT IN ('cancelada', 'no_asistio')
                WHERE p.activo = true
                GROUP BY p.id, p.nombre_completo, p.especialidad, p.telefono, p.email, p.activo
            )
            SELECT 
                id,
                cedula_profesional,
                nombre_completo,
                especialidad,
                telefono,
                email,
                activo,
                tiene_horario > 0 as tiene_horario_dia,
                slots_totales::integer as slots_disponibles_totales,
                citas_agendadas,
                (slots_totales - citas_agendadas)::integer as slots_libres
            FROM podologo_slots
            WHERE tiene_horario > 0  -- Solo podólogos con horario para ese día
            ORDER BY slots_libres DESC, nombre_completo
            """
            
            rows = await conn.fetch(query, dia_semana, fecha_obj)
        
        result = []
        for row in rows:
            result.append({
                'id': row['id'],
                'cedula_profesional': row['cedula_profesional'],
                'nombre_completo': row['nombre_completo'],
                'especialidad': row['especialidad'],
                'telefono': row['telefono'],
                'email': row['email'],
                'activo': row['activo'],
                'tiene_horario_dia': row['tiene_horario_dia'],
                'slots_disponibles_totales': row['slots_disponibles_totales'],
                'citas_agendadas': row['citas_agendadas'],
                'slots_libres': row['slots_libres'],
                'fecha_consultada': fecha_obj.isoformat()
            })
        
        logger.info(f"Found {len(result)} available podologos for {fecha_obj}")
        return result
    
    except Exception as e:
        logger.error(f"Error getting available podologos: {e}")
        # Fallback to simple active query
        return await get_all_podologos(activo_only=True)


async def get_available_podologos(
    conn: asyncpg.Connection,
    fecha: date,
    hora_inicio: str,
    hora_fin: str
) -> List[Dict[str, Any]]:
    """
    Obtiene podólogos disponibles en un horario específico.
    
    Verifica que el podólogo:
    1. Esté activo
    2. No tenga citas conflictivas en ese horario
    
    Args:
        conn: Conexión a BD
        fecha: Fecha de la consulta
        hora_inicio: Hora de inicio (HH:MM)
        hora_fin: Hora de fin (HH:MM)
        
    Returns:
        Lista de podólogos disponibles con su información
    """
    query = """
        SELECT 
            u.id,
            u.nombre_usuario,
            u.nombre_completo,
            u.email,
            COUNT(c.id) as citas_activas
        FROM usuarios u
        LEFT JOIN citas c ON c.podologo_id = u.id
            AND c.fecha = $1
            AND c.estado NOT IN ('cancelada', 'completada')
            AND (
                (c.hora_inicio < $3 AND c.hora_fin > $2)
                OR (c.hora_inicio >= $2 AND c.hora_inicio < $3)
                OR (c.hora_fin > $2 AND c.hora_fin <= $3)
            )
        WHERE u.rol = 'Podologo'
            AND u.activo = true
        GROUP BY u.id, u.nombre_usuario, u.nombre_completo, u.email
        HAVING COUNT(c.id) = 0
        ORDER BY u.nombre_completo
    """
    
    rows = await conn.fetch(query, fecha, hora_inicio, hora_fin)
    
    return [
        {
            "id": row['id'],
            "nombre_usuario": row['nombre_usuario'],
            "nombre_completo": row['nombre_completo'],
            "email": row['email'],
            "disponible": True
        }
        for row in rows
    ]


async def create_podologo_from_user(
    id_usuario: int,
    cedula_profesional: str,
    nombre_completo: str,
    email: str,
    telefono: str = "",
    especialidad: str = "Podología General"
) -> dict:
    """
    Crear registro de podólogo al crear un usuario con rol Podologo
    
    Args:
        id_usuario: ID del usuario creado
        cedula_profesional: Cédula profesional del podólogo
        nombre_completo: Nombre completo
        email: Email
        telefono: Teléfono (opcional)
        especialidad: Especialidad (default: Podología General)
    
    Returns:
        Datos del podólogo creado
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                INSERT INTO podologos (
                    cedula_profesional,
                    nombre_completo,
                    especialidad,
                    telefono,
                    email,
                    activo,
                    fecha_contratacion,
                    id_usuario
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, cedula_profesional, nombre_completo, especialidad, 
                          telefono, email, activo, fecha_contratacion, id_usuario
                """,
                (
                    cedula_profesional,
                    nombre_completo,
                    especialidad,
                    telefono,
                    email,
                    True,  # activo
                    date.today(),  # fecha_contratacion
                    id_usuario
                )
            )
            result = cursor.fetchone()
            conn.commit()
            
            logger.info(f"Created podologo record for user {id_usuario}")
            return dict(result)
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating podologo: {e}")
        raise
    finally:
        conn.close()
