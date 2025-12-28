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

# Importar routers de módulos principales
from pacientes import router as pacientes_router
from citas import router as citas_router
from tratamientos import router as tratamientos_router

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
        logger.info("Database pool initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Podoskin Solution Backend...")
    try:
        await close_db_pool()
        logger.info("Database pool closed")
    except Exception as e:
        logger.error(f"Error closing database pool: {e}")


# Crear aplicación FastAPI
app = FastAPI(
    title="Podoskin Solution API",
    description="API para gestión clínica de podología con IA integrada",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router)
app.include_router(pacientes_router)
app.include_router(citas_router, prefix="/citas", tags=["Citas"])
app.include_router(tratamientos_router)


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
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check de la aplicación"""
    return {
        "status": "healthy",
        "service": "podoskin-backend",
        "version": "1.0.0"
    }


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
        "rol": current_user.rol
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
        "admin": current_user.nombre_completo
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
        "rol": current_user.rol
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="info"
    )
