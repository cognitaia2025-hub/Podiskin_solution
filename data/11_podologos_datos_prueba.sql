-- Insertar datos de prueba para podólogos
-- Solo inserta si hay menos de 3 podólogos en la tabla

INSERT INTO podologos (cedula_profesional, nombre_completo, especialidad, telefono, email, activo, fecha_contratacion)
SELECT 
    cedula_profesional, 
    nombre_completo, 
    especialidad, 
    telefono, 
    email, 
    activo, 
    fecha_contratacion::date
FROM (VALUES
    ('CED-123456', 'Dr. Alejandro Martínez', 'Podología Deportiva', '555-0101', 'alejandro.martinez@podoskin.com', true, '2020-01-15'),
    ('CED-789012', 'Dra. Isabel Rodríguez', 'Podología Geriátrica', '555-0102', 'isabel.rodriguez@podoskin.com', true, '2019-06-20'),
    ('CED-345678', 'Dr. Carlos Hernández', 'Podología Pediátrica', '555-0103', 'carlos.hernandez@podoskin.com', true, '2021-03-10'),
    ('CED-901234', 'Dra. Ana García', 'Biomecánica del Pie', '555-0104', 'ana.garcia@podoskin.com', true, '2018-09-05'),
    ('CED-567890', 'Dr. Roberto Sánchez', 'Cirugía Podológica', '555-0105', 'roberto.sanchez@podoskin.com', true, '2022-01-20')
) AS v(cedula_profesional, nombre_completo, especialidad, telefono, email, activo, fecha_contratacion)
WHERE (SELECT COUNT(*) FROM podologos) < 3;

-- Verificar datos insertados
SELECT id, nombre_completo, especialidad, activo FROM podologos ORDER BY id;
