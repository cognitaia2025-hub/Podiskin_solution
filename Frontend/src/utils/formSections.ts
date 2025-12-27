import type { FormSection, GuidedStep, SelectOption } from '../types/medical';

// ============================================================================
// SECCIONES DEL FORMULARIO
// ============================================================================

export const FORM_SECTIONS: FormSection[] = [
  // PARTE 1: DATOS DEL PACIENTE
  {
    id: 'ficha_identificacion',
    title: '1. Ficha de Identificación',
    description: 'Datos personales y de contacto del paciente',
    icon: 'User',
    order: 1,
    requiredFields: ['primer_nombre', 'primer_apellido', 'fecha_nacimiento', 'sexo', 'telefono_principal'],
    fields: [
      {
        name: 'informacion_personal.primer_nombre',
        label: 'Primer Nombre',
        type: 'text',
        placeholder: 'Ingrese primer nombre',
        validation: { required: true, minLength: 2, message: 'El nombre debe tener al menos 2 caracteres' },
        gridCols: 6,
      },
      {
        name: 'informacion_personal.segundo_nombre',
        label: 'Segundo Nombre',
        type: 'text',
        placeholder: 'Opcional',
        gridCols: 6,
      },
      {
        name: 'informacion_personal.primer_apellido',
        label: 'Primer Apellido',
        type: 'text',
        placeholder: 'Ingrese primer apellido',
        validation: { required: true, minLength: 2 },
        gridCols: 6,
      },
      {
        name: 'informacion_personal.segundo_apellido',
        label: 'Segundo Apellido',
        type: 'text',
        placeholder: 'Opcional',
        gridCols: 6,
      },
      {
        name: 'informacion_personal.fecha_nacimiento',
        label: 'Fecha de Nacimiento',
        type: 'date',
        validation: { required: true },
        gridCols: 6,
      },
      {
        name: 'informacion_personal.sexo',
        label: 'Sexo',
        type: 'select',
        validation: { required: true },
        options: [
          { value: '', label: 'Seleccionar...' },
          { value: 'M', label: 'Masculino' },
          { value: 'F', label: 'Femenino' },
          { value: 'O', label: 'Otro' },
        ],
        gridCols: 6,
      },
      {
        name: 'informacion_personal.curp',
        label: 'CURP',
        type: 'text',
        placeholder: '18 caracteres',
        helpText: 'Clave Única de Registro de Población',
        gridCols: 6,
      },
      {
        name: 'informacion_personal.estado_civil',
        label: 'Estado Civil',
        type: 'select',
        options: [
          { value: '', label: 'Seleccionar...' },
          { value: 'Soltero/a', label: 'Soltero/a' },
          { value: 'Casado/a', label: 'Casado/a' },
          { value: 'Divorciado/a', label: 'Divorciado/a' },
          { value: 'Viudo/a', label: 'Viudo/a' },
          { value: 'Unión libre', label: 'Unión libre' },
        ],
        gridCols: 6,
      },
      {
        name: 'informacion_personal.escolaridad',
        label: 'Escolaridad',
        type: 'select',
        options: [
          { value: '', label: 'Seleccionar...' },
          { value: 'Sin estudios', label: 'Sin estudios' },
          { value: 'Primaria', label: 'Primaria' },
          { value: 'Secundaria', label: 'Secundaria' },
          { value: 'Preparatoria', label: 'Preparatoria' },
          { value: 'Licenciatura', label: 'Licenciatura' },
          { value: 'Posgrado', label: 'Posgrado' },
        ],
        gridCols: 6,
      },
      {
        name: 'informacion_personal.ocupacion',
        label: 'Ocupación',
        type: 'text',
        placeholder: 'Profesión o trabajo actual',
        gridCols: 6,
      },
      {
        name: 'informacion_personal.religion',
        label: 'Religión',
        type: 'text',
        placeholder: 'Opcional',
        gridCols: 12,
      },
      {
        name: 'informacion_personal.calle',
        label: 'Calle',
        type: 'text',
        placeholder: 'Nombre de la calle',
        gridCols: 8,
      },
      {
        name: 'informacion_personal.numero_exterior',
        label: 'Número Exterior',
        type: 'text',
        placeholder: 'Núm.',
        gridCols: 4,
      },
      {
        name: 'informacion_personal.numero_interior',
        label: 'Número Interior',
        type: 'text',
        placeholder: 'Depto/Oficina',
        gridCols: 6,
      },
      {
        name: 'informacion_personal.colonia',
        label: 'Colonia',
        type: 'text',
        placeholder: 'Colonia',
        gridCols: 6,
      },
      {
        name: 'informacion_personal.ciudad',
        label: 'Ciudad/Municipio',
        type: 'text',
        placeholder: 'Ciudad',
        gridCols: 6,
      },
      {
        name: 'informacion_personal.estado',
        label: 'Estado',
        type: 'text',
        placeholder: 'Estado',
        gridCols: 6,
      },
      {
        name: 'informacion_personal.codigo_postal',
        label: 'Código Postal',
        type: 'text',
        placeholder: 'CP',
        gridCols: 6,
      },
      {
        name: 'informacion_personal.telefono_principal',
        label: 'Teléfono Principal',
        type: 'phone',
        placeholder: '10 dígitos',
        validation: { required: true, minLength: 10, pattern: '^[0-9]{10}$', message: 'Ingrese un teléfono válido de 10 dígitos' },
        gridCols: 6,
      },
      {
        name: 'informacion_personal.telefono_secundario',
        label: 'Teléfono Secundario',
        type: 'phone',
        placeholder: 'Opcional',
        gridCols: 6,
      },
      {
        name: 'informacion_personal.correo_electronico',
        label: 'Correo Electrónico',
        type: 'email',
        placeholder: 'correo@ejemplo.com',
        validation: { pattern: '^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$', message: 'Ingrese un correo válido' },
        gridCols: 12,
      },
      {
        name: 'informacion_personal.como_supo_de_nosotros',
        label: '¿Cómo supo de nosotros?',
        type: 'text',
        placeholder: 'Recomendación, publicidad, redes sociales, etc.',
        gridCols: 12,
      },
    ],
  },

  {
    id: 'alergias',
    title: '2. Alergias',
    description: 'Alergias conocidas del paciente',
    icon: 'AlertTriangle',
    order: 2,
    requiredFields: [],
    fields: [
      {
        name: 'alergias',
        label: 'Lista de Alergias',
        type: 'array',
        helpText: 'Haga clic en "Agregar Alergia" para registrar cada alergia conocida',
        gridCols: 12,
      },
    ],
  },

  {
    id: 'antecedentes_medicos',
    title: '3. Antecedentes Médicos',
    description: 'Historial médico familiar y personal',
    icon: 'Heart',
    order: 3,
    requiredFields: [],
    fields: [
      {
        name: 'antecedentes_medicos.heredofamiliares',
        label: 'Antecedentes Heredofamiliares',
        type: 'array',
        helpText: 'Enfermedades que presentan familiares directos (padres, hermanos, abuelos)',
        gridCols: 12,
      },
      {
        name: 'antecedentes_medicos.patologicos',
        label: 'Antecedentes Patológicos',
        type: 'array',
        helpText: 'Enfermedades que el paciente ha tenido a lo largo de su vida',
        gridCols: 12,
      },
      {
        name: 'antecedentes_medicos.quirurgicos',
        label: 'Antecedentes Quirúrgicos',
        type: 'array',
        helpText: 'Cirugías previas que ha undergone el paciente',
        gridCols: 12,
      },
      {
        name: 'antecedentes_medicos.traumaticos',
        label: 'Antecedentes Traumáticos',
        type: 'array',
        helpText: 'Fracturas, golpes fuertes o lesiones importantes',
        gridCols: 12,
      },
      {
        name: 'antecedentes_medicos.transfusionales',
        label: 'Antecedentes Transfusionales',
        type: 'checkbox',
        gridCols: 12,
      },
    ],
  },

  {
    id: 'estilo_vida',
    title: '4. Estilo de Vida',
    description: 'Hábitos y factores de riesgo',
    icon: 'Activity',
    order: 4,
    requiredFields: [],
    fields: [
      {
        name: 'estilo_vida.dieta',
        label: 'Tipo de Dieta',
        type: 'select',
        options: [
          { value: '', label: 'Seleccionar...' },
          { value: 'Normal', label: 'Normal' },
          { value: 'Vegetariana', label: 'Vegetariana' },
          { value: 'Vegana', label: 'Vegana' },
          { value: 'Keto', label: 'Keto' },
          { value: 'Diabética', label: 'Diabética' },
          { value: 'Otro', label: 'Otro' },
        ],
        gridCols: 6,
      },
      {
        name: 'estilo_vida.descripcion_dieta',
        label: 'Descripción de la Dieta',
        type: 'textarea',
        placeholder: 'Describa sus hábitos alimenticios...',
        gridCols: 6,
      },
      {
        name: 'estilo_vida.suplementos_vitaminas',
        label: 'Suplementos o Vitaminas',
        type: 'text',
        placeholder: 'Vitaminas, minerales, suplementos...',
        gridCols: 12,
      },
      {
        name: 'estilo_vida.frecuencia_ejercicio',
        label: 'Frecuencia de Ejercicio',
        type: 'select',
        options: [
          { value: '', label: 'Seleccionar...' },
          { value: 'Nunca', label: 'Nunca' },
          { value: '1 vez por semana', label: '1 vez por semana' },
          { value: '2-3 veces por semana', label: '2-3 veces por semana' },
          { value: '4-5 veces por semana', label: '4-5 veces por semana' },
          { value: 'Todos los días', label: 'Todos los días' },
        ],
        gridCols: 6,
      },
      {
        name: 'estilo_vida.tipo_ejercicio',
        label: 'Tipo de Ejercicio',
        type: 'text',
        placeholder: 'Correr, nadar, caminata, gym, etc.',
        gridCols: 6,
      },
      {
        name: 'estilo_vida.fuma',
        label: '¿Fuma?',
        type: 'boolean',
        gridCols: 4,
      },
      {
        name: 'estilo_vida.cigarros_dia',
        label: 'Cigarrillos por Día',
        type: 'number',
        placeholder: '0',
        dependsOn: { field: 'estilo_vida.fuma', value: true },
        gridCols: 4,
      },
      {
        name: 'estilo_vida.anos_fumando',
        label: 'Años Fumando',
        type: 'number',
        placeholder: '0',
        dependsOn: { field: 'estilo_vida.fuma', value: true },
        gridCols: 4,
      },
      {
        name: 'estilo_vida.consume_alcohol',
        label: '¿Consume Alcohol?',
        type: 'boolean',
        gridCols: 6,
      },
      {
        name: 'estilo_vida.frecuencia_alcohol',
        label: 'Frecuencia de Consumo',
        type: 'select',
        options: [
          { value: '', label: 'Seleccionar...' },
          { value: 'Nunca', label: 'Nunca' },
          { value: 'Ocasionalmente', label: 'Ocasionalmente' },
          { value: '1-2 veces por semana', label: '1-2 veces por semana' },
          { value: '3-4 veces por semana', label: '3-4 veces por semana' },
          { value: 'Diario', label: 'Diario' },
        ],
        dependsOn: { field: 'estilo_vida.consume_alcohol', value: true },
        gridCols: 6,
      },
      {
        name: 'estilo_vida.consume_drogas',
        label: '¿Consume Drogas?',
        type: 'boolean',
        gridCols: 6,
      },
      {
        name: 'estilo_vida.tipo_drogas',
        label: 'Tipo de Drogas',
        type: 'text',
        placeholder: 'Especifique...',
        dependsOn: { field: 'estilo_vida.consume_drogas', value: true },
        gridCols: 6,
      },
      {
        name: 'estilo_vida.vacunas_completas',
        label: '¿Tiene Vacunas Completas?',
        type: 'boolean',
        gridCols: 6,
      },
      {
        name: 'estilo_vida.horas_sueno',
        label: 'Horas de Sueño Promedio',
        type: 'number',
        placeholder: '7-8 horas',
        gridCols: 6,
      },
      {
        name: 'estilo_vida.exposicion_toxicos',
        label: 'Exposición a Tóxicos',
        type: 'text',
        placeholder: 'Trabajo con químicos, pesticidas, etc.',
        gridCols: 12,
      },
      {
        name: 'estilo_vida.notas_adicionales',
        label: 'Notas Adicionales',
        type: 'textarea',
        placeholder: 'Otros datos relevantes sobre el estilo de vida...',
        gridCols: 12,
      },
    ],
  },

  {
    id: 'historia_ginecologica',
    title: '5. Historia Ginecológica',
    description: 'Datos de historia ginecológica (solo mujeres)',
    icon: 'Flower',
    order: 5,
    dependsOn: { field: 'informacion_personal.sexo', value: 'F' },
    requiredFields: [],
    fields: [
      {
        name: 'historia_ginecologica.edad_menarca',
        label: 'Edad de Primera Menstruación',
        type: 'number',
        placeholder: 'Edad en años',
        gridCols: 6,
      },
      {
        name: 'historia_ginecologica.dias_ciclo',
        label: 'Duración del Ciclo',
        type: 'number',
        placeholder: 'Días',
        gridCols: 6,
      },
      {
        name: 'historia_ginecologica.fecha_ultima_menstruacion',
        label: 'Fecha de Última Menstruación',
        type: 'date',
        gridCols: 6,
      },
      {
        name: 'historia_ginecologica.numero_embarazos',
        label: 'Número de Embarazos',
        type: 'number',
        placeholder: '0',
        gridCols: 4,
      },
      {
        name: 'historia_ginecologica.numero_partos',
        label: 'Número de Partos',
        type: 'number',
        placeholder: '0',
        gridCols: 4,
      },
      {
        name: 'historia_ginecologica.numero_cesareas',
        label: 'Número de Cesáreas',
        type: 'number',
        placeholder: '0',
        gridCols: 4,
      },
      {
        name: 'historia_ginecologica.numero_abortos',
        label: 'Número de Abortos',
        type: 'number',
        placeholder: '0',
        gridCols: 6,
      },
      {
        name: 'historia_ginecologica.metodo_anticonceptivo',
        label: 'Método Anticonceptivo',
        type: 'text',
        placeholder: 'Especifique el método...',
        gridCols: 6,
      },
      {
        name: 'historia_ginecologica.tiene_menopausia',
        label: '¿Ya tiene Menopausia?',
        type: 'boolean',
        gridCols: 6,
      },
      {
        name: 'historia_ginecologica.fecha_inicio_menopausia',
        label: 'Inicio de Menopausia',
        type: 'date',
        dependsOn: { field: 'historia_ginecologica.tiene_menopausia', value: true },
        gridCols: 6,
      },
      {
        name: 'historia_ginecologica.notas',
        label: 'Notas Adicionales',
        type: 'textarea',
        placeholder: '其他 datos relevantes...',
        gridCols: 12,
      },
    ],
  },

  {
    id: 'motivo_consulta',
    title: '6. Motivo de Consulta',
    description: 'Razón de la visita actual',
    icon: 'Clipboard',
    order: 6,
    requiredFields: ['sintomas_principales'],
    fields: [
      {
        name: 'motivo_consulta.sintomas_principales',
        label: 'Síntomas Principales',
        type: 'textarea',
        placeholder: 'Describa el motivo de su visita...',
        validation: { required: true, minLength: 10, message: 'Por favor describa los síntomas con más detalle' },
        gridCols: 12,
        helpText: 'Sea lo más específico posible sobre el problema',
      },
      {
        name: 'motivo_consulta.fecha_inicio_sintomas',
        label: '¿Cuándo iniciaron los síntomas?',
        type: 'text',
        placeholder: 'Hace una semana, hace un mes, etc.',
        gridCols: 6,
      },
      {
        name: 'motivo_consulta.evolucion_sintomas',
        label: '¿Cómo han evolucionado los síntomas?',
        type: 'textarea',
        placeholder: '¿Han empeorado, mejorado, stayed igual?',
        gridCols: 6,
      },
      {
        name: 'motivo_consulta.automedicacion',
        label: '¿Ha tomado algún medicamento?',
        type: 'textarea',
        placeholder: 'Medicamentos, cremas, remedios caseros...',
        gridCols: 12,
      },
    ],
  },

  // PARTE 2: DATOS DEL MÉDICO
  {
    id: 'signos_vitales',
    title: '7. Signos Vitales',
    description: 'Mediciones biométricas del paciente',
    icon: 'Thermometer',
    order: 7,
    requiredFields: [],
    fields: [
      {
        name: 'signos_vitales.fecha_hora_medicion',
        label: 'Fecha y Hora',
        type: 'datetime',
        gridCols: 6,
      },
      {
        name: 'signos_vitales.peso_kg',
        label: 'Peso (kg)',
        type: 'number',
        placeholder: '0.0',
        validation: { min: 0, max: 300 },
        gridCols: 3,
      },
      {
        name: 'signos_vitales.talla_cm',
        label: 'Talla (cm)',
        type: 'number',
        placeholder: '0',
        validation: { min: 0, max: 250 },
        gridCols: 3,
      },
      {
        name: 'signos_vitales.imc',
        label: 'IMC',
        type: 'number',
        placeholder: 'Auto-calculado',
        helpText: 'Índice de Masa Corporal',
        gridCols: 3,
      },
      {
        name: 'signos_vitales.presion_arterial_sistolica',
        label: 'PA Sistólica (mmHg)',
        type: 'number',
        placeholder: '120',
        validation: { min: 60, max: 250 },
        gridCols: 3,
      },
      {
        name: 'signos_vitales.presion_arterial_diastolica',
        label: 'PA Diastólica (mmHg)',
        type: 'number',
        placeholder: '80',
        validation: { min: 40, max: 150 },
        gridCols: 3,
      },
      {
        name: 'signos_vitales.frecuencia_cardiaca',
        label: 'Frecuencia Cardíaca (lpm)',
        type: 'number',
        placeholder: '70',
        validation: { min: 30, max: 250 },
        gridCols: 3,
      },
      {
        name: 'signos_vitales.frecuencia_respiratoria',
        label: 'Frecuencia Respiratoria (rpm)',
        type: 'number',
        placeholder: '16',
        validation: { min: 8, max: 60 },
        gridCols: 3,
      },
      {
        name: 'signos_vitales.temperatura_celsius',
        label: 'Temperatura (°C)',
        type: 'number',
        placeholder: '36.5',
        validation: { min: 32, max: 42 },
        gridCols: 3,
      },
      {
        name: 'signos_vitales.saturacion_o2',
        label: 'SpO2 (%)',
        type: 'number',
        placeholder: '98',
        validation: { min: 0, max: 100 },
        gridCols: 3,
      },
      {
        name: 'signos_vitales.glucosa_capilar',
        label: 'Glucosa Capilar (mg/dL)',
        type: 'number',
        placeholder: '100',
        validation: { min: 0, max: 500 },
        gridCols: 6,
      },
    ],
  },

  {
    id: 'exploracion_fisica',
    title: '8. Exploración Física',
    description: 'Evaluación podológica completa',
    icon: 'Stethoscope',
    order: 8,
    requiredFields: [],
    fields: [
      {
        name: 'exploracion_fisica.estado_general',
        label: 'Estado General',
        type: 'textarea',
        placeholder: 'Estado general del paciente...',
        gridCols: 12,
      },
      {
        name: 'exploracion_fisica.inspeccion_pies',
        label: 'Inspección de Pies',
        type: 'textarea',
        placeholder: 'Observaciones visuales de ambos pies...',
        helpText: 'Color, forma, edemas, deformidades visibles',
        gridCols: 6,
      },
      {
        name: 'exploracion_fisica.palpacion',
        label: 'Palpación',
        type: 'textarea',
        placeholder: 'Hallazgos a la palpación...',
        helpText: 'Dolor, sensibilidad, temperatura, pulsos',
        gridCols: 6,
      },
      {
        name: 'exploracion_fisica.movilidad',
        label: 'Movilidad Articular',
        type: 'textarea',
        placeholder: 'Rango de movimiento de articulaciones...',
        gridCols: 6,
      },
      {
        name: 'exploracion_fisica.sensibilidad',
        label: 'Sensibilidad',
        type: 'textarea',
        placeholder: 'Pruebas de sensibilidad realizadas...',
        helpText: 'Monofilamento, sensibilidad superficial y profunda',
        gridCols: 6,
      },
      {
        name: 'exploracion_fisica.circulacion',
        label: 'Circulación',
        type: 'textarea',
        placeholder: 'Evaluación de circulación sanguínea...',
        helpText: 'Pulsos pedios, tibial posterior, llenado capilar',
        gridCols: 6,
      },
      {
        name: 'exploracion_fisica.lesiones_observadas',
        label: 'Lesiones Observadas',
        type: 'textarea',
        placeholder: 'Descripción detallada de lesiones...',
        helpText: 'Úlceras, heridas, ampollas, eritema, etc.',
        gridCols: 6,
      },
      {
        name: 'exploracion_fisica.deformidades',
        label: 'Deformidades',
        type: 'textarea',
        placeholder: 'Deformidades estructurales identificadas...',
        helpText: 'Juanetes, dedos en garra, pie plano, etc.',
        gridCols: 6,
      },
      {
        name: 'exploracion_fisica.estado_unas',
        label: 'Estado de Uñas',
        type: 'textarea',
        placeholder: 'Condición de las uñas...',
        helpText: 'Onicomicosis, uña incarnada, engrosamiento, etc.',
        gridCols: 6,
      },
      {
        name: 'exploracion_fisica.estado_piel',
        label: 'Estado de la Piel',
        type: 'textarea',
        placeholder: 'Condición de la piel de pies y piernas...',
        helpText: 'Xerosis, fisuras, maceración, queratosis',
        gridCols: 6,
      },
    ],
  },

  {
    id: 'diagnosticos',
    title: '9. Diagnósticos',
    description: 'Diagnósticos clínicos con código CIE-10',
    icon: 'ClipboardList',
    order: 9,
    requiredFields: [],
    fields: [
      {
        name: 'diagnosticos',
        label: 'Lista de Diagnósticos',
        type: 'array',
        helpText: 'Agregue los diagnósticos presuntivos, definitivos o diferenciales',
        gridCols: 12,
      },
    ],
  },

  {
    id: 'plan_tratamiento',
    title: '10. Plan de Tratamiento',
    description: 'Servicios y procedimientos a realizar',
    icon: 'Package',
    order: 10,
    requiredFields: [],
    fields: [
      {
        name: 'plan_tratamiento',
        label: 'Tratamientos/Servicios',
        type: 'array',
        helpText: 'Seleccione los tratamientos a aplicar en esta sesión',
        gridCols: 12,
      },
    ],
  },

  {
    id: 'indicaciones',
    title: '11. Indicaciones y Pronóstico',
    description: 'Plan de tratamiento, indicaciones al paciente y pronóstico',
    icon: 'FileText',
    order: 11,
    requiredFields: [],
    fields: [
      {
        name: 'indicaciones.plan_tratamiento_general',
        label: 'Plan de Tratamiento General',
        type: 'textarea',
        placeholder: 'Describa el plan de tratamiento integral...',
        gridCols: 12,
      },
      {
        name: 'indicaciones.cuidados_casa',
        label: 'Cuidados en Casa',
        type: 'textarea',
        placeholder: 'Instrucciones para cuidados en el hogar...',
        helpText: 'Higiene, ejercicios, restricciones',
        gridCols: 6,
      },
      {
        name: 'indicaciones.medicamentos_recetados',
        label: 'Medicamentos Recetados',
        type: 'textarea',
        placeholder: 'Medicamentos, dosis y frecuencia...',
        gridCols: 6,
      },
      {
        name: 'indicaciones.restricciones',
        label: 'Restricciones',
        type: 'textarea',
        placeholder: 'Actividades o acciones a evitar...',
        gridCols: 6,
      },
      {
        name: 'indicaciones.recomendaciones',
        label: 'Recomendaciones',
        type: 'textarea',
        placeholder: 'Recomendaciones adicionales...',
        gridCols: 6,
      },
      {
        name: 'indicaciones.pronostico',
        label: 'Pronóstico',
        type: 'select',
        options: [
          { value: '', label: 'Seleccionar...' },
          { value: 'Bueno', label: 'Bueno' },
          { value: 'Reservado', label: 'Reservado' },
          { value: 'Malo', label: 'Malo' },
        ],
        gridCols: 6,
      },
      {
        name: 'indicaciones.fecha_proxima_cita',
        label: 'Próxima Cita',
        type: 'date',
        gridCols: 6,
      },
    ],
  },

  {
    id: 'evolucion',
    title: '12. Evolución del Tratamiento',
    description: 'Seguimiento y evolución del paciente',
    icon: 'TrendingUp',
    order: 12,
    requiredFields: [],
    fields: [
      {
        name: 'evolucion',
        label: 'Historial de Evolución',
        type: 'array',
        helpText: 'Registro de cada fase de evolución del tratamiento',
        gridCols: 12,
      },
    ],
  },
];

// ============================================================================
// PASOS PARA MODO GUIADO
// ============================================================================

export const GUIDED_STEPS: GuidedStep[] = [
  {
    id: 'step-1',
    title: 'Datos Personales',
    description: 'Información básica del paciente',
    sectionId: 'ficha_identificacion',
    order: 1,
    fields: [
      'informacion_personal.primer_nombre',
      'informacion_personal.segundo_nombre',
      'informacion_personal.primer_apellido',
      'informacion_personal.segundo_apellido',
      'informacion_personal.fecha_nacimiento',
      'informacion_personal.sexo',
      'informacion_personal.telefono_principal',
    ],
  },
  {
    id: 'step-2',
    title: 'Datos de Contacto',
    description: 'Domicilio y contacto adicional',
    sectionId: 'ficha_identificacion',
    order: 2,
    fields: [
      'informacion_personal.curp',
      'informacion_personal.estado_civil',
      'informacion_personal.escolaridad',
      'informacion_personal.ocupacion',
      'informacion_personal.calle',
      'informacion_personal.numero_exterior',
      'informacion_personal.colonia',
      'informacion_personal.ciudad',
      'informacion_personal.estado',
      'informacion_personal.codigo_postal',
      'informacion_personal.telefono_secundario',
      'informacion_personal.correo_electronico',
    ],
  },
  {
    id: 'step-3',
    title: 'Alergias',
    description: 'Alergias conocidas',
    sectionId: 'alergias',
    order: 3,
    fields: ['alergias'],
  },
  {
    id: 'step-4',
    title: 'Antecedentes',
    description: 'Historial médico',
    sectionId: 'antecedentes_medicos',
    order: 4,
    fields: [
      'antecedentes_medicos.heredofamiliares',
      'antecedentes_medicos.patologicos',
      'antecedentes_medicos.quirurgicos',
      'antecedentes_medicos.traumaticos',
      'antecedentes_medicos.transfusionales',
    ],
  },
  {
    id: 'step-5',
    title: 'Estilo de Vida',
    description: 'Hábitos y factores de riesgo',
    sectionId: 'estilo_vida',
    order: 5,
    fields: [
      'estilo_vida.dieta',
      'estilo_vida.fuma',
      'estilo_vida.consume_alcohol',
      'estilo_vida.consume_drogas',
      'estilo_vida.vacunas_completas',
      'estilo_vida.frecuencia_ejercicio',
      'estilo_vida.horas_sueno',
    ],
  },
  {
    id: 'step-6',
    title: 'Historia Ginecológica',
    description: 'Datos ginecológicos (mujeres)',
    sectionId: 'historia_ginecologica',
    order: 6,
    isOptional: true,
    dependsOn: { field: 'informacion_personal.sexo', value: 'F' },
    fields: [
      'historia_ginecologica.edad_menarca',
      'historia_ginecologica.numero_embarazos',
      'historia_ginecologica.numero_partos',
      'historia_ginecologica.tiene_menopausia',
    ],
  },
  {
    id: 'step-7',
    title: 'Motivo de Consulta',
    description: 'Razón de la visita',
    sectionId: 'motivo_consulta',
    order: 7,
    fields: [
      'motivo_consulta.sintomas_principales',
      'motivo_consulta.fecha_inicio_sintomas',
      'motivo_consulta.evolucion_sintomas',
      'motivo_consulta.automedicacion',
    ],
  },
  {
    id: 'step-8',
    title: 'Signos Vitales',
    description: 'Mediciones biométricas',
    sectionId: 'signos_vitales',
    order: 8,
    fields: [
      'signos_vitales.peso_kg',
      'signos_vitales.talla_cm',
      'signos_vitales.presion_arterial_sistolica',
      'signos_vitales.presion_arterial_diastolica',
      'signos_vitales.frecuencia_cardiaca',
      'signos_vitales.temperatura_celsius',
      'signos_vitales.saturacion_o2',
    ],
  },
  {
    id: 'step-9',
    title: 'Exploración Física',
    description: 'Evaluación podológica',
    sectionId: 'exploracion_fisica',
    order: 9,
    fields: [
      'exploracion_fisica.inspeccion_pies',
      'exploracion_fisica.palpacion',
      'exploracion_fisica.sensibilidad',
      'exploracion_fisica.circulacion',
      'exploracion_fisica.lesiones_observadas',
      'exploracion_fisica.deformidades',
      'exploracion_fisica.estado_unas',
      'exploracion_fisica.estado_piel',
    ],
  },
  {
    id: 'step-10',
    title: 'Diagnóstico',
    description: 'Diagnóstico clínico',
    sectionId: 'diagnosticos',
    order: 10,
    fields: ['diagnosticos'],
  },
  {
    id: 'step-11',
    title: 'Tratamiento',
    description: 'Plan de tratamiento',
    sectionId: 'plan_tratamiento',
    order: 11,
    fields: ['plan_tratamiento'],
  },
  {
    id: 'step-12',
    title: 'Indicaciones',
    description: 'Indicaciones al paciente',
    sectionId: 'indicaciones',
    order: 12,
    fields: [
      'indicaciones.plan_tratamiento_general',
      'indicaciones.cuidados_casa',
      'indicaciones.pronostico',
      'indicaciones.fecha_proxima_cita',
    ],
  },
];

// ============================================================================
// UTILIDADES
// ============================================================================

export function getSectionById(id: string): FormSection | undefined {
  return FORM_SECTIONS.find(section => section.id === id);
}

export function getStepById(id: string): GuidedStep | undefined {
  return GUIDED_STEPS.find(step => step.id === id);
}

export function getStepsBySection(sectionId: string): GuidedStep[] {
  return GUIDED_STEPS.filter(step => step.sectionId === sectionId);
}

export function getTotalSteps(): number {
  return GUIDED_STEPS.length;
}

export function getProgressPercentage(completedSteps: number[], totalSteps: number = GUIDED_STEPS.length): number {
  if (totalSteps === 0) return 0;
  return Math.round((completedSteps.length / totalSteps) * 100);
}

export function getNextStep(currentStep: number): number {
  const nextStep = GUIDED_STEPS.find(step => step.order > currentStep);
  return nextStep?.order || -1;
}

export function getPreviousStep(currentStep: number): number {
  const previousSteps = GUIDED_STEPS.filter(step => step.order < currentStep);
  const lastPrevious = previousSteps[previousSteps.length - 1];
  return lastPrevious?.order || -1;
}

// Filtrar pasos según condiciones
export function getVisibleSteps(formData: Record<string, any>): GuidedStep[] {
  return GUIDED_STEPS.filter(step => {
    if (!step.dependsOn) return true;
    const { field, value } = step.dependsOn;
    const fieldValue = getNestedValue(formData, field);
    return fieldValue === value;
  });
}

// Obtener valor anidado de un objeto
function getNestedValue(obj: Record<string, any>, path: string): any {
  return path.split('.').reduce((acc, part) => acc && acc[part], obj);
}

// Obtener campos requeridos de un paso
export function getRequiredFieldsForStep(step: GuidedStep, sections: FormSection[]): string[] {
  const section = sections.find(s => s.id === step.sectionId);
  if (!section || !section.requiredFields) return [];
  
  // Mapear campos requeridos al path completo
  return section.requiredFields.map(fieldName => {
    const fieldConfig = section.fields.find(f => f.name.endsWith(`.${fieldName}`) || f.name === fieldName);
    return fieldConfig?.name || fieldName;
  });
}
