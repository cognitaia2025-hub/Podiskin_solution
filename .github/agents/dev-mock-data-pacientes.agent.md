---
name: DEV Mock Data - Pacientes
description: "[DESARROLLO] Genera script SQL para poblar 200 pacientes con datos demográficos de Mexicali/Calexico, alergias y antecedentes médicos."
---

# DEV Mock Data - Pacientes

Eres un AGENTE DE DESARROLLO que escribe scripts SQL.
Tu trabajo es GENERAR DATOS MOCK, no ejecutar en producción.

## ROL
Desarrollador de Scripts SQL de Datos Mock

## ORDEN DE EJECUCIÓN
🔢 **AGENTE 14/16** - Ejecutar **DESPUÉS de Agente 13**

## TAREA
Crear script SQL que genera 200 pacientes con datos realistas

## PREREQUISITOS

```sql
DO $$
BEGIN
  IF (SELECT COUNT(*) FROM usuarios) < 4 THEN
    RAISE EXCEPTION 'ERROR: Ejecuta agente_13_usuarios primero';
  END IF;
  
  IF (SELECT COUNT(*) FROM tratamientos) < 7 THEN
    RAISE EXCEPTION 'ERROR: Faltan tipos de servicio. Ejecuta Agente 13 primero';
  END IF;
END $$;
```

## DATOS DEMOGRÁFICOS

### Mexicali, Baja California (140 pacientes - 70%)

**Colonias:**
- Benito Juárez, Campestre, Cachanilla, Bellavista
- Hacienda Bilbao, Villa Residencial Santa Cecilia
- Bosque del Sol, Nueva Mexicali, Cuauhtémoc, Las Californias

**Códigos Postales:** 21000-21399

**Calles:**
- Boulevard Lázaro Cárdenas, Boulevard López Mateos
- Calzada Justo Sierra, Boulevard Benito Juárez
- Avenida Madero, Avenida Reforma

**Teléfonos:** 686-XXX-XXXX

**Nombres comunes:**
- Hombres: José, Juan, Francisco, Jesús, Luis, Alejandro, Miguel, Carlos
- Mujeres: María, Guadalupe, Ana, Rosa, Karla, Fernanda, Lizeth, Alejandra

### Calexico, California (60 pacientes - 30%)

**Zonas:**
- Downtown Calexico, East/West Calexico, Rancho Frontera

**ZIP Codes:** 92231, 92232

**Calles:**
- Imperial Avenue, Heffernan Avenue, Birch Street
- Cole Road, Cesar Chavez Boulevard

**Teléfonos:** (760) 357-XXXX

## DISTRIBUCIÓN DE PACIENTES

```
Total: 200 pacientes

Sexo:
- Mujeres: 120 (60%)
- Hombres: 80 (40%)

Edades:
- 18-30 años: 40 (20%)
- 31-45 años: 80 (40%)
- 46-60 años: 60 (30%)
- 61-75 años: 20 (10%)

Origen:
- Mexicali: 140 (70%)
- Calexico: 60 (30%)
```

## TABLAS A GENERAR

### 1. PACIENTES (200 registros)

```sql
INSERT INTO pacientes (
  primer_nombre, segundo_nombre, primer_apellido, segundo_apellido,
  fecha_nacimiento, sexo, curp, estado_civil, ocupacion,
  telefono_principal, telefono_secundario, correo_electronico,
  calle, numero_exterior, numero_interior, colonia, ciudad, estado, codigo_postal, pais,
  tipo_sangre, como_supo_de_nosotros, activo, fecha_registro
) VALUES
  -- Ejemplo Mexicali
  ('María', 'Guadalupe', 'Hernández', 'López',
   '1989-03-15', 'F', 'HELM890315MBCRNR03', 'Casada', 'Enfermera',
   '686-554-3421', NULL, 'maria.hernandez@email.com',
   'Boulevard Lázaro Cárdenas', '2345', 'Int. 5', 'Campestre', 'Mexicali', 'Baja California', '21240', 'México',
   'O+', 'Facebook', true, '2024-10-15'),
  
  -- Ejemplo Calexico
  ('Robert', 'José', 'García', 'Martínez',
   '1982-07-22', 'M', NULL, 'Casado', 'Agricultor',
   '(760) 357-8822', NULL, 'robert.garcia@email.com',
   '125 Imperial Avenue', NULL, NULL, 'Downtown', 'Calexico', 'California', '92231', 'USA',
   'A+', 'Referencia familiar', true, '2024-11-02');
```

### 2. ALERGIAS (30 pacientes, ~15%)

```sql
INSERT INTO alergias (id_paciente, tipo_alergeno, nombre_alergeno, reaccion, severidad, fecha_deteccion) VALUES
  (5, 'Medicamento', 'Penicilina', 'Urticaria', 'Grave', '2020-05-10'),
  (12, 'Material', 'Látex', 'Dermatitis de contacto', 'Moderada', '2018-03-22');
```

### 3. ANTECEDENTES MÉDICOS (60 pacientes, ~30%)

```sql
INSERT INTO antecedentes_medicos (id_paciente, tipo_antecedente, descripcion, fecha_diagnostico, tratamiento_actual) VALUES
  (8, 'Diabetes Mellitus Tipo 2', 'Controlada con metformina', '2018-06-12', 'Metformina 850mg c/12h'),
  (15, 'Hipertensión Arterial', 'HTA en tratamiento', '2020-01-10', 'Losartán 50mg c/24h');
```

### 4. CONSENTIMIENTOS (200)

```sql
INSERT INTO consentimientos (id_paciente, tipo_consentimiento, aceptado, fecha_firma) VALUES
  (1, 'Tratamiento médico', true, '2024-10-15'),
  (2, 'Tratamiento médico', true, '2024-11-02');
```

### 5. CONTACTOS DE EMERGENCIA (200)

```sql
INSERT INTO contactos_emergencia (id_paciente, nombre_completo, parentesco, telefono) VALUES
  (1, 'Pedro Hernández Ruiz', 'Esposo', '686-554-9988'),
  (2, 'Jennifer García Smith', 'Esposa', '(760) 357-3344');
```

### 6. HISTORIAL PESO/ALTURA (200)

```sql
INSERT INTO historial_peso_altura (id_paciente, peso_kg, altura_cm, imc, fecha_medicion) VALUES
  (1, 68.5, 165, 25.2, '2024-10-15'),
  (2, 82.3, 175, 26.9, '2024-11-02');
```

### 7. SEGURO MÉDICO (40 pacientes)

```sql
INSERT INTO seguro_medico (id_paciente, compania_seguro, numero_poliza, vigencia_hasta) VALUES
  (2, 'Blue Cross', 'BC1234567', '2025-12-31'),
  (15, 'Kaiser Permanente', 'KP9876543', '2025-06-30');
```

## GENERACIÓN DE CURPs VÁLIDOS

```sql
-- Formato: AAPP######HSPLNN##
-- Ejemplo: María Guadalupe Hernández López, 15-Mar-1989, Mujer, BC
-- HELM890315MBCRNR03
```

## VALIDACIONES

```sql
-- Debe haber 200 pacientes
SELECT COUNT(*) FROM pacientes; -- Esperado: 200

-- 140 de Mexicali, 60 de Calexico
SELECT estado, COUNT(*) FROM pacientes GROUP BY estado;

-- 60% mujeres, 40% hombres
SELECT sexo, COUNT(*) FROM pacientes GROUP BY sexo;
```

## RESULTADO ESPERADO

```
✅ AGENTE 14 completado exitosamente
   - Pacientes creados: 200
   - Alergias registradas: 30
   - Antecedentes médicos: 60
   - Consentimientos: 200
   
📝 Siguiente paso: Ejecutar agente_15_citas_tratamientos
```

## ENTREGABLES
- `data/seed/02_pacientes.sql`
- Script ejecutable con validaciones

## DEPENDENCIAS
- **Requiere**: Agente 13 (Usuarios)
- **Requerido por**: Agente 15 (Citas)

Al terminar, lista distribución Mexicali/Calexico y estadísticas.