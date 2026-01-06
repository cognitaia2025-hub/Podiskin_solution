"""
Ejemplo de Uso del Sistema de Autenticación
============================================

Ejemplo completo mostrando cómo usar el sistema de autenticación.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse

# Import auth components
from auth import (
    router as auth_router,
    get_current_user,
    require_admin,
    require_podologo,
    require_recepcion,
    require_any_authenticated,
    CurrentUser
)

# Create FastAPI app
app = FastAPI(
    title="Podoskin Auth Example",
    description="Ejemplo de uso del sistema de autenticación"
)

# Include auth router
app.include_router(auth_router)


# ============================================================================
# EJEMPLOS DE ENDPOINTS PROTEGIDOS
# ============================================================================

@app.get("/")
async def root():
    """Endpoint público - no requiere autenticación"""
    return {
        "message": "Bienvenido a Podoskin API",
        "auth": "Use POST /auth/login para autenticarse"
    }


@app.get("/profile")
async def get_profile(current_user: CurrentUser = Depends(get_current_user)):
    """
    Endpoint protegido - requiere autenticación
    
    Cualquier usuario autenticado puede acceder
    """
    return {
        "message": "Perfil de usuario",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "rol": current_user.rol,
            "nombre_completo": current_user.nombre_completo
        }
    }


@app.get("/admin/dashboard")
async def admin_dashboard(current_user: CurrentUser = Depends(require_admin())):
    """
    Endpoint solo para administradores
    
    Solo usuarios con rol "Admin" pueden acceder
    """
    return {
        "message": "Dashboard de administración",
        "user": current_user.username,
        "data": {
            "total_usuarios": 10,
            "total_pacientes": 150
        }
    }


@app.get("/podologo/pacientes")
async def get_pacientes(current_user: CurrentUser = Depends(require_podologo())):
    """
    Endpoint para podólogos
    
    Usuarios con rol "Admin" o "Podologo" pueden acceder
    """
    return {
        "message": "Lista de pacientes",
        "user": current_user.username,
        "rol": current_user.rol,
        "pacientes": [
            {"id": 1, "nombre": "Juan Pérez"},
            {"id": 2, "nombre": "María García"}
        ]
    }


@app.post("/recepcion/citas")
async def crear_cita(
    cita_data: dict,
    current_user: CurrentUser = Depends(require_recepcion())
):
    """
    Endpoint para recepción
    
    Usuarios con rol "Admin", "Podologo" o "Recepcionista" pueden acceder
    """
    return {
        "message": "Cita creada exitosamente",
        "created_by": current_user.username,
        "rol": current_user.rol,
        "cita": cita_data
    }


@app.get("/dashboard")
async def dashboard(current_user: CurrentUser = Depends(require_any_authenticated())):
    """
    Dashboard general
    
    Cualquier usuario autenticado puede acceder
    """
    # Datos personalizados por rol
    data = {
        "Admin": {
            "widgets": ["usuarios", "pacientes", "citas", "finanzas"],
            "permissions": ["all"]
        },
        "Podologo": {
            "widgets": ["mis_citas", "mis_pacientes", "tratamientos"],
            "permissions": ["view_patients", "manage_appointments"]
        },
        "Recepcionista": {
            "widgets": ["agenda", "nuevas_citas", "pacientes"],
            "permissions": ["view_patients", "create_appointments"]
        },
        "Asistente": {
            "widgets": ["agenda_dia"],
            "permissions": ["view_appointments"]
        }
    }
    
    return {
        "message": "Dashboard",
        "user": {
            "username": current_user.username,
            "rol": current_user.rol
        },
        "dashboard": data.get(current_user.rol, {})
    }


# ============================================================================
# ENDPOINT DE INFORMACIÓN
# ============================================================================

@app.get("/auth/info")
async def auth_info():
    """
    Información sobre el sistema de autenticación
    """
    return {
        "authentication": {
            "type": "JWT",
            "token_type": "Bearer",
            "expires_in": 3600,
            "header": "Authorization: Bearer {token}"
        },
        "roles": {
            "Admin": "Acceso total al sistema",
            "Podologo": "Acceso clínico completo",
            "Recepcionista": "Gestión de citas y pacientes",
            "Asistente": "Acceso limitado"
        },
        "endpoints": {
            "public": [
                "GET / - Home",
                "GET /auth/info - Esta información",
                "GET /docs - Documentación interactiva"
            ],
            "authenticated": [
                "GET /profile - Perfil de usuario (cualquier rol)",
                "GET /dashboard - Dashboard personalizado (cualquier rol)"
            ],
            "admin_only": [
                "GET /admin/dashboard - Dashboard admin"
            ],
            "podologo": [
                "GET /podologo/pacientes - Lista de pacientes (Admin, Podologo)"
            ],
            "recepcion": [
                "POST /recepcion/citas - Crear cita (Admin, Podologo, Recepcionista)"
            ]
        },
        "usage": {
            "1_login": "POST /auth/login con username y password",
            "2_get_token": "Obtener access_token de la respuesta",
            "3_use_token": "Incluir en header: Authorization: Bearer {token}",
            "4_access": "Acceder a endpoints protegidos"
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("🚀 Iniciando servidor de ejemplo...")
    print("=" * 60)
    print("\n📚 Documentación interactiva:")
    print("   → http://localhost:8000/docs")
    print("\n📖 Información de autenticación:")
    print("   → http://localhost:8000/auth/info")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(
        "example_usage:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
