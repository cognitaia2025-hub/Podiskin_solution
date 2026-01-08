-- ============================================================================
-- MIGRACIÓN 16: Mejoras de Inventario y Gastos
-- ============================================================================
-- Fecha: 06/01/2026
-- Objetivo: Implementar mejoras basadas en operación real del cliente Santiago
-- 
-- Cambios incluidos:
-- 1. Migrar tabla servicios (anestesia, sesiones, categoría)
-- 2. Crear ENUM y migrar tabla gastos (categorización de gastos)
-- 3. Migrar tabla inventario (unidades de medida, cantidad por unidad, categoría)
-- 4. Crear tabla gastos_inventario (vinculación gastos ↔ inventario)
-- 5. Insertar 8 servicios del cliente como cortesía
-- ============================================================================

BEGIN;

-- ============================================================================
-- PARTE 1: MIGRACIÓN DE TABLA SERVICIOS
-- ============================================================================
-- Agregar campos para mejorar gestión de servicios

ALTER TABLE catalogo_servicios 
ADD COLUMN IF NOT EXISTS requiere_anestesia BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS sesiones_estimadas VARCHAR(20) DEFAULT '1',
ADD COLUMN IF NOT EXISTS categoria_servicio VARCHAR(50);

COMMENT ON COLUMN catalogo_servicios.requiere_anestesia IS 'Indica si el servicio requiere anestesia local';
COMMENT ON COLUMN catalogo_servicios.sesiones_estimadas IS 'Número de sesiones estimadas o "variable"';
COMMENT ON COLUMN catalogo_servicios.categoria_servicio IS 'Categoría del servicio: Consulta, Procedimiento, Cirugía, Estético, Láser';

-- ============================================================================
-- PARTE 2: CATEGORIZACIÓN DE GASTOS
-- ============================================================================
-- Crear ENUM para categorías de gastos y agregar campo a tabla gastos

-- Crear tipo ENUM para categorías de gastos
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'categoria_gasto_enum') THEN
        CREATE TYPE categoria_gasto_enum AS ENUM (
            'SERVICIOS_BASICOS',      -- Luz, agua, internet
            'SERVICIOS_PROFESIONALES', -- Contabilidad, asesoría legal
            'RENTA_LOCAL',             -- Renta del consultorio
            'MATERIAL_MEDICO',         -- Gasas, guantes, jeringas, hojas bisturí
            'MEDICAMENTOS',            -- Lidocaína, benzocaína, anestésicos
            'LIMPIEZA',                -- Lysol, toallas, sanitas, desinfectantes
            'CAFETERIA',               -- Café, vasos, servilletas, agua
            'MANTENIMIENTO',           -- Reparaciones, WD-40, herramientas
            'OTROS'                    -- Gastos no clasificados
        );
    END IF;
END $$;

-- Agregar campo categoría a tabla gastos
ALTER TABLE gastos 
ADD COLUMN IF NOT EXISTS categoria categoria_gasto_enum DEFAULT 'OTROS';

COMMENT ON COLUMN gastos.categoria IS 'Categoría del gasto para análisis financiero';

-- ============================================================================
-- PARTE 3: UNIDADES DE MEDIDA EN INVENTARIO
-- ============================================================================
-- Crear ENUM para categorías de productos y agregar campos a inventario

-- Crear tipo ENUM para categorías de productos
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'categoria_producto_enum') THEN
        CREATE TYPE categoria_producto_enum AS ENUM (
            'INSTRUMENTAL_MEDICO',    -- Tijeras, pinzas, mangos bisturí
            'CONSUMIBLES_MEDICOS',    -- Gasas, jeringas, hojas bisturí
            'MEDICAMENTOS',           -- Lidocaína, benzocaína
            'LIMPIEZA',               -- Lysol, toallas, sanitas
            'CAFETERIA',              -- Café, vasos, servilletas
            'EQUIPO_LASER',           -- Láseres, lentes protectores
            'OFICINA'                 -- Folders, plumas, papelería
        );
    END IF;
END $$;

-- Agregar campos a tabla inventario
ALTER TABLE inventario_productos 
ADD COLUMN IF NOT EXISTS unidad_medida VARCHAR(20) 
    CHECK (unidad_medida IN (
        'PZA',      -- Piezas (gasas, jeringas, hojas bisturí)
        'CAJA',     -- Cajas (guantes, cubrebocas)
        'LITRO',    -- Litros (alcohol, químicos líquidos)
        'KG',       -- Kilogramos (café, azúcar)
        'BOTELLA',  -- Botellas (cuando no se mide en litros exactos)
        'ROLLO',    -- Rollos (film, toallas de papel)
        'BOLSA',    -- Bolsas (servilletas, vasos desechables)
        'UNIDAD'    -- Unidad (drill, extintor, aparatos)
    )),
ADD COLUMN IF NOT EXISTS cantidad_por_unidad INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS categoria categoria_producto_enum;

COMMENT ON COLUMN inventario_productos.unidad_medida IS 'Unidad de medida del producto';
COMMENT ON COLUMN inventario_productos.cantidad_por_unidad IS 'Para cajas/bolsas: cantidad de piezas por unidad contenedora';
COMMENT ON COLUMN inventario_productos.categoria IS 'Categoría del producto para filtros y reportes';

-- ============================================================================
-- PARTE 4: TABLA DE VINCULACIÓN GASTOS ↔ INVENTARIO
-- ============================================================================
-- Crear tabla para vincular gastos con productos del inventario

CREATE TABLE IF NOT EXISTS gastos_inventario (
    id SERIAL PRIMARY KEY,
    gasto_id INTEGER NOT NULL REFERENCES gastos(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL REFERENCES inventario_productos(id) ON DELETE RESTRICT,
    cantidad_comprada DECIMAL(10,2) NOT NULL CHECK (cantidad_comprada > 0),
    precio_unitario DECIMAL(10,2) NOT NULL CHECK (precio_unitario >= 0),
    fecha_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_gasto_producto UNIQUE (gasto_id, producto_id)
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_gastos_inventario_gasto ON gastos_inventario(gasto_id);
CREATE INDEX IF NOT EXISTS idx_gastos_inventario_producto ON gastos_inventario(producto_id);
CREATE INDEX IF NOT EXISTS idx_gastos_inventario_fecha ON gastos_inventario(fecha_entrada);

COMMENT ON TABLE gastos_inventario IS 'Vincula gastos con productos del inventario para trazabilidad';
COMMENT ON COLUMN gastos_inventario.cantidad_comprada IS 'Cantidad de producto comprada en esta compra';
COMMENT ON COLUMN gastos_inventario.precio_unitario IS 'Precio unitario de compra para análisis histórico';

-- ============================================================================
-- PARTE 5: CARGA INICIAL DE SERVICIOS DEL CLIENTE
-- ============================================================================
-- Insertar 8 servicios operados por la clínica Podoskin

-- Verificar si ya existen servicios para evitar duplicados
DO $$
BEGIN
    -- Solo insertar si la tabla servicios está vacía o no tiene estos servicios
    IF NOT EXISTS (SELECT 1 FROM catalogo_servicios WHERE nombre = 'Consulta de valoración') THEN
        
        INSERT INTO catalogo_servicios (
            nombre, 
            descripcion, 
            precio, 
            duracion_minutos, 
            requiere_anestesia, 
            sesiones_estimadas, 
            categoria_servicio
        ) VALUES 
        
        -- Servicios de consulta
        (
            'Consulta de valoración',
            'Evaluación inicial del paciente, diagnóstico preliminar y plan de tratamiento',
            500.00,
            30,
            FALSE,
            '1',
            'Consulta'
        ),
        
        -- Procedimientos básicos
        (
            'Espiculotomía (uña enterrada)',
            'Extracción de espícula de uña enterrada sin anestesia',
            500.00,
            30,
            FALSE,
            '1',
            'Procedimiento'
        ),
        
        -- Cirugías menores
        (
            'Matricectomía (uña enterrada)',
            'Cirugía de uña enterrada con matricectomía parcial o total',
            1500.00,
            60,
            TRUE,
            '1',
            'Cirugía menor'
        ),
        (
            'Tratamiento de verrugas plantares',
            'Remoción de verrugas plantares mediante cirugía menor',
            1500.00,
            45,
            TRUE,
            '1',
            'Cirugía menor'
        ),
        
        -- Servicios estéticos
        (
            'Pedicure clínico',
            'Pedicure especializado con técnicas podológicas para pies sanos',
            500.00,
            45,
            FALSE,
            '1',
            'Estético'
        ),
        (
            'Pedicure químico',
            'Pedicure especializado con productos químicos para callosidades severas',
            800.00,
            60,
            FALSE,
            '1',
            'Estético'
        ),
        
        -- Tratamientos con láser
        (
            'Láser UV-B (pie de atleta)',
            'Tratamiento con láser ultravioleta para pie de atleta y hongos superficiales',
            800.00,
            30,
            FALSE,
            'variable',
            'Láser'
        ),
        (
            'Láser antimicótico (onicomicosis)',
            'Tratamiento con láser para hongos en uñas - requiere múltiples sesiones',
            800.00,
            30,
            FALSE,
            'variable',
            'Láser'
        );
        
        RAISE NOTICE 'Se insertaron 8 servicios del cliente Santiago';
    ELSE
        RAISE NOTICE 'Los servicios ya existen, se omitió la inserción';
    END IF;
END $$;

-- ============================================================================
-- PARTE 6: VERIFICACIÓN DE MIGRACIÓN
-- ============================================================================

-- Verificar columnas agregadas a servicios
DO $$
DECLARE
    col_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns
    WHERE table_name = 'catalogo_servicios' 
    AND column_name IN ('requiere_anestesia', 'sesiones_estimadas', 'categoria_servicio');
    
    IF col_count = 3 THEN
        RAISE NOTICE '✓ Tabla catalogo_servicios migrada correctamente (3 columnas agregadas)';
    ELSE
        RAISE WARNING '⚠ Tabla catalogo_servicios: esperadas 3 columnas, encontradas %', col_count;
    END IF;
END $$;

-- Verificar columnas agregadas a gastos
DO $$
DECLARE
    col_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'gastos' AND column_name = 'categoria'
    ) INTO col_exists;
    
    IF col_exists THEN
        RAISE NOTICE '✓ Tabla gastos migrada correctamente (columna categoria agregada)';
    ELSE
        RAISE WARNING '⚠ Tabla gastos: columna categoria no encontrada';
    END IF;
END $$;

-- Verificar columnas agregadas a inventario
DO $$
DECLARE
    col_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns
    WHERE table_name = 'inventario_productos' 
    AND column_name IN ('unidad_medida', 'cantidad_por_unidad', 'categoria');
    
    IF col_count = 3 THEN
        RAISE NOTICE '✓ Tabla inventario_productos migrada correctamente (3 columnas agregadas)';
    ELSE
        RAISE WARNING '⚠ Tabla inventario_productos: esperadas 3 columnas, encontradas %', col_count;
    END IF;
END $$;

-- Verificar creación de tabla gastos_inventario
DO $$
DECLARE
    table_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'gastos_inventario'
    ) INTO table_exists;
    
    IF table_exists THEN
        RAISE NOTICE '✓ Tabla gastos_inventario creada correctamente';
    ELSE
        RAISE WARNING '⚠ Tabla gastos_inventario no fue creada';
    END IF;
END $$;

-- Verificar servicios insertados
DO $$
DECLARE
    service_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO service_count
    FROM catalogo_servicios
    WHERE nombre IN (
        'Consulta de valoración',
        'Espiculotomía (uña enterrada)',
        'Matricectomía (uña enterrada)',
        'Tratamiento de verrugas plantares',
        'Pedicure clínico',
        'Pedicure químico',
        'Láser UV-B (pie de atleta)',
        'Láser antimicótico (onicomicosis)'
    );
    
    IF service_count = 8 THEN
        RAISE NOTICE '✓ 8 servicios del cliente insertados correctamente';
    ELSE
        RAISE NOTICE '⚠ Servicios encontrados: % (esperados: 8)', service_count;
    END IF;
END $$;

-- ============================================================================
-- RESUMEN DE MIGRACIÓN
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════';
    RAISE NOTICE '  MIGRACIÓN 16 COMPLETADA EXITOSAMENTE';
    RAISE NOTICE '═══════════════════════════════════════════════════════════';
    RAISE NOTICE '';
    RAISE NOTICE 'Cambios aplicados:';
    RAISE NOTICE '  ✓ Tabla catalogo_servicios: +3 columnas (anestesia, sesiones, categoría)';
    RAISE NOTICE '  ✓ Tabla gastos: +1 columna (categoría con 9 opciones)';
    RAISE NOTICE '  ✓ Tabla inventario_productos: +3 columnas (unidad, cantidad_por_unidad, categoría)';
    RAISE NOTICE '  ✓ Nueva tabla: gastos_inventario (vinculación)';
    RAISE NOTICE '  ✓ 8 servicios del cliente insertados';
    RAISE NOTICE '';
    RAISE NOTICE 'ENUMs creados:';
    RAISE NOTICE '  • categoria_gasto_enum (9 valores)';
    RAISE NOTICE '  • categoria_producto_enum (7 valores)';
    RAISE NOTICE '';
    RAISE NOTICE 'Siguiente paso: Actualizar modelos Pydantic en backend';
    RAISE NOTICE '═══════════════════════════════════════════════════════════';
END $$;

COMMIT;
