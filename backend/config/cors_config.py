"""
Configuración CORS para Backend
================================
Centraliza configuración de CORS para desarrollo y producción
"""

import os
from typing import List

def get_cors_origins() -> List[str]:
    """
    Obtiene los orígenes permitidos según el entorno.
    
    En desarrollo: Permite localhost
    En producción: Solo dominios específicos
    
    Returns:
        Lista de orígenes permitidos
    """
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        # Dominios de producción (CONFIGURAR SEGÚN TU DOMINIO)
        return [
            "https://podoskin.com",
            "https://www.podoskin.com",
            "https://app.podoskin.com",
        ]
    else:
        # Desarrollo: Permite localhost y variantes
        return [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:3000",
        ]

def get_cors_config() -> dict:
    """
    Configuración completa de CORS.
    
    Returns:
        Diccionario con configuración CORS
    """
    return {
        "allow_origins": get_cors_origins(),
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        "allow_headers": ["*"],
        "expose_headers": ["Content-Range", "X-Content-Range"],
        "max_age": 600,  # Cache preflight por 10 minutos
    }

# Configuración por defecto
CORS_CONFIG = get_cors_config()
