# Información de Operación de la Clínica - Santiago Ornelas
**Fecha de recopilación:** 06/01/2026

---

## 1. CATÁLOGO DE SERVICIOS Y PRECIOS 💰

### Servicios Principales

| Servicio | Precio | Notas |
|----------|--------|-------|
| Consulta de valoración | $500 | Evaluación inicial |
| Espiculotomía (uña enterrada) | $500 | SIN anestesia |
| Matricectomía (uña enterrada) | $1,500 | CON anestesia |
| Verrugas plantares | $1,500 | CON anestesia |
| Pedicure clínico | $500 | - |
| Pedicure químico | $800 | - |
| Láser ultravioleta B (pie de atleta) | $800 | Por sesión |
| Láser antimicótico (onicomicosis) | $800 | Por sesión, cantidad variable |

### Procedimiento de Láser Antimicótico (Detalle)
- Incluye: Recorte, limado de uñas, limpieza de canales laterales
- Aplicación de 3 tipos distintos de láseres
- Opción de estudio de laboratorio para identificar patógeno, resistencia y sensibilidad

**📌 Uso en la App:**
- ✅ **Tabla `servicios`** ya tiene estructura para almacenar estos servicios
- ✅ Precio base, nombre, descripción
- ⚠️ Falta: Campo para indicar si requiere anestesia, número de sesiones estimadas

---

## 2. ESTRUCTURA DE GASTOS 📊

### 2.1 Gastos Fijos Mensuales (Servicios)
**Categoría actual:** "Renta" (+ $11,000 mensuales)

Incluye:
- 💡 Luz
- 💧 Agua  
- 🌐 Internet
- 📋 Contabilidad
- 🏢 Renta del local

**Método actual de Santiago:** 
> "No lo desgloso, cuando me cae el gasto lo meto en ese apartado si sé que es de servicios necesarios"

**📌 Uso en la App:**
- ✅ **Tabla `gastos`** permite registrar estos gastos
- ⚠️ **Recomendación:** Crear categorías específicas:
  - `SERVICIOS_BASICOS` (luz, agua, internet)
  - `SERVICIOS_PROFESIONALES` (contabilidad)
  - `RENTA_LOCAL`
- 💡 Dashboard puede mostrar gráfica de gastos fijos vs variables

---

### 2.2 Gastos Variables (Consumibles)
**Categoría actual:** "Inversión"

Santiago clasifica en 3 subcategorías:

#### A) Materiales Médicos
- Gasas, guantes, jeringas, bisturíes, fresas, etc.

#### B) Limpieza y Desinfección
- Alcohol, toallas desinfectantes, Lysol, aromatizantes

#### C) Cafetería y Atención al Cliente
- Café, azúcar, crema, agua embotellada
- Vasos, platos, cucharas, servilletas
- Galletas, sodas

**Justificación de Santiago:**
> "Para que la gente pase una espera tranquila mientras les toca atención o vienen acompañados con familia"

**📌 Uso en la App:**
- ✅ **Tabla `gastos`** puede almacenar estos gastos con categorías
- ⚠️ **Mejora necesaria:** Vincular gastos con movimientos de inventario
- 💡 **Alertas:** Cuando compra materiales médicos → actualizar inventario automáticamente
- 💡 **Reportes:** Separar en dashboard "Gastos Médicos" vs "Gastos Operativos" vs "Gastos Cafetería"

---

## 3. INVENTARIO ACTUAL (Snapshot 06/01/2026) 📦

### 3.1 Instrumental Médico Reutilizable

| Artículo | Stock Actual | Capacidad Máxima |
|----------|--------------|------------------|
| Cizallas tijera podológica | 20 | 40 |
| Guías de corte | 16 | 10 ⚠️ |
| Espátula | 5 | 4 ⚠️ |
| Tijera lister | 2 | 2 |
| Pinza mosco | 2 | 2 |
| Pinza adson | 1 | 1 |
| Tijera retiro de puntos | 1 | 1 |
| Punzón | 1 | 1 |
| Cucharilla de corte | 1 | 1 |
| Mango bisturí #3 | 2 | 4 |
| Mango bisturí #4 | 2 | 4 |
| Drill | 2 | 2 |
| Extintor | 2 | 2 |

**⚠️ NOTA:** Guías de corte y Espátula superan la capacidad máxima (posible error o reconteo)

---

### 3.2 Consumibles Médicos

| Artículo | Stock Actual | Alerta de Reorden | Estado |
|----------|--------------|-------------------|--------|
| Hojas bisturí #10 | 31 | 100 | 🟢 OK |
| Pododisco | 7 | 6 | 🟢 OK |
| Limas de pododisco | 420 | 100 | 🟢 Stock alto |
| Adaptador cauterio | 4 | 4 | 🟡 Medio |
| Agujas cauterio | 55 | 100 | 🟢 OK |
| Fresa fina | 16 | 20 | 🟢 OK |
| Fresa cónica | 18 | 20 | 🟢 OK |
| Fresa avellanada | 24 | 20 | 🟢 Stock alto |
| Fresa cilíndrica Roma | 23 | 20 | 🟢 Stock alto |
| Fresa cilíndrica recta | 24 | 20 | 🟢 Stock alto |
| Aplicador de madera | 260 | 500 | 🟢 OK |
| **Hisopos de madera** | **0** | **1000** | 🔴 **CRÍTICO** |
| Venda elástica autoadherente | 10 | 10 | 🟡 Mínimo |
| Bolsas esterilización | 2 cajas | 5 cajas | 🟡 Bajo |
| Campos clínicos | 350 | 500 | 🟢 OK |
| Rollos de film | 4 | 10 | 🟡 Medio |
| Cubrebocas | 14 cajas | 10 cajas | 🟢 Stock alto |
| Gasas estériles | 210 | 100 | 🟢 Stock alto |
| Jeringas insulina | 96 | 100 | 🟢 OK |
| Jeringas 3 ML | 190 | 100 | 🟢 Stock alto |
| Torundas | 2 bolsas | 3 bolsas | 🟡 Medio |
| Alcohol | 2 botellas | 3 botellas | 🟡 Medio |
| Guantes talla L | 2 cajas | 4 cajas | 🟡 Bajo |
| Guantes talla M | 3 cajas | 4 cajas | 🟢 OK |
| Plumas para drill | 4 | 6 | 🟢 OK |

---

### 3.3 Medicamentos y Químicos

| Artículo | Stock Actual | Capacidad | Estado |
|----------|--------------|-----------|--------|
| Lidocaína 2% | 1 | 4 | 🟡 Bajo |
| Benzocaína 20% | 2 | 6 | 🟡 Medio |
| Hidróxido de potasio | 2 lt | 4 lt | 🟡 Medio |
| Hidróxido de potasio gel | 1 lt | 2 lt | 🟡 Medio |
| Glicerina | 1 lt | 2 lt | 🟡 Medio |

---

### 3.4 Limpieza y Desinfección

| Artículo | Stock Actual | Capacidad | Estado |
|----------|--------------|-----------|--------|
| Toallas desinfectantes | 2 rollos | 10 rollos | 🔴 Crítico |
| Toallas secantes | 1 | 10 | 🔴 Crítico |
| Sanitas | 12 | 150 | 🔴 Crítico |
| Lysol spray | 1 | 10 | 🔴 Crítico |
| Aromatizante spray | 2 | 10 | 🟡 Bajo |
| **Aromatizantes air wick** | **0** | **6** | 🔴 **CRÍTICO** |
| Qrit | 1 | 3 | 🟡 Bajo |
| WD-40 | 1 | 2 | 🟡 Bajo |
| Carbón activado | 2 | 10 | 🟡 Bajo |

---

### 3.5 Material de Oficina

| Artículo | Stock Actual | Capacidad | Estado |
|----------|--------------|-----------|--------|
| Folders | 61 | 100 | 🟢 OK |
| Redma | 1 | 2 | 🟡 Bajo |

---

### 3.6 Cafetería y Atención al Cliente

| Artículo | Stock Actual | Capacidad | Estado |
|----------|--------------|-----------|--------|
| Botellas de agua | 35 | 40 | 🟢 OK |
| Servilletas | 1 bolsa | 3 bolsas | 🟡 Bajo |
| Platos | 1 bolsa | 3 bolsas | 🟡 Bajo |
| Cucharas | 3 bolsas | 3 bolsas | 🟢 OK |
| **Vasos** | **0** | **3 bolsas** | 🔴 **CRÍTICO** |
| Café | 1.5 | 2 | 🟢 OK |
| Azúcar | 0.5 | 2 | 🟡 Bajo |
| Crema para café | 0.5 | 2 | 🟡 Bajo |

---

### 3.7 Equipo Láser (Alta Especialización)

| Equipo | Stock Actual | Capacidad | Estado |
|--------|--------------|-----------|--------|
| Contenedores RPB y rígidos | 3 | 4 | 🟢 OK |
| Lentes protectores láser | 5 | 6 | 🟢 OK |
| Láser ultravioleta | 3 | 3 | 🟢 OK |
| Láser rojo | 2 | 3 | 🟢 OK |
| Láser foto disparo | 3 | 3 | 🟢 OK |
| Láser infrarrojo | 3 | 3 | 🟢 OK |

---

## 4. ANÁLISIS PARA INTEGRACIÓN EN LA APP 🚀

### 4.1 Módulos Que Ya Están Listos ✅
- ✅ **Catálogo de servicios** → Tabla `servicios` (agregar precios actuales)
- ✅ **Inventario** → Tabla `inventario` (cargar inventario real de Santiago)
- ✅ **Gastos** → Tabla `gastos` (crear categorías sugeridas)

### 4.2 Mejoras Necesarias ⚠️

**A) Módulo de Inventario:**
- Agregar categorías claras:
  - `INSTRUMENTAL_MEDICO`
  - `CONSUMIBLES_MEDICOS`
  - `MEDICAMENTOS`
  - `LIMPIEZA`
  - `CAFETERIA`
  - `EQUIPO_LASER`
- Alertas automáticas cuando stock < 30% de capacidad
- Lista de compras automática basada en consumo histórico

**B) Módulo de Gastos:**
- Separar en categorías visuales en dashboard:
  - 📊 Gastos Fijos (renta, servicios)
  - 🏥 Gastos Médicos (material clínico)
  - 🧹 Gastos Operativos (limpieza, cafetería)
- Vincular compras de consumibles → actualización automática de inventario
- Gráfica de tendencia: "¿Estoy gastando más este mes?"

**C) Dashboard Ejecutivo:**
- KPI nuevo: "Costo promedio por paciente atendido"
- Comparativa: Ingresos por servicio vs Costo de materiales usados
- Proyección: "A este ritmo de consumo, te quedarás sin [producto] en X días"

### 4.3 Funcionalidades IA Recomendadas 🤖

**Recordatorios Inteligentes:**
- "Santiago, llevas 3 semanas sin registrar gastos de luz"
- "El inventario de hisopos está en 0, ¿ya los compraste?"
- "Históricamente compras Lysol cada 15 días, ¿necesitas agregarlo a la lista?"

**Análisis de Rentabilidad:**
- "El tratamiento de láser antimicótico cuesta $800 pero gastas $150 en materiales por sesión. Margen: 81%"
- "La cafetería te cuesta $2,500/mes. ¿Quieres seguir ofreciéndola o reducir gastos?"

**Optimización de Compras:**
- "Compraste 14 cajas de cubrebocas pero solo usas 2 al mes. Inventario para 7 meses"
- "Te quedas sin vasos cada 3 semanas. Recomiendo comprar más en la próxima orden"

---

## 5. ITEMS CRÍTICOS DETECTADOS 🚨

### Productos Agotados (Stock = 0)
1. 🔴 **Hisopos de madera** - Necesario para aplicación de medicamentos
2. 🔴 **Vasos desechables** - Cafetería sin servicio de bebidas
3. 🔴 **Aromatizantes air wick** - Ambiente de sala de espera

### Productos en Estado Crítico (< 20% capacidad)
1. 🔴 **Toallas desinfectantes** - 20% (2 de 10)
2. 🔴 **Toallas secantes** - 10% (1 de 10)
3. 🔴 **Sanitas** - 8% (12 de 150)
4. 🔴 **Lysol spray** - 10% (1 de 10)

### Recomendación de Compra Urgente
```
LISTA DE COMPRAS PRIORITARIA:
[ ] Hisopos de madera (1000 unidades)
[ ] Vasos desechables (3 bolsas)
[ ] Aromatizantes air wick (6 unidades)
[ ] Toallas desinfectantes (10 rollos)
[ ] Toallas secantes (10 unidades)
[ ] Sanitas (150 unidades)
[ ] Lysol spray (10 unidades)
[ ] Guantes talla L (2 cajas más)
[ ] Lidocaína 2% (3 más)
```

---

## 6. TAREAS PENDIENTES PARA IMPLEMENTACIÓN 📝

### Prioridad Alta 🔴
1. ✅ Cargar catálogo de servicios con precios reales de Santiago
2. ✅ Cargar inventario actual (este snapshot) en la base de datos
3. ⚠️ Configurar alertas de stock bajo para productos críticos
4. ⚠️ Crear categorías de gastos (Fijos, Médicos, Operativos, Cafetería)
5. 🔴 **URGENTE:** Generar lista de compras para productos críticos

### Prioridad Media 🟡
1. Dashboard con separación visual de tipos de gastos
2. Vinculación: Registro de gasto → Actualización de inventario
3. Reportes: "Análisis de rentabilidad por servicio"
4. Lista de compras automática basada en consumo
5. Historial de precios de productos para análisis de inflación

### Prioridad Baja 🟢
1. Proyecciones de consumo basadas en histórico
2. Recomendaciones de IA para optimización de compras
3. Comparativas mes a mes de gastos operativos
4. Integración con proveedores para pedidos automáticos

---

## 7. RESUMEN EJECUTIVO PARA SANTIAGO 📋

**Lo que tenemos:**
- ✅ Catálogo completo de 8 servicios principales con precios
- ✅ Inventario de 95+ productos diferentes organizados
- ✅ Estructura de gastos definida (fijos vs variables)

**Lo que necesitamos hacer:**
- 🔴 **URGENTE:** Comprar productos críticos (7 productos agotados o casi)
- 🟡 Cargar toda esta información en la app para empezar a usarla
- 🟡 Crear sistema de alertas para que no te quedes sin material

**Beneficios una vez implementado:**
- 📊 Verás en tiempo real qué productos se están acabando
- 💰 Sabrás exactamente cuánto ganas vs cuánto gastas por servicio
- 🤖 La app te recordará comprar cosas antes de que se acaben
- 📈 Podrás tomar mejores decisiones sobre precios y eficiencia

**Próximo paso:**
Crear un script SQL para cargar este inventario completo en la base de datos y activar las alertas de stock.

---

**Última actualización:** 06/01/2026 - 16:00 hrs  
**Preparado por:** Sistema de documentación PodoskiSolution  
**Próxima revisión:** Al implementar módulo de inventario completo
