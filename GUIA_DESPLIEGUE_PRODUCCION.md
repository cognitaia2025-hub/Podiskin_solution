# 🚀 GUÍA DE DESPLIEGUE A PRODUCCIÓN

## ✅ Correcciones Implementadas

### 1. **Fuga de Conexiones Corregida**

Se han implementado las siguientes correcciones críticas para resolver el error:
```
psycopg.pool - WARNING - rolling back returned connection: <psycopg.AsyncConnection [INTRANS]>
```

#### Cambios en `backend/auth/database.py`:
- ✅ **Pool de conexiones aumentado**: `min_size=5, max_size=20` (antes: 2-10)
- ✅ **Rollback preventivo agregado** en todas las funciones de solo lectura
- ✅ **Manejo robusto de excepciones** con rollback en bloques catch
- ✅ Funciones corregidas:
  - `get_user_by_username()`
  - `is_user_active()`
  - `get_all_users()`
  - `get_user_by_id()`

#### Cambios en `backend/stats/router.py`:
- ✅ **Rollback en excepciones agregado** para todos los endpoints
- ✅ Verificado uso correcto de `async with conn.cursor()`
- ✅ Endpoints corregidos:
  - `/stats/dashboard` - Múltiples consultas SQL
  - `/stats/appointments-trend` - Consulta de tendencias

### 2. **Patrón Correcto de Uso de Conexiones**

**❌ PATRÓN INCORRECTO (Causa fuga):**
```python
conn = await _get_connection()
await conn.execute("SELECT ...")  # ⚠️ Deja transacción abierta
await _return_connection(conn)
```

**✅ PATRÓN CORRECTO (Implementado):**
```python
conn = None
try:
    conn = await _get_connection()
    async with conn.cursor() as cur:
        await cur.execute("SELECT ...")
        result = await cur.fetchall()
    # Cerrar transacción de solo lectura
    await conn.rollback()
    return result
except Exception as e:
    if conn:
        await conn.rollback()
    raise
finally:
    if conn:
        await _return_connection(conn)
```

---

## 📋 PASOS PARA DESPLIEGUE

### Paso 1: Verificar Dependencias

Asegúrate de que estas dependencias estén instaladas:
```bash
cd backend
pip install psycopg[binary]>=3.1.0
pip install psycopg-pool>=3.1.0
```

### Paso 2: Configurar Variables de Entorno

Crea o actualiza el archivo `.env` en `backend/`:
```env
# Database
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=podoskin_db
DB_USER=podoskin_user
DB_PASSWORD=podoskin_password_123

# JWT
JWT_SECRET_KEY=tu-secret-key-en-produccion-CAMBIAR

# Server
PORT=8000
DEBUG=false
ALLOWED_ORIGINS=https://tu-dominio.com
```

### Paso 3: Ejecutar Tests de Conexiones

Antes de desplegar, verifica que el pool funciona correctamente:
```bash
cd backend
python test_connection_pool.py
```

Debes ver:
```
✅ Pool inicializado correctamente
✅ Query 1: N usuarios
✅ Query 2: N usuarios
...
✅ TODAS LAS PRUEBAS PASARON
```

### Paso 4: Limpiar Base de Datos (SOLO SI ES NECESARIO)

⚠️ **ADVERTENCIA**: Este paso eliminará TODOS los datos de prueba.

Si necesitas limpiar la BD manteniendo solo el staff:
```bash
cd backend
python clean_for_production.py
```

Este script:
- ✅ Mantiene los 4 usuarios del staff (dr.santiago.ornelas, adm.santiago.ornelas, ivette.martinez, ibeth.martinez)
- ✅ Mantiene roles y permisos
- ❌ Elimina todos los pacientes de prueba
- ❌ Elimina todas las citas de prueba
- ❌ Elimina todos los expedientes médicos
- ❌ Elimina datos financieros de prueba

### Paso 5: Iniciar Backend

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

O con reload (solo desarrollo):
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Paso 6: Verificar que el Dashboard Funciona

1. Inicia sesión en la aplicación
2. Navega al Dashboard
3. Verifica que:
   - ✅ No aparecen errores 500
   - ✅ Las métricas se cargan correctamente
   - ✅ No hay warnings de "rolling back returned connection" en los logs
   - ✅ Las gráficas se renderizan sin errores

---

## 🔍 Monitoreo Post-Despliegue

### Logs a Vigilar

Busca estos mensajes en los logs del backend:

**✅ Mensajes Buenos:**
```
Auth database pool initialized successfully
```

**❌ Mensajes Malos (Ya NO deberían aparecer):**
```
psycopg.pool - WARNING - rolling back returned connection: <psycopg.AsyncConnection [INTRANS]>
500 Internal Server Error
```

### Comandos de Monitoreo

Si usas `docker-compose`:
```bash
docker-compose logs -f backend | grep -i "warning\|error"
```

Si ejecutas directamente:
```bash
# Ver logs en tiempo real
tail -f backend.log | grep -i "warning\|error"
```

---

## 🐛 Troubleshooting

### Error: "psycopg_pool not installed"

**Solución:**
```bash
pip install psycopg-pool>=3.1.0
```

### Error: "Connection refused"

**Solución:**
1. Verifica que PostgreSQL esté corriendo:
   ```bash
   sudo systemctl status postgresql
   ```
2. Verifica las variables de entorno en `.env`
3. Verifica que el firewall permite la conexión al puerto 5432

### Error: "Pool exhausted"

Si sigues viendo errores de pool agotado después de las correcciones:

1. Aumenta aún más el tamaño del pool en `auth/database.py`:
   ```python
   _pool = AsyncConnectionPool(
       conninfo=CONNINFO, min_size=10, max_size=30, open=False
   )
   ```

2. Verifica que no hay otros endpoints con fugas de conexiones:
   ```bash
   cd backend
   grep -r "_get_connection" --include="*.py" | grep -v "def _get_connection"
   ```

---

## 📊 Métricas de Éxito

Después del despliegue, debes observar:

1. **Reducción de errores 500**: Cerca del 0%
2. **Sin warnings de conexiones**: 0 warnings de "rolling back"
3. **Dashboard estable**: Carga sin errores en múltiples navegadores simultáneos
4. **Tiempo de respuesta**: `/stats/dashboard` responde en < 500ms

---

## 📞 Soporte

Si encuentras problemas después del despliegue:

1. Captura los logs completos del error
2. Ejecuta `test_connection_pool.py` y comparte el resultado
3. Verifica la versión de psycopg: `pip show psycopg psycopg-pool`

---

## ✅ Checklist Final

Antes de marcar como completo:

- [ ] Dependencias instaladas (`psycopg`, `psycopg-pool`)
- [ ] Variables de entorno configuradas
- [ ] Test de pool ejecutado exitosamente
- [ ] Script de limpieza ejecutado (si es necesario)
- [ ] Backend iniciado sin errores
- [ ] Dashboard carga sin errores 500
- [ ] Sin warnings de conexiones en los logs
- [ ] Métricas verificadas en producción

---

🎉 **¡Base de datos lista para producción!**
