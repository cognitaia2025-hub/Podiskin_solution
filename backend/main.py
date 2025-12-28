"""
Main FastAPI Application
=========================

Aplicación FastAPI principal con autenticación integrada.

Para ejecutar:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""

import os
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import auth module
from .auth import router as auth_router
from .auth import get_current_user, require_podologo, CurrentUser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Podoskin Solution API",
    description="API REST para gestión de clínica de podología con autenticación JWT",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)


@app.get("/", tags=["Health"])
async def root():
    """
    Health check endpoint
    """
    return {
        "status": "ok",
        "service": "Podoskin Solution API",
        "version": "1.0.0"
    }


@app.get("/protected", tags=["Test"])
async def protected_route(current_user: CurrentUser = Depends(get_current_user)):
    """
    Ruta protegida de ejemplo - requiere autenticación
    
    Requiere: Header "Authorization: Bearer {token}"
    """
    return {
        "message": "Esta es una ruta protegida",
        "user": {
            "username": current_user.username,
            "rol": current_user.rol,
            "nombre_completo": current_user.nombre_completo
        }
    }


@app.get("/admin-only", tags=["Test"])
async def admin_only_route(current_user: CurrentUser = Depends(require_podologo())):
    """
    Ruta solo para podólogos - requiere autenticación y rol Podologo o Admin
    
    Requiere: 
    - Header "Authorization: Bearer {token}"
    - Rol: Admin o Podologo
    """
    return {
        "message": "Esta es una ruta solo para podólogos y administradores",
        "user": {
            "username": current_user.username,
            "rol": current_user.rol
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
