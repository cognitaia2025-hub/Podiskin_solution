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

### 2. `02_pacientes.sql` (AGENTE 14/16)
**Estado:** Pendiente  
**Descripción:** Datos mock de pacientes y sus historiales clínicos

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

**Última actualización:** 2026-01-01  
**Mantenedor:** Equipo de Desarrollo Podoskin
