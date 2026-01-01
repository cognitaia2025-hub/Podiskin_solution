-- ============================================================================
-- Archivo: tablas_core_usuarios.sql
-- Descripción: Tablas de usuarios y podólogos (sin schemas explícitos)
-- Para usar con database.build
-- ============================================================================

-- ============================================================================
-- TABLES
-- ============================================================================

CREATE TABLE usuarios (
    id bigint NOT NULL,
    nombre_usuario text NOT NULL,
    password_hash text NOT NULL,
    nombre_completo text NOT NULL,
    email text NOT NULL,
    id_rol bigint NOT NULL,
    activo boolean DEFAULT true,
    ultimo_login timestamp without time zone,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    creado_por bigint
);

ALTER TABLE usuarios ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME usuarios_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- ============================================================================
-- TABLA: roles
-- Descripción: Catálogo de roles y permisos del sistema
-- ============================================================================

CREATE TABLE roles (
    id bigint NOT NULL,
    nombre_rol text NOT NULL,
    descripcion text,
    permisos jsonb,
    activo boolean DEFAULT true,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE roles ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME roles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- ============================================================================
-- DATOS INICIALES: Roles del sistema
-- ============================================================================

INSERT INTO roles (nombre_rol, descripcion, permisos, activo) VALUES
('Admin', 'Administrador del sistema', '{"all":true}'::jsonb, true),
('Podologo', 'Podólogo con acceso a consultas', '{"pacientes":true,"citas":true,"tratamientos":true,"expedientes":true}'::jsonb, true),
('Recepcionista', 'Recepción y citas', '{"citas":true,"pagos":true,"pacientes":{"leer":true,"crear":true}}'::jsonb, true),
('Asistente', 'Asistente de consultorio', '{"pacientes":{"leer":true},"citas":{"leer":true}}'::jsonb, true);

CREATE TABLE podologos (
    id bigint NOT NULL,
    cedula_profesional text NOT NULL,
    nombre_completo text NOT NULL,
    especialidad text,
    telefono text NOT NULL,
    email text,
    activo boolean DEFAULT true,
    fecha_contratacion date,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id_usuario bigint
);

ALTER TABLE podologos ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME podologos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- ============================================================================
-- CONSTRAINTS
-- ============================================================================

ALTER TABLE ONLY roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);

ALTER TABLE ONLY roles
    ADD CONSTRAINT roles_nombre_rol_key UNIQUE (nombre_rol);

ALTER TABLE ONLY usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);

ALTER TABLE ONLY usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);

ALTER TABLE ONLY usuarios
    ADD CONSTRAINT usuarios_nombre_usuario_key UNIQUE (nombre_usuario);

ALTER TABLE ONLY podologos
    ADD CONSTRAINT podologos_pkey PRIMARY KEY (id);

ALTER TABLE ONLY podologos
    ADD CONSTRAINT podologos_cedula_profesional_key UNIQUE (cedula_profesional);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_roles_activo ON roles USING btree (activo);
CREATE INDEX idx_usuarios_id_rol ON usuarios USING btree (id_rol);
CREATE INDEX idx_usuarios_activo ON usuarios USING btree (activo);
CREATE INDEX idx_usuarios_email ON usuarios USING btree (email);
CREATE INDEX idx_podologos_activo ON podologos USING btree (activo);

-- ============================================================================
-- FOREIGN KEYS
-- ============================================================================

ALTER TABLE ONLY usuarios
    ADD CONSTRAINT usuarios_id_rol_fkey FOREIGN KEY (id_rol) REFERENCES roles(id);

ALTER TABLE ONLY usuarios
    ADD CONSTRAINT usuarios_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES usuarios(id);

ALTER TABLE ONLY podologos
    ADD CONSTRAINT podologos_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES usuarios(id);
