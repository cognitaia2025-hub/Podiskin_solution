/**
 * Tipos Unificados del Sistema
 * =============================
 * Centraliza todos los modelos de datos para evitar duplicación
 */

// ========================================================================
// PACIENTE - Modelo Unificado
// ========================================================================

export interface PatientUnified {
  // Identificación
  id: number;
  nombre: string;
  apellidos: string;
  nombre_completo?: string; // Computed field
  
  // Contacto
  email?: string;
  telefono?: string;
  telefono_emergencia?: string;
  
  // Información personal
  fecha_nacimiento?: string;
  edad?: number; // Computed field
  genero?: 'Masculino' | 'Femenino' | 'Otro';
  
  // Dirección
  direccion?: string;
  ciudad?: string;
  estado?: string;
  codigo_postal?: string;
  
  // Información médica
  alergias?: string[];
  condiciones_medicas?: string[];
  medicamentos?: string[];
  notas_medicas?: string;
  
  // Metadata
  fecha_registro: string;
  ultimo_acceso?: string;
  activo: boolean;
  
  // Relaciones
  expediente_id?: number;
  citas?: AppointmentUnified[];
}

// ========================================================================
// CITA - Modelo Unificado
// ========================================================================

export interface AppointmentUnified {
  id: number;
  
  // Paciente
  paciente_id: number;
  paciente?: PatientUnified;
  
  // Podólogo
  podologo_id: number;
  podologo_nombre?: string;
  
  // Fecha y hora
  fecha: string;
  hora_inicio: string;
  hora_fin: string;
  duracion_minutos?: number;
  
  // Detalles
  tipo: 'consulta' | 'seguimiento' | 'urgencia' | 'cirugia';
  motivo?: string;
  notas?: string;
  
  // Estado
  estado: 'pendiente' | 'confirmada' | 'en_curso' | 'completada' | 'cancelada';
  
  // Metadata
  fecha_creacion: string;
  fecha_modificacion?: string;
  cancelada_por?: string;
  razon_cancelacion?: string;
}

// ========================================================================
// EXPEDIENTE MÉDICO - Modelo Unificado
// ========================================================================

export interface MedicalRecordUnified {
  id: number;
  paciente_id: number;
  
  // Historia clínica
  antecedentes_personales?: string;
  antecedentes_familiares?: string;
  alergias: string[];
  medicamentos_actuales: string[];
  
  // Evaluación física
  signos_vitales?: {
    presion_arterial?: string;
    frecuencia_cardiaca?: number;
    temperatura?: number;
    peso?: number;
    altura?: number;
  };
  
  // Diagnóstico
  diagnostico_principal?: string;
  diagnosticos_secundarios?: string[];
  
  // Tratamiento
  plan_tratamiento?: string;
  tratamientos: TreatmentUnified[];
  
  // Metadata
  fecha_creacion: string;
  ultima_actualizacion: string;
  creado_por: string;
  actualizado_por?: string;
}

// ========================================================================
// TRATAMIENTO - Modelo Unificado
// ========================================================================

export interface TreatmentUnified {
  id: number;
  expediente_id: number;
  
  // Detalles
  tipo: string;
  descripcion: string;
  fecha: string;
  
  // Resultados
  observaciones?: string;
  imagenes?: string[];
  
  // Metadata
  realizado_por: string;
  fecha_creacion: string;
}

// ========================================================================
// PAGO - Modelo Unificado
// ========================================================================

export interface PaymentUnified {
  id: number;
  
  // Paciente y cita
  paciente_id: number;
  cita_id?: number;
  
  // Monto
  monto: number;
  moneda: 'MXN' | 'USD';
  
  // Método de pago
  metodo_pago: 'efectivo' | 'tarjeta' | 'transferencia';
  
  // Estado
  estado: 'pendiente' | 'pagado' | 'cancelado';
  
  // Facturación
  requiere_factura: boolean;
  factura_emitida: boolean;
  factura_id?: string;
  
  // Metadata
  fecha_pago?: string;
  fecha_creacion: string;
  registrado_por: string;
  
  // Notas
  concepto?: string;
  notas?: string;
}

// ========================================================================
// HELPER FUNCTIONS
// ========================================================================

export const unifiedHelpers = {
  // Calcular nombre completo
  getFullName: (patient: PatientUnified): string => {
    return `${patient.nombre} ${patient.apellidos}`.trim();
  },
  
  // Calcular edad
  calculateAge: (fecha_nacimiento: string): number => {
    const today = new Date();
    const birthDate = new Date(fecha_nacimiento);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age;
  },
  
  // Formatear fecha
  formatDate: (date: string): string => {
    return new Date(date).toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  },
  
  // Formatear hora
  formatTime: (time: string): string => {
    return new Date(`2000-01-01T${time}`).toLocaleTimeString('es-MX', {
      hour: '2-digit',
      minute: '2-digit',
    });
  },
};

export default {
  PatientUnified,
  AppointmentUnified,
  MedicalRecordUnified,
  TreatmentUnified,
  PaymentUnified,
  unifiedHelpers,
};
