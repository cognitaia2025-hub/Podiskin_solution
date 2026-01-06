-- ============================================================================
-- Archivo: 06_expedientes_medicos.sql
-- Descripción: Tablas para expedientes médicos y consultas
-- ============================================================================

-- Tabla principal de consultas médicas
CREATE TABLE consultas (
    id bigint NOT NULL,
    id_paciente bigint NOT NULL,
    id_podologo bigint NOT NULL,
    id_cita bigint,
    fecha_consulta timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    motivo_consulta text NOT NULL,
    sintomas text,
    exploracion_fisica text,
    plan_tratamiento text,
    indicaciones text,
    observaciones text,
    finalizada boolean DEFAULT false,
    fecha_finalizacion timestamp without time zone,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT consultas_pkey PRIMARY KEY (id)
);

ALTER TABLE consultas ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME consultas_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- Tabla de diagnósticos por consulta
CREATE TABLE diagnosticos (
    id bigint NOT NULL,
    id_consulta bigint NOT NULL,
    id_paciente bigint NOT NULL,
    codigo_cie10 text,
    nombre_diagnostico text NOT NULL,
    tipo_diagnostico text DEFAULT 'Presuntivo'::text,
    descripcion text,
    fecha_diagnostico date NOT NULL DEFAULT CURRENT_DATE,
    activo boolean DEFAULT true,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT diagnosticos_pkey PRIMARY KEY (id),
    CONSTRAINT diagnosticos_tipo_check CHECK ((tipo_diagnostico = ANY (ARRAY['Presuntivo'::text, 'Definitivo'::text])))
);

ALTER TABLE diagnosticos ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME diagnosticos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- Tabla de historial de cambios en expedientes
CREATE TABLE historial_cambios_expediente (
    id bigint NOT NULL,
    id_paciente bigint NOT NULL,
    seccion_modificada text NOT NULL,
    campo_modificado text NOT NULL,
    valor_anterior text,
    valor_nuevo text,
    modificado_por bigint NOT NULL,
    fecha_modificacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    motivo_cambio text,
    CONSTRAINT historial_cambios_expediente_pkey PRIMARY KEY (id)
);

ALTER TABLE historial_cambios_expediente ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME historial_cambios_expediente_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- Vista materializada para resumen de expediente médico
CREATE MATERIALIZED VIEW expedientes_medicos_resumen AS
SELECT 
    p.id as paciente_id,
    p.primer_nombre || ' ' || p.primer_apellido || COALESCE(' ' || p.segundo_apellido, '') as paciente_nombre,
    p.fecha_nacimiento,
    p.sexo,
    p.telefono_principal as telefono,
    p.email,
    p.fecha_registro,
    -- Última consulta
    (SELECT MAX(fecha_consulta) FROM consultas WHERE id_paciente = p.id) as ultima_visita,
    -- Total de consultas
    (SELECT COUNT(*) FROM consultas WHERE id_paciente = p.id AND finalizada = true) as total_consultas,
    -- Alergias activas
    (SELECT COUNT(*) > 0 FROM alergias WHERE id_paciente = p.id AND activo = true) as tiene_alergias,
    -- Último diagnóstico
    (SELECT nombre_diagnostico 
     FROM diagnosticos 
     WHERE id_paciente = p.id AND activo = true 
     ORDER BY fecha_diagnostico DESC 
     LIMIT 1) as diagnostico_reciente,
    -- Última actualización del expediente
    GREATEST(
        p.fecha_modificacion,
        (SELECT MAX(fecha_registro) FROM consultas WHERE id_paciente = p.id),
        (SELECT MAX(fecha_registro) FROM alergias WHERE id_paciente = p.id),
        (SELECT MAX(fecha_actualizacion) FROM estilo_vida WHERE id_paciente = p.id)
    ) as fecha_ultima_actualizacion
FROM pacientes p
WHERE p.activo = true;

-- Índices para mejor performance
CREATE INDEX IF NOT EXISTS idx_consultas_paciente ON consultas USING btree (id_paciente);
CREATE INDEX IF NOT EXISTS idx_consultas_podologo ON consultas USING btree (id_podologo);
CREATE INDEX IF NOT EXISTS idx_consultas_fecha ON consultas USING btree (fecha_consulta DESC);
CREATE INDEX IF NOT EXISTS idx_consultas_finalizada ON consultas USING btree (finalizada, fecha_consulta DESC);

CREATE INDEX IF NOT EXISTS idx_diagnosticos_consulta_paciente ON diagnosticos USING btree (id_paciente);
CREATE INDEX IF NOT EXISTS idx_diagnosticos_consulta ON diagnosticos USING btree (id_consulta);
CREATE INDEX IF NOT EXISTS idx_diagnosticos_consulta_activo ON diagnosticos USING btree (id_paciente, activo);

CREATE INDEX IF NOT EXISTS idx_historial_paciente ON historial_cambios_expediente USING btree (id_paciente, fecha_modificacion DESC);
CREATE INDEX IF NOT EXISTS idx_historial_usuario ON historial_cambios_expediente USING btree (modificado_por);

-- Índice único para refrescar la vista materializada
CREATE UNIQUE INDEX expedientes_medicos_resumen_paciente_id_idx ON expedientes_medicos_resumen (paciente_id);

-- Foreign Keys
ALTER TABLE ONLY consultas ADD CONSTRAINT consultas_id_paciente_fkey FOREIGN KEY (id_paciente) REFERENCES pacientes(id);
ALTER TABLE ONLY consultas ADD CONSTRAINT consultas_id_podologo_fkey FOREIGN KEY (id_podologo) REFERENCES usuarios(id);
ALTER TABLE ONLY consultas ADD CONSTRAINT consultas_id_cita_fkey FOREIGN KEY (id_cita) REFERENCES citas(id);

ALTER TABLE ONLY diagnosticos ADD CONSTRAINT diagnosticos_id_consulta_fkey FOREIGN KEY (id_consulta) REFERENCES consultas(id);
ALTER TABLE ONLY diagnosticos ADD CONSTRAINT diagnosticos_id_paciente_fkey FOREIGN KEY (id_paciente) REFERENCES pacientes(id);

ALTER TABLE ONLY historial_cambios_expediente ADD CONSTRAINT historial_cambios_id_paciente_fkey FOREIGN KEY (id_paciente) REFERENCES pacientes(id);
ALTER TABLE ONLY historial_cambios_expediente ADD CONSTRAINT historial_cambios_modificado_por_fkey FOREIGN KEY (modificado_por) REFERENCES usuarios(id);

-- Función para registrar cambios en historial
CREATE OR REPLACE FUNCTION registrar_cambio_expediente()
RETURNS TRIGGER AS $$
BEGIN
    -- Esta función se puede extender para registrar automáticamente cambios
    -- Por ahora solo retorna NEW
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Función para refrescar vista materializada
CREATE OR REPLACE FUNCTION refrescar_expedientes_resumen()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY expedientes_medicos_resumen;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE consultas IS 'Registro de consultas médicas realizadas';
COMMENT ON TABLE diagnosticos IS 'Diagnósticos asociados a consultas';
COMMENT ON TABLE historial_cambios_expediente IS 'Auditoría de cambios en expedientes médicos';
COMMENT ON MATERIALIZED VIEW expedientes_medicos_resumen IS 'Resumen rápido de expedientes para listados';
