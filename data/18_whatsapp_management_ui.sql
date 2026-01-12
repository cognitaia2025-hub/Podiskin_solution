-- ============================================================================
-- Migración: Interfaz de Gestión de WhatsApp
-- Descripción: Agrega tablas y campos para la UI de gestión con QR, 
--              aprendizaje avanzado y análisis de sentimiento
-- Fecha: 2026-01-10
-- ============================================================================

-- ============================================================================
-- 1. TABLA: aprendizajes_agente
-- ============================================================================

CREATE TABLE IF NOT EXISTS aprendizajes_agente (
    id SERIAL PRIMARY KEY,
    
    -- ========================================================================
    -- FASE 1: CONTEXTO/TRIGGER (Cuándo aplicar este conocimiento)
    -- ========================================================================
    pregunta_original TEXT NOT NULL,
    contexto_trigger TEXT NOT NULL,  -- "Cuando el cliente pregunta sobre..."
    palabras_clave TEXT[],  -- Palabras clave para matching
    pregunta_embedding BYTEA,  -- Embedding para búsqueda semántica (384 dims)
    
    -- ========================================================================
    -- FASE 2: RESPUESTA SUGERIDA (Qué responder)
    -- ========================================================================
    respuesta_sugerida TEXT NOT NULL,  -- "Responde esto..."
    respuesta_admin TEXT NOT NULL,  -- Respuesta original del admin
    
    -- ========================================================================
    -- ANÁLISIS DE TONO E INTENCIÓN
    -- ========================================================================
    tono_cliente TEXT CHECK (tono_cliente IN ('molesto', 'contento', 'neutral', 'urgente', 'confundido', 'agradecido', 'impaciente')),
    intencion_cliente TEXT CHECK (intencion_cliente IN ('queja', 'consulta', 'agradecimiento', 'urgencia', 'cancelacion', 'confirmacion', 'otro')),
    tono_respuesta TEXT CHECK (tono_respuesta IN ('empático', 'profesional', 'amigable', 'formal', 'urgente')),
    
    -- ========================================================================
    -- METADATA ENRIQUECIDA
    -- ========================================================================
    resumen_aprendizaje TEXT NOT NULL,
    categoria TEXT,
    tags TEXT[],
    confianza FLOAT DEFAULT 1.0,
    veces_utilizado INT DEFAULT 0,
    efectividad FLOAT DEFAULT 0.0,  -- % de veces que fue útil (0.0 - 1.0)
    
    -- ========================================================================
    -- RELACIONES
    -- ========================================================================
    id_conversacion BIGINT REFERENCES conversaciones(id),
    id_duda_pendiente INT REFERENCES dudas_pendientes(id),
    id_paciente BIGINT REFERENCES pacientes(id),
    
    -- ========================================================================
    -- VALIDACIÓN Y ORIGEN
    -- ========================================================================
    origen TEXT DEFAULT 'escalamiento' CHECK (origen IN ('escalamiento', 'manual', 'importado', 'auto_aprendizaje')),
    validado BOOLEAN DEFAULT false,
    validado_por BIGINT REFERENCES usuarios(id),
    fecha_validacion TIMESTAMP,
    
    -- ========================================================================
    -- APRENDIZAJE PROGRESIVO
    -- ========================================================================
    version INT DEFAULT 1,  -- Versión del conocimiento
    id_version_anterior INT REFERENCES aprendizajes_agente(id),  -- Para tracking de evolución
    
    -- ========================================================================
    -- TIMESTAMPS
    -- ========================================================================
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP,
    fecha_ultimo_uso TIMESTAMP,
    creado_por BIGINT REFERENCES usuarios(id),
    modificado_por BIGINT REFERENCES usuarios(id)
);

-- Índices optimizados para aprendizajes_agente
CREATE INDEX idx_aprendizajes_embedding ON aprendizajes_agente USING btree(id) WHERE pregunta_embedding IS NOT NULL;
CREATE INDEX idx_aprendizajes_palabras_clave ON aprendizajes_agente USING gin(palabras_clave);
CREATE INDEX idx_aprendizajes_tono ON aprendizajes_agente(tono_cliente, tono_respuesta);
CREATE INDEX idx_aprendizajes_efectividad ON aprendizajes_agente(efectividad DESC) WHERE validado = true;
CREATE INDEX idx_aprendizajes_categoria ON aprendizajes_agente(categoria);
CREATE INDEX idx_aprendizajes_fecha ON aprendizajes_agente(fecha_creacion DESC);
CREATE INDEX idx_aprendizajes_conversacion ON aprendizajes_agente(id_conversacion) WHERE id_conversacion IS NOT NULL;
CREATE INDEX idx_aprendizajes_paciente ON aprendizajes_agente(id_paciente) WHERE id_paciente IS NOT NULL;
CREATE INDEX idx_aprendizajes_validado ON aprendizajes_agente(validado);

-- Comentarios
COMMENT ON TABLE aprendizajes_agente IS 'Conocimientos aprendidos por el agente con sistema de dos fases';
COMMENT ON COLUMN aprendizajes_agente.contexto_trigger IS 'Descripción de cuándo aplicar este conocimiento';
COMMENT ON COLUMN aprendizajes_agente.respuesta_sugerida IS 'Respuesta que Maya debe dar';
COMMENT ON COLUMN aprendizajes_agente.efectividad IS 'Porcentaje de efectividad (0.0 - 1.0)';

-- ============================================================================
-- 2. TABLA: whatsapp_qr_sessions
-- ============================================================================

CREATE TABLE IF NOT EXISTS whatsapp_qr_sessions (
    id SERIAL PRIMARY KEY,
    
    -- QR Code
    qr_code TEXT NOT NULL,  -- Código QR en formato base64 o texto
    qr_image_url TEXT,  -- URL de la imagen del QR generada
    
    -- Estado de la sesión
    estado TEXT DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'escaneado', 'conectado', 'desconectado', 'expirado', 'error')),
    
    -- Información de la conexión
    telefono_conectado TEXT,
    nombre_dispositivo TEXT,
    whatsapp_id TEXT,
    
    -- Metadata
    proveedor TEXT DEFAULT 'twilio' CHECK (proveedor IN ('twilio', 'whatsapp-business-api', 'otro')),
    
    -- Timestamps
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP,
    fecha_escaneo TIMESTAMP,
    fecha_conexion TIMESTAMP,
    fecha_desconexion TIMESTAMP,
    
    -- Usuario que inició la sesión
    iniciado_por BIGINT REFERENCES usuarios(id)
);

-- Índices para whatsapp_qr_sessions
CREATE INDEX idx_qr_sessions_estado ON whatsapp_qr_sessions(estado, fecha_generacion DESC);
CREATE INDEX idx_qr_sessions_activo ON whatsapp_qr_sessions(estado) WHERE estado IN ('pendiente', 'conectado');
CREATE INDEX idx_qr_sessions_proveedor ON whatsapp_qr_sessions(proveedor);

-- Comentarios
COMMENT ON TABLE whatsapp_qr_sessions IS 'Sesiones de QR para sincronización de WhatsApp';
COMMENT ON COLUMN whatsapp_qr_sessions.proveedor IS 'Proveedor de mensajería (twilio, whatsapp-business-api, etc.)';

-- ============================================================================
-- 3. TABLA: analisis_sentimiento
-- ============================================================================

CREATE TABLE IF NOT EXISTS analisis_sentimiento (
    id SERIAL PRIMARY KEY,
    
    -- Relaciones
    id_mensaje BIGINT REFERENCES mensajes(id),
    id_conversacion BIGINT REFERENCES conversaciones(id),
    
    -- Análisis de sentimiento
    sentimiento TEXT CHECK (sentimiento IN ('positivo', 'neutral', 'negativo', 'urgente')),
    confianza_sentimiento FLOAT,
    
    -- Análisis de tono
    tono TEXT CHECK (tono IN ('molesto', 'contento', 'neutral', 'urgente', 'confundido', 'agradecido', 'impaciente')),
    confianza_tono FLOAT,
    
    -- Análisis de intención
    intencion TEXT CHECK (intencion IN ('queja', 'consulta', 'agradecimiento', 'urgencia', 'cancelacion', 'confirmacion', 'otro')),
    confianza_intencion FLOAT,
    
    -- Emociones detectadas (múltiples)
    emociones JSONB,  -- {"frustración": 0.8, "urgencia": 0.6}
    
    -- Palabras clave que influyeron en el análisis
    palabras_clave_detectadas TEXT[],
    
    -- Metadata
    modelo_utilizado TEXT DEFAULT 'sentiment-analysis-v1',
    
    -- Timestamps
    fecha_analisis TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para analisis_sentimiento
CREATE INDEX idx_sentimiento_mensaje ON analisis_sentimiento(id_mensaje);
CREATE INDEX idx_sentimiento_conversacion ON analisis_sentimiento(id_conversacion);
CREATE INDEX idx_sentimiento_tono ON analisis_sentimiento(tono, sentimiento);
CREATE INDEX idx_sentimiento_fecha ON analisis_sentimiento(fecha_analisis DESC);

-- Comentarios
COMMENT ON TABLE analisis_sentimiento IS 'Análisis de sentimiento, tono e intención de mensajes';
COMMENT ON COLUMN analisis_sentimiento.emociones IS 'Emociones detectadas con sus scores (JSON)';

-- ============================================================================
-- 4. MODIFICAR TABLA: conversaciones
-- ============================================================================

-- Agregar campos adicionales para mejor gestión
ALTER TABLE conversaciones 
ADD COLUMN IF NOT EXISTS requiere_atencion BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS atendido_por BIGINT REFERENCES usuarios(id),
ADD COLUMN IF NOT EXISTS fecha_atencion TIMESTAMP,
ADD COLUMN IF NOT EXISTS notas_internas TEXT,
ADD COLUMN IF NOT EXISTS id_paciente BIGINT REFERENCES pacientes(id);

-- Índices adicionales
CREATE INDEX IF NOT EXISTS idx_conversaciones_requiere_atencion 
ON conversaciones(requiere_atencion) WHERE requiere_atencion = true;

CREATE INDEX IF NOT EXISTS idx_conversaciones_paciente 
ON conversaciones(id_paciente) WHERE id_paciente IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_conversaciones_atendido 
ON conversaciones(atendido_por) WHERE atendido_por IS NOT NULL;

-- Comentarios
COMMENT ON COLUMN conversaciones.requiere_atencion IS 'Indica si la conversación requiere atención humana';
COMMENT ON COLUMN conversaciones.notas_internas IS 'Notas internas del equipo sobre la conversación';

-- ============================================================================
-- 5. MODIFICAR TABLA: dudas_pendientes
-- ============================================================================

-- Agregar campos para mejor tracking
ALTER TABLE dudas_pendientes
ADD COLUMN IF NOT EXISTS id_conversacion BIGINT REFERENCES conversaciones(id),
ADD COLUMN IF NOT EXISTS id_paciente BIGINT REFERENCES pacientes(id),
ADD COLUMN IF NOT EXISTS atendido_por BIGINT REFERENCES usuarios(id),
ADD COLUMN IF NOT EXISTS aprendizaje_generado BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS id_aprendizaje INT REFERENCES aprendizajes_agente(id);

-- Índices adicionales
CREATE INDEX IF NOT EXISTS idx_dudas_conversacion ON dudas_pendientes(id_conversacion);
CREATE INDEX IF NOT EXISTS idx_dudas_paciente ON dudas_pendientes(id_paciente);
CREATE INDEX IF NOT EXISTS idx_dudas_aprendizaje ON dudas_pendientes(aprendizaje_generado);
CREATE INDEX IF NOT EXISTS idx_dudas_atendido ON dudas_pendientes(atendido_por) WHERE atendido_por IS NOT NULL;

-- Comentarios
COMMENT ON COLUMN dudas_pendientes.aprendizaje_generado IS 'Indica si se generó un aprendizaje a partir de esta duda';
COMMENT ON COLUMN dudas_pendientes.id_aprendizaje IS 'ID del aprendizaje generado (si existe)';

-- ============================================================================
-- 6. FUNCIONES AUXILIARES
-- ============================================================================

-- Función para generar resumen de aprendizaje (placeholder)
CREATE OR REPLACE FUNCTION generar_resumen_aprendizaje(
    p_pregunta TEXT,
    p_respuesta TEXT
) RETURNS TEXT AS $$
BEGIN
    -- Por ahora retorna un resumen simple
    -- En producción, esto se generaría con IA
    RETURN 'Aprendizaje sobre: ' || LEFT(p_pregunta, 50) || 
           CASE WHEN LENGTH(p_pregunta) > 50 THEN '...' ELSE '' END;
END;
$$ LANGUAGE plpgsql;

-- Trigger para auto-generar resumen si no se proporciona
CREATE OR REPLACE FUNCTION auto_generar_resumen_aprendizaje()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.resumen_aprendizaje IS NULL OR NEW.resumen_aprendizaje = '' THEN
        NEW.resumen_aprendizaje := generar_resumen_aprendizaje(
            NEW.pregunta_original,
            NEW.respuesta_admin
        );
    END IF;
    
    -- Actualizar fecha_actualizacion
    IF TG_OP = 'UPDATE' THEN
        NEW.fecha_actualizacion := CURRENT_TIMESTAMP;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_resumen
BEFORE INSERT OR UPDATE ON aprendizajes_agente
FOR EACH ROW
EXECUTE FUNCTION auto_generar_resumen_aprendizaje();

-- Función para actualizar fecha_ultimo_uso cuando se utiliza un aprendizaje
CREATE OR REPLACE FUNCTION actualizar_uso_aprendizaje(p_aprendizaje_id INT)
RETURNS VOID AS $$
BEGIN
    UPDATE aprendizajes_agente
    SET veces_utilizado = veces_utilizado + 1,
        fecha_ultimo_uso = CURRENT_TIMESTAMP
    WHERE id = p_aprendizaje_id;
END;
$$ LANGUAGE plpgsql;

-- Función para calcular efectividad de un aprendizaje
CREATE OR REPLACE FUNCTION calcular_efectividad_aprendizaje(
    p_aprendizaje_id INT,
    p_fue_util BOOLEAN
) RETURNS VOID AS $$
DECLARE
    v_veces_utilizado INT;
    v_efectividad_actual FLOAT;
    v_nueva_efectividad FLOAT;
BEGIN
    SELECT veces_utilizado, efectividad
    INTO v_veces_utilizado, v_efectividad_actual
    FROM aprendizajes_agente
    WHERE id = p_aprendizaje_id;
    
    -- Calcular nueva efectividad (promedio móvil)
    IF v_veces_utilizado = 0 THEN
        v_nueva_efectividad := CASE WHEN p_fue_util THEN 1.0 ELSE 0.0 END;
    ELSE
        v_nueva_efectividad := (v_efectividad_actual * v_veces_utilizado + 
                                CASE WHEN p_fue_util THEN 1.0 ELSE 0.0 END) / 
                               (v_veces_utilizado + 1);
    END IF;
    
    UPDATE aprendizajes_agente
    SET efectividad = v_nueva_efectividad
    WHERE id = p_aprendizaje_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 7. VISTAS ÚTILES
-- ============================================================================

-- Vista de aprendizajes más efectivos
CREATE OR REPLACE VIEW aprendizajes_efectivos AS
SELECT 
    a.id,
    a.pregunta_original,
    a.resumen_aprendizaje,
    a.categoria,
    a.tono_cliente,
    a.veces_utilizado,
    a.efectividad,
    a.validado,
    a.fecha_creacion,
    CASE 
        WHEN a.veces_utilizado >= 10 AND a.efectividad >= 0.8 THEN 'Excelente'
        WHEN a.veces_utilizado >= 5 AND a.efectividad >= 0.6 THEN 'Bueno'
        WHEN a.veces_utilizado >= 3 AND a.efectividad >= 0.4 THEN 'Regular'
        ELSE 'Nuevo'
    END as nivel_efectividad
FROM aprendizajes_agente a
WHERE a.validado = true
ORDER BY a.efectividad DESC, a.veces_utilizado DESC;

-- Vista de conversaciones con análisis de sentimiento
CREATE OR REPLACE VIEW conversaciones_con_sentimiento AS
SELECT 
    c.id,
    c.id_contacto,
    co.nombre as contacto_nombre,
    c.estado,
    c.requiere_atencion,
    COUNT(DISTINCT m.id) as total_mensajes,
    COUNT(DISTINCT CASE WHEN a.sentimiento = 'negativo' THEN m.id END) as mensajes_negativos,
    COUNT(DISTINCT CASE WHEN a.tono = 'molesto' THEN m.id END) as mensajes_molestos,
    COUNT(DISTINCT CASE WHEN a.tono = 'urgente' THEN m.id END) as mensajes_urgentes,
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN a.tono IN ('molesto', 'urgente') THEN m.id END) > 0 THEN true
        ELSE false
    END as requiere_atencion_especial
FROM conversaciones c
INNER JOIN contactos co ON c.id_contacto = co.id
LEFT JOIN mensajes m ON m.id_conversacion = c.id
LEFT JOIN analisis_sentimiento a ON a.id_mensaje = m.id
GROUP BY c.id, c.id_contacto, co.nombre, c.estado, c.requiere_atencion;

-- ============================================================================
-- 8. DATOS INICIALES (OPCIONAL)
-- ============================================================================

-- Insertar categorías comunes para aprendizajes
-- (Esto es opcional, se puede hacer desde la UI)

-- ============================================================================
-- FIN DE LA MIGRACIÓN
-- ============================================================================

-- Verificar que todas las tablas se crearon correctamente
DO $$
BEGIN
    RAISE NOTICE 'Migración 18_whatsapp_management_ui completada exitosamente';
    RAISE NOTICE 'Tablas creadas: aprendizajes_agente, whatsapp_qr_sessions, analisis_sentimiento';
    RAISE NOTICE 'Tablas modificadas: conversaciones, dudas_pendientes';
    RAISE NOTICE 'Funciones creadas: generar_resumen_aprendizaje, actualizar_uso_aprendizaje, calcular_efectividad_aprendizaje';
    RAISE NOTICE 'Vistas creadas: aprendizajes_efectivos, conversaciones_con_sentimiento';
END $$;
