-- ============================================================================
-- Archivo: 07_asistente_voz_consulta.sql
-- Descripción: Tablas para el asistente de voz con Gemini Live durante consultas
-- Dependencias: 02_usuarios.sql, 03_pacientes.sql, 04_citas_tratamientos.sql
-- ============================================================================

-- ============================================================================
-- SESIONES DE CONSULTA CON ASISTENTE DE VOZ
-- ============================================================================

CREATE TABLE sesiones_consulta_voz (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_cita bigint NOT NULL REFERENCES citas(id),
    id_paciente bigint NOT NULL REFERENCES pacientes(id),
    id_podologo bigint NOT NULL REFERENCES podologos(id),
    
    -- Control de sesión
    fecha_inicio timestamp NOT NULL DEFAULT NOW(),
    fecha_fin timestamp,
    duracion_segundos integer,
    estado text DEFAULT 'Activa' CHECK (estado IN ('Activa', 'Pausada', 'Finalizada', 'Error')),
    
    -- Audio y transcripción
    url_grabacion_completa text,
    transcripcion_completa text,
    resumen_ia text,
    
    -- Métricas de la sesión
    total_comandos_voz integer DEFAULT 0,
    total_campos_llenados integer DEFAULT 0,
    total_consultas_respondidas integer DEFAULT 0,
    
    -- Gemini Live session metadata
    gemini_session_id text,
    modelo_utilizado text DEFAULT 'gemini-2.0-flash-exp',
    
    -- Auditoría
    creado_en timestamp DEFAULT NOW(),
    actualizado_en timestamp DEFAULT NOW()
);

CREATE INDEX idx_sesiones_cita ON sesiones_consulta_voz(id_cita);
CREATE INDEX idx_sesiones_estado ON sesiones_consulta_voz(estado, fecha_inicio DESC);
CREATE INDEX idx_sesiones_podologo ON sesiones_consulta_voz(id_podologo, fecha_inicio DESC);

-- ============================================================================
-- TRANSCRIPCIÓN EN TIEMPO REAL
-- ============================================================================

CREATE TABLE transcripcion_tiempo_real (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_sesion bigint NOT NULL REFERENCES sesiones_consulta_voz(id) ON DELETE CASCADE,
    
    -- Timing del segmento
    timestamp_inicio numeric(10,3) NOT NULL, -- Segundos desde inicio de sesión
    timestamp_fin numeric(10,3),
    duracion_ms integer,
    
    -- Contenido
    hablante text NOT NULL CHECK (hablante IN ('Podologo', 'Paciente', 'Asistente_IA')),
    texto text NOT NULL,
    texto_normalizado text, -- Sin acentos, minúsculas, para búsqueda
    
    -- Metadatos de transcripción
    confianza numeric(3,2) CHECK (confianza BETWEEN 0 AND 1),
    idioma_detectado text DEFAULT 'es-MX',
    
    -- Procesamiento
    procesado_por_ia boolean DEFAULT false,
    entidades_extraidas jsonb, -- {"medicamentos": ["Ibuprofeno"], "sintomas": ["dolor"]}
    requiere_atencion boolean DEFAULT false, -- Si detecta algo crítico
    
    -- Timestamps
    fecha_creacion timestamp DEFAULT NOW()
);

CREATE INDEX idx_transcripcion_sesion ON transcripcion_tiempo_real(id_sesion, timestamp_inicio);
CREATE INDEX idx_transcripcion_hablante ON transcripcion_tiempo_real(id_sesion, hablante);
CREATE INDEX idx_transcripcion_texto ON transcripcion_tiempo_real USING gin(to_tsvector('spanish', texto));

-- ============================================================================
-- FUNCTION CALLS EJECUTADAS (Gemini Live)
-- ============================================================================

CREATE TABLE function_calls_ejecutadas (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_sesion bigint NOT NULL REFERENCES sesiones_consulta_voz(id) ON DELETE CASCADE,
    
    -- Identificación de la llamada
    function_name text NOT NULL,
    timestamp_audio numeric(10,3), -- Momento en el audio donde se solicitó
    
    -- Parámetros de entrada
    parametros_entrada jsonb NOT NULL,
    
    -- Tipo de acción
    tipo_accion text NOT NULL CHECK (tipo_accion IN (
        'Llenar_Campo',           -- fill_patient_field
        'Consultar_Dato',         -- query_patient_data
        'Navegar_Seccion',        -- navigate_to_section
        'Crear_Nota',             -- create_clinical_note
        'Actualizar_Signos',      -- update_vital_signs
        'Buscar_Historial',       -- search_patient_history
        'Generar_Resumen'         -- generate_summary
    )),
    
    -- Ejecución
    estado_ejecucion text DEFAULT 'Pendiente' CHECK (estado_ejecucion IN ('Pendiente', 'Ejecutando', 'Exitosa', 'Fallida')),
    resultado_ejecucion jsonb,
    error_detalle text,
    
    -- Impacto en BD
    tabla_afectada text,
    campo_afectado text,
    valor_anterior text,
    valor_nuevo text,
    
    -- Validación
    requiere_confirmacion boolean DEFAULT false,
    confirmado_por_usuario boolean,
    confirmado_en timestamp,
    
    -- Timestamps
    fecha_ejecucion timestamp DEFAULT NOW(),
    duracion_ms integer
);

CREATE INDEX idx_function_calls_sesion ON function_calls_ejecutadas(id_sesion, fecha_ejecucion);
CREATE INDEX idx_function_calls_tipo ON function_calls_ejecutadas(tipo_accion, estado_ejecucion);
CREATE INDEX idx_function_calls_tabla ON function_calls_ejecutadas(tabla_afectada, campo_afectado);

-- ============================================================================
-- COMANDOS DE VOZ ESPECÍFICOS
-- ============================================================================

CREATE TABLE comandos_voz_consulta (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_sesion bigint NOT NULL REFERENCES sesiones_consulta_voz(id) ON DELETE CASCADE,
    id_transcripcion bigint REFERENCES transcripcion_tiempo_real(id),
    
    -- Comando original
    comando_texto text NOT NULL,
    comando_normalizado text, -- Versión procesada
    timestamp_audio numeric(10,3),
    
    -- Interpretación de la IA
    intencion_detectada text, -- "llenar_peso", "consultar_alergias", "navegar_historial"
    confianza_intencion numeric(3,2),
    parametros_extraidos jsonb,
    
    -- Respuesta de la IA
    respuesta_texto text,
    respuesta_audio_url text,
    
    -- Ejecución
    id_function_call bigint REFERENCES function_calls_ejecutadas(id),
    ejecutado boolean DEFAULT false,
    
    -- Timestamps
    fecha_creacion timestamp DEFAULT NOW()
);

CREATE INDEX idx_comandos_sesion ON comandos_voz_consulta(id_sesion, timestamp_audio);
CREATE INDEX idx_comandos_intencion ON comandos_voz_consulta(intencion_detectada);

-- ============================================================================
-- CAMPOS DEL FORMULARIO CONFIGURABLES PARA VOZ
-- ============================================================================

CREATE TABLE campos_formulario_voz (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    
    -- Identificación del campo
    tabla_destino text NOT NULL,
    campo_destino text NOT NULL,
    nombre_amigable text NOT NULL, -- "peso del paciente"
    categoria text, -- "signos_vitales", "antecedentes", "nota_clinica"
    
    -- Configuración de tipo
    tipo_dato text NOT NULL CHECK (tipo_dato IN ('numero', 'texto', 'fecha', 'booleano', 'seleccion', 'texto_largo')),
    unidad_medida text, -- 'kg', 'cm', 'mmHg', 'lpm'
    valores_permitidos jsonb, -- Para campos de selección: ["Normal", "Vegetariana", "Vegana"]
    
    -- Validación
    validacion_regex text,
    valor_minimo numeric,
    valor_maximo numeric,
    obligatorio boolean DEFAULT false,
    
    -- Configuración para IA
    orden_sugerido integer, -- Orden en que la IA debería preguntar
    prompt_ia text, -- "Por favor indique el peso del paciente en kilogramos"
    ejemplos_validos jsonb, -- ["75.5 kg", "setenta y cinco kilos"]
    
    -- Function calling
    function_name text, -- Nombre de la función en Gemini Live
    parametro_nombre text, -- Nombre del parámetro en la función
    
    -- Estado
    activo boolean DEFAULT true,
    fecha_creacion timestamp DEFAULT NOW()
);

CREATE INDEX idx_campos_tabla ON campos_formulario_voz(tabla_destino, activo);
CREATE INDEX idx_campos_categoria ON campos_formulario_voz(categoria, orden_sugerido);

-- Insertar campos predefinidos para signos vitales
INSERT INTO campos_formulario_voz (tabla_destino, campo_destino, nombre_amigable, categoria, tipo_dato, unidad_medida, prompt_ia, function_name, parametro_nombre, orden_sugerido) VALUES
('signos_vitales', 'peso_kg', 'Peso del paciente', 'signos_vitales', 'numero', 'kg', '¿Cuál es el peso del paciente en kilogramos?', 'update_vital_signs', 'peso_kg', 1),
('signos_vitales', 'talla_cm', 'Talla del paciente', 'signos_vitales', 'numero', 'cm', '¿Cuál es la talla del paciente en centímetros?', 'update_vital_signs', 'talla_cm', 2),
('signos_vitales', 'ta_sistolica', 'Tensión arterial sistólica', 'signos_vitales', 'numero', 'mmHg', '¿Cuál es la presión sistólica?', 'update_vital_signs', 'ta_sistolica', 3),
('signos_vitales', 'ta_diastolica', 'Tensión arterial diastólica', 'signos_vitales', 'numero', 'mmHg', '¿Cuál es la presión diastólica?', 'update_vital_signs', 'ta_diastolica', 4),
('signos_vitales', 'frecuencia_cardiaca', 'Frecuencia cardíaca', 'signos_vitales', 'numero', 'lpm', '¿Cuál es la frecuencia cardíaca?', 'update_vital_signs', 'frecuencia_cardiaca', 5),
('signos_vitales', 'temperatura_c', 'Temperatura corporal', 'signos_vitales', 'numero', '°C', '¿Cuál es la temperatura del paciente?', 'update_vital_signs', 'temperatura_c', 6),
('nota_clinica', 'motivo_consulta', 'Motivo de consulta', 'nota_clinica', 'texto_largo', NULL, '¿Cuál es el motivo de la consulta?', 'create_clinical_note', 'motivo_consulta', 10),
('nota_clinica', 'padecimiento_actual', 'Padecimiento actual', 'nota_clinica', 'texto_largo', NULL, 'Describa el padecimiento actual del paciente', 'create_clinical_note', 'padecimiento_actual', 11),
('nota_clinica', 'exploracion_fisica', 'Exploración física', 'nota_clinica', 'texto_largo', NULL, 'Describa los hallazgos de la exploración física', 'create_clinical_note', 'exploracion_fisica', 12);

-- ============================================================================
-- AUDITORIA DE LLENADO DE CAMPOS
-- ============================================================================

CREATE TABLE auditoria_llenado_campos (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_sesion bigint NOT NULL REFERENCES sesiones_consulta_voz(id) ON DELETE CASCADE,
    id_function_call bigint REFERENCES function_calls_ejecutadas(id),
    
    -- Campo modificado
    tabla_afectada text NOT NULL,
    campo_afectado text NOT NULL,
    registro_id bigint, -- ID del registro modificado (ej: id de signos_vitales)
    
    -- Cambio realizado
    valor_anterior text,
    valor_nuevo text NOT NULL,
    
    -- Método de llenado
    metodo_llenado text NOT NULL CHECK (metodo_llenado IN ('Voz_IA', 'Manual_Teclado', 'Manual_Click', 'Importado', 'Calculado')),
    confianza_ia numeric(3,2),
    
    -- Validación
    requiere_validacion boolean DEFAULT false,
    validado boolean DEFAULT false,
    validado_por bigint REFERENCES usuarios(id),
    validado_en timestamp,
    
    -- Timestamps
    fecha_modificacion timestamp DEFAULT NOW()
);

CREATE INDEX idx_auditoria_sesion ON auditoria_llenado_campos(id_sesion, fecha_modificacion);
CREATE INDEX idx_auditoria_tabla ON auditoria_llenado_campos(tabla_afectada, campo_afectado);
CREATE INDEX idx_auditoria_validacion ON auditoria_llenado_campos(requiere_validacion, validado);

-- ============================================================================
-- TRIGGERS PARA AUDITORIA AUTOMÁTICA
-- ============================================================================

-- Trigger para registrar cambios en signos_vitales
CREATE OR REPLACE FUNCTION auditar_signos_vitales() RETURNS trigger AS $$
DECLARE
    v_sesion_activa bigint;
BEGIN
    -- Buscar sesión activa para esta cita
    SELECT id INTO v_sesion_activa
    FROM sesiones_consulta_voz
    WHERE id_cita = (SELECT id_cita FROM signos_vitales WHERE id = NEW.id)
      AND estado = 'Activa'
    LIMIT 1;
    
    IF v_sesion_activa IS NOT NULL THEN
        -- Registrar cambio de peso
        IF (TG_OP = 'UPDATE' AND OLD.peso_kg IS DISTINCT FROM NEW.peso_kg) OR (TG_OP = 'INSERT' AND NEW.peso_kg IS NOT NULL) THEN
            INSERT INTO auditoria_llenado_campos (id_sesion, tabla_afectada, campo_afectado, registro_id, valor_anterior, valor_nuevo, metodo_llenado)
            VALUES (v_sesion_activa, 'signos_vitales', 'peso_kg', NEW.id, OLD.peso_kg::text, NEW.peso_kg::text, 'Voz_IA');
        END IF;
        
        -- Similar para otros campos...
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auditar_signos_vitales
AFTER INSERT OR UPDATE ON signos_vitales
FOR EACH ROW
EXECUTE FUNCTION auditar_signos_vitales();

-- ============================================================================
-- VISTAS ÚTILES
-- ============================================================================

-- Vista de resumen de sesión
CREATE VIEW resumen_sesiones_voz AS
SELECT 
    s.id,
    s.id_cita,
    p.primer_nombre || ' ' || p.primer_apellido AS nombre_paciente,
    pod.nombre_completo AS nombre_podologo,
    s.fecha_inicio,
    s.fecha_fin,
    s.duracion_segundos,
    s.estado,
    s.total_comandos_voz,
    s.total_campos_llenados,
    s.total_consultas_respondidas,
    -- Estadísticas de function calls
    (SELECT COUNT(*) FROM function_calls_ejecutadas WHERE id_sesion = s.id AND estado_ejecucion = 'Exitosa') AS functions_exitosas,
    (SELECT COUNT(*) FROM function_calls_ejecutadas WHERE id_sesion = s.id AND estado_ejecucion = 'Fallida') AS functions_fallidas,
    -- Campos pendientes de validación
    (SELECT COUNT(*) FROM auditoria_llenado_campos WHERE id_sesion = s.id AND requiere_validacion = true AND validado = false) AS campos_pendientes_validacion
FROM sesiones_consulta_voz s
JOIN pacientes p ON s.id_paciente = p.id
JOIN podologos pod ON s.id_podologo = pod.id
ORDER BY s.fecha_inicio DESC;

-- Vista de comandos más usados
CREATE VIEW comandos_voz_frecuentes AS
SELECT 
    intencion_detectada,
    COUNT(*) AS total_usos,
    AVG(confianza_intencion) AS confianza_promedio,
    COUNT(*) FILTER (WHERE ejecutado = true) AS ejecutados,
    COUNT(*) FILTER (WHERE ejecutado = false) AS no_ejecutados
FROM comandos_voz_consulta
WHERE intencion_detectada IS NOT NULL
GROUP BY intencion_detectada
ORDER BY total_usos DESC;
