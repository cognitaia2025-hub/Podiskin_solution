-- ============================================================================
-- Archivo: 11_horarios_personal.sql
-- Descripción: Gestión de horarios de trabajo y disponibilidad de agenda
-- Dependencias: 02_usuarios.sql, 04_citas_tratamientos.sql
-- ============================================================================

-- ============================================================================
-- HORARIOS DE TRABAJO
-- ============================================================================

CREATE TABLE horarios_trabajo (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_podologo bigint NOT NULL REFERENCES podologos(id),
    
    -- Día y horario
    dia_semana integer NOT NULL CHECK (dia_semana BETWEEN 0 AND 6), -- 0=Domingo, 6=Sábado
    hora_inicio time NOT NULL,
    hora_fin time NOT NULL,
    
    -- Configuración de citas
    duracion_cita_minutos integer DEFAULT 30,
    tiempo_buffer_minutos integer DEFAULT 5, -- Tiempo entre citas
    max_citas_simultaneas integer DEFAULT 1,
    
    -- Vigencia
    activo boolean DEFAULT true,
    fecha_inicio_vigencia date DEFAULT CURRENT_DATE,
    fecha_fin_vigencia date,
    
    -- Auditoría
    creado_por bigint REFERENCES usuarios(id),
    fecha_creacion timestamp DEFAULT NOW(),
    
    CONSTRAINT horario_valido CHECK (hora_fin > hora_inicio)
);

CREATE INDEX idx_horarios_podologo ON horarios_trabajo(id_podologo, dia_semana, activo);

-- ============================================================================
-- BLOQUEOS DE AGENDA
-- ============================================================================

CREATE TABLE bloqueos_agenda (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_podologo bigint NOT NULL REFERENCES podologos(id),
    
    -- Período de bloqueo
    fecha_inicio timestamp NOT NULL,
    fecha_fin timestamp NOT NULL,
    
    -- Tipo y motivo
    tipo_bloqueo text NOT NULL CHECK (tipo_bloqueo IN (
        'Vacaciones',
        'Dia_Festivo',
        'Capacitacion',
        'Enfermedad',
        'Permiso_Personal',
        'Mantenimiento',
        'Otro'
    )),
    motivo text,
    notas text,
    
    -- Recurrencia (para días festivos anuales)
    es_recurrente boolean DEFAULT false,
    
    -- Estado
    activo boolean DEFAULT true,
    
    -- Auditoría
    creado_por bigint REFERENCES usuarios(id),
    fecha_creacion timestamp DEFAULT NOW(),
    
    CONSTRAINT bloqueo_valido CHECK (fecha_fin > fecha_inicio)
);

CREATE INDEX idx_bloqueos_podologo ON bloqueos_agenda(id_podologo, fecha_inicio, fecha_fin);
CREATE INDEX idx_bloqueos_fechas ON bloqueos_agenda(fecha_inicio, fecha_fin) WHERE activo = true;

-- ============================================================================
-- FUNCIÓN: OBTENER HORARIOS DISPONIBLES
-- ============================================================================

CREATE OR REPLACE FUNCTION obtener_horarios_disponibles(
    p_id_podologo bigint,
    p_fecha date
) RETURNS TABLE (
    hora_slot time,
    disponible boolean,
    motivo_no_disponible text
) AS $$
DECLARE
    v_dia_semana integer;
    v_horario RECORD;
    v_hora_actual time;
    v_citas_existentes integer;
    v_bloqueo_activo boolean;
BEGIN
    -- Obtener día de la semana
    v_dia_semana := EXTRACT(DOW FROM p_fecha);
    
    -- Obtener horario del día
    SELECT * INTO v_horario
    FROM horarios_trabajo
    WHERE id_podologo = p_id_podologo
      AND dia_semana = v_dia_semana
      AND activo = true
      AND (fecha_inicio_vigencia IS NULL OR fecha_inicio_vigencia <= p_fecha)
      AND (fecha_fin_vigencia IS NULL OR fecha_fin_vigencia >= p_fecha)
    LIMIT 1;
    
    -- Si no hay horario configurado
    IF v_horario IS NULL THEN
        RETURN;
    END IF;
    
    -- Generar slots de tiempo
    v_hora_actual := v_horario.hora_inicio;
    
    WHILE v_hora_actual < v_horario.hora_fin LOOP
        -- Verificar si hay bloqueo
        SELECT EXISTS (
            SELECT 1 FROM bloqueos_agenda
            WHERE id_podologo = p_id_podologo
              AND activo = true
              AND (p_fecha + v_hora_actual) BETWEEN fecha_inicio AND fecha_fin
        ) INTO v_bloqueo_activo;
        
        -- Contar citas en este slot
        SELECT COUNT(*) INTO v_citas_existentes
        FROM citas
        WHERE id_podologo = p_id_podologo
          AND fecha_hora_inicio::date = p_fecha
          AND fecha_hora_inicio::time = v_hora_actual
          AND estado NOT IN ('Cancelada');
        
        -- Determinar disponibilidad
        IF v_bloqueo_activo THEN
            hora_slot := v_hora_actual;
            disponible := false;
            motivo_no_disponible := 'Agenda bloqueada';
            RETURN NEXT;
        ELSIF v_citas_existentes >= v_horario.max_citas_simultaneas THEN
            hora_slot := v_hora_actual;
            disponible := false;
            motivo_no_disponible := 'Horario ocupado';
            RETURN NEXT;
        ELSE
            hora_slot := v_hora_actual;
            disponible := true;
            motivo_no_disponible := NULL;
            RETURN NEXT;
        END IF;
        
        -- Siguiente slot
        v_hora_actual := v_hora_actual + (v_horario.duracion_cita_minutos + v_horario.tiempo_buffer_minutos) * INTERVAL '1 minute';
    END LOOP;
    
    RETURN;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FUNCIÓN: VALIDAR DISPONIBILIDAD ANTES DE AGENDAR
-- ============================================================================

CREATE OR REPLACE FUNCTION validar_disponibilidad_cita() RETURNS trigger AS $$
DECLARE
    v_disponible boolean;
    v_motivo text;
BEGIN
    -- Obtener disponibilidad del slot
    SELECT disponible, motivo_no_disponible 
    INTO v_disponible, v_motivo
    FROM obtener_horarios_disponibles(NEW.id_podologo, NEW.fecha_hora_inicio::date)
    WHERE hora_slot = NEW.fecha_hora_inicio::time;
    
    -- Si no está disponible, rechazar
    IF NOT v_disponible THEN
        RAISE EXCEPTION 'No se puede agendar cita: %', v_motivo;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validar_disponibilidad
BEFORE INSERT ON citas
FOR EACH ROW
EXECUTE FUNCTION validar_disponibilidad_cita();

-- ============================================================================
-- VISTA: RESUMEN DE DISPONIBILIDAD SEMANAL
-- ============================================================================

CREATE VIEW disponibilidad_semanal AS
SELECT 
    p.id AS id_podologo,
    p.nombre_completo,
    h.dia_semana,
    CASE h.dia_semana
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Lunes'
        WHEN 2 THEN 'Martes'
        WHEN 3 THEN 'Miércoles'
        WHEN 4 THEN 'Jueves'
        WHEN 5 THEN 'Viernes'
        WHEN 6 THEN 'Sábado'
    END AS dia_nombre,
    h.hora_inicio,
    h.hora_fin,
    h.duracion_cita_minutos,
    -- Calcular slots disponibles por día
    FLOOR(EXTRACT(EPOCH FROM (h.hora_fin - h.hora_inicio)) / 60 / 
          (h.duracion_cita_minutos + h.tiempo_buffer_minutos)) AS slots_disponibles_dia,
    h.activo
FROM podologos p
JOIN horarios_trabajo h ON p.id = h.id_podologo
WHERE p.activo = true
ORDER BY p.nombre_completo, h.dia_semana, h.hora_inicio;

-- ============================================================================
-- VISTA: BLOQUEOS ACTIVOS
-- ============================================================================

CREATE VIEW bloqueos_activos AS
SELECT 
    b.id,
    p.nombre_completo AS podologo,
    b.tipo_bloqueo,
    b.fecha_inicio,
    b.fecha_fin,
    EXTRACT(DAY FROM (b.fecha_fin - b.fecha_inicio)) AS dias_bloqueados,
    b.motivo,
    u.nombre_completo AS creado_por_nombre
FROM bloqueos_agenda b
JOIN podologos p ON b.id_podologo = p.id
LEFT JOIN usuarios u ON b.creado_por = u.id
WHERE b.activo = true
  AND b.fecha_fin >= CURRENT_DATE
ORDER BY b.fecha_inicio;

-- ============================================================================
-- FUNCIÓN: CALCULAR CAPACIDAD MENSUAL
-- ============================================================================

CREATE OR REPLACE FUNCTION calcular_capacidad_mensual(
    p_id_podologo bigint,
    p_mes date
) RETURNS TABLE (
    total_dias_laborables integer,
    total_slots_disponibles integer,
    slots_ocupados integer,
    slots_libres integer,
    tasa_ocupacion numeric
) AS $$
DECLARE
    v_fecha date;
    v_slots_dia integer;
    v_total_slots integer := 0;
    v_ocupados integer := 0;
BEGIN
    -- Iterar cada día del mes
    FOR v_fecha IN 
        SELECT generate_series(
            DATE_TRUNC('month', p_mes),
            DATE_TRUNC('month', p_mes) + INTERVAL '1 month' - INTERVAL '1 day',
            '1 day'::interval
        )::date
    LOOP
        -- Contar slots disponibles ese día
        SELECT COUNT(*) INTO v_slots_dia
        FROM obtener_horarios_disponibles(p_id_podologo, v_fecha);
        
        v_total_slots := v_total_slots + v_slots_dia;
        
        -- Contar citas ocupadas ese día
        SELECT COUNT(*) INTO v_ocupados
        FROM citas
        WHERE id_podologo = p_id_podologo
          AND fecha_hora_inicio::date = v_fecha
          AND estado NOT IN ('Cancelada');
    END LOOP;
    
    RETURN QUERY
    SELECT 
        EXTRACT(DAY FROM DATE_TRUNC('month', p_mes) + INTERVAL '1 month' - INTERVAL '1 day')::integer,
        v_total_slots,
        v_ocupados,
        v_total_slots - v_ocupados,
        CASE WHEN v_total_slots > 0 
             THEN ROUND((v_ocupados::numeric / v_total_slots * 100), 2)
             ELSE 0 
        END;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Vista: Productividad de Podólogos (movida de 06_vistas.sql)
-- Descripción: Analiza el desempeño y productividad de cada podólogo
-- ============================================================================
CREATE VIEW productividad_podologos AS
SELECT 
    pod.id AS id_podologo,
    u.nombre_completo AS nombre_podologo,
    u.email,
    pod.especialidad,
    pod.activo,
    -- Métricas de citas del mes actual
    COUNT(DISTINCT c.id) FILTER (WHERE c.fecha_hora_inicio >= DATE_TRUNC('month', CURRENT_DATE)) AS citas_mes_actual,
    COUNT(DISTINCT c.id) FILTER (WHERE c.fecha_hora_inicio >= DATE_TRUNC('month', CURRENT_DATE) AND c.estado = 'Completada') AS citas_completadas_mes,
    COUNT(DISTINCT c.id) FILTER (WHERE c.fecha_hora_inicio >= DATE_TRUNC('month', CURRENT_DATE) AND c.estado = 'Cancelada') AS citas_canceladas_mes,
    COUNT(DISTINCT c.id) FILTER (WHERE c.fecha_hora_inicio >= DATE_TRUNC('month', CURRENT_DATE) AND c.estado = 'No_Asistio') AS pacientes_no_asistieron_mes,
    -- Tasa de efectividad
    ROUND(
        COUNT(DISTINCT c.id) FILTER (WHERE c.fecha_hora_inicio >= DATE_TRUNC('month', CURRENT_DATE) AND c.estado = 'Completada')::NUMERIC / 
        NULLIF(COUNT(DISTINCT c.id) FILTER (WHERE c.fecha_hora_inicio >= DATE_TRUNC('month', CURRENT_DATE)), 0) * 100, 
        2
    ) AS tasa_completitud_mes,
    -- Métricas de pacientes
    COUNT(DISTINCT c.id_paciente) FILTER (WHERE c.fecha_hora_inicio >= DATE_TRUNC('month', CURRENT_DATE)) AS pacientes_unicos_mes,
    COUNT(DISTINCT c.id_paciente) FILTER (WHERE c.es_primera_vez = true AND c.fecha_hora_inicio >= DATE_TRUNC('month', CURRENT_DATE)) AS pacientes_nuevos_mes,
    -- Ingresos generados
    COALESCE(SUM(p.monto_pagado) FILTER (WHERE c.fecha_hora_inicio >= DATE_TRUNC('month', CURRENT_DATE)), 0) AS ingresos_mes,
    COALESCE(AVG(p.monto_pagado) FILTER (WHERE c.fecha_hora_inicio >= DATE_TRUNC('month', CURRENT_DATE)), 0) AS ticket_promedio_mes,
    -- Tratamientos realizados
    COUNT(dc.id) FILTER (WHERE c.fecha_hora_inicio >= DATE_TRUNC('month', CURRENT_DATE) AND c.estado = 'Completada') AS tratamientos_realizados_mes,
    -- Horarios disponibles
    COUNT(ht.id) FILTER (WHERE ht.activo = true) AS dias_laborales_configurados,
    -- Métricas históricas (últimos 3 meses)
    COUNT(DISTINCT c.id) FILTER (WHERE c.fecha_hora_inicio >= CURRENT_DATE - INTERVAL '3 months') AS citas_ultimos_3_meses,
    COALESCE(SUM(p.monto_pagado) FILTER (WHERE c.fecha_hora_inicio >= CURRENT_DATE - INTERVAL '3 months'), 0) AS ingresos_ultimos_3_meses,
    -- Última actividad
    MAX(c.fecha_hora_inicio) AS ultima_cita_atendida
FROM podologos pod
JOIN usuarios u ON pod.id_usuario = u.id
LEFT JOIN citas c ON pod.id = c.id_podologo
LEFT JOIN detalle_cita dc ON c.id = dc.id_cita
LEFT JOIN pagos p ON c.id = p.id_cita
LEFT JOIN horarios_trabajo ht ON pod.id = ht.id_podologo
GROUP BY pod.id, u.nombre_completo, u.email, pod.especialidad, pod.activo
ORDER BY citas_mes_actual DESC;
