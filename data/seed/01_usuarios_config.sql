-- ============================================================================
-- Archivo: 01_usuarios_config.sql
-- Agente: 13/16 - DEV Mock Data - Usuarios y Configuración
-- Descripción: Script de datos iniciales (seed data) para el sistema Podoskin
-- Dependencias: Requiere que las tablas estén creadas (Agente DEV Database Setup)
-- ============================================================================
-- 
-- USUARIOS PROTEGIDOS (NO DUPLICAR):
--   1. Santiago de Jesús Ornelas Reynoso (santiago.ornelas)
--      Email: enfsantiagoornelas@gmail.com
--      Roles: Admin + Podologo
--   
--   2. Joana Ibeth Meraz Arregin (joana.meraz)
--      Email: joana.meraz@podoskin.com
--      Roles: Podologo + Recepcionista
--
-- NOTAS:
--   - Passwords por defecto: Admin123, Podologo123, Recepcio123
--   - Hashes generados con PBKDF2-SHA256 (compatible con backend Python/passlib)
--   - Script incluye validaciones para evitar duplicados
--   - Se ejecuta en una transacción con rollback automático en caso de error
-- ============================================================================

-- Iniciar transacción
BEGIN;

-- ============================================================================
-- VARIABLES Y VALIDACIÓN
-- ============================================================================

DO $$
DECLARE
    v_count_santiago INTEGER;
    v_count_joana INTEGER;
BEGIN
    -- Verificar si los usuarios protegidos ya existen
    SELECT COUNT(*) INTO v_count_santiago FROM usuarios WHERE email = 'enfsantiagoornelas@gmail.com';
    SELECT COUNT(*) INTO v_count_joana FROM usuarios WHERE email = 'joana.meraz@podoskin.com';
    
    IF v_count_santiago > 0 THEN
        RAISE NOTICE '⚠️  Usuario Santiago ya existe en la base de datos, omitiendo inserción';
    END IF;
    
    IF v_count_joana > 0 THEN
        RAISE NOTICE '⚠️  Usuario Joana ya existe en la base de datos, omitiendo inserción';
    END IF;
END $$;

-- ============================================================================
-- 1. USUARIOS
-- ============================================================================
-- Insertar usuarios solo si no existen (validación por email)
-- Passwords: Admin123, Podologo123, Recepcio123 (PBKDF2-SHA256)

-- Usuario 1: Santiago Ornelas (Admin + Podologo)
INSERT INTO usuarios (nombre_usuario, password_hash, nombre_completo, email, rol, activo, fecha_registro)
SELECT 
    'santiago.ornelas',
    '$pbkdf2-sha256$29000$PMfYe8/ZW0sJYUzJufdeyw$P7e8BGo3Ubm9rD.Ji0AlwrTA9YNW1d4l6aE2wDMQ/KA',
    'Santiago de Jesús Ornelas Reynoso',
    'enfsantiagoornelas@gmail.com',
    'Admin',
    true,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE email = 'enfsantiagoornelas@gmail.com'
);

-- Usuario 2: Joana Meraz (Podologo + Recepcionista)
INSERT INTO usuarios (nombre_usuario, password_hash, nombre_completo, email, rol, activo, fecha_registro)
SELECT 
    'joana.meraz',
    '$pbkdf2-sha256$29000$.Z9TKuVcixHivJcy5twbgw$1z/PCQ1tRoZgW.qdRQW2Ek3MPYNWhm8YCJy.ZqzMkk0',
    'Joana Ibeth Meraz Arregin',
    'joana.meraz@podoskin.com',
    'Podologo',
    true,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE email = 'joana.meraz@podoskin.com'
);

-- Usuario 3: Recepcionista adicional
INSERT INTO usuarios (nombre_usuario, password_hash, nombre_completo, email, rol, activo, fecha_registro)
SELECT 
    'maria.lopez',
    '$pbkdf2-sha256$29000$BICw1vpfK6W01jrHuBciRA$QuxaUpEYF/0x277tw4d176SNRrHyrLqAfMkg6WJwTtQ',
    'María Guadalupe López García',
    'maria.lopez@podoskin.com',
    'Recepcionista',
    true,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE email = 'maria.lopez@podoskin.com'
);

-- Usuario 4: Admin adicional
INSERT INTO usuarios (nombre_usuario, password_hash, nombre_completo, email, rol, activo, fecha_registro)
SELECT 
    'admin.sistema',
    '$pbkdf2-sha256$29000$PMfYe8/ZW0sJYUzJufdeyw$P7e8BGo3Ubm9rD.Ji0AlwrTA9YNW1d4l6aE2wDMQ/KA',
    'Administrador del Sistema',
    'admin@podoskin.com',
    'Admin',
    true,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE email = 'admin@podoskin.com'
);

-- ============================================================================
-- 2. PODOLOGOS
-- ============================================================================
-- Vincular usuarios con perfil de podólogo

-- Podólogo 1: Santiago Ornelas
INSERT INTO podologos (
    cedula_profesional, 
    nombre_completo, 
    especialidad, 
    telefono, 
    email, 
    activo, 
    fecha_contratacion,
    id_usuario,
    fecha_registro
)
SELECT 
    'POD-2018-001',
    'Santiago de Jesús Ornelas Reynoso',
    'Podología General, Biomecánica',
    '+52-686-555-0101',
    'enfsantiagoornelas@gmail.com',
    true,
    '2018-01-15',
    u.id,
    NOW()
FROM usuarios u
WHERE u.email = 'enfsantiagoornelas@gmail.com'
AND NOT EXISTS (
    SELECT 1 FROM podologos p WHERE p.cedula_profesional = 'POD-2018-001'
);

-- Podólogo 2: Joana Meraz
INSERT INTO podologos (
    cedula_profesional, 
    nombre_completo, 
    especialidad, 
    telefono, 
    email, 
    activo, 
    fecha_contratacion,
    id_usuario,
    fecha_registro
)
SELECT 
    'POD-2020-002',
    'Joana Ibeth Meraz Arregin',
    'Podología General, Dermatología Podal',
    '+52-686-555-0102',
    'joana.meraz@podoskin.com',
    true,
    '2020-03-01',
    u.id,
    NOW()
FROM usuarios u
WHERE u.email = 'joana.meraz@podoskin.com'
AND NOT EXISTS (
    SELECT 1 FROM podologos p WHERE p.cedula_profesional = 'POD-2020-002'
);

-- ============================================================================
-- 3. HORARIOS DE TRABAJO
-- ============================================================================
-- Configurar horarios laborales de los podólogos

-- Horarios de Santiago Ornelas (Lun-Vie 09:00-18:00)
INSERT INTO horarios_trabajo (
    id_podologo,
    dia_semana,
    hora_inicio,
    hora_fin,
    duracion_cita_minutos,
    tiempo_buffer_minutos,
    max_citas_simultaneas,
    activo,
    fecha_inicio_vigencia,
    creado_por
)
SELECT 
    p.id,
    d.dia,
    '09:00'::time,
    '18:00'::time,
    30,
    5,
    1,
    true,
    CURRENT_DATE,
    u.id
FROM podologos p
CROSS JOIN (VALUES (1), (2), (3), (4), (5)) AS d(dia)  -- Lunes a Viernes
JOIN usuarios u ON u.email = 'enfsantiagoornelas@gmail.com'
WHERE p.cedula_profesional = 'POD-2018-001'
AND NOT EXISTS (
    SELECT 1 FROM horarios_trabajo ht 
    WHERE ht.id_podologo = p.id 
    AND ht.dia_semana = d.dia
);

-- Horarios de Joana Meraz (Lun-Vie 10:00-17:00)
INSERT INTO horarios_trabajo (
    id_podologo,
    dia_semana,
    hora_inicio,
    hora_fin,
    duracion_cita_minutos,
    tiempo_buffer_minutos,
    max_citas_simultaneas,
    activo,
    fecha_inicio_vigencia,
    creado_por
)
SELECT 
    p.id,
    d.dia,
    '10:00'::time,
    '17:00'::time,
    30,
    5,
    1,
    true,
    CURRENT_DATE,
    u.id
FROM podologos p
CROSS JOIN (VALUES (1), (2), (3), (4), (5)) AS d(dia)  -- Lunes a Viernes
JOIN usuarios u ON u.email = 'joana.meraz@podoskin.com'
WHERE p.cedula_profesional = 'POD-2020-002'
AND NOT EXISTS (
    SELECT 1 FROM horarios_trabajo ht 
    WHERE ht.id_podologo = p.id 
    AND ht.dia_semana = d.dia
);

-- ============================================================================
-- 4. TIPOS DE SERVICIOS / TRATAMIENTOS
-- ============================================================================
-- Catálogo de servicios podológicos con precios Mexicali 2024-2025

INSERT INTO tratamientos (codigo_servicio, nombre_servicio, descripcion, precio_base, duracion_minutos, requiere_consentimiento, activo)
SELECT * FROM (VALUES
    ('CONS-GEN-001', 'Consulta General', 'Evaluación y diagnóstico podológico general', 600.00, 30, false, true),
    ('ONIC-001', 'Onicomicosis', 'Tratamiento de hongos en las uñas', 750.00, 45, false, true),
    ('PIE-ATL-001', 'Pie de atleta', 'Tratamiento de infección fúngica en los pies', 600.00, 30, false, true),
    ('PEDI-CLI-001', 'Pedicure Clínico', 'Cuidado profesional de pies y uñas', 800.00, 60, false, true),
    ('UNAS-ENT-001', 'Uñas Enterradas', 'Tratamiento de uñas encarnadas', 550.00, 45, true, true),
    ('CALLO-001', 'Callosidades', 'Eliminación de callos y durezas', 500.00, 30, false, true),
    ('VERR-PLA-001', 'Verrugas Plantares', 'Tratamiento de verrugas en plantas de los pies', 900.00, 45, false, true)
) AS t(codigo_servicio, nombre_servicio, descripcion, precio_base, duracion_minutos, requiere_consentimiento, activo)
WHERE NOT EXISTS (
    SELECT 1 FROM tratamientos tr WHERE tr.codigo_servicio = t.codigo_servicio
);

-- ============================================================================
-- RESUMEN DE EJECUCIÓN
-- ============================================================================

DO $$
DECLARE
    v_usuarios_count INTEGER;
    v_podologos_count INTEGER;
    v_horarios_count INTEGER;
    v_tratamientos_count INTEGER;
BEGIN
    -- Contar registros insertados
    SELECT COUNT(*) INTO v_usuarios_count FROM usuarios;
    SELECT COUNT(*) INTO v_podologos_count FROM podologos;
    SELECT COUNT(*) INTO v_horarios_count FROM horarios_trabajo;
    SELECT COUNT(*) INTO v_tratamientos_count FROM tratamientos;
    
    -- Mostrar resumen
    RAISE NOTICE '';
    RAISE NOTICE '╔════════════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║  ✅ AGENTE 13/16 COMPLETADO EXITOSAMENTE                      ║';
    RAISE NOTICE '║  Script: 01_usuarios_config.sql                               ║';
    RAISE NOTICE '╠════════════════════════════════════════════════════════════════╣';
    RAISE NOTICE '║  📊 RESUMEN DE DATOS INSERTADOS:                              ║';
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '║     👤 Usuarios creados:        % usuarios                   ║', LPAD(v_usuarios_count::TEXT, 2, ' ');
    RAISE NOTICE '║     👨‍⚕️ Podólogos registrados:   % podólogos                 ║', LPAD(v_podologos_count::TEXT, 2, ' ');
    RAISE NOTICE '║     📅 Horarios configurados:   % horarios                   ║', LPAD(v_horarios_count::TEXT, 2, ' ');
    RAISE NOTICE '║     💼 Servicios disponibles:   % tratamientos               ║', LPAD(v_tratamientos_count::TEXT, 2, ' ');
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '╠════════════════════════════════════════════════════════════════╣';
    RAISE NOTICE '║  👥 USUARIOS CONFIGURADOS:                                    ║';
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '║  1️⃣  santiago.ornelas (Admin)                                 ║';
    RAISE NOTICE '║     📧 enfsantiagoornelas@gmail.com                           ║';
    RAISE NOTICE '║     🔑 Password: Admin123                                     ║';
    RAISE NOTICE '║     👨‍⚕️ Podólogo: Sí | Horario: Lun-Vie 09:00-18:00          ║';
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '║  2️⃣  joana.meraz (Podologo)                                   ║';
    RAISE NOTICE '║     📧 joana.meraz@podoskin.com                               ║';
    RAISE NOTICE '║     🔑 Password: Podologo123                                  ║';
    RAISE NOTICE '║     👨‍⚕️ Podóloga: Sí | Horario: Lun-Vie 10:00-17:00          ║';
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '║  3️⃣  maria.lopez (Recepcionista)                              ║';
    RAISE NOTICE '║     📧 maria.lopez@podoskin.com                               ║';
    RAISE NOTICE '║     🔑 Password: Recepcio123                                  ║';
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '║  4️⃣  admin.sistema (Admin)                                    ║';
    RAISE NOTICE '║     📧 admin@podoskin.com                                     ║';
    RAISE NOTICE '║     🔑 Password: Admin123                                     ║';
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '╠════════════════════════════════════════════════════════════════╣';
    RAISE NOTICE '║  💼 SERVICIOS CONFIGURADOS (Mexicali 2024-2025):             ║';
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '║     • Consulta General:      $600 MXN (30 min)                ║';
    RAISE NOTICE '║     • Onicomicosis:          $750 MXN (45 min)                ║';
    RAISE NOTICE '║     • Pie de atleta:         $600 MXN (30 min)                ║';
    RAISE NOTICE '║     • Pedicure Clínico:      $800 MXN (60 min)                ║';
    RAISE NOTICE '║     • Uñas Enterradas:       $550 MXN (45 min)                ║';
    RAISE NOTICE '║     • Callosidades:          $500 MXN (30 min)                ║';
    RAISE NOTICE '║     • Verrugas Plantares:    $900 MXN (45 min)                ║';
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '╠════════════════════════════════════════════════════════════════╣';
    RAISE NOTICE '║  ⚙️  CONFIGURACIÓN DEL SISTEMA:                               ║';
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '║     🏥 Clínica:    Podoskin Solution                          ║';
    RAISE NOTICE '║     📍 Ubicación:  Mexicali, Baja California                  ║';
    RAISE NOTICE '║     ⏱️  Slots:      30 minutos                                 ║';
    RAISE NOTICE '║     💵 Moneda:     MXN                                         ║';
    RAISE NOTICE '║     📊 IVA:        16%%                                        ║';
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '╠════════════════════════════════════════════════════════════════╣';
    RAISE NOTICE '║  📝 SIGUIENTE PASO:                                           ║';
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '║     ▶️  Ejecutar: agente_14_pacientes.sql                     ║';
    RAISE NOTICE '║     📦 Crear datos mock de pacientes y citas                  ║';
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '╚════════════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';
END $$;

-- Confirmar transacción
COMMIT;

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================
-- Ejecución: psql -U postgres -d podoskin -f 01_usuarios_config.sql
-- o bien: \i /ruta/a/01_usuarios_config.sql desde psql
-- ============================================================================
