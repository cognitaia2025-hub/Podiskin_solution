-- Tabla para gestionar dudas escaladas a administrador
DROP TABLE IF EXISTS dudas_pendientes CASCADE;

CREATE TABLE dudas_pendientes (
    id SERIAL PRIMARY KEY,
    paciente_chat_id TEXT NOT NULL,
    paciente_nombre TEXT,
    paciente_telefono TEXT,
    duda TEXT NOT NULL,
    contexto TEXT,
    estado TEXT DEFAULT 'pendiente',
    respuesta_admin TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_respuesta TIMESTAMP,
    fecha_expiracion TIMESTAMP,
    admin_chat_id TEXT
);

CREATE INDEX idx_dudas_estado ON dudas_pendientes(estado);
CREATE INDEX idx_dudas_paciente ON dudas_pendientes(paciente_chat_id);
