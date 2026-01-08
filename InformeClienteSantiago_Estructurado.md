# Análisis de Lógica y Funcionalidades - Clínica Podoskin
**Fecha de análisis:** 06/01/2026  
**Objetivo:** Identificar mejoras de lógica de programación necesarias basadas en operación real del cliente

---

## 1. CATÁLOGO DE SERVICIOS Y PRECIOS 💰

### Servicios a Cargar (Cortesía de Implementación)

| Servicio | Precio | Requiere Anestesia | Sesiones | Categoría |
|----------|--------|-------------------|----------|-----------|
| Consulta de valoración | $500 | No | 1 | Consulta |
| Espiculotomía (uña enterrada) | $500 | No | 1 | Procedimiento |
| Matricectomía (uña enterrada) | $1,500 | Sí | 1 | Cirugía menor |
| Verrugas plantares | $1,500 | Sí | 1 | Cirugía menor |
| Pedicure clínico | $500 | No | 1 | Estético |
| Pedicure químico | $800 | No | 1 | Estético |
| Láser UV-B (pie de atleta) | $800 | No | Variable | Láser |
| Láser antimicótico (onicomicosis) | $800 | No | Variable | Láser |

**📌 Mejoras de Lógica Necesarias en la App:**

❌ **Falta actualmente:**
- Campo `requiere_anestesia` (BOOLEAN) en tabla `servicios`
- Campo `numero_sesiones_estimadas` (INTEGER o VARCHAR "variable")
- Campo `categoria_servicio` (ENUM: Consulta, Procedimiento, Cirugía, Estético, Láser)
- Lógica para servicios multi-sesión (trackear cuántas sesiones lleva el paciente)

✅ **Lo que haremos:**
- Agregar estos campos a la tabla `servicios` (migración SQL)
- Cargar estos 8 servicios como cortesía
- Cliente solo tendrá que actualizar precios si cambian

---

## 2. ESTRUCTURA DE GASTOS - CATEGORIZACIÓN 📊

### 2.1 Categorías de Gastos Identificadas

Cliente actualmente agrupa gastos en 2 categorías genéricas:
1. **"Renta"** → Incluye: luz, agua, internet, contabilidad, renta (~$11,000/mes)
2. **"Inversión"** → Incluye: todo lo demás (materiales, limpieza, cafetería)

**📌 Mejoras de Lógica Necesarias:**

❌ **Problema actual:**
- No hay categorización clara en tabla `gastos`
- Dashboard no puede separar gastos fijos vs variables
- Imposible hacer análisis de rentabilidad por categoría

✅ **Solución propuesta:**

Agregar campo `categoria_gasto` (ENUM) en tabla `gastos`:
```sql
CREATE TYPE categoria_gasto_enum AS ENUM (
    'SERVICIOS_BASICOS',      -- Luz, agua, internet
    'SERVICIOS_PROFESIONALES', -- Contabilidad, asesoría
    'RENTA_LOCAL',             -- Renta del consultorio
    'MATERIAL_MEDICO',         -- Gasas, guantes, jeringas
    'MEDICAMENTOS',            -- Lidocaína, benzocaína
    'LIMPIEZA',                -- Lysol, toallas, sanitas
    'CAFETERIA',               -- Café, vasos, servilletas
    'MANTENIMIENTO',           -- Reparaciones, WD-40
    'OTROS'
);
```

**Beneficio:**
- Dashboard puede mostrar gráficas separadas por categoría
- Alertas: "Gastos de cafetería aumentaron 30% este mes"
- Análisis: "Material médico representa 35% de gastos variables"

---

## 3. INVENTARIO - UNIDADES DE MEDIDA VARIABLES 📦

### 3.1 Problema Detectado: Unidades de Medida Inconsistentes

**Ejemplos reales del cliente:**
- Alcohol → **2 botellas** (pero podría ser litros)
- Hidróxido de potasio → **2 lt**
- Gasas estériles → **210 piezas**
- Cubrebocas → **14 cajas**
- Café → **1.5 kg** (asumiendo)
- Guantes → **2 cajas** (pero cada caja tiene X pares)

**📌 Estructura Actual de Tabla `inventario`:**

```sql
-- Revisar estructura actual
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'inventario';
```

❌ **Problema:**
- Probablemente solo tiene campo `cantidad` (número)
- No hay campo para unidad de medida
- No diferencia entre "2 litros" vs "2 cajas"

✅ **Solución propuesta:**

**Agregar campos:**
```sql
ALTER TABLE inventario 
ADD COLUMN unidad_medida VARCHAR(20) CHECK (unidad_medida IN (
    'PZA',      -- Piezas (gasas, jeringas, hojas bisturí)
    'CAJA',     -- Cajas (guantes, cubrebocas)
    'LITRO',    -- Litros (alcohol, químicos)
    'KG',       -- Kilogramos (café, azúcar)
    'BOTELLA',  -- Botellas (cuando no se mide en litros)
    'ROLLO',    -- Rollos (film, toallas)
    'BOLSA',    -- Bolsas (servilletas, vasos)
    'UNIDAD'    -- Unidad (drill, extintor)
)),
ADD COLUMN cantidad_por_unidad INTEGER DEFAULT 1;
-- Para cuando una caja tiene X piezas
```

**Ejemplo de registro:**
```sql
INSERT INTO inventario (nombre, cantidad, unidad_medida, cantidad_por_unidad)
VALUES 
    ('Alcohol', 3, 'LITRO', 1),
    ('Guantes talla M', 3, 'CAJA', 100),  -- 3 cajas de 100 pares
    ('Gasas estériles', 210, 'PZA', 1),
    ('Café', 1.5, 'KG', 1);
```

**Beneficio:**
- Cliente puede registrar: "Alcohol - 3 - Litros"
- App calcula: "Si tienes 3 cajas de guantes con 100 pares c/u = 300 pares disponibles"
- Alertas más precisas: "Te quedan 0.5 litros de alcohol (17% del stock)"

---

## 4. PRODUCTOS/MATERIALES - CATEGORIZACIÓN 🏷️

### 4.1 Categorías Identificadas de Inventario

Del análisis de operación real, se identifican 7 categorías:

| Categoría | Ejemplo de Productos | Unidad Típica |
|-----------|---------------------|---------------|
| INSTRUMENTAL_MEDICO | Tijeras, pinzas, mangos bisturí | UNIDAD |
| CONSUMIBLES_MEDICOS | Gasas, jeringas, hojas bisturí | PZA |
| MEDICAMENTOS | Lidocaína, benzocaína | LITRO/PZA |
| LIMPIEZA | Lysol, toallas, sanitas | ROLLO/BOTELLA |
| CAFETERIA | Café, vasos, servilletas | KG/BOLSA |
| EQUIPO_LASER | Láseres, lentes protectores | UNIDAD |
| OFICINA | Folders, plumas | PZA |

**📌 Mejora de Lógica:**

✅ **Agregar campo `categoria_producto` en tabla `inventario`:**
```sql
CREATE TYPE categoria_producto_enum AS ENUM (
    'INSTRUMENTAL_MEDICO',
    'CONSUMIBLES_MEDICOS',
    'MEDICAMENTOS',
    'LIMPIEZA',
    'CAFETERIA',
    'EQUIPO_LASER',
    'OFICINA'
);

ALTER TABLE inventario ADD COLUMN categoria categoria_producto_enum;
```

**Beneficio:**
- Reportes separados: "Gasto mensual en material médico vs cafetería"
- Filtros en frontend: "Mostrar solo productos de limpieza"
- Dashboard: Gráfica de distribución de inventario por categoría

---

## 5. VINCULACIÓN GASTOS ↔ INVENTARIO 🔗

### 5.1 Problema: Gastos e Inventario Desconectados

**Situación actual del cliente:**
> "Cuando compro materiales lo pongo en gastos como inversión"

**📌 Problema de lógica:**
- Cliente registra gasto: "$2,500 en materiales médicos"
- **NO actualiza inventario** manualmente
- Inventario se desactualiza
- No hay trazabilidad de compra → entrada de stock

❌ **Flujo actual (desconectado):**
```
Compra materiales → Registra gasto → [FIN]
                     (inventario NO se actualiza)
```

✅ **Flujo propuesto (conectado):**
```
Compra materiales → Registra gasto → Opción: "¿Actualizar inventario?"
                                     → Agregar productos + cantidades
                                     → Inventario se actualiza automático
                                     → Gasto queda vinculado a productos
```

**Implementación:**

1. **Tabla de vinculación:**
```sql
CREATE TABLE gastos_inventario (
    id SERIAL PRIMARY KEY,
    gasto_id INTEGER REFERENCES gastos(id),
    producto_id INTEGER REFERENCES inventario(id),
    cantidad_comprada DECIMAL(10,2),
    precio_unitario DECIMAL(10,2),
    fecha_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

2. **Endpoint backend:**
```python
POST /api/gastos/con-inventario
{
    "concepto": "Compra materiales médicos",
    "monto": 2500,
    "categoria": "MATERIAL_MEDICO",
    "productos": [
        {"id": 15, "cantidad": 100, "precio_unitario": 5},   # Gasas
        {"id": 23, "cantidad": 200, "precio_unitario": 10}   # Jeringas
    ]
}
```

3. **Lógica automática:**
- Crea registro en `gastos`
- Actualiza `inventario.cantidad` sumando lo comprado
- Crea registros en `gastos_inventario` para trazabilidad
- Dashboard muestra: "Este gasto agregó 100 gasas y 200 jeringas al inventario"

**Beneficio:**
- Inventario siempre actualizado
- Histórico de precios de compra
- Análisis: "¿Está subiendo el precio de las gasas?"

---

## 6. DASHBOARD - MÉTRICAS FINANCIERAS 📊

### 6.1 KPIs Necesarios Según Operación Real

**Métricas que el cliente necesita ver:**

| KPI | Descripción | Fuente de Datos |
|-----|-------------|-----------------|
| Gastos Fijos/mes | Suma de renta + servicios | `gastos` categoría fija |
| Gastos Variables/mes | Suma de materiales + limpieza | `gastos` categoría variable |
| Costo por paciente | Gasto total / pacientes atendidos | `gastos` / `citas` |
| Margen por servicio | Precio - costo materiales | `servicios` - `gastos_inventario` |
| Productos por acabarse | Stock < 30% capacidad | `inventario` |
| Servicios más rentables | Top 5 con mejor margen | Cálculo precio-costo |

**📌 Endpoint backend necesario:**
```python
GET /api/stats/metricas-financieras
Response:
{
    "gastos_fijos_mes": 11000,
    "gastos_variables_mes": 15000,
    "total_pacientes_mes": 80,
    "costo_promedio_paciente": 325,
    "servicios_rentables": [
        {"servicio": "Láser antimicótico", "margen": 85},
        {"servicio": "Pedicure clínico", "margen": 78}
    ],
    "productos_criticos": [...]
}
```

---

## 7. DATOS A CARGAR COMO CORTESÍA 🎁

### 7.1 Lo que NOSOTROS cargaremos:

✅ **Servicios (8 servicios con precios)**
- Script SQL listo con los 8 servicios y precios
- Campos completos: precio, anestesia, sesiones, categoría

✅ **Catálogo de Productos (tipos solamente)**
- ~95 tipos de productos identificados
- Con categoría y unidad de medida sugerida
- **SIN cantidades** (cliente las agregará)

✅ **Categorías predefinidas**
- Categorías de gastos (9 tipos)
- Categorías de productos (7 tipos)
- Unidades de medida (8 opciones)

✅ **Horarios sugeridos**
- Si el cliente mencionó horarios de operación, los cargamos

### 7.2 Lo que el CLIENTE hará:

📝 **Stock inicial**
- Contar sus productos y registrar cantidades

📝 **Actualización de precios**
- Si suben precios de servicios, los modifica

📝 **Gastos diarios**
- Registrar gastos conforme ocurran

---

## 8. RESUMEN DE MEJORAS DE LÓGICA NECESARIAS 🚀

### Prioridad ALTA (Bloquean funcionalidad)

1. ✅ **Agregar unidades de medida a inventario**
   - Campo `unidad_medida` (ENUM)
   - Campo `cantidad_por_unidad` (para cajas, bolsas)

2. ✅ **Categorización de gastos**
   - Campo `categoria_gasto` (ENUM con 9 categorías)
   - Dashboard con gráficas separadas

3. ✅ **Vinculación gastos ↔ inventario**
   - Tabla `gastos_inventario`
   - Endpoint `/api/gastos/con-inventario`
   - Actualización automática de stock

### Prioridad MEDIA (Mejoran experiencia)

4. ⚠️ **Categorización de productos**
   - Campo `categoria_producto` en inventario
   - Filtros en frontend

5. ⚠️ **Servicios multi-sesión**
   - Campos adicionales en tabla `servicios`
   - Lógica para trackear sesiones completadas

6. ⚠️ **Dashboard financiero**
   - Endpoint `/api/stats/metricas-financieras`
   - Componente frontend con KPIs

### Prioridad BAJA (Nice to have)

7. 🟢 **Histórico de precios**
   - Tabla `productos_precios_historico`
   - Análisis de inflación

8. 🟢 **Proyecciones de consumo**
   - IA para predecir cuándo comprar

---

## 9. SCRIPTS SQL A CREAR 📝

### 9.1 Migración de Base de Datos

```sql
-- 1. Agregar campos a servicios
ALTER TABLE servicios 
ADD COLUMN requiere_anestesia BOOLEAN DEFAULT FALSE,
ADD COLUMN sesiones_estimadas VARCHAR(20) DEFAULT '1',
ADD COLUMN categoria_servicio VARCHAR(50);

-- 2. Crear ENUM de categorías de gastos
CREATE TYPE categoria_gasto_enum AS ENUM (...);
ALTER TABLE gastos ADD COLUMN categoria categoria_gasto_enum;

-- 3. Agregar unidades de medida a inventario
ALTER TABLE inventario
ADD COLUMN unidad_medida VARCHAR(20),
ADD COLUMN cantidad_por_unidad INTEGER DEFAULT 1,
ADD COLUMN categoria categoria_producto_enum;

-- 4. Crear tabla de vinculación
CREATE TABLE gastos_inventario (...);

-- 5. Cargar servicios del cliente
INSERT INTO servicios VALUES (...); -- 8 servicios

-- 6. Cargar catálogo de productos (solo tipos)
INSERT INTO inventario (nombre, categoria, unidad_medida) 
VALUES (...); -- ~95 productos
```

---

## 10. PLAN DE IMPLEMENTACIÓN ⚡

### Fase 1: Mejoras de Base de Datos (2-3 horas)
- Crear migraciones SQL
- Agregar campos faltantes
- Crear ENUMs y tablas nuevas

### Fase 2: Backend - Nuevos Endpoints (3-4 horas)
- `POST /api/gastos/con-inventario`
- `GET /api/stats/metricas-financieras`
- Actualizar endpoints existentes con nuevos campos

### Fase 3: Frontend - Componentes Nuevos (4-5 horas)
- Selector de unidad de medida en formulario inventario
- Selector de categoría en formulario gastos
- Dashboard con gráficas de gastos por categoría
- Vista de "Métricas Financieras"

### Fase 4: Carga de Datos Cortesía (1 hora)
- Ejecutar scripts SQL con servicios
- Cargar catálogo de productos (tipos)
- Verificar que todo funcione

**Total estimado: 10-13 horas de desarrollo**

---

**Última actualización:** 06/01/2026 - 16:30 hrs  
**Siguiente paso:** Crear scripts SQL de migración y carga inicial
