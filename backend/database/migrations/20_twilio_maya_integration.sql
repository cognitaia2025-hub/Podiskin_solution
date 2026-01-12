-- ============================================================================
-- MIGRACIÓN: Integración Twilio + Maya Optimizado
-- Fecha: 2026-01-12
-- Descripción: Tablas para separación de datos vectoriales y Twilio
-- ============================================================================

BEGIN;

-- ============================================================================
-- TABLA 1: conversaciones_embeddings (Contexto por paciente - AISLADO)
-- ============================================================================

CREATE TABLE IF NOT EXISTS conversaciones_embeddings (
    id SERIAL PRIMARY KEY,
    
    -- 🔑 AISLAMIENTO POR PACIENTE (thread-scoped)
    id_contacto BIGINT NOT NULL REFERENCES contactos(id) ON DELETE CASCADE,
    id_conversacion BIGINT NOT NULL REFERENCES conversaciones(id) ON DELETE CASCADE,
    
    -- Resumen de la conversación
    resumen_conversacion TEXT NOT NULL,
    
    -- Embedding del resumen (384 dims, all-MiniLM-L6-v2)
    embedding BYTEA NOT NULL,
    
    -- Metadata estructurada (JSON)
    metadata JSONB DEFAULT '{}'::jsonb,
    /* Estructura recomendada:
    {
        "topicos": ["cita_agendada", "consulta_precio"],
        "fecha_conversacion": "2026-01-12",
        "duracion_minutos": 5,
        "resuelto": true,
        "tipo_consulta": "agendar_cita",
        "sentimiento": "positivo"
    }
    */
    
    -- Timestamps
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_ultima_consulta TIMESTAMP,
    
    -- Constraint: Una conversación = un embedding
    UNIQUE(id_conversacion)
);

-- ✅ ÍNDICE CRÍTICO: Buscar SOLO conversaciones de un contacto
CREATE INDEX idx_conv_embeddings_contacto 
ON conversaciones_embeddings(id_contacto);

CREATE INDEX idx_conv_embeddings_fecha 
ON conversaciones_embeddings(fecha_creacion DESC);

CREATE INDEX idx_conv_embeddings_metadata 
ON conversaciones_embeddings USING gin(metadata);

COMMENT ON TABLE conversaciones_embeddings IS 
'Contexto conversacional aislado POR PACIENTE. NO compartido entre contactos';

COMMENT ON COLUMN conversaciones_embeddings.id_contacto IS 
'CRÍTICO: Filtro para aislar conversaciones por paciente (thread-scoped memory)';

-- ============================================================================
-- TABLA 2: knowledge_base_validated (KB Compartida - Sin datos operativos)
-- ============================================================================

CREATE TABLE IF NOT EXISTS knowledge_base_validated (
    id SERIAL PRIMARY KEY,
    
    -- Pregunta y respuesta
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    
    -- Embedding de la pregunta (384 dims)
    pregunta_embedding BYTEA NOT NULL,
    
    -- Categorización
    categoria TEXT NOT NULL CHECK (categoria IN (
        'FAQ_Proceso',           -- "¿Cómo agendar una cita?"
        'Politica_Clinica',      -- "¿Puedo cancelar?"
        'Informacion_General',   -- "¿Dónde están ubicados?"
        'Procedimiento_Medico',  -- "¿Duele el tratamiento X?"
        'Regla_Comportamiento'   -- Cómo responder en situaciones
    )),
    
    -- ⚠️ RESTRICCIÓN: NO contiene precios, horarios ni servicios
    contiene_datos_operativos BOOLEAN DEFAULT false 
        CHECK (contiene_datos_operativos = false),
    
    -- Aprobación y origen
    aprobado BOOLEAN DEFAULT false,
    origen TEXT CHECK (origen IN (
        'admin_manual',          -- Agregado manualmente
        'escalamiento_aprendido', -- Aprendido de escalamiento
        'importado'              -- Importado desde otra fuente
    )),
    
    -- Métricas de uso
    veces_consultada INT DEFAULT 0,
    efectividad_score FLOAT DEFAULT 1.0 CHECK (efectividad_score BETWEEN 0.0 AND 1.0),
    feedback_positivo INT DEFAULT 0,
    feedback_negativo INT DEFAULT 0,
    
    -- Timestamps
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP,
    fecha_aprobacion TIMESTAMP,
    aprobado_por BIGINT REFERENCES usuarios(id),
    fecha_ultimo_uso TIMESTAMP
);

-- Índices optimizados
CREATE INDEX idx_kb_validated_categoria 
ON knowledge_base_validated(categoria) 
WHERE aprobado = true;

CREATE INDEX idx_kb_validated_aprobado 
ON knowledge_base_validated(aprobado, efectividad_score DESC) 
WHERE aprobado = true;

CREATE INDEX idx_kb_validated_fecha 
ON knowledge_base_validated(fecha_creacion DESC);

COMMENT ON TABLE knowledge_base_validated IS 
'Knowledge base de aprendizajes validados. NO contiene precios, horarios ni servicios (solo SQL)';

COMMENT ON COLUMN knowledge_base_validated.contiene_datos_operativos IS 
'Debe ser siempre FALSE. Los datos operativos están en tablas SQL estructuradas';

COMMENT ON COLUMN knowledge_base_validated.efectividad_score IS 
'Score de efectividad basado en feedback: (positivo - negativo) / total';

-- ============================================================================
-- TABLA 3: behavior_rules (Reglas Dinámicas - System Prompt)
-- ============================================================================

CREATE TABLE IF NOT EXISTS behavior_rules (
    id SERIAL PRIMARY KEY,
    
    -- Descripción del patrón
    pattern TEXT NOT NULL,
    /* Ejemplo: 
    "Cuando un paciente pregunte por precios de servicios"
    */
    
    -- Instrucción de corrección
    correction_logic TEXT NOT NULL,
    /* Ejemplo:
    "SIEMPRE consultar la tabla 'tratamientos' en PostgreSQL.  
     NUNCA inventar precios ni basarse en conversaciones previas. 
     Usar la tool 'consultar_tratamientos_sql' con el término extraído."
    */
    
    -- Embedding del patrón (384 dims)
    embedding BYTEA NOT NULL,
    
    -- Metadata
    categoria TEXT CHECK (categoria IN (
        'datos_operativos',      -- Precios, horarios, servicios
        'politicas',             -- Políticas de la clínica
        'tono_comunicacion',     -- Cómo responder
        'escalamiento',          -- Cuándo escalar
        'validacion'             -- Validaciones necesarias
    )),
    
    prioridad INT DEFAULT 5 CHECK (prioridad BETWEEN 1 AND 10), -- 1 (máxima) - 10 (mínima)
    
    -- Estado
    activo BOOLEAN DEFAULT true,
    aprobado BOOLEAN DEFAULT false,
    
    -- Métricas
    veces_utilizada INT DEFAULT 0,
    ultima_utilizacion TIMESTAMP,
    
    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP,
    creado_por BIGINT REFERENCES usuarios(id),
    aprobado_por BIGINT REFERENCES usuarios(id)
);

-- Índices
CREATE INDEX idx_behavior_rules_activo 
ON behavior_rules(activo, prioridad) 
WHERE aprobado = true;

CREATE INDEX idx_behavior_rules_categoria 
ON behavior_rules(categoria, activo);

COMMENT ON TABLE behavior_rules IS 
'Reglas de comportamiento inyectadas dinámicamente al System Prompt del agente';

COMMENT ON COLUMN behavior_rules.prioridad IS 
'1 = Máxima prioridad (se aplica primero), 10 = Mínima prioridad';

-- ============================================================================
-- TABLA 4: whatsapp_filters (Blacklist/Whitelist/Grupos)
-- ============================================================================

CREATE TABLE IF NOT EXISTS whatsapp_filters (
    id SERIAL PRIMARY KEY,
    
    -- Tipo de filtro
    tipo TEXT NOT NULL CHECK (tipo IN (
        'blacklist',          -- Número bloqueado
        'whitelist',          -- Número permitido (modo restrictivo)
        'grupo_bloqueado'     -- Grupo bloqueado
    )),
    
    -- Valor del filtro
    valor TEXT NOT NULL, -- Número de teléfono o ID de grupo
    
    -- Información adicional
    razon TEXT,
    notas TEXT,
    
    -- Estado
    activo BOOLEAN DEFAULT true,
    
    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP,
    creado_por BIGINT REFERENCES usuarios(id),
    
    -- Constraint: Un valor solo puede tener un tipo activo
    UNIQUE(valor, tipo) WHERE activo = true
);

-- Índices
CREATE INDEX idx_whatsapp_filters_tipo 
ON whatsapp_filters(tipo, activo) 
WHERE activo = true;

CREATE INDEX idx_whatsapp_filters_valor 
ON whatsapp_filters(valor) 
WHERE activo = true;

COMMENT ON TABLE whatsapp_filters IS 
'Filtros de entrada: blacklist, whitelist, grupos bloqueados';

-- ============================================================================
-- TABLA 5: twilio_webhook_logs (Auditoría de webhooks)
-- ============================================================================

CREATE TABLE IF NOT EXISTS twilio_webhook_logs (
    id SERIAL PRIMARY KEY,
    
    -- Datos del webhook
    message_sid TEXT NOT NULL UNIQUE,
    from_number TEXT NOT NULL,
    to_number TEXT NOT NULL,
    body TEXT,
    
    -- Validación
    signature_valid BOOLEAN,
    
    -- Procesamiento
    procesado BOOLEAN DEFAULT false,
    error TEXT,
    tiempo_procesamiento_ms INT,
    
    -- Respuesta generada
    respuesta_enviada TEXT,
    fuente_respuesta TEXT, -- 'sql_estructurado', 'knowledge_base', etc.
    confidence_score FLOAT,
    
    -- Metadata
    raw_payload JSONB,
    
    -- Timestamps
    fecha_recepcion TIMESTAMP DEFAULT NOW(),
    fecha_procesamiento TIMESTAMP
);

-- Índices
CREATE INDEX idx_twilio_logs_fecha 
ON twilio_webhook_logs(fecha_recepcion DESC);

CREATE INDEX idx_twilio_logs_from 
ON twilio_webhook_logs(from_number, fecha_recepcion DESC);

CREATE INDEX idx_twilio_logs_procesado 
ON twilio_webhook_logs(procesado) 
WHERE procesado = false;

COMMENT ON TABLE twilio_webhook_logs IS 
'Log completo de webhooks de Twilio para auditoría y debugging';

-- ============================================================================
-- MODIFICAR TABLA: mensajes (Agregar metadata JSON)
-- ============================================================================

ALTER TABLE mensajes 
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;

-- Índice para búsquedas por metadata
CREATE INDEX IF NOT EXISTS idx_mensajes_metadata 
ON mensajes USING gin(metadata);

COMMENT ON COLUMN mensajes.metadata IS 
'Metadata estructurada del mensaje: fuente_respuesta, confidence, tabla_consultada, etc.';

-- ============================================================================
-- FUNCIÓN: Actualizar efectividad de KB
-- ============================================================================

CREATE OR REPLACE FUNCTION actualizar_efectividad_kb()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE knowledge_base_validated
        SET efectividad_score = CASE 
            WHEN (feedback_positivo + feedback_negativo) > 0 
            THEN (feedback_positivo::float - feedback_negativo::float) / (feedback_positivo + feedback_negativo)
            ELSE 1.0
        END,
        fecha_actualizacion = NOW()
        WHERE id = NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_efectividad_kb
AFTER INSERT OR UPDATE OF feedback_positivo, feedback_negativo
ON knowledge_base_validated
FOR EACH ROW
EXECUTE FUNCTION actualizar_efectividad_kb();

-- ============================================================================
-- INSERTAR REGLAS DE COMPORTAMIENTO INICIALES
-- ============================================================================

-- Regla 1: Consultar precios en SQL
INSERT INTO behavior_rules (pattern, correction_logic, embedding, categoria, prioridad, activo, aprobado)
VALUES (
    'Cuando un paciente pregunte por precios, costos o tarifas de servicios',
    'SIEMPRE consultar la tabla "tratamientos" usando la tool consultar_tratamientos_sql(). NUNCA inventar precios ni basarse en conversaciones previas. Si no encuentras el servicio, escala a humano.',
    E'\\x00',  -- Placeholder, se actualizará con embedding real
    'datos_operativos',
    1,  -- Máxima prioridad
    true,
    true
);

-- Regla 2: Consultar horarios en SQL
INSERT INTO behavior_rules (pattern, correction_logic, embedding, categoria, prioridad, activo, aprobado)
VALUES (
    'Cuando un paciente pregunte por horarios de atención o disponibilidad',
    'SIEMPRE consultar la tabla "horarios_trabajo" usando la tool consultar_horarios_sql(). NUNCA asumir horarios ni basarse en memoria conversacional. Los horarios pueden cambiar.',
    E'\\x00',
    'datos_operativos',
    1,
    true,
    true
);

-- Regla 3: Tono empático
INSERT INTO behavior_rules (pattern, correction_logic, embedding, categoria, prioridad, activo, aprobado)
VALUES (
    'Cuando detectes frustración, molestia o urgencia en el paciente',
    'Responde con tono EMPÁTICO y PROFESIONAL. Usa frases como "Entiendo tu situación", "Lamento las molestias", "Permíteme ayudarte inmediatamente". Prioriza la escalación a humano si el tono es muy negativo.',
    E'\\x00',
    'tono_comunicacion',
    3,
    true,
    true
);

COMMIT;

-- ============================================================================
-- VERIFICACIÓN POST-MIGRACIÓN
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migración completada exitosamente';
    RAISE NOTICE 'Tablas creadas:';
    RAISE NOTICE '  - conversaciones_embeddings (contexto aislado por paciente)';
    RAISE NOTICE '  - knowledge_base_validated (KB sin datos operativos)';
    RAISE NOTICE '  - behavior_rules (reglas dinámicas para System Prompt)';
    RAISE NOTICE '  - whatsapp_filters (blacklist/whitelist)';
    RAISE NOTICE '  - twilio_webhook_logs (auditoría)';
    RAISE NOTICE '';
    RAISE NOTICE 'Modificaciones:';
    RAISE NOTICE '  - mensajes.metadata (columna JSONB agregada)';
    RAISE NOTICE '';
    RAISE NOTICE '🔧 Siguiente paso: Generar embeddings iniciales para behavior_rules';
END $$;
