"""
Ejemplo de Aplicación FastAPI - Tratamientos
============================================

Aplicación de ejemplo que muestra cómo integrar el módulo de tratamientos.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar router y utilidades de base de datos
from tratamientos import router as tratamientos_router
from tratamientos.database import init_db_pool, close_db_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación.
    Inicializa y cierra el pool de conexiones a la base de datos.
    """
    print("🚀 Iniciando aplicación...")
    await init_db_pool()
    print("✅ Conexión a base de datos establecida")
    
    yield
    
    print("🔌 Cerrando conexiones...")
    await close_db_pool()
    print("✅ Aplicación cerrada correctamente")


# Crear aplicación FastAPI
app = FastAPI(
    title="Podoskin Solution - API de Tratamientos",
    description="API REST para gestión de tratamientos, signos vitales y diagnósticos médicos",
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

# Incluir router de tratamientos
app.include_router(tratamientos_router)


@app.get("/")
async def root():
    """Endpoint raíz con información de la API."""
    return {
        "message": "Podoskin Solution - API de Tratamientos",
        "version": "1.0.0",
        "endpoints": {
            "tratamientos": "/api/tratamientos",
            "signos_vitales": "/api/citas/{id}/signos-vitales",
            "diagnosticos": "/api/citas/{id}/diagnosticos",
            "cie10": "/api/diagnosticos/cie10",
            "docs": "/docs",
            "openapi": "/openapi.json",
        }
    }


@app.get("/health")
async def health_check():
    """Endpoint de health check."""
    return {
        "status": "healthy",
        "service": "tratamientos-api"
    }


# Para ejecutar la aplicación:
# uvicorn app_example:app --reload --port 8000
#
# Documentación interactiva disponible en:
# - http://localhost:8000/docs (Swagger UI)
# - http://localhost:8000/redoc (ReDoc)
