-- ============================================================================
-- Migración: Complemento para Control de WhatsApp.js
-- Descripción: Agrega tablas para contactos especiales, configuración y grupos
-- Fecha: 2026-01-10
-- Nota: Complementa la migración 18_whatsapp_management_ui.sql
-- ============================================================================

-- ============================================================================
-- 1. TABLA: whatsapp_config
-- ============================================================================

CREATE TABLE IF NOT EXISTS whatsapp_config (
    id SERIAL PRIMARY KEY,
    
    -- Administración
    telefono_admin VARCHAR(20) NOT NULL,
    telefonos_respaldo TEXT[], -- Array de teléfonos de respaldo
    
    -- Estado del servicio
    estado VARCHAR(20) DEFAULT 'stopped' CHECK (estado IN ('stopped', 'starting', 'running', 'error')),
    
    -- Control de grupos
    grupos_activos BOOLEAN DEFAULT true,
    
    -- Sesión actual
    session_id VARCHAR(100),
    ultima_sesion_qr_id INTEGER REFERENCES whatsapp_qr_sessions(id),
    
    -- Timestamps
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultimo_inicio TIMESTAMP,
    fecha_ultimo_paro TIMESTAMP,
    
    -- Usuario que configuró
    configurado_por BIGINT REFERENCES usuarios(id)
);

-- Solo debe haber una configuración activa
CREATE UNIQUE INDEX idx_whatsapp_config_singleton ON whatsapp_config ((id IS NOT NULL));

COMMENT ON TABLE whatsapp_config IS 'Configuración global del servicio WhatsApp';
COMMENT ON COLUMN whatsapp_config.telefonos_respaldo IS 'Teléfonos de respaldo para notificaciones';

-- ============================================================================
-- 2. TABLA: whatsapp_contactos_especiales
-- ============================================================================

CREATE TABLE IF NOT EXISTS whatsapp_contactos_especiales (
    id SERIAL PRIMARY KEY,
    
    -- Identificación
    telefono VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    
    -- Clasificación
    etiqueta VARCHAR(50) CHECK (etiqueta IN ('proveedor', 'familiar', 'emergencia', 'vip', 'bloqueado', 'otro')),
    descripcion TEXT,
    
    -- Comportamiento del agente
    comportamiento VARCHAR(20) DEFAULT 'normal' CHECK (comportamiento IN ('normal', 'no_responder', 'prioritario', 'solo_humano')),
    
    -- Contexto para IA
    contexto_ia TEXT, -- "Este es el proveedor de insumos médicos..."
    
    -- Notificaciones
    notificar_admin BOOLEAN DEFAULT false, -- Si debe notificar al admin cada mensaje
    
    -- Estado
    activo BOOLEAN DEFAULT true,
    
    -- Timestamps
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Usuario que lo agregó
    creado_por BIGINT REFERENCES usuarios(id)
);

-- Índices
CREATE INDEX idx_contactos_especiales_telefono ON whatsapp_contactos_especiales(telefono);
CREATE INDEX idx_contactos_especiales_comportamiento ON whatsapp_contactos_especiales(comportamiento);
CREATE INDEX idx_contactos_especiales_etiqueta ON whatsapp_contactos_especiales(etiqueta);
CREATE INDEX idx_contactos_especiales_activo ON whatsapp_contactos_especiales(activo) WHERE activo = true;

COMMENT ON TABLE whatsapp_contactos_especiales IS 'Contactos con comportamiento especial del agente';
COMMENT ON COLUMN whatsapp_contactos_especiales.comportamiento IS 'normal: agente normal, no_responder: ignorar, prioritario: alta prioridad, solo_humano: siempre escalar';
COMMENT ON COLUMN whatsapp_contactos_especiales.contexto_ia IS 'Contexto adicional para que el agente personalice respuestas';

-- ============================================================================
-- 3. TABLA: whatsapp_grupos
-- ============================================================================

CREATE TABLE IF NOT EXISTS whatsapp_grupos (
    id SERIAL PRIMARY KEY,
    
    -- Identificación del grupo
    group_id VARCHAR(100) NOT NULL UNIQUE, -- ID de WhatsApp del grupo
    nombre VARCHAR(100),
    descripcion TEXT,
    
    -- Control del bot
    bot_activo BOOLEAN DEFAULT false,
    
    -- Comportamiento
    modo VARCHAR(20) DEFAULT 'observador' CHECK (modo IN ('observador', 'participante', 'moderador', 'desactivado')),
    
    -- Configuración
    responder_menciones BOOLEAN DEFAULT true, -- Solo responder si mencionan al bot
    palabras_clave_activacion TEXT[], -- Palabras que activan al bot
    
    -- Timestamps
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultimo_mensaje TIMESTAMP,
    
    -- Usuario que lo configuró
    configurado_por BIGINT REFERENCES usuarios(id)
);

-- Índices
CREATE INDEX idx_whatsapp_grupos_id ON whatsapp_grupos(group_id);
CREATE INDEX idx_whatsapp_grupos_activo ON whatsapp_grupos(bot_activo) WHERE bot_activo = true;
CREATE INDEX idx_whatsapp_grupos_modo ON whatsapp_grupos(modo);

COMMENT ON TABLE whatsapp_grupos IS 'Configuración de grupos de WhatsApp';
COMMENT ON COLUMN whatsapp_grupos.modo IS 'observador: solo lee, participante: responde, moderador: gestiona grupo, desactivado: ignora';

-- ============================================================================
-- 4. TABLA: whatsapp_control_logs
-- ============================================================================

CREATE TABLE IF NOT EXISTS whatsapp_control_logs (
    id SERIAL PRIMARY KEY,
    
    -- Acción realizada
    accion VARCHAR(50) NOT NULL CHECK (accion IN (
        'start', 'stop', 'emergency_stop', 'restart',
        'qr_generated', 'qr_scanned', 'connected', 'disconnected',
        'config_updated', 'contact_added', 'group_configured'
    )),
    
    -- Detalles
    detalles JSONB,
    mensaje TEXT,
    
    -- Usuario que ejecutó la acción
    usuario_id BIGINT REFERENCES usuarios(id),
    
    -- Timestamp
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_control_logs_accion ON whatsapp_control_logs(accion);
CREATE INDEX idx_control_logs_fecha ON whatsapp_control_logs(fecha DESC);
CREATE INDEX idx_control_logs_usuario ON whatsapp_control_logs(usuario_id);

COMMENT ON TABLE whatsapp_control_logs IS 'Registro de acciones de control del servicio WhatsApp';

-- ============================================================================
-- 5. FUNCIONES AUXILIARES
-- ============================================================================

-- Función para registrar acción de control
CREATE OR REPLACE FUNCTION registrar_accion_control(
    p_accion VARCHAR(50),
    p_usuario_id BIGINT,
    p_detalles JSONB DEFAULT NULL,
    p_mensaje TEXT DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    v_log_id INTEGER;
BEGIN
    INSERT INTO whatsapp_control_logs (accion, usuario_id, detalles, mensaje)
    VALUES (p_accion, p_usuario_id, p_detalles, p_mensaje)
    RETURNING id INTO v_log_id;
    
    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener configuración activa
CREATE OR REPLACE FUNCTION get_whatsapp_config()
RETURNS TABLE (
    telefono_admin VARCHAR(20),
    telefonos_respaldo TEXT[],
    estado VARCHAR(20),
    grupos_activos BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        wc.telefono_admin,
        wc.telefonos_respaldo,
        wc.estado,
        wc.grupos_activos
    FROM whatsapp_config wc
    ORDER BY wc.id DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Función para verificar si un contacto es especial
CREATE OR REPLACE FUNCTION get_contacto_comportamiento(p_telefono VARCHAR(20))
RETURNS VARCHAR(20) AS $$
DECLARE
    v_comportamiento VARCHAR(20);
BEGIN
    SELECT comportamiento INTO v_comportamiento
    FROM whatsapp_contactos_especiales
    WHERE telefono = p_telefono AND activo = true
    LIMIT 1;
    
    RETURN COALESCE(v_comportamiento, 'normal');
END;
$$ LANGUAGE plpgsql;

-- Función para verificar si un grupo tiene bot activo
CREATE OR REPLACE FUNCTION is_grupo_bot_activo(p_group_id VARCHAR(100))
RETURNS BOOLEAN AS $$
DECLARE
    v_activo BOOLEAN;
BEGIN
    SELECT bot_activo INTO v_activo
    FROM whatsapp_grupos
    WHERE group_id = p_group_id
    LIMIT 1;
    
    RETURN COALESCE(v_activo, false);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 6. TRIGGERS
-- ============================================================================

-- Trigger para actualizar fecha_actualizacion en whatsapp_config
CREATE OR REPLACE FUNCTION update_whatsapp_config_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_whatsapp_config
BEFORE UPDATE ON whatsapp_config
FOR EACH ROW
EXECUTE FUNCTION update_whatsapp_config_timestamp();

-- Trigger similar para contactos especiales
CREATE TRIGGER trigger_update_contactos_especiales
BEFORE UPDATE ON whatsapp_contactos_especiales
FOR EACH ROW
EXECUTE FUNCTION update_whatsapp_config_timestamp();

-- Trigger similar para grupos
CREATE TRIGGER trigger_update_whatsapp_grupos
BEFORE UPDATE ON whatsapp_grupos
FOR EACH ROW
EXECUTE FUNCTION update_whatsapp_config_timestamp();

-- ============================================================================
-- 7. DATOS INICIALES
-- ============================================================================

-- Insertar configuración por defecto (solo si no existe)
INSERT INTO whatsapp_config (telefono_admin, telefonos_respaldo, estado, grupos_activos)
SELECT '', ARRAY[]::TEXT[], 'stopped', true
WHERE NOT EXISTS (SELECT 1 FROM whatsapp_config);

-- ============================================================================
-- FIN DE LA MIGRACIÓN
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Migración 19_whatsapp_control completada exitosamente';
    RAISE NOTICE 'Tablas creadas: whatsapp_config, whatsapp_contactos_especiales, whatsapp_grupos, whatsapp_control_logs';
    RAISE NOTICE 'Funciones creadas: registrar_accion_control, get_whatsapp_config, get_contacto_comportamiento, is_grupo_bot_activo';
END $$;
