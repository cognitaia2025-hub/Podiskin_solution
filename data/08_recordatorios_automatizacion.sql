-- ============================================================================
-- Archivo: 08_recordatorios_automatizacion.sql
-- Descripción: Sistema de recordatorios automáticos y análisis de pacientes
-- Dependencias: 03_pacientes.sql, 04_citas_tratamientos.sql, 05_chatbot_crm.sql
-- ============================================================================

-- ============================================================================
-- RECORDATORIOS PROGRAMADOS
-- ============================================================================

CREATE TABLE recordatorios_programados (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    
    -- Relaciones
    id_cita bigint REFERENCES citas(id) ON DELETE CASCADE,
    id_paciente bigint NOT NULL REFERENCES pacientes(id),
    id_contacto bigint REFERENCES contactos(id),
    
    -- Configuración del recordatorio
    tipo_recordatorio text NOT NULL CHECK (tipo_recordatorio IN (
        'Cita_Proxima',           -- 24h antes, 2h antes
        'Confirmacion_Cita',      -- Al agendar
        'Seguimiento_Post_Cita',  -- Después de la cita
        'Reagendar',              -- Para pacientes que cancelaron
        'Revision_Periodica',     -- Cada 3/6 meses
        'Cumpleaños',             -- Felicitación
        'Tratamiento_Pendiente',  -- Recordar continuar tratamiento
        'Pago_Pendiente'          -- Saldo por pagar
    )),
    
    -- Programación
    fecha_envio_programada timestamp NOT NULL,
    fecha_envio_real timestamp,
    
    -- Contenido
    id_plantilla bigint REFERENCES plantillas_mensajes(id),
    mensaje_personalizado text, -- Si se sobrescribe la plantilla
    variables_plantilla jsonb, -- {"nombre": "Juan", "fecha": "2025-01-15"}
    
    -- Canal de envío
    canal text NOT NULL CHECK (canal IN ('whatsapp', 'sms', 'email', 'push')),
    prioridad text DEFAULT 'Media' CHECK (prioridad IN ('Baja', 'Media', 'Alta', 'Urgente')),
    
    -- Estado
    estado text DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente', 'Enviando', 'Enviado', 'Fallido', 'Cancelado')),
    id_mensaje_enviado bigint REFERENCES mensajes(id),
    
    -- Reintentos
    intentos_envio integer DEFAULT 0,
    max_intentos integer DEFAULT 3,
    proximo_intento timestamp,
    error_detalle text,
    
    -- Respuesta del paciente
    paciente_respondio boolean DEFAULT false,
    fecha_respuesta timestamp,
    respuesta_texto text,
    
    -- Auditoría
    creado_por bigint REFERENCES usuarios(id),
    creado_en timestamp DEFAULT NOW(),
    cancelado_por bigint REFERENCES usuarios(id),
    cancelado_en timestamp
);

CREATE INDEX idx_recordatorios_pendientes ON recordatorios_programados(fecha_envio_programada, estado) 
WHERE estado = 'Pendiente';

CREATE INDEX idx_recordatorios_paciente ON recordatorios_programados(id_paciente, tipo_recordatorio);
CREATE INDEX idx_recordatorios_cita ON recordatorios_programados(id_cita);
CREATE INDEX idx_recordatorios_tipo ON recordatorios_programados(tipo_recordatorio, estado);

-- ============================================================================
-- TRIGGER: CREAR RECORDATORIOS AL AGENDAR CITA
-- ============================================================================

CREATE OR REPLACE FUNCTION crear_recordatorios_automaticos() RETURNS trigger AS $$
DECLARE
    v_id_contacto bigint;
    v_id_plantilla_24h bigint;
    v_id_plantilla_2h bigint;
BEGIN
    -- Solo para citas confirmadas
    IF NEW.estado != 'Confirmada' THEN
        RETURN NEW;
    END IF;
    
    -- Obtener contacto del paciente
    SELECT id INTO v_id_contacto
    FROM contactos
    WHERE id_paciente = NEW.id_paciente
    LIMIT 1;
    
    -- Obtener plantillas
    SELECT id INTO v_id_plantilla_24h
    FROM plantillas_mensajes
    WHERE categoria = 'Recordatorio_Cita' AND activo = true
    LIMIT 1;
    
    -- Recordatorio 24 horas antes
    IF NEW.fecha_hora_inicio > NOW() + INTERVAL '24 hours' THEN
        INSERT INTO recordatorios_programados (
            id_cita, id_paciente, id_contacto, tipo_recordatorio, 
            fecha_envio_programada, id_plantilla, canal, prioridad
        ) VALUES (
            NEW.id,
            NEW.id_paciente,
            v_id_contacto,
            'Cita_Proxima',
            NEW.fecha_hora_inicio - INTERVAL '24 hours',
            v_id_plantilla_24h,
            'whatsapp',
            'Alta'
        );
    END IF;
    
    -- Recordatorio 2 horas antes
    IF NEW.fecha_hora_inicio > NOW() + INTERVAL '2 hours' THEN
        INSERT INTO recordatorios_programados (
            id_cita, id_paciente, id_contacto, tipo_recordatorio,
            fecha_envio_programada, id_plantilla, canal, prioridad
        ) VALUES (
            NEW.id,
            NEW.id_paciente,
            v_id_contacto,
            'Cita_Proxima',
            NEW.fecha_hora_inicio - INTERVAL '2 hours',
            v_id_plantilla_24h,
            'whatsapp',
            'Urgente'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_crear_recordatorios_cita
AFTER INSERT ON citas
FOR EACH ROW
EXECUTE FUNCTION crear_recordatorios_automaticos();

-- ============================================================================
-- TRIGGER: RECORDATORIO DE REAGENDADO PARA CANCELACIONES
-- ============================================================================

CREATE OR REPLACE FUNCTION recordatorio_reagendar_cancelacion() RETURNS trigger AS $$
DECLARE
    v_id_contacto bigint;
BEGIN
    -- Solo cuando cambia a estado Cancelada
    IF NEW.estado = 'Cancelada' AND OLD.estado != 'Cancelada' THEN
        
        SELECT id INTO v_id_contacto
        FROM contactos
        WHERE id_paciente = NEW.id_paciente
        LIMIT 1;
        
        -- Programar recordatorio para 3 días después
        INSERT INTO recordatorios_programados (
            id_cita, id_paciente, id_contacto, tipo_recordatorio,
            fecha_envio_programada, canal, prioridad,
            mensaje_personalizado
        ) VALUES (
            NEW.id,
            NEW.id_paciente,
            v_id_contacto,
            'Reagendar',
            NOW() + INTERVAL '3 days',
            'whatsapp',
            'Media',
            'Hola, notamos que cancelaste tu cita. ¿Te gustaría reagendar? Estamos aquí para ayudarte.'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_recordatorio_cancelacion
AFTER UPDATE ON citas
FOR EACH ROW
EXECUTE FUNCTION recordatorio_reagendar_cancelacion();

-- ============================================================================
-- ANÁLISIS DE PACIENTES
-- ============================================================================

CREATE TABLE scoring_pacientes (
    id_paciente bigint PRIMARY KEY REFERENCES pacientes(id),
    
    -- Scores (0-100)
    score_adherencia numeric(5,2) DEFAULT 50, -- Basado en asistencia
    score_riesgo numeric(5,2) DEFAULT 0, -- Basado en condiciones médicas
    score_valor numeric(10,2) DEFAULT 0, -- Valor total facturado
    score_engagement numeric(5,2) DEFAULT 50, -- Interacción con mensajes
    
    -- Estadísticas
    total_citas integer DEFAULT 0,
    citas_completadas integer DEFAULT 0,
    citas_canceladas integer DEFAULT 0,
    citas_no_asistio integer DEFAULT 0,
    tasa_asistencia numeric(5,2),
    
    -- Valor económico
    valor_total_facturado numeric(10,2) DEFAULT 0,
    saldo_pendiente numeric(10,2) DEFAULT 0,
    
    -- Engagement
    mensajes_respondidos integer DEFAULT 0,
    mensajes_ignorados integer DEFAULT 0,
    ultima_interaccion timestamp,
    
    -- Recomendaciones de IA
    recomendacion_ia text,
    requiere_seguimiento boolean DEFAULT false,
    prioridad_seguimiento text CHECK (prioridad_seguimiento IN ('Baja', 'Media', 'Alta', 'Urgente')),
    
    -- Timestamps
    ultima_actualizacion timestamp DEFAULT NOW(),
    proxima_revision_sugerida date
);

CREATE INDEX idx_scoring_adherencia ON scoring_pacientes(score_adherencia DESC);
CREATE INDEX idx_scoring_valor ON scoring_pacientes(score_valor DESC);
CREATE INDEX idx_scoring_seguimiento ON scoring_pacientes(requiere_seguimiento, prioridad_seguimiento);

-- ============================================================================
-- FUNCIÓN: CALCULAR SCORING DE PACIENTE
-- ============================================================================

CREATE OR REPLACE FUNCTION calcular_scoring_paciente(p_id_paciente bigint) RETURNS void AS $$
DECLARE
    v_total_citas integer;
    v_completadas integer;
    v_canceladas integer;
    v_no_asistio integer;
    v_tasa_asistencia numeric(5,2);
    v_valor_total numeric(10,2);
    v_saldo numeric(10,2);
    v_score_adherencia numeric(5,2);
    v_score_valor numeric(10,2);
BEGIN
    -- Obtener estadísticas de citas
    SELECT 
        COUNT(*),
        COUNT(*) FILTER (WHERE estado = 'Completada'),
        COUNT(*) FILTER (WHERE estado = 'Cancelada'),
        COUNT(*) FILTER (WHERE estado = 'No_Asistio')
    INTO v_total_citas, v_completadas, v_canceladas, v_no_asistio
    FROM citas
    WHERE id_paciente = p_id_paciente;
    
    -- Calcular tasa de asistencia
    IF v_total_citas > 0 THEN
        v_tasa_asistencia := (v_completadas::numeric / v_total_citas * 100);
        v_score_adherencia := v_tasa_asistencia;
    ELSE
        v_tasa_asistencia := 50;
        v_score_adherencia := 50;
    END IF;
    
    -- Obtener valor económico
    SELECT 
        COALESCE(SUM(monto_total), 0),
        COALESCE(SUM(saldo_pendiente), 0)
    INTO v_valor_total, v_saldo
    FROM pagos p
    JOIN citas c ON p.id_cita = c.id
    WHERE c.id_paciente = p_id_paciente;
    
    -- Normalizar score de valor (0-100)
    v_score_valor := LEAST(v_valor_total / 100, 100);
    
    -- Insertar o actualizar scoring
    INSERT INTO scoring_pacientes (
        id_paciente, score_adherencia, score_valor,
        total_citas, citas_completadas, citas_canceladas, citas_no_asistio,
        tasa_asistencia, valor_total_facturado, saldo_pendiente
    ) VALUES (
        p_id_paciente, v_score_adherencia, v_score_valor,
        v_total_citas, v_completadas, v_canceladas, v_no_asistio,
        v_tasa_asistencia, v_valor_total, v_saldo
    )
    ON CONFLICT (id_paciente) DO UPDATE SET
        score_adherencia = EXCLUDED.score_adherencia,
        score_valor = EXCLUDED.score_valor,
        total_citas = EXCLUDED.total_citas,
        citas_completadas = EXCLUDED.citas_completadas,
        citas_canceladas = EXCLUDED.citas_canceladas,
        citas_no_asistio = EXCLUDED.citas_no_asistio,
        tasa_asistencia = EXCLUDED.tasa_asistencia,
        valor_total_facturado = EXCLUDED.valor_total_facturado,
        saldo_pendiente = EXCLUDED.saldo_pendiente,
        ultima_actualizacion = NOW();
        
    -- Determinar si requiere seguimiento
    UPDATE scoring_pacientes
    SET requiere_seguimiento = (
        score_adherencia < 50 OR 
        citas_canceladas > 2 OR
        saldo_pendiente > 1000
    ),
    prioridad_seguimiento = CASE
        WHEN score_adherencia < 30 THEN 'Urgente'
        WHEN score_adherencia < 50 THEN 'Alta'
        WHEN citas_canceladas > 2 THEN 'Media'
        ELSE 'Baja'
    END
    WHERE id_paciente = p_id_paciente;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VISTAS DE ANÁLISIS
-- ============================================================================

-- Vista: Pacientes que cancelaron en un período
CREATE OR REPLACE FUNCTION obtener_cancelaciones_periodo(
    fecha_inicio date,
    fecha_fin date
) RETURNS TABLE (
    paciente_id bigint,
    nombre text,
    telefono text,
    email text,
    total_cancelaciones_periodo integer,
    ultima_cancelacion timestamp,
    motivo_ultima_cancelacion text,
    score_adherencia numeric
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.primer_nombre || ' ' || p.primer_apellido,
        p.telefono_principal,
        p.email,
        COUNT(*)::integer,
        MAX(c.fecha_hora_inicio),
        (SELECT motivo_cancelacion FROM citas WHERE id_paciente = p.id AND estado = 'Cancelada' ORDER BY fecha_hora_inicio DESC LIMIT 1),
        COALESCE(s.score_adherencia, 50)
    FROM citas c
    JOIN pacientes p ON c.id_paciente = p.id
    LEFT JOIN scoring_pacientes s ON p.id = s.id_paciente
    WHERE c.estado = 'Cancelada'
      AND c.fecha_hora_inicio::date BETWEEN fecha_inicio AND fecha_fin
    GROUP BY p.id, p.primer_nombre, p.primer_apellido, p.telefono_principal, p.email, s.score_adherencia
    ORDER BY COUNT(*) DESC;
END;
$$ LANGUAGE plpgsql;

-- Vista: Pacientes que requieren seguimiento
CREATE VIEW pacientes_requieren_seguimiento AS
SELECT 
    p.id,
    p.primer_nombre || ' ' || p.primer_apellido AS nombre_completo,
    p.telefono_principal,
    p.email,
    s.score_adherencia,
    s.score_valor,
    s.total_citas,
    s.citas_canceladas,
    s.tasa_asistencia,
    s.saldo_pendiente,
    s.prioridad_seguimiento,
    s.recomendacion_ia,
    s.ultima_interaccion,
    -- Última cita
    (SELECT MAX(fecha_hora_inicio) FROM citas WHERE id_paciente = p.id) AS ultima_cita,
    -- Días sin contacto
    EXTRACT(DAY FROM NOW() - s.ultima_interaccion) AS dias_sin_contacto
FROM pacientes p
JOIN scoring_pacientes s ON p.id = s.id_paciente
WHERE s.requiere_seguimiento = true
  AND p.activo = true
ORDER BY s.prioridad_seguimiento DESC, s.score_adherencia ASC;

-- Vista: Dashboard de recordatorios
CREATE VIEW dashboard_recordatorios AS
SELECT 
    tipo_recordatorio,
    estado,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE fecha_envio_programada::date = CURRENT_DATE) AS hoy,
    COUNT(*) FILTER (WHERE fecha_envio_programada::date = CURRENT_DATE + 1) AS mañana,
    COUNT(*) FILTER (WHERE estado = 'Fallido') AS fallidos,
    COUNT(*) FILTER (WHERE paciente_respondio = true) AS con_respuesta
FROM recordatorios_programados
WHERE estado != 'Cancelado'
GROUP BY tipo_recordatorio, estado
ORDER BY tipo_recordatorio, estado;
