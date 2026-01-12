"""
Servicio de envío de emails con templates Jinja2
"""

from tasks.celery_app import celery_app
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime, timedelta
from db import get_connection, release_connection
import asyncio
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path

# Configuración de email
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_FROM = os.getenv('SMTP_FROM', 'noreply@podoskin.com')

# Configurar Jinja2
templates_dir = Path(__file__).parent / 'templates'
templates_dir.mkdir(exist_ok=True)

jinja_env = Environment(
    loader=FileSystemLoader(str(templates_dir)),
    autoescape=select_autoescape(['html', 'xml'])
)


def enviar_email(destinatario: str, asunto: str, html: str, archivos_adjuntos: list = None):
    """
    Envía un email HTML
    
    Args:
        destinatario: Email del destinatario
        asunto: Asunto del email
        html: Contenido HTML del email
        archivos_adjuntos: Lista de (filename, content) tuplas
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        print("⚠️ Credenciales SMTP no configuradas. Email no enviado.")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_FROM
        msg['To'] = destinatario
        msg['Subject'] = asunto
        
        # Agregar contenido HTML
        html_part = MIMEText(html, 'html')
        msg.attach(html_part)
        
        # Agregar archivos adjuntos si existen
        if archivos_adjuntos:
            for filename, content in archivos_adjuntos:
                attachment = MIMEApplication(content)
                attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(attachment)
        
        # Enviar email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False


@celery_app.task(name='backend.tasks.email_service.enviar_confirmacion_cita')
def enviar_confirmacion_cita(cita_id: int):
    """
    Tarea: Envía email de confirmación de cita al paciente
    """
    return asyncio.run(_enviar_confirmacion_cita_async(cita_id))


async def _enviar_confirmacion_cita_async(cita_id: int):
    """Versión async de enviar confirmación de cita"""
    conn = await get_connection()
    
    try:
        # Obtener información de la cita
        cita = await conn.fetchrow("""
            SELECT 
                c.cita_id,
                c.fecha_cita,
                c.hora_inicio,
                c.hora_fin,
                p.nombre as paciente_nombre,
                p.email as paciente_email,
                pod.nombre as podologo_nombre,
                pod.telefono as podologo_telefono,
                cs.nombre as servicio_nombre,
                cs.precio_base
            FROM citas c
            JOIN pacientes p ON c.paciente_id = p.paciente_id
            JOIN podologos pod ON c.podologo_id = pod.podologo_id
            LEFT JOIN catalogo_servicios cs ON c.tratamiento_id = cs.servicio_id
            WHERE c.cita_id = $1
        """, cita_id)
        
        if not cita or not cita['paciente_email']:
            return {'status': 'error', 'error': 'Cita no encontrada o email no disponible'}
        
        # Template HTML (inline por simplicidad)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #366092; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 20px; }}
                .cita-info {{ background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #366092; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #366092; color: white; text-decoration: none; border-radius: 4px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Confirmación de Cita</h1>
                    <p>Podoskin Solution</p>
                </div>
                <div class="content">
                    <h2>Hola {cita['paciente_nombre']},</h2>
                    <p>Su cita ha sido confirmada exitosamente:</p>
                    
                    <div class="cita-info">
                        <p><strong>📅 Fecha:</strong> {cita['fecha_cita'].strftime('%d de %B de %Y')}</p>
                        <p><strong>🕐 Hora:</strong> {cita['hora_inicio'].strftime('%H:%M')} - {cita['hora_fin'].strftime('%H:%M')}</p>
                        <p><strong>👨‍⚕️ Podólogo:</strong> {cita['podologo_nombre']}</p>
                        <p><strong>🔬 Servicio:</strong> {cita['servicio_nombre']}</p>
                        <p><strong>💰 Precio:</strong> ${cita['precio_base']:,.2f} MXN</p>
                    </div>
                    
                    <p>📞 Para cualquier duda o cambio, contacte al: {cita['podologo_telefono']}</p>
                    
                    <p><strong>Importante:</strong> Por favor llegue 10 minutos antes de su cita.</p>
                </div>
                <div class="footer">
                    <p>Este es un correo automático, por favor no responder.</p>
                    <p>&copy; {datetime.now().year} Podoskin Solution. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Enviar email
        enviado = enviar_email(
            cita['paciente_email'],
            f"Confirmación de Cita - {cita['fecha_cita'].strftime('%d/%m/%Y')}",
            html
        )
        
        return {
            'status': 'success' if enviado else 'error',
            'cita_id': cita_id,
            'destinatario': cita['paciente_email'],
            'enviado': enviado
        }
        
    except Exception as e:
        return {'status': 'error', 'error': str(e)}
    finally:
        await release_connection(conn)


@celery_app.task(name='backend.tasks.email_service.enviar_resumen_diario')
def enviar_resumen_diario():
    """
    Tarea periódica: Envía resumen diario de citas a administradores
    """
    return asyncio.run(_enviar_resumen_diario_async())


async def _enviar_resumen_diario_async():
    """Versión async de enviar resumen diario"""
    conn = await get_connection()
    
    try:
        hoy = datetime.now().date()
        manana = hoy + timedelta(days=1)
        
        # Obtener citas del día siguiente
        citas = await conn.fetch("""
            SELECT 
                c.cita_id,
                c.fecha_cita,
                c.hora_inicio,
                c.estado,
                p.nombre as paciente_nombre,
                pod.nombre as podologo_nombre,
                cs.nombre as servicio_nombre
            FROM citas c
            JOIN pacientes p ON c.paciente_id = p.paciente_id
            JOIN podologos pod ON c.podologo_id = pod.podologo_id
            LEFT JOIN catalogo_servicios cs ON c.tratamiento_id = cs.servicio_id
            WHERE c.fecha_cita = $1
            ORDER BY c.hora_inicio
        """, manana)
        
        # Obtener emails de administradores
        admins = await conn.fetch("""
            SELECT email FROM users WHERE rol = 'admin' AND email IS NOT NULL
        """)
        
        if not admins:
            return {'status': 'error', 'error': 'No hay administradores con email'}
        
        # Generar HTML del resumen
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #366092; color: white; padding: 20px; text-align: center; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background: #366092; color: white; padding: 10px; text-align: left; }}
                td {{ border: 1px solid #ddd; padding: 10px; }}
                tr:nth-child(even) {{ background: #f9f9f9; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Resumen de Citas - {manana.strftime('%d/%m/%Y')}</h1>
                </div>
                <p>Total de citas programadas: <strong>{len(citas)}</strong></p>
                <table>
                    <thead>
                        <tr>
                            <th>Hora</th>
                            <th>Paciente</th>
                            <th>Podólogo</th>
                            <th>Servicio</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for cita in citas:
            html += f"""
                        <tr>
                            <td>{cita['hora_inicio'].strftime('%H:%M')}</td>
                            <td>{cita['paciente_nombre']}</td>
                            <td>{cita['podologo_nombre']}</td>
                            <td>{cita['servicio_nombre'] or 'N/A'}</td>
                            <td>{cita['estado']}</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        # Enviar a todos los administradores
        enviados = 0
        for admin in admins:
            if enviar_email(admin['email'], f"Resumen de Citas - {manana.strftime('%d/%m/%Y')}", html):
                enviados += 1
        
        return {
            'status': 'success',
            'total_citas': len(citas),
            'emails_enviados': enviados,
            'fecha': manana.isoformat()
        }
        
    except Exception as e:
        return {'status': 'error', 'error': str(e)}
    finally:
        await release_connection(conn)


@celery_app.task(name='backend.tasks.email_service.enviar_reporte_mensual')
def enviar_reporte_mensual():
    """
    Tarea periódica: Genera y envía reporte mensual a administradores
    """
    return asyncio.run(_enviar_reporte_mensual_async())


async def _enviar_reporte_mensual_async():
    """Versión async de enviar reporte mensual"""
    conn = await get_connection()
    
    try:
        # Calcular mes anterior
        hoy = datetime.now()
        primer_dia_mes_actual = hoy.replace(day=1)
        ultimo_dia_mes_anterior = primer_dia_mes_actual - timedelta(days=1)
        primer_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)
        
        # Obtener estadísticas del mes
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(DISTINCT c.cita_id) as total_citas,
                COUNT(DISTINCT c.paciente_id) as total_pacientes,
                COALESCE(SUM(p.monto), 0) as total_ingresos,
                (SELECT COUNT(*) FROM citas WHERE estado = 'cancelada' 
                 AND fecha_cita BETWEEN $1 AND $2) as citas_canceladas
            FROM citas c
            LEFT JOIN pagos p ON c.cita_id = p.cita_id
            WHERE c.fecha_cita BETWEEN $1 AND $2
        """, primer_dia_mes_anterior, ultimo_dia_mes_anterior)
        
        # Obtener emails de administradores
        admins = await conn.fetch("SELECT email FROM users WHERE rol = 'admin' AND email IS NOT NULL")
        
        mes_nombre = primer_dia_mes_anterior.strftime('%B %Y')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #366092; color: white; padding: 20px; text-align: center; }}
                .metric {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #366092; }}
                .metric h3 {{ margin: 0; color: #366092; }}
                .metric p {{ font-size: 24px; margin: 10px 0; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Reporte Mensual</h1>
                    <p>{mes_nombre}</p>
                </div>
                <div class="metric">
                    <h3>📅 Citas Realizadas</h3>
                    <p>{stats['total_citas']}</p>
                </div>
                <div class="metric">
                    <h3>👥 Pacientes Atendidos</h3>
                    <p>{stats['total_pacientes']}</p>
                </div>
                <div class="metric">
                    <h3>💰 Ingresos Totales</h3>
                    <p>${stats['total_ingresos']:,.2f} MXN</p>
                </div>
                <div class="metric">
                    <h3>❌ Citas Canceladas</h3>
                    <p>{stats['citas_canceladas']}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Enviar a administradores
        enviados = 0
        for admin in admins:
            if enviar_email(admin['email'], f"Reporte Mensual - {mes_nombre}", html):
                enviados += 1
        
        return {
            'status': 'success',
            'emails_enviados': enviados,
            'mes': mes_nombre,
            'metricas': dict(stats)
        }
        
    except Exception as e:
        return {'status': 'error', 'error': str(e)}
    finally:
        await release_connection(conn)
