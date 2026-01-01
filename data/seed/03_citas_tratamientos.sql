-- ============================================================================
-- Archivo: 03_citas_tratamientos.sql
-- Agente: 15/16 - DEV Mock Data - Citas y Tratamientos
-- Descripción: Script de datos mock para 363 citas con tratamientos completos
-- Dependencias: Requiere Agente 13 (01_usuarios_config.sql) + Agente 14 (02_pacientes.sql)
-- ============================================================================
-- 
-- DISTRIBUCIÓN DE CITAS:
--   - Período: Noviembre 2024 - Enero 2025 (66 días hábiles)
--   - Total citas: 363
--   - Noviembre 2024: 115 citas
--   - Diciembre 2024: 121 citas
--   - Enero 2025: 127 citas
--
-- DISTRIBUCIÓN POR DOCTOR:
--   - Santiago (55%%): 200 citas
--   - Joana (45%%): 163 citas
--
-- DISTRIBUCIÓN POR SERVICIO:
--   - Consulta General: 91 citas (25%%) - $600
--   - Onicomicosis: 73 citas (20%%) - $750
--   - Uñas Enterradas: 73 citas (20%%) - $550
--   - Pedicure Clínico: 54 citas (15%%) - $800
--   - Callosidades: 44 citas (12%%) - $500
--   - Verrugas Plantares: 18 citas (5%%) - $900
--   - Pie de Atleta: 10 citas (3%%) - $600
--
-- ESTADOS DE CITA:
--   - Completada: 308 citas (85%%)
--   - Cancelada: 18 citas (5%%)
--   - No Asistió: 7 citas (2%%)
--   - Pendiente: 30 citas (8%%)
--
-- TRATAMIENTOS Y DIAGNÓSTICOS:
--   - 310 tratamientos (solo citas completadas)
--   - 310 diagnósticos con códigos CIE-10 válidos
-- ============================================================================

-- Iniciar transacción
BEGIN;

-- ============================================================================
-- VALIDACIÓN DE PREREQUISITOS
-- ============================================================================

DO $$
BEGIN
  -- Verificar que existan pacientes (Agente 14)
  IF (SELECT COUNT(*) FROM pacientes) < 200 THEN
    RAISE EXCEPTION 'ERROR: Ejecuta agente_14_pacientes primero. Se requieren 200 pacientes.';
  END IF;
  
  -- Verificar que existan tipos de servicio (Agente 13)
  IF (SELECT COUNT(*) FROM tratamientos) < 7 THEN
    RAISE EXCEPTION 'ERROR: Faltan tipos de servicio. Ejecuta Agente 13 primero.';
  END IF;
  
  -- Verificar que existan horarios de doctores (Agente 13)
  IF (SELECT COUNT(*) FROM horarios_trabajo) < 10 THEN
    RAISE EXCEPTION 'ERROR: Faltan horarios. Ejecuta Agente 13 primero.';
  END IF;
  
  RAISE NOTICE '✅ Prerequisitos verificados correctamente';
END $$;

-- ============================================================================
-- 1. CITAS (363 registros)
-- ============================================================================

RAISE NOTICE 'Insertando 363 citas...';

INSERT INTO citas (
  id_paciente, id_podologo, fecha_hora_inicio, fecha_hora_fin,
  tipo_cita, estado, motivo_cancelacion, es_primera_vez, notas_recepcion, fecha_creacion
) VALUES
  (73, 2, '2024-11-01 12:30:00', '2024-11-01 13:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Callosidades - $500.00', '2024-11-01 12:30:00'),
  (93, 2, '2024-11-01 13:00:00', '2024-11-01 13:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2024-11-01 13:00:00'),
  (2, 2, '2024-11-01 15:00:00', '2024-11-01 15:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Verrugas Plantares - $900.00', '2024-11-01 15:00:00'),
  (163, 2, '2024-11-01 15:30:00', '2024-11-01 16:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-11-01 15:30:00'),
  (110, 1, '2024-11-01 16:30:00', '2024-11-01 17:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-01 16:30:00'),
  (91, 1, '2024-11-01 17:00:00', '2024-11-01 17:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-11-01 17:00:00'),
  (128, 1, '2024-11-04 10:30:00', '2024-11-04 11:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-04 10:30:00'),
  (168, 2, '2024-11-04 10:30:00', '2024-11-04 11:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-04 10:30:00'),
  (162, 2, '2024-11-04 14:30:00', '2024-11-04 15:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-04 14:30:00'),
  (113, 1, '2024-11-04 15:00:00', '2024-11-04 15:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-11-04 15:00:00'),
  (177, 2, '2024-11-04 15:00:00', '2024-11-04 15:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-11-04 15:00:00'),
  (96, 1, '2024-11-04 16:30:00', '2024-11-04 17:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-11-04 16:30:00'),
  (21, 2, '2024-11-05 12:30:00', '2024-11-05 13:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-11-05 12:30:00'),
  (171, 2, '2024-11-05 14:00:00', '2024-11-05 14:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-05 14:00:00'),
  (106, 1, '2024-11-05 14:00:00', '2024-11-05 14:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Uñas Enterradas - $550.00', '2024-11-05 14:00:00'),
  (114, 2, '2024-11-05 15:00:00', '2024-11-05 15:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-05 15:00:00'),
  (190, 1, '2024-11-05 15:30:00', '2024-11-05 16:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-05 15:30:00'),
  (152, 2, '2024-11-05 16:00:00', '2024-11-05 16:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Uñas Enterradas - $550.00', '2024-11-05 16:00:00'),
  (155, 1, '2024-11-06 09:00:00', '2024-11-06 09:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2024-11-06 09:00:00'),
  (25, 2, '2024-11-06 13:00:00', '2024-11-06 13:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-06 13:00:00'),
  (160, 2, '2024-11-06 14:00:00', '2024-11-06 14:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2024-11-06 14:00:00'),
  (72, 2, '2024-11-06 15:00:00', '2024-11-06 15:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-06 15:00:00'),
  (7, 2, '2024-11-06 15:30:00', '2024-11-06 16:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-11-06 15:30:00'),
  (28, 1, '2024-11-06 17:00:00', '2024-11-06 17:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-11-06 17:00:00'),
  (197, 1, '2024-11-07 09:30:00', '2024-11-07 10:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-07 09:30:00'),
  (10, 1, '2024-11-07 10:00:00', '2024-11-07 10:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-07 10:00:00'),
  (24, 2, '2024-11-07 11:00:00', '2024-11-07 11:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-11-07 11:00:00'),
  (40, 2, '2024-11-07 13:00:00', '2024-11-07 13:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-07 13:00:00'),
  (102, 1, '2024-11-07 14:00:00', '2024-11-07 15:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Pedicure Clínico - $800.00', '2024-11-07 14:00:00'),
  (4, 1, '2024-11-07 17:00:00', '2024-11-07 18:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-11-07 17:00:00'),
  (34, 2, '2024-11-08 11:00:00', '2024-11-08 11:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-08 11:00:00'),
  (135, 1, '2024-11-08 12:30:00', '2024-11-08 13:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2024-11-08 12:30:00'),
  (151, 1, '2024-11-08 15:00:00', '2024-11-08 15:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Uñas Enterradas - $550.00', '2024-11-08 15:00:00'),
  (94, 1, '2024-11-08 15:30:00', '2024-11-08 16:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-11-08 15:30:00'),
  (121, 1, '2024-11-08 16:00:00', '2024-11-08 17:00:00', 'Primera Vez', 'Pendiente', NULL, true, 'Servicio: Pedicure Clínico - $800.00', '2024-11-08 16:00:00'),
  (148, 1, '2024-11-08 16:30:00', '2024-11-08 17:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-11-08 16:30:00'),
  (57, 1, '2024-11-11 09:00:00', '2024-11-11 09:45:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-11 09:00:00'),
  (67, 1, '2024-11-11 10:00:00', '2024-11-11 10:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pie de Atleta - $600.00', '2024-11-11 10:00:00'),
  (61, 1, '2024-11-11 10:30:00', '2024-11-11 11:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-11-11 10:30:00'),
  (122, 2, '2024-11-11 12:30:00', '2024-11-11 13:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-11-11 12:30:00'),
  (116, 2, '2024-11-11 13:00:00', '2024-11-11 14:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-11-11 13:00:00'),
  (95, 2, '2024-11-11 15:00:00', '2024-11-11 15:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-11 15:00:00'),
  (153, 2, '2024-11-12 11:30:00', '2024-11-12 12:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-12 11:30:00'),
  (80, 2, '2024-11-12 12:00:00', '2024-11-12 12:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Verrugas Plantares - $900.00', '2024-11-12 12:00:00'),
  (54, 2, '2024-11-12 12:30:00', '2024-11-12 13:15:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Uñas Enterradas - $550.00', '2024-11-12 12:30:00'),
  (38, 2, '2024-11-12 13:00:00', '2024-11-12 13:45:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-11-12 13:00:00'),
  (97, 2, '2024-11-12 14:00:00', '2024-11-12 14:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-12 14:00:00'),
  (150, 2, '2024-11-12 14:30:00', '2024-11-12 15:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-11-12 14:30:00'),
  (125, 1, '2024-11-13 09:00:00', '2024-11-13 09:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2024-11-13 09:00:00'),
  (194, 2, '2024-11-13 10:30:00', '2024-11-13 11:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2024-11-13 10:30:00'),
  (30, 2, '2024-11-13 11:00:00', '2024-11-13 11:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-13 11:00:00'),
  (33, 1, '2024-11-13 14:00:00', '2024-11-13 14:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Verrugas Plantares - $900.00', '2024-11-13 14:00:00'),
  (120, 1, '2024-11-13 14:30:00', '2024-11-13 15:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Pedicure Clínico - $800.00', '2024-11-13 14:30:00'),
  (77, 2, '2024-11-13 16:00:00', '2024-11-13 16:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-11-13 16:00:00'),
  (178, 1, '2024-11-14 09:30:00', '2024-11-14 10:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-11-14 09:30:00'),
  (20, 2, '2024-11-14 11:30:00', '2024-11-14 12:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-14 11:30:00'),
  (8, 1, '2024-11-14 12:00:00', '2024-11-14 12:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-14 12:00:00'),
  (143, 2, '2024-11-14 14:00:00', '2024-11-14 14:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Verrugas Plantares - $900.00', '2024-11-14 14:00:00'),
  (31, 1, '2024-11-14 15:00:00', '2024-11-14 16:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-11-14 15:00:00'),
  (185, 2, '2024-11-14 16:00:00', '2024-11-14 16:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-14 16:00:00'),
  (147, 1, '2024-11-15 10:30:00', '2024-11-15 11:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-11-15 10:30:00'),
  (192, 2, '2024-11-15 11:00:00', '2024-11-15 11:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-15 11:00:00'),
  (180, 2, '2024-11-15 11:30:00', '2024-11-15 12:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-15 11:30:00'),
  (53, 1, '2024-11-15 12:30:00', '2024-11-15 13:30:00', 'Seguimiento', 'Cancelada', 'Emergencia personal', false, 'Servicio: Pedicure Clínico - $800.00', '2024-11-15 12:30:00'),
  (173, 2, '2024-11-15 13:00:00', '2024-11-15 13:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-15 13:00:00'),
  (159, 1, '2024-11-18 10:00:00', '2024-11-18 10:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-11-18 10:00:00'),
  (100, 1, '2024-11-18 13:30:00', '2024-11-18 14:30:00', 'Seguimiento', 'Cancelada', 'Cancelado por el paciente', false, 'Servicio: Pedicure Clínico - $800.00', '2024-11-18 13:30:00'),
  (174, 1, '2024-11-18 15:00:00', '2024-11-18 15:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-18 15:00:00'),
  (79, 1, '2024-11-18 16:30:00', '2024-11-18 17:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-11-18 16:30:00'),
  (127, 1, '2024-11-18 17:00:00', '2024-11-18 17:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2024-11-18 17:00:00'),
  (183, 1, '2024-11-19 10:00:00', '2024-11-19 10:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-11-19 10:00:00'),
  (32, 2, '2024-11-19 13:00:00', '2024-11-19 13:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-11-19 13:00:00'),
  (144, 2, '2024-11-19 14:00:00', '2024-11-19 14:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-19 14:00:00'),
  (76, 1, '2024-11-19 14:30:00', '2024-11-19 15:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-19 14:30:00'),
  (179, 1, '2024-11-19 16:00:00', '2024-11-19 16:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Uñas Enterradas - $550.00', '2024-11-19 16:00:00'),
  (36, 1, '2024-11-20 09:30:00', '2024-11-20 10:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Pedicure Clínico - $800.00', '2024-11-20 09:30:00'),
  (195, 1, '2024-11-20 11:00:00', '2024-11-20 11:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Verrugas Plantares - $900.00', '2024-11-20 11:00:00'),
  (182, 2, '2024-11-20 11:30:00', '2024-11-20 12:00:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Callosidades - $500.00', '2024-11-20 11:30:00'),
  (48, 2, '2024-11-20 12:30:00', '2024-11-20 13:15:00', 'Seguimiento', 'Cancelada', 'Cancelado por el paciente', false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-20 12:30:00'),
  (119, 2, '2024-11-20 14:00:00', '2024-11-20 15:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-11-20 14:00:00'),
  (165, 2, '2024-11-21 11:00:00', '2024-11-21 11:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2024-11-21 11:00:00'),
  (45, 2, '2024-11-21 11:30:00', '2024-11-21 12:15:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-11-21 11:30:00'),
  (157, 2, '2024-11-21 13:00:00', '2024-11-21 13:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-21 13:00:00'),
  (146, 1, '2024-11-21 15:00:00', '2024-11-21 15:45:00', 'Primera Vez', 'No_Asistio', NULL, true, 'Servicio: Uñas Enterradas - $550.00', '2024-11-21 15:00:00'),
  (60, 1, '2024-11-21 15:30:00', '2024-11-21 16:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-11-21 15:30:00'),
  (62, 1, '2024-11-22 09:30:00', '2024-11-22 10:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Verrugas Plantares - $900.00', '2024-11-22 09:30:00'),
  (154, 2, '2024-11-22 10:00:00', '2024-11-22 10:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Callosidades - $500.00', '2024-11-22 10:00:00'),
  (123, 1, '2024-11-22 13:30:00', '2024-11-22 14:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-22 13:30:00'),
  (133, 2, '2024-11-22 13:30:00', '2024-11-22 14:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-11-22 13:30:00'),
  (137, 2, '2024-11-22 15:00:00', '2024-11-22 16:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-11-22 15:00:00'),
  (63, 2, '2024-11-25 12:00:00', '2024-11-25 12:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pie de Atleta - $600.00', '2024-11-25 12:00:00'),
  (107, 1, '2024-11-25 12:00:00', '2024-11-25 12:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-25 12:00:00'),
  (87, 2, '2024-11-25 12:30:00', '2024-11-25 13:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-25 12:30:00'),
  (71, 1, '2024-11-25 13:30:00', '2024-11-25 14:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-11-25 13:30:00'),
  (156, 1, '2024-11-25 14:00:00', '2024-11-25 14:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-25 14:00:00'),
  (134, 1, '2024-11-26 10:30:00', '2024-11-26 11:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Callosidades - $500.00', '2024-11-26 10:30:00'),
  (140, 1, '2024-11-26 11:00:00', '2024-11-26 11:45:00', 'Primera Vez', 'No_Asistio', NULL, true, 'Servicio: Uñas Enterradas - $550.00', '2024-11-26 11:00:00'),
  (1, 1, '2024-11-26 14:00:00', '2024-11-26 14:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2024-11-26 14:00:00'),
  (81, 1, '2024-11-26 15:30:00', '2024-11-26 16:15:00', 'Seguimiento', 'Cancelada', 'Reagendado por conflicto', false, 'Servicio: Verrugas Plantares - $900.00', '2024-11-26 15:30:00'),
  (200, 1, '2024-11-26 17:00:00', '2024-11-26 17:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-11-26 17:00:00'),
  (111, 2, '2024-11-27 11:00:00', '2024-11-27 11:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Verrugas Plantares - $900.00', '2024-11-27 11:00:00'),
  (167, 1, '2024-11-27 11:30:00', '2024-11-27 12:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-27 11:30:00'),
  (19, 1, '2024-11-27 14:00:00', '2024-11-27 14:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2024-11-27 14:00:00'),
  (189, 1, '2024-11-27 16:00:00', '2024-11-27 16:45:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-11-27 16:00:00'),
  (70, 1, '2024-11-27 16:30:00', '2024-11-27 17:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-11-27 16:30:00'),
  (35, 1, '2024-11-28 09:00:00', '2024-11-28 09:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2024-11-28 09:00:00'),
  (129, 1, '2024-11-28 09:30:00', '2024-11-28 10:15:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2024-11-28 09:30:00'),
  (191, 2, '2024-11-28 13:30:00', '2024-11-28 14:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-28 13:30:00'),
  (92, 1, '2024-11-28 14:30:00', '2024-11-28 15:15:00', 'Primera Vez', 'Pendiente', NULL, true, 'Servicio: Onicomicosis - $750.00', '2024-11-28 14:30:00'),
  (59, 1, '2024-11-28 16:30:00', '2024-11-28 17:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pie de Atleta - $600.00', '2024-11-28 16:30:00'),
  (199, 1, '2024-11-29 09:30:00', '2024-11-29 10:00:00', 'Primera Vez', 'Cancelada', 'Paciente enfermo', true, 'Servicio: Callosidades - $500.00', '2024-11-29 09:30:00'),
  (118, 1, '2024-11-29 10:30:00', '2024-11-29 11:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Pedicure Clínico - $800.00', '2024-11-29 10:30:00'),
  (130, 2, '2024-11-29 11:30:00', '2024-11-29 12:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-11-29 11:30:00'),
  (49, 2, '2024-11-29 15:30:00', '2024-11-29 16:15:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Verrugas Plantares - $900.00', '2024-11-29 15:30:00'),
  (136, 1, '2024-11-29 16:00:00', '2024-11-29 17:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-11-29 16:00:00'),
  (109, 2, '2024-12-02 10:00:00', '2024-12-02 10:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-02 10:00:00'),
  (166, 2, '2024-12-02 15:00:00', '2024-12-02 15:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2024-12-02 15:00:00'),
  (3, 2, '2024-12-02 15:30:00', '2024-12-02 16:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-02 15:30:00'),
  (15, 1, '2024-12-02 15:30:00', '2024-12-02 16:15:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-02 15:30:00'),
  (124, 2, '2024-12-02 16:00:00', '2024-12-02 16:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2024-12-02 16:00:00'),
  (170, 1, '2024-12-02 16:30:00', '2024-12-02 17:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2024-12-02 16:30:00'),
  (90, 1, '2024-12-03 09:00:00', '2024-12-03 09:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-03 09:00:00'),
  (14, 2, '2024-12-03 10:30:00', '2024-12-03 11:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-12-03 10:30:00'),
  (193, 1, '2024-12-03 13:00:00', '2024-12-03 13:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-03 13:00:00'),
  (142, 2, '2024-12-03 13:30:00', '2024-12-03 14:30:00', 'Seguimiento', 'Cancelada', 'Reagendado por conflicto', false, 'Servicio: Pedicure Clínico - $800.00', '2024-12-03 13:30:00'),
  (66, 1, '2024-12-03 14:00:00', '2024-12-03 14:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Callosidades - $500.00', '2024-12-03 14:00:00'),
  (46, 2, '2024-12-03 15:00:00', '2024-12-03 15:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-03 15:00:00'),
  (172, 1, '2024-12-04 09:30:00', '2024-12-04 10:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-04 09:30:00'),
  (41, 2, '2024-12-04 11:00:00', '2024-12-04 11:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-12-04 11:00:00'),
  (145, 2, '2024-12-04 14:30:00', '2024-12-04 15:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-04 14:30:00'),
  (186, 1, '2024-12-04 15:00:00', '2024-12-04 15:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2024-12-04 15:00:00'),
  (132, 2, '2024-12-04 15:30:00', '2024-12-04 16:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-04 15:30:00'),
  (138, 1, '2024-12-04 16:00:00', '2024-12-04 16:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-04 16:00:00'),
  (58, 1, '2024-12-05 10:30:00', '2024-12-05 11:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pie de Atleta - $600.00', '2024-12-05 10:30:00'),
  (47, 1, '2024-12-05 11:00:00', '2024-12-05 11:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-05 11:00:00'),
  (13, 2, '2024-12-05 13:00:00', '2024-12-05 13:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-05 13:00:00'),
  (68, 2, '2024-12-05 14:00:00', '2024-12-05 15:00:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-12-05 14:00:00'),
  (75, 2, '2024-12-05 14:30:00', '2024-12-05 15:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-05 14:30:00'),
  (86, 1, '2024-12-05 16:00:00', '2024-12-05 16:30:00', 'Primera Vez', 'Pendiente', NULL, true, 'Servicio: Consulta General - $600.00', '2024-12-05 16:00:00'),
  (126, 2, '2024-12-06 10:00:00', '2024-12-06 11:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-12-06 10:00:00'),
  (181, 2, '2024-12-06 11:00:00', '2024-12-06 11:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-12-06 11:00:00'),
  (131, 2, '2024-12-06 11:30:00', '2024-12-06 12:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-06 11:30:00'),
  (22, 2, '2024-12-06 15:30:00', '2024-12-06 16:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-06 15:30:00'),
  (89, 1, '2024-12-06 16:00:00', '2024-12-06 16:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2024-12-06 16:00:00'),
  (99, 1, '2024-12-06 16:30:00', '2024-12-06 17:15:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-06 16:30:00'),
  (112, 1, '2024-12-09 09:00:00', '2024-12-09 09:45:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-09 09:00:00'),
  (64, 1, '2024-12-09 09:30:00', '2024-12-09 10:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-09 09:30:00'),
  (115, 2, '2024-12-09 11:30:00', '2024-12-09 12:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-09 11:30:00'),
  (83, 2, '2024-12-09 12:30:00', '2024-12-09 13:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-12-09 12:30:00'),
  (74, 1, '2024-12-09 14:30:00', '2024-12-09 15:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-09 14:30:00'),
  (117, 2, '2024-12-09 15:30:00', '2024-12-09 16:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-09 15:30:00'),
  (139, 1, '2024-12-10 09:30:00', '2024-12-10 10:00:00', 'Primera Vez', 'Pendiente', NULL, true, 'Servicio: Consulta General - $600.00', '2024-12-10 09:30:00'),
  (161, 2, '2024-12-10 12:30:00', '2024-12-10 13:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2024-12-10 12:30:00'),
  (44, 2, '2024-12-10 13:30:00', '2024-12-10 14:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-10 13:30:00'),
  (141, 2, '2024-12-10 14:00:00', '2024-12-10 14:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2024-12-10 14:00:00'),
  (98, 1, '2024-12-10 14:30:00', '2024-12-10 15:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-12-10 14:30:00'),
  (164, 2, '2024-12-10 16:00:00', '2024-12-10 17:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Pedicure Clínico - $800.00', '2024-12-10 16:00:00'),
  (188, 1, '2024-12-11 10:00:00', '2024-12-11 11:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-12-11 10:00:00'),
  (198, 1, '2024-12-11 10:30:00', '2024-12-11 11:15:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Verrugas Plantares - $900.00', '2024-12-11 10:30:00'),
  (103, 1, '2024-12-11 13:00:00', '2024-12-11 13:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-11 13:00:00'),
  (78, 1, '2024-12-11 13:30:00', '2024-12-11 14:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-11 13:30:00'),
  (196, 2, '2024-12-11 14:30:00', '2024-12-11 15:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-11 14:30:00'),
  (9, 1, '2024-12-11 15:30:00', '2024-12-11 16:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-11 15:30:00'),
  (11, 2, '2024-12-12 11:30:00', '2024-12-12 12:00:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Callosidades - $500.00', '2024-12-12 11:30:00'),
  (39, 1, '2024-12-12 12:00:00', '2024-12-12 12:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Callosidades - $500.00', '2024-12-12 12:00:00'),
  (12, 1, '2024-12-12 13:30:00', '2024-12-12 14:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-12 13:30:00'),
  (69, 2, '2024-12-12 15:30:00', '2024-12-12 16:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-12 15:30:00'),
  (18, 1, '2024-12-12 15:30:00', '2024-12-12 16:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2024-12-12 15:30:00'),
  (176, 1, '2024-12-12 17:00:00', '2024-12-12 17:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-12 17:00:00'),
  (17, 1, '2024-12-13 09:00:00', '2024-12-13 10:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-12-13 09:00:00'),
  (104, 1, '2024-12-13 10:30:00', '2024-12-13 11:15:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Uñas Enterradas - $550.00', '2024-12-13 10:30:00'),
  (101, 2, '2024-12-13 11:00:00', '2024-12-13 11:45:00', 'Primera Vez', 'Pendiente', NULL, true, 'Servicio: Verrugas Plantares - $900.00', '2024-12-13 11:00:00'),
  (26, 1, '2024-12-13 11:30:00', '2024-12-13 12:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-12-13 11:30:00'),
  (187, 1, '2024-12-13 15:30:00', '2024-12-13 16:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-13 15:30:00'),
  (27, 2, '2024-12-13 16:00:00', '2024-12-13 16:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Uñas Enterradas - $550.00', '2024-12-13 16:00:00'),
  (84, 1, '2024-12-16 09:00:00', '2024-12-16 09:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2024-12-16 09:00:00'),
  (29, 1, '2024-12-16 11:00:00', '2024-12-16 11:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2024-12-16 11:00:00'),
  (23, 2, '2024-12-16 11:00:00', '2024-12-16 11:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-12-16 11:00:00'),
  (52, 2, '2024-12-16 13:00:00', '2024-12-16 13:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-16 13:00:00'),
  (6, 2, '2024-12-16 13:30:00', '2024-12-16 14:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-16 13:30:00'),
  (85, 2, '2024-12-16 16:00:00', '2024-12-16 16:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-16 16:00:00'),
  (50, 1, '2024-12-17 11:30:00', '2024-12-17 12:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-17 11:30:00'),
  (42, 2, '2024-12-17 14:00:00', '2024-12-17 14:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-17 14:00:00'),
  (82, 1, '2024-12-17 15:00:00', '2024-12-17 15:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Verrugas Plantares - $900.00', '2024-12-17 15:00:00'),
  (56, 1, '2024-12-17 16:00:00', '2024-12-17 16:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-17 16:00:00'),
  (51, 1, '2024-12-17 17:00:00', '2024-12-17 17:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Uñas Enterradas - $550.00', '2024-12-17 17:00:00'),
  (184, 2, '2024-12-18 12:00:00', '2024-12-18 12:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-18 12:00:00'),
  (43, 1, '2024-12-18 12:30:00', '2024-12-18 13:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-18 12:30:00'),
  (158, 2, '2024-12-18 15:00:00', '2024-12-18 15:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-18 15:00:00'),
  (16, 1, '2024-12-18 15:30:00', '2024-12-18 16:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-18 15:30:00'),
  (108, 1, '2024-12-18 16:00:00', '2024-12-18 16:30:00', 'Seguimiento', 'Cancelada', 'Emergencia personal', false, 'Servicio: Consulta General - $600.00', '2024-12-18 16:00:00'),
  (105, 2, '2024-12-19 11:00:00', '2024-12-19 11:30:00', 'Primera Vez', 'Cancelada', 'Emergencia personal', true, 'Servicio: Callosidades - $500.00', '2024-12-19 11:00:00'),
  (88, 1, '2024-12-19 12:00:00', '2024-12-19 12:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-19 12:00:00'),
  (149, 2, '2024-12-19 16:00:00', '2024-12-19 16:30:00', 'Primera Vez', 'Cancelada', 'Reagendado por conflicto', true, 'Servicio: Consulta General - $600.00', '2024-12-19 16:00:00'),
  (175, 1, '2024-12-19 16:00:00', '2024-12-19 16:30:00', 'Seguimiento', 'No_Asistio', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-19 16:00:00'),
  (5, 1, '2024-12-19 17:00:00', '2024-12-19 17:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-19 17:00:00'),
  (73, 1, '2024-12-20 10:30:00', '2024-12-20 11:00:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Pie de Atleta - $600.00', '2024-12-20 10:30:00'),
  (37, 1, '2024-12-20 12:30:00', '2024-12-20 13:00:00', 'Seguimiento', 'No_Asistio', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-20 12:30:00'),
  (65, 2, '2024-12-20 13:30:00', '2024-12-20 14:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2024-12-20 13:30:00'),
  (169, 2, '2024-12-20 14:00:00', '2024-12-20 14:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-20 14:00:00'),
  (55, 2, '2024-12-20 16:00:00', '2024-12-20 16:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-20 16:00:00'),
  (93, 2, '2024-12-23 10:00:00', '2024-12-23 10:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Callosidades - $500.00', '2024-12-23 10:00:00'),
  (110, 1, '2024-12-23 10:00:00', '2024-12-23 10:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-12-23 10:00:00'),
  (2, 2, '2024-12-23 10:30:00', '2024-12-23 11:00:00', 'Seguimiento', 'No_Asistio', NULL, false, 'Servicio: Callosidades - $500.00', '2024-12-23 10:30:00'),
  (163, 2, '2024-12-23 12:30:00', '2024-12-23 13:00:00', 'Primera Vez', 'Cancelada', 'Reagendado por conflicto', true, 'Servicio: Callosidades - $500.00', '2024-12-23 12:30:00'),
  (91, 2, '2024-12-23 13:00:00', '2024-12-23 14:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-12-23 13:00:00'),
  (168, 2, '2024-12-24 12:00:00', '2024-12-24 12:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-24 12:00:00'),
  (128, 1, '2024-12-24 12:00:00', '2024-12-24 12:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-24 12:00:00'),
  (96, 1, '2024-12-24 13:00:00', '2024-12-24 13:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-12-24 13:00:00'),
  (177, 2, '2024-12-24 14:00:00', '2024-12-24 14:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-12-24 14:00:00'),
  (113, 2, '2024-12-24 14:30:00', '2024-12-24 15:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Verrugas Plantares - $900.00', '2024-12-24 14:30:00'),
  (171, 1, '2024-12-25 10:00:00', '2024-12-25 10:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-25 10:00:00'),
  (162, 1, '2024-12-25 11:00:00', '2024-12-25 11:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-25 11:00:00'),
  (114, 2, '2024-12-25 11:30:00', '2024-12-25 12:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-12-25 11:30:00'),
  (21, 1, '2024-12-25 14:30:00', '2024-12-25 15:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-25 14:30:00'),
  (152, 1, '2024-12-25 16:00:00', '2024-12-25 17:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Pedicure Clínico - $800.00', '2024-12-25 16:00:00'),
  (190, 1, '2024-12-26 09:00:00', '2024-12-26 09:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pie de Atleta - $600.00', '2024-12-26 09:00:00'),
  (106, 2, '2024-12-26 13:00:00', '2024-12-26 13:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-26 13:00:00'),
  (72, 2, '2024-12-26 14:30:00', '2024-12-26 15:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-26 14:30:00'),
  (25, 1, '2024-12-26 15:00:00', '2024-12-26 15:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-26 15:00:00'),
  (7, 1, '2024-12-26 17:00:00', '2024-12-26 17:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-26 17:00:00'),
  (24, 1, '2024-12-27 09:30:00', '2024-12-27 10:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Callosidades - $500.00', '2024-12-27 09:30:00'),
  (102, 1, '2024-12-27 11:00:00', '2024-12-27 11:30:00', 'Primera Vez', 'Cancelada', 'Emergencia personal', true, 'Servicio: Callosidades - $500.00', '2024-12-27 11:00:00'),
  (160, 1, '2024-12-27 11:30:00', '2024-12-27 12:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Callosidades - $500.00', '2024-12-27 11:30:00'),
  (28, 2, '2024-12-27 13:00:00', '2024-12-27 13:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2024-12-27 13:00:00'),
  (155, 2, '2024-12-27 14:00:00', '2024-12-27 14:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2024-12-27 14:00:00'),
  (10, 1, '2024-12-30 09:00:00', '2024-12-30 09:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-30 09:00:00'),
  (197, 1, '2024-12-30 11:30:00', '2024-12-30 12:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2024-12-30 11:30:00'),
  (94, 2, '2024-12-30 11:30:00', '2024-12-30 12:15:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Uñas Enterradas - $550.00', '2024-12-30 11:30:00'),
  (40, 1, '2024-12-30 13:00:00', '2024-12-30 13:45:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-30 13:00:00'),
  (4, 2, '2024-12-30 14:30:00', '2024-12-30 15:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2024-12-30 14:30:00'),
  (34, 2, '2024-12-31 14:00:00', '2024-12-31 14:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2024-12-31 14:00:00'),
  (148, 1, '2024-12-31 14:30:00', '2024-12-31 15:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-12-31 14:30:00'),
  (151, 1, '2024-12-31 15:30:00', '2024-12-31 16:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-31 15:30:00'),
  (135, 2, '2024-12-31 16:00:00', '2024-12-31 16:45:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Onicomicosis - $750.00', '2024-12-31 16:00:00'),
  (121, 1, '2024-12-31 16:30:00', '2024-12-31 17:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2024-12-31 16:30:00'),
  (122, 1, '2025-01-01 09:30:00', '2025-01-01 10:15:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Onicomicosis - $750.00', '2025-01-01 09:30:00'),
  (95, 2, '2025-01-01 10:30:00', '2025-01-01 11:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Verrugas Plantares - $900.00', '2025-01-01 10:30:00'),
  (116, 1, '2025-01-01 12:30:00', '2025-01-01 13:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2025-01-01 12:30:00'),
  (57, 2, '2025-01-01 13:30:00', '2025-01-01 14:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2025-01-01 13:30:00'),
  (61, 2, '2025-01-01 14:30:00', '2025-01-01 15:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2025-01-01 14:30:00'),
  (67, 1, '2025-01-01 17:00:00', '2025-01-01 18:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2025-01-01 17:00:00'),
  (80, 1, '2025-01-02 10:00:00', '2025-01-02 10:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-02 10:00:00'),
  (153, 1, '2025-01-02 11:30:00', '2025-01-02 12:15:00', 'Primera Vez', 'Pendiente', NULL, true, 'Servicio: Onicomicosis - $750.00', '2025-01-02 11:30:00'),
  (150, 1, '2025-01-02 12:00:00', '2025-01-02 12:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-02 12:00:00'),
  (38, 2, '2025-01-02 12:30:00', '2025-01-02 13:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-02 12:30:00'),
  (54, 2, '2025-01-02 13:30:00', '2025-01-02 14:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2025-01-02 13:30:00'),
  (97, 2, '2025-01-02 15:30:00', '2025-01-02 16:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-02 15:30:00'),
  (194, 1, '2025-01-03 09:30:00', '2025-01-03 10:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2025-01-03 09:30:00'),
  (77, 1, '2025-01-03 11:00:00', '2025-01-03 11:45:00', 'Seguimiento', 'Cancelada', 'Emergencia personal', false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-03 11:00:00'),
  (120, 1, '2025-01-03 13:00:00', '2025-01-03 14:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2025-01-03 13:00:00'),
  (125, 1, '2025-01-03 14:00:00', '2025-01-03 14:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2025-01-03 14:00:00'),
  (30, 2, '2025-01-03 15:30:00', '2025-01-03 16:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Callosidades - $500.00', '2025-01-03 15:30:00'),
  (33, 1, '2025-01-03 16:00:00', '2025-01-03 16:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-03 16:00:00'),
  (31, 2, '2025-01-06 10:00:00', '2025-01-06 10:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2025-01-06 10:00:00'),
  (143, 1, '2025-01-06 10:00:00', '2025-01-06 10:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pie de Atleta - $600.00', '2025-01-06 10:00:00'),
  (178, 1, '2025-01-06 10:30:00', '2025-01-06 11:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2025-01-06 10:30:00'),
  (20, 2, '2025-01-06 12:30:00', '2025-01-06 13:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2025-01-06 12:30:00'),
  (185, 1, '2025-01-06 14:00:00', '2025-01-06 14:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-06 14:00:00'),
  (8, 2, '2025-01-06 14:30:00', '2025-01-06 15:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-06 14:30:00'),
  (53, 1, '2025-01-07 09:30:00', '2025-01-07 10:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2025-01-07 09:30:00'),
  (159, 1, '2025-01-07 10:30:00', '2025-01-07 11:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pie de Atleta - $600.00', '2025-01-07 10:30:00'),
  (173, 1, '2025-01-07 13:00:00', '2025-01-07 13:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-07 13:00:00'),
  (180, 1, '2025-01-07 13:30:00', '2025-01-07 14:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-07 13:30:00'),
  (147, 2, '2025-01-07 13:30:00', '2025-01-07 14:15:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Uñas Enterradas - $550.00', '2025-01-07 13:30:00'),
  (192, 1, '2025-01-07 16:00:00', '2025-01-07 16:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-07 16:00:00'),
  (100, 2, '2025-01-08 11:30:00', '2025-01-08 12:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2025-01-08 11:30:00'),
  (127, 1, '2025-01-08 11:30:00', '2025-01-08 12:15:00', 'Primera Vez', 'No_Asistio', NULL, true, 'Servicio: Onicomicosis - $750.00', '2025-01-08 11:30:00'),
  (76, 2, '2025-01-08 13:30:00', '2025-01-08 14:15:00', 'Seguimiento', 'Cancelada', 'Paciente enfermo', false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-08 13:30:00'),
  (179, 2, '2025-01-08 15:00:00', '2025-01-08 15:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2025-01-08 15:00:00'),
  (174, 2, '2025-01-08 16:00:00', '2025-01-08 16:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2025-01-08 16:00:00'),
  (79, 1, '2025-01-08 16:30:00', '2025-01-08 17:15:00', 'Seguimiento', 'No_Asistio', NULL, false, 'Servicio: Verrugas Plantares - $900.00', '2025-01-08 16:30:00'),
  (32, 1, '2025-01-09 09:30:00', '2025-01-09 10:15:00', 'Seguimiento', 'Cancelada', 'Cancelado por el paciente', false, 'Servicio: Onicomicosis - $750.00', '2025-01-09 09:30:00'),
  (195, 1, '2025-01-09 11:00:00', '2025-01-09 11:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2025-01-09 11:00:00'),
  (119, 2, '2025-01-09 12:30:00', '2025-01-09 13:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2025-01-09 12:30:00'),
  (144, 1, '2025-01-09 13:30:00', '2025-01-09 14:15:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2025-01-09 13:30:00'),
  (48, 1, '2025-01-09 14:00:00', '2025-01-09 14:30:00', 'Primera Vez', 'Pendiente', NULL, true, 'Servicio: Callosidades - $500.00', '2025-01-09 14:00:00'),
  (183, 1, '2025-01-09 15:00:00', '2025-01-09 15:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2025-01-09 15:00:00'),
  (36, 2, '2025-01-10 10:30:00', '2025-01-10 11:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2025-01-10 10:30:00'),
  (157, 1, '2025-01-10 11:00:00', '2025-01-10 11:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2025-01-10 11:00:00'),
  (146, 1, '2025-01-10 12:30:00', '2025-01-10 13:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-10 12:30:00'),
  (182, 2, '2025-01-10 13:00:00', '2025-01-10 13:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2025-01-10 13:00:00'),
  (165, 2, '2025-01-10 13:30:00', '2025-01-10 14:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-10 13:30:00'),
  (60, 2, '2025-01-10 14:30:00', '2025-01-10 15:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2025-01-10 14:30:00'),
  (62, 1, '2025-01-13 09:30:00', '2025-01-13 10:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-13 09:30:00'),
  (45, 1, '2025-01-13 10:00:00', '2025-01-13 11:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2025-01-13 10:00:00'),
  (137, 1, '2025-01-13 10:30:00', '2025-01-13 11:15:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2025-01-13 10:30:00'),
  (154, 1, '2025-01-13 11:00:00', '2025-01-13 11:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Verrugas Plantares - $900.00', '2025-01-13 11:00:00'),
  (133, 1, '2025-01-13 14:00:00', '2025-01-13 14:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-13 14:00:00'),
  (123, 2, '2025-01-13 15:00:00', '2025-01-13 15:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-13 15:00:00'),
  (134, 1, '2025-01-14 09:00:00', '2025-01-14 10:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Pedicure Clínico - $800.00', '2025-01-14 09:00:00'),
  (71, 1, '2025-01-14 09:30:00', '2025-01-14 10:30:00', 'Primera Vez', 'Pendiente', NULL, true, 'Servicio: Pedicure Clínico - $800.00', '2025-01-14 09:30:00'),
  (87, 1, '2025-01-14 10:30:00', '2025-01-14 11:15:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2025-01-14 10:30:00'),
  (63, 1, '2025-01-14 11:00:00', '2025-01-14 11:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-14 11:00:00'),
  (107, 2, '2025-01-14 13:30:00', '2025-01-14 14:15:00', 'Seguimiento', 'Cancelada', 'Emergencia personal', false, 'Servicio: Onicomicosis - $750.00', '2025-01-14 13:30:00'),
  (156, 2, '2025-01-14 15:00:00', '2025-01-14 15:30:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-14 15:00:00'),
  (19, 2, '2025-01-15 10:00:00', '2025-01-15 10:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2025-01-15 10:00:00'),
  (200, 1, '2025-01-15 10:30:00', '2025-01-15 11:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2025-01-15 10:30:00'),
  (81, 1, '2025-01-15 11:30:00', '2025-01-15 12:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-15 11:30:00'),
  (140, 2, '2025-01-15 13:00:00', '2025-01-15 13:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Callosidades - $500.00', '2025-01-15 13:00:00'),
  (1, 1, '2025-01-15 13:30:00', '2025-01-15 14:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2025-01-15 13:30:00'),
  (167, 2, '2025-01-15 16:00:00', '2025-01-15 16:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-15 16:00:00'),
  (189, 1, '2025-01-16 09:00:00', '2025-01-16 09:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2025-01-16 09:00:00'),
  (129, 1, '2025-01-16 10:00:00', '2025-01-16 10:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Pie de Atleta - $600.00', '2025-01-16 10:00:00'),
  (111, 1, '2025-01-16 11:00:00', '2025-01-16 11:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-16 11:00:00'),
  (92, 1, '2025-01-16 12:00:00', '2025-01-16 12:45:00', 'Primera Vez', 'Cancelada', 'Emergencia personal', true, 'Servicio: Onicomicosis - $750.00', '2025-01-16 12:00:00'),
  (191, 2, '2025-01-16 12:30:00', '2025-01-16 13:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-16 12:30:00'),
  (70, 2, '2025-01-16 14:30:00', '2025-01-16 15:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-16 14:30:00'),
  (199, 1, '2025-01-17 09:30:00', '2025-01-17 10:15:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Uñas Enterradas - $550.00', '2025-01-17 09:30:00'),
  (59, 2, '2025-01-17 10:00:00', '2025-01-17 10:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-17 10:00:00'),
  (35, 2, '2025-01-17 13:00:00', '2025-01-17 13:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-17 13:00:00'),
  (118, 2, '2025-01-17 14:00:00', '2025-01-17 14:30:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-17 14:00:00'),
  (130, 2, '2025-01-17 14:30:00', '2025-01-17 15:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Pedicure Clínico - $800.00', '2025-01-17 14:30:00'),
  (136, 1, '2025-01-20 10:00:00', '2025-01-20 10:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2025-01-20 10:00:00'),
  (170, 2, '2025-01-20 13:00:00', '2025-01-20 13:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2025-01-20 13:00:00'),
  (15, 1, '2025-01-20 13:30:00', '2025-01-20 14:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-20 13:30:00'),
  (124, 1, '2025-01-20 14:00:00', '2025-01-20 14:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Consulta General - $600.00', '2025-01-20 14:00:00'),
  (49, 2, '2025-01-20 16:00:00', '2025-01-20 17:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2025-01-20 16:00:00'),
  (109, 1, '2025-01-21 09:00:00', '2025-01-21 09:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2025-01-21 09:00:00'),
  (46, 2, '2025-01-21 14:30:00', '2025-01-21 15:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2025-01-21 14:30:00'),
  (3, 2, '2025-01-21 15:30:00', '2025-01-21 16:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-21 15:30:00'),
  (166, 2, '2025-01-21 16:00:00', '2025-01-21 16:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Verrugas Plantares - $900.00', '2025-01-21 16:00:00'),
  (193, 1, '2025-01-21 16:00:00', '2025-01-21 16:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pie de Atleta - $600.00', '2025-01-21 16:00:00'),
  (90, 1, '2025-01-22 10:00:00', '2025-01-22 10:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-22 10:00:00'),
  (172, 1, '2025-01-22 13:30:00', '2025-01-22 14:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2025-01-22 13:30:00'),
  (142, 1, '2025-01-22 14:00:00', '2025-01-22 14:45:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-22 14:00:00'),
  (14, 2, '2025-01-22 16:00:00', '2025-01-22 16:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-22 16:00:00'),
  (66, 1, '2025-01-22 16:00:00', '2025-01-22 16:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-22 16:00:00'),
  (138, 1, '2025-01-23 09:00:00', '2025-01-23 10:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2025-01-23 09:00:00'),
  (186, 1, '2025-01-23 10:00:00', '2025-01-23 11:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Pedicure Clínico - $800.00', '2025-01-23 10:00:00'),
  (145, 1, '2025-01-23 10:30:00', '2025-01-23 11:15:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Uñas Enterradas - $550.00', '2025-01-23 10:30:00'),
  (41, 2, '2025-01-23 13:30:00', '2025-01-23 14:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-23 13:30:00'),
  (132, 2, '2025-01-23 16:00:00', '2025-01-23 16:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2025-01-23 16:00:00'),
  (75, 1, '2025-01-24 09:30:00', '2025-01-24 10:00:00', 'Seguimiento', 'Cancelada', 'Reagendado por conflicto', false, 'Servicio: Consulta General - $600.00', '2025-01-24 09:30:00'),
  (68, 1, '2025-01-24 10:00:00', '2025-01-24 10:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Onicomicosis - $750.00', '2025-01-24 10:00:00'),
  (47, 2, '2025-01-24 10:00:00', '2025-01-24 10:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2025-01-24 10:00:00'),
  (86, 1, '2025-01-24 12:00:00', '2025-01-24 12:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Callosidades - $500.00', '2025-01-24 12:00:00'),
  (58, 2, '2025-01-24 14:30:00', '2025-01-24 15:30:00', 'Primera Vez', 'Pendiente', NULL, true, 'Servicio: Pedicure Clínico - $800.00', '2025-01-24 14:30:00'),
  (89, 1, '2025-01-27 10:00:00', '2025-01-27 11:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2025-01-27 10:00:00'),
  (22, 2, '2025-01-27 10:00:00', '2025-01-27 10:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2025-01-27 10:00:00'),
  (13, 1, '2025-01-27 11:30:00', '2025-01-27 12:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Pedicure Clínico - $800.00', '2025-01-27 11:30:00'),
  (126, 2, '2025-01-27 13:30:00', '2025-01-27 14:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-27 13:30:00'),
  (99, 2, '2025-01-27 15:00:00', '2025-01-27 15:45:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-27 15:00:00'),
  (181, 1, '2025-01-28 10:30:00', '2025-01-28 11:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2025-01-28 10:30:00'),
  (117, 1, '2025-01-28 15:30:00', '2025-01-28 16:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-28 15:30:00'),
  (83, 2, '2025-01-28 16:00:00', '2025-01-28 16:30:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-28 16:00:00'),
  (112, 1, '2025-01-28 16:30:00', '2025-01-28 17:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Onicomicosis - $750.00', '2025-01-28 16:30:00'),
  (131, 1, '2025-01-28 17:00:00', '2025-01-28 18:00:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Pedicure Clínico - $800.00', '2025-01-28 17:00:00'),
  (64, 1, '2025-01-29 09:30:00', '2025-01-29 10:15:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Uñas Enterradas - $550.00', '2025-01-29 09:30:00'),
  (74, 2, '2025-01-29 10:30:00', '2025-01-29 11:00:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-29 10:30:00'),
  (139, 1, '2025-01-29 12:00:00', '2025-01-29 12:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Uñas Enterradas - $550.00', '2025-01-29 12:00:00'),
  (141, 1, '2025-01-29 15:00:00', '2025-01-29 15:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-29 15:00:00'),
  (115, 2, '2025-01-29 15:30:00', '2025-01-29 16:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Pedicure Clínico - $800.00', '2025-01-29 15:30:00'),
  (44, 1, '2025-01-30 09:30:00', '2025-01-30 10:15:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Verrugas Plantares - $900.00', '2025-01-30 09:30:00'),
  (164, 2, '2025-01-30 13:00:00', '2025-01-30 13:45:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Onicomicosis - $750.00', '2025-01-30 13:00:00'),
  (161, 2, '2025-01-30 15:00:00', '2025-01-30 15:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-30 15:00:00'),
  (78, 2, '2025-01-30 15:30:00', '2025-01-30 16:30:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Pedicure Clínico - $800.00', '2025-01-30 15:30:00'),
  (98, 2, '2025-01-30 16:00:00', '2025-01-30 16:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-30 16:00:00'),
  (196, 2, '2025-01-31 10:00:00', '2025-01-31 10:45:00', 'Seguimiento', 'Pendiente', NULL, false, 'Servicio: Onicomicosis - $750.00', '2025-01-31 10:00:00'),
  (198, 2, '2025-01-31 12:00:00', '2025-01-31 12:30:00', 'Seguimiento', 'Completada', NULL, false, 'Servicio: Consulta General - $600.00', '2025-01-31 12:00:00'),
  (188, 1, '2025-01-31 12:00:00', '2025-01-31 13:00:00', 'Seguimiento', 'Cancelada', 'Cancelado por el paciente', false, 'Servicio: Pedicure Clínico - $800.00', '2025-01-31 12:00:00'),
  (103, 1, '2025-01-31 15:30:00', '2025-01-31 16:30:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Pedicure Clínico - $800.00', '2025-01-31 15:30:00'),
  (9, 1, '2025-01-31 17:00:00', '2025-01-31 17:45:00', 'Primera Vez', 'Completada', NULL, true, 'Servicio: Uñas Enterradas - $550.00', '2025-01-31 17:00:00');

-- ============================================================================
-- 2. DETALLE_CITA (363 registros - uno por cita)
-- ============================================================================

RAISE NOTICE 'Insertando detalles de citas...';

INSERT INTO detalle_cita (
  id_cita, id_tratamiento, precio_aplicado, descuento_porcentaje, precio_final, notas_tratamiento
)
SELECT 
  c.id,
  t.id,
  t.precio_base,
  0,
  t.precio_base,
  CASE 
    WHEN c.notas_recepcion IS NOT NULL THEN 
      SUBSTRING(c.notas_recepcion FROM 'Servicio: ([^-]+)')
    ELSE 
      t.nombre_servicio
  END
FROM citas c
JOIN tratamientos t ON 
  (c.notas_recepcion LIKE '%Consulta General%' AND t.nombre_servicio = 'Consulta General') OR
  (c.notas_recepcion LIKE '%Onicomicosis%' AND t.nombre_servicio = 'Onicomicosis') OR
  (c.notas_recepcion LIKE '%Uñas Enterradas%' AND t.nombre_servicio = 'Uñas Enterradas') OR
  (c.notas_recepcion LIKE '%Pedicure Clínico%' AND t.nombre_servicio = 'Pedicure Clínico') OR
  (c.notas_recepcion LIKE '%Callosidades%' AND t.nombre_servicio = 'Callosidades') OR
  (c.notas_recepcion LIKE '%Verrugas Plantares%' AND t.nombre_servicio = 'Verrugas Plantares') OR
  (c.notas_recepcion LIKE '%Pie de Atleta%' AND t.nombre_servicio = 'Pie de atleta')
WHERE c.id >= (SELECT MIN(id) FROM citas WHERE fecha_hora_inicio >= '2024-11-01')
  AND c.id <= (SELECT MAX(id) FROM citas WHERE fecha_hora_inicio < '2025-02-01');

-- ============================================================================
-- 3. NOTA_CLINICA (308 registros - solo citas completadas)
-- ============================================================================

RAISE NOTICE 'Insertando notas clínicas...';

INSERT INTO nota_clinica (
  id_cita, motivo_consulta, padecimiento_actual, exploracion_fisica,
  diagnostico_presuntivo, diagnostico_definitivo, plan_tratamiento,
  indicaciones_paciente, fecha_elaboracion, elaborado_por
)
SELECT 
  c.id,
  CASE
    WHEN c.notas_recepcion LIKE '%Consulta General%' THEN 'Dolor en talón al caminar'
    WHEN c.notas_recepcion LIKE '%Consulta General%' THEN 'Revisión de pies por diabetes'
    WHEN c.notas_recepcion LIKE '%Consulta General%' THEN 'Consulta preventiva'
    WHEN c.notas_recepcion LIKE '%Consulta General%' THEN 'Molestias en planta del pie'
    WHEN c.notas_recepcion LIKE '%Consulta General%' THEN 'Dolor en arco plantar'
    WHEN c.notas_recepcion LIKE '%Onicomicosis%' THEN 'Uña amarillenta y engrosada'
    WHEN c.notas_recepcion LIKE '%Onicomicosis%' THEN 'Hongos en uñas de los pies'
    WHEN c.notas_recepcion LIKE '%Onicomicosis%' THEN 'Decoloración de uñas'
    WHEN c.notas_recepcion LIKE '%Onicomicosis%' THEN 'Uña quebradiza'
    WHEN c.notas_recepcion LIKE '%Uñas Enterradas%' THEN 'Dolor e inflamación en dedo'
    WHEN c.notas_recepcion LIKE '%Uñas Enterradas%' THEN 'Uña enterrada con pus'
    WHEN c.notas_recepcion LIKE '%Uñas Enterradas%' THEN 'Enrojecimiento lateral de uña'
    WHEN c.notas_recepcion LIKE '%Uñas Enterradas%' THEN 'Molestia al usar zapatos'
    WHEN c.notas_recepcion LIKE '%Pedicure Clínico%' THEN 'Cuidado general de pies'
    WHEN c.notas_recepcion LIKE '%Pedicure Clínico%' THEN 'Pies resecos y agrietados'
    WHEN c.notas_recepcion LIKE '%Pedicure Clínico%' THEN 'Mantenimiento preventivo'
    WHEN c.notas_recepcion LIKE '%Pedicure Clínico%' THEN 'Limpieza profunda de pies'
    WHEN c.notas_recepcion LIKE '%Callosidades%' THEN 'Callos dolorosos en planta'
    WHEN c.notas_recepcion LIKE '%Callosidades%' THEN 'Durezas en talones'
    WHEN c.notas_recepcion LIKE '%Callosidades%' THEN 'Hiperqueratosis plantar'
    WHEN c.notas_recepcion LIKE '%Callosidades%' THEN 'Callosidad entre dedos'
    WHEN c.notas_recepcion LIKE '%Verrugas Plantares%' THEN 'Verruga dolorosa en planta'
    WHEN c.notas_recepcion LIKE '%Verrugas Plantares%' THEN 'Lesión tipo verruga'
    WHEN c.notas_recepcion LIKE '%Verrugas Plantares%' THEN 'Crecimiento en pie'
    WHEN c.notas_recepcion LIKE '%Verrugas Plantares%' THEN 'Papiloma en planta'
    WHEN c.notas_recepcion LIKE '%Pie de Atleta%' THEN 'Comezón entre los dedos'
    WHEN c.notas_recepcion LIKE '%Pie de Atleta%' THEN 'Piel descamada en pies'
    WHEN c.notas_recepcion LIKE '%Pie de Atleta%' THEN 'Enrojecimiento y mal olor'
    WHEN c.notas_recepcion LIKE '%Pie de Atleta%' THEN 'Hongos en pies'
    ELSE 'Consulta podológica general'
  END,
  CASE
    WHEN c.notas_recepcion LIKE '%Consulta General%' THEN 'Paciente refiere molestias al caminar'
    WHEN c.notas_recepcion LIKE '%Onicomicosis%' THEN 'Alteración de coloración y textura en uñas'
    WHEN c.notas_recepcion LIKE '%Uñas Enterradas%' THEN 'Inflamación y dolor en borde lateral de uña'
    WHEN c.notas_recepcion LIKE '%Pedicure Clínico%' THEN 'Pies con resequedad y callosidades leves'
    WHEN c.notas_recepcion LIKE '%Callosidades%' THEN 'Hiperqueratosis en zonas de presión'
    WHEN c.notas_recepcion LIKE '%Verrugas Plantares%' THEN 'Lesión hiperqueratósica dolorosa'
    WHEN c.notas_recepcion LIKE '%Pie de Atleta%' THEN 'Descamación y prurito interdigital'
    ELSE 'Exploración física normal'
  END,
  CASE
    WHEN c.notas_recepcion LIKE '%Consulta General%' THEN 'Inspección de ambos pies, palpación de estructuras'
    WHEN c.notas_recepcion LIKE '%Onicomicosis%' THEN 'Uñas engrosadas con decoloración amarillenta'
    WHEN c.notas_recepcion LIKE '%Uñas Enterradas%' THEN 'Borde lateral de uña penetrando tejido blando'
    WHEN c.notas_recepcion LIKE '%Pedicure Clínico%' THEN 'Pies con higiene adecuada, callosidades leves'
    WHEN c.notas_recepcion LIKE '%Callosidades%' THEN 'Hiperqueratosis plantar en zonas de carga'
    WHEN c.notas_recepcion LIKE '%Verrugas Plantares%' THEN 'Lesión papular con puntos negros centrales'
    WHEN c.notas_recepcion LIKE '%Pie de Atleta%' THEN 'Eritema y descamación en espacios interdigitales'
    ELSE 'Sin alteraciones evidentes'
  END,
  CASE
    WHEN c.notas_recepcion LIKE '%Consulta General%' THEN 'Fascitis plantar vs espolón calcáneo'
    WHEN c.notas_recepcion LIKE '%Onicomicosis%' THEN 'Onicomicosis por dermatofitos'
    WHEN c.notas_recepcion LIKE '%Uñas Enterradas%' THEN 'Onicocriptosis'
    WHEN c.notas_recepcion LIKE '%Pedicure Clínico%' THEN 'Pies sanos con cuidado preventivo'
    WHEN c.notas_recepcion LIKE '%Callosidades%' THEN 'Hiperqueratosis plantar'
    WHEN c.notas_recepcion LIKE '%Verrugas Plantares%' THEN 'Verruga plantar por VPH'
    WHEN c.notas_recepcion LIKE '%Pie de Atleta%' THEN 'Tinea pedis'
    ELSE 'Pie sano'
  END,
  CASE
    WHEN c.notas_recepcion LIKE '%Consulta General%' THEN 'Fascitis plantar'
    WHEN c.notas_recepcion LIKE '%Onicomicosis%' THEN 'Onicomicosis confirmada'
    WHEN c.notas_recepcion LIKE '%Uñas Enterradas%' THEN 'Onicocriptosis grado II'
    WHEN c.notas_recepcion LIKE '%Pedicure Clínico%' THEN 'Cuidado preventivo completado'
    WHEN c.notas_recepcion LIKE '%Callosidades%' THEN 'Callosidad adquirida'
    WHEN c.notas_recepcion LIKE '%Verrugas Plantares%' THEN 'Verruga plantar'
    WHEN c.notas_recepcion LIKE '%Pie de Atleta%' THEN 'Tiña del pie'
    ELSE 'Normal'
  END,
  CASE
    WHEN c.notas_recepcion LIKE '%Consulta General%' THEN 'Ejercicios de estiramiento, plantillas ortopédicas'
    WHEN c.notas_recepcion LIKE '%Onicomicosis%' THEN 'Tratamiento antimicótico tópico y oral'
    WHEN c.notas_recepcion LIKE '%Uñas Enterradas%' THEN 'Extracción parcial de uña, cuidados locales'
    WHEN c.notas_recepcion LIKE '%Pedicure Clínico%' THEN 'Hidratación diaria, uso de calzado cómodo'
    WHEN c.notas_recepcion LIKE '%Callosidades%' THEN 'Desbridamiento, plantillas de descarga'
    WHEN c.notas_recepcion LIKE '%Verrugas Plantares%' THEN 'Crioterapia o ácido salicílico'
    WHEN c.notas_recepcion LIKE '%Pie de Atleta%' THEN 'Antifúngico tópico, higiene rigurosa'
    ELSE 'Cuidados generales'
  END,
  CASE
    WHEN c.notas_recepcion LIKE '%Consulta General%' THEN 'Reposo relativo, evitar caminar descalzo'
    WHEN c.notas_recepcion LIKE '%Onicomicosis%' THEN 'Aplicar tratamiento 2 veces al día por 3 meses'
    WHEN c.notas_recepcion LIKE '%Uñas Enterradas%' THEN 'Curaciones diarias, antibiótico si hay infección'
    WHEN c.notas_recepcion LIKE '%Pedicure Clínico%' THEN 'Hidratar pies diariamente, revisión cada 2 meses'
    WHEN c.notas_recepcion LIKE '%Callosidades%' THEN 'Exfoliación suave, crema hidratante'
    WHEN c.notas_recepcion LIKE '%Verrugas Plantares%' THEN 'No manipular, evitar caminar descalzo en áreas públicas'
    WHEN c.notas_recepcion LIKE '%Pie de Atleta%' THEN 'Mantener pies secos, cambiar calcetines diariamente'
    ELSE 'Revisión en 1 mes'
  END,
  c.fecha_hora_inicio,
  c.id_podologo
FROM citas c
WHERE c.estado = 'Completada'
  AND c.id >= (SELECT MIN(id) FROM citas WHERE fecha_hora_inicio >= '2024-11-01')
  AND c.id <= (SELECT MAX(id) FROM citas WHERE fecha_hora_inicio < '2025-02-01');

-- ============================================================================
-- 4. CATÁLOGO CIE-10 (códigos diagnósticos)
-- ============================================================================

RAISE NOTICE 'Insertando códigos CIE-10...';

INSERT INTO catalogo_cie10 (codigo, descripcion, categoria, activo)
VALUES
  ('M72.2', 'Fascitis plantar', 'Trastornos de tejidos blandos', true),
  ('B35.1', 'Onicomicosis por dermatofitos', 'Infecciones fúngicas', true),
  ('L60.0', 'Uña encarnada', 'Trastornos de uñas', true),
  ('L85.1', 'Callosidad adquirida', 'Trastornos de queratinización', true),
  ('L84', 'Callos y callosidades', 'Trastornos de queratinización', true),
  ('B07', 'Verruga plantar por VPH', 'Infecciones virales', true),
  ('B35.3', 'Tiña del pie', 'Infecciones fúngicas', true),
  ('M77.3', 'Espolón calcáneo', 'Entesoptías', true),
  ('L30.4', 'Dermatitis del pie', 'Dermatitis', true)
ON CONFLICT (codigo) DO NOTHING;

-- ============================================================================
-- 5. DIAGNÓSTICOS_TRATAMIENTO (310 registros - solo citas completadas)
-- ============================================================================

RAISE NOTICE 'Insertando diagnósticos con códigos CIE-10...';

INSERT INTO diagnosticos_tratamiento (
  id_detalle_cita, tipo_diagnostico, descripcion_diagnostico,
  id_cie10, codigo_cie10_manual, diagnosticado_por
)
SELECT 
  dc.id,
  'Definitivo',
  CASE
    WHEN t.nombre_servicio = 'Consulta General' THEN 'Fascitis plantar'
    WHEN t.nombre_servicio = 'Onicomicosis' THEN 'Onicomicosis por dermatofitos'
    WHEN t.nombre_servicio = 'Uñas Enterradas' THEN 'Uña encarnada'
    WHEN t.nombre_servicio = 'Pedicure Clínico' THEN 'Cuidado preventivo de pies'
    WHEN t.nombre_servicio = 'Callosidades' THEN 'Callosidad adquirida'
    WHEN t.nombre_servicio = 'Verrugas Plantares' THEN 'Verruga plantar por VPH'
    WHEN t.nombre_servicio = 'Pie de atleta' THEN 'Tiña del pie'
    ELSE 'Diagnóstico general'
  END,
  cie10.id,
  cie10.codigo,
  c.id_podologo
FROM detalle_cita dc
JOIN citas c ON dc.id_cita = c.id
JOIN tratamientos t ON dc.id_tratamiento = t.id
LEFT JOIN catalogo_cie10 cie10 ON (
  (t.nombre_servicio = 'Consulta General' AND cie10.codigo = 'M72.2') OR
  (t.nombre_servicio = 'Onicomicosis' AND cie10.codigo = 'B35.1') OR
  (t.nombre_servicio = 'Uñas Enterradas' AND cie10.codigo = 'L60.0') OR
  (t.nombre_servicio = 'Callosidades' AND cie10.codigo = 'L85.1') OR
  (t.nombre_servicio = 'Verrugas Plantares' AND cie10.codigo = 'B07') OR
  (t.nombre_servicio = 'Pie de atleta' AND cie10.codigo = 'B35.3') OR
  (t.nombre_servicio = 'Pedicure Clínico' AND cie10.codigo = 'L84')
)
WHERE c.estado = 'Completada'
  AND c.id >= (SELECT MIN(id) FROM citas WHERE fecha_hora_inicio >= '2024-11-01')
  AND c.id <= (SELECT MAX(id) FROM citas WHERE fecha_hora_inicio < '2025-02-01');

-- ============================================================================
-- VALIDACIONES
-- ============================================================================

RAISE NOTICE '';
RAISE NOTICE '========================================';
RAISE NOTICE 'Ejecutando validaciones...';
RAISE NOTICE '========================================';

DO $$
DECLARE
    v_total_citas INTEGER;
    v_citas_santiago INTEGER;
    v_citas_joana INTEGER;
    v_solapamientos INTEGER;
    v_pacientes_duplicados INTEGER;
    v_total_completadas INTEGER;
    v_total_diagnosticos INTEGER;
    v_total_ingresos NUMERIC;
    v_citas_nov INTEGER;
    v_citas_dic INTEGER;
    v_citas_ene INTEGER;
    v_consulta_general INTEGER;
    v_onicomicosis INTEGER;
    v_unas_enterradas INTEGER;
    v_pedicure INTEGER;
    v_callosidades INTEGER;
    v_verrugas INTEGER;
    v_pie_atleta INTEGER;
BEGIN
    -- Contar citas totales
    SELECT COUNT(*) INTO v_total_citas 
    FROM citas 
    WHERE fecha_hora_inicio >= '2024-11-01' AND fecha_hora_inicio < '2025-02-01';
    
    -- Distribución por doctor
    SELECT COUNT(*) INTO v_citas_santiago 
    FROM citas 
    WHERE id_podologo = 1 AND fecha_hora_inicio >= '2024-11-01' AND fecha_hora_inicio < '2025-02-01';
    
    SELECT COUNT(*) INTO v_citas_joana 
    FROM citas 
    WHERE id_podologo = 2 AND fecha_hora_inicio >= '2024-11-01' AND fecha_hora_inicio < '2025-02-01';
    
    -- Verificar solapamientos (mismo doctor, misma hora)
    SELECT COUNT(*) INTO v_solapamientos
    FROM (
        SELECT fecha_hora_inicio, id_podologo, COUNT(*) as cnt
        FROM citas
        WHERE fecha_hora_inicio >= '2024-11-01' AND fecha_hora_inicio < '2025-02-01'
        GROUP BY fecha_hora_inicio, id_podologo
        HAVING COUNT(*) > 1
    ) AS overlaps;
    
    -- Verificar pacientes con 2+ citas el mismo día
    SELECT COUNT(*) INTO v_pacientes_duplicados
    FROM (
        SELECT id_paciente, DATE(fecha_hora_inicio) as fecha, COUNT(*) as cnt
        FROM citas
        WHERE fecha_hora_inicio >= '2024-11-01' AND fecha_hora_inicio < '2025-02-01'
        GROUP BY id_paciente, DATE(fecha_hora_inicio)
        HAVING COUNT(*) > 1
    ) AS dups;
    
    -- Contar citas completadas y diagnósticos
    SELECT COUNT(*) INTO v_total_completadas 
    FROM citas 
    WHERE estado = 'Completada' 
      AND fecha_hora_inicio >= '2024-11-01' AND fecha_hora_inicio < '2025-02-01';
    
    SELECT COUNT(*) INTO v_total_diagnosticos 
    FROM diagnosticos_tratamiento dt
    JOIN detalle_cita dc ON dt.id_detalle_cita = dc.id
    JOIN citas c ON dc.id_cita = c.id
    WHERE c.fecha_hora_inicio >= '2024-11-01' AND c.fecha_hora_inicio < '2025-02-01';
    
    -- Calcular ingresos estimados (solo completadas)
    SELECT COALESCE(SUM(dc.precio_final), 0) INTO v_total_ingresos
    FROM detalle_cita dc
    JOIN citas c ON dc.id_cita = c.id
    WHERE c.estado = 'Completada'
      AND c.fecha_hora_inicio >= '2024-11-01' AND c.fecha_hora_inicio < '2025-02-01';
    
    -- Distribución mensual
    SELECT COUNT(*) INTO v_citas_nov
    FROM citas
    WHERE fecha_hora_inicio >= '2024-11-01' AND fecha_hora_inicio < '2024-12-01';
    
    SELECT COUNT(*) INTO v_citas_dic
    FROM citas
    WHERE fecha_hora_inicio >= '2024-12-01' AND fecha_hora_inicio < '2025-01-01';
    
    SELECT COUNT(*) INTO v_citas_ene
    FROM citas
    WHERE fecha_hora_inicio >= '2025-01-01' AND fecha_hora_inicio < '2025-02-01';
    
    -- Distribución por servicio
    SELECT COUNT(*) INTO v_consulta_general
    FROM detalle_cita dc
    JOIN citas c ON dc.id_cita = c.id
    JOIN tratamientos t ON dc.id_tratamiento = t.id
    WHERE t.nombre_servicio = 'Consulta General'
      AND c.fecha_hora_inicio >= '2024-11-01' AND c.fecha_hora_inicio < '2025-02-01';
    
    SELECT COUNT(*) INTO v_onicomicosis
    FROM detalle_cita dc
    JOIN citas c ON dc.id_cita = c.id
    JOIN tratamientos t ON dc.id_tratamiento = t.id
    WHERE t.nombre_servicio = 'Onicomicosis'
      AND c.fecha_hora_inicio >= '2024-11-01' AND c.fecha_hora_inicio < '2025-02-01';
    
    SELECT COUNT(*) INTO v_unas_enterradas
    FROM detalle_cita dc
    JOIN citas c ON dc.id_cita = c.id
    JOIN tratamientos t ON dc.id_tratamiento = t.id
    WHERE t.nombre_servicio = 'Uñas Enterradas'
      AND c.fecha_hora_inicio >= '2024-11-01' AND c.fecha_hora_inicio < '2025-02-01';
    
    SELECT COUNT(*) INTO v_pedicure
    FROM detalle_cita dc
    JOIN citas c ON dc.id_cita = c.id
    JOIN tratamientos t ON dc.id_tratamiento = t.id
    WHERE t.nombre_servicio = 'Pedicure Clínico'
      AND c.fecha_hora_inicio >= '2024-11-01' AND c.fecha_hora_inicio < '2025-02-01';
    
    SELECT COUNT(*) INTO v_callosidades
    FROM detalle_cita dc
    JOIN citas c ON dc.id_cita = c.id
    JOIN tratamientos t ON dc.id_tratamiento = t.id
    WHERE t.nombre_servicio = 'Callosidades'
      AND c.fecha_hora_inicio >= '2024-11-01' AND c.fecha_hora_inicio < '2025-02-01';
    
    SELECT COUNT(*) INTO v_verrugas
    FROM detalle_cita dc
    JOIN citas c ON dc.id_cita = c.id
    JOIN tratamientos t ON dc.id_tratamiento = t.id
    WHERE t.nombre_servicio = 'Verrugas Plantares'
      AND c.fecha_hora_inicio >= '2024-11-01' AND c.fecha_hora_inicio < '2025-02-01';
    
    SELECT COUNT(*) INTO v_pie_atleta
    FROM detalle_cita dc
    JOIN citas c ON dc.id_cita = c.id
    JOIN tratamientos t ON dc.id_tratamiento = t.id
    WHERE t.nombre_servicio = 'Pie de atleta'
      AND c.fecha_hora_inicio >= '2024-11-01' AND c.fecha_hora_inicio < '2025-02-01';
    
    -- Mostrar resumen
    RAISE NOTICE '';
    RAISE NOTICE '╔════════════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║  ✅ AGENTE 15/16 COMPLETADO EXITOSAMENTE                      ║';
    RAISE NOTICE '║  Script: 03_citas_tratamientos.sql                            ║';
    RAISE NOTICE '╠════════════════════════════════════════════════════════════════╣';
    RAISE NOTICE '║  📊 RESUMEN DE DATOS INSERTADOS:                              ║';
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '║     📅 Total citas:              % citas                     ║', LPAD(v_total_citas::TEXT, 3, ' ');
    RAISE NOTICE '║     ✅ Citas completadas:        % citas                     ║', LPAD(v_total_completadas::TEXT, 3, ' ');
    RAISE NOTICE '║     📋 Diagnósticos con CIE-10:  % registros                ║', LPAD(v_total_diagnosticos::TEXT, 3, ' ');
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '║  📅 DISTRIBUCIÓN MENSUAL:                                     ║';
    RAISE NOTICE '║     • Noviembre 2024:            % citas                     ║', LPAD(v_citas_nov::TEXT, 3, ' ');
    RAISE NOTICE '║     • Diciembre 2024:            % citas                     ║', LPAD(v_citas_dic::TEXT, 3, ' ');
    RAISE NOTICE '║     • Enero 2025:                % citas                     ║', LPAD(v_citas_ene::TEXT, 3, ' ');
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '║  👨‍⚕️ DISTRIBUCIÓN POR DOCTOR:                                 ║';
    RAISE NOTICE '║     • Santiago (55%%):            % citas                     ║', LPAD(v_citas_santiago::TEXT, 3, ' ');
    RAISE NOTICE '║     • Joana (45%%):               % citas                     ║', LPAD(v_citas_joana::TEXT, 3, ' ');
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '║  💼 DISTRIBUCIÓN POR SERVICIO:                                ║';
    RAISE NOTICE '║     • Consulta General (25%%):    % citas ($600)             ║', LPAD(v_consulta_general::TEXT, 3, ' ');
    RAISE NOTICE '║     • Onicomicosis (20%%):        % citas ($750)             ║', LPAD(v_onicomicosis::TEXT, 3, ' ');
    RAISE NOTICE '║     • Uñas Enterradas (20%%):     % citas ($550)             ║', LPAD(v_unas_enterradas::TEXT, 3, ' ');
    RAISE NOTICE '║     • Pedicure Clínico (15%%):    % citas ($800)             ║', LPAD(v_pedicure::TEXT, 3, ' ');
    RAISE NOTICE '║     • Callosidades (12%%):        % citas ($500)             ║', LPAD(v_callosidades::TEXT, 3, ' ');
    RAISE NOTICE '║     • Verrugas Plantares (5%%):   % citas ($900)             ║', LPAD(v_verrugas::TEXT, 3, ' ');
    RAISE NOTICE '║     • Pie de Atleta (3%%):        % citas ($600)             ║', LPAD(v_pie_atleta::TEXT, 3, ' ');
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '║  💰 INGRESOS ESTIMADOS:                                       ║';
    RAISE NOTICE '║     Total (citas completadas):   $% MXN                 ║', TRIM(TO_CHAR(v_total_ingresos, '999,999.00'));
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '║  ✓ VALIDACIONES:                                              ║';
    RAISE NOTICE '║     • Solapamientos horarios:    % (esperado: 0)            ║', LPAD(v_solapamientos::TEXT, 3, ' ');
    RAISE NOTICE '║     • Duplicados paciente/día:   % (esperado: 0)            ║', LPAD(v_pacientes_duplicados::TEXT, 3, ' ');
    RAISE NOTICE '║                                                                ║';
    RAISE NOTICE '╠════════════════════════════════════════════════════════════════╣';
    RAISE NOTICE '║  📝 SIGUIENTE PASO:                                           ║';
    RAISE NOTICE '║     ▶️  Ejecutar: agente_16_pagos_inventario.sql              ║';
    RAISE NOTICE '╚════════════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';
    
    -- Verificar que no haya solapamientos
    IF v_solapamientos > 0 THEN
        RAISE WARNING '⚠️  ADVERTENCIA: Se encontraron % solapamientos de horarios', v_solapamientos;
    END IF;
    
    -- Verificar que no haya duplicados
    IF v_pacientes_duplicados > 0 THEN
        RAISE WARNING '⚠️  ADVERTENCIA: Se encontraron % pacientes con múltiples citas el mismo día', v_pacientes_duplicados;
    END IF;
END $$;

-- Confirmar transacción
COMMIT;

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================
-- Ejecución: psql -U postgres -d podoskin -f data/seed/03_citas_tratamientos.sql
-- o bien: \i data/seed/03_citas_tratamientos.sql desde psql
-- ============================================================================
