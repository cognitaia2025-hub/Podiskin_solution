-- ============================================================================
-- Archivo: tablas_pacientes.sql
-- Descripción: Tablas de gestión de pacientes (sin schemas explícitos)
-- Para usar con database.build
-- ============================================================================

CREATE TABLE pacientes (
    id bigint NOT NULL,
    primer_nombre text NOT NULL,
    segundo_nombre text,
    primer_apellido text NOT NULL,
    segundo_apellido text,
    sexo text NOT NULL,
    fecha_nacimiento date NOT NULL,
    curp text,
    estado_civil text,
    telefono_principal text NOT NULL,
    telefono_secundario text,
    email text,
    calle text,
    numero_exterior text,
    numero_interior text,
    colonia text,
    ciudad text,
    estado text,
    cp text,
    escolaridad text,
    ocupacion text,
    religion text,
    referencia_como_nos_conocio text,
    activo boolean DEFAULT true,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    creado_por bigint,
    modificado_por bigint,
    fecha_modificacion timestamp without time zone,
    CONSTRAINT pacientes_sexo_check CHECK ((sexo = ANY (ARRAY['M'::text, 'F'::text, 'O'::text])))
);

ALTER TABLE pacientes ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME pacientes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE alergias (
    id bigint NOT NULL,
    id_paciente bigint NOT NULL,
    tipo_alergeno text NOT NULL,
    nombre_alergeno text NOT NULL,
    reaccion text,
    severidad text DEFAULT 'Leve'::text,
    fecha_diagnostico date,
    activo boolean DEFAULT true,
    notas text,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT alergias_severidad_check CHECK ((severidad = ANY (ARRAY['Leve'::text, 'Moderada'::text, 'Grave'::text, 'Mortal'::text]))),
    CONSTRAINT alergias_tipo_alergeno_check CHECK ((tipo_alergeno = ANY (ARRAY['Medicamento'::text, 'Alimento'::text, 'Ambiental'::text, 'Material'::text, 'Otro'::text])))
);

ALTER TABLE alergias ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME alergias_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE antecedentes_medicos (
    id bigint NOT NULL,
    id_paciente bigint NOT NULL,
    tipo_categoria text NOT NULL,
    nombre_enfermedad text NOT NULL,
    parentesco text,
    fecha_inicio date,
    descripcion_temporal text,
    tratamiento_actual text,
    controlado boolean,
    activo boolean DEFAULT true,
    notas text,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT antecedentes_medicos_tipo_categoria_check CHECK ((tipo_categoria = ANY (ARRAY['Heredofamiliar'::text, 'Patologico'::text, 'Quirurgico'::text, 'Traumatico'::text, 'Transfusional'::text])))
);

ALTER TABLE antecedentes_medicos ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME antecedentes_medicos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE estilo_vida (
    id bigint NOT NULL,
    id_paciente bigint NOT NULL,
    tipo_dieta text,
    descripcion_dieta text,
    ejercicio_frecuencia text,
    tipo_ejercicio text,
    tabaquismo boolean DEFAULT false,
    tabaco_cigarros_dia integer,
    tabaco_anios integer,
    alcoholismo boolean DEFAULT false,
    alcohol_frecuencia text,
    drogas boolean DEFAULT false,
    drogas_tipo text,
    inmunizaciones_completas boolean,
    esquema_vacunacion text,
    higiene_sueno_horas numeric(3,1),
    exposicion_toxicos text,
    suplementos_vitaminas text,
    notas text,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion timestamp without time zone,
    CONSTRAINT estilo_vida_tipo_dieta_check CHECK ((tipo_dieta = ANY (ARRAY['Normal'::text, 'Vegetariana'::text, 'Vegana'::text, 'Keto'::text, 'Diabetica'::text, 'Otro'::text])))
);

ALTER TABLE estilo_vida ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME estilo_vida_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE historia_ginecologica (
    id bigint NOT NULL,
    id_paciente bigint NOT NULL,
    menarca_edad integer,
    ritmo_menstrual_dias text,
    fecha_ultima_menstruacion date,
    gestaciones integer DEFAULT 0,
    partos integer DEFAULT 0,
    cesareas integer DEFAULT 0,
    abortos integer DEFAULT 0,
    metodo_anticonceptivo text,
    menopausia boolean DEFAULT false,
    fecha_menopausia date,
    notas_adicionales text,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modificado_por bigint,
    fecha_modificacion timestamp without time zone
);

ALTER TABLE historia_ginecologica ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME historia_ginecologica_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE signos_vitales (
    id bigint NOT NULL,
    id_paciente bigint NOT NULL,
    id_cita bigint,
    fecha_registro timestamp without time zone NOT NULL,
    peso_kg numeric(5,2),
    talla_cm numeric(5,2),
    imc numeric(4,2),
    ta_sistolica integer,
    ta_diastolica integer,
    frecuencia_cardiaca integer,
    frecuencia_respiratoria integer,
    temperatura_c numeric(4,2),
    saturacion_o2 integer,
    glucosa_capilar integer,
    registrado_por bigint
);

ALTER TABLE signos_vitales ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME signos_vitales_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- ============================================================================
-- CONSTRAINTS
-- ============================================================================

ALTER TABLE ONLY pacientes ADD CONSTRAINT pacientes_pkey PRIMARY KEY (id);
ALTER TABLE ONLY pacientes ADD CONSTRAINT pacientes_curp_key UNIQUE (curp);
ALTER TABLE ONLY alergias ADD CONSTRAINT alergias_pkey PRIMARY KEY (id);
ALTER TABLE ONLY antecedentes_medicos ADD CONSTRAINT antecedentes_medicos_pkey PRIMARY KEY (id);
ALTER TABLE ONLY estilo_vida ADD CONSTRAINT estilo_vida_pkey PRIMARY KEY (id);
ALTER TABLE ONLY estilo_vida ADD CONSTRAINT estilo_vida_id_paciente_key UNIQUE (id_paciente);
ALTER TABLE ONLY historia_ginecologica ADD CONSTRAINT historia_ginecologica_pkey PRIMARY KEY (id);
ALTER TABLE ONLY historia_ginecologica ADD CONSTRAINT historia_ginecologica_id_paciente_key UNIQUE (id_paciente);
ALTER TABLE ONLY signos_vitales ADD CONSTRAINT signos_vitales_pkey PRIMARY KEY (id);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_pacientes_activo ON pacientes USING btree (activo);
CREATE INDEX idx_pacientes_curp ON pacientes USING btree (curp);
CREATE INDEX idx_pacientes_nombre ON pacientes USING btree (primer_apellido, segundo_apellido, primer_nombre);
CREATE INDEX idx_alergias_paciente ON alergias USING btree (id_paciente);
CREATE INDEX idx_alergias_activo ON alergias USING btree (id_paciente, activo);
CREATE INDEX idx_antecedentes_paciente ON antecedentes_medicos USING btree (id_paciente);
CREATE INDEX idx_signos_paciente_fecha ON signos_vitales USING btree (id_paciente, fecha_registro DESC);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE TRIGGER trigger_calcular_imc BEFORE INSERT OR UPDATE ON signos_vitales FOR EACH ROW EXECUTE FUNCTION calcular_imc();

-- ============================================================================
-- FOREIGN KEYS
-- ============================================================================

ALTER TABLE ONLY pacientes ADD CONSTRAINT pacientes_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES usuarios(id);
ALTER TABLE ONLY pacientes ADD CONSTRAINT pacientes_modificado_por_fkey FOREIGN KEY (modificado_por) REFERENCES usuarios(id);
ALTER TABLE ONLY alergias ADD CONSTRAINT alergias_id_paciente_fkey FOREIGN KEY (id_paciente) REFERENCES pacientes(id);
ALTER TABLE ONLY antecedentes_medicos ADD CONSTRAINT antecedentes_medicos_id_paciente_fkey FOREIGN KEY (id_paciente) REFERENCES pacientes(id);
ALTER TABLE ONLY estilo_vida ADD CONSTRAINT estilo_vida_id_paciente_fkey FOREIGN KEY (id_paciente) REFERENCES pacientes(id);
ALTER TABLE ONLY historia_ginecologica ADD CONSTRAINT historia_ginecologica_id_paciente_fkey FOREIGN KEY (id_paciente) REFERENCES pacientes(id);
ALTER TABLE ONLY historia_ginecologica ADD CONSTRAINT historia_ginecologica_modificado_por_fkey FOREIGN KEY (modificado_por) REFERENCES usuarios(id);
ALTER TABLE ONLY signos_vitales ADD CONSTRAINT signos_vitales_id_paciente_fkey FOREIGN KEY (id_paciente) REFERENCES pacientes(id);
ALTER TABLE ONLY signos_vitales ADD CONSTRAINT signos_vitales_registrado_por_fkey FOREIGN KEY (registrado_por) REFERENCES usuarios(id);
