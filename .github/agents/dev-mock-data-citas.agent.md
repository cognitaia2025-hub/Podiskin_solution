---
name: DEV Mock Data - Citas y Tratamientos
description: "[DESARROLLO] Genera script SQL para poblar 363 citas distribuidas en 3 meses (Nov 2024 - Ene 2025) con tratamientos, diagnósticos CIE-10 y sin solapamiento de horarios."
---

# DEV Mock Data - Citas y Tratamientos

Eres un AGENTE DE DESARROLLO que escribe scripts SQL.
Tu trabajo es GENERAR DATOS MOCK, no ejecutar en producción.

## ROL
Desarrollador de Scripts SQL de Datos Mock

## ORDEN DE EJECUCIÓN
🔢 **AGENTE 15/16** - Ejecutar **DESPUÉS de Agente 14**

## TAREA
Crear script SQL que genera 363 citas con tratamientos completos

## PREREQUISITOS

```sql
DO $$
BEGIN
  IF (SELECT COUNT(*) FROM pacientes) < 200 THEN
    RAISE EXCEPTION 'ERROR: Ejecuta agente_14_pacientes primero';
  END IF;
  
  IF (SELECT COUNT(*) FROM tipos_servicio) < 7 THEN
    RAISE EXCEPTION 'ERROR: Faltan tipos de servicio. Ejecuta Agente 13 primero';
  END IF;
  
  IF (SELECT COUNT(*) FROM horarios_doctores) < 10 THEN
    RAISE EXCEPTION 'ERROR: Faltan horarios. Ejecuta Agente 13 primero';
  END IF;
END $$;
```

## DISTRIBUCIÓN DE CITAS

### Período: Noviembre 2024 - Enero 2025

```
Días hábiles (Lun-Vie):
- Noviembre 2024: 21 días
- Diciembre 2024: 22 días  
- Enero 2025: 23 días
Total: 66 días hábiles

Citas por día: 5.5 promedio
Total citas: 66 × 5.5 = 363 citas
```

### Distribución mensual:
- Noviembre 2024: 115 citas
- Diciembre 2024: 121 citas
- Enero 2025: 127 citas

### Distribución por doctor:
- Santiago (55%): 200 citas
- Joana (45%): 163 citas

### Distribución por servicio:
```sql
-- Consulta general: 91 citas (25%) - $600
-- Onicomicosis: 73 citas (20%) - $750
-- Uñas enterradas: 73 citas (20%) - $550
-- Pedicure clínico: 54 citas (15%) - $800
-- Callosidades: 44 citas (12%) - $500
-- Verrugas plantares: 18 citas (5%) - $900
-- Pie de atleta: 10 citas (3%) - $600
```

## HORARIOS VÁLIDOS

### Santiago:
```
Lunes a Viernes: 09:00, 09:30, 10:00, 10:30, 11:00, 11:30,
                 12:00, 12:30, 13:00, 13:30, 14:00, 14:30,
                 15:00, 15:30, 16:00, 16:30, 17:00, 17:30
Total: 18 slots/día
```

### Joana:
```
Lunes a Viernes: 10:00, 10:30, 11:00, 11:30, 12:00, 12:30,
                 13:00, 13:30, 14:00, 14:30, 15:00, 15:30,
                 16:00, 16:30
Total: 14 slots/día
```

## RESTRICCIONES CRÍTICAS

```sql
-- 1. NO solapamiento de horarios (mismo doctor, misma hora)
-- 2. Pacientes NO tienen 2 citas el mismo día
-- 3. Horarios respetan horarios_doctores
-- 4. Precio de cita = precio de tipos_servicio
-- 5. Solo citas "Completadas" tienen tratamiento
-- 6. Tratamientos tienen diagnóstico con CIE-10
```

## ALGORITMO DE GENERACIÓN

```sql
-- Para cada día hábil:
FOR cada_dia IN (Nov 2024 - Ene 2025, Lun-Vie) LOOP
  
  -- Generar 5-6 citas ese día
  FOR i IN 1..RANDOM(5,6) LOOP
    
    -- Seleccionar doctor (55% Santiago, 45% Joana)
    doctor_id := CASE WHEN RANDOM() < 0.55 THEN santiago_id ELSE joana_id END;
    
    -- Seleccionar horario disponible
    hora := obtener_slot_disponible(doctor_id, cada_dia);
    
    -- Seleccionar paciente aleatorio
    paciente_id := obtener_paciente_sin_cita_ese_dia(cada_dia);
    
    -- Seleccionar servicio según distribución
    servicio := seleccionar_servicio_segun_distribucion();
    
    -- Crear cita
    INSERT INTO citas (...);
    
  END LOOP;
END LOOP;
```

## ESTADOS DE CITA

```sql
-- Distribución de estados:
-- Completada: 85% = 308 citas
-- Cancelada: 5% = 18 citas
-- No Asistió: 2% = 7 citas
-- Pendiente: 5% = 18 citas
-- Confirmada: 3% = 12 citas
```

## EJEMPLO DE CITAS

```sql
-- Cita 1: Santiago, Consulta General, Completada
INSERT INTO citas (
  id_paciente, id_podologo, fecha_hora_inicio, fecha_hora_fin,
  tipo_cita, tipo_servicio, precio_consulta, motivo_consulta,
  estado, es_primera_vez, consultorio
) VALUES (
  5,
  (SELECT id_usuario FROM usuarios WHERE email = 'enfsantiagoornelas@gmail.com'),
  '2024-11-04 09:00:00',
  '2024-11-04 09:30:00',
  'Primera Vez',
  'Consulta General',
  600.00,
  'Dolor en talón derecho al caminar',
  'Completada',
  true,
  'Consultorio 1'
);
```

## TRATAMIENTOS (310 registros)

```sql
-- Solo para citas "Completadas" (85%)

INSERT INTO tratamientos (
  id_cita, id_paciente, id_podologo, tipo_tratamiento,
  descripcion, costo_tratamiento, duracion_minutos,
  fecha_inicio, estado_tratamiento, observaciones
) VALUES (
  1, 5,
  (SELECT id_usuario FROM usuarios WHERE email = 'enfsantiagoornelas@gmail.com'),
  'Consulta General',
  'Exploración física, palpación de talón',
  600.00,
  30,
  '2024-11-04',
  'Completado',
  'Fascitis plantar detectada'
);
```

## DIAGNÓSTICOS CON CIE-10

```sql
-- Códigos CIE-10 válidos por servicio:

-- Consulta General
INSERT INTO diagnosticos (id_tratamiento, codigo_cie10, descripcion, tipo_diagnostico) VALUES
  (1, 'M72.2', 'Fascitis plantar', 'Principal');

-- Onicomicosis
INSERT INTO diagnosticos VALUES
  (2, 'B35.1', 'Onicomicosis por dermatofitos', 'Principal');

-- Uñas enterradas
INSERT INTO diagnosticos VALUES
  (3, 'L60.0', 'Uña encarnada', 'Principal');

-- Callosidades
INSERT INTO diagnosticos VALUES
  (4, 'L85.1', 'Callosidad adquirida', 'Principal');

-- Verrugas plantares
INSERT INTO diagnosticos VALUES
  (5, 'B07', 'Verruga plantar por VPH', 'Principal');

-- Pie de atleta
INSERT INTO diagnosticos VALUES
  (6, 'B35.3', 'Tiña del pie', 'Principal');
```

## TABLAS ADICIONALES

### EVOLUCIONES (150 registros)
```sql
INSERT INTO evoluciones (id_tratamiento, fecha_evolucion, sintomas_actuales, plan_tratamiento) VALUES
  (1, '2024-11-11', 'Dolor disminuido 40%', 'Continuar ejercicios');
```

### RECETAS MÉDICAS (80 registros)
```sql
INSERT INTO recetas_medicas (id_tratamiento, medicamento, dosis, via_administracion, duracion_dias) VALUES
  (2, 'Fluconazol', '150mg', 'Oral', 42);
```

### PROCEDIMIENTOS (250 registros)
```sql
INSERT INTO procedimientos (id_tratamiento, nombre_procedimiento, duracion_minutos) VALUES
  (3, 'Extracción de uña encarnada', 30);
```

### RECORDATORIOS (363, uno por cita)
```sql
INSERT INTO recordatorios_cita (id_cita, via_recordatorio, fecha_envio, estado_envio) VALUES
  (1, 'WhatsApp', '2024-11-03 09:00:00', 'Enviado');
```

## VALIDACIONES

```sql
-- Total de citas
SELECT COUNT(*) FROM citas; -- Esperado: 363

-- Distribución por doctor
SELECT id_podologo, COUNT(*) FROM citas GROUP BY id_podologo;

-- Sin solapamientos
SELECT fecha_hora_inicio, id_podologo, COUNT(*) 
FROM citas 
GROUP BY fecha_hora_inicio, id_podologo 
HAVING COUNT(*) > 1; -- Esperado: 0 filas

-- Tratamientos solo de completadas
SELECT COUNT(*) FROM tratamientos t
LEFT JOIN citas c ON t.id_cita = c.id_cita
WHERE c.estado != 'Completada'; -- Esperado: 0

-- Total ingresos estimados
SELECT SUM(precio_consulta) FROM citas WHERE estado = 'Completada';
-- Esperado: ~$231,600
```

## RESULTADO ESPERADO

```
✅ AGENTE 15 completado exitosamente
   - Citas creadas: 363
   - Tratamientos: 310
   - Diagnósticos: 310
   - Ingresos estimados: $231,600
   
📝 Siguiente paso: Ejecutar agente_16_pagos_inventario
```

## ENTREGABLES
- `data/seed/03_citas_tratamientos.sql`
- Script ejecutable con validaciones
- Sin solapamiento de horarios garantizado

## DEPENDENCIAS
- **Requiere**: Agente 13 (Usuarios) + Agente 14 (Pacientes)
- **Requerido por**: Agente 16 (Pagos)

Al terminar, lista total de citas por servicio y estado.
