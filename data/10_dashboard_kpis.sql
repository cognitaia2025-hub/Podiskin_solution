-- ============================================================================
-- Archivo: 10_dashboard_kpis.sql
-- Descripción: Dashboard ejecutivo, KPIs y reportes para Santiago
-- Dependencias: Todos los archivos anteriores
-- ============================================================================

-- ============================================================================
-- DASHBOARD EJECUTIVO EN TIEMPO REAL
-- ============================================================================

CREATE VIEW dashboard_ejecutivo AS
SELECT 
    -- CITAS DE HOY
    (SELECT COUNT(*) 
     FROM citas 
     WHERE fecha_hora_inicio::date = CURRENT_DATE 
       AND estado NOT IN ('Cancelada')) AS citas_hoy,
    
    (SELECT COUNT(*) 
     FROM citas 
     WHERE fecha_hora_inicio::date = CURRENT_DATE 
       AND estado = 'Completada') AS citas_completadas_hoy,
    
    (SELECT COUNT(*) 
     FROM citas 
     WHERE fecha_hora_inicio::date = CURRENT_DATE 
       AND estado = 'Pendiente') AS citas_pendientes_hoy,
    
    -- INGRESOS
    (SELECT COALESCE(SUM(monto_pagado), 0) 
     FROM pagos 
     WHERE fecha_pago::date = CURRENT_DATE) AS ingresos_hoy,
    
    (SELECT COALESCE(SUM(monto_pagado), 0) 
     FROM pagos 
     WHERE EXTRACT(MONTH FROM fecha_pago) = EXTRACT(MONTH FROM CURRENT_DATE)
       AND EXTRACT(YEAR FROM fecha_pago) = EXTRACT(YEAR FROM CURRENT_DATE)) AS ingresos_mes,
    
    (SELECT COALESCE(SUM(saldo_pendiente), 0) 
     FROM pagos 
     WHERE saldo_pendiente > 0) AS saldo_total_pendiente,
    
    -- PACIENTES
    (SELECT COUNT(DISTINCT id_paciente) 
     FROM citas 
     WHERE EXTRACT(MONTH FROM fecha_hora_inicio) = EXTRACT(MONTH FROM CURRENT_DATE)
       AND estado = 'Completada') AS pacientes_atendidos_mes,
    
    (SELECT COUNT(*) 
     FROM pacientes 
     WHERE EXTRACT(MONTH FROM fecha_registro) = EXTRACT(MONTH FROM CURRENT_DATE)) AS pacientes_nuevos_mes,
    
    -- CONVERSACIONES Y CRM
    (SELECT COUNT(*) 
     FROM conversaciones 
     WHERE estado IN ('Activa', 'Esperando_Humano')) AS conversaciones_pendientes,
    
    (SELECT COUNT(*) 
     FROM recordatorios_programados 
     WHERE estado = 'Pendiente' 
       AND fecha_envio_programada::date = CURRENT_DATE) AS recordatorios_hoy,
    
    -- INVENTARIO
    (SELECT COUNT(*) 
     FROM inventario_productos 
     WHERE stock_actual <= stock_minimo 
       AND activo = true) AS productos_stock_bajo,
    
    -- PRÓXIMA CITA
    (SELECT MIN(fecha_hora_inicio) 
     FROM citas 
     WHERE fecha_hora_inicio > NOW() 
       AND estado IN ('Pendiente', 'Confirmada')) AS proxima_cita,
    
    -- TASA DE OCUPACIÓN HOY
    (SELECT 
        ROUND((COUNT(*) FILTER (WHERE estado NOT IN ('Cancelada'))::numeric / 
        NULLIF(COUNT(*), 0) * 100), 2)
     FROM citas 
     WHERE fecha_hora_inicio::date = CURRENT_DATE) AS tasa_ocupacion_hoy;

-- ============================================================================
-- KPIs MENSUALES
-- ============================================================================

CREATE VIEW kpis_mensuales AS
SELECT 
    DATE_TRUNC('month', c.fecha_hora_inicio)::date AS mes,
    
    -- CITAS
    COUNT(*) AS total_citas,
    COUNT(*) FILTER (WHERE c.estado = 'Completada') AS citas_completadas,
    COUNT(*) FILTER (WHERE c.estado = 'Cancelada') AS citas_canceladas,
    COUNT(*) FILTER (WHERE c.estado = 'No_Asistio') AS no_asistencias,
    ROUND((COUNT(*) FILTER (WHERE c.estado = 'Completada')::numeric / 
           NULLIF(COUNT(*), 0) * 100), 2) AS tasa_asistencia,
    
    -- PACIENTES
    COUNT(DISTINCT c.id_paciente) AS pacientes_atendidos,
    COUNT(*) FILTER (WHERE c.es_primera_vez = true) AS pacientes_nuevos,
    COUNT(DISTINCT c.id_paciente) FILTER (WHERE c.estado = 'Completada') AS pacientes_activos,
    
    -- INGRESOS
    COALESCE(SUM(p.monto_total), 0) AS ingresos_brutos,
    COALESCE(SUM(p.monto_pagado), 0) AS ingresos_cobrados,
    COALESCE(SUM(p.saldo_pendiente), 0) AS saldo_pendiente,
    ROUND(COALESCE(AVG(p.monto_total), 0), 2) AS ticket_promedio,
    
    -- EFICIENCIA
    ROUND(AVG(EXTRACT(EPOCH FROM (c.fecha_hora_fin - c.fecha_hora_inicio)) / 60), 2) AS duracion_promedio_min,
    
    -- TRATAMIENTOS
    COUNT(DISTINCT dc.id_tratamiento) AS tratamientos_diferentes,
    COUNT(dc.id) AS total_tratamientos_aplicados
    
FROM citas c
LEFT JOIN pagos p ON c.id = p.id_cita
LEFT JOIN detalle_cita dc ON c.id = dc.id_cita
GROUP BY DATE_TRUNC('month', c.fecha_hora_inicio)
ORDER BY mes DESC;

-- ============================================================================
-- ANÁLISIS DE TRATAMIENTOS
-- ============================================================================

CREATE VIEW tratamientos_mas_solicitados AS
SELECT 
    t.id,
    t.codigo_servicio,
    t.nombre_servicio,
    t.precio_base,
    COUNT(dc.id) AS veces_aplicado,
    SUM(dc.precio_final) AS ingresos_generados,
    ROUND(AVG(dc.precio_final), 2) AS precio_promedio,
    COUNT(DISTINCT c.id_paciente) AS pacientes_unicos,
    MAX(c.fecha_hora_inicio) AS ultima_aplicacion
FROM tratamientos t
LEFT JOIN detalle_cita dc ON t.id = dc.id_tratamiento
LEFT JOIN citas c ON dc.id_cita = c.id
WHERE c.estado = 'Completada'
  AND c.fecha_hora_inicio >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY t.id, t.codigo_servicio, t.nombre_servicio, t.precio_base
ORDER BY veces_aplicado DESC;

-- ============================================================================
-- ANÁLISIS DE PACIENTES
-- ============================================================================

CREATE VIEW analisis_pacientes AS
SELECT 
    p.id,
    p.primer_nombre || ' ' || p.primer_apellido AS nombre_completo,
    p.telefono_principal,
    p.email,
    p.fecha_registro,
    
    -- Citas
    COUNT(c.id) AS total_citas,
    COUNT(c.id) FILTER (WHERE c.estado = 'Completada') AS citas_completadas,
    COUNT(c.id) FILTER (WHERE c.estado = 'Cancelada') AS citas_canceladas,
    MAX(c.fecha_hora_inicio) AS ultima_cita,
    MIN(c.fecha_hora_inicio) AS primera_cita,
    
    -- Ingresos
    COALESCE(SUM(pg.monto_total), 0) AS valor_total,
    COALESCE(SUM(pg.monto_pagado), 0) AS total_pagado,
    COALESCE(SUM(pg.saldo_pendiente), 0) AS saldo_pendiente,
    
    -- Scoring
    COALESCE(s.score_adherencia, 50) AS score_adherencia,
    COALESCE(s.score_valor, 0) AS score_valor,
    
    -- Clasificación
    CASE 
        WHEN COUNT(c.id) = 0 THEN 'Sin_Citas'
        WHEN COUNT(c.id) = 1 THEN 'Nuevo'
        WHEN COUNT(c.id) BETWEEN 2 AND 5 THEN 'Regular'
        WHEN COUNT(c.id) > 5 THEN 'Frecuente'
    END AS clasificacion,
    
    -- Días desde última cita
    CASE 
        WHEN MAX(c.fecha_hora_inicio) IS NULL THEN NULL
        ELSE EXTRACT(DAY FROM NOW() - MAX(c.fecha_hora_inicio))::integer
    END AS dias_sin_cita
    
FROM pacientes p
LEFT JOIN citas c ON p.id = c.id_paciente
LEFT JOIN pagos pg ON c.id = pg.id_cita
LEFT JOIN scoring_pacientes s ON p.id = s.id_paciente
WHERE p.activo = true
GROUP BY p.id, p.primer_nombre, p.primer_apellido, p.telefono_principal, p.email, p.fecha_registro, s.score_adherencia, s.score_valor
ORDER BY valor_total DESC;

-- ============================================================================
-- REPORTE DE INGRESOS DETALLADO
-- ============================================================================

CREATE VIEW reporte_ingresos_detallado AS
SELECT 
    DATE_TRUNC('day', p.fecha_pago)::date AS fecha,
    DATE_TRUNC('week', p.fecha_pago)::date AS semana,
    DATE_TRUNC('month', p.fecha_pago)::date AS mes,
    
    -- Métodos de pago
    COUNT(*) AS total_pagos,
    COUNT(*) FILTER (WHERE p.metodo_pago = 'Efectivo') AS pagos_efectivo,
    COUNT(*) FILTER (WHERE p.metodo_pago LIKE 'Tarjeta%') AS pagos_tarjeta,
    COUNT(*) FILTER (WHERE p.metodo_pago = 'Transferencia') AS pagos_transferencia,
    
    -- Montos
    SUM(p.monto_total) AS monto_total,
    SUM(p.monto_pagado) AS monto_pagado,
    SUM(p.saldo_pendiente) AS saldo_pendiente,
    
    -- Estados
    COUNT(*) FILTER (WHERE p.estado_pago = 'Pagado') AS pagos_completos,
    COUNT(*) FILTER (WHERE p.estado_pago = 'Parcial') AS pagos_parciales,
    COUNT(*) FILTER (WHERE p.estado_pago = 'Pendiente') AS pagos_pendientes,
    
    -- Promedios
    ROUND(AVG(p.monto_total), 2) AS ticket_promedio,
    ROUND(AVG(p.monto_pagado), 2) AS pago_promedio
    
FROM pagos p
GROUP BY DATE_TRUNC('day', p.fecha_pago), DATE_TRUNC('week', p.fecha_pago), DATE_TRUNC('month', p.fecha_pago)
ORDER BY fecha DESC;

-- ============================================================================
-- ANÁLISIS DE CONVERSIONES (CRM)
-- ============================================================================

CREATE VIEW analisis_conversiones_crm AS
SELECT 
    DATE_TRUNC('month', co.fecha_primer_contacto)::date AS mes,
    
    -- Contactos
    COUNT(*) AS total_contactos,
    COUNT(*) FILTER (WHERE co.tipo = 'Prospecto') AS prospectos,
    COUNT(*) FILTER (WHERE co.tipo = 'Lead_Calificado') AS leads_calificados,
    COUNT(*) FILTER (WHERE co.tipo = 'Paciente_Convertido') AS convertidos,
    
    -- Tasa de conversión
    ROUND((COUNT(*) FILTER (WHERE co.tipo = 'Paciente_Convertido')::numeric / 
           NULLIF(COUNT(*), 0) * 100), 2) AS tasa_conversion,
    
    -- Origen
    COUNT(*) FILTER (WHERE co.origen = 'WhatsApp') AS origen_whatsapp,
    COUNT(*) FILTER (WHERE co.origen = 'Facebook') AS origen_facebook,
    COUNT(*) FILTER (WHERE co.origen = 'Referido') AS origen_referido,
    COUNT(*) FILTER (WHERE co.origen = 'Google') AS origen_google,
    
    -- Conversaciones
    COUNT(DISTINCT cv.id) FILTER (WHERE cv.estado = 'Resuelta') AS conversaciones_resueltas,
    
    -- Tiempo promedio de conversión
    ROUND(AVG(EXTRACT(DAY FROM pac.fecha_registro - co.fecha_primer_contacto)), 2) AS dias_promedio_conversion
    
FROM contactos co
LEFT JOIN pacientes pac ON co.id_paciente = pac.id
LEFT JOIN conversaciones cv ON co.id = cv.id_contacto
GROUP BY DATE_TRUNC('month', co.fecha_primer_contacto)
ORDER BY mes DESC;

-- ============================================================================
-- FUNCIÓN: GENERAR REPORTE PERSONALIZADO
-- ============================================================================

CREATE OR REPLACE FUNCTION generar_reporte_periodo(
    p_fecha_inicio date,
    p_fecha_fin date
) RETURNS TABLE (
    total_citas bigint,
    citas_completadas bigint,
    tasa_asistencia numeric,
    ingresos_totales numeric,
    ticket_promedio numeric,
    pacientes_atendidos bigint,
    pacientes_nuevos bigint,
    tratamientos_aplicados bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(c.id),
        COUNT(c.id) FILTER (WHERE c.estado = 'Completada'),
        ROUND((COUNT(c.id) FILTER (WHERE c.estado = 'Completada')::numeric / 
               NULLIF(COUNT(c.id), 0) * 100), 2),
        COALESCE(SUM(p.monto_pagado), 0),
        ROUND(COALESCE(AVG(p.monto_total), 0), 2),
        COUNT(DISTINCT c.id_paciente),
        COUNT(DISTINCT c.id_paciente) FILTER (WHERE c.es_primera_vez = true),
        COUNT(dc.id)
    FROM citas c
    LEFT JOIN pagos p ON c.id = p.id_cita
    LEFT JOIN detalle_cita dc ON c.id = dc.id_cita
    WHERE c.fecha_hora_inicio::date BETWEEN p_fecha_inicio AND p_fecha_fin;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VISTA: TOP 10 PACIENTES POR VALOR
-- ============================================================================

CREATE VIEW top_pacientes_valor AS
SELECT 
    p.id,
    p.primer_nombre || ' ' || p.primer_apellido AS nombre,
    p.telefono_principal,
    COUNT(c.id) AS total_citas,
    SUM(pg.monto_total) AS valor_total,
    SUM(pg.monto_pagado) AS total_pagado,
    MAX(c.fecha_hora_inicio) AS ultima_visita,
    s.score_adherencia
FROM pacientes p
JOIN citas c ON p.id = c.id_paciente
JOIN pagos pg ON c.id = pg.id_cita
LEFT JOIN scoring_pacientes s ON p.id = s.id_paciente
WHERE c.estado = 'Completada'
GROUP BY p.id, p.primer_nombre, p.primer_apellido, p.telefono_principal, s.score_adherencia
ORDER BY valor_total DESC
LIMIT 10;

-- ============================================================================
-- VISTA: ALERTAS Y NOTIFICACIONES
-- ============================================================================

CREATE VIEW alertas_sistema AS
SELECT 
    'Stock Bajo' AS tipo_alerta,
    'Inventario' AS categoria,
    'Alta' AS prioridad,
    COUNT(*) AS cantidad,
    'Productos con stock por debajo del mínimo' AS descripcion
FROM inventario_productos
WHERE stock_actual <= stock_minimo AND activo = true

UNION ALL

SELECT 
    'Saldo Pendiente' AS tipo_alerta,
    'Pagos' AS categoria,
    'Media' AS prioridad,
    COUNT(*) AS cantidad,
    'Pacientes con saldo pendiente mayor a $500' AS descripcion
FROM pagos
WHERE saldo_pendiente > 500

UNION ALL

SELECT 
    'Conversaciones Sin Atender' AS tipo_alerta,
    'CRM' AS categoria,
    'Alta' AS prioridad,
    COUNT(*) AS cantidad,
    'Conversaciones activas sin respuesta' AS descripcion
FROM conversaciones
WHERE estado IN ('Activa', 'Esperando_Humano')

UNION ALL

SELECT 
    'Productos por Caducar' AS tipo_alerta,
    'Inventario' AS categoria,
    'Urgente' AS prioridad,
    COUNT(*) AS cantidad,
    'Productos que caducan en menos de 30 días' AS descripcion
FROM inventario_productos
WHERE tiene_caducidad = true
  AND fecha_caducidad <= CURRENT_DATE + INTERVAL '30 days'
  AND stock_actual > 0

UNION ALL

SELECT 
    'Pacientes Inactivos' AS tipo_alerta,
    'Seguimiento' AS categoria,
    'Baja' AS prioridad,
    COUNT(*) AS cantidad,
    'Pacientes sin cita en los últimos 6 meses' AS descripcion
FROM pacientes p
WHERE p.activo = true
  AND NOT EXISTS (
      SELECT 1 FROM citas c 
      WHERE c.id_paciente = p.id 
        AND c.fecha_hora_inicio >= CURRENT_DATE - INTERVAL '6 months'
  );
