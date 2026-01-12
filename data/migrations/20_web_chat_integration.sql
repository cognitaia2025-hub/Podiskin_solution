-- ============================================================================
-- Archivo: 20_web_chat_integration.sql
-- Descripción: Extensiones para soportar chat web REUTILIZANDO tablas existentes
-- Usa: pacientes, contactos, conversaciones, mensajes (ya existentes)
-- Fecha: 2025-01-12
-- ============================================================================

-- ============================================================================
-- 1. EXTENDER TABLA PACIENTES CON PATIENT_ID
-- ============================================================================

-- Agregar columnas para ID legible en la tabla pacientes EXISTENTE
ALTER TABLE pacientes 
ADD COLUMN IF NOT EXISTS patient_id VARCHAR(20) UNIQUE,
ADD COLUMN IF NOT EXISTS partial_id VARCHAR(15),
ADD COLUMN IF NOT EXISTS id_counter INTEGER DEFAULT 1;

-- Índices para búsqueda rápida
CREATE INDEX IF NOT EXISTS idx_pacientes_patient_id ON pacientes(patient_id);
CREATE INDEX IF NOT EXISTS idx_pacientes_partial_id ON pacientes(partial_id);
CREATE INDEX IF NOT EXISTS idx_pacientes_nombres_fecha ON pacientes(primer_nombre, primer_apellido, fecha_nacimiento);

-- ============================================================================
-- 2. FUNCIÓN PARA GENERAR PATIENT_ID AUTOMÁTICAMENTE
-- ============================================================================

CREATE OR REPLACE FUNCTION generate_patient_id()
RETURNS TRIGGER AS $$
DECLARE
    last_name_part VARCHAR(2);
    first_name_part VARCHAR(2);
    date_part VARCHAR(4);
    counter_part VARCHAR(4);
    base_id VARCHAR(15);
    max_counter INTEGER;
BEGIN
    -- Extraer las últimas 2 letras del apellido (usar primer_apellido)
    last_name_part := UPPER(SUBSTRING(REGEXP_REPLACE(NEW.primer_apellido, '[^a-zA-Z]', '', 'g') FROM '.{2}$'));
    IF LENGTH(last_name_part) < 2 THEN
        last_name_part := LPAD(last_name_part, 2, 'X');
    END IF;
    
    -- Extraer las últimas 2 letras del nombre (usar primer_nombre)
    first_name_part := UPPER(SUBSTRING(REGEXP_REPLACE(NEW.primer_nombre, '[^a-zA-Z]', '', 'g') FROM '.{2}$'));
    IF LENGTH(first_name_part) < 2 THEN
        first_name_part := LPAD(first_name_part, 2, 'X');
    END IF;
    
    -- Extraer MMDD de la fecha de nacimiento
    date_part := TO_CHAR(NEW.fecha_nacimiento, 'MMDD');
    
    -- Crear el ID parcial
    base_id := last_name_part || '-' || first_name_part || '-' || date_part;
    NEW.partial_id := base_id;
    
    -- Buscar el contador máximo para este base_id
    SELECT COALESCE(MAX(id_counter), 0) + 1 INTO max_counter
    FROM pacientes
    WHERE partial_id = base_id;
    
    NEW.id_counter := max_counter;
    
    -- Formatear el contador con ceros a la izquierda
    counter_part := LPAD(max_counter::TEXT, 4, '0');
    
    -- Generar el patient_id completo
    NEW.patient_id := base_id || '-' || counter_part;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para auto-generar patient_id en INSERT
DROP TRIGGER IF EXISTS trigger_generate_patient_id ON pacientes;
CREATE TRIGGER trigger_generate_patient_id
BEFORE INSERT ON pacientes
FOR EACH ROW
WHEN (NEW.patient_id IS NULL)
EXECUTE FUNCTION generate_patient_id();

-- ============================================================================
-- 3. EXTENDER TABLA CONVERSACIONES PARA SOPORTE WEB
-- ============================================================================

-- Asegurar que 'web' está en el CHECK de canal (ya debería estar según 05_chatbot_crm.sql)
-- La tabla conversaciones YA tiene soporte para canal 'web'

-- Agregar columna session_id para compatibilidad con frontend web
ALTER TABLE conversaciones
ADD COLUMN IF NOT EXISTS session_id UUID DEFAULT gen_random_uuid();

CREATE INDEX IF NOT EXISTS idx_conversaciones_session_id ON conversaciones(session_id);
CREATE INDEX IF NOT EXISTS idx_conversaciones_canal_estado ON conversaciones(canal, estado);

-- ============================================================================
-- 4. VISTAS SIMPLIFICADAS PARA WEB CHAT API
-- ============================================================================

-- Vista que mapea la estructura existente a la interfaz esperada por el web chat
CREATE OR REPLACE VIEW web_chat_sessions AS
SELECT 
    c.id,
    c.session_id,
    c.id_contacto,
    ct.id_paciente,
    p.patient_id,
    p.primer_nombre,
    p.primer_apellido,
    c.canal AS channel,
    c.fecha_inicio AS started_at,
    c.fecha_ultima_actividad AS last_activity,
    c.estado AS status,
    c.numero_mensajes AS message_count,
    c.entidades_extraidas AS metadata
FROM conversaciones c
LEFT JOIN contactos ct ON c.id_contacto = ct.id
LEFT JOIN pacientes p ON ct.id_paciente = p.id
WHERE c.canal = 'web';

-- Vista para mensajes del web chat
CREATE OR REPLACE VIEW web_chat_messages AS
SELECT 
    m.id,
    c.session_id,
    ct.id_paciente,
    p.patient_id,
    CASE 
        WHEN m.enviado_por_tipo = 'Contacto' THEN 'user'
        WHEN m.enviado_por_tipo = 'Bot' THEN 'assistant'
        ELSE 'system'
    END AS message_type,
    m.contenido AS content,
    m.fecha_envio AS timestamp,
    m.metadata
FROM mensajes m
JOIN conversaciones c ON m.id_conversacion = c.id
LEFT JOIN contactos ct ON c.id_contacto = ct.id
LEFT JOIN pacientes p ON ct.id_paciente = p.id
WHERE c.canal = 'web';

-- ============================================================================
-- 5. FUNCIÓN AUXILIAR: BUSCAR O CREAR CONTACTO WEB
-- ============================================================================

CREATE OR REPLACE FUNCTION get_or_create_web_contact(
    p_id_paciente BIGINT,
    p_email TEXT DEFAULT NULL
) RETURNS BIGINT AS $$
DECLARE
    v_id_contacto BIGINT;
BEGIN
    -- Buscar contacto existente del paciente para canal web
    SELECT id INTO v_id_contacto
    FROM contactos
    WHERE id_paciente = p_id_paciente
    LIMIT 1;
    
    -- Si no existe, crear uno nuevo
    IF v_id_contacto IS NULL THEN
        INSERT INTO contactos (
            id_paciente,
            nombre,
            email,
            tipo,
            origen,
            activo
        )
        SELECT 
            p.id,
            CONCAT(p.primer_nombre, ' ', p.primer_apellido),
            COALESCE(p_email, p.email),
            'Lead_Calificado',
            'web',
            true
        FROM pacientes p
        WHERE p.id = p_id_paciente
        RETURNING id INTO v_id_contacto;
    END IF;
    
    RETURN v_id_contacto;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 6. FUNCIÓN AUXILIAR: BUSCAR PACIENTE POR DATOS
-- ============================================================================

CREATE OR REPLACE FUNCTION find_patient_by_name_and_birthdate(
    p_primer_nombre TEXT,
    p_primer_apellido TEXT,
    p_fecha_nacimiento DATE
) RETURNS TABLE(
    id BIGINT,
    patient_id VARCHAR(20),
    primer_nombre TEXT,
    segundo_nombre TEXT,
    primer_apellido TEXT,
    segundo_apellido TEXT,
    fecha_nacimiento DATE,
    telefono_principal TEXT,
    email TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pac.id,
        pac.patient_id,
        pac.primer_nombre,
        pac.segundo_nombre,
        pac.primer_apellido,
        pac.segundo_apellido,
        pac.fecha_nacimiento,
        pac.telefono_principal,
        pac.email
    FROM pacientes pac
    WHERE LOWER(pac.primer_nombre) = LOWER(p_primer_nombre)
      AND LOWER(pac.primer_apellido) = LOWER(p_primer_apellido)
      AND pac.fecha_nacimiento = p_fecha_nacimiento
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 7. FUNCIÓN DE LIMPIEZA: SESIONES ANTIGUAS
-- ============================================================================

CREATE OR REPLACE FUNCTION cleanup_old_web_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Cerrar conversaciones web inactivas por más de 30 días
    UPDATE conversaciones
    SET estado = 'Cerrada'
    WHERE canal = 'web'
      AND estado != 'Cerrada'
      AND fecha_ultima_actividad < NOW() - INTERVAL '30 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMENTARIOS DE DOCUMENTACIÓN
-- ============================================================================

COMMENT ON COLUMN pacientes.patient_id IS 'ID legible formato: AP-NO-MMDD-#### (autogenerado)';
COMMENT ON COLUMN pacientes.partial_id IS 'ID parcial sin contador: AP-NO-MMDD';
COMMENT ON COLUMN pacientes.id_counter IS 'Contador secuencial para el partial_id';
COMMENT ON COLUMN conversaciones.session_id IS 'UUID para identificación de sesión en frontend web';
COMMENT ON VIEW web_chat_sessions IS 'Vista simplificada de sesiones web para API - mapea conversaciones existentes';
COMMENT ON VIEW web_chat_messages IS 'Vista simplificada de mensajes web para API - mapea mensajes existentes';
COMMENT ON FUNCTION get_or_create_web_contact IS 'Busca o crea un contacto web para un paciente dado';
COMMENT ON FUNCTION find_patient_by_name_and_birthdate IS 'Busca un paciente por nombre, apellido y fecha de nacimiento';
COMMENT ON FUNCTION cleanup_old_web_sessions IS 'Cierra sesiones web inactivas mayores a 30 días';

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================

DO $$
BEGIN
    -- Verificar que patient_id fue agregado
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'pacientes' AND column_name = 'patient_id'
    ) THEN
        RAISE EXCEPTION 'Columna patient_id no fue agregada a pacientes';
    END IF;
    
    -- Verificar que session_id fue agregado
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'conversaciones' AND column_name = 'session_id'
    ) THEN
        RAISE EXCEPTION 'Columna session_id no fue agregada a conversaciones';
    END IF;
    
    -- Verificar que las vistas existen
    IF NOT EXISTS (SELECT 1 FROM pg_views WHERE viewname = 'web_chat_sessions') THEN
        RAISE EXCEPTION 'Vista web_chat_sessions no fue creada';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_views WHERE viewname = 'web_chat_messages') THEN
        RAISE EXCEPTION 'Vista web_chat_messages no fue creada';
    END IF;
    
    RAISE NOTICE '✅ Migración 20_web_chat_integration completada exitosamente';
    RAISE NOTICE '   - Extendida tabla pacientes con patient_id';
    RAISE NOTICE '   - Extendida tabla conversaciones con session_id';
    RAISE NOTICE '   - Creadas vistas web_chat_sessions y web_chat_messages';
    RAISE NOTICE '   - Creadas funciones auxiliares';
END $$;

-- ============================================================================
-- NOTAS DE INTEGRACIÓN
-- ============================================================================

/*
REUTILIZACIÓN DE TABLAS EXISTENTES:
- pacientes: Tabla principal compartida por TODOS los canales
- contactos: Relación entre canales y pacientes (whatsapp_id, telegram_id, etc)
- conversaciones: Sesiones de chat multi-canal (whatsapp, web, telegram, facebook)
- mensajes: Historial de mensajes de todas las conversaciones

FORMATO DE patient_id:
- Generado automáticamente en INSERT
- Formato: [AP]-[NO]-[MMDD]-[####]
- Ejemplo: VA-AM-0504-0009
  * VA: últimas 2 letras de "Vargas"
  * AM: últimas 2 letras de "Amelia"
  * 0504: 04 de mayo (MMDD)
  * 0009: contador secuencial

FLUJO WEB CHAT:
1. Frontend genera partial_id: "VA-AM-0504"
2. Frontend llama a /api/patient/lookup (buscar si existe)
3. Si no existe, llama a /api/patient/register
4. Backend inserta en pacientes → trigger genera patient_id completo
5. Backend crea contacto en tabla contactos con origen='web'
6. Backend crea conversación en tabla conversaciones con canal='web'
7. Mensajes se guardan en tabla mensajes con relación a conversación

COMPATIBILIDAD:
- WhatsApp usa el mismo flujo pero con canal='whatsapp'
- Ambos canales usan el mismo agente (whatsapp_medico)
- Thread IDs en LangGraph: "web_{session_id}" o "whatsapp_{phone}"
*/
