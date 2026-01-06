# Errores y Funcionalidades Pendientes - Backend

==========================================

## TODOs y Funcionalidades Pendientes [04/01/26] [17:43]

==========================================

### Funcionalidades Pendientes de Implementación

**1. api/live_sessions.py - Sistema de sesiones**

- **L36**: Reemplazar almacenamiento en memoria por Redis para producción
  - Impacto: Escalabilidad horizontal y persistencia
  
- **L194**: Verificar permisos de usuario para acceso a pacientes
  - Impacto: Seguridad - validar que el usuario tenga permiso para ver datos del paciente
  
- **L473-484**: Implementar llamadas a endpoints REST reales
  - L487: POST /api/patients/{patient_id}/vital-signs
  - L498: POST /api/appointments/{appointment_id}/clinical-note
  - L509: GET /api/patients/{patient_id}
  - L520: POST /api/patients/{patient_id}/allergies
  - Impacto: Actualmente usa respuestas mock (simuladas)

**2. stats/router.py - Estadísticas**

- **L197**: Implementar top_treatments cuando exista tabla tratamientos
  - Impacto: Dashboard incompleto, falta métrica de tratamientos más usados
  
- **L198**: Calcular ocupacion_porcentaje basado en horarios
  - Impacto: Falta métrica de utilización de agenda

**3. podologos/service.py - Disponibilidad**

- **L333-334**: Integrar con calendario de citas para disponibilidad real
  - Impacto: Actualmente solo devuelve podólogos activos, no verifica agenda real

**4. medical_records/router.py - Expedientes**

- **L291**: Implementar actualización por sección específica
  - Impacto: Actualización de expedientes no está completamente modularizada

### Validaciones y Mejoras de Seguridad

**5. auth/authorization.py - Control de acceso**

- **L105**: Decorator para requerir cualquier rol de staff
  - Estado: Implementado pero podría mejorarse con logging

**6. Configuración de CORS en producción**

- **citas/app_example.py L75**: allow_origins=["*"]
- **tratamientos/app_example.py L46**: allow_origins=["*"]
  - Impacto: Inseguro para producción, debe especificar dominios permitidos

### Funcionalidades Parcialmente Implementadas

**7. Sistema de rate limiting**

- **auth/router.py L33-71**: Rate limiting en memoria
  - Recomendación: Usar Redis para producción

**8. Blacklist de tokens JWT**

- **auth/router.py L204-227**: Logout no invalida tokens
  - Impacto: Tokens siguen válidos hasta expiración natural
  - Recomendación: Implementar blacklist en Redis

### Resumen de Prioridades

**Alta Prioridad (Seguridad):**

1. Implementar verificación de permisos de usuario (live_sessions.py L194)
2. Configurar CORS correctamente para producción
3. Implementar blacklist de tokens JWT

**Media Prioridad (Funcionalidad):**

1. Conectar funciones de Gemini Live con endpoints REST reales (L473-520)
2. Implementar estadísticas completas (top_treatments, ocupación)
3. Integrar disponibilidad real de podólogos con calendario

**Baja Prioridad (Optimización):**

1. Migrar sesiones y rate limiting a Redis
2. Modularizar actualización de expedientes por sección

### Resumen para Santiago

Se encontraron varias funcionalidades que están marcadas como "pendientes" en el código:

**Lo que necesita atención:**

1. **Seguridad mejorada**: Algunas validaciones de permisos están pendientes. Esto significa que aunque el sistema funciona, se puede hacer más seguro verificando que cada usuario solo vea la información que le corresponde.

2. **Estadísticas completas**: El dashboard muestra información básica, pero faltan algunas métricas como "tratamientos más usados" y "porcentaje de ocupación de la agenda". Estas se pueden agregar más adelante.

3. **Integración de voz**: El sistema de dictado por voz (Gemini Live) está funcionando con datos de prueba. Para que funcione completamente, necesita conectarse con los endpoints reales de la base de datos.

**Impacto en tu experiencia:**

- **Ahora**: La aplicación funciona correctamente para el uso diario
- **Futuro**: Estas mejoras harán el sistema más robusto, seguro y completo
- **Urgencia**: Ninguna es crítica, el sistema es usable tal como está

Piensa en estos TODOs como "mejoras futuras" que harán la aplicación aún mejor, pero no impiden que la uses ahora mismo.

---
