-- =====================================================
-- Migración: Agregar campos faltantes a tabla citas
-- Fecha: 2026-01-12
-- Descripción: Agrega campos motivo_consulta y color
--              para alinear con el frontend
-- =====================================================

-- Agregar campo motivo_consulta
ALTER TABLE citas 
ADD COLUMN IF NOT EXISTS motivo_consulta TEXT;

-- Agregar campo color (formato HEX #RRGGBB)
ALTER TABLE citas 
ADD COLUMN IF NOT EXISTS color VARCHAR(7) 
CHECK (color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$');

-- Comentarios para documentación
COMMENT ON COLUMN citas.motivo_consulta IS 'Motivo principal de la consulta descrito por el paciente o recepcionista';
COMMENT ON COLUMN citas.color IS 'Color personalizado para la cita en formato HEX (#RRGGBB) para visualización en calendario';

-- Índice para búsqueda por motivo_consulta (opcional pero recomendado)
CREATE INDEX IF NOT EXISTS idx_citas_motivo_consulta_gin 
ON citas USING gin (to_tsvector('spanish', motivo_consulta));

-- Log de migración
DO $$
BEGIN
    RAISE NOTICE 'Migración 20260112_add_citas_fields.sql completada exitosamente';
    RAISE NOTICE 'Agregados campos: motivo_consulta (TEXT), color (VARCHAR(7))';
END $$;
