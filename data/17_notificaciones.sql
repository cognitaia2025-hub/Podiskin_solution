-- ============================================================================
-- Archivo: 17_notificaciones.sql
-- Descripción: Tabla para el sistema de notificaciones en tiempo real
-- ============================================================================

CREATE TABLE IF NOT EXISTS notificaciones (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    usuario_id text NOT NULL, -- Almacena el nombre_usuario (sub del JWT)
    tipo text NOT NULL, -- 'info', 'success', 'warning', 'error', 'cita', etc.
    titulo text NOT NULL,
    mensaje text NOT NULL,
    referencia_id bigint, -- ID opcional de un objeto relacionado (ej: id_cita)
    referencia_tipo text, -- Tipo opcional de objeto relacionado (ej: 'cita')
    fecha_envio timestamp with time zone DEFAULT NOW(),
    leido boolean DEFAULT FALSE,
    fecha_lectura timestamp with time zone
);

CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario_leido ON notificaciones(usuario_id, leido);
CREATE INDEX IF NOT EXISTS idx_notificaciones_fecha_envio ON notificaciones(fecha_envio DESC);
