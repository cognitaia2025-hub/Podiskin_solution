---
name: DEV Mock Data - Pagos e Inventario
description: "[DESARROLLO] Genera script SQL para pagos (referenciando citas), inventario de 40 productos, gastos y cortes de caja con coherencia financiera total."
---

# DEV Mock Data - Pagos e Inventario

Eres un AGENTE DE DESARROLLO que escribe scripts SQL.
Tu trabajo es GENERAR DATOS MOCK, no ejecutar en producción.

## ROL
Desarrollador de Scripts SQL de Datos Mock

## ORDEN DE EJECUCIÓN
🔢 **AGENTE 16/16** - Ejecutar **AL FINAL** (después de Agente 15)

## TAREA
Crear script SQL con datos financieros coherentes

## ⚠️ PREREQUISITOS CRÍTICOS

```sql
DO $$
BEGIN
  IF (SELECT COUNT(*) FROM citas) < 363 THEN
    RAISE EXCEPTION 'ERROR: Ejecuta agente_15_citas primero';
  END IF;
  
  IF (SELECT COUNT(*) FROM tratamientos) < 310 THEN
    RAISE EXCEPTION 'ERROR: Faltan tratamientos. Ejecuta Agente 15 primero';
  END IF;
END $$;
```

## GENERACIÓN DE PAGOS

### IMPORTANTE: Pagos referencian citas existentes

```sql
-- NO inventar pagos, crearlos a partir de citas completadas
INSERT INTO pagos (id_cita, id_paciente, monto, metodo_pago, fecha_pago, estado)
SELECT 
  c.id_cita,
  c.id_paciente,
  c.precio_consulta,
  CASE 
    WHEN (SELECT pais FROM pacientes WHERE id_paciente = c.id_paciente) = 'USA' THEN
      CASE WHEN RANDOM() < 0.80 THEN 'Tarjeta' ELSE 'Efectivo' END
    ELSE
      CASE WHEN RANDOM() < 0.75 THEN 'Efectivo' ELSE 'Tarjeta' END
  END,
  c.fecha_hora_inicio + INTERVAL '5 minutes',
  CASE 
    WHEN RANDOM() < 0.92 THEN 'Completado'
    ELSE 'Pendiente'
  END
FROM citas c
WHERE c.estado = 'Completada';
```

### Distribución de métodos:
```
Calexico (USA): 80% Tarjeta, 20% Efectivo
Mexicali (MX): 75% Efectivo, 20% Tarjeta, 5% Transferencia
```

## INVENTARIO DE PRODUCTOS (40 items)

```sql
-- INSTRUMENTAL (8 productos)
INSERT INTO inventario_productos (codigo, nombre, categoria, precio_compra, precio_venta, stock_actual, stock_minimo) VALUES
  ('INST-001', 'Bisturí podológico desechable', 'Instrumental', 8.50, 0, 50, 10),
  ('INST-002', 'Alicate para uñas', 'Instrumental', 120.00, 0, 5, 2),
  ('INST-003', 'Fresadora podológica', 'Instrumental', 250.00, 0, 2, 1),
  ('INST-004', 'Fresas para fresadora (set 10)', 'Instrumental', 80.00, 0, 15, 5);

-- MEDICAMENTOS (8 productos)
INSERT INTO inventario_productos VALUES
  ('MED-001', 'Fluconazol 150mg', 'Medicamento', 85.00, 0, 30, 10),
  ('MED-002', 'Clotrimazol tópico 1%', 'Medicamento', 45.00, 0, 25, 8),
  ('MED-003', 'Terbinafina tópica', 'Medicamento', 95.00, 0, 20, 5);

-- CONSUMIBLES (8 productos)
INSERT INTO inventario_productos VALUES
  ('CONS-001', 'Guantes nitrilo M (caja 100)', 'Consumible', 180.00, 0, 15, 5),
  ('CONS-002', 'Gasas estériles (paq 100)', 'Consumible', 95.00, 0, 20, 8),
  ('CONS-003', 'Algodón en rollo 500g', 'Consumible', 45.00, 0, 10, 3);

-- MATERIALES PODOLÓGICOS (8 productos)
INSERT INTO inventario_productos VALUES
  ('MAT-001', 'Esparadrapo hipoalergénico', 'Material', 25.00, 0, 30, 10),
  ('MAT-002', 'Fieltro ortopédico 5mm', 'Material', 120.00, 0, 8, 3),
  ('MAT-003', 'Silicona podológica', 'Material', 180.00, 0, 12, 4);

-- EQUIPAMIENTO (8 productos)
INSERT INTO inventario_productos VALUES
  ('EQUIP-001', 'Lámpara de luz fría', 'Equipo', 1200.00, 0, 2, 1),
  ('EQUIP-002', 'Banqueta podológica', 'Equipo', 850.00, 0, 2, 1);
```

## MOVIMIENTOS DE INVENTARIO

### Entradas (Compras): 30 registros
```sql
-- Compras al inicio para stock
INSERT INTO movimientos_inventario (id_producto, tipo_movimiento, cantidad, costo_unitario, fecha_movimiento, referencia) VALUES
  ((SELECT id_producto FROM inventario_productos WHERE codigo = 'INST-001'), 'Entrada', 50, 8.50, '2024-10-15', 'COMPRA-001'),
  ((SELECT id_producto FROM inventario_productos WHERE codigo = 'CONS-001'), 'Entrada', 15, 180.00, '2024-10-15', 'COMPRA-001');
```

### Salidas (Uso): ~500 registros
```sql
-- Salidas referenciando productos usados en tratamientos
INSERT INTO movimientos_inventario (id_producto, tipo_movimiento, cantidad, fecha_movimiento, id_tratamiento)
SELECT 
  put.id_producto,
  'Salida',
  put.cantidad_usada,
  t.fecha_inicio,
  t.id_tratamiento
FROM productos_usados_tratamiento put
JOIN tratamientos t ON put.id_tratamiento = t.id_tratamiento;
```

## GASTOS OPERATIVOS (20 registros)

```sql
-- Renta mensual
INSERT INTO gastos (categoria, concepto, monto, fecha, metodo_pago) VALUES
  ('Renta', 'Renta consultorio - Noviembre 2024', 15000.00, '2024-11-01', 'Transferencia'),
  ('Renta', 'Renta consultorio - Diciembre 2024', 15000.00, '2024-12-01', 'Transferencia'),
  ('Renta', 'Renta consultorio - Enero 2025', 15000.00, '2025-01-02', 'Transferencia');

-- Servicios mensuales
INSERT INTO gastos VALUES
  ('Servicios', 'Luz, agua, internet - Noviembre', 3000.00, '2024-11-05', 'Efectivo'),
  ('Servicios', 'Luz, agua, internet - Diciembre', 3200.00, '2024-12-05', 'Efectivo'),
  ('Servicios', 'Luz, agua, internet - Enero', 2800.00, '2025-01-05', 'Efectivo');

-- Compra de insumos
INSERT INTO gastos VALUES
  ('Insumos', 'Compra inicial instrumental', 12500.00, '2024-10-15', 'Transferencia'),
  ('Insumos', 'Reabastecimiento medicamentos', 4500.00, '2024-11-20', 'Efectivo'),
  ('Insumos', 'Compra material podológico', 3800.00, '2024-12-10', 'Efectivo');

-- Otros gastos
INSERT INTO gastos VALUES
  ('Marketing', 'Publicidad Facebook', 1500.00, '2024-11-15', 'Tarjeta'),
  ('Mantenimiento', 'Reparación fresadora', 800.00, '2024-12-18', 'Efectivo'),
  ('Capacitación', 'Curso actualización', 2500.00, '2024-11-22', 'Transferencia');
```

**Total gastos 3 meses: ~$86,000 MXN**

## CORTES DE CAJA DIARIOS (66 registros)

```sql
-- Uno por cada día hábil
INSERT INTO cortes_caja (fecha, ingresos_efectivo, ingresos_tarjeta, gastos_dia, saldo_final)
SELECT 
  DATE(p.fecha_pago),
  SUM(CASE WHEN p.metodo_pago = 'Efectivo' THEN p.monto ELSE 0 END),
  SUM(CASE WHEN p.metodo_pago = 'Tarjeta' THEN p.monto ELSE 0 END),
  COALESCE((SELECT SUM(monto) FROM gastos WHERE DATE(fecha) = DATE(p.fecha_pago)), 0),
  SUM(p.monto) - COALESCE((SELECT SUM(monto) FROM gastos WHERE DATE(fecha) = DATE(p.fecha_pago)), 0)
FROM pagos p
WHERE p.estado = 'Completado'
GROUP BY DATE(p.fecha_pago)
ORDER BY DATE(p.fecha_pago);
```

## COHERENCIA FINANCIERA GARANTIZADA

### Validación automática:
```sql
-- Total pagos debe igualar citas completadas × precio
SELECT 
  (SELECT SUM(precio_consulta) FROM citas WHERE estado = 'Completada') as total_citas,
  (SELECT SUM(monto) FROM pagos WHERE estado = 'Completado') as total_pagos;
-- Deben ser iguales

-- Stock = Entradas - Salidas
SELECT 
  p.nombre,
  (SELECT SUM(cantidad) FROM movimientos_inventario WHERE id_producto = p.id_producto AND tipo_movimiento = 'Entrada') as entradas,
  (SELECT SUM(cantidad) FROM movimientos_inventario WHERE id_producto = p.id_producto AND tipo_movimiento = 'Salida') as salidas,
  p.stock_actual
FROM inventario_productos p;
```

## CÁLCULOS FINALES

```sql
-- Ingresos totales
Citas completadas: 308 × $600 promedio = $184,800
Tratamientos pagados: 284 × $700 promedio = $198,800
TOTAL INGRESOS: ~$217,948 MXN

-- Gastos totales
Renta (3 meses): $45,000
Servicios: $9,000
Insumos: $25,000
Otros: $7,000
TOTAL GASTOS: $86,000 MXN

-- Utilidad
$217,948 - $86,000 = $131,948 MXN ✅
```

## PROVEEDORES (8 registros)

```sql
INSERT INTO proveedores (nombre, tipo, telefono, email, direccion) VALUES
  ('Instrumentos Médicos del Norte', 'Instrumental', '686-555-0101', 'ventas@imn.mx', 'Mexicali, BC'),
  ('Farmacéutica Regional', 'Medicamentos', '686-555-0202', 'pedidos@farmareg.mx', 'Mexicali, BC'),
  ('Distribuidora de Consumibles', 'Consumibles', '686-555-0303', 'info@distcons.mx', 'Tijuana, BC');
```

## FACTURAS (50 registros)

```sql
-- Solo para pagos con tarjeta mayores a $1,000
INSERT INTO facturas (id_pago, folio_fiscal, rfc_emisor, rfc_receptor, subtotal, iva, total, fecha_emision)
SELECT 
  p.id_pago,
  'A1B2C3D4-E5F6-7890-ABCD-' || LPAD(p.id_pago::TEXT, 12, '0'),
  'PSK123456ABC',
  'XAXX010101000',
  p.monto / 1.16,
  p.monto - (p.monto / 1.16),
  p.monto,
  p.fecha_pago
FROM pagos p
WHERE p.metodo_pago = 'Tarjeta' 
  AND p.monto > 1000
  AND p.estado = 'Completado';
```

## VALIDACIONES FINALES

```sql
-- 1. Pagos completados = 92% de citas completadas
SELECT COUNT(*) FROM pagos WHERE estado = 'Completado';
-- Esperado: ~283

-- 2. Total ingresos
SELECT SUM(monto) FROM pagos WHERE estado = 'Completado';
-- Esperado: ~$217,948

-- 3. Total gastos
SELECT SUM(monto) FROM gastos;
-- Esperado: $86,000

-- 4. Cortes de caja
SELECT COUNT(*) FROM cortes_caja;
-- Esperado: 66 (días hábiles)

-- 5. Stock coherente
SELECT COUNT(*) FROM inventario_productos 
WHERE stock_actual < 0;
-- Esperado: 0
```

## RESULTADO ESPERADO

```
✅ AGENTE 16 completado exitosamente
   - Pagos registrados: 334
   - Productos inventario: 40
   - Movimientos: 530
   - Gastos: 20
   - Cortes de caja: 66
   - Ingresos totales: $217,948
   - Gastos totales: $86,000
   - Utilidad: $131,948
   
🎉 TODOS LOS AGENTES COMPLETADOS
   Total registros generados: ~2,500
```

## ENTREGABLES
- `data/seed/04_pagos_inventario.sql`
- Script con coherencia financiera total
- Validaciones automáticas incluidas

## DEPENDENCIAS
- **Requiere**: Agentes 13, 14 y 15 completados
- **Requerido por**: Ninguno (es el último)

Al terminar, muestra resumen financiero completo y confirma coherencia de datos.

---

**Nota crítica**: Este agente DEBE ejecutarse último porque depende de IDs de citas creadas por Agente 15.
