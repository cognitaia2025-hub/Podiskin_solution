# 📘 Instrucciones de Ejecución - Scripts de Datos Mock

Este documento explica cómo cargar y limpiar los datos de prueba (mock data) en tu base de datos PostgreSQL local.

---

## 📁 Archivos Incluidos

```
data/seed/
├── 01_usuarios_config.sql          # Usuarios, roles, servicios, horarios
├── 02_pacientes.sql                # 200 pacientes con datos completos
├── 03_citas_tratamientos.sql       # 363 citas (Nov 2024 - Ene 2025)
├── 04_pagos_inventario.sql         # Pagos, inventario, gastos
├── load_all.sql                    # ⭐ Script maestro (carga todo)
├── clean_mock_data.sql             # 🧹 Limpia datos falsos
└── INSTRUCCIONES_EJECUCION.md      # Este archivo
```

---

## 🚀 PASO 1: Preparar el Entorno

### Prerequisitos

1. **PostgreSQL 16** instalado y corriendo
2. **Base de datos creada** con el nombre `podoskin`
3. **Tablas creadas** (ejecutar scripts de esquema primero)

### Verificar conexión

```bash
psql -U postgres -d podoskin -c "SELECT version();"
```

Si la conexión falla, ajusta:
- Usuario: `-U postgres` (o tu usuario)
- Base de datos: `-d podoskin` (o tu nombre de BD)

---

## 📥 PASO 2: Cargar Datos Mock

### Opción A: Script Maestro (Recomendado)

Ejecuta **UN SOLO COMANDO** para cargar los 4 archivos en orden:

```bash
cd data/seed/
psql -U postgres -d podoskin -f load_all.sql
```

### Opción B: Cargar Archivos Individualmente

Si prefieres control manual:

```bash
cd data/seed/

# 1. Usuarios y configuración
psql -U postgres -d podoskin -f 01_usuarios_config.sql

# 2. Pacientes
psql -U postgres -d podoskin -f 02_pacientes.sql

# 3. Citas y tratamientos
psql -U postgres -d podoskin -f 03_citas_tratamientos.sql

# 4. Pagos e inventario
psql -U postgres -d podoskin -f 04_pagos_inventario.sql
```

---

## ✅ PASO 3: Verificar Carga

### Ver resumen de datos cargados

```sql
psql -U postgres -d podoskin

SELECT 'Usuarios' as tabla, COUNT(*) as registros FROM usuarios
UNION ALL
SELECT 'Pacientes', COUNT(*) FROM pacientes
UNION ALL
SELECT 'Citas', COUNT(*) FROM citas
UNION ALL
SELECT 'Pagos', COUNT(*) FROM pagos
UNION ALL
SELECT 'Productos', COUNT(*) FROM inventario_productos;
```

### Resultado esperado:

```
    tabla     | registros
--------------+-----------
 Usuarios     |         4
 Pacientes    |       200
 Citas        |       363
 Pagos        |       334
 Productos    |        40
```

---

## 🧪 PASO 4: Probar el Sistema

Con los datos mock cargados, puedes:

✅ **Probar el frontend** con pacientes reales  
✅ **Validar el calendario** con 363 citas  
✅ **Ver métricas financieras** (~$217K ingresos)  
✅ **Probar búsquedas** y filtros  
✅ **Ejecutar tests E2E** con datos realistas  

---

## 🧹 PASO 5: Limpiar Datos Mock (Producción)

Cuando termines las pruebas y quieras **dejar solo usuarios reales**:

### ⚠️ ADVERTENCIA: Esta operación NO se puede deshacer

```bash
cd data/seed/
psql -U postgres -d podoskin -f clean_mock_data.sql
```

### ¿Qué se conserva?

✅ **Santiago de Jesús Ornelas Reynoso**  
   - Email: `enfsantiagoornelas@gmail.com`  
   - Usuario: `santiago.ornelas`  
   - Rol: Admin + Podólogo  

✅ **Joana Ibeth Meraz Arregin**  
   - Email: `joana.meraz@podoskin.com`  
   - Usuario: `joana.meraz`  
   - Rol: Podólogo + Recepcionista  

✅ **Horarios de trabajo** de ambos usuarios  
✅ **Tipos de servicio** (7 servicios podológicos)  
✅ **Roles y permisos**  

### ¿Qué se elimina?

❌ **200 pacientes** mock  
❌ **363 citas** mock  
❌ **334 pagos** mock  
❌ **40 productos** de inventario mock  
❌ **Gastos y cortes de caja** mock  
❌ **Usuarios adicionales** de prueba  

---

## 🔄 PASO 6: Recargar Datos Mock

Si necesitas volver a cargar los datos:

```bash
# 1. Limpiar datos actuales
psql -U postgres -d podoskin -f clean_mock_data.sql

# 2. Recargar datos mock
psql -U postgres -d podoskin -f load_all.sql
```

---

## 🛠️ Troubleshooting

### Error: "relation does not exist"

**Problema:** Las tablas no están creadas.

**Solución:**
```bash
# Ejecutar primero los scripts de creación de tablas
psql -U postgres -d podoskin -f data/schema/01_create_tables.sql
```

---

### Error: "duplicate key value violates unique constraint"

**Problema:** Intentas cargar datos cuando ya existen.

**Solución:**
```bash
# Opción 1: Limpiar y recargar
psql -U postgres -d podoskin -f clean_mock_data.sql
psql -U postgres -d podoskin -f load_all.sql

# Opción 2: Borrar base de datos y recrear
dropdb podoskin
createdb podoskin
# Luego ejecutar scripts de esquema y load_all.sql
```

---

### Error: "could not open file"

**Problema:** No estás en el directorio correcto.

**Solución:**
```bash
# Asegúrate de estar en data/seed/
cd /ruta/completa/al/proyecto/Podiskin_solution/data/seed/
psql -U postgres -d podoskin -f load_all.sql
```

---

## 📊 Datos de Prueba Incluidos

### Usuarios (4)
- Santiago Ornelas (Admin + Podólogo)
- Joana Meraz (Podólogo + Recepcionista)
- María López (Recepcionista)
- Admin Sistema (Admin)

### Pacientes (200)
- **Mexicali:** 140 pacientes (70%)
  - Colonias reales: Campestre, Cachanilla, etc.
  - Teléfonos: 686-XXX-XXXX
  - CURPs válidos
  
- **Calexico:** 60 pacientes (30%)
  - Zonas: Downtown, East/West Calexico
  - Teléfonos: (760) 357-XXXX
  - Sin CURP

### Citas (363)
- **Período:** Nov 2024 - Ene 2025
- **Distribución:**
  - Santiago: 200 citas (55%)
  - Joana: 163 citas (45%)
- **Estados:**
  - Completadas: 308 (85%)
  - Canceladas: 18 (5%)
  - No Asistió: 7 (2%)
  - Pendientes: 30 (8%)

### Servicios Podológicos (7)
1. Consulta General - $600 MXN
2. Onicomicosis - $750 MXN
3. Uñas Enterradas - $550 MXN
4. Pedicure Clínico - $800 MXN
5. Callosidades - $500 MXN
6. Verrugas Plantares - $900 MXN
7. Pie de Atleta - $600 MXN

### Datos Financieros
- **Ingresos totales:** $217,948 MXN
- **Gastos totales:** $86,500 MXN
- **Utilidad neta:** $131,448 MXN (60.3%)

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs de PostgreSQL
2. Verifica que las tablas existan
3. Confirma versión de PostgreSQL (16+)
4. Revisa permisos de usuario

---

## ✅ Checklist de Ejecución

- [ ] PostgreSQL 16 instalado
- [ ] Base de datos `podoskin` creada
- [ ] Tablas creadas (esquema)
- [ ] Usuario con permisos adecuados
- [ ] Ejecutado `load_all.sql` exitosamente
- [ ] Verificado conteo de registros
- [ ] Sistema funcionando con datos mock
- [ ] (Opcional) Ejecutado `clean_mock_data.sql` antes de producción

---

**Última actualización:** 2026-01-01  
**Versión:** 1.0  
**Autor:** Sistema de Agentes de Desarrollo