-- Limpiar datos existentes
TRUNCATE TABLE alergias, antecedentes_medicos, citas, detalles_factura, diagnosticos, 
               facturas, gastos, inventario, movimientos_inventario, pacientes, pagos, 
               productos, proveedores, usuarios, cortes_caja CASCADE;

-- Reiniciar secuencias
ALTER SEQUENCE usuarios_id_seq RESTART WITH 1;
ALTER SEQUENCE pacientes_id_seq RESTART WITH 1;
ALTER SEQUENCE citas_id_seq RESTART WITH 1;
ALTER SEQUENCE diagnosticos_id_seq RESTART WITH 1;
ALTER SEQUENCE facturas_id_seq RESTART WITH 1;
ALTER SEQUENCE detalles_factura_id_seq RESTART WITH 1;
ALTER SEQUENCE pagos_id_seq RESTART WITH 1;
ALTER SEQUENCE productos_id_seq RESTART WITH 1;
ALTER SEQUENCE proveedores_id_seq RESTART WITH 1;
ALTER SEQUENCE inventario_id_seq RESTART WITH 1;
ALTER SEQUENCE movimientos_inventario_id_seq RESTART WITH 1;
ALTER SEQUENCE gastos_id_seq RESTART WITH 1;
ALTER SEQUENCE cortes_caja_id_seq RESTART WITH 1;
ALTER SEQUENCE antecedentes_medicos_id_seq RESTART WITH 1;
ALTER SEQUENCE alergias_id_seq RESTART WITH 1;

-- Insertar Usuarios (contraseñas hasheadas con bcrypt)
INSERT INTO usuarios (nombre, email, password, rol, estado, created_at, updated_at) VALUES
('Dr. Juan Pérez', 'juan.perez@podiskin.com', '$2b$10$YourHashedPasswordHere1', 'admin', 'activo', NOW(), NOW()),
('Dra. María García', 'maria.garcia@podiskin.com', '$2b$10$YourHashedPasswordHere2', 'medico', 'activo', NOW(), NOW()),
('Ana López', 'ana.lopez@podiskin.com', '$2b$10$YourHashedPasswordHere3', 'recepcionista', 'activo', NOW(), NOW()),
('Carlos Martínez', 'carlos.martinez@podiskin.com', '$2b$10$YourHashedPasswordHere4', 'medico', 'activo', NOW(), NOW()),
('Laura Sánchez', 'laura.sanchez@podiskin.com', '$2b$10$YourHashedPasswordHere5', 'recepcionista', 'inactivo', NOW(), NOW());

-- Insertar Pacientes
INSERT INTO pacientes (nombre, apellido, fecha_nacimiento, genero, telefono, email, direccion, ciudad, estado, codigo_postal, created_at, updated_at) VALUES
('Pedro', 'González', '1985-03-15', 'M', '555-0101', 'pedro.gonzalez@email.com', 'Calle Principal 123', 'Ciudad de México', 'CDMX', '01000', NOW(), NOW()),
('Lucía', 'Hernández', '1990-07-22', 'F', '555-0102', 'lucia.hernandez@email.com', 'Avenida Reforma 456', 'Ciudad de México', 'CDMX', '02000', NOW(), NOW()),
('Roberto', 'Ramírez', '1978-11-30', 'M', '555-0103', 'roberto.ramirez@email.com', 'Calle Juárez 789', 'Guadalajara', 'Jalisco', '44100', NOW(), NOW()),
('Carmen', 'Torres', '1995-01-18', 'F', '555-0104', 'carmen.torres@email.com', 'Boulevard Insurgentes 321', 'Monterrey', 'Nuevo León', '64000', NOW(), NOW()),
('Miguel', 'Flores', '1982-09-05', 'M', '555-0105', 'miguel.flores@email.com', 'Paseo de la Reforma 654', 'Ciudad de México', 'CDMX', '03000', NOW(), NOW()),
('Sofia', 'Morales', '1988-12-12', 'F', '555-0106', 'sofia.morales@email.com', 'Calle Madero 987', 'Puebla', 'Puebla', '72000', NOW(), NOW()),
('Javier', 'Ruiz', '1975-04-25', 'M', '555-0107', 'javier.ruiz@email.com', 'Avenida Hidalgo 147', 'Querétaro', 'Querétaro', '76000', NOW(), NOW()),
('Patricia', 'Jiménez', '1993-08-08', 'F', '555-0108', 'patricia.jimenez@email.com', 'Calle Morelos 258', 'Mérida', 'Yucatán', '97000', NOW(), NOW());

-- Insertar Antecedentes Médicos
INSERT INTO antecedentes_medicos (paciente_id, diabetes, hipertension, cardiopatias, alergias_medicamentos, cirugias_previas, otras_condiciones, created_at, updated_at) VALUES
(1, true, false, false, 'Ninguna', 'Apendicectomía (2010)', 'Ninguna', NOW(), NOW()),
(2, false, true, false, 'Penicilina', 'Ninguna', 'Asma leve', NOW(), NOW()),
(3, true, true, true, 'Ninguna', 'Bypass coronario (2015)', 'Colesterol alto', NOW(), NOW()),
(4, false, false, false, 'Ibuprofeno', 'Cesárea (2018)', 'Ninguna', NOW(), NOW()),
(5, false, false, false, 'Ninguna', 'Ninguna', 'Ninguna', NOW(), NOW());

-- Insertar Alergias
INSERT INTO alergias (paciente_id, alergia, severidad, created_at, updated_at) VALUES
(2, 'Penicilina', 'alta', NOW(), NOW()),
(3, 'Polen', 'media', NOW(), NOW()),
(4, 'Ibuprofeno', 'media', NOW(), NOW()),
(6, 'Mariscos', 'alta', NOW(), NOW());

-- Insertar Citas
INSERT INTO citas (paciente_id, medico_id, fecha_hora, motivo, estado, notas, created_at, updated_at) VALUES
(1, 2, '2024-01-15 09:00:00', 'Revisión rutinaria de pie diabético', 'completada', 'Paciente en buen estado', NOW(), NOW()),
(2, 2, '2024-01-15 10:30:00', 'Dolor en talón derecho', 'completada', 'Posible fascitis plantar', NOW(), NOW()),
(3, 4, '2024-01-16 11:00:00', 'Seguimiento post-operatorio', 'completada', 'Recuperación satisfactoria', NOW(), NOW()),
(4, 2, '2024-01-17 14:00:00', 'Consulta inicial - uñas encarnadas', 'completada', 'Se programó procedimiento', NOW(), NOW()),
(5, 4, '2024-01-18 09:30:00', 'Dolor en arco del pie', 'completada', 'Se ordenaron estudios', NOW(), NOW()),
(6, 2, '2024-01-19 15:00:00', 'Verrugas plantares', 'completada', 'Tratamiento aplicado', NOW(), NOW()),
(7, 4, '2024-01-22 10:00:00', 'Control de callosidades', 'completada', 'Tratamiento exitoso', NOW(), NOW()),
(8, 2, '2024-01-23 11:30:00', 'Hongos en uñas', 'completada', 'Medicamento prescrito', NOW(), NOW()),
(1, 2, '2024-01-25 09:00:00', 'Seguimiento pie diabético', 'confirmada', NULL, NOW(), NOW()),
(3, 4, '2024-01-26 14:00:00', 'Revisión general', 'pendiente', NULL, NOW(), NOW());

-- Insertar Diagnósticos
INSERT INTO diagnosticos (cita_id, descripcion, tratamiento, notas, created_at, updated_at) VALUES
(1, 'Pie diabético grado 1 - sin complicaciones', 'Continuar con cuidados preventivos, revisión cada 3 meses', 'Mantener control glucémico', NOW(), NOW()),
(2, 'Fascitis plantar aguda', 'Terapia física, antiinflamatorios, plantillas ortopédicas', 'Reposo relativo por 2 semanas', NOW(), NOW()),
(3, 'Post-operatorio satisfactorio de bunionectomía', 'Continuar ejercicios de rehabilitación', 'Sin signos de complicación', NOW(), NOW()),
(4, 'Onicocriptosis bilateral', 'Cirugía menor programada para próxima semana', 'Antibiótico preventivo', NOW(), NOW()),
(5, 'Tendinitis del tibial posterior', 'Fisioterapia, AINES, férula nocturna', 'Evaluar en 4 semanas', NOW(), NOW()),
(6, 'Verrugas plantares múltiples', 'Crioterapia aplicada, seguimiento en 3 semanas', 'Puede requerir sesiones adicionales', NOW(), NOW()),
(7, 'Hiperqueratosis plantar', 'Desbridamiento realizado, crema queratolítica', 'Control en 1 mes', NOW(), NOW()),
(8, 'Onicomicosis en ambos pies', 'Tratamiento antifúngico oral por 3 meses', 'Control mensual', NOW(), NOW());

-- Insertar Productos
INSERT INTO productos (nombre, descripcion, categoria, precio_unitario, codigo_barras, created_at, updated_at) VALUES
('Plantillas Ortopédicas Premium', 'Plantillas personalizables para pie plano y arco alto', 'ortopedia', 450.00, '7501234567890', NOW(), NOW()),
('Crema Antifúngica 30g', 'Tratamiento tópico para hongos en pies', 'medicamentos', 180.00, '7501234567891', NOW(), NOW()),
('Vendaje Compresivo 10cm', 'Vendaje elástico para soporte y compresión', 'suministros', 85.00, '7501234567892', NOW(), NOW()),
('Plantillas de Gel', 'Plantillas de gel para amortiguación', 'ortopedia', 320.00, '7501234567893', NOW(), NOW()),
('Antiséptico 500ml', 'Solución antiséptica para limpieza', 'suministros', 95.00, '7501234567894', NOW(), NOW()),
('Férula Nocturna Ajustable', 'Férula para fascitis plantar', 'ortopedia', 680.00, '7501234567895', NOW(), NOW()),
('Crema Hidratante Podológica', 'Crema especializada para pies secos', 'cuidado', 150.00, '7501234567896', NOW(), NOW()),
('Kit Cuidado de Uñas', 'Set profesional para cuidado de uñas', 'suministros', 220.00, '7501234567897', NOW(), NOW());

-- Insertar Proveedores
INSERT INTO proveedores (nombre, contacto, telefono, email, direccion, ciudad, estado, productos_suministrados, created_at, updated_at) VALUES
('Ortopedia Médica SA', 'Ing. Roberto Silva', '555-2001', 'ventas@ortopediamedica.com', 'Av. Industrial 100', 'Ciudad de México', 'CDMX', 'Plantillas, férulas, soportes ortopédicos', NOW(), NOW()),
('Farmacéutica del Centro', 'Lic. Ana Mendoza', '555-2002', 'contacto@farmaceuticacentro.com', 'Calle Comercio 200', 'Guadalajara', 'Jalisco', 'Medicamentos, cremas, antisépticos', NOW(), NOW()),
('Suministros Podológicos', 'Dr. Luis Vargas', '555-2003', 'info@suministrospodo.com', 'Boulevard Sur 300', 'Monterrey', 'Nuevo León', 'Instrumental, suministros médicos', NOW(), NOW()),
('Distribuidora Médica Nacional', 'Dra. Carmen Reyes', '555-2004', 'ventas@distribumed.com', 'Av. Central 400', 'Puebla', 'Puebla', 'Productos diversos de podología', NOW(), NOW());

-- Insertar Inventario
INSERT INTO inventario (producto_id, cantidad_actual, cantidad_minima, ultima_actualizacion) VALUES
(1, 25, 10, NOW()),
(2, 40, 15, NOW()),
(3, 60, 20, NOW()),
(4, 30, 10, NOW()),
(5, 15, 5, NOW()),
(6, 12, 5, NOW()),
(7, 35, 15, NOW()),
(8, 20, 10, NOW());

-- Insertar Facturas
INSERT INTO facturas (paciente_id, cita_id, fecha_emision, subtotal, descuento, impuestos, total, estado, metodo_pago, notas, created_at, updated_at) VALUES
(1, 1, '2024-01-15', 800.00, 0.00, 128.00, 928.00, 'pagada', 'efectivo', 'Consulta + seguimiento', NOW(), NOW()),
(2, 2, '2024-01-15', 1200.00, 100.00, 176.00, 1276.00, 'pagada', 'tarjeta', 'Consulta + plantillas', NOW(), NOW()),
(3, 3, '2024-01-16', 600.00, 0.00, 96.00, 696.00, 'pagada', 'transferencia', 'Seguimiento post-op', NOW(), NOW()),
(4, 4, '2024-01-17', 1500.00, 0.00, 240.00, 1740.00, 'pagada', 'efectivo', 'Consulta + procedimiento programado', NOW(), NOW()),
(5, 5, '2024-01-18', 950.00, 50.00, 144.00, 1044.00, 'pagada', 'tarjeta', 'Consulta + férula', NOW(), NOW()),
(6, 6, '2024-01-19', 800.00, 0.00, 128.00, 928.00, 'pagada', 'efectivo', 'Tratamiento verrugas', NOW(), NOW()),
(7, 7, '2024-01-22', 700.00, 0.00, 112.00, 812.00, 'pagada', 'tarjeta', 'Tratamiento callosidades', NOW(), NOW()),
(8, 8, '2024-01-23', 1100.00, 100.00, 160.00, 1160.00, 'pagada', 'efectivo', 'Consulta + medicamento', NOW(), NOW());

-- Insertar Detalles de Factura
INSERT INTO detalles_factura (factura_id, concepto, cantidad, precio_unitario, subtotal, created_at, updated_at) VALUES
(1, 'Consulta médica especializada', 1, 600.00, 600.00, NOW(), NOW()),
(1, 'Revisión pie diabético', 1, 200.00, 200.00, NOW(), NOW()),
(2, 'Consulta inicial', 1, 600.00, 600.00, NOW(), NOW()),
(2, 'Plantillas Ortopédicas Premium', 1, 450.00, 450.00, NOW(), NOW()),
(2, 'Estudio biomecánico', 1, 250.00, 250.00, NOW(), NOW()),
(3, 'Consulta de seguimiento', 1, 600.00, 600.00, NOW(), NOW()),
(4, 'Consulta inicial', 1, 600.00, 600.00, NOW(), NOW()),
(4, 'Valoración pre-quirúrgica', 1, 400.00, 400.00, NOW(), NOW()),
(4, 'Antibiótico preventivo', 1, 500.00, 500.00, NOW(), NOW()),
(5, 'Consulta médica', 1, 600.00, 600.00, NOW(), NOW()),
(5, 'Férula Nocturna Ajustable', 1, 680.00, 680.00, NOW(), NOW()),
(6, 'Consulta y tratamiento', 1, 600.00, 600.00, NOW(), NOW()),
(6, 'Crioterapia (3 verrugas)', 1, 200.00, 200.00, NOW(), NOW()),
(7, 'Consulta', 1, 600.00, 600.00, NOW(), NOW()),
(7, 'Desbridamiento', 1, 100.00, 100.00, NOW(), NOW()),
(8, 'Consulta especializada', 1, 600.00, 600.00, NOW(), NOW()),
(8, 'Tratamiento antifúngico (3 meses)', 1, 600.00, 600.00, NOW(), NOW());

-- Insertar Pagos
INSERT INTO pagos (factura_id, fecha_pago, monto, metodo_pago, referencia, notas, created_at, updated_at) VALUES
(1, '2024-01-15 10:00:00', 928.00, 'efectivo', NULL, 'Pago completo', NOW(), NOW()),
(2, '2024-01-15 11:30:00', 1276.00, 'tarjeta', 'AUTH-123456', 'Pago completo con tarjeta', NOW(), NOW()),
(3, '2024-01-16 12:00:00', 696.00, 'transferencia', 'TRANS-789012', 'Transferencia bancaria', NOW(), NOW()),
(4, '2024-01-17 15:00:00', 1740.00, 'efectivo', NULL, 'Pago completo en efectivo', NOW(), NOW()),
(5, '2024-01-18 10:30:00', 1044.00, 'tarjeta', 'AUTH-234567', 'Pago con tarjeta débito', NOW(), NOW()),
(6, '2024-01-19 16:00:00', 928.00, 'efectivo', NULL, 'Pago al finalizar consulta', NOW(), NOW()),
(7, '2024-01-22 11:00:00', 812.00, 'tarjeta', 'AUTH-345678', 'Pago con tarjeta crédito', NOW(), NOW()),
(8, '2024-01-23 12:30:00', 1160.00, 'efectivo', NULL, 'Pago completo', NOW(), NOW());

-- Insertar Movimientos de Inventario
INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad, motivo, usuario_id, created_at) VALUES
(1, 'salida', 1, 'Venta a paciente - Factura #2', 3, '2024-01-15 11:30:00'),
(5, 'salida', 1, 'Venta a paciente - Factura #5', 3, '2024-01-18 10:30:00'),
(2, 'entrada', 50, 'Compra a proveedor - Orden #001', 1, '2024-01-10 09:00:00'),
(3, 'entrada', 100, 'Compra a proveedor - Orden #002', 1, '2024-01-10 09:30:00'),
(7, 'salida', 5, 'Uso en tratamientos', 2, '2024-01-20 14:00:00'),
(8, 'salida', 2, 'Venta directa', 3, '2024-01-21 16:00:00');

-- Insertar Gastos
INSERT INTO gastos (categoria, descripcion, monto, fecha_gasto, metodo_pago, proveedor_id, factura_numero, notas, usuario_id, created_at, updated_at) VALUES
('inventario', 'Compra de cremas antifúngicas', 4500.00, '2024-01-10', 'transferencia', 2, 'FACT-2024-001', 'Orden #001 - 50 unidades', 1, NOW(), NOW()),
('inventario', 'Compra de vendajes y suministros', 6800.00, '2024-01-10', 'transferencia', 3, 'FACT-2024-002', 'Orden #002 - Material diverso', 1, NOW(), NOW()),
('servicios', 'Mantenimiento de equipo médico', 1200.00, '2024-01-12', 'efectivo', NULL, NULL, 'Servicio técnico anual', 1, NOW(), NOW()),
('servicios', 'Internet y telefonía - Enero', 800.00, '2024-01-05', 'domiciliacion', NULL, 'SERV-2024-001', 'Pago mensual', 1, NOW(), NOW()),
('administrativo', 'Material de oficina', 450.00, '2024-01-08', 'efectivo', NULL, NULL, 'Papelería y consumibles', 3, NOW(), NOW()),
('servicios', 'Limpieza profesional', 600.00, '2024-01-15', 'efectivo', NULL, NULL, 'Servicio quincenal', 3, NOW(), NOW());

-- Insertar Cortes de Caja
INSERT INTO cortes_caja (fecha_corte, usuario_id, efectivo_inicial, ingresos_efectivo, ingresos_tarjeta, ingresos_transferencia, egresos_efectivo, efectivo_final, efectivo_esperado, diferencia, notas, created_at, updated_at) VALUES
('2024-01-15', 3, 500.00, 1856.00, 1276.00, 0.00, 0.00, 2356.00, 2356.00, 0.00, 'Corte día 15 - Sin diferencias', NOW(), NOW()),
('2024-01-16', 3, 500.00, 0.00, 0.00, 696.00, 0.00, 500.00, 500.00, 0.00, 'Corte día 16 - Solo transferencia', NOW(), NOW()),
('2024-01-17', 3, 500.00, 1740.00, 0.00, 0.00, 0.00, 2240.00, 2240.00, 0.00, 'Corte día 17 - Todo efectivo', NOW(), NOW()),
('2024-01-18', 3, 500.00, 0.00, 1044.00, 0.00, 450.00, 50.00, 50.00, 0.00, 'Corte día 18 - Gasto material oficina', NOW(), NOW()),
('2024-01-19', 3, 500.00, 928.00, 0.00, 0.00, 600.00, 828.00, 828.00, 0.00, 'Corte día 19 - Gasto limpieza', NOW(), NOW()),
('2024-01-22', 3, 500.00, 0.00, 812.00, 0.00, 0.00, 500.00, 500.00, 0.00, 'Corte día 22 - Solo tarjeta', NOW(), NOW()),
('2024-01-23', 3, 500.00, 1160.00, 0.00, 0.00, 0.00, 1660.00, 1660.00, 0.00, 'Corte día 23 - Sin diferencias', NOW(), NOW());

-- Actualizar secuencias al valor correcto después de las inserciones
SELECT setval('facturas_id_seq', (SELECT MAX(id) FROM facturas));
SELECT setval('cortes_caja_id_seq', (SELECT MAX(id) FROM cortes_caja));
SELECT setval('gastos_id_seq', (SELECT MAX(id) FROM gastos));
SELECT setval('movimientos_inventario_id_seq', (SELECT MAX(id) FROM movimientos_inventario));
SELECT setval('productos_id_seq', (SELECT MAX(id) FROM productos));
SELECT setval('proveedores_id_seq', (SELECT MAX(id) FROM proveedores));
SELECT setval('pagos_id_seq', (SELECT MAX(id) FROM pagos));
SELECT setval('diagnosticos_id_seq', (SELECT MAX(id) FROM diagnosticos));
SELECT setval('detalles_factura_id_seq', (SELECT MAX(id) FROM detalles_factura));
SELECT setval('citas_id_seq', (SELECT MAX(id) FROM citas));
SELECT setval('antecedentes_medicos_id_seq', (SELECT MAX(id) FROM antecedentes_medicos));
SELECT setval('alergias_id_seq', (SELECT MAX(id) FROM alergias));
SELECT setval('pacientes_id_seq', (SELECT MAX(id) FROM pacientes));
SELECT setval('usuarios_id_seq', (SELECT MAX(id) FROM usuarios));
SELECT setval('inventario_id_seq', (SELECT MAX(id) FROM inventario));