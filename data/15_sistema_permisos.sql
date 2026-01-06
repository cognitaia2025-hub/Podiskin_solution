-- ============================================================================
-- Archivo: 15_sistema_permisos.sql
-- Descripción: Sistema de permisos granular y auditoría
-- Dependencias: 02_usuarios.sql
-- Fecha: 05/01/2026
-- ============================================================================

-- ============================================================================
-- TABLA: permisos_usuarios
-- Descripción: Almacena permisos granulares por usuario en formato JSONB
-- ============================================================================

CREATE TABLE permisos_usuarios (
    id bigint NOT NULL,
    id_usuario bigint NOT NULL UNIQUE,
    permisos jsonb NOT NULL DEFAULT '{}'::jsonb,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    actualizado_por bigint
);

ALTER TABLE permisos_usuarios ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME permisos_usuarios_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- ============================================================================
-- TABLA: auditoria
-- Descripción: Registro de todas las acciones sensibles en el sistema
-- ============================================================================

CREATE TABLE auditoria (
    id bigint NOT NULL,
    usuario_id bigint NOT NULL,
    accion text NOT NULL,
    modulo text NOT NULL,
    descripcion text NOT NULL,
    datos_anteriores jsonb,
    datos_nuevos jsonb,
    ip_address text,
    fecha_hora timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE auditoria ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME auditoria_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- ============================================================================
-- CONSTRAINTS
-- ============================================================================

ALTER TABLE ONLY permisos_usuarios
    ADD CONSTRAINT permisos_usuarios_pkey PRIMARY KEY (id);

ALTER TABLE ONLY auditoria
    ADD CONSTRAINT auditoria_pkey PRIMARY KEY (id);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_permisos_usuario ON permisos_usuarios USING btree (id_usuario);
CREATE INDEX idx_auditoria_usuario ON auditoria USING btree (usuario_id);
CREATE INDEX idx_auditoria_modulo ON auditoria USING btree (modulo);
CREATE INDEX idx_auditoria_fecha ON auditoria USING btree (fecha_hora DESC);
CREATE INDEX idx_auditoria_accion ON auditoria USING btree (accion);

-- ============================================================================
-- FOREIGN KEYS
-- ============================================================================

ALTER TABLE ONLY permisos_usuarios
    ADD CONSTRAINT permisos_usuarios_id_usuario_fkey 
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE;

ALTER TABLE ONLY permisos_usuarios
    ADD CONSTRAINT permisos_usuarios_actualizado_por_fkey 
    FOREIGN KEY (actualizado_por) REFERENCES usuarios(id);

ALTER TABLE ONLY auditoria
    ADD CONSTRAINT auditoria_usuario_id_fkey 
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id);

-- ============================================================================
-- FUNCIÓN: Actualizar timestamp en permisos_usuarios
-- ============================================================================

CREATE OR REPLACE FUNCTION actualizar_timestamp_permisos()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_timestamp_permisos
    BEFORE UPDATE ON permisos_usuarios
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_timestamp_permisos();

-- ============================================================================
-- INSERTAR PERMISOS DEFAULT PARA USUARIOS EXISTENTES
-- ============================================================================

-- Plantilla de permisos completos (Admin)
INSERT INTO permisos_usuarios (id_usuario, permisos)
SELECT 
    id,
    '{
        "calendario": {"read": true, "write": true},
        "pacientes": {"read": true, "write": true},
        "cobros": {"read": true, "write": true},
        "expedientes": {"read": true, "write": true},
        "inventario": {"read": true, "write": true},
        "gastos": {"read": true, "write": true},
        "cortes_caja": {"read": true, "write": true},
        "administracion": {"read": true, "write": true}
    }'::jsonb
FROM usuarios
WHERE NOT EXISTS (
    SELECT 1 FROM permisos_usuarios WHERE id_usuario = usuarios.id
);

-- ============================================================================
-- COMENTARIOS
-- ============================================================================

COMMENT ON TABLE permisos_usuarios IS 'Almacena permisos granulares por usuario';
COMMENT ON TABLE auditoria IS 'Registro de auditoría de acciones del sistema';
COMMENT ON COLUMN permisos_usuarios.permisos IS 'JSONB con estructura: {"modulo": {"read": bool, "write": bool}}';
COMMENT ON COLUMN auditoria.datos_anteriores IS 'Estado anterior del registro (JSON)';
COMMENT ON COLUMN auditoria.datos_nuevos IS 'Estado nuevo del registro (JSON)';
