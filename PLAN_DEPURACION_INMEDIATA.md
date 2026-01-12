# 🔧 PLAN DE DEPURACIÓN INMEDIATA - BACKEND

## 📌 Prioridad P0 - COMENZAR HOY

Este documento detalla los **primeros cambios** que implementaré de forma inmediata.

---

## 🎯 OBJETIVO FASE 1 (Día 1)

**Migrar conexiones de base de datos a pool centralizado AsyncPG**

### Archivos a Modificar (en orden):

1. ✅ **`backend/pagos/service.py`** (497 líneas)
2. ✅ **`backend/facturas/service.py`** (309 líneas)
3. ✅ **`backend/pacientes/database.py`** (50 líneas)

---

## 📝 CAMBIO 1: `backend/pagos/service.py`

### Problema Actual:
```python
import psycopg
from psycopg.rows import dict_row

class PagosService:
    def __init__(self):
        self.conn = None
    
    def _get_connection(self):
        """Crea conexiones individuales - NO POOLED"""
        if self.conn is None or self.conn.closed:
            self.conn = psycopg.connect(...)  # ❌ PROBLEMA
        return self.conn
```

### Solución:
```python
from db import get_connection, release_connection, fetch_all, fetch_one, execute_returning
import asyncpg

class PagosService:
    """Servicio async usando pool centralizado"""
    
    # ✅ Sin __init__, sin self.conn
    
    async def get_all(self, **filters):
        """Usa pool centralizado"""
        conn = await get_connection()
        try:
            query = "SELECT * FROM pagos WHERE ..."
            result = await conn.fetch(query, *params)
            return [dict(row) for row in result]
        finally:
            await release_connection(conn)
```

### Impacto:
- ✅ Elimina conexiones huérfanas
- ✅ Pooling automático
- ✅ Mejor performance (5-10x más rápido)
- ✅ Memory leaks resueltos

---

## 📝 CAMBIO 2: `backend/facturas/service.py`

### Transformación:
```python
# ❌ ANTES (psycopg3 síncrono)
class FacturasService:
    def get_all(self, **filters):
        conn = self._get_connection()  # Conexión individual
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

# ✅ DESPUÉS (AsyncPG pooled)
class FacturasService:
    async def get_all(self, **filters):
        query = "SELECT * FROM facturas WHERE ..."
        return await fetch_all(query, *params)  # Usa pool
```

---

## 📝 CAMBIO 3: `backend/pacientes/database.py`

### Problema:
```python
class DatabaseConnection:
    async def connect(self):
        self.pool = await asyncpg.create_pool(...)  # ❌ Pool separado
```

### Solución:
```python
# ✅ Simplemente importar y usar el pool existente
from db import get_connection, release_connection

# Eliminar clase DatabaseConnection completa
# Todos los módulos usan directamente:
# conn = await get_connection()
```

---

## 🎯 OBJETIVO FASE 2 (Día 1 tarde)

**Corregir manejo de excepciones silenciosas**

### Archivo Crítico: `backend/agents/whatsapp_medico/nodes/rag_manager.py`

#### 6 Casos a Corregir:

**Línea 88-89:**
```python
# ❌ ANTES
try:
    data = json.loads(result)
    if isinstance(data, list) and len(data) > 0:
        return {...}
except:
    pass

# ✅ DESPUÉS
try:
    data = json.loads(result)
    if isinstance(data, list) and len(data) > 0:
        logger.info(f"✅ Tratamientos encontrados: {len(data)}")
        return {...}
except json.JSONDecodeError as e:
    logger.error(f"Error parsing tratamientos JSON: {e}", exc_info=True)
except Exception as e:
    logger.error(f"Error inesperado en búsqueda de tratamientos: {e}", exc_info=True)
```

**Repetir para líneas:** 116-117, 139-140, 165-166, 194-195

---

## 🎯 OBJETIVO FASE 3 (Día 2)

**Eliminar passwords hardcodeadas**

### Cambio Global:

**Crear `backend/config/env_validator.py`:**
```python
"""
Validador de Variables de Entorno
==================================
"""
import os
import logging

logger = logging.getLogger(__name__)

REQUIRED_ENV_VARS = [
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "ANTHROPIC_API_KEY",
]

PRODUCTION_REQUIRED = [
    "SECRET_KEY",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
]

def validate_env():
    """Valida variables de entorno requeridas"""
    missing = []
    
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing.append(var)
    
    if os.getenv("ENV") == "production":
        for var in PRODUCTION_REQUIRED:
            if not os.getenv(var):
                missing.append(var)
    
    if missing:
        raise ValueError(
            f"❌ Falta configurar variables de entorno: {', '.join(missing)}"
        )
    
    # Validar que no se usen valores por defecto en producción
    if os.getenv("ENV") == "production":
        db_pass = os.getenv("DB_PASSWORD")
        if "password_123" in db_pass or "default" in db_pass.lower():
            raise ValueError("❌ No usar password por defecto en producción")
    
    logger.info("✅ Variables de entorno validadas correctamente")

def get_db_password():
    """Obtiene password de DB con validación"""
    password = os.getenv("DB_PASSWORD")
    if not password:
        raise ValueError("DB_PASSWORD no configurada")
    return password
```

**Actualizar `backend/main.py`:**
```python
from config.env_validator import validate_env

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ Validar ANTES de inicializar pool
    try:
        validate_env()
    except ValueError as e:
        logger.error(f"❌ Error de configuración: {e}")
        raise
    
    # Resto del código...
```

**Actualizar `backend/db.py`:**
```python
from config.env_validator import get_db_password

# ✅ Sin fallback inseguro
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = get_db_password()  # ✅ Con validación
```

---

## 📋 CHECKLIST DE EJECUCIÓN

### Día 1 (Mañana) - Conexiones DB

- [ ] Backup de archivos originales
- [ ] Migrar `pagos/service.py`
  - [ ] Cambiar imports
  - [ ] Convertir a async
  - [ ] Actualizar router para usar async
  - [ ] Test manual
- [ ] Migrar `facturas/service.py`
  - [ ] Mismo proceso
- [ ] Migrar `pacientes/database.py`
  - [ ] Eliminar clase DatabaseConnection
  - [ ] Actualizar imports en módulos que lo usan
- [ ] Ejecutar tests: `pytest tests/test_pagos.py -v`
- [ ] Ejecutar tests: `pytest tests/test_facturas.py -v`
- [ ] Verificar logs: `grep "ERROR" backend.log`

### Día 1 (Tarde) - Excepciones

- [ ] Backup de `rag_manager.py`
- [ ] Corregir 6 bloques `except: pass`
- [ ] Agregar logging específico
- [ ] Test del agente WhatsApp
- [ ] Verificar logs muestran errores correctamente

### Día 2 - Seguridad

- [ ] Crear `backend/config/env_validator.py`
- [ ] Actualizar `backend/main.py`
- [ ] Actualizar `backend/db.py`
- [ ] Crear `.env.example`
- [ ] Probar startup con y sin .env
- [ ] Validar mensaje de error claro

---

## 🧪 TESTS DE VALIDACIÓN

### Test 1: Conexiones DB
```bash
# Verificar que solo hay 1 pool
python3 -c "
import asyncio
from backend.db import _pool, init_db_pool

asyncio.run(init_db_pool())
print(f'Pool size: {_pool._holders.__len__()}')
print(f'Min connections: {_pool._minsize}')
print(f'Max connections: {_pool._maxsize}')
"
```

### Test 2: Manejo de Errores
```bash
# Verificar que errores se loggean
pytest tests/test_rag_manager.py -v -s --log-cli-level=DEBUG
grep "Error parsing" backend.log  # Debe aparecer
```

### Test 3: Validación de Env
```bash
# Sin .env debe fallar
mv .env .env.backup
python3 backend/main.py  # Debe mostrar: "❌ Falta configurar variables..."
mv .env.backup .env
```

---

## 📊 MÉTRICAS DE ÉXITO

| Métrica | Antes | Después (Esperado) |
|---------|-------|-------------------|
| Conexiones DB simultáneas | 50-100 | 5-20 |
| Memory usage | ~500MB | ~200MB |
| Response time (p95) | 500ms | 100ms |
| Errores silenciosos/día | 50+ | 0 |
| Logs útiles | 20% | 90% |

---

## 🚨 ROLLBACK PLAN

Si algo falla:

```bash
# Rollback rápido
git stash
git checkout HEAD -- backend/pagos/service.py
git checkout HEAD -- backend/facturas/service.py
git checkout HEAD -- backend/pacientes/database.py

# Reiniciar servidor
docker-compose restart backend
```

---

## ✅ CRITERIOS DE ACEPTACIÓN

Para considerar FASE 1 completa:

1. ✅ 0 importaciones de `psycopg` en los 3 archivos migrados
2. ✅ Todos los tests pasan
3. ✅ Logs muestran solo 1 pool inicializado
4. ✅ No hay `except: pass` en archivos críticos
5. ✅ Variables de entorno validadas en startup
6. ✅ Documentación actualizada

---

**Inicio de Ejecución:** AHORA  
**Tiempo Estimado FASE 1:** 4-6 horas  
**Responsable:** Desarrollador Backend

**¿Listo para comenzar? → Ejecutar migración de `pagos/service.py`**
