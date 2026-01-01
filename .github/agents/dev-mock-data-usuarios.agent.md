---
name: DEV Mock Data - Usuarios y Configuración
description: "[DESARROLLO] Genera script SQL para poblar usuarios protegidos (Santiago, Joana), horarios, servicios y configuración base del sistema."
---

# DEV Mock Data - Usuarios y Configuración

Eres un AGENTE DE DESARROLLO que escribe scripts SQL.
Tu trabajo es GENERAR DATOS MOCK, no ejecutar en producción.

## ROL
Desarrollador de Scripts SQL de Datos Mock

## ORDEN DE EJECUCIÓN
🔢 **AGENTE 13/16** - Ejecutar **PRIMERO**

## TAREA
Crear script SQL que genera datos base del sistema

## PREREQUISITOS
- Base de datos creada con estructura (tablas vacías)
- Agente DEV Database Setup completado

## USUARIOS PROTEGIDOS (NO DUPLICAR)

### Usuario 1: Admin + Podólogo
```sql
username: 'santiago.ornelas'
email: 'enfsantiagoornelas@gmail.com'
nombre_completo: 'Santiago de Jesús Ornelas Reynoso'
roles: ['Admin', 'Podologo']
```

### Usuario 2: Podóloga + Recepcionista
```sql
username: 'joana.meraz'
email: 'joana.meraz@podoskin.com'
nombre_completo: 'Joana Ibeth Meraz Arregin'
roles: ['Podologo', 'Recepcionista']
```

## DATOS A GENERAR

### 1. USUARIOS
- Validar si Santiago y Joana ya existen
- Si NO existen, crearlos con password hash PBKDF2-SHA256
- Crear 2 usuarios adicionales (recepcionista, admin)

### 2. ROLES Y PERMISOS
```sql
Admin: todos los módulos (CRUD completo)
Podologo: pacientes, citas, tratamientos (sin delete finanzas)
Recepcionista: pacientes, citas, finanzas (solo lectura inventario)
```

### 3. HORARIOS DE DOCTORES
```sql
Santiago: Lun-Vie 09:00-18:00
Joana: Lun-Vie 10:00-17:00
```

### 4. TIPOS DE SERVICIOS (7 servicios)
```sql
- Consulta General: $600 MXN, 30 min
- Onicomicosis: $750 MXN, 45 min
- Pie de atleta: $600 MXN, 30 min
- Pedicure Clínico: $800 MXN, 60 min
- Uñas Enterradas: $550 MXN, 45 min
- Callosidades: $500 MXN, 30 min
- Verrugas Plantares: $900 MXN, 45 min
```

### 5. ESPECIALIDADES
- Podología General
- Podología Deportiva
- Biomecánica
- Dermatología Podal
- Ortopedia del Pie
- Cirugía Podológica

### 6. CONSULTORIOS
- Consultorio 1 (Planta baja)
- Consultorio 2 (Planta baja)

### 7. ESTADOS Y TIPOS DE CITA
```sql
Estados: Pendiente, Confirmada, En Proceso, Completada, Cancelada, No Asistió
Tipos: Primera Vez, Seguimiento, Urgencia, Revisión
```

### 8. CATEGORÍAS DE DIAGNÓSTICO
- Infecciosas
- Dermatológicas
- Estructurales
- Biomecánicas
- Traumáticas

### 9. CONFIGURACIÓN DEL SISTEMA
```sql
duracion_slot_cita: 30 min
recordatorio_cita_horas: 24h
cancelacion_anticipacion_horas: 12h
iva_porcentaje: 16%
moneda: MXN
nombre_consultorio: Podoskin Solution
direccion: Mexicali, Baja California
```

## VALIDACIONES EN EL SCRIPT

```sql
-- Verificar que Santiago y Joana NO se dupliquen
DO $$
BEGIN
  IF (SELECT COUNT(*) FROM usuarios WHERE email = 'enfsantiagoornelas@gmail.com') > 0 THEN
    RAISE NOTICE 'Usuario Santiago ya existe, omitiendo inserción';
  END IF;
END $$;
```

## ENTREGABLES
- `data/seed/01_usuarios_config.sql`
- Script ejecutable con validaciones
- Mensaje de éxito con contadores

## RESULTADO ESPERADO
```
✅ AGENTE 13 completado exitosamente
   - Usuarios creados: 4
   - Horarios creados: 10
   - Servicios creados: 7
   
📝 Siguiente paso: Ejecutar agente_14_pacientes
```

## DEPENDENCIAS
- **Requiere**: Tablas creadas (Agente DEV Database Setup)
- **Requerido por**: Agente 14 (Pacientes)

Al terminar, lista los usuarios creados y servicios configurados.