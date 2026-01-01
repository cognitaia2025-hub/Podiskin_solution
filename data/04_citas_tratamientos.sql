-- ============================================================================
-- Archivo: tablas_citas_tratamientos.sql
-- Descripción: Tablas de citas, tratamientos y pagos (sin schemas explícitos)
-- Para usar con database.build
-- ============================================================================

CREATE TABLE tratamientos (
    id bigint NOT NULL,
    codigo_servicio text NOT NULL,
    nombre_servicio text NOT NULL,
    descripcion text,
    precio_base numeric(10,2) NOT NULL,
    duracion_minutos integer DEFAULT 30,
    requiere_consentimiento boolean DEFAULT false,
    activo boolean DEFAULT true,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE tratamientos ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tratamientos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE citas (
    id bigint NOT NULL,
    id_paciente bigint NOT NULL,
    id_podologo bigint NOT NULL,
    fecha_hora_inicio timestamp without time zone NOT NULL,
    fecha_hora_fin timestamp without time zone NOT NULL,
    estado text DEFAULT 'Pendiente'::text,
    motivo_cancelacion text,
    es_primera_vez boolean DEFAULT false,
    tipo_cita text DEFAULT 'Consulta'::text,
    notas_recepcion text,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    creado_por bigint,
    cancelado_por bigint,
    CONSTRAINT citas_estado_check CHECK ((estado = ANY (ARRAY['Pendiente'::text, 'Confirmada'::text, 'En_Curso'::text, 'Completada'::text, 'Cancelada'::text, 'No_Asistio'::text]))),
    CONSTRAINT citas_tipo_cita_check CHECK ((tipo_cita = ANY (ARRAY['Consulta'::text, 'Seguimiento'::text, 'Urgencia'::text])))
);

ALTER TABLE citas ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME citas_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE detalle_cita (
    id bigint NOT NULL,
    id_cita bigint NOT NULL,
    id_tratamiento bigint NOT NULL,
    precio_aplicado numeric(10,2) NOT NULL,
    descuento_porcentaje numeric(5,2) DEFAULT 0,
    precio_final numeric(10,2) NOT NULL,
    notas_tratamiento text,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE detalle_cita ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME detalle_cita_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE evolucion_tratamiento (
    id bigint NOT NULL,
    id_detalle_cita bigint NOT NULL,
    numero_fase integer NOT NULL,
    fecha_fase date NOT NULL,
    descripcion_evolucion text NOT NULL,
    resultado text,
    indicaciones text,
    fecha_proxima_revision date,
    registrado_por bigint NOT NULL,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT evolucion_tratamiento_resultado_check CHECK ((resultado = ANY (ARRAY['Mejoria'::text, 'Sin_Cambios'::text, 'Empeoramiento'::text])))
);

ALTER TABLE evolucion_tratamiento ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME evolucion_tratamiento_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE nota_clinica (
    id bigint NOT NULL,
    id_cita bigint NOT NULL,
    motivo_consulta text NOT NULL,
    padecimiento_actual text,
    exploracion_fisica text,
    diagnostico_presuntivo text,
    diagnostico_definitivo text,
    id_cie10_presuntivo bigint,
    id_cie10_definitivo bigint,
    codigo_cie10_presuntivo_manual text,
    codigo_cie10_definitivo_manual text,
    plan_tratamiento text,
    indicaciones_paciente text,
    pronostico text,
    proxima_cita_sugerida date,
    fecha_elaboracion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    elaborado_por bigint NOT NULL
);

ALTER TABLE nota_clinica ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME nota_clinica_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE consentimientos_informados (
    id bigint NOT NULL,
    id_paciente bigint NOT NULL,
    id_tratamiento bigint,
    id_cita bigint,
    tipo_consentimiento text NOT NULL,
    fecha_firma date NOT NULL,
    firmado_digitalmente boolean DEFAULT false,
    id_archivo_escaneado bigint,
    testigo_1_nombre text,
    testigo_2_nombre text,
    revocado boolean DEFAULT false,
    fecha_revocacion date,
    notas text,
    registrado_por bigint,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE consentimientos_informados ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME consentimientos_informados_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE archivos_multimedia (
    id bigint NOT NULL,
    id_paciente bigint NOT NULL,
    id_cita bigint,
    id_evolucion bigint,
    tipo_archivo text NOT NULL,
    nombre_archivo text NOT NULL,
    url_almacenamiento text NOT NULL,
    mime_type text,
    tamanio_bytes bigint,
    descripcion text,
    fecha_subida timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    subido_por bigint,
    CONSTRAINT archivos_multimedia_tipo_archivo_check CHECK ((tipo_archivo = ANY (ARRAY['Foto_Clinica'::text, 'Radiografia'::text, 'Laboratorio'::text, 'Consentimiento'::text, 'Estudio'::text, 'Receta'::text, 'Otro'::text])))
);

ALTER TABLE archivos_multimedia ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME archivos_multimedia_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE pagos (
    id bigint NOT NULL,
    id_cita bigint NOT NULL,
    fecha_pago timestamp without time zone NOT NULL,
    monto_total numeric(10,2) NOT NULL,
    monto_pagado numeric(10,2) NOT NULL,
    saldo_pendiente numeric(10,2) DEFAULT 0,
    metodo_pago text NOT NULL,
    referencia_pago text,
    factura_solicitada boolean DEFAULT false,
    factura_emitida boolean DEFAULT false,
    rfc_factura text,
    folio_factura text,
    estado_pago text DEFAULT 'Pendiente'::text,
    recibo_por bigint,
    notas text,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pagos_estado_pago_check CHECK ((estado_pago = ANY (ARRAY['Pagado'::text, 'Parcial'::text, 'Pendiente'::text, 'Cancelado'::text]))),
    CONSTRAINT pagos_metodo_pago_check CHECK ((metodo_pago = ANY (ARRAY['Efectivo'::text, 'Tarjeta_Debito'::text, 'Tarjeta_Credito'::text, 'Transferencia'::text, 'Cheque'::text, 'Otro'::text])))
);

ALTER TABLE pagos ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME pagos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- ============================================================================
-- CONSTRAINTS
-- ============================================================================

ALTER TABLE ONLY tratamientos ADD CONSTRAINT tratamientos_pkey PRIMARY KEY (id);
ALTER TABLE ONLY tratamientos ADD CONSTRAINT tratamientos_codigo_servicio_key UNIQUE (codigo_servicio);
ALTER TABLE ONLY citas ADD CONSTRAINT citas_pkey PRIMARY KEY (id);
ALTER TABLE ONLY detalle_cita ADD CONSTRAINT detalle_cita_pkey PRIMARY KEY (id);
ALTER TABLE ONLY evolucion_tratamiento ADD CONSTRAINT evolucion_tratamiento_pkey PRIMARY KEY (id);
ALTER TABLE ONLY evolucion_tratamiento ADD CONSTRAINT uq_detalle_fase UNIQUE (id_detalle_cita, numero_fase);
ALTER TABLE ONLY nota_clinica ADD CONSTRAINT nota_clinica_pkey PRIMARY KEY (id);
ALTER TABLE ONLY nota_clinica ADD CONSTRAINT nota_clinica_id_cita_key UNIQUE (id_cita);
ALTER TABLE ONLY consentimientos_informados ADD CONSTRAINT consentimientos_informados_pkey PRIMARY KEY (id);
ALTER TABLE ONLY archivos_multimedia ADD CONSTRAINT archivos_multimedia_pkey PRIMARY KEY (id);
ALTER TABLE ONLY pagos ADD CONSTRAINT pagos_pkey PRIMARY KEY (id);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_tratamientos_activo ON tratamientos USING btree (activo);
CREATE INDEX idx_citas_paciente ON citas USING btree (id_paciente);
CREATE INDEX idx_citas_fecha_podologo ON citas USING btree (fecha_hora_inicio, id_podologo);
CREATE INDEX idx_citas_estado ON citas USING btree (estado);
CREATE INDEX idx_detalle_cita_tratamiento ON detalle_cita USING btree (id_cita, id_tratamiento);
CREATE INDEX idx_evolucion_detalle ON evolucion_tratamiento USING btree (id_detalle_cita);
CREATE INDEX idx_nota_cita ON nota_clinica USING btree (id_cita);
CREATE INDEX idx_nota_clinica_cie10_presuntivo ON nota_clinica USING btree (id_cie10_presuntivo);
CREATE INDEX idx_nota_clinica_cie10_definitivo ON nota_clinica USING btree (id_cie10_definitivo);
CREATE INDEX idx_consentimientos_paciente ON consentimientos_informados USING btree (id_paciente);
CREATE INDEX idx_archivos_paciente_tipo ON archivos_multimedia USING btree (id_paciente, tipo_archivo);
CREATE INDEX idx_archivos_cita ON archivos_multimedia USING btree (id_cita);
CREATE INDEX idx_pagos_cita ON pagos USING btree (id_cita);
CREATE INDEX idx_pagos_estado ON pagos USING btree (estado_pago);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE TRIGGER trigger_precio_final BEFORE INSERT OR UPDATE ON detalle_cita FOR EACH ROW EXECUTE FUNCTION calcular_precio_final();
CREATE TRIGGER trigger_saldo_pendiente BEFORE INSERT OR UPDATE ON pagos FOR EACH ROW EXECUTE FUNCTION calcular_saldo();
CREATE TRIGGER trigger_vincular_contacto_paciente AFTER INSERT ON citas FOR EACH ROW EXECUTE FUNCTION vincular_contacto_paciente();

-- ============================================================================
-- FOREIGN KEYS
-- ============================================================================

ALTER TABLE ONLY citas ADD CONSTRAINT citas_id_paciente_fkey FOREIGN KEY (id_paciente) REFERENCES pacientes(id);
ALTER TABLE ONLY citas ADD CONSTRAINT citas_id_podologo_fkey FOREIGN KEY (id_podologo) REFERENCES podologos(id);
ALTER TABLE ONLY citas ADD CONSTRAINT citas_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES usuarios(id);
ALTER TABLE ONLY citas ADD CONSTRAINT citas_cancelado_por_fkey FOREIGN KEY (cancelado_por) REFERENCES usuarios(id);
ALTER TABLE ONLY detalle_cita ADD CONSTRAINT detalle_cita_id_cita_fkey FOREIGN KEY (id_cita) REFERENCES citas(id) ON DELETE CASCADE;
ALTER TABLE ONLY detalle_cita ADD CONSTRAINT detalle_cita_id_tratamiento_fkey FOREIGN KEY (id_tratamiento) REFERENCES tratamientos(id);
ALTER TABLE ONLY evolucion_tratamiento ADD CONSTRAINT evolucion_tratamiento_id_detalle_cita_fkey FOREIGN KEY (id_detalle_cita) REFERENCES detalle_cita(id) ON DELETE CASCADE;
ALTER TABLE ONLY evolucion_tratamiento ADD CONSTRAINT evolucion_tratamiento_registrado_por_fkey FOREIGN KEY (registrado_por) REFERENCES podologos(id);
ALTER TABLE ONLY nota_clinica ADD CONSTRAINT nota_clinica_id_cita_fkey FOREIGN KEY (id_cita) REFERENCES citas(id);
ALTER TABLE ONLY nota_clinica ADD CONSTRAINT nota_clinica_elaborado_por_fkey FOREIGN KEY (elaborado_por) REFERENCES podologos(id);
-- Las FK de catalogo_cie10 se agregan al final del archivo, después de crear la tabla
ALTER TABLE ONLY consentimientos_informados ADD CONSTRAINT consentimientos_informados_id_paciente_fkey FOREIGN KEY (id_paciente) REFERENCES pacientes(id);
ALTER TABLE ONLY consentimientos_informados ADD CONSTRAINT consentimientos_informados_id_tratamiento_fkey FOREIGN KEY (id_tratamiento) REFERENCES tratamientos(id);
ALTER TABLE ONLY consentimientos_informados ADD CONSTRAINT consentimientos_informados_id_cita_fkey FOREIGN KEY (id_cita) REFERENCES citas(id);
ALTER TABLE ONLY consentimientos_informados ADD CONSTRAINT consentimientos_informados_id_archivo_escaneado_fkey FOREIGN KEY (id_archivo_escaneado) REFERENCES archivos_multimedia(id);
ALTER TABLE ONLY consentimientos_informados ADD CONSTRAINT consentimientos_informados_registrado_por_fkey FOREIGN KEY (registrado_por) REFERENCES usuarios(id);
ALTER TABLE ONLY archivos_multimedia ADD CONSTRAINT archivos_multimedia_id_paciente_fkey FOREIGN KEY (id_paciente) REFERENCES pacientes(id);
ALTER TABLE ONLY archivos_multimedia ADD CONSTRAINT archivos_multimedia_id_cita_fkey FOREIGN KEY (id_cita) REFERENCES citas(id);
ALTER TABLE ONLY archivos_multimedia ADD CONSTRAINT archivos_multimedia_id_evolucion_fkey FOREIGN KEY (id_evolucion) REFERENCES evolucion_tratamiento(id);
ALTER TABLE ONLY archivos_multimedia ADD CONSTRAINT archivos_multimedia_subido_por_fkey FOREIGN KEY (subido_por) REFERENCES usuarios(id);
ALTER TABLE ONLY pagos ADD CONSTRAINT pagos_id_cita_fkey FOREIGN KEY (id_cita) REFERENCES citas(id);
ALTER TABLE ONLY pagos ADD CONSTRAINT pagos_recibo_por_fkey FOREIGN KEY (recibo_por) REFERENCES usuarios(id);

-- Foreign key from signos_vitales to citas
ALTER TABLE ONLY signos_vitales ADD CONSTRAINT signos_vitales_id_cita_fkey FOREIGN KEY (id_cita) REFERENCES citas(id);

-- ============================================================================
-- TABLA: catalogo_cie10
-- Descripción: Catálogo de códigos CIE-10 para diagnósticos médicos
-- ============================================================================

CREATE TABLE catalogo_cie10 (
    id bigint NOT NULL,
    codigo text NOT NULL,
    descripcion text NOT NULL,
    categoria text,
    subcategoria text,
    activo boolean DEFAULT true,
    notas text,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT catalogo_cie10_codigo_format_check 
        CHECK (codigo ~ '^[A-Z][0-9]{2}(\.[0-9]{1,4})?$')
);

ALTER TABLE catalogo_cie10 ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catalogo_cie10_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- ============================================================================
-- TABLA: diagnosticos_tratamiento
-- Descripción: Diagnósticos específicos por tratamiento (presuntivo, definitivo, diferencial)
-- ============================================================================

CREATE TABLE diagnosticos_tratamiento (
    id bigint NOT NULL,
    id_detalle_cita bigint NOT NULL,
    id_evolucion bigint,
    tipo_diagnostico text NOT NULL,
    descripcion_diagnostico text NOT NULL,
    id_cie10 bigint,
    codigo_cie10_manual text,
    fecha_diagnostico timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    diagnosticado_por bigint NOT NULL,
    notas text,
    activo boolean DEFAULT true,
    CONSTRAINT diagnosticos_tipo_check 
        CHECK (tipo_diagnostico = ANY (ARRAY['Presuntivo'::text, 'Definitivo'::text, 'Diferencial'::text]))
);

ALTER TABLE diagnosticos_tratamiento ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME diagnosticos_tratamiento_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- ============================================================================
-- CONSTRAINTS ADICIONALES
-- ============================================================================

ALTER TABLE ONLY catalogo_cie10 ADD CONSTRAINT catalogo_cie10_pkey PRIMARY KEY (id);
ALTER TABLE ONLY catalogo_cie10 ADD CONSTRAINT catalogo_cie10_codigo_key UNIQUE (codigo);
ALTER TABLE ONLY diagnosticos_tratamiento ADD CONSTRAINT diagnosticos_tratamiento_pkey PRIMARY KEY (id);

-- ============================================================================
-- INDEXES ADICIONALES
-- ============================================================================

CREATE INDEX idx_cie10_codigo ON catalogo_cie10 USING btree (codigo);
CREATE INDEX idx_cie10_descripcion ON catalogo_cie10 USING gin (to_tsvector('spanish', descripcion));
CREATE INDEX idx_cie10_categoria ON catalogo_cie10 USING btree (categoria);
CREATE INDEX idx_cie10_activo ON catalogo_cie10 USING btree (activo);

CREATE INDEX idx_diagnosticos_detalle_cita ON diagnosticos_tratamiento USING btree (id_detalle_cita);
CREATE INDEX idx_diagnosticos_evolucion ON diagnosticos_tratamiento USING btree (id_evolucion);
CREATE INDEX idx_diagnosticos_tipo ON diagnosticos_tratamiento USING btree (tipo_diagnostico);
CREATE INDEX idx_diagnosticos_cie10 ON diagnosticos_tratamiento USING btree (id_cie10);
CREATE INDEX idx_diagnosticos_fecha ON diagnosticos_tratamiento USING btree (fecha_diagnostico DESC);
CREATE INDEX idx_diagnosticos_activo ON diagnosticos_tratamiento USING btree (activo);

-- ============================================================================
-- FOREIGN KEYS ADICIONALES
-- ============================================================================

ALTER TABLE ONLY diagnosticos_tratamiento ADD CONSTRAINT diagnosticos_tratamiento_id_detalle_cita_fkey 
    FOREIGN KEY (id_detalle_cita) REFERENCES detalle_cita(id) ON DELETE CASCADE;
ALTER TABLE ONLY diagnosticos_tratamiento ADD CONSTRAINT diagnosticos_tratamiento_id_evolucion_fkey 
    FOREIGN KEY (id_evolucion) REFERENCES evolucion_tratamiento(id) ON DELETE CASCADE;
ALTER TABLE ONLY diagnosticos_tratamiento ADD CONSTRAINT diagnosticos_tratamiento_id_cie10_fkey 
    FOREIGN KEY (id_cie10) REFERENCES catalogo_cie10(id);
ALTER TABLE ONLY diagnosticos_tratamiento ADD CONSTRAINT diagnosticos_tratamiento_diagnosticado_por_fkey 
    FOREIGN KEY (diagnosticado_por) REFERENCES podologos(id);

-- ============================================================================
-- DATOS INICIALES: Códigos CIE-10 comunes en podología
-- ============================================================================

INSERT INTO catalogo_cie10 (codigo, descripcion, categoria, subcategoria) VALUES
-- Diabetes y complicaciones
('E11', 'Diabetes mellitus tipo 2', 'Enfermedades endocrinas', 'Diabetes'),
('E11.9', 'Diabetes mellitus tipo 2 sin mención de complicación', 'Enfermedades endocrinas', 'Diabetes'),
('E11.621', 'Diabetes mellitus tipo 2 con úlcera cutánea del pie', 'Enfermedades endocrinas', 'Diabetes'),
('E11.622', 'Diabetes mellitus tipo 2 con otra úlcera cutánea', 'Enfermedades endocrinas', 'Diabetes'),
('E11.65', 'Diabetes mellitus tipo 2 con hiperglucemia', 'Enfermedades endocrinas', 'Diabetes'),
('E10', 'Diabetes mellitus tipo 1', 'Enfermedades endocrinas', 'Diabetes'),
('E10.621', 'Diabetes mellitus tipo 1 con úlcera cutánea del pie', 'Enfermedades endocrinas', 'Diabetes'),
-- Infecciones por hongos
('B35.1', 'Tiña de las uñas (Onicomicosis)', 'Infecciones', 'Hongos'),
('B35.3', 'Tiña del pie (Pie de atleta)', 'Infecciones', 'Hongos'),
-- Deformidades del pie
('M20.1', 'Hallux valgus (Juanete)', 'Enfermedades musculoesqueléticas', 'Deformidades'),
('M20.2', 'Hallux rigidus', 'Enfermedades musculoesqueléticas', 'Deformidades'),
('M20.3', 'Otras deformidades del hallux', 'Enfermedades musculoesqueléticas', 'Deformidades'),
('M20.4', 'Otros dedos en martillo', 'Enfermedades musculoesqueléticas', 'Deformidades'),
('M21.6', 'Otras deformidades adquiridas del tobillo y pie', 'Enfermedades musculoesqueléticas', 'Deformidades'),
-- Fascitis y dolor
('M72.2', 'Fascitis plantar', 'Enfermedades musculoesqueléticas', 'Fascitis'),
('M77.3', 'Espolón calcáneo', 'Enfermedades musculoesqueléticas', 'Espolón'),
('M79.3', 'Paniculitis no especificada', 'Enfermedades musculoesqueléticas', 'Dolor'),
-- Uñas
('L60.0', 'Uña encarnada', 'Enfermedades de la piel', 'Uñas'),
('L60.3', 'Onicólisis', 'Enfermedades de la piel', 'Uñas'),
('L60.8', 'Otros trastornos de las uñas', 'Enfermedades de la piel', 'Uñas'),
-- Callosidades y verrugas
('L84', 'Callos y callosidades', 'Enfermedades de la piel', 'Hiperqueratosis'),
('B07', 'Verrugas víricas', 'Infecciones', 'Virus'),
-- Úlceras
('L97', 'Úlcera de miembro inferior, no clasificada en otra parte', 'Enfermedades de la piel', 'Úlceras'),
('L89', 'Úlcera por presión', 'Enfermedades de la piel', 'Úlceras'),
-- Circulación
('I73.9', 'Enfermedad vascular periférica, no especificada', 'Enfermedades circulatorias', 'Vascular'),
('I87.2', 'Insuficiencia venosa (crónica) (periférica)', 'Enfermedades circulatorias', 'Venosa'),
-- Neuropatías
('G57.6', 'Lesión del nervio plantar', 'Enfermedades del sistema nervioso', 'Neuropatía'),
('G62.9', 'Polineuropatía, no especificada', 'Enfermedades del sistema nervioso', 'Neuropatía'),
-- Traumatismos
('S93.4', 'Esguince y torcedura del tobillo', 'Traumatismos', 'Tobillo'),
('S92.9', 'Fractura del pie, parte no especificada', 'Traumatismos', 'Pie'),
-- Otros
('M25.57', 'Dolor en articulación del tobillo y pie', 'Enfermedades musculoesqueléticas', 'Dolor articular'),
('R60.0', 'Edema localizado', 'Síntomas y signos', 'Edema');

-- ============================================================================
-- FOREIGN KEYS para catalogo_cie10 (añadidas aquí porque la tabla ya existe)
-- ============================================================================

ALTER TABLE ONLY nota_clinica ADD CONSTRAINT nota_clinica_id_cie10_presuntivo_fkey FOREIGN KEY (id_cie10_presuntivo) REFERENCES catalogo_cie10(id);
ALTER TABLE ONLY nota_clinica ADD CONSTRAINT nota_clinica_id_cie10_definitivo_fkey FOREIGN KEY (id_cie10_definitivo) REFERENCES catalogo_cie10(id);
