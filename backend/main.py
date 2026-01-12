"""
Podoskin Solution - Backend API

Aplicación principal FastAPI con autenticación.
"""

from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date
from typing import Optional
from contextlib import asynccontextmanager  # ✅ AGREGAR ESTA LÍNEA
import logging
import os
from dotenv import load_dotenv

# Cargar variables de entorno AL PRINCIPIO
load_dotenv()

# Importar módulo de autenticación
from auth import auth_router, get_current_user, User

# Importar módulo de usuarios
from users import router as users_router

# Importar módulo de inventario
from inventory import router as inventory_router

# Importar módulo de podólogos
from podologos import router as podologos_router
from podologos.patients_router import router as podologos_patients_router

# Importar routers de módulos principales
# Importar routers de módulos principales
# Nota: Importamos desde .router explícitamente para evitar problemas si falta __init__.py
from pacientes.router import router as pacientes_router
from citas.router import router as citas_router
from tratamientos.router import router as tratamientos_router
from roles.router import router as roles_router
from proveedores.router import router as proveedores_router
from gastos.router import router as gastos_router
from cortes_caja.router import router as cortes_caja_router
from pagos.router import router as pagos_router
from facturas.router import router as facturas_router
from audit.router import router as audit_router

# Importar routers de API
from api import live_sessions_router, orchestrator_router

# Importar Twilio Webhook Router
from api.twilio_webhook import router as twilio_webhook_router

# Importar WhatsApp Management API
from api.whatsapp_management_api import router as whatsapp_mgmt_router

# Importar Web Chat API (mismo agente para web y WhatsApp)
from api.web_chat_api import router as web_chat_router

# Importar middleware de rate limiting
from middleware.rate_limit import rate_limit_middleware

# Importar catálogo de servicios
from catalog.router import router as catalog_router

# Importar horarios
from horarios.router import router as horarios_router

# Importar estadísticas
from stats.router import router as stats_router

# Importar expedientes médicos
from medical_records.router import router as medical_records_router

# Importar reportes
from reportes.router import router as reportes_router

# Importar analytics
from analytics.router import router as analytics_router

# Importar WebSocket para notificaciones
from ws_notifications.notifications_ws import router as websocket_router

# Importar Agente WhatsApp (LangGraph) - AI Agent System
from agents.whatsapp_medico.api import router as whatsapp_agent_router

# Configurar logging - Solo WARNING y ERROR para reducir ruido
# Cambiar a INFO temporalmente si necesitas depurar
logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Contexto de ciclo de vida de la aplicación.
    Ejecuta código al iniciar y al cerrar la aplicación.
    """
    # ✅ Startup
    logger.info("Starting Podoskin Solution Backend...")
    
    # ⚠️ Validar variables de entorno críticas
    required_env_vars = [
        "DB_HOST",
        "DB_PORT", 
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",  # Crítico para seguridad
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ FALTAN VARIABLES DE ENTORNO CRÍTICAS: {', '.join(missing_vars)}")
        logger.error("📝 Revisa el archivo .env.example para la configuración requerida")
        raise RuntimeError(
            f"Variables de entorno requeridas no configuradas: {', '.join(missing_vars)}. "
            "Revisa .env.example"
        )
    
    # Validar que DB_PASSWORD no sea el valor inseguro por defecto
    db_password = os.getenv("DB_PASSWORD")
    if db_password == "podoskin_password_123":
        logger.warning("⚠️ ADVERTENCIA: Usando password por defecto inseguro!")

    # Inicializar pool centralizado de AsyncPG
    try:
        from db import init_db_pool

        await init_db_pool()
        logger.info("✅ Database pool initialized (AsyncPG)")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database pool: {e}")
        raise

    yield  # ← La aplicación corre aquí

    # ✅ Shutdown
    logger.info("Shutting down Podoskin Solution Backend...")

    try:
        from db import close_db_pool

        await close_db_pool()
        logger.info("✅ Database pool closed")
    except Exception as e:
        logger.error(f"❌ Error closing database pool: {e}")


# Crear aplicación FastAPI
app = FastAPI(
    title="Podoskin Solution API",
    description="API para gestión clínica de podología con IA integrada",
    version="1.0.0",
    lifespan=lifespan,  # ← Usa lifespan
)

# Configurar CORS
from fastapi.middleware.cors import CORSMiddleware
from config.cors_config import CORS_CONFIG


# Configurar CORS con configuración centralizada
app.add_middleware(CORSMiddleware, **CORS_CONFIG)

# Configurar rate limiting middleware (para WhatsApp webhook)
app.middleware("http")(rate_limit_middleware)

# Incluir routers
app.include_router(auth_router)
app.include_router(users_router, prefix="/api")
app.include_router(inventory_router, prefix="/api")
app.include_router(podologos_router, prefix="/api")
app.include_router(pacientes_router)
app.include_router(citas_router)
app.include_router(tratamientos_router)
app.include_router(roles_router, prefix="/api")
app.include_router(proveedores_router, prefix="/api")
app.include_router(gastos_router, prefix="/api")
app.include_router(cortes_caja_router, prefix="/api")
app.include_router(pagos_router, prefix="/api")
app.include_router(facturas_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(catalog_router, prefix="/api")
app.include_router(horarios_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(medical_records_router)
app.include_router(reportes_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(whatsapp_agent_router)  # WhatsApp Agent (LangGraph) - AI System

# WebSocket para notificaciones en tiempo real (sin prefix /api)
app.include_router(websocket_router)

# Incluir routers de API
app.include_router(live_sessions_router)
app.include_router(orchestrator_router)
app.include_router(twilio_webhook_router)  # Twilio WhatsApp Webhook
app.include_router(whatsapp_mgmt_router)  # WhatsApp Management API
app.include_router(web_chat_router)  # Web Chat API (mismo agente que WhatsApp)

# Importar módulo de permisos
from auth.permissions_router import router as permissions_router

# Registrar routers
app.include_router(auth_router)
app.include_router(permissions_router)
app.include_router(podologos_patients_router)  # ✅ AGREGAR ESTA LÍNEA


# ============================================================================
# ENDPOINTS COMPATIBILIDAD FRONTEND
# ============================================================================

from typing import Optional
from fastapi import Query
from datetime import datetime
from citas import service as citas_service


@app.get("/appointments", tags=["Appointments"])
async def get_appointments(
    start_date: Optional[str] = Query(None, description="Fecha inicio ISO"),
    end_date: Optional[str] = Query(None, description="Fecha fin ISO"),
    doctor_id: Optional[str] = Query(
        None, description="IDs de doctores separados por coma"
    ),
):
    """
    Endpoint /appointments para compatibilidad con el frontend.
    El frontend llama a /appointments con query params en formato diferente.
    """
    # Parsear doctor_ids si vienen como "1,2,3"
    id_podologo = None
    if doctor_id:
        doctor_ids = [int(id.strip()) for id in doctor_id.split(",")]
        id_podologo = doctor_ids[0] if len(doctor_ids) == 1 else None

    # Parsear fechas
    fecha_inicio = None
    fecha_fin = None
    if start_date:
        try:
            fecha_inicio = datetime.fromisoformat(
                start_date.replace("Z", "+00:00")
            ).date()
        except ValueError as e:
            logger.warning(f"Formato de fecha inválido en start_date: {start_date} - {e}")
            fecha_inicio = None
    if end_date:
        try:
            fecha_fin = datetime.fromisoformat(end_date.replace("Z", "+00:00")).date()
        except ValueError as e:
            logger.warning(f"Formato de fecha inválido en end_date: {end_date} - {e}")
            fecha_fin = None

    # Llamar al servicio de citas
    citas, total = await citas_service.obtener_citas(
        id_podologo=id_podologo,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        limit=100,
        offset=0,
    )

    return {"total": total, "citas": citas}


# ============================================================================
# ENDPOINTS DE EJEMPLO
# ============================================================================


@app.get("/")
async def root():
    """Endpoint raíz - información de la API"""
    return {
        "message": "Podoskin Solution API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check de la aplicación"""
    return {"status": "healthy", "service": "podoskin-backend", "version": "1.0.0"}


@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """
    Ejemplo de endpoint protegido que requiere autenticación.

    Debes enviar el token JWT en el header:
    Authorization: Bearer <tu_token_aqui>
    """
    return {
        "message": f"Hola {current_user.nombre_completo}",
        "user_id": current_user.id,
        "username": current_user.nombre_usuario,
        "rol": current_user.rol,
    }


# ============================================================================
# EJEMPLO DE USO DE AUTORIZACIÓN RBAC
# ============================================================================

from auth import require_role, AdminOnly


@app.get("/admin-only")
async def admin_only_route(current_user: User = Depends(AdminOnly)):
    """
    Endpoint que solo puede acceder un administrador.

    Usa el RoleChecker AdminOnly como dependency.
    """
    return {
        "message": "Acceso permitido solo para administradores",
        "admin": current_user.nombre_completo,
    }


@app.post("/staff-action")
@require_role(["Admin", "Podologo", "Recepcionista"])
async def staff_action(current_user: User = Depends(get_current_user)):
    """
    Endpoint que pueden acceder Admin, Podologo o Recepcionista.

    Usa el decorator @require_role.
    """
    return {
        "message": "Acción de staff ejecutada",
        "user": current_user.nombre_completo,
        "rol": current_user.rol,
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    # log_level="warning" para reducir ruido. Cambiar a "info" para depurar
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=debug, log_level="warning")
