-- =====================================================
-- Migración: Sistema de Recordatorios para Citas
-- Fecha: 2026-01-12
-- Descripción: Crea tabla cita_recordatorios para
--              gestionar recordatorios automáticos
-- =====================================================

-- Crear tabla de recordatorios
CREATE TABLE IF NOT EXISTS cita_recordatorios (
    id BIGSERIAL PRIMARY KEY,
    id_cita BIGINT NOT NULL REFERENCES citas(id) ON DELETE CASCADE,
    tiempo INT NOT NULL CHECK (tiempo > 0),
    unidad VARCHAR(10) NOT NULL CHECK (unidad IN ('minutos', 'horas', 'días')),
    enviado BOOLEAN DEFAULT FALSE,
    fecha_envio TIMESTAMP,
    metodo_envio VARCHAR(20) DEFAULT 'whatsapp' CHECK (metodo_envio IN ('whatsapp', 'email', 'sms')),
    error_envio TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT recordatorio_unico_por_cita UNIQUE (id_cita, tiempo, unidad)
);

-- Índices para rendimiento
CREATE INDEX IF NOT EXISTS idx_recordatorios_cita 
ON cita_recordatorios(id_cita);

CREATE INDEX IF NOT EXISTS idx_recordatorios_pendientes 
ON cita_recordatorios(enviado) 
WHERE enviado = FALSE;

CREATE INDEX IF NOT EXISTS idx_recordatorios_fecha_envio 
ON cita_recordatorios(fecha_envio) 
WHERE fecha_envio IS NOT NULL;

-- Comentarios para documentación
COMMENT ON TABLE cita_recordatorios IS 'Recordatorios configurados para citas médicas';
COMMENT ON COLUMN cita_recordatorios.tiempo IS 'Cantidad de tiempo antes de la cita para enviar el recordatorio';
COMMENT ON COLUMN cita_recordatorios.unidad IS 'Unidad de tiempo: minutos, horas o días';
COMMENT ON COLUMN cita_recordatorios.enviado IS 'Indica si el recordatorio ya fue enviado';
COMMENT ON COLUMN cita_recordatorios.metodo_envio IS 'Canal por el cual se envió el recordatorio';

-- Vista para recordatorios pendientes con información de la cita
CREATE OR REPLACE VIEW vista_recordatorios_pendientes AS
SELECT 
    r.id as id_recordatorio,
    r.id_cita,
    r.tiempo,
    r.unidad,
    r.metodo_envio,
    c.fecha_hora_inicio,
    c.id_paciente,
    c.id_podologo,
    CONCAT_WS(' ', p.primer_nombre, p.segundo_nombre, p.primer_apellido, p.segundo_apellido) as nombre_paciente,
    p.telefono_principal as telefono_paciente,
    p.email as email_paciente,
    pod.nombre_completo as nombre_podologo,
    -- Calcular fecha/hora en que debe enviarse el recordatorio
    CASE 
        WHEN r.unidad = 'minutos' THEN c.fecha_hora_inicio - (r.tiempo || ' minutes')::INTERVAL
        WHEN r.unidad = 'horas' THEN c.fecha_hora_inicio - (r.tiempo || ' hours')::INTERVAL
        WHEN r.unidad = 'días' THEN c.fecha_hora_inicio - (r.tiempo || ' days')::INTERVAL
    END as fecha_hora_envio_programado
FROM cita_recordatorios r
JOIN citas c ON r.id_cita = c.id
JOIN pacientes p ON c.id_paciente = p.id
JOIN podologos pod ON c.id_podologo = pod.id
WHERE r.enviado = FALSE 
  AND c.estado NOT IN ('Cancelada', 'Completada')
ORDER BY c.fecha_hora_inicio;

-- Función para marcar recordatorio como enviado
CREATE OR REPLACE FUNCTION marcar_recordatorio_enviado(
    p_id_recordatorio BIGINT,
    p_metodo VARCHAR(20) DEFAULT NULL,
    p_error TEXT DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE cita_recordatorios 
    SET 
        enviado = TRUE,
        fecha_envio = CURRENT_TIMESTAMP,
        metodo_envio = COALESCE(p_metodo, metodo_envio),
        error_envio = p_error
    WHERE id = p_id_recordatorio;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener recordatorios que deben enviarse ahora
CREATE OR REPLACE FUNCTION obtener_recordatorios_para_enviar(
    p_ventana_minutos INT DEFAULT 5
) RETURNS TABLE (
    id_recordatorio BIGINT,
    id_cita BIGINT,
    nombre_paciente TEXT,
    telefono_paciente VARCHAR,
    email_paciente VARCHAR,
    fecha_hora_cita TIMESTAMP,
    nombre_podologo TEXT,
    metodo_envio VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.id,
        r.id_cita,
        p.nombre_completo,
        p.telefono_principal,
        p.email,
        c.fecha_hora_inicio,
        pod.nombre_completo,
        r.metodo_envio
    FROM cita_recordatorios r
    JOIN citas c ON r.id_cita = c.id
    JOIN pacientes p ON c.id_paciente = p.id
    JOIN podologos pod ON c.id_podologo = pod.id
    WHERE r.enviado = FALSE
      AND c.estado NOT IN ('Cancelada', 'Completada')
      AND (
          CASE 
              WHEN r.unidad = 'minutos' THEN 
                  c.fecha_hora_inicio - (r.tiempo || ' minutes')::INTERVAL
              WHEN r.unidad = 'horas' THEN 
                  c.fecha_hora_inicio - (r.tiempo || ' hours')::INTERVAL
              WHEN r.unidad = 'días' THEN 
                  c.fecha_hora_inicio - (r.tiempo || ' days')::INTERVAL
          END
      ) <= (CURRENT_TIMESTAMP + (p_ventana_minutos || ' minutes')::INTERVAL)
      AND c.fecha_hora_inicio > CURRENT_TIMESTAMP
    ORDER BY c.fecha_hora_inicio;
END;
$$ LANGUAGE plpgsql;

-- Log de migración
DO $$
BEGIN
    RAISE NOTICE 'Migración 20260112_create_recordatorios.sql completada exitosamente';
    RAISE NOTICE 'Creada tabla: cita_recordatorios';
    RAISE NOTICE 'Creada vista: vista_recordatorios_pendientes';
    RAISE NOTICE 'Creadas funciones: marcar_recordatorio_enviado, obtener_recordatorios_para_enviar';
END $$;
