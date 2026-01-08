"""
Configuración de Celery para tareas asíncronas
"""

from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de Redis
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Crear instancia de Celery
celery_app = Celery(
    'podoskin',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        'backend.tasks.notifications',
        'backend.tasks.email_service'
    ]
)

# Configuración de Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Mexico_City',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos máximo
    task_soft_time_limit=25 * 60,  # 25 minutos warning
    result_expires=3600,  # 1 hora
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Configuración de tareas periódicas (Celery Beat)
celery_app.conf.beat_schedule = {
    # Enviar recordatorios de citas cada hora
    'enviar-recordatorios-citas': {
        'task': 'backend.tasks.notifications.enviar_recordatorios_citas',
        'schedule': crontab(minute=0),  # Cada hora en punto
    },
    
    # Enviar recordatorios urgentes 2h antes (cada 30 minutos)
    'enviar-recordatorios-2h': {
        'task': 'backend.tasks.notifications.enviar_recordatorios_2h',
        'schedule': crontab(minute='*/30'),  # Cada 30 minutos
    },
    
    # Revisar productos críticos cada mañana a las 9 AM
    'alertar-productos-criticos': {
        'task': 'backend.tasks.notifications.alertar_productos_criticos',
        'schedule': crontab(hour=9, minute=0),  # 9:00 AM diario
    },
    
    # Enviar resumen diario de citas a las 8 PM
    'resumen-citas-diario': {
        'task': 'backend.tasks.email_service.enviar_resumen_diario',
        'schedule': crontab(hour=20, minute=0),  # 8:00 PM diario
    },
    
    # Generar reporte mensual el primer día del mes a las 10 AM
    'reporte-mensual': {
        'task': 'backend.tasks.email_service.enviar_reporte_mensual',
        'schedule': crontab(hour=10, minute=0, day_of_month=1),  # 1ro de mes a las 10 AM
    },
    
    # Limpiar registros antiguos de notificaciones (cada domingo a las 2 AM)
    'limpiar-notificaciones-antiguas': {
        'task': 'backend.tasks.notifications.limpiar_notificaciones_antiguas',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Domingo 2 AM
    },
}

# Configuración de colas (queues)
celery_app.conf.task_routes = {
    'backend.tasks.notifications.*': {'queue': 'notifications'},
    'backend.tasks.email_service.*': {'queue': 'emails'},
}

if __name__ == '__main__':
    celery_app.start()
