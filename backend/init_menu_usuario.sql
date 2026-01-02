-- ============================================================================
-- Archivo: init_menu_usuario.sql
-- Descripción: Datos iniciales y vistas para el menú de usuario
-- ============================================================================

-- ============================================================================
-- DATOS INICIALES: Roles del sistema
-- ============================================================================

INSERT INTO roles (nombre_rol, descripcion, permisos, activo) VALUES
('Admin', 'Administrador completo', '{"all":true}'::jsonb, true),
('Podologo', 'Acceso clinico', '{"pacientes":true,"citas":true,"tratamientos":true}'::jsonb, true),
('Recepcionista', 'Citas y pagos', '{"citas":true,"pagos":true}'::jsonb, true),
('Asistente', 'Solo lectura', '{"lectura":true}'::jsonb, true)
ON CONFLICT (nombre_rol) DO NOTHING;

-- ============================================================================
-- VISTA: Resumen de gastos por categoria y mes
-- ============================================================================

CREATE OR REPLACE VIEW resumen_gastos_mensual AS
SELECT 
    categoria,
    DATE_TRUNC('month', fecha_gasto) as mes,
    COUNT(*) as total_registros,
    SUM(monto) as total_monto
FROM gastos
GROUP BY categoria, DATE_TRUNC('month', fecha_gasto)
ORDER BY mes DESC, total_monto DESC;

-- ============================================================================
-- VISTA: Balance financiero (ingresos vs egresos)
-- ============================================================================

CREATE OR REPLACE VIEW balance_financiero AS
SELECT 
    DATE_TRUNC('month', p.fecha_pago) as mes,
    SUM(p.monto_total) as ingresos,
    COALESCE((
        SELECT SUM(g.monto) 
        FROM gastos g 
        WHERE DATE_TRUNC('month', g.fecha_gasto) = DATE_TRUNC('month', p.fecha_pago)
    ), 0) as egresos,
    SUM(p.monto_total) - COALESCE((
        SELECT SUM(g.monto) 
        FROM gastos g 
        WHERE DATE_TRUNC('month', g.fecha_gasto) = DATE_TRUNC('month', p.fecha_pago)
    ), 0) as utilidad
FROM pagos p
GROUP BY DATE_TRUNC('month', p.fecha_pago)
ORDER BY mes DESC;

-- ============================================================================
-- VISTA: Alertas de inventario (stock bajo)
-- ============================================================================

CREATE OR REPLACE VIEW alertas_inventario AS
SELECT 
    id,
    nombre,
    categoria,
    stock_actual,
    stock_minimo,
    (stock_minimo - stock_actual) as cantidad_faltante,
    costo_unitario,
    (stock_minimo - stock_actual) * costo_unitario as costo_reposicion
FROM inventario_productos
WHERE stock_actual <= stock_minimo
  AND activo = true
ORDER BY cantidad_faltante DESC;

-- ============================================================================
-- VERIFICACION
-- ============================================================================

SELECT 'Roles insertados:' as info, COUNT(*) as total FROM roles;
SELECT 'Vistas creadas: resumen_gastos_mensual, balance_financiero, alertas_inventario' as info;
