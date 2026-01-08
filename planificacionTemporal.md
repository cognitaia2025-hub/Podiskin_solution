## 📋 Plan de Migración a AsyncPG - Por Fases

---

## 🎯 FASE 0: Preparación y Análisis (15 min) ✅

**Objetivo:** Identificar todos los módulos afectados y crear respaldos

**Resultados:**
- Módulos identificados: citas, tratamientos, roles, proveedores, podologos, horarios, cortes_caja, agents
- Branch creado: feature/migrate-to-asyncpg

**Tareas:**
1. Identificar todos los módulos con psycopg2/ThreadedConnectionPool
2. Crear branch de git para la migración
3. Documentar estado actual de tests

**Comandos:**
```bash
# Buscar módulos con psycopg2
grep -r "ThreadedConnectionPool" backend/
grep -r "psycopg2" backend/

# Crear branch
git checkout -b feature/migrate-to-asyncpg

# Ejecutar tests actuales
pytest tests/ -v
```

---

## 🔧 FASE 1: Preparar db.py centralizado (20 min) ✅

**Objetivo:** Asegurar que db.py tenga todas las utilidades necesarias

**Archivo:** db.py

**Resultados:**
- ✅ Funciones helper agregadas: fetch_one, fetch_all, execute, execute_returning
- ✅ Función get_pool() disponible para otros módulos
- ✅ Imports actualizados

**Tareas:**
1. Verificar que `get_pool()` esté disponible para otros módulos
2. Agregar funciones helper comunes:
   - `async def fetch_one(query, *params)` 
   - `async def fetch_all(query, *params)`
   - `async def execute(query, *params)` (para INSERT/UPDATE/DELETE)
   - `async def execute_returning(query, *params)` (con RETURNING)

**Código a agregar:**
```python
# Agregar al final de db.py
async def fetch_one(query: str, *params) -> Optional[Dict[str, Any]]:
    """Ejecuta query y retorna un registro"""
    async with _pool.acquire() as conn:
        row = await conn.fetchrow(query, *params)
        return dict(row) if row else None

async def fetch_all(query: str, *params) -> List[Dict[str, Any]]:
    """Ejecuta query y retorna todos los registros"""
    async with _pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]

async def execute(query: str, *params) -> str:
    """Ejecuta INSERT/UPDATE/DELETE sin retornar datos"""
    async with _pool.acquire() as conn:
        return await conn.execute(query, *params)

async def execute_returning(query: str, *params) -> Optional[Dict[str, Any]]:
    """Ejecuta INSERT/UPDATE/DELETE con RETURNING"""
    async with _pool.acquire() as conn:
        row = await conn.fetchrow(query, *params)
        return dict(row) if row else None
```

---

## 📦 FASE 2: Migrar módulo CITAS (60 min) ✅

**Objetivo:** Convertir database.py a AsyncPG puro

**Resultados:**
- ✅ Creado database.py nuevo con AsyncPG
- ✅ service.py actualizado (eliminado run_in_executor)
- ✅ main.py actualizado (eliminada inicialización dual)
- ✅ Archivo viejo eliminado

**Nota:** Reiniciar backend y probar endpoints de citas

### 2.1 - Crear nueva versión AsyncPG (20 min)

**Archivo:** `backend/citas/database_async.py` (nuevo)

**Contenido:**
```python
"""Database Utilities AsyncPG - Módulo de Citas"""
import logging
from typing import Optional, List, Dict, Any
from db import fetch_one, fetch_all, execute_returning

logger = logging.getLogger(__name__)

# Ya no necesitamos init_db_pool ni close_db_pool
# El pool centralizado ya está inicializado

async def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Ejecuta SELECT que retorna múltiples filas"""
    return await fetch_all(query, *params)

async def execute_query_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """Ejecuta SELECT que retorna una fila"""
    return await fetch_one(query, *params)

async def execute_mutation(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """Ejecuta INSERT/UPDATE/DELETE con RETURNING"""
    return await execute_returning(query, *params)
```

### 2.2 - Actualizar service.py (15 min)

**Archivo:** service.py

**Cambiar:**
```python
# ANTES:
from .database import (
    init_db_pool,
    close_db_pool,
    execute_query,
    execute_query_one,
    execute_mutation,
)

# DESPUÉS:
from .database_async import (
    execute_query,
    execute_query_one,
    execute_mutation,
)
```

### 2.3 - Actualizar main.py (5 min)

**Archivo:** main.py

**Eliminar:** Toda la sección de inicialización de citas pool

```python
# ELIMINAR estas líneas:
    # Inicializar pool de citas (psycopg2)
    try:
        from citas.database import init_db_pool as init_citas_pool
        await init_citas_pool()
        logger.info("✅ Citas database pool initialized (psycopg2)")
    except Exception as e:
        logger.error(f"❌ Failed to initialize citas pool: {e}")

# Y también eliminar en shutdown:
    try:
        from citas.database import close_db_pool as close_citas_pool
        await close_citas_pool()
        logger.info("✅ Citas database pool closed")
    except Exception as e:
        logger.error(f"❌ Error closing citas pool: {e}")
```

### 2.4 - Probar exhaustivamente (20 min)

```bash
# Reiniciar backend
# Probar manualmente todos los endpoints de citas
# Ejecutar tests
pytest tests/test_citas.py -v
```

### 2.5 - Limpiar código viejo (5 min)

```bash
# Si todo funciona:
rm backend/citas/database.py
mv backend/citas/database_async.py backend/citas/database.py
```

---

## 📦 FASE 3: Migrar módulos TRATAMIENTOS, PACIENTES, etc. (45 min) ✅

**Objetivo:** Aplicar el mismo patrón a los demás módulos

**Resultados:**
- ✅ tratamientos/database.py migrado a AsyncPG
- ✅ roles/service.py migrado a AsyncPG
- ✅ proveedores/service.py migrado a AsyncPG
- ✅ podologos/service.py migrado a AsyncPG
- ✅ horarios/service.py migrado a AsyncPG
- ✅ cortes_caja/service.py migrado a AsyncPG
- ⏭️ agents/sub_agent_whatsApp (pendiente - opcional)

**Nota:** Reiniciar backend y probar endpoints

**Para cada módulo:**
1. Identificar si usa psycopg2 (revisar imports)
2. Aplicar el mismo proceso de FASE 2
3. Probar endpoints
4. Commit por módulo

**Módulos a revisar:**
- `tratamientos/`
- `pacientes/`
- `pagos/`
- `facturas/`
- `gastos/`
- `cortes_caja/`
- `medical_records/`
- `horarios/`

---

## 🧪 FASE 4: Testing Completo (30 min)

**Objetivo:** Validar que todo funciona correctamente

**Tareas:**
1. Ejecutar suite completa de tests
   ```bash
   pytest tests/ -v --cov=backend
   ```

2. Probar manualmente flujos críticos:
   - Login
   - Crear cita
   - Crear paciente
   - Crear tratamiento
   - Generar factura
   - Dashboard

3. Verificar logs en consola (no deben haber errores)

4. Probar con carga concurrente (opcional):
   ```bash
   # Usar locust o similar para simular múltiples usuarios
   ```

---

## 📝 FASE 5: Limpieza y Documentación (20 min)

**Objetivo:** Limpiar código legacy y documentar cambios

**Tareas:**
1. Eliminar dependencia de psycopg2:
   ```bash
   # Editar requirements.txt - eliminar psycopg2
   ```

2. Actualizar documentación:
   - Actualizar README con nueva arquitectura
   - Documentar que ahora todo usa AsyncPG
   - Actualizar diagramas si existen

3. Commit final y merge:
   ```bash
   git add .
   git commit -m "feat: migrate all modules to AsyncPG for better performance"
   git checkout main
   git merge feature/migrate-to-asyncpg
   ```

---

## ✅ CHECKLIST FINAL

- [ ] Todos los módulos usan AsyncPG
- [ ] No quedan referencias a psycopg2
- [ ] Todos los tests pasan
- [ ] No hay errores en logs
- [ ] Backend arranca sin warnings
- [ ] Endpoints funcionan correctamente
- [ ] Documentación actualizada
- [ ] Código legacy eliminado

---

## 🚨 Plan de Rollback (Si algo sale mal)

```bash
# Volver al código anterior
git checkout main
git branch -D feature/migrate-to-asyncpg

# O si ya hiciste merge:
git revert HEAD
```

---

## ⏱️ Tiempo Total Estimado: 3 horas

- Fase 0: 15 min
- Fase 1: 20 min
- Fase 2: 60 min
- Fase 3: 45 min
- Fase 4: 30 min
- Fase 5: 20 min
- Buffer: 30 min

---