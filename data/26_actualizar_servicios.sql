-- ============================================================================
-- Actualizar duraciones de tratamientos y cargar servicios reales
-- ============================================================================

-- 1. Actualizar TODOS los tratamientos existentes a 60 minutos
UPDATE tratamientos 
SET duracion_minutos = 60
WHERE activo = true;

-- 2. Limpiar tratamientos de prueba si existen
DELETE FROM tratamientos WHERE codigo_servicio LIKE 'TEST%';

-- 3. Insertar servicios reales de la clínica
INSERT INTO tratamientos (codigo_servicio, nombre_servicio, descripcion, precio_base, duracion_minutos, requiere_consentimiento, activo)
VALUES
    ('CONS-VAL', 'Consulta de valoración', 'Evaluación inicial del paciente', 500.00, 60, false, true),
    ('ESPI', 'Espiculotomía (uña enterrada)', 'Procedimiento para uña encarnada sin anestesia', 500.00, 60, false, true),
    ('MATRI', 'Matricectomía (uña enterrada)', 'Cirugía menor para uña encarnada con anestesia', 1500.00, 60, true, true),
    ('VERR-PLANT', 'Verrugas plantares', 'Tratamiento de verrugas con anestesia', 1500.00, 60, true, true),
    ('PEDI-CLIN', 'Pedicure clínico', 'Pedicure médico profesional', 500.00, 60, false, true),
    ('PEDI-QUIM', 'Pedicure químico', 'Pedicure con productos químicos especializados', 800.00, 60, false, true),
    ('LASER-UVB', 'Láser UV-B (pie de atleta)', 'Tratamiento láser para hongos superficiales', 800.00, 60, false, true),
    ('LASER-ONICO', 'Láser antimicótico (onicomicosis)', 'Tratamiento láser para hongos en uñas', 800.00, 60, false, true)
ON CONFLICT (codigo_servicio) 
DO UPDATE SET
    nombre_servicio = EXCLUDED.nombre_servicio,
    descripcion = EXCLUDED.descripcion,
    precio_base = EXCLUDED.precio_base,
    duracion_minutos = EXCLUDED.duracion_minutos,
    requiere_consentimiento = EXCLUDED.requiere_consentimiento,
    activo = EXCLUDED.activo;

-- 4. Verificar resultados
SELECT 
    codigo_servicio,
    nombre_servicio,
    precio_base,
    duracion_minutos,
    requiere_consentimiento
FROM tratamientos
WHERE activo = true
ORDER BY precio_base;
