-- ============================================================================
-- Archivo: load_all.sql
-- Descripción: Script maestro para cargar TODOS los datos mock en orden
-- Autor: Sistema de Agentes de Desarrollo
-- Fecha: 2026-01-01
-- ============================================================================
-- 
-- PREREQUISITOS:
--   1. Las tablas de la base de datos deben estar creadas
--   2. La base de datos debe estar vacía o limpia
--   3. Ejecutar desde el directorio data/seed/
--
-- EJECUCIÓN:
--   psql -U postgres -d podoskin -f load_all.sql
--
-- ORDEN DE CARGA:
--   1. Usuarios y configuración (Agente 13)
--   2. Pacientes (Agente 14)
--   3. Citas y tratamientos (Agente 15)
--   4. Pagos e inventario (Agente 16)
-- ============================================================================

\echo ''
\echo '╔════════════════════════════════════════════════════════════════════╗'
\echo '║                                                                    ║'
\echo '║          SISTEMA DE CARGA DE DATOS MOCK - PODOSKIN SOLUTION       ║'
\echo '║                                                                    ║'
\echo '╚════════════════════════════════════════════════════════════════════╝'
\echo ''

-- Configurar mensajes informativos
\set ON_ERROR_STOP on
\set VERBOSITY verbose

\echo '⏱️  Inicio de carga: ' :DATE

-- ============================================================================
-- VALIDACIONES INICIALES
-- ============================================================================

\echo ''
\echo '🔍 Validando prerequisitos...'
\echo ''

DO $$
BEGIN
    -- Verificar que existan las tablas principales
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'usuarios') THEN
        RAISE EXCEPTION '❌ ERROR: Tabla usuarios no existe. Ejecuta los scripts de creación de tablas primero.';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pacientes') THEN
        RAISE EXCEPTION '❌ ERROR: Tabla pacientes no existe. Ejecuta los scripts de creación de tablas primero.';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'citas') THEN
        RAISE EXCEPTION '❌ ERROR: Tabla citas no existe. Ejecuta los scripts de creación de tablas primero.';
    END IF;
    
    RAISE NOTICE '✅ Todas las tablas requeridas existen';
END $$;

-- ============================================================================
-- SCRIPT 1: USUARIOS Y CONFIGURACIÓN (Agente 13)
-- ============================================================================

\echo ''
\echo '╔════════════════════════════════════════════════════════════════════╗'
\echo '║  📝 EJECUTANDO: 01_usuarios_config.sql (Agente 13/16)             ║'
\echo '╚════════════════════════════════════════════════════════════════════╝'
\echo ''

\i 01_usuarios_config.sql

\echo ''
\echo '✅ Script 1 completado'
\echo ''

-- ============================================================================
-- SCRIPT 2: PACIENTES (Agente 14)
-- ============================================================================

\echo ''
\echo '╔════════════════════════════════════════════════════════════════════╗'
\echo '║  📝 EJECUTANDO: 02_pacientes.sql (Agente 14/16)                   ║'
\echo '╚════════════════════════════════════════════════════════════════════╝'
\echo ''

\i 02_pacientes.sql

\echo ''
\echo '✅ Script 2 completado'
\echo ''

-- ============================================================================
-- SCRIPT 3: CITAS Y TRATAMIENTOS (Agente 15)
-- ============================================================================

\echo ''
\echo '╔════════════════════════════════════════════════════════════════════╗'
\echo '║  📝 EJECUTANDO: 03_citas_tratamientos.sql (Agente 15/16)          ║'
\echo '╚════════════════════════════════════════════════════════════════════╝'
\echo ''

\i 03_citas_tratamientos.sql

\echo ''
\echo '✅ Script 3 completado'
\echo ''

-- ============================================================================
-- SCRIPT 4: PAGOS E INVENTARIO (Agente 16)
-- ============================================================================

\echo ''
\echo '╔════════════════════════════════════════════════════════════════════╗'
\echo '║  📝 EJECUTANDO: 04_pagos_inventario.sql (Agente 16/16)            ║'
\echo '╚════════════════════════════════════════════════════════════════════╝'
\echo ''

\i 04_pagos_inventario.sql

\echo ''
\echo '✅ Script 4 completado'
\echo ''

-- ============================================================================
-- RESUMEN FINAL
-- ============================================================================

\echo ''
\echo '╔════════════════════════════════════════════════════════════════════╗'
\echo '║                                                                    ║'
\echo '║                    ✅ CARGA COMPLETADA EXITOSAMENTE                ║'
\echo '║                                                                    ║'
\echo '╚════════════════════════════════════════════════════════════════════╝'
\echo ''

-- Mostrar resumen de datos cargados
SELECT 
    '📊 RESUMEN DE DATOS CARGADOS' as titulo;

SELECT 
    'Usuarios' as tabla,
    COUNT(*) as registros
FROM usuarios
UNION ALL
SELECT 'Pacientes', COUNT(*) FROM pacientes
UNION ALL
SELECT 'Citas', COUNT(*) FROM citas
UNION ALL
SELECT 'Pagos', COUNT(*) FROM pagos
UNION ALL
SELECT 'Productos Inventario', COUNT(*) FROM inventario_productos
ORDER BY tabla;

\echo ''
\echo '⏱️  Fin de carga: ' :DATE
\echo ''
\echo '📝 SIGUIENTE PASO:'
\echo '   Para limpiar datos mock y conservar solo usuarios reales:'
\echo '   psql -U postgres -d podoskin -f clean_mock_data.sql'
\echo ''

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================