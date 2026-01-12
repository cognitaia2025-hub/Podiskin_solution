-- ============================================================================
-- Migración: Agregar Código de Paciente Personalizado
-- ============================================================================
-- Descripción: Agrega columna codigo_paciente con formato XX-XX-MM.DD-NNN
-- Fecha: 2026-01-09
-- ============================================================================

-- Paso 1: Agregar columna codigo_paciente
ALTER TABLE pacientes 
ADD COLUMN IF NOT EXISTS codigo_paciente VARCHAR(15) UNIQUE;

-- Paso 2: Crear índice para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_pacientes_codigo ON pacientes(codigo_paciente);

-- Paso 3: Agregar comentario descriptivo
COMMENT ON COLUMN pacientes.codigo_paciente IS 
'Código único legible: XX-XX-MM.DD-NNN (apellido-nombre-fecha-contador)';

-- Paso 4: Crear función para generar códigos
CREATE OR REPLACE FUNCTION generar_codigo_paciente(
    p_primer_nombre VARCHAR,
    p_primer_apellido VARCHAR,
    p_fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) RETURNS VARCHAR AS $$
DECLARE
    v_apellido_part VARCHAR(2);
    v_nombre_part VARCHAR(2);
    v_fecha_part VARCHAR(5);
    v_contador INTEGER;
    v_codigo VARCHAR(15);
    v_apellido_clean VARCHAR;
    v_nombre_clean VARCHAR;
BEGIN
    -- Limpiar y normalizar apellido (sin acentos, solo letras)
    v_apellido_clean := UPPER(
        REGEXP_REPLACE(
            TRANSLATE(
                p_primer_apellido, 
                'áéíóúñÁÉÍÓÚÑäëïöüÄËÏÖÜ', 
                'aeiounAEIOUNaeiouAEIOU'
            ),
            '[^A-Z]', '', 'g'
        )
    );
    
    -- Extraer últimas 2 letras del apellido
    IF LENGTH(v_apellido_clean) >= 2 THEN
        v_apellido_part := RIGHT(v_apellido_clean, 2);
    ELSIF LENGTH(v_apellido_clean) = 1 THEN
        v_apellido_part := v_apellido_clean || v_apellido_clean;
    ELSE
        v_apellido_part := 'XX';
    END IF;
    
    -- Limpiar y normalizar nombre (sin acentos, solo letras)
    v_nombre_clean := UPPER(
        REGEXP_REPLACE(
            TRANSLATE(
                p_primer_nombre, 
                'áéíóúñÁÉÍÓÚÑäëïöüÄËÏÖÜ', 
                'aeiounAEIOUNaeiouAEIOU'
            ),
            '[^A-Z]', '', 'g'
        )
    );
    
    -- Extraer últimas 2 letras del nombre
    IF LENGTH(v_nombre_clean) >= 2 THEN
        v_nombre_part := RIGHT(v_nombre_clean, 2);
    ELSIF LENGTH(v_nombre_clean) = 1 THEN
        v_nombre_part := v_nombre_clean || v_nombre_clean;
    ELSE
        v_nombre_part := 'XX';
    END IF;
    
    -- Formato de fecha MM.DD
    v_fecha_part := TO_CHAR(p_fecha_registro, 'MM.DD');
    
    -- Obtener contador del día (contar pacientes registrados el mismo día)
    SELECT COALESCE(COUNT(*), 0) + 1
    INTO v_contador
    FROM pacientes
    WHERE DATE(fecha_registro) = DATE(p_fecha_registro);
    
    -- Construir código final
    v_codigo := v_apellido_part || '-' || v_nombre_part || '-' || 
                v_fecha_part || '-' || LPAD(v_contador::TEXT, 3, '0');
    
    RETURN v_codigo;
END;
$$ LANGUAGE plpgsql;

-- Paso 5: Generar códigos para pacientes existentes (si los hay)
DO $$
DECLARE
    paciente_record RECORD;
    nuevo_codigo VARCHAR(15);
BEGIN
    FOR paciente_record IN 
        SELECT id, primer_nombre, primer_apellido, fecha_registro
        FROM pacientes
        WHERE codigo_paciente IS NULL
        ORDER BY fecha_registro ASC
    LOOP
        -- Generar código usando la función
        nuevo_codigo := generar_codigo_paciente(
            paciente_record.primer_nombre,
            paciente_record.primer_apellido,
            paciente_record.fecha_registro
        );
        
        -- Actualizar paciente
        UPDATE pacientes
        SET codigo_paciente = nuevo_codigo
        WHERE id = paciente_record.id;
        
        RAISE NOTICE 'Código generado para paciente %: %', 
                     paciente_record.id, nuevo_codigo;
    END LOOP;
END $$;

-- Paso 6: Verificar resultados
SELECT 
    COUNT(*) as total_pacientes,
    COUNT(codigo_paciente) as pacientes_con_codigo,
    COUNT(*) - COUNT(codigo_paciente) as pacientes_sin_codigo
FROM pacientes;

-- Mostrar ejemplos de códigos generados
SELECT 
    id,
    codigo_paciente,
    primer_nombre,
    primer_apellido,
    fecha_registro
FROM pacientes
ORDER BY fecha_registro DESC
LIMIT 10;
