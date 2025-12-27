import { z } from 'zod';

// ============================================================================
// ESQUEMAS ZOD (Validación)
// ============================================================================

// Datos Personales
export const PersonalInfoSchema = z.object({
  primer_nombre: z.string().min(1, 'El primer nombre es obligatorio'),
  segundo_nombre: z.string().optional(),
  primer_apellido: z.string().min(1, 'El primer apellido es obligatorio'),
  segundo_apellido: z.string().optional(),
  fecha_nacimiento: z.string().min(1, 'La fecha de nacimiento es obligatoria'),
  sexo: z.enum(['M', 'F', 'O'], { required_error: 'El sexo es obligatorio' }),
  curp: z.string().optional(),
  estado_civil: z.string().optional(),
  escolaridad: z.string().optional(),
  ocupacion: z.string().optional(),
  religion: z.string().optional(),
  // Domicilio
  calle: z.string().optional(),
  numero_exterior: z.string().optional(),
  numero_interior: z.string().optional(),
  colonia: z.string().optional(),
  ciudad: z.string().optional(),
  estado: z.string().optional(),
  codigo_postal: z.string().optional(),
  // Contacto
  telefono_principal: z.string().min(10, 'El teléfono debe tener al menos 10 dígitos'),
  telefono_secundario: z.string().optional(),
  correo_electronico: z.string().email('Correo electrónico inválido').optional().or(z.literal('')),
  // Referencia
  como_supo_de_nosotros: z.string().optional(),
});

export type PersonalInfo = z.infer<typeof PersonalInfoSchema>;

// Alergia
export const AllergySchema = z.object({
  id: z.string(),
  tipo_alergeno: z.enum(['Medicamento', 'Alimento', 'Ambiental', 'Material', 'Otro']),
  nombre_alergeno: z.string().min(1, 'El nombre del alérgeno es obligatorio'),
  reaccion: z.string().optional(),
  severidad: z.enum(['Leve', 'Moderada', 'Grave', 'Mortal']),
  fecha_diagnostico: z.string().optional(),
  notas: z.string().optional(),
});

export type Allergy = z.infer<typeof AllergySchema>;

// Antecedentes Heredofamiliares
export const FamilyHistorySchema = z.object({
  id: z.string(),
  enfermedad: z.string().min(1, 'La enfermedad es obligatoria'),
  parentesco: z.string().min(1, 'El parentesco es obligatorio'),
  fecha_diagnostico: z.string().optional(),
  tratamiento: z.string().optional(),
  esta_controlado: z.boolean(),
});

export type FamilyHistory = z.infer<typeof FamilyHistorySchema>;

// Antecedentes Patológicos
export const PathologicalHistorySchema = z.object({
  id: z.string(),
  enfermedad: z.string().min(1, 'La enfermedad es obligatoria'),
  fecha_diagnostico: z.string().optional(),
  tratamiento_actual: z.string().optional(),
  esta_controlado: z.boolean(),
});

export type PathologicalHistory = z.infer<typeof PathologicalHistorySchema>;

// Antecedentes Quirúrgicos
export const SurgicalHistorySchema = z.object({
  id: z.string(),
  tipo_cirugia: z.string().min(1, 'El tipo de cirugía es obligatorio'),
  fecha: z.string().optional(),
  descripcion: z.string().optional(),
});

export type SurgicalHistory = z.infer<typeof SurgicalHistorySchema>;

// Antecedentes Traumáticos
export const TraumaticHistorySchema = z.object({
  id: z.string(),
  tipo_traumatismo: z.string().min(1, 'El tipo de traumatismo es obligatorio'),
  fecha: z.string().optional(),
  descripcion: z.string().optional(),
});

export type TraumaticHistory = z.infer<typeof TraumaticHistorySchema>;

// Antecedentes Transfusionales
export const TransfusionHistorySchema = z.object({
  ha_recibido_transfusiones: z.boolean(),
  fecha: z.string().optional(),
  descripcion: z.string().optional(),
});

export type TransfusionHistory = z.infer<typeof TransfusionHistorySchema>;

// Antecedentes Médicos Completos
export const MedicalHistorySchema = z.object({
  heredofamiliares: z.array(FamilyHistorySchema),
  patologicos: z.array(PathologicalHistorySchema),
  quirurgicos: z.array(SurgicalHistorySchema),
  traumaticos: z.array(TraumaticHistorySchema),
  transfusionales: TransfusionHistorySchema,
});

export type MedicalHistory = z.infer<typeof MedicalHistorySchema>;

// Estilo de Vida
export const LifestyleSchema = z.object({
  dieta: z.enum(['Normal', 'Vegetariana', 'Vegana', 'Keto', 'Diabética', 'Otro']),
  descripcion_dieta: z.string().optional(),
  suplementos_vitaminas: z.string().optional(),
  frecuencia_ejercicio: z.string().optional(),
  tipo_ejercicio: z.string().optional(),
  fuma: z.boolean(),
  cigarros_dia: z.number().optional(),
  anos_fumando: z.number().optional(),
  consume_alcohol: z.boolean(),
  frecuencia_alcohol: z.string().optional(),
  consume_drogas: z.boolean(),
  tipo_drogas: z.string().optional(),
  vacunas_completas: z.boolean(),
  esquema_vacunacion: z.string().optional(),
  horas_sueno: z.number().min(0).max(24).optional(),
  exposicion_toxicos: z.string().optional(),
  notas_adicionales: z.string().optional(),
});

export type Lifestyle = z.infer<typeof LifestyleSchema>;

// Historia Ginecológica (Solo mujeres)
export const GynecologicalHistorySchema = z.object({
  edad_menarca: z.number().optional(),
  dias_ciclo: z.number().optional(),
  fecha_ultima_menstruacion: z.string().optional(),
  numero_embarazos: z.number().optional(),
  numero_partos: z.number().optional(),
  numero_cesareas: z.number().optional(),
  numero_abortos: z.number().optional(),
  metodo_anticonceptivo: z.string().optional(),
  tiene_menopausia: z.boolean(),
  fecha_inicio_menopausia: z.string().optional(),
  notas: z.string().optional(),
});

export type GynecologicalHistory = z.infer<typeof GynecologicalHistorySchema>;

// Motivo de Consulta
export const ConsultationReasonSchema = z.object({
  sintomas_principales: z.string().min(1, 'El síntoma principal es obligatorio'),
  fecha_inicio_sintomas: z.string().optional(),
  evolucion_sintomas: z.string().optional(),
  automedicacion: z.string().optional(),
});

export type ConsultationReason = z.infer<typeof ConsultationReasonSchema>;

// Signos Vitales
export const VitalSignsSchema = z.object({
  fecha_hora_medicion: z.string().optional(),
  peso_kg: z.number().min(0).max(300, 'Peso inválido').optional(),
  talla_cm: z.number().min(0).max(250, 'Talla inválida').optional(),
  imc: z.number().optional(), // Auto-calculado
  presion_arterial_sistolica: z.number().min(60).max(250, 'Valor inválido').optional(),
  presion_arterial_diastolica: z.number().min(40).max(150, 'Valor inválido').optional(),
  frecuencia_cardiaca: z.number().min(30).max(250, 'Valor inválido').optional(),
  frecuencia_respiratoria: z.number().min(8).max(60, 'Valor inválido').optional(),
  temperatura_celsius: z.number().min(32).max(42, 'Temperatura inválida').optional(),
  saturacion_o2: z.number().min(0).max(100, 'Valor inválido').optional(),
  glucosa_capilar: z.number().min(0).max(500, 'Valor inválido').optional(),
  medido_por: z.string().optional(),
});

export type VitalSigns = z.infer<typeof VitalSignsSchema>;

// Exploración Física
export const PhysicalExamSchema = z.object({
  estado_general: z.string().optional(),
  inspeccion_pies: z.string().optional(),
  palpacion: z.string().optional(),
  movilidad: z.string().optional(),
  sensibilidad: z.string().optional(),
  circulacion: z.string().optional(),
  lesiones_observadas: z.string().optional(),
  deformidades: z.string().optional(),
  estado_unas: z.string().optional(),
  estado_piel: z.string().optional(),
});

export type PhysicalExam = z.infer<typeof PhysicalExamSchema>;

// Diagnóstico
export const DiagnosisSchema = z.object({
  id: z.string(),
  tipo: z.enum(['Presuntivo', 'Definitivo', 'Diferencial']),
  descripcion: z.string().min(1, 'La descripción del diagnóstico es obligatoria'),
  cie10_catalogo: z.string().optional(),
  cie10_manual: z.string().optional(),
  fecha_diagnostico: z.string().optional(),
  diagnostico_por: z.string().optional(),
  notas: z.string().optional(),
});

export type Diagnosis = z.infer<typeof DiagnosisSchema>;

// Plan de Tratamiento
export const TreatmentPlanSchema = z.object({
  id: z.string(),
  servicio: z.string().min(1, 'El servicio es obligatorio'),
  precio_aplicado: z.number().min(0).optional(),
  descuento_porcentaje: z.number().min(0).max(100).optional(),
  precio_final: z.number().optional(),
  notas: z.string().optional(),
});

export type TreatmentPlan = z.infer<typeof TreatmentPlanSchema>;

// Indicaciones
export const IndicationsSchema = z.object({
  plan_tratamiento_general: z.string().optional(),
  indicaciones_paciente: z.string().optional(),
  cuidados_casa: z.string().optional(),
  medicamentos_recetados: z.string().optional(),
  restricciones: z.string().optional(),
  recomendaciones: z.string().optional(),
  pronostico: z.enum(['Bueno', 'Reservado', 'Malo']).optional(),
  fecha_proxima_cita: z.string().optional(),
});

export type Indications = z.infer<typeof IndicationsSchema>;

// Evolución
export const EvolutionSchema = z.object({
  id: z.string(),
  fase: z.number(),
  fecha_evaluacion: z.string(),
  descripcion: z.string().min(1, 'La descripción es obligatoria'),
  resultado: z.enum(['Mejoría', 'Sin cambios', 'Empeoramiento']),
  indicaciones_siguiente_fase: z.string().optional(),
  fecha_proxima_revision: z.string().optional(),
  evaluado_por: z.string().optional(),
});

export type Evolution = z.infer<typeof EvolutionSchema>;

// Consentimientos
export const ConsentSchema = z.object({
  tipo_consentimiento: z.string().optional(),
  fecha_firma: z.string().optional(),
  firmado_digitalmente: z.boolean(),
  testigo1: z.string().optional(),
  testigo2: z.string().optional(),
});

export type Consent = z.infer<typeof ConsentSchema>;

// Información de Pago
export const PaymentInfoSchema = z.object({
  metodo_pago: z.enum(['Efectivo', 'Tarjeta Débito', 'Tarjeta Crédito', 'Transferencia', 'Cheque', 'Otro']),
  requiere_factura: z.boolean(),
  rfc_factura: z.string().optional(),
});

export type PaymentInfo = z.infer<typeof PaymentInfoSchema>;

// Expediente Médico Completo
export const MedicalRecordSchema = z.object({
  id: z.string(),
  id_paciente: z.string(),
  id_podologo: z.string(),
  fecha_creacion: z.string(),
  fecha_actualizacion: z.string(),
  // Parte 1: Datos del Paciente
  informacion_personal: PersonalInfoSchema,
  alergias: z.array(AllergySchema),
  antecedentes_medicos: MedicalHistorySchema,
  estilo_vida: LifestyleSchema,
  historia_ginecologica: GynecologicalHistorySchema.optional(),
  motivo_consulta: ConsultationReasonSchema,
  consentimientos: ConsentSchema.optional(),
  informacion_pago: PaymentInfoSchema.optional(),
  // Parte 2: Datos del Médico
  signos_vitales: VitalSignsSchema.optional(),
  exploracion_fisica: PhysicalExamSchema.optional(),
  diagnosticos: z.array(DiagnosisSchema),
  plan_tratamiento: z.array(TreatmentPlanSchema),
  indicaciones: IndicationsSchema.optional(),
  evolucion: z.array(EvolutionSchema),
  // Estado
  estado: z.enum(['Borrador', 'Completado', 'Firmado', 'Archivado']),
  notas_privadas: z.string().optional(),
});

export type MedicalRecord = z.infer<typeof MedicalRecordSchema>;

// ============================================================================
// CONFIGURACIÓN DE CAMPOS DE FORMULARIO
// ============================================================================

export type FieldType = 
  | 'text' 
  | 'number' 
  | 'email' 
  | 'phone' 
  | 'date' 
  | 'datetime' 
  | 'select' 
  | 'multiselect' 
  | 'textarea' 
  | 'radio' 
  | 'checkbox' 
  | 'boolean' 
  | 'currency'
  | 'array';

export interface SelectOption {
  value: string;
  label: string;
}

export interface FieldValidation {
  required?: boolean;
  min?: number;
  max?: number;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
  message?: string;
}

export interface FormFieldConfig {
  name: string;
  label: string;
  type: FieldType;
  placeholder?: string;
  helpText?: string;
  options?: SelectOption[];
  validation?: FieldValidation;
  dependsOn?: {
    field: string;
    value: any;
  };
  gridCols?: number; // Para layout en grid
}

export interface FormSection {
  id: string;
  title: string;
  description?: string;
  icon?: string;
  order: number;
  fields: FormFieldConfig[];
  requiredFields?: string[];
  dependsOn?: {
    field: string;
    value: any;
  };
}

// ============================================================================
// CONFIGURACIÓN DE PASOS PARA MODO GUIADO
// ============================================================================

export interface GuidedStep {
  id: string;
  title: string;
  description?: string;
  sectionId: string;
  order: number;
  fields: string[]; // Nombres de campos en este paso
  isOptional?: boolean;
  helpText?: string;
}

// ============================================================================
// ESTADO DEL FORMULARIO
// ============================================================================

export type FormMode = 'guided' | 'free';

export interface FormState {
  currentStep: number;
  completedSteps: number[];
  errors: Record<string, string>;
  isDirty: boolean;
  isSubmitting: boolean;
  isSaving: boolean;
  lastSavedAt: Date | null;
  showValidationErrors: boolean;
}

export interface MedicalFormContextValue {
  // Datos
  formData: Partial<MedicalRecord>;
  formState: FormState;
  formMode: FormMode;
  
  // Paciente actual
  currentPatient: {
    id: string;
    name: string;
    phone?: string;
    email?: string;
  } | null;
  
  // Acciones
  updateFormData: (path: string, value: any) => void;
  setFormMode: (mode: FormMode) => void;
  setCurrentStep: (step: number) => void;
  markStepComplete: (stepId: number) => void;
  validateField: (fieldName: string, value: any) => string | null;
  validateForm: () => boolean;
  saveForm: () => Promise<void>;
  submitForm: () => Promise<void>;
  resetForm: () => void;
  
  // Utilidades
  getFieldValue: (path: string) => any;
  calculateIMC: (peso: number, talla: number) => number;
  getProgressPercentage: () => number;
}

// ============================================================================
// INTERFACES DE API/MOCK
// ============================================================================

export interface MayaSuggestion {
  id: string;
  type: 'diagnosis' | 'treatment' | 'cie10' | 'summary' | 'autocomplete';
  confidence: number;
  content: string;
  explanation?: string;
  actionLabel?: string;
}

export interface PatientSummary {
  age: number;
  riskFactors: string[];
  allergiesSummary: string;
  chronicConditions: string[];
  currentMedications: string[];
  lastVisit?: Date;
  pendingTreatments: string[];
}

export interface Cie10Code {
  code: string;
  description: string;
  category: string;
}

// ============================================================================
// UTILIDADES DE SCHEMA
// ============================================================================

// Crear expediente vacío
export function createEmptyMedicalRecord(id_paciente: string, id_podologo: string): MedicalRecord {
  return {
    id: crypto.randomUUID(),
    id_paciente,
    id_podologo,
    fecha_creacion: new Date().toISOString(),
    fecha_actualizacion: new Date().toISOString(),
    informacion_personal: {
      primer_nombre: '',
      segundo_nombre: '',
      primer_apellido: '',
      segundo_apellido: '',
      fecha_nacimiento: '',
      sexo: undefined as any,
      curp: '',
      estado_civil: '',
      escolaridad: '',
      ocupacion: '',
      religion: '',
      calle: '',
      numero_exterior: '',
      numero_interior: '',
      colonia: '',
      ciudad: '',
      estado: '',
      codigo_postal: '',
      telefono_principal: '',
      telefono_secundario: '',
      correo_electronico: '',
      como_supo_de_nosotros: '',
    },
    alergias: [],
    antecedentes_medicos: {
      heredofamiliares: [],
      patologicos: [],
      quirurgicos: [],
      traumaticos: [],
      transfusionales: {
        ha_recibido_transfusiones: false,
        fecha: undefined,
        descripcion: '',
      },
    },
    estilo_vida: {
      dieta: 'Normal',
      descripcion_dieta: '',
      suplementos_vitaminas: '',
      frecuencia_ejercicio: '',
      tipo_ejercicio: '',
      fuma: false,
      cigarros_dia: undefined,
      anos_fumando: undefined,
      consume_alcohol: false,
      frecuencia_alcohol: '',
      consume_drogas: false,
      tipo_drogas: '',
      vacunas_completas: false,
      esquema_vacunacion: '',
      horas_sueno: undefined,
      exposicion_toxicos: '',
      notas_adicionales: '',
    },
    historia_ginecologica: undefined,
    motivo_consulta: {
      sintomas_principales: '',
      fecha_inicio_sintomas: '',
      evolucion_sintomas: '',
      automedicacion: '',
    },
    consentimientos: undefined,
    informacion_pago: undefined,
    signos_vitales: undefined,
    exploracion_fisica: undefined,
    diagnosticos: [],
    plan_tratamiento: [],
    indicaciones: undefined,
    evolucion: [],
    estado: 'Borrador',
    notas_privadas: '',
  };
}

// ============================================================================
// CATÁLOGOS
// ============================================================================

export const SEXO_OPCIONES = [
  { value: 'M', label: 'Masculino' },
  { value: 'F', label: 'Femenino' },
  { value: 'O', label: 'Otro' },
];

export const ESTADO_CIVIL_OPCIONES = [
  { value: 'Soltero/a', label: 'Soltero/a' },
  { value: 'Casado/a', label: 'Casado/a' },
  { value: 'Divorciado/a', label: 'Divorciado/a' },
  { value: 'Viudo/a', label: 'Viudo/a' },
  { value: 'Unión libre', label: 'Unión libre' },
];

export const ESCOLARIDAD_OPCIONES = [
  { value: 'Sin estudios', label: 'Sin estudios' },
  { value: 'Primaria', label: 'Primaria' },
  { value: 'Secundaria', label: 'Secundaria' },
  { value: 'Preparatoria', label: 'Preparatoria' },
  { value: 'Licenciatura', label: 'Licenciatura' },
  { value: 'Posgrado', label: 'Posgrado' },
];

export const DIETA_OPCIONES = [
  { value: 'Normal', label: 'Normal' },
  { value: 'Vegetariana', label: 'Vegetariana' },
  { value: 'Vegana', label: 'Vegana' },
  { value: 'Keto', label: 'Keto' },
  { value: 'Diabética', label: 'Diabética' },
  { value: 'Otro', label: 'Otro' },
];

export const TIPO_ALERGENO_OPCIONES = [
  { value: 'Medicamento', label: 'Medicamento' },
  { value: 'Alimento', label: 'Alimento' },
  { value: 'Ambiental', label: 'Ambiental' },
  { value: 'Material', label: 'Material' },
  { value: 'Otro', label: 'Otro' },
];

export const SEVERIDAD_ALERGIA_OPCIONES = [
  { value: 'Leve', label: 'Leve' },
  { value: 'Moderada', label: 'Moderada' },
  { value: 'Grave', label: 'Grave' },
  { value: 'Mortal', label: 'Mortal' },
];

export const PRONOSTICO_OPCIONES = [
  { value: 'Bueno', label: 'Bueno' },
  { value: 'Reservado', label: 'Reservado' },
  { value: 'Malo', label: 'Malo' },
];

export const RESULTADO_EVOLUCION_OPCIONES = [
  { value: 'Mejoría', label: 'Mejoría' },
  { value: 'Sin cambios', label: 'Sin cambios' },
  { value: 'Empeoramiento', label: 'Empeoramiento' },
];

export const METODO_PAGO_OPCIONES = [
  { value: 'Efectivo', label: 'Efectivo' },
  { value: 'Tarjeta Débito', label: 'Tarjeta de Débito' },
  { value: 'Tarjeta Crédito', label: 'Tarjeta de Crédito' },
  { value: 'Transferencia', label: 'Transferencia' },
  { value: 'Cheque', label: 'Cheque' },
  { value: 'Otro', label: 'Otro' },
];

export const TIPO_DIAGNOSTICO_OPCIONES = [
  { value: 'Presuntivo', label: 'Presuntivo' },
  { value: 'Definitivo', label: 'Definitivo' },
  { value: 'Diferencial', label: 'Diferencial' },
];

// Catálogo CIE-10 para Podología
export const CIE10_PODOLOGIA = [
  { code: 'E10.9', description: 'Diabetes mellitus tipo 1 sin complicaciones', category: 'Diabetes' },
  { code: 'E11.9', description: 'Diabetes mellitus tipo 2 sin complicaciones', category: 'Diabetes' },
  { code: 'E11.65', description: 'Diabetes mellitus tipo 2 con hyperglycemia', category: 'Diabetes' },
  { code: 'B35.1', description: 'Tinea unguium (Onicomicosis)', category: 'Infecciones' },
  { code: 'B35.3', description: 'Tinea pedis (Pie de atleta)', category: 'Infecciones' },
  { code: 'B07', description: 'Verugas víricas', category: 'Infecciones' },
  { code: 'M20.1', description: 'Hallux valgus (Juanete)', category: 'Deformidades' },
  { code: 'M20.2', description: 'Hallux rigidus', category: 'Deformidades' },
  { code: 'M20.4', description: 'Otros dedos en martillo (acortados)', category: 'Deformidades' },
  { code: 'M20.5', description: 'Dedos en garra adquiridos', category: 'Deformidades' },
  { code: 'M21.4', description: 'Pie plano (pes planus)', category: 'Deformidades' },
  { code: 'M72.2', description: 'Fascitis plantar', category: 'Tejidos Blandos' },
  { code: 'M77.3', description: 'Espolón calcáneo', category: 'Tejidos Blandos' },
  { code: 'M77.5', description: 'Tendinitis del tibial posterior', category: 'Tejidos Blandos' },
  { code: 'L60.0', description: 'Uña incarnada', category: 'Uñas' },
  { code: 'L84', description: 'Callo y callosidad', category: 'Piel' },
  { code: 'L90.0', description: 'Acantosis nigricans', category: 'Piel' },
  { code: 'L97', description: 'Úlcera de extremidad inferior, no clasificada', category: 'Úlceras' },
  { code: 'L89.0', description: 'Úlcera por presión de grado I', category: 'Úlceras' },
  { code: 'L89.1', description: 'Úlcera por presión de grado II', category: 'Úlceras' },
  { code: 'S91.3', description: 'Herida abierta de pie', category: 'Traumatismos' },
  { code: 'S93.4', description: 'Esguince de tobillo', category: 'Traumatismos' },
  { code: 'S92.0', description: 'Fractura de calcáneo', category: 'Traumatismos' },
  { code: 'G57.1', description: 'Meralgia parestésica', category: 'Neurológicos' },
  { code: 'G56.0', description: 'Síndrome del túnel carpiano', category: 'Neurológicos' },
  { code: 'R20.2', description: 'Parestesia de piel', category: 'Neurológicos' },
  { code: 'I73.9', description: 'Enfermedad vascular periférica no especificada', category: 'Vascular' },
  { code: 'I80.2', description: 'Flebitis y tromboflebitis de vasos profundos', category: 'Vascular' },
];

// Servicios de Podología
export const SERVICIOS_PODOLOGIA = [
  { code: 'CONS', name: 'Consulta de Primera Vez', price: 500, duration: 30 },
  { code: 'SEGP', name: 'Consulta de Seguimiento', price: 350, duration: 20 },
  { code: 'QUIR', name: 'Quiropodia (Corte de uñas)', price: 400, duration: 25 },
  { code: 'QUI2', name: 'Quiropodia Compleja', price: 600, duration: 40 },
  { code: 'ONIC', name: 'Tratamiento de Onicomicosis', price: 800, duration: 30 },
  { code: 'VERU', name: 'Tratamiento de Verrugas', price: 450, duration: 20 },
  { code: 'CALO', name: 'Eliminación de Callos', price: 500, duration: 25 },
  { code: 'ORTO', name: 'Ortesis de Silicona', price: 1200, duration: 45 },
  { code: 'PLANT', name: 'Plantillas Ortopédicas', price: 2500, duration: 60 },
  { code: 'PODO', name: 'Exploración Podológica Completa', price: 700, duration: 40 },
  { code: 'REGI', name: 'Reflexología Podal', price: 600, duration: 45 },
  { code: 'MASA', name: 'Masaje Podal Terapéutico', price: 500, duration: 30 },
  { code: 'CIRC', name: 'Estudio de Marcha/Circulación', price: 900, duration: 45 },
  { code: 'DIAB', name: 'Pie Diabético - Evaluación', price: 800, duration: 40 },
  { code: 'ULCE', name: 'Tratamiento de Úlcera', price: 1000, duration: 45 },
  { code: 'CIRU', name: 'Cirugía Ambulatoria', price: 3500, duration: 90 },
  { code: 'ONIC', name: 'Avulsión Parcial de Uña', price: 1500, duration: 30 },
  { code: 'MATR', name: 'Matriectomía', price: 2000, duration: 45 },
  { code: 'HALL', name: 'Corrección de Hallux Valgus', price: 5000, medida: 120 },
  { code: 'INYE', name: 'Infiltración', price: 800, duration: 15 },
];
