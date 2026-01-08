# Estado de Migración a AsyncPG - Bifurcación del Plan

## Fecha: 2026-01-08

## Plan Original

**Objetivo:** Eliminar el "Frankenstein" técnico migrando todo el backend a AsyncPG 100% async.

**Fases Planeadas:**

1. ✅ Pool Centralizado
2. ✅ Gastos Async (crítico - bloqueante)
3. ✅ Auth migrado de psycopg3 a AsyncPG
4. ⏸️ Citas (psycopg2 → AsyncPG)
5. ⏸️ Otros módulos (horarios, cortes_caja, tratamientos, roles, podologos, proveedores)
6. ⏸️ Limpieza final

## Dónde Me Quedé

### ✅ Completado (Fases 1-3)

1. **Pool Centralizado** - `backend/db.py`
   - Creado pool único con AsyncPG
   - Eliminada dependencia de `databases` library
   - Actualizado `main.py` para usar pool centralizado

2. **Gastos Migrado a Async** - `backend/gastos/service.py`
   - Eliminado código síncrono bloqueante (psycopg2)
   - Migrado a AsyncPG con pool centralizado
   - Actualizado router con `await`

3. **Auth Migrado** - `backend/auth/database.py`
   - Migrado de psycopg3 a AsyncPG
   - Usa pool centralizado
   - Todas las funciones async

### ❌ Bloqueo Encontrado

**Problema:** Al intentar iniciar el backend, descubrí que múltiples módulos dependen de funciones que eliminé de `auth/database.py`:

```python
# Módulos bloqueados:
- backend/inventory/service.py (355 líneas) - usa _get_connection, _return_connection
- backend/stats/router.py - usa _get_connection, _return_connection
- Posiblemente más módulos por descubrir
```

**Error:**

```
ImportError: cannot import name '_get_connection' from 'auth.database'
```

## Decisión: Bifurcación del Plan

### Por qué bifurqué

1. **Backend no funcional** - No puedo verificar que las 3 fases completadas funcionan
2. **Más dependencias de lo esperado** - Hay más módulos acoplados a `auth/database.py`
3. **Riesgo de producción** - Migración completa sin verificación es arriesgada
4. **Solicitud del usuario** - Quiere lo "correcto" para producción, no lo "fácil"

### Nuevo Enfoque: Migración Gradual con Wrappers

**Estrategia:**

1. Crear wrappers temporales en `auth/database.py` que llamen al pool centralizado
2. Backend funciona inmediatamente
3. Verificar que fases 1-3 funcionan correctamente
4. Migrar módulos restantes uno por uno
5. Eliminar wrappers cuando todos estén migrados

**Ventajas:**

- ✅ Backend funcional para verificación
- ✅ Migración segura y gradual
- ✅ Fácil rollback si hay problemas
- ✅ Descubrir problemas uno a la vez
- ✅ Apropiado para producción

## Archivos Modificados Hasta Ahora

### Completados

- ✅ `backend/db.py` - Pool centralizado AsyncPG
- ✅ `backend/main.py` - Usa pool centralizado
- ✅ `backend/gastos/service.py` - Migrado a AsyncPG
- ✅ `backend/gastos/router.py` - Agregado await
- ✅ `backend/auth/database.py` - Migrado a AsyncPG
- ✅ `backend/auth/__init__.py` - Eliminados exports obsoletos

### Pendientes de Migración

- ⏸️ `backend/inventory/service.py` - Usa psycopg3
- ⏸️ `backend/stats/router.py` - Usa funciones obsoletas
- ⏸️ `backend/citas/database.py` - Usa psycopg2
- ⏸️ Otros módulos por identificar

## Próximos Pasos

1. **Agregar wrappers temporales** en `auth/database.py`
2. **Verificar backend** inicia correctamente
3. **Probar login** y gastos funcionan
4. **Migrar módulos** uno por uno:
   - inventory/service.py
   - stats/router.py
   - citas/database.py
   - Otros según se descubran
5. **Eliminar wrappers** cuando todos estén migrados

## Notas Importantes

> [!IMPORTANT]
> Los wrappers son TEMPORALES. No son la solución final, solo un puente para migración gradual.

> [!WARNING]
> NO desplegar a producción hasta eliminar todos los wrappers y completar la migración.

> [!NOTE]
> Este enfoque es estándar en la industria para migraciones grandes. Es lo "correcto", no lo "fácil".
