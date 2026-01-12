"""
Tareas de notificaciones con Celery
Envío de recordatorios de citas y alertas
"""

from tasks.celery_app import celery_app
from datetime import datetime, timedelta
import asyncio
import asyncpg
import os
from typing import List, Dict, Any

# Configuración de base de datos
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'podoskin_db'),
    'user': os.getenv('POSTGRES_USER', 'podoskin_user'),
    'password': os.getenv('POSTGRES_PASSWORD') or os.getenv('DB_PASSWORD'),  # Requerido
}


async def get_db_connection():
    """Obtiene conexión a la base de datos"""
    return await asyncpg.connect(**DB_CONFIG)


@celery_app.task(name='backend.tasks.notifications.enviar_recordatorios_citas')
def enviar_recordatorios_citas():
    """
    Tarea periódica: Envía recordatorios de citas programadas para las próximas 24 horas
    """
    return asyncio.run(_enviar_recordatorios_citas_async())


async def _enviar_recordatorios_citas_async():
    """Versión async de enviar recordatorios 24h antes"""
    conn = await get_db_connection()
    
    try:
        # Obtener citas de las próximas 24 horas que no tengan recordatorio enviado
        ahora = datetime.now()
        manana = ahora + timedelta(hours=24)
        dos_horas = ahora + timedelta(hours=26)  # Ventana: 24-26 horas adelante
        
        citas = await conn.fetch("""
            SELECT 
                c.cita_id,
                c.fecha_cita,
                c.hora_inicio,
                p.nombre as paciente_nombre,
                p.primer_nombre as paciente_primer_nombre,
                p.telefono as paciente_telefono,
                p.email as paciente_email,
                p.paciente_id,
                pod.nombre as podologo_nombre,
                cs.nombre as servicio_nombre
            FROM citas c
            JOIN pacientes p ON c.paciente_id = p.paciente_id
            JOIN podologos pod ON c.podologo_id = pod.podologo_id
            LEFT JOIN catalogo_servicios cs ON c.tratamiento_id = cs.servicio_id
            WHERE c.fecha_cita BETWEEN $1 AND $2
              AND c.estado = 'confirmada'
              AND NOT EXISTS (
                  SELECT 1 FROM notificaciones n
                  WHERE n.referencia_id = c.cita_id::text
                    AND n.tipo = 'recordatorio_cita_24h'
                    AND n.fecha_envio > NOW() - INTERVAL '26 hours'
              )
        """, manana, dos_horas)
        
        recordatorios_enviados = 0
        
        for cita in citas:
            # Mensaje natural y humano
            primer_nombre = cita['paciente_primer_nombre'] or cita['paciente_nombre'].split()[0]
            dia_semana = cita['fecha_cita'].strftime('%A')
            dias_es = {'Monday': 'lunes', 'Tuesday': 'martes', 'Wednesday': 'miércoles', 
                       'Thursday': 'jueves', 'Friday': 'viernes', 'Saturday': 'sábado', 'Sunday': 'domingo'}
            dia_es = dias_es.get(dia_semana, dia_semana.lower())
            
            mensaje = f"Hola {primer_nombre}, ¿qué tal? 😊\n\n"
            mensaje += f"Solo para recordarte que tenemos tu cita programada para mañana {dia_es} "
            mensaje += f"{cita['fecha_cita'].strftime('%d/%m/%Y')} a las {cita['hora_inicio'].strftime('%I:%M %p')} "
            mensaje += f"con {cita['podologo_nombre']}.\n\n"
            mensaje += f"Si necesitas reagendar o tienes alguna duda, solo avísanos. "
            mensaje += f"¡Nos vemos pronto! 🦶✨"
            
            # Crear notificación en la BD
            await conn.execute("""
                INSERT INTO notificaciones 
                (usuario_id, tipo, titulo, mensaje, referencia_id, referencia_tipo, fecha_envio, leido)
                VALUES (
                    (SELECT usuario_id FROM pacientes WHERE paciente_id = $1),
                    'recordatorio_cita_24h',
                    'Recordatorio: Cita Mañana',
                    $2,
                    $3,
                    'cita',
                    NOW(),
                    FALSE
                )
            """, 
                cita['paciente_id'],
                mensaje,
                str(cita['cita_id'])
            )
            
            recordatorios_enviados += 1
            
            # TODO FUTURO: Integración con WhatsApp + Maya (LangGraph)
            # from backend.agents.sub_agent_whatsApp.notification_handler import enviar_notificacion_whatsapp
            # await enviar_notificacion_whatsapp(
            #     paciente_id=cita['paciente_id'],
            #     telefono=cita['paciente_telefono'],
            #     mensaje=mensaje,
            #     tipo_notificacion='recordatorio_cita_24h',
            #     cita_id=cita['cita_id']
            # )
        
        return {
            'status': 'success',
            'recordatorios_enviados': recordatorios_enviados,
            'fecha_ejecucion': ahora.isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        await conn.close()


@celery_app.task(name='backend.tasks.notifications.enviar_recordatorios_2h')
def enviar_recordatorios_2h():
    """
    Tarea periódica: Envía recordatorios de citas en las próximas 2 horas
    """
    return asyncio.run(_enviar_recordatorios_2h_async())


async def _enviar_recordatorios_2h_async():
    """Versión async de enviar recordatorios 2h antes"""
    conn = await get_db_connection()
    
    try:
        # Obtener citas de las próximas 2 horas que no tengan recordatorio enviado
        ahora = datetime.now()
        dos_horas = ahora + timedelta(hours=2)
        dos_horas_media = ahora + timedelta(hours=2, minutes=30)  # Ventana: 2-2.5h
        
        citas = await conn.fetch("""
            SELECT 
                c.cita_id,
                c.fecha_cita,
                c.hora_inicio,
                p.nombre as paciente_nombre,
                p.primer_nombre as paciente_primer_nombre,
                p.telefono as paciente_telefono,
                p.email as paciente_email,
                p.paciente_id,
                pod.nombre as podologo_nombre,
                cs.nombre as servicio_nombre
            FROM citas c
            JOIN pacientes p ON c.paciente_id = p.paciente_id
            JOIN podologos pod ON c.podologo_id = pod.podologo_id
            LEFT JOIN catalogo_servicios cs ON c.tratamiento_id = cs.servicio_id
            WHERE c.fecha_cita BETWEEN $1 AND $2
              AND c.estado = 'confirmada'
              AND NOT EXISTS (
                  SELECT 1 FROM notificaciones n
                  WHERE n.referencia_id = c.cita_id::text
                    AND n.tipo = 'recordatorio_cita_2h'
                    AND n.fecha_envio > NOW() - INTERVAL '3 hours'
              )
        """, dos_horas, dos_horas_media)
        
        recordatorios_enviados = 0
        
        for cita in citas:
            # Mensaje natural y humano - más breve y directo
            primer_nombre = cita['paciente_primer_nombre'] or cita['paciente_nombre'].split()[0]
            
            # Determinar si es "hoy" o calcular tiempo exacto
            tiempo_hasta_cita = cita['fecha_cita'] - ahora
            horas_restantes = int(tiempo_hasta_cita.total_seconds() / 3600)
            minutos_restantes = int((tiempo_hasta_cita.total_seconds() % 3600) / 60)
            
            if horas_restantes <= 0:
                tiempo_texto = f"en {minutos_restantes} minutos"
            elif horas_restantes == 1:
                tiempo_texto = f"en 1 hora"
            else:
                tiempo_texto = f"en {horas_restantes} horas"
            
            mensaje = f"Hola {primer_nombre}! 👋\n\n"
            mensaje += f"¿Cómo estás? Solo un recordatorio rápido: "
            mensaje += f"tenemos tu cita {tiempo_texto} "
            mensaje += f"({cita['hora_inicio'].strftime('%I:%M %p')}) "
            mensaje += f"con {cita['podologo_nombre']}.\n\n"
            mensaje += f"¡Te esperamos! 😊"
            
            # Crear notificación en la BD
            await conn.execute("""
                INSERT INTO notificaciones 
                (usuario_id, tipo, titulo, mensaje, referencia_id, referencia_tipo, fecha_envio, leido)
                VALUES (
                    (SELECT usuario_id FROM pacientes WHERE paciente_id = $1),
                    'recordatorio_cita_2h',
                    'Tu cita es pronto',
                    $2,
                    $3,
                    'cita',
                    NOW(),
                    FALSE
                )
            """, 
                cita['paciente_id'],
                mensaje,
                str(cita['cita_id'])
            )
            
            recordatorios_enviados += 1
            
            # TODO FUTURO: Integración con WhatsApp + Maya (LangGraph)
            # Este recordatorio es más urgente, ideal para WhatsApp
            # from backend.agents.sub_agent_whatsApp.notification_handler import enviar_notificacion_whatsapp
            # await enviar_notificacion_whatsapp(
            #     paciente_id=cita['paciente_id'],
            #     telefono=cita['paciente_telefono'],
            #     mensaje=mensaje,
            #     tipo_notificacion='recordatorio_cita_2h',
            #     cita_id=cita['cita_id'],
            #     requiere_respuesta=True  # Maya espera confirmación
            # )
        
        return {
            'status': 'success',
            'recordatorios_enviados': recordatorios_enviados,
            'fecha_ejecucion': ahora.isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        await conn.close()


@celery_app.task(name='backend.tasks.notifications.alertar_productos_criticos')
def alertar_productos_criticos():
    """
    Tarea periódica: Revisa inventario y envía alertas de productos críticos
    """
    return asyncio.run(_alertar_productos_criticos_async())


async def _alertar_productos_criticos_async():
    """Versión async de alertar productos críticos"""
    conn = await get_db_connection()
    
    try:
        # Obtener productos críticos (stock <= mínimo * 1.2)
        productos_criticos = await conn.fetch("""
            SELECT 
                producto_id,
                codigo_producto,
                nombre,
                categoria,
                stock_actual,
                stock_minimo,
                unidad_medida
            FROM inventario_productos
            WHERE activo = TRUE
              AND stock_actual <= (stock_minimo * 1.2)
            ORDER BY (stock_actual - stock_minimo) ASC
        """)
        
        if not productos_criticos:
            return {
                'status': 'success',
                'productos_criticos': 0,
                'mensaje': 'No hay productos críticos'
            }
        
        # Crear notificación para el administrador
        mensaje = f"⚠️ {len(productos_criticos)} productos requieren reabastecimiento:\n\n"
        for p in productos_criticos[:10]:  # Top 10
            deficit = p['stock_minimo'] - p['stock_actual']
            mensaje += f"• {p['nombre']}: {p['stock_actual']:.1f} {p['unidad_medida']} (Falta: {deficit:.1f})\n"
        
        # Insertar notificación para usuarios admin
        await conn.execute("""
            INSERT INTO notificaciones 
            (usuario_id, tipo, titulo, mensaje, referencia_tipo, fecha_envio, leido)
            SELECT 
                u.user_id,
                'alerta_inventario',
                'Productos Críticos en Inventario',
                $1,
                'inventario',
                NOW(),
                FALSE
            FROM users u
            WHERE u.rol = 'admin'
        """, mensaje)
        
        return {
            'status': 'success',
            'productos_criticos': len(productos_criticos),
            'alertas_enviadas': True
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        await conn.close()


@celery_app.task(name='backend.tasks.notifications.enviar_seguimiento_tratamiento')
def enviar_seguimiento_tratamiento(cita_id: int, dias_despues: int = 7):
    """
    Tarea manual: Envía seguimiento post-tratamiento N días después de la cita
    
    Args:
        cita_id: ID de la cita
        dias_despues: Días después de la cita para enviar seguimiento
    """
    return asyncio.run(_enviar_seguimiento_async(cita_id, dias_despues))


async def _enviar_seguimiento_async(cita_id: int, dias_despues: int):
    """Versión async de enviar seguimiento"""
    conn = await get_db_connection()
    
    try:
        # Obtener información de la cita
        cita = await conn.fetchrow("""
            SELECT 
                c.cita_id,
                c.fecha_cita,
                p.paciente_id,
                p.nombre as paciente_nombre,
                p.email as paciente_email,
                pod.nombre as podologo_nombre,
                cs.nombre as servicio_nombre
            FROM citas c
            JOIN pacientes p ON c.paciente_id = p.paciente_id
            JOIN podologos pod ON c.podologo_id = pod.podologo_id
            LEFT JOIN catalogo_servicios cs ON c.tratamiento_id = cs.servicio_id
            WHERE c.cita_id = $1
        """, cita_id)
        
        if not cita:
            return {'status': 'error', 'error': 'Cita no encontrada'}
        
        # Calcular fecha de seguimiento
        fecha_seguimiento = cita['fecha_cita'] + timedelta(days=dias_despues)
        
        if datetime.now().date() < fecha_seguimiento.date():
            return {
                'status': 'pending',
                'mensaje': f'Seguimiento programado para {fecha_seguimiento.strftime("%d/%m/%Y")}'
            }
        
        # Crear notificación de seguimiento
        mensaje = f"""
        Hola {cita['paciente_nombre']},
        
        Han pasado {dias_despues} días desde su tratamiento de {cita['servicio_nombre']}.
        
        ¿Cómo se ha sentido? ¿Ha notado mejoría?
        
        Si tiene alguna duda o molestia, no dude en contactarnos.
        
        {cita['podologo_nombre']} y todo el equipo de Podoskin.
        """
        
        await conn.execute("""
            INSERT INTO notificaciones 
            (usuario_id, tipo, titulo, mensaje, referencia_id, referencia_tipo, fecha_envio, leido)
            VALUES (
                (SELECT usuario_id FROM pacientes WHERE paciente_id = $1),
                'seguimiento_tratamiento',
                'Seguimiento de Tratamiento',
                $2,
                $3,
                'cita',
                NOW(),
                FALSE
            )
        """, cita['paciente_id'], mensaje, str(cita_id))
        
        return {
            'status': 'success',
            'cita_id': cita_id,
            'paciente': cita['paciente_nombre'],
            'fecha_envio': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        await conn.close()


@celery_app.task(name='backend.tasks.notifications.limpiar_notificaciones_antiguas')
def limpiar_notificaciones_antiguas(dias: int = 90):
    """
    Tarea periódica: Limpia notificaciones leídas antiguas (>90 días)
    """
    return asyncio.run(_limpiar_notificaciones_async(dias))


async def _limpiar_notificaciones_async(dias: int):
    """Versión async de limpiar notificaciones"""
    conn = await get_db_connection()
    
    try:
        fecha_limite = datetime.now() - timedelta(days=dias)
        
        result = await conn.execute("""
            DELETE FROM notificaciones
            WHERE leido = TRUE
              AND fecha_envio < $1
        """, fecha_limite)
        
        # Extraer número de filas eliminadas
        eliminadas = int(result.split()[-1]) if result else 0
        
        return {
            'status': 'success',
            'notificaciones_eliminadas': eliminadas,
            'fecha_limite': fecha_limite.isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        await conn.close()
