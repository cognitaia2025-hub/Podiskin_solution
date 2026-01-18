-- ============================================================================
-- Archivo: 25_bloques_horario.sql
-- Descripción: Sistema de horarios granular con detección de conflictos
-- Dependencias: 02_usuarios.sql, 04_citas_tratamientos.sql
-- ============================================================================

-- ============================================================================
-- EXTENSIÓN: btree_gist (requerida para exclusion constraints)
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS btree_gist;

-- ============================================================================
-- TABLA: bloques_horario (Horarios granulares por fecha específica)
-- ============================================================================

CREATE TABLE bloques_horario (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_podologo bigint NOT NULL REFERENCES podologos(id),
    
    -- GRANULAR: Fecha + Rango de tiempo
    fecha date NOT NULL,
    periodo tsrange NOT NULL,  -- [2026-01-19 08:30, 2026-01-19 14:30)
    
    -- Metadatos
    tipo text DEFAULT 'trabajo' CHECK (tipo IN ('trabajo', 'descanso', 'administrativo')),
    duracion_slot_minutos integer DEFAULT 30,
    notas text,
    
    -- Auditoría
    creado_por bigint REFERENCES usuarios(id),
    fecha_creacion timestamp DEFAULT NOW(),
    modificado_por bigint REFERENCES usuarios(id),
    fecha_modificacion timestamp,
    
    -- 🔥 EXCLUSION CONSTRAINT: Previene solapamientos para el mismo podólogo
    CONSTRAINT bloques_no_solapan EXCLUDE USING gist (
        id_podologo WITH =,
        periodo WITH &&
    )
);

-- Índices para rendimiento
CREATE INDEX idx_bloques_podologo_fecha ON bloques_horario(id_podologo, fecha);
CREATE INDEX idx_bloques_periodo ON bloques_horario USING gist(periodo);

COMMENT ON TABLE bloques_horario IS 'Bloques de tiempo granulares para horarios de podólogos';
COMMENT ON COLUMN bloques_horario.periodo IS 'Rango de tiempo [inicio, fin) usando tsrange';
COMMENT ON CONSTRAINT bloques_no_solapan ON bloques_horario IS 'Previene que un podólogo tenga bloques de tiempo solapados';

-- ============================================================================
-- MODIFICAR TABLA CITAS: Agregar columna periodo
-- ============================================================================

-- Agregar columna de rango de tiempo
ALTER TABLE citas ADD COLUMN IF NOT EXISTS periodo tsrange;

-- Poblar con datos existentes (si existen)
UPDATE citas 
SET periodo = tsrange(fecha_hora_inicio, fecha_hora_fin, '[)')
WHERE periodo IS NULL AND fecha_hora_inicio IS NOT NULL AND fecha_hora_fin IS NOT NULL;

-- Crear índice GiST para rendimiento
CREATE INDEX IF NOT EXISTS idx_citas_periodo ON citas USING gist(periodo);

-- 🔥 EXCLUSION CONSTRAINT: Previene doble-booking
DO $$
BEGIN
    -- Verificar si el constraint ya existe
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'citas_no_solapan'
    ) THEN
        ALTER TABLE citas ADD CONSTRAINT citas_no_solapan 
            EXCLUDE USING gist (
                id_podologo WITH =,
                periodo WITH &&
            ) WHERE (estado NOT IN ('Cancelada', 'No_Asistio'));
    END IF;
END $$;

COMMENT ON COLUMN citas.periodo IS 'Rango de tiempo de la cita [inicio, fin)';

-- ============================================================================
-- TRIGGER: Sincronizar periodo con fecha_hora_inicio/fin
-- ============================================================================

CREATE OR REPLACE FUNCTION sync_cita_periodo() 
RETURNS trigger AS $$
BEGIN
    -- Si se modifican las fechas, actualizar periodo
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
        IF NEW.fecha_hora_inicio IS NOT NULL AND NEW.fecha_hora_fin IS NOT NULL THEN
            NEW.periodo := tsrange(NEW.fecha_hora_inicio, NEW.fecha_hora_fin, '[)');
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_sync_cita_periodo ON citas;
CREATE TRIGGER trigger_sync_cita_periodo
BEFORE INSERT OR UPDATE ON citas
FOR EACH ROW
EXECUTE FUNCTION sync_cita_periodo();

-- ============================================================================
-- TRIGGER: Validar que la cita esté dentro de un bloque de trabajo
-- ============================================================================

CREATE OR REPLACE FUNCTION validar_cita_en_bloque_horario() 
RETURNS trigger AS $$
DECLARE
    v_bloque_existe boolean;
    v_bloques_disponibles text;
BEGIN
    -- Solo validar si es una cita nueva o se está modificando el horario
    IF (TG_OP = 'INSERT' OR (TG_OP = 'UPDATE' AND OLD.periodo IS DISTINCT FROM NEW.periodo)) THEN
        
        -- Verificar que existe un bloque de trabajo que CONTENGA el período de la cita
        SELECT EXISTS (
            SELECT 1 FROM bloques_horario
            WHERE id_podologo = NEW.id_podologo
              AND tipo = 'trabajo'
              AND periodo @> NEW.periodo  -- El bloque CONTIENE la cita
        ) INTO v_bloque_existe;
        
        IF NOT v_bloque_existe THEN
            -- Obtener bloques disponibles para mensaje de error útil
            SELECT string_agg(
                periodo::text, ', '
            ) INTO v_bloques_disponibles
            FROM bloques_horario
            WHERE id_podologo = NEW.id_podologo
              AND tipo = 'trabajo'
              AND fecha = NEW.fecha_hora_inicio::date
            LIMIT 5;
            
            RAISE EXCEPTION 'No existe horario de trabajo para este podólogo en el período solicitado (%). Bloques disponibles: %', 
                NEW.periodo::text,
                COALESCE(v_bloques_disponibles, 'ninguno');
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_validar_cita_bloque ON citas;
CREATE TRIGGER trigger_validar_cita_bloque
BEFORE INSERT OR UPDATE ON citas
FOR EACH ROW
EXECUTE FUNCTION validar_cita_en_bloque_horario();

-- ============================================================================
-- TRIGGER: Bloquear modificación/eliminación de horarios con citas
-- ============================================================================

CREATE OR REPLACE FUNCTION bloquear_modificacion_horario_con_citas() 
RETURNS trigger AS $$
DECLARE
    v_citas_afectadas integer;
    v_citas_detalle text;
BEGIN
    -- Contar citas que quedarían fuera del nuevo horario
    IF TG_OP = 'UPDATE' THEN
        SELECT COUNT(*) INTO v_citas_afectadas
        FROM citas c
        WHERE c.id_podologo = OLD.id_podologo
          AND c.estado NOT IN ('Cancelada', 'No_Asistio')
          AND c.periodo && OLD.periodo  -- Citas en el rango ORIGINAL
          AND NOT (NEW.periodo @> c.periodo);  -- Que NO estarían en el NUEVO rango
          
    ELSIF TG_OP = 'DELETE' THEN
        SELECT COUNT(*) INTO v_citas_afectadas
        FROM citas c
        WHERE c.id_podologo = OLD.id_podologo
          AND c.estado NOT IN ('Cancelada', 'No_Asistio')
          AND c.periodo && OLD.periodo;  -- Citas en el rango a eliminar
    END IF;
    
    IF v_citas_afectadas > 0 THEN
        -- Obtener detalles de las citas afectadas
        SELECT string_agg(
            'ID ' || c.id || ' (' || c.fecha_hora_inicio::text || ')', ', '
        ) INTO v_citas_detalle
        FROM citas c
        WHERE c.id_podologo = OLD.id_podologo
          AND c.estado NOT IN ('Cancelada', 'No_Asistio')
          AND c.periodo && OLD.periodo
        LIMIT 3;
        
        RAISE EXCEPTION 'No se puede % el horario: hay % cita(s) programadas que quedarían afectadas. Citas: %. Cancela o reagenda esas citas primero.', 
            CASE WHEN TG_OP = 'DELETE' THEN 'eliminar' ELSE 'modificar' END,
            v_citas_afectadas,
            v_citas_detalle;
    END IF;
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_bloquear_modificacion_horario ON bloques_horario;
CREATE TRIGGER trigger_bloquear_modificacion_horario
BEFORE UPDATE OR DELETE ON bloques_horario
FOR EACH ROW
EXECUTE FUNCTION bloquear_modificacion_horario_con_citas();

-- ============================================================================
-- FUNCIÓN HELPER: Generar bloques desde horarios_trabajo (migración)
-- ============================================================================

CREATE OR REPLACE FUNCTION generar_bloques_desde_plantilla(
    p_id_podologo bigint,
    p_fecha_inicio date,
    p_fecha_fin date
) RETURNS integer AS $$
DECLARE
    v_fecha date;
    v_dia_semana integer;
    v_horario RECORD;
    v_bloques_creados integer := 0;
BEGIN
    -- Iterar cada día en el rango
    FOR v_fecha IN 
        SELECT generate_series(p_fecha_inicio, p_fecha_fin, '1 day'::interval)::date
    LOOP
        -- Obtener día de la semana (0=Domingo, 6=Sábado)
        v_dia_semana := EXTRACT(DOW FROM v_fecha);
        
        -- Buscar plantilla de horario para este día
        FOR v_horario IN
            SELECT * FROM horarios_trabajo
            WHERE id_podologo = p_id_podologo
              AND dia_semana = v_dia_semana
              AND activo = true
              AND (fecha_inicio_vigencia IS NULL OR fecha_inicio_vigencia <= v_fecha)
              AND (fecha_fin_vigencia IS NULL OR fecha_fin_vigencia >= v_fecha)
        LOOP
            -- Crear bloque de horario
            INSERT INTO bloques_horario (
                id_podologo,
                fecha,
                periodo,
                tipo,
                duracion_slot_minutos,
                notas
            ) VALUES (
                p_id_podologo,
                v_fecha,
                tsrange(
                    v_fecha + v_horario.hora_inicio,
                    v_fecha + v_horario.hora_fin,
                    '[)'
                ),
                'trabajo',
                v_horario.duracion_cita_minutos,
                'Generado automáticamente desde plantilla'
            )
            ON CONFLICT DO NOTHING;  -- Ignorar si ya existe
            
            v_bloques_creados := v_bloques_creados + 1;
        END LOOP;
    END LOOP;
    
    RETURN v_bloques_creados;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION generar_bloques_desde_plantilla IS 'Genera bloques_horario a partir de plantillas en horarios_trabajo para un rango de fechas';

-- ============================================================================
-- VISTA: Disponibilidad de bloques con slots
-- ============================================================================

CREATE OR REPLACE VIEW disponibilidad_bloques AS
SELECT 
    b.id,
    b.id_podologo,
    u.nombre_completo AS podologo_nombre,
    b.fecha,
    b.periodo,
    lower(b.periodo) AS hora_inicio,
    upper(b.periodo) AS hora_fin,
    b.duracion_slot_minutos,
    b.tipo,
    -- Calcular slots totales
    FLOOR(
        EXTRACT(EPOCH FROM (upper(b.periodo) - lower(b.periodo))) / 60 / b.duracion_slot_minutos
    )::integer AS slots_totales,
    -- Contar citas ocupadas
    (
        SELECT COUNT(*)
        FROM citas c
        WHERE c.id_podologo = b.id_podologo
          AND c.periodo && b.periodo
          AND c.estado NOT IN ('Cancelada', 'No_Asistio')
    ) AS slots_ocupados,
    -- Calcular slots libres
    FLOOR(
        EXTRACT(EPOCH FROM (upper(b.periodo) - lower(b.periodo))) / 60 / b.duracion_slot_minutos
    )::integer - (
        SELECT COUNT(*)
        FROM citas c
        WHERE c.id_podologo = b.id_podologo
          AND c.periodo && b.periodo
          AND c.estado NOT IN ('Cancelada', 'No_Asistio')
    ) AS slots_libres
FROM bloques_horario b
JOIN podologos p ON b.id_podologo = p.id
JOIN usuarios u ON p.id_usuario = u.id
WHERE b.tipo = 'trabajo'
ORDER BY b.fecha, b.id_podologo, lower(b.periodo);

COMMENT ON VIEW disponibilidad_bloques IS 'Vista de disponibilidad de bloques con cálculo de slots libres/ocupados';
