"""
Ejemplo de integración del módulo de citas con FastAPI
======================================================

Este archivo muestra cómo integrar el módulo de citas en una aplicación FastAPI.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar router de citas
import sys
sys.path.insert(0, "/home/runner/work/Podiskin_solution/Podiskin_solution/backend")

from citas import router as citas_router
from citas import service as citas_service


# ============================================================================
# LIFECYCLE MANAGEMENT
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación.
    
    - Inicializa el pool de conexiones al arrancar
    - Cierra las conexiones al apagar
    """
    # Startup
    print("🚀 Iniciando aplicación...")
    
    # Obtener URL de base de datos
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/podoskin"
    )
    
    try:
        # Inicializar pool de conexiones para citas
        citas_service.init_db_pool(database_url)
        print("✅ Pool de conexiones inicializado")
    except Exception as e:
        print(f"❌ Error inicializando pool: {e}")
        raise
    
    yield
    
    # Shutdown
    print("🔌 Cerrando aplicación...")
    citas_service.close_db_pool()
    print("✅ Pool de conexiones cerrado")


# ============================================================================
# CREAR APLICACIÓN
# ============================================================================


app = FastAPI(
    title="Podoskin Solution - Backend API",
    description="API REST para gestión de clínica podológica",
    version="1.0.0",
    lifespan=lifespan,
)

# Configurar CORS
# Obtener orígenes permitidos desde variable de entorno
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Orígenes configurados desde ALLOWED_ORIGINS env var
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REGISTRAR ROUTERS
# ============================================================================


# Incluir router de citas
app.include_router(citas_router)

# Aquí se pueden agregar más routers:
# app.include_router(pacientes_router)
# app.include_router(tratamientos_router)
# etc.


# ============================================================================
# ENDPOINTS BASE
# ============================================================================


@app.get("/")
async def root():
    """Endpoint raíz."""
    return {
        "message": "Podoskin Solution - Backend API",
        "version": "1.0.0",
        "modules": [
            "citas"
        ],
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health():
    """Healthcheck general."""
    return {
        "status": "healthy",
        "service": "podoskin-backend"
    }


# ============================================================================
# EJECUTAR
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║         PODOSKIN SOLUTION - BACKEND API                            ║
    ║         Gestión de Citas - Sistema de Agendamiento                 ║
    ╚════════════════════════════════════════════════════════════════════╝
    
    📚 Endpoints disponibles:
    
    GET    /                          - Información general
    GET    /health                    - Healthcheck
    GET    /docs                      - Documentación interactiva (Swagger)
    GET    /redoc                     - Documentación (ReDoc)
    
    🗓️  Módulo Citas:
    
    GET    /citas/disponibilidad      - Consultar horarios disponibles
    GET    /citas                     - Listar citas (con filtros)
    GET    /citas/{id}                - Obtener cita específica
    POST   /citas                     - Crear nueva cita
    PUT    /citas/{id}                - Actualizar cita
    DELETE /citas/{id}                - Cancelar cita
    
    ⚙️  Configuración:
    
    DATABASE_URL = {db_url}
    
    🚀 Iniciando servidor...
    """.format(
        db_url=os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/podoskin")
    ))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
