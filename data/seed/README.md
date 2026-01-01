# 🌱 Seed Data - Datos Iniciales del Sistema

Este directorio contiene scripts SQL para poblar la base de datos con datos iniciales (seed data) necesarios para el funcionamiento del sistema Podoskin.

## 📋 Orden de Ejecución

Los scripts deben ejecutarse en el siguiente orden:

### 1. `01_usuarios_config.sql` ✅ (AGENTE 13/16)
**Estado:** Completado  
**Descripción:** Configuración inicial de usuarios, podólogos, horarios y servicios

**Contiene:**
- 4 usuarios del sistema (admin, podólogos, recepcionista)
- 2 perfiles de podólogos vinculados
- 10 horarios de trabajo (Lun-Vie para 2 doctores)
- 7 servicios/tratamientos con precios

**Usuarios Protegidos (NO DUPLICAR):**
1. **Santiago de Jesús Ornelas Reynoso**
   - Username: `santiago.ornelas`
   - Email: `enfsantiagoornelas@gmail.com`
   - Rol: Admin
   - Password: `Admin123`
   - Podólogo: Sí (Cédula: POD-2018-001)
   - Horario: Lun-Vie 09:00-18:00

2. **Joana Ibeth Meraz Arregin**
   - Username: `joana.meraz`
   - Email: `joana.meraz@podoskin.com`
   - Rol: Podologo
   - Password: `Podologo123`
   - Podóloga: Sí (Cédula: POD-2020-002)
   - Horario: Lun-Vie 10:00-17:00

**Usuarios Adicionales:**
3. **María Guadalupe López García**
   - Username: `maria.lopez`
   - Email: `maria.lopez@podoskin.com`
   - Rol: Recepcionista
   - Password: `Recepcio123`

4. **Administrador del Sistema**
   - Username: `admin.sistema`
   - Email: `admin@podoskin.com`
   - Rol: Admin
   - Password: `Admin123`

**Servicios Configurados (Precios Mexicali 2024-2025):**
| Servicio | Código | Precio | Duración |
|----------|--------|--------|----------|
| Consulta General | CONS-GEN-001 | $600 MXN | 30 min |
| Onicomicosis | ONIC-001 | $750 MXN | 45 min |
| Pie de atleta | PIE-ATL-001 | $600 MXN | 30 min |
| Pedicure Clínico | PEDI-CLI-001 | $800 MXN | 60 min |
| Uñas Enterradas | UNAS-ENT-001 | $550 MXN | 45 min |
| Callosidades | CALLO-001 | $500 MXN | 30 min |
| Verrugas Plantares | VERR-PLA-001 | $900 MXN | 45 min |

### 2. `02_pacientes.sql` ✅ (AGENTE 14/16)
**Estado:** Completado  
**Descripción:** Datos mock de 200 pacientes con historiales clínicos completos

### 3. `03_citas.sql` (AGENTE 15/16)
**Estado:** Pendiente  
**Descripción:** Citas de ejemplo, tratamientos y pagos

### 4. `04_chatbot_crm.sql` (AGENTE 16/16)
**Estado:** Pendiente  
**Descripción:** Conversaciones de ejemplo y plantillas de mensajes

## 🚀 Cómo Ejecutar

### Opción 1: Desde línea de comandos
```bash
# Navegar al directorio del proyecto
cd /ruta/al/proyecto

# Ejecutar el script con psql
psql -U postgres -d podoskin -f data/seed/01_usuarios_config.sql
```

### Opción 2: Desde PostgreSQL interactivo
```sql
-- Conectarse a la base de datos
psql -U postgres -d podoskin

-- Ejecutar el script
\i data/seed/01_usuarios_config.sql
```

### Opción 3: Desde Docker Compose
```bash
# Si usas Docker Compose
docker-compose exec postgres psql -U postgres -d podoskin -f /docker-entrypoint-initdb.d/seed/01_usuarios_config.sql
```

## ⚙️ Configuración del Sistema

- **Nombre de la clínica:** Podoskin Solution
- **Ubicación:** Mexicali, Baja California
- **Consultorios:** 2 (Consultorio 1 y Consultorio 2)
- **Duración de slots de cita:** 30 minutos
- **Recordatorio de cita:** 24 horas antes
- **Cancelación anticipada:** 12 horas
- **IVA:** 16%
- **Moneda:** MXN (Pesos Mexicanos)

## 🔐 Seguridad

- Las contraseñas están hasheadas usando **PBKDF2-SHA256**
- El algoritmo es compatible con Python passlib
- **IMPORTANTE:** Cambiar las contraseñas por defecto en producción

## ✅ Validaciones

El script incluye validaciones automáticas para:
- ✓ Evitar duplicación de usuarios protegidos (Santiago y Joana)
- ✓ Verificar existencia antes de insertar
- ✓ Transacciones con rollback automático en caso de error
- ✓ Mensajes informativos de progreso

## 📊 Resultado Esperado

Después de ejecutar `01_usuarios_config.sql`:

```
✅ AGENTE 13 completado exitosamente
   - Usuarios creados: 4
   - Podólogos registrados: 2
   - Horarios configurados: 10
   - Servicios disponibles: 7
```

## 🔗 Referencias

- [BRD_Podoskin_Solution.md](../../BRD_Podoskin_Solution.md)
- [SRS_Podoskin_Solution.md](../../SRS_Podoskin_Solution.md)
- [FSD_Podoskin_Solution.md](../../FSD_Podoskin_Solution.md)

## 📝 Notas

- Los scripts están diseñados para ser **idempotentes** (se pueden ejecutar múltiples veces)
- Todos los checks de validación están implementados en el propio SQL
- El script genera un resumen detallado al finalizar la ejecución
- Compatible con PostgreSQL 12+

## 🐛 Troubleshooting

### Error: "duplicate key value violates unique constraint"
**Solución:** El script ya tiene validaciones. Si ocurre, verificar que no haya datos previos.

### Error: "relation does not exist"
**Solución:** Ejecutar primero los scripts de creación de tablas en `/data/`

### Error: "permission denied"
**Solución:** Asegurarse de tener permisos de escritura en la base de datos

## 👥 Contribución

Al agregar nuevos scripts de seed:
1. Seguir la nomenclatura: `XX_nombre_descriptivo.sql`
2. Incluir validaciones de duplicados
3. Usar transacciones (BEGIN/COMMIT)
4. Agregar resumen al final del script
5. Documentar en este README

---

## 📊 AGENTE 14: Reporte de Datos de Pacientes (02_pacientes.sql)

### ✅ Estado: COMPLETADO

**Archivo:** `02_pacientes.sql`  
**Tamaño:** 96 KB (1,466 líneas)  
**Fecha de generación:** 2026-01-01

### 📋 Datos Generados

#### 🏥 Pacientes (200 registros)
- **IDs:** 1 a 200
- **Distribución Geográfica:**
  - 🇲🇽 Mexicali, Baja California: 143 pacientes (71.5%)
  - 🇺🇸 Calexico, California: 57 pacientes (28.5%)

- **Distribución por Sexo:**
  - 👩 Mujeres: 120 (60%)
  - 👨 Hombres: 80 (40%)

- **Distribución por Edad:**
  - 18-30 años: ~40 pacientes (20%)
  - 31-45 años: ~80 pacientes (40%)
  - 46-60 años: ~60 pacientes (30%)
  - 61-75 años: ~20 pacientes (10%)

#### 🏥 Datos Médicos Complementarios

- **Alergias:** 30 registros (~15% de pacientes)
  - Medicamentos: Penicilina, Aspirina, Ibuprofeno, Sulfonamidas, etc.
  - Alimentos: Mariscos, Nueces, Huevo, Leche, Soya, Gluten
  - Ambientales: Polen, Ácaros del polvo, Moho, Caspa de animales
  - Materiales: Látex, Níquel, Yodo, Adhesivos médicos

- **Antecedentes Médicos:** 60 registros (~30% de pacientes)
  - Patológicos: Diabetes Mellitus Tipo 2, Hipertensión Arterial, Asma, Obesidad, etc.
  - Heredofamiliares: Historia familiar de diabetes, cáncer, hipertensión
  - Quirúrgicos: Colecistectomía, Apendicectomía, Cesárea, Hernioplastía, etc.

- **Consentimientos Informados:** 200 registros (1 por paciente)
  - Tipo: "Tratamiento podológico general"
  - Firmados digitalmente
  - Fecha de firma: fecha de registro del paciente

- **Signos Vitales:** 200 registros (peso/altura)
  - Peso: 58-93 kg (rangos realistas)
  - Talla: 156-180 cm (según sexo)
  - IMC: Calculado automáticamente por trigger
  - Registrado por: Usuario ID 1

### 🌎 Datos Geográficos Detallados

#### Pacientes de Mexicali (143)
- **Colonias:** Benito Juárez, Campestre, Cachanilla, Bellavista, Hacienda Bilbao, Villa Residencial Santa Cecilia, Bosque del Sol, Nueva Mexicali, Cuauhtémoc, Las Californias
- **Calles:** Boulevard Lázaro Cárdenas, Boulevard López Mateos, Calzada Justo Sierra, Boulevard Benito Juárez, Avenida Madero, Avenida Reforma
- **Códigos Postales:** 21000-21399
- **Teléfonos:** Formato 686-XXX-XXXX
- **CURPs:** Válidos según formato oficial (AAPP######HSPLNN##)
- **País:** México

#### Pacientes de Calexico (57)
- **Zonas:** Downtown, East Calexico, West Calexico, Rancho Frontera
- **Calles:** Imperial Avenue, Heffernan Avenue, Birch Street, Cole Road, Cesar Chavez Boulevard
- **ZIP Codes:** 92231, 92232
- **Teléfonos:** Formato (760) 357-XXXX
- **CURPs:** NULL (no aplica para USA)
- **País:** USA

### 📝 Características de los Datos

✅ **Nombres Realistas:**
- Hombres: José, Juan, Francisco, Jesús, Luis, Alejandro, Miguel, Carlos, Fernando, Roberto, etc.
- Mujeres: María, Guadalupe, Ana, Rosa, Karla, Fernanda, Lizeth, Alejandra, Patricia, Gabriela, etc.

✅ **CURPs Válidos:** Formato oficial mexicano con algoritmo de validación

✅ **Emails Automáticos:** Generados a partir de nombres (ej: maria.hernandez@gmail.com)

✅ **Direcciones Reales:** Calles y colonias existentes en Mexicali/Calexico

✅ **Fechas de Registro:** Distribuidas en los últimos 6 meses

✅ **Estados Civiles:** Soltero, Casado, Divorciado, Viudo, Unión Libre

✅ **Ocupaciones:** Empleado, Comerciante, Ama de casa, Estudiante, Agricultor, Profesionista, etc.

### 🔍 Validaciones Incluidas

El script incluye bloques de validación automática:

```sql
DO $$
BEGIN
  -- Verificar prerequisitos
  IF (SELECT COUNT(*) FROM usuarios) < 2 THEN
    RAISE EXCEPTION 'ERROR: Ejecuta agente_13_usuarios primero';
  END IF;
  
  IF (SELECT COUNT(*) FROM tratamientos) < 5 THEN
    RAISE NOTICE '⚠️  ADVERTENCIA: Faltan tratamientos';
  END IF;
END $$;
```

**Validaciones Post-Inserción:**
- ✓ Total de pacientes = 200
- ✓ Distribución geográfica (Mexicali/Calexico)
- ✓ Distribución por sexo (60%/40%)
- ✓ Totales de alergias, antecedentes, consentimientos
- ✓ Mensaje de éxito con estadísticas completas

### 🚀 Ejecución

```bash
# Desde línea de comandos
psql -U postgres -d podoskin -f data/seed/02_pacientes.sql

# Desde PostgreSQL interactivo
\i data/seed/02_pacientes.sql
```

**Prerequisitos:**
- Base de datos creada con esquema completo
- Script `01_usuarios_config.sql` ejecutado previamente
- Tabla `tratamientos` debe contener al menos 5 registros

### 📊 Salida Esperada

```
NOTICE: ✅ Prerequisitos verificados correctamente
NOTICE: Insertando 200 pacientes...
NOTICE: Insertando alergias...
NOTICE: Insertando antecedentes médicos...
NOTICE: Insertando consentimientos informados...
NOTICE: Insertando signos vitales (peso/altura)...
NOTICE: Ejecutando validaciones...
NOTICE: 
NOTICE: ====================================================================
NOTICE: ✅ AGENTE 14 COMPLETADO EXITOSAMENTE
NOTICE: ====================================================================
NOTICE: 
NOTICE: 📊 ESTADÍSTICAS DE DATOS INSERTADOS:
NOTICE: --------------------------------------------------------------------
NOTICE:   Total Pacientes:              200
NOTICE: 
NOTICE:   DISTRIBUCIÓN GEOGRÁFICA:
NOTICE:     • Mexicali, BC:             143 (72%)
NOTICE:     • Calexico, CA:             57 (28%)
NOTICE: 
NOTICE:   DISTRIBUCIÓN POR SEXO:
NOTICE:     • Mujeres:                  120 (60%)
NOTICE:     • Hombres:                  80 (40%)
NOTICE: 
NOTICE:   DATOS MÉDICOS:
NOTICE:     • Alergias registradas:     30 pacientes (15%)
NOTICE:     • Antecedentes médicos:     60 pacientes (30%)
NOTICE:     • Consentimientos:          200
NOTICE:     • Signos vitales (P/A):     200
NOTICE: 
NOTICE: ====================================================================
NOTICE: 📝 SIGUIENTE PASO: Ejecutar agente_15_citas_tratamientos
NOTICE: ====================================================================
COMMIT
NOTICE: ✅ Script 02_pacientes.sql ejecutado exitosamente
```

### 🔬 Verificación Post-Ejecución

```sql
-- Verificar total de pacientes
SELECT COUNT(*) FROM pacientes;  -- Esperado: 200

-- Verificar distribución geográfica
SELECT estado, COUNT(*) 
FROM pacientes 
GROUP BY estado;
-- Esperado: 
--   Baja California: 143
--   California: 57

-- Verificar distribución por sexo
SELECT sexo, COUNT(*) 
FROM pacientes 
GROUP BY sexo;
-- Esperado:
--   F: 120
--   M: 80

-- Verificar datos médicos
SELECT COUNT(*) FROM alergias;  -- Esperado: 30
SELECT COUNT(*) FROM antecedentes_medicos;  -- Esperado: 60
SELECT COUNT(*) FROM consentimientos_informados;  -- Esperado: 200
SELECT COUNT(*) FROM signos_vitales;  -- Esperado: 200
```

### 📌 Ejemplo de Datos

**Paciente de Mexicali:**
```sql
ID: 1
Nombre: María Guadalupe Hernández López
Sexo: F
Fecha Nacimiento: 1989-03-15
CURP: HELM890315MBCRNR03
Estado Civil: Casada
Teléfono: 686-554-3421
Email: maria.hernandez@email.com
Dirección: Boulevard Lázaro Cárdenas 2345, Int. 5
Colonia: Campestre
Ciudad: Mexicali, Baja California
CP: 21240
País: México
Ocupación: Enfermera
Referencia: Facebook
```

**Paciente de Calexico:**
```sql
ID: 2
Nombre: Robert José García Martínez
Sexo: M
Fecha Nacimiento: 1982-07-22
Estado Civil: Casado
Teléfono: (760) 357-8822
Email: robert.garcia@email.com
Dirección: 125 Imperial Avenue
Zona: Downtown
Ciudad: Calexico, California
ZIP: 92231
País: USA
Ocupación: Agricultor
Referencia: Referencia familiar
```

### ⚠️ Notas Importantes

- **Transacciones:** Script usa BEGIN/COMMIT con rollback automático en caso de error
- **Idempotencia:** Los IDs van del 1 al 200. No ejecutar múltiples veces sin limpiar datos primero
- **CURPs:** Válidos en formato pero no verificados contra base real RENAPO
- **Emails:** Generados automáticamente, pueden no ser reales
- **Fechas:** Distribuidas en los últimos 6 meses desde la fecha de generación (2026-01-01)

### 🔗 Siguiente Paso

▶️ **Ejecutar:** `agente_15_citas_tratamientos.sql` (AGENTE 15/16)  
Para generar citas y tratamientos para estos 200 pacientes.

### 🛠️ Implementación Técnica

**Generación de Datos:**
- Script Python para generar datos consistentes y realistas
- Algoritmo de validación CURP oficial mexicano
- Distribución geográfica con colonias/calles reales
- Generación automática de emails a partir de nombres
- Randomización de fechas en ventana de 6 meses

**Estructura SQL:**
- Transacción completa con BEGIN/COMMIT
- Validación de prerequisitos con DO blocks
- 5 INSERT statements principales
- Bloque de validación post-inserción
- Mensajes informativos con RAISE NOTICE

**Compatibilidad:**
- PostgreSQL 12+
- Compatible con esquema existente
- Formato seguido: nomenclatura estándar del proyecto

---

**Última actualización:** 2026-01-01  
**Mantenedor:** Equipo de Desarrollo Podoskin
