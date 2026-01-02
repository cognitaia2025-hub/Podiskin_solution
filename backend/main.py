"""
Podoskin Solution - Backend API

Aplicación principal FastAPI con autenticación.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

# Importar módulo de autenticación
from auth import auth_router, init_db_pool, close_db_pool, get_current_user, User

# Importar módulo de usuarios
from users import router as users_router

# Importar módulo de inventario
from inventory import router as inventory_router

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

# Importar routers de API
from api import live_sessions_router, orchestrator_router

# Importar catálogo de servicios
from catalog.router import router as catalog_router

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Contexto de ciclo de vida de la aplicación.
    Ejecuta código al iniciar y al cerrar la aplicación.
    """
    # Startup
    logger.info("Starting Podoskin Solution Backend...")
    try:
        await init_db_pool()
        logger.info("Auth database pool initialized")
    except Exception as e:
        logger.error(f"Failed to initialize auth database pool: {e}")

    # Inicializar pool de citas (usa psycopg2 sincrono)
    try:
        from citas.database import init_db_pool as init_citas_pool

        init_citas_pool()
        logger.info("Citas database pool initialized")
    except Exception as e:
        logger.error(f"Failed to initialize citas database pool: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Podoskin Solution Backend...")
    try:
        await close_db_pool()
        logger.info("Auth database pool closed")
    except Exception as e:
        logger.error(f"Error closing auth database pool: {e}")

    try:
        from citas.database import close_db_pool as close_citas_pool

        close_citas_pool()
        logger.info("Citas database pool closed")
    except Exception as e:
        logger.error(f"Error closing citas database pool: {e}")


# Crear aplicación FastAPI
app = FastAPI(
    title="Podoskin Solution API",
    description="API para gestión clínica de podología con IA integrada",
    version="1.0.0",
    lifespan=lifespan,
)

# Configurar CORS
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:5174",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router)
app.include_router(users_router, prefix="/api")
app.include_router(inventory_router, prefix="/api")
app.include_router(pacientes_router)
app.include_router(citas_router)
app.include_router(tratamientos_router)
app.include_router(roles_router, prefix="/api")
app.include_router(proveedores_router, prefix="/api")
app.include_router(gastos_router, prefix="/api")
app.include_router(cortes_caja_router, prefix="/api")
app.include_router(catalog_router, prefix="/api")

# Incluir routers de API
app.include_router(live_sessions_router)
app.include_router(orchestrator_router)


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
        except ValueError:
            pass
    if end_date:
        try:
            fecha_fin = datetime.fromisoformat(end_date.replace("Z", "+00:00")).date()
        except ValueError:
            pass

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

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=debug, log_level="info")
