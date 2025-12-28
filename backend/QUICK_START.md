# 🚀 Quick Start - Autenticación Backend

Guía rápida para empezar a usar el sistema de autenticación.

## ⚡ Inicio Rápido (5 minutos)

### 1. Instalar Dependencias

```bash
pip install fastapi uvicorn pydantic python-jose[cryptography] passlib[bcrypt] bcrypt python-dotenv psycopg2-binary
```

### 2. Configurar Environment

```bash
# Crear archivo .env
cat > .env << 'ENVEOF'
JWT_SECRET_KEY=tu-clave-secreta-cambiar-en-produccion
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/podoskin_db
ENVEOF
```

### 3. Iniciar Servidor

```bash
python main.py
```

### 4. Probar Login

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"dr.santiago","password":"password123"}'

# Usar token (reemplazar TOKEN con el access_token recibido)
TOKEN="eyJhbGciOiJIUzI1NiIs..."
curl -X GET http://localhost:8000/protected \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Ver Documentación Interactiva

Abrir en navegador: http://localhost:8000/docs

---

## 📚 Documentación Completa

- [auth/README.md](auth/README.md) - Guía completa del módulo
- [ENDPOINTS.md](ENDPOINTS.md) - Lista de endpoints
- [auth/IMPLEMENTATION_SUMMARY.md](auth/IMPLEMENTATION_SUMMARY.md) - Resumen de implementación

---

## 🎯 Uso Básico

### Proteger un Endpoint

```python
from fastapi import APIRouter, Depends
from auth import get_current_user, User

router = APIRouter()

@router.get("/mi-endpoint")
async def mi_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": f"Hola {current_user.nombre_completo}"}
```

### Requerir Rol Específico

```python
from auth import require_role, get_current_user

@router.post("/admin-action")
@require_role(["Admin"])
async def admin_action(current_user: User = Depends(get_current_user)):
    return {"status": "ok"}
```

---

## ✅ Checklist

- [ ] Dependencias instaladas
- [ ] .env configurado con JWT_SECRET_KEY y DATABASE_URL
- [ ] Base de datos corriendo (PostgreSQL con tabla usuarios)
- [ ] Servidor FastAPI iniciado
- [ ] Login exitoso
- [ ] Token JWT recibido
- [ ] Endpoint protegido accedido con token

---

**¿Problemas?** Ver [auth/README.md#troubleshooting](auth/README.md#🐛-troubleshooting)
