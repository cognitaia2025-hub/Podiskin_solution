# 📋 INFORME DE DEPURACIÓN - BACKEND PODOSKIN SOLUTION

**Fecha de Análisis:** 12 de Enero de 2026  
**Analista:** GitHub Copilot (Claude Sonnet 4.5)  
**Alcance:** Backend completo (181 archivos Python, ~22,265 líneas de código)

---

## 🎯 RESUMEN EJECUTIVO

Se identificaron **7 categorías críticas** de problemas que requieren depuración inmediata:

| Categoría | Severidad | Archivos Afectados | Prioridad |
|-----------|-----------|-------------------|-----------|
| **Múltiples Conexiones DB** | 🔴 CRÍTICA | 8 archivos | **P0** |
| **Manejo de Excepciones Silenciosas** | 🔴 CRÍTICA | 15+ archivos | **P0** |
| **Passwords Hardcodeadas** | 🟠 ALTA | 30+ archivos | **P1** |
| **TODOs Sin Implementar** | 🟡 MEDIA | 12 archivos | **P2** |
| **Logging Inadecuado** | 🟡 MEDIA | Todo el backend | **P2** |
| **Dependencias Obsoletas** | 🟡 MEDIA | 5 archivos | **P2** |
| **Código Duplicado** | 🟢 BAJA | Varios módulos | **P3** |

---

## 🔴 PROBLEMAS CRÍTICOS (P0)

### 1. MÚLTIPLES POOLS DE CONEXIONES A BASE DE DATOS

**Problema:** El backend tiene **múltiples implementaciones** de conexión a PostgreSQL coexistiendo simultáneamente, lo que causa:
- Agotamiento de conexiones
- Memory leaks
- Rendimiento degradado
- Complejidad innecesaria

#### 📍 Archivos Afectados:

1. **`backend/db.py`** ✅ (Pool centralizado AsyncPG - CORRECTO)
   - Pool global con AsyncPG
   - Funciones helper: `get_connection()`, `fetch_one()`, `fetch_all()`
   - **ESTE ES EL ESTÁNDAR A SEGUIR**

2. **`backend/pagos/service.py`** ❌ (psycopg3 - INCORRECTO)
   ```python
   # Línea 28-37: Crea conexiones individuales
   def _get_connection(self):
       if self.conn is None or self.conn.closed:
           self.conn = psycopg.connect(...)
   ```
   - **Problema:** Cada instancia de `PagosService` crea su propia conexión
   - **Impacto:** Conexiones no son pooled, no se liberan correctamente

3. **`backend/facturas/service.py`** ❌ (psycopg3 - INCORRECTO)
   ```python
   # Línea 28-38: Mismo patrón que pagos
   def _get_connection(self):
       self.conn = psycopg.connect(...)
   ```

4. **`backend/pacientes/database.py`** ❌ (AsyncPG duplicado)
   ```python
   # Línea 11-43: Crea su propio pool AsyncPG
   class DatabaseConnection:
       async def connect(self):
           self.pool = await asyncpg.create_pool(...)
   ```
   - **Problema:** Pool separado del pool centralizado
   - **Debería usar:** `from db import get_connection`

5. **`backend/agents/sub_agent_operator/utils/database.py`** ❌ (psycopg2)
   ```python
   # Línea 23-39: Pool psycopg2 síncrono
   _pool = psycopg2.pool.SimpleConnectionPool(...)
   ```
   - **Problema:** Usa librería obsoleta (psycopg2)
   - **Problema:** Pool síncrono en aplicación async

6. **`backend/ws_notifications/notifications_ws.py`** ❌
   ```python
   # Línea 25: Conexión individual asyncpg
   'password': os.getenv('DB_PASSWORD', 'podoskin_password_123')
   ```

7. **`backend/tasks/email_service.py`** ❌
   ```python
   # Línea 43: Conexiones individuales
   async def get_db_connection():
       return await asyncpg.connect(**DB_CONFIG)
   ```

8. **`backend/auth/permissions.py`** ❌
   ```python
   # Línea 67: Conexión individual asyncpg
   password=os.getenv("DB_PASSWORD", "podoskin_password_123")
   ```

#### 🎯 Plan de Corrección (P0):

```python
# ❌ PATRÓN INCORRECTO (NO USAR)
import psycopg
conn = psycopg.connect(...)
result = conn.execute("SELECT ...")

# ✅ PATRÓN CORRECTO (USAR EN TODOS LOS MÓDULOS)
from db import get_connection, release_connection

async def mi_funcion():
    conn = await get_connection()
    try:
        result = await conn.fetch("SELECT ...")
        return [dict(row) for row in result]
    finally:
        await release_connection(conn)

# ✅ PATRÓN SIMPLIFICADO (PARA QUERIES SIMPLES)
from db import fetch_one, fetch_all, execute_returning

async def get_patient(patient_id: int):
    return await fetch_one(
        "SELECT * FROM pacientes WHERE id = $1",
        patient_id
    )
```

**Archivos a Migrar (Orden de Prioridad):**
1. ✅ `pagos/service.py` - Usado frecuentemente
2. ✅ `facturas/service.py` - Usado frecuentemente
3. ✅ `pacientes/database.py` - Módulo core
4. ✅ `agents/sub_agent_operator/utils/database.py` - Agente crítico
5. ✅ `ws_notifications/notifications_ws.py` - WebSocket importante
6. ✅ `tasks/email_service.py` - Background tasks
7. ✅ `auth/permissions.py` - Autenticación crítica

---

### 2. MANEJO DE EXCEPCIONES SILENCIOSAS

**Problema:** Múltiples bloques `except:` sin especificar tipo de excepción y usando `pass`, ocultando errores críticos.

#### 📍 Casos Identificados:

**`backend/agents/whatsapp_medico/nodes/rag_manager.py`** (6 instancias):
```python
# Línea 88-89:
except:
    pass  # ❌ PELIGROSO: Oculta cualquier error

# Línea 116-117:
except:
    pass  # ❌ No se registra qué falló

# Línea 139-140:
except:
    pass

# Línea 165-166:
except:
    pass

# Línea 194-195:
except:
    pass
```

**Otros archivos:**
- `catalog/models.py:24` - `pass` sin log
- `tratamientos/models.py:54` - `pass` sin log
- `proveedores/router.py:36` - `pass` sin log

#### 🎯 Plan de Corrección:

```python
# ❌ INCORRECTO
try:
    result = json.loads(data)
    if result['success']:
        return result
except:
    pass  # Silencioso, no sabemos qué falló

# ✅ CORRECTO
import logging
logger = logging.getLogger(__name__)

try:
    result = json.loads(data)
    if result.get('success'):
        return result
except json.JSONDecodeError as e:
    logger.error(f"Error parsing JSON: {e}", exc_info=True)
    return None
except KeyError as e:
    logger.warning(f"Missing key in response: {e}")
    return None
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return None
```

**Archivos a Corregir:**
1. ✅ `agents/whatsapp_medico/nodes/rag_manager.py` (6 casos)
2. ✅ `catalog/models.py`
3. ✅ `tratamientos/models.py`
4. ✅ `proveedores/router.py`

---

## 🟠 PROBLEMAS ALTOS (P1)

### 3. PASSWORDS HARDCODEADAS EN VALORES DEFAULT

**Problema:** 30+ archivos tienen contraseñas hardcodeadas como valores por defecto:

```python
# ❌ INSEGURO
DB_PASSWORD = os.getenv("DB_PASSWORD", "podoskin_password_123")
```

#### 📍 Archivos Afectados (muestra):
- `backend/db.py:24`
- `backend/auth/database.py:23`
- `backend/agents/whatsapp_medico/config.py:22`
- `backend/pacientes/database.py:24`
- `backend/ws_notifications/notifications_ws.py:25`
- `backend/tasks/notifications.py:19`
- `backend/tasks/email_service.py:30`
- Y 23+ archivos más...

#### 🎯 Plan de Corrección:

```python
# ❌ INCORRECTO
DB_PASSWORD = os.getenv("DB_PASSWORD", "podoskin_password_123")

# ✅ CORRECTO - Opción 1: Forzar variable de entorno
DB_PASSWORD = os.getenv("DB_PASSWORD")
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD environment variable is required")

# ✅ CORRECTO - Opción 2: Valor seguro para dev
DB_PASSWORD = os.getenv("DB_PASSWORD", "dev_password_CHANGE_IN_PROD")
if DB_PASSWORD == "dev_password_CHANGE_IN_PROD" and os.getenv("ENV") == "production":
    raise ValueError("Must set DB_PASSWORD in production")
```

**Acción Inmediata:**
1. ✅ Crear archivo `.env.example` con variables requeridas
2. ✅ Actualizar todos los archivos para validar variables críticas
3. ✅ Agregar validación en `main.py` al iniciar

---

### 4. MANEJO DE ERRORES QUE RETORNAN VALORES INCORRECTOS

**Problema:** Funciones que devuelven listas vacías `[]` o `None` cuando hay errores, ocultando problemas:

```python
# Patrón problemático encontrado en 15+ archivos
async def get_products():
    try:
        # ... query database
        return results
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return []  # ❌ Oculta el error al llamador
```

#### 📍 Archivos Afectados:
- `inventory/service.py` (6 funciones)
- `agents/sub_agent_operator/tools/patient_tools.py` (3 funciones)
- `agents/sub_agent_operator/tools/appointment_tools.py` (3 funciones)
- Otros 10+ archivos

#### 🎯 Plan de Corrección:

```python
# ❌ INCORRECTO
async def get_products():
    try:
        return await fetch_all("SELECT * FROM products")
    except Exception as e:
        logger.error(f"Error: {e}")
        return []  # Cliente no sabe que hubo error

# ✅ CORRECTO - Propagar el error
async def get_products():
    try:
        return await fetch_all("SELECT * FROM products")
    except asyncpg.PostgresError as e:
        logger.error(f"Database error fetching products: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching products"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise
```

---

## 🟡 PROBLEMAS MEDIOS (P2)

### 5. TODOs SIN IMPLEMENTAR EN CÓDIGO CRÍTICO

**Problema:** 12+ TODOs en funcionalidades core que están sin implementar:

#### 📍 Casos Críticos:

**`backend/agents/sub_agent_operator/graph.py`** (10 TODOs):
```python
# Líneas 84, 91, 98, 105, 112, 119, 126, 133, 140, 147
def handle_xxx():
    # TODO: Implementar
    pass
```
- **Impacto:** 10 funciones stub sin implementación real

**`backend/agents/orchestrator/graph.py:59`**:
```python
# TODO: Add postgres/redis checkpointer
```
- **Impacto:** No hay persistencia de estado del agente

**`backend/middleware/rate_limit.py:40`**:
```python
# TODO en producción:
# - Implementar rate limiting real
```

#### 🎯 Plan de Corrección:
1. ✅ Catalogar todos los TODOs
2. ✅ Priorizar por criticidad
3. ✅ Implementar o documentar como "futuro enhancement"

---

### 6. LOGGING INADECUADO

**Problema:** Configuración de logging muy restrictiva:

```python
# backend/main.py:87
logging.basicConfig(
    level=logging.WARNING,  # ❌ Solo WARNING y ERROR
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

**Impacto:**
- No se registran eventos INFO importantes
- Dificulta debugging
- No hay trazabilidad de operaciones exitosas

#### 🎯 Plan de Corrección:

```python
# ✅ Logging configurado por ambiente
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if os.getenv("ENV") == "production" else "DEBUG")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("backend.log") if os.getenv("ENV") == "production" else logging.NullHandler()
    ]
)
```

---

### 7. DEPENDENCIAS OBSOLETAS Y CONFLICTOS

**Problema:** `requirements.txt` tiene dependencias con versiones potencialmente problemáticas:

```plaintext
# Línea 25 - torch muy específico
torch==2.9.0  # ⚠️ Versión futura? (actual estable es 2.1.x)

# Línea 47 - websockets con restricción estricta
websockets>=11.0,<12.0  # ⚠️ Por qué restricción?

# Línea 106 - TODO: psycopg2-binary eliminado pero aún comentado
# psycopg2-binary - ELIMINADO: Migrado a AsyncPG puro
```

#### 🎯 Plan de Corrección:
1. ✅ Verificar versión correcta de torch
2. ✅ Documentar razón de restricciones de versión
3. ✅ Eliminar comentarios de dependencias obsoletas
4. ✅ Agregar `requirements-lock.txt` con versiones específicas

---

## 🟢 PROBLEMAS BAJOS (P3)

### 8. CÓDIGO DUPLICADO

**Problema:** Lógica duplicada en múltiples módulos:

- Validación de fechas: 5+ archivos
- Formateo de respuestas JSON: 10+ archivos
- Manejo de paginación: 8+ archivos

#### 🎯 Plan de Corrección:
- Crear `backend/common/utils.py` con funciones compartidas
- Refactorizar módulos para usar utilities comunes

---

## 📋 PLAN DE ACCIÓN PRIORIZADO

### **FASE 1: CRÍTICO - Semana 1** (P0)

#### Día 1-2: Migración de Conexiones DB
- [ ] Migrar `pagos/service.py` a AsyncPG
- [ ] Migrar `facturas/service.py` a AsyncPG
- [ ] Migrar `pacientes/database.py` a pool centralizado
- [ ] Pruebas de carga para validar

#### Día 3-4: Manejo de Excepciones
- [ ] Corregir `rag_manager.py` (6 casos)
- [ ] Corregir otros archivos con `except: pass`
- [ ] Agregar tests unitarios para casos de error

#### Día 5: Validación y Testing
- [ ] Ejecutar suite de tests completa
- [ ] Validar logs de errores
- [ ] Pruebas de integración

### **FASE 2: ALTA - Semana 2** (P1)

#### Día 1-2: Seguridad de Passwords
- [ ] Crear `.env.example`
- [ ] Actualizar validación de variables de entorno
- [ ] Agregar checks en CI/CD

#### Día 3-4: Manejo de Errores Mejorado
- [ ] Refactorizar funciones que retornan `[]` en error
- [ ] Implementar excepciones personalizadas
- [ ] Actualizar documentación de APIs

### **FASE 3: MEDIA - Semana 3** (P2)

#### Día 1-2: TODOs y Logging
- [ ] Implementar o eliminar TODOs críticos
- [ ] Mejorar configuración de logging
- [ ] Agregar métricas de observabilidad

#### Día 3-4: Dependencias
- [ ] Auditar y actualizar `requirements.txt`
- [ ] Crear `requirements-lock.txt`
- [ ] Ejecutar security audit

### **FASE 4: BAJA - Semana 4** (P3)

- [ ] Refactorizar código duplicado
- [ ] Mejorar documentación
- [ ] Optimizaciones de performance

---

## 📊 MÉTRICAS DE CÓDIGO

```
Total de Archivos Python: 181
Total de Líneas de Código: ~22,265
Módulos Principales: 25+
Sub-agentes IA: 3 (Orchestrator, WhatsApp Médico, Operador)

Problemas Identificados:
- 🔴 Críticos (P0): 15 instancias
- 🟠 Altos (P1): 30+ instancias
- 🟡 Medios (P2): 20+ instancias
- 🟢 Bajos (P3): Variable

Deuda Técnica Estimada: ~2-3 semanas de trabajo
```

---

## 🎯 ARCHIVOS PRIORITARIOS PARA DEPURACIÓN

### Top 10 Archivos a Revisar (Orden de Impacto):

1. **`backend/db.py`** - ✅ Pool centralizado (correcto, es el estándar)
2. **`backend/pagos/service.py`** - ❌ Migrar a AsyncPG
3. **`backend/facturas/service.py`** - ❌ Migrar a AsyncPG
4. **`backend/pacientes/database.py`** - ❌ Usar pool centralizado
5. **`backend/agents/whatsapp_medico/nodes/rag_manager.py`** - ❌ Corregir excepciones
6. **`backend/agents/sub_agent_operator/utils/database.py`** - ❌ Eliminar psycopg2
7. **`backend/main.py`** - ⚠️ Mejorar logging y validación startup
8. **`backend/requirements.txt`** - ⚠️ Revisar versiones
9. **`backend/middleware/rate_limit.py`** - ⚠️ Implementar TODOs
10. **`backend/agents/sub_agent_operator/graph.py`** - ⚠️ Implementar handlers

---

## ✅ RECOMENDACIONES ADICIONALES

### 1. Testing
- Agregar tests de integración para conexiones DB
- Implementar health checks en `/health` endpoint
- Agregar monitoring de pool de conexiones

### 2. Observabilidad
```python
# Agregar a main.py
from prometheus_client import Counter, Histogram

db_connections_total = Counter('db_connections_total', 'Total DB connections')
request_duration = Histogram('request_duration_seconds', 'Request duration')
```

### 3. Documentation
- Crear `ARCHITECTURE.md` con flujo de conexiones DB
- Documentar estándares de código en `CONTRIBUTING.md`
- Actualizar README con setup de desarrollo

### 4. CI/CD
```yaml
# .github/workflows/backend-tests.yml
- name: Run Linters
  run: |
    flake8 backend/ --max-line-length=100
    black --check backend/
    
- name: Run Tests
  run: pytest tests/ -v --cov=backend
  
- name: Security Audit
  run: |
    pip install safety
    safety check
```

---

## 🚀 PRÓXIMOS PASOS

1. **Revisión de este informe** con el equipo técnico
2. **Priorizar archivos** según impacto en producción
3. **Crear tickets** en sistema de gestión de proyectos
4. **Asignar recursos** para cada fase
5. **Comenzar FASE 1** inmediatamente

---

**Fin del Informe**  
*Generado automáticamente por análisis estático de código*
