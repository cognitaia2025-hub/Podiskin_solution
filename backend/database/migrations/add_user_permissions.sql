/*
 * Migración: Permisos Granulares por Usuario
 * ==========================================
 * Permite asignar permisos específicos por usuario
 * y permisos de acceso a pacientes específicos
 */

-- Tabla de permisos custom por usuario
CREATE TABLE IF NOT EXISTS user_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    module_name VARCHAR(50) NOT NULL,
    can_read BOOLEAN DEFAULT FALSE,
    can_write BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, module_name)
);

-- Tabla de acceso a pacientes específicos
CREATE TABLE IF NOT EXISTS user_patient_access (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    patient_id INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    access_level VARCHAR(20) DEFAULT 'read', -- 'read', 'write', 'full'
    granted_by INTEGER REFERENCES usuarios(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    notes TEXT,
    
    UNIQUE(user_id, patient_id)
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_user_permissions_user ON user_permissions(user_id);
CREATE INDEX idx_user_permissions_module ON user_permissions(module_name);
CREATE INDEX idx_user_patient_access_user ON user_patient_access(user_id);
CREATE INDEX idx_user_patient_access_patient ON user_patient_access(patient_id);
CREATE INDEX idx_user_patient_access_active ON user_patient_access(user_id, patient_id) 
    WHERE expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP;

-- Trigger para actualizar updated_at
CREATE OR REPLACE FUNCTION update_user_permissions_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_permissions_timestamp
BEFORE UPDATE ON user_permissions
FOR EACH ROW
EXECUTE FUNCTION update_user_permissions_timestamp();

-- Comentarios de documentación
COMMENT ON TABLE user_permissions IS 'Permisos personalizados por usuario para módulos del sistema';
COMMENT ON TABLE user_patient_access IS 'Control de acceso granular a pacientes específicos';
COMMENT ON COLUMN user_patient_access.access_level IS 'read: solo lectura, write: puede editar, full: control total';
