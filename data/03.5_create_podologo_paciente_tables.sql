/*
 * Sistema de Asignación de Pacientes a Podólogos
 * ===============================================
 * Tablas para gestionar asignación oficial y podólogos interinos
 */

-- ========================================================================
-- 1. TABLA DE ASIGNACIÓN OFICIAL: PODÓLOGO → PACIENTES
-- ========================================================================

CREATE TABLE IF NOT EXISTS podologo_paciente_asignacion (
    id SERIAL PRIMARY KEY,
    
    -- Relaciones
    podologo_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    
    -- Metadata de asignación
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    asignado_por INTEGER REFERENCES usuarios(id),
    notas TEXT,
    activo BOOLEAN DEFAULT TRUE,
    
    -- Constraint: Prevenir asignaciones duplicadas
    UNIQUE(podologo_id, paciente_id)
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_podologo_paciente_podologo ON podologo_paciente_asignacion(podologo_id) WHERE activo = TRUE;
CREATE INDEX idx_podologo_paciente_paciente ON podologo_paciente_asignacion(paciente_id) WHERE activo = TRUE;

-- Crear índice único parcial para garantizar un solo podólogo activo por paciente
CREATE UNIQUE INDEX idx_podologo_paciente_activo_unico 
ON podologo_paciente_asignacion(paciente_id) 
WHERE activo = TRUE;

-- Comentarios
COMMENT ON TABLE podologo_paciente_asignacion IS 'Asignación oficial de pacientes a podólogos';
COMMENT ON COLUMN podologo_paciente_asignacion.activo IS 'Solo puede haber una asignación activa por paciente';

-- ========================================================================
-- 2. TABLA DE PODÓLOGOS INTERINOS (TEMPORALES)
-- ========================================================================

CREATE TABLE IF NOT EXISTS podologo_interino_asignacion (
    id SERIAL PRIMARY KEY,
    
    -- Relaciones
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    podologo_oficial_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    podologo_interino_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    
    -- Validez temporal
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP,
    
    -- Metadata
    motivo TEXT, -- Ej: "Dr. Santiago enfermo", "Vacaciones"
    asignado_por INTEGER REFERENCES usuarios(id),
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    
    -- Constraints
    CHECK (podologo_oficial_id != podologo_interino_id),
    CHECK (fecha_fin IS NULL OR fecha_fin > fecha_inicio)
);

-- Índices
CREATE INDEX idx_interino_paciente ON podologo_interino_asignacion(paciente_id) WHERE activo = TRUE;
CREATE INDEX idx_interino_podologo_oficial ON podologo_interino_asignacion(podologo_oficial_id) WHERE activo = TRUE;
CREATE INDEX idx_interino_podologo_interino ON podologo_interino_asignacion(podologo_interino_id) WHERE activo = TRUE;
CREATE INDEX idx_interino_vigencia ON podologo_interino_asignacion(fecha_inicio, fecha_fin) WHERE activo = TRUE;

-- Crear índice único parcial para garantizar un solo interino activo por paciente
CREATE UNIQUE INDEX idx_interino_paciente_activo_unico 
ON podologo_interino_asignacion(paciente_id) 
WHERE activo = TRUE;

-- Comentarios
COMMENT ON TABLE podologo_interino_asignacion IS 'Asignaciones temporales de podólogos interinos';
COMMENT ON COLUMN podologo_interino_asignacion.fecha_fin IS 'NULL = sin límite de tiempo';

-- ========================================================================
-- 3. VISTA: PACIENTES CON SUS PODÓLOGOS (OFICIAL E INTERINO)
-- ========================================================================

CREATE OR REPLACE VIEW v_pacientes_con_podologos AS
SELECT 
    p.id as paciente_id,
    -- ✅ AJUSTADO: Concatenar nombres y apellidos según estructura real
    TRIM(CONCAT(
        COALESCE(p.primer_nombre, ''), 
        ' ',
        COALESCE(p.segundo_nombre, ''),
        ' ', 
        COALESCE(p.primer_apellido, ''),
        ' ',
        COALESCE(p.segundo_apellido, '')
    )) as paciente_nombre,
    p.telefono_principal as telefono,
    p.email,
    
    -- Podólogo oficial
    u_oficial.id as podologo_oficial_id,
    u_oficial.nombre_completo as podologo_oficial_nombre,
    
    -- Podólogo interino (si existe)
    u_interino.id as podologo_interino_id,
    u_interino.nombre_completo as podologo_interino_nombre,
    pi.motivo as motivo_interino,
    pi.fecha_fin as fecha_fin_interino,
    
    -- Último tratamiento
    (
        SELECT MAX(fecha_hora_inicio::date)
        FROM citas c
        WHERE c.id_paciente = p.id 
            AND c.estado = 'Completada'
    ) as fecha_ultimo_tratamiento,
    
    (
        SELECT CONCAT('Cita #', c.id::text)
        FROM citas c
        WHERE c.id_paciente = p.id 
            AND c.estado = 'Completada'
        ORDER BY fecha_hora_inicio DESC
        LIMIT 1
    ) as ultimo_tratamiento

FROM pacientes p

-- Join con podólogo oficial
LEFT JOIN podologo_paciente_asignacion ppa 
    ON p.id = ppa.paciente_id 
    AND ppa.activo = TRUE
LEFT JOIN usuarios u_oficial 
    ON ppa.podologo_id = u_oficial.id

-- Join con podólogo interino
LEFT JOIN podologo_interino_asignacion pi 
    ON p.id = pi.paciente_id 
    AND pi.activo = TRUE
    AND (pi.fecha_fin IS NULL OR pi.fecha_fin > CURRENT_TIMESTAMP)
LEFT JOIN usuarios u_interino 
    ON pi.podologo_interino_id = u_interino.id

WHERE p.activo = TRUE;

-- Comentario
COMMENT ON VIEW v_pacientes_con_podologos IS 'Vista completa de pacientes con sus podólogos oficial e interino';

-- ========================================================================
-- 4. FUNCIÓN: OBTENER PACIENTES DE UN PODÓLOGO
-- ========================================================================

CREATE OR REPLACE FUNCTION get_pacientes_podologo(p_podologo_id INTEGER)
RETURNS TABLE (
    paciente_id BIGINT,
    nombre_completo TEXT,
    telefono TEXT,
    ultimo_tratamiento TEXT,
    fecha_ultimo_tratamiento DATE,
    tiene_interino BOOLEAN,
    podologo_interino_id BIGINT,
    podologo_interino_nombre TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        v.paciente_id,
        v.paciente_nombre,
        v.telefono,
        v.ultimo_tratamiento,
        v.fecha_ultimo_tratamiento,
        (v.podologo_interino_id IS NOT NULL) as tiene_interino,
        v.podologo_interino_id,
        v.podologo_interino_nombre
    FROM v_pacientes_con_podologos v
    WHERE v.podologo_oficial_id = p_podologo_id
    ORDER BY v.paciente_nombre;
END;
$$ LANGUAGE plpgsql;

-- ========================================================================
-- 5. FUNCIÓN: ASIGNAR PODÓLOGO INTERINO
-- ========================================================================

CREATE OR REPLACE FUNCTION asignar_podologo_interino(
    p_paciente_id INTEGER,
    p_podologo_oficial_id INTEGER,
    p_podologo_interino_id INTEGER,
    p_fecha_fin TIMESTAMP DEFAULT NULL,
    p_motivo TEXT DEFAULT NULL,
    p_asignado_por INTEGER DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_asignacion_id INTEGER;
BEGIN
    -- Validar que el paciente esté asignado al podólogo oficial
    IF NOT EXISTS (
        SELECT 1 
        FROM podologo_paciente_asignacion 
        WHERE paciente_id = p_paciente_id 
            AND podologo_id = p_podologo_oficial_id 
            AND activo = TRUE
    ) THEN
        RAISE EXCEPTION 'El paciente no está asignado a este podólogo';
    END IF;
    
    -- Validar que el interino sea realmente un podólogo
    IF NOT EXISTS (
        SELECT 1 
        FROM usuarios 
        WHERE id = p_podologo_interino_id 
            AND rol = 'Podologo' 
            AND activo = TRUE
    ) THEN
        RAISE EXCEPTION 'El usuario seleccionado no es un podólogo activo';
    END IF;
    
    -- Desactivar cualquier asignación interina previa
    UPDATE podologo_interino_asignacion
    SET activo = FALSE
    WHERE paciente_id = p_paciente_id
        AND activo = TRUE;
    
    -- Crear nueva asignación
    INSERT INTO podologo_interino_asignacion (
        paciente_id,
        podologo_oficial_id,
        podologo_interino_id,
        fecha_fin,
        motivo,
        asignado_por
    ) VALUES (
        p_paciente_id,
        p_podologo_oficial_id,
        p_podologo_interino_id,
        p_fecha_fin,
        p_motivo,
        p_asignado_por
    )
    RETURNING id INTO v_asignacion_id;
    
    RETURN v_asignacion_id;
END;
$$ LANGUAGE plpgsql;

-- ========================================================================
-- 6. FUNCIÓN: QUITAR PODÓLOGO INTERINO
-- ========================================================================

CREATE OR REPLACE FUNCTION quitar_podologo_interino(
    p_paciente_id INTEGER
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE podologo_interino_asignacion
    SET activo = FALSE
    WHERE paciente_id = p_paciente_id
        AND activo = TRUE;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- ========================================================================
-- 7. TRIGGER: EXPIRACIÓN AUTOMÁTICA DE ASIGNACIONES INTERINAS
-- ========================================================================

CREATE OR REPLACE FUNCTION check_interino_expiration()
RETURNS TRIGGER AS $$
BEGIN
    -- Si la fecha_fin ya pasó, marcar como inactivo
    IF NEW.fecha_fin IS NOT NULL AND NEW.fecha_fin < CURRENT_TIMESTAMP THEN
        NEW.activo = FALSE;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_interino_expiration
BEFORE INSERT OR UPDATE ON podologo_interino_asignacion
FOR EACH ROW
EXECUTE FUNCTION check_interino_expiration();

-- ========================================================================
-- 8. DATOS INICIALES: ASIGNAR PACIENTES EXISTENTES A PODÓLOGOS
-- ========================================================================

-- Nota: Ejecutar solo si quieres asignar pacientes existentes
-- Este script asigna todos los pacientes sin asignación al primer podólogo

/*
INSERT INTO podologo_paciente_asignacion (podologo_id, paciente_id, asignado_por)
SELECT 
    (SELECT id FROM usuarios WHERE rol = 'Podologo' AND activo = TRUE LIMIT 1) as podologo_id,
    p.id as paciente_id,
    (SELECT id FROM usuarios WHERE rol = 'Admin' LIMIT 1) as asignado_por
FROM pacientes p
WHERE NOT EXISTS (
    SELECT 1 
    FROM podologo_paciente_asignacion ppa 
    WHERE ppa.paciente_id = p.id AND ppa.activo = TRUE
)
AND p.activo = TRUE;
*/

