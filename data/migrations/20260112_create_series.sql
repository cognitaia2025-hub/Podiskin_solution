-- =====================================================
-- Migración: Sistema de Recurrencia para Citas
-- Fecha: 2026-01-12
-- Descripción: Crea tablas para gestionar series de
--              citas recurrentes (diarias, semanales, mensuales)
-- =====================================================

-- Crear tabla de series recurrentes
CREATE TABLE IF NOT EXISTS cita_series (
    id BIGSERIAL PRIMARY KEY,
    regla_recurrencia JSONB NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    id_paciente BIGINT NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    id_podologo BIGINT NOT NULL REFERENCES podologos(id),
    tipo_cita VARCHAR(20) NOT NULL,
    duracion_minutos INT NOT NULL DEFAULT 30 CHECK (duracion_minutos > 0),
    hora_inicio TIME NOT NULL,
    notas_serie TEXT,
    activa BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creado_por BIGINT REFERENCES usuarios(id),
    CONSTRAINT regla_recurrencia_valida CHECK (
        regla_recurrencia ? 'frequency' AND
        (regla_recurrencia->>'frequency') IN ('DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY')
    )
);

-- Agregar columna serie_id a tabla citas
ALTER TABLE citas 
ADD COLUMN IF NOT EXISTS serie_id BIGINT REFERENCES cita_series(id) ON DELETE SET NULL;

-- Índices para rendimiento
CREATE INDEX IF NOT EXISTS idx_series_paciente 
ON cita_series(id_paciente);

CREATE INDEX IF NOT EXISTS idx_series_podologo 
ON cita_series(id_podologo);

CREATE INDEX IF NOT EXISTS idx_series_activas 
ON cita_series(activa) 
WHERE activa = TRUE;

CREATE INDEX IF NOT EXISTS idx_series_fecha_rango 
ON cita_series(fecha_inicio, fecha_fin);

CREATE INDEX IF NOT EXISTS idx_citas_serie 
ON citas(serie_id) 
WHERE serie_id IS NOT NULL;

-- Comentarios para documentación
COMMENT ON TABLE cita_series IS 'Series de citas recurrentes configuradas';
COMMENT ON COLUMN cita_series.regla_recurrencia IS 'Regla RRULE en formato JSON: {frequency: DAILY|WEEKLY|MONTHLY, interval: N, count: N, byweekday: [0-6]}';
COMMENT ON COLUMN cita_series.duracion_minutos IS 'Duración en minutos de cada cita de la serie';
COMMENT ON COLUMN cita_series.hora_inicio IS 'Hora de inicio para todas las citas de la serie';
COMMENT ON COLUMN cita_series.activa IS 'Si FALSE, no se generarán más citas de esta serie';

-- Vista para series activas con resumen
CREATE OR REPLACE VIEW vista_series_activas AS
SELECT 
    s.id as id_serie,
    s.regla_recurrencia,
    s.fecha_inicio,
    s.fecha_fin,
    s.duracion_minutos,
    s.hora_inicio,
    s.tipo_cita,
    s.activa,
    CONCAT_WS(' ', p.primer_nombre, p.segundo_nombre, p.primer_apellido, p.segundo_apellido) as nombre_paciente,
    p.telefono_principal,
    pod.nombre_completo as nombre_podologo,
    COUNT(c.id) as citas_generadas,
    COUNT(CASE WHEN c.estado = 'Completada' THEN 1 END) as citas_completadas,
    COUNT(CASE WHEN c.estado = 'Cancelada' THEN 1 END) as citas_canceladas
FROM cita_series s
JOIN pacientes p ON s.id_paciente = p.id
JOIN podologos pod ON s.id_podologo = pod.id
LEFT JOIN citas c ON c.serie_id = s.id
WHERE s.activa = TRUE
GROUP BY s.id, s.regla_recurrencia, s.fecha_inicio, s.fecha_fin, s.duracion_minutos, 
         s.hora_inicio, s.tipo_cita, s.activa, p.primer_nombre, p.segundo_nombre, p.primer_apellido, p.segundo_apellido, p.telefono_principal, 
         pod.nombre_completo
ORDER BY s.fecha_inicio DESC;

-- Función para generar citas desde una serie
CREATE OR REPLACE FUNCTION generar_citas_desde_serie(
    p_id_serie BIGINT,
    p_fecha_hasta DATE DEFAULT NULL
) RETURNS INT AS $$
DECLARE
    v_serie RECORD;
    v_fecha_actual DATE;
    v_fecha_limite DATE;
    v_intervalo INT;
    v_frequency TEXT;
    v_count INT;
    v_citas_generadas INT := 0;
    v_fecha_hora_inicio TIMESTAMP;
    v_fecha_hora_fin TIMESTAMP;
    v_existe_cita BOOLEAN;
BEGIN
    -- Obtener datos de la serie
    SELECT * INTO v_serie FROM cita_series WHERE id = p_id_serie AND activa = TRUE;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Serie % no encontrada o inactiva', p_id_serie;
    END IF;
    
    -- Extraer parámetros de la regla de recurrencia
    v_frequency := v_serie.regla_recurrencia->>'frequency';
    v_intervalo := COALESCE((v_serie.regla_recurrencia->>'interval')::INT, 1);
    v_count := (v_serie.regla_recurrencia->>'count')::INT;
    
    -- Determinar fecha límite
    v_fecha_limite := COALESCE(p_fecha_hasta, v_serie.fecha_fin, CURRENT_DATE + INTERVAL '1 year');
    
    -- Fecha de inicio
    v_fecha_actual := v_serie.fecha_inicio;
    
    -- Generar citas según la frecuencia
    WHILE v_fecha_actual <= v_fecha_limite AND (v_count IS NULL OR v_citas_generadas < v_count) LOOP
        -- Construir timestamp completo
        v_fecha_hora_inicio := v_fecha_actual + v_serie.hora_inicio;
        v_fecha_hora_fin := v_fecha_hora_inicio + (v_serie.duracion_minutos || ' minutes')::INTERVAL;
        
        -- Verificar que la cita no exista ya
        SELECT EXISTS(
            SELECT 1 FROM citas 
            WHERE serie_id = p_id_serie 
              AND fecha_hora_inicio = v_fecha_hora_inicio
        ) INTO v_existe_cita;
        
        IF NOT v_existe_cita THEN
            -- Crear la cita
            INSERT INTO citas (
                id_paciente,
                id_podologo,
                fecha_hora_inicio,
                fecha_hora_fin,
                tipo_cita,
                estado,
                es_primera_vez,
                notas_recepcion,
                serie_id,
                creado_por
            ) VALUES (
                v_serie.id_paciente,
                v_serie.id_podologo,
                v_fecha_hora_inicio,
                v_fecha_hora_fin,
                v_serie.tipo_cita,
                'Pendiente',
                FALSE,
                v_serie.notas_serie,
                p_id_serie,
                v_serie.creado_por
            );
            
            v_citas_generadas := v_citas_generadas + 1;
        END IF;
        
        -- Avanzar a la siguiente fecha según frecuencia
        CASE v_frequency
            WHEN 'DAILY' THEN
                v_fecha_actual := v_fecha_actual + (v_intervalo || ' days')::INTERVAL;
            WHEN 'WEEKLY' THEN
                v_fecha_actual := v_fecha_actual + (v_intervalo * 7 || ' days')::INTERVAL;
            WHEN 'MONTHLY' THEN
                v_fecha_actual := v_fecha_actual + (v_intervalo || ' months')::INTERVAL;
            WHEN 'YEARLY' THEN
                v_fecha_actual := v_fecha_actual + (v_intervalo || ' years')::INTERVAL;
        END CASE;
    END LOOP;
    
    RETURN v_citas_generadas;
END;
$$ LANGUAGE plpgsql;

-- Función para desactivar una serie (cancelar futuras citas)
CREATE OR REPLACE FUNCTION desactivar_serie(
    p_id_serie BIGINT,
    p_cancelar_futuras BOOLEAN DEFAULT FALSE
) RETURNS BOOLEAN AS $$
BEGIN
    -- Marcar serie como inactiva
    UPDATE cita_series 
    SET activa = FALSE, fecha_fin = CURRENT_DATE
    WHERE id = p_id_serie;
    
    -- Opcionalmente cancelar citas futuras
    IF p_cancelar_futuras THEN
        UPDATE citas 
        SET estado = 'Cancelada',
            motivo_cancelacion = 'Serie recurrente desactivada'
        WHERE serie_id = p_id_serie 
          AND fecha_hora_inicio > CURRENT_TIMESTAMP
          AND estado NOT IN ('Completada', 'Cancelada');
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Trigger para generar automáticamente citas al crear una serie
CREATE OR REPLACE FUNCTION trigger_generar_citas_serie()
RETURNS TRIGGER AS $$
BEGIN
    -- Generar citas para los próximos 3 meses
    PERFORM generar_citas_desde_serie(NEW.id, CURRENT_DATE + INTERVAL '3 months');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_insert_cita_serie
AFTER INSERT ON cita_series
FOR EACH ROW
WHEN (NEW.activa = TRUE)
EXECUTE FUNCTION trigger_generar_citas_serie();

-- Log de migración
DO $$
BEGIN
    RAISE NOTICE 'Migración 20260112_create_series.sql completada exitosamente';
    RAISE NOTICE 'Creada tabla: cita_series';
    RAISE NOTICE 'Agregada columna: citas.serie_id';
    RAISE NOTICE 'Creada vista: vista_series_activas';
    RAISE NOTICE 'Creadas funciones: generar_citas_desde_serie, desactivar_serie';
    RAISE NOTICE 'Creado trigger: after_insert_cita_serie';
END $$;
