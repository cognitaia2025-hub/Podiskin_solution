# 🎙️ Function Declarations para Gemini Live - Podoskin

Este documento define las funciones que el asistente de IA puede llamar durante una consulta médica.

## 📋 Funciones Principales

### 1. `update_vital_signs` - Actualizar Signos Vitales

```typescript
{
  name: 'update_vital_signs',
  description: 'Actualiza los signos vitales del paciente durante la consulta (peso, talla, presión arterial, etc.)',
  parameters: {
    type: Type.OBJECT,
    properties: {
      peso_kg: {
        type: Type.NUMBER,
        description: 'Peso del paciente en kilogramos (ej: 75.5)'
      },
      talla_cm: {
        type: Type.NUMBER,
        description: 'Talla del paciente en centímetros (ej: 170)'
      },
      ta_sistolica: {
        type: Type.INTEGER,
        description: 'Presión arterial sistólica en mmHg (ej: 120)'
      },
      ta_diastolica: {
        type: Type.INTEGER,
        description: 'Presión arterial diastólica en mmHg (ej: 80)'
      },
      frecuencia_cardiaca: {
        type: Type.INTEGER,
        description: 'Frecuencia cardíaca en latidos por minuto'
      },
      temperatura_c: {
        type: Type.NUMBER,
        description: 'Temperatura corporal en grados Celsius (ej: 36.5)'
      },
      saturacion_o2: {
        type: Type.INTEGER,
        description: 'Saturación de oxígeno en porcentaje (ej: 98)'
      },
      glucosa_capilar: {
        type: Type.INTEGER,
        description: 'Glucosa capilar en mg/dL'
      }
    },
    required: []
  }
}
```

**Ejemplo de uso:**

- Usuario: "El peso es 75 kilos y medio"
- IA: *Llama a `update_vital_signs({peso_kg: 75.5})`*
- IA: "Perfecto, he registrado el peso de 75.5 kilogramos"

---

### 2. `create_clinical_note` - Crear/Actualizar Nota Clínica

```typescript
{
  name: 'create_clinical_note',
  description: 'Crea o actualiza la nota clínica de la consulta actual',
  parameters: {
    type: Type.OBJECT,
    properties: {
      motivo_consulta: {
        type: Type.STRING,
        description: 'Motivo principal de la consulta'
      },
      padecimiento_actual: {
        type: Type.STRING,
        description: 'Descripción del padecimiento actual del paciente'
      },
      exploracion_fisica: {
        type: Type.STRING,
        description: 'Hallazgos de la exploración física'
      },
      diagnostico_presuntivo: {
        type: Type.STRING,
        description: 'Diagnóstico presuntivo o preliminar'
      },
      diagnostico_definitivo: {
        type: Type.STRING,
        description: 'Diagnóstico definitivo'
      },
      plan_tratamiento: {
        type: Type.STRING,
        description: 'Plan de tratamiento propuesto'
      },
      indicaciones_paciente: {
        type: Type.STRING,
        description: 'Indicaciones para el paciente'
      }
    },
    required: ['motivo_consulta']
  }
}
```

**Ejemplo de uso:**

- Usuario: "El motivo de consulta es dolor en el talón derecho desde hace 3 semanas"
- IA: *Llama a `create_clinical_note({motivo_consulta: "Dolor en talón derecho de 3 semanas de evolución"})`*
- IA: "He registrado el motivo de consulta"

---

### 3. `query_patient_data` - Consultar Datos del Paciente

```typescript
{
  name: 'query_patient_data',
  description: 'Consulta información específica del paciente (alergias, antecedentes, tratamientos previos, etc.)',
  parameters: {
    type: Type.OBJECT,
    properties: {
      tipo_consulta: {
        type: Type.STRING,
        description: 'Tipo de información a consultar',
        enum: [
          'alergias',
          'antecedentes_medicos',
          'tratamientos_previos',
          'ultima_cita',
          'signos_vitales_historico',
          'pagos_pendientes',
          'datos_contacto'
        ]
      },
      filtro_fecha: {
        type: Type.STRING,
        description: 'Filtro de fecha opcional (ej: "ultimos_6_meses", "ultimo_año")'
      }
    },
    required: ['tipo_consulta']
  }
}
```

**Ejemplo de uso:**

- Usuario: "¿Tiene el paciente alguna alergia?"
- IA: *Llama a `query_patient_data({tipo_consulta: "alergias"})`*
- IA: "Sí, el paciente tiene alergia a la penicilina registrada desde 2020"

---

### 4. `search_patient_history` - Buscar en Historial

```typescript
{
  name: 'search_patient_history',
  description: 'Busca información específica en el historial completo del paciente usando búsqueda semántica',
  parameters: {
    type: Type.OBJECT,
    properties: {
      query: {
        type: Type.STRING,
        description: 'Texto a buscar en el historial (ej: "tratamientos para hongos")'
      },
      limite_resultados: {
        type: Type.INTEGER,
        description: 'Número máximo de resultados a devolver',
        default: 5
      }
    },
    required: ['query']
  }
}
```

**Ejemplo de uso:**

- Usuario: "¿Cuándo fue la última vez que tratamos hongos en las uñas?"
- IA: *Llama a `search_patient_history({query: "tratamiento hongos uñas"})`*
- IA: "Encontré un tratamiento para onicomicosis en marzo de 2024"

---

### 5. `add_allergy` - Registrar Alergia

```typescript
{
  name: 'add_allergy',
  description: 'Registra una nueva alergia del paciente',
  parameters: {
    type: Type.OBJECT,
    properties: {
      tipo_alergeno: {
        type: Type.STRING,
        description: 'Tipo de alérgeno',
        enum: ['Medicamento', 'Alimento', 'Ambiental', 'Material', 'Otro']
      },
      nombre_alergeno: {
        type: Type.STRING,
        description: 'Nombre específico del alérgeno (ej: "Penicilina", "Látex")'
      },
      reaccion: {
        type: Type.STRING,
        description: 'Descripción de la reacción alérgica'
      },
      severidad: {
        type: Type.STRING,
        description: 'Severidad de la alergia',
        enum: ['Leve', 'Moderada', 'Grave', 'Mortal']
      }
    },
    required: ['tipo_alergeno', 'nombre_alergeno']
  }
}
```

---

### 6. `generate_summary` - Generar Resumen

```typescript
{
  name: 'generate_summary',
  description: 'Genera un resumen de la consulta actual o del historial del paciente',
  parameters: {
    type: Type.OBJECT,
    properties: {
      tipo_resumen: {
        type: Type.STRING,
        description: 'Tipo de resumen a generar',
        enum: ['consulta_actual', 'evolucion_tratamiento', 'historial_completo']
      },
      formato: {
        type: Type.STRING,
        description: 'Formato del resumen',
        enum: ['breve', 'detallado', 'para_paciente'],
        default: 'breve'
      }
    },
    required: ['tipo_resumen']
  }
}
```

---

### 7. `navigate_to_section` - Navegar en la Interfaz

```typescript
{
  name: 'navigate_to_section',
  description: 'Navega a una sección específica de la interfaz de consulta',
  parameters: {
    type: Type.OBJECT,
    properties: {
      seccion: {
        type: Type.STRING,
        description: 'Sección a la que navegar',
        enum: [
          'signos_vitales',
          'nota_clinica',
          'historial_medico',
          'tratamientos',
          'archivos_multimedia',
          'pagos',
          'evolucion'
        ]
      }
    },
    required: ['seccion']
  }
}
```

---

### 8. `schedule_followup` - Programar Seguimiento

```typescript
{
  name: 'schedule_followup',
  description: 'Programa una cita de seguimiento o recordatorio',
  parameters: {
    type: Type.OBJECT,
    properties: {
      tipo_seguimiento: {
        type: Type.STRING,
        description: 'Tipo de seguimiento',
        enum: ['cita_revision', 'recordatorio_tratamiento', 'llamada_seguimiento']
      },
      dias_adelante: {
        type: Type.INTEGER,
        description: 'Número de días en el futuro para programar'
      },
      notas: {
        type: Type.STRING,
        description: 'Notas adicionales sobre el seguimiento'
      }
    },
    required: ['tipo_seguimiento', 'dias_adelante']
  }
}
```

---

## 🎯 System Instructions para Gemini Live

```typescript
const SYSTEM_INSTRUCTION = `Eres un asistente médico de IA para la clínica de podología Podoskin Solution. 
Tu función es ayudar al Dr. Santiago durante las consultas médicas.

RESPONSABILIDADES:
1. Escuchar la conversación entre el doctor y el paciente
2. Llenar automáticamente los campos del expediente cuando escuches información relevante
3. Responder preguntas del doctor sobre el historial del paciente
4. Generar resúmenes de la consulta cuando se te solicite
5. Confirmar siempre las acciones que realizas

REGLAS IMPORTANTES:
- NUNCA des diagnósticos o recomendaciones médicas directamente al paciente
- SIEMPRE confirma antes de registrar información crítica (alergias, diagnósticos)
- Si escuchas español, responde en español
- Sé breve y preciso en tus respuestas durante la consulta
- Si no estás seguro de algo, pregunta al doctor

FORMATO DE RESPUESTAS:
- Para confirmaciones: "He registrado [dato] en [campo]"
- Para consultas: "Según el historial, [información solicitada]"
- Para errores: "No pude completar [acción] porque [razón]"

DATOS SENSIBLES:
- Trata toda la información médica con confidencialidad
- No repitas información sensible en voz alta a menos que sea necesario
`;
```

---

## 🔄 Flujo de Trabajo Típico

### Inicio de Consulta

1. Usuario: "Inicia consulta para paciente Juan Pérez"
2. IA: *Carga datos del paciente*
3. IA: "Consulta iniciada. Juan Pérez, 45 años. Última cita hace 3 meses"

### Durante la Consulta

1. Doctor: "Peso 78 kilos, talla 175"
2. IA: *Llama `update_vital_signs({peso_kg: 78, talla_cm: 175})`*
3. IA: "Registrado. IMC: 25.4"

### Consulta de Historial

1. Doctor: "¿Tiene alergias?"
2. IA: *Llama `query_patient_data({tipo_consulta: "alergias"})`*
3. IA: "Sí, alergia a látex moderada desde 2022"

### Fin de Consulta

1. Doctor: "Genera resumen de la consulta"
2. IA: *Llama `generate_summary({tipo_resumen: "consulta_actual"})`*
3. IA: "Resumen generado y guardado en la nota clínica"

---

## 📊 Métricas a Trackear

Todas las llamadas a funciones se registran en `function_calls_ejecutadas` con:

- Timestamp exacto
- Parámetros utilizados
- Resultado de la ejecución
- Tiempo de respuesta
- Errores (si los hay)

Esto permite:

- Auditoría completa de lo que la IA hizo
- Análisis de confiabilidad
- Mejora continua del sistema
- Cumplimiento regulatorio (HIPAA, GDPR)
