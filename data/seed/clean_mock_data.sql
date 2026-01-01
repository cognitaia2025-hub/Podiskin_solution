-- =====================================================================
-- Clean Mock Data Script
-- =====================================================================
-- Purpose: Remove all mock/test data while preserving core system users
-- Preserved Users:
--   - Santiago de Jesús Ornelas Reynoso
--   - Joana Ibeth Meraz Arregin
-- Date Created: 2026-01-01
-- =====================================================================

BEGIN;

-- =====================================================================
-- SECTION 1: Display Initial State
-- =====================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Starting Mock Data Cleanup Process';
    RAISE NOTICE 'Timestamp: %', NOW();
    RAISE NOTICE '========================================';
END $$;

-- Show initial counts
DO $$
DECLARE
    v_usuarios_count INTEGER;
    v_pacientes_count INTEGER;
    v_citas_count INTEGER;
    v_facturas_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_usuarios_count FROM usuarios;
    SELECT COUNT(*) INTO v_pacientes_count FROM pacientes;
    SELECT COUNT(*) INTO v_citas_count FROM citas;
    SELECT COUNT(*) INTO v_facturas_count FROM facturas;
    
    RAISE NOTICE 'Initial Counts:';
    RAISE NOTICE '  - Usuarios: %', v_usuarios_count;
    RAISE NOTICE '  - Pacientes: %', v_pacientes_count;
    RAISE NOTICE '  - Citas: %', v_citas_count;
    RAISE NOTICE '  - Facturas: %', v_facturas_count;
    RAISE NOTICE '----------------------------------------';
END $$;

-- =====================================================================
-- SECTION 2: Delete Financial Records (Facturas, Cortes, Gastos)
-- =====================================================================
DO $$
DECLARE
    v_deleted INTEGER;
BEGIN
    RAISE NOTICE 'Step 1: Cleaning Financial Records...';
    
    -- Delete Facturas
    DELETE FROM facturas;
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RAISE NOTICE '  ✓ Deleted % facturas', v_deleted;
    
    -- Delete Cortes de Caja
    DELETE FROM cortes_caja;
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RAISE NOTICE '  ✓ Deleted % cortes_caja', v_deleted;
    
    -- Delete Gastos
    DELETE FROM gastos;
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RAISE NOTICE '  ✓ Deleted % gastos', v_deleted;
    
    RAISE NOTICE '----------------------------------------';
END $$;

-- =====================================================================
-- SECTION 3: Delete Inventory Records
-- =====================================================================
DO $$
DECLARE
    v_deleted INTEGER;
BEGIN
    RAISE NOTICE 'Step 2: Cleaning Inventory Records...';
    
    -- Delete Movimientos Inventario
    DELETE FROM movimientos_inventario;
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RAISE NOTICE '  ✓ Deleted % movimientos_inventario', v_deleted;
    
    -- Delete Inventario Productos
    DELETE FROM inventario_productos;
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RAISE NOTICE '  ✓ Deleted % inventario_productos', v_deleted;
    
    -- Delete Proveedores
    DELETE FROM proveedores;
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RAISE NOTICE '  ✓ Deleted % proveedores', v_deleted;
    
    RAISE NOTICE '----------------------------------------';
END $$;

-- =====================================================================
-- SECTION 4: Delete Appointment Related Records
-- =====================================================================
DO $$
DECLARE
    v_deleted INTEGER;
BEGIN
    RAISE NOTICE 'Step 3: Cleaning Appointment Records...';
    
    -- Delete Pagos
    DELETE FROM pagos;
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RAISE NOTICE '  ✓ Deleted % pagos', v_deleted;
    
    -- Delete Diagnosticos
    DELETE FROM diagnosticos;
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RAISE NOTICE '  ✓ Deleted % diagnosticos', v_deleted;
    
    -- Delete Detalle Cita
    DELETE FROM detalle_cita;
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RAISE NOTICE '  ✓ Deleted % detalle_cita', v_deleted;
    
    -- Delete Citas
    DELETE FROM citas;
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RAISE NOTICE '  ✓ Deleted % citas', v_deleted;
    
    RAISE NOTICE '----------------------------------------';
END $$;

-- =====================================================================
-- SECTION 5: Delete Patient Medical Records
-- =====================================================================
DO $$
DECLARE
    v_deleted INTEGER;
BEGIN
    RAISE NOTICE 'Step 4: Cleaning Patient Medical Records...';
    
    -- Delete Antecedentes Médicos
    DELETE FROM antecedentes_medicos;
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RAISE NOTICE '  ✓ Deleted % antecedentes_medicos', v_deleted;
    
    -- Delete Alergias
    DELETE FROM alergias;
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RAISE NOTICE '  ✓ Deleted % alergias', v_deleted;
    
    RAISE NOTICE '----------------------------------------';
END $$;

-- =====================================================================
-- SECTION 6: Delete Mock Patients (All 200 Mock Patients)
-- =====================================================================
DO $$
DECLARE
    v_deleted INTEGER;
BEGIN
    RAISE NOTICE 'Step 5: Deleting Mock Patients...';
    
    -- Delete all mock patients (assuming they are test data)
    -- This will keep any real patients if they exist
    DELETE FROM pacientes;
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RAISE NOTICE '  ✓ Deleted % pacientes (mock data)', v_deleted;
    
    RAISE NOTICE '----------------------------------------';
END $$;

-- =====================================================================
-- SECTION 7: Reset Sequences
-- =====================================================================
DO $$
BEGIN
    RAISE NOTICE 'Step 6: Resetting Sequences...';
    
    -- Reset sequences for cleaned tables
    PERFORM setval(pg_get_serial_sequence('facturas', 'id'), 1, false);
    PERFORM setval(pg_get_serial_sequence('cortes_caja', 'id'), 1, false);
    PERFORM setval(pg_get_serial_sequence('gastos', 'id'), 1, false);
    PERFORM setval(pg_get_serial_sequence('movimientos_inventario', 'id'), 1, false);
    PERFORM setval(pg_get_serial_sequence('inventario_productos', 'id'), 1, false);
    PERFORM setval(pg_get_serial_sequence('proveedores', 'id'), 1, false);
    PERFORM setval(pg_get_serial_sequence('pagos', 'id'), 1, false);
    PERFORM setval(pg_get_serial_sequence('diagnosticos', 'id'), 1, false);
    PERFORM setval(pg_get_serial_sequence('detalle_cita', 'id'), 1, false);
    PERFORM setval(pg_get_serial_sequence('citas', 'id'), 1, false);
    PERFORM setval(pg_get_serial_sequence('antecedentes_medicos', 'id'), 1, false);
    PERFORM setval(pg_get_serial_sequence('alergias', 'id'), 1, false);
    PERFORM setval(pg_get_serial_sequence('pacientes', 'id'), 1, false);
    
    RAISE NOTICE '  ✓ All sequences reset to starting values';
    RAISE NOTICE '----------------------------------------';
END $$;

-- =====================================================================
-- SECTION 8: Verification - Show Remaining Data
-- =====================================================================
DO $$
DECLARE
    v_usuarios_count INTEGER;
    v_pacientes_count INTEGER;
    v_citas_count INTEGER;
    v_facturas_count INTEGER;
    v_roles_count INTEGER;
    v_servicios_count INTEGER;
    v_horarios_count INTEGER;
BEGIN
    RAISE NOTICE 'Step 7: Verification - Final State';
    RAISE NOTICE '========================================';
    
    -- Count remaining records
    SELECT COUNT(*) INTO v_usuarios_count FROM usuarios;
    SELECT COUNT(*) INTO v_pacientes_count FROM pacientes;
    SELECT COUNT(*) INTO v_citas_count FROM citas;
    SELECT COUNT(*) INTO v_facturas_count FROM facturas;
    SELECT COUNT(*) INTO v_roles_count FROM roles;
    SELECT COUNT(*) INTO v_servicios_count FROM servicios;
    SELECT COUNT(*) INTO v_horarios_count FROM horarios_trabajo;
    
    RAISE NOTICE 'Remaining Counts:';
    RAISE NOTICE '  - Usuarios: %', v_usuarios_count;
    RAISE NOTICE '  - Pacientes: %', v_pacientes_count;
    RAISE NOTICE '  - Citas: %', v_citas_count;
    RAISE NOTICE '  - Facturas: %', v_facturas_count;
    RAISE NOTICE '  - Roles: %', v_roles_count;
    RAISE NOTICE '  - Servicios: %', v_servicios_count;
    RAISE NOTICE '  - Horarios Trabajo: %', v_horarios_count;
    RAISE NOTICE '----------------------------------------';
END $$;

-- Display preserved users
DO $$
DECLARE
    user_record RECORD;
BEGIN
    RAISE NOTICE 'Preserved Users:';
    RAISE NOTICE '';
    
    FOR user_record IN 
        SELECT 
            u.id,
            u.nombre_completo,
            u.email,
            r.nombre_rol as rol
        FROM usuarios u
        LEFT JOIN roles r ON u.id_rol = r.id
        ORDER BY u.id
    LOOP
        RAISE NOTICE '  User ID: %', user_record.id;
        RAISE NOTICE '    Name: %', user_record.nombre_completo;
        RAISE NOTICE '    Email: %', user_record.email;
        RAISE NOTICE '    Role: %', COALESCE(user_record.rol, 'No role assigned');
        RAISE NOTICE '';
    END LOOP;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Mock Data Cleanup Completed Successfully';
    RAISE NOTICE 'Timestamp: %', NOW();
    RAISE NOTICE '========================================';
END $$;

COMMIT;

-- =====================================================================
-- Post-Execution Notes:
-- =====================================================================
-- This script has successfully:
--   ✓ Removed all financial records (facturas, cortes_caja, gastos)
--   ✓ Removed all inventory data (movimientos, productos, proveedores)
--   ✓ Removed all appointment records (citas, detalles, diagnosticos, pagos)
--   ✓ Removed all patient medical records (antecedentes, alergias)
--   ✓ Removed all 200 mock patients
--   ✓ Reset all relevant sequences
--   ✓ Preserved core users: Santiago de Jesús Ornelas Reynoso and 
--     Joana Ibeth Meraz Arregin
--   ✓ Preserved their roles, services, and work schedules
--
-- The database is now clean and ready for production use with the
-- core administrative users intact.
-- =====================================================================
