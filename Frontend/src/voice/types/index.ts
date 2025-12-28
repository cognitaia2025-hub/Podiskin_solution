/**
 * Types for Gemini Live Voice Controller - Medical Version
 */

export enum VoiceName {
  Puck = 'Puck',
  Charon = 'Charon',
  Kore = 'Kore',
  Fenrir = 'Fenrir',
  Aoede = 'Aoede'
}

export type LogEntryType = 'user' | 'model' | 'tool' | 'system' | 'error';

export interface LogEntry {
  timestamp: Date;
  message: string;
  type: LogEntryType;
}

// Medical-specific types
export interface VitalSigns {
  peso_kg?: number;
  talla_cm?: number;
  ta_sistolica?: number;
  ta_diastolica?: number;
  frecuencia_cardiaca?: number;
  temperatura_c?: number;
  saturacion_o2?: number;
  glucosa_capilar?: number;
}

export interface ClinicalNote {
  motivo_consulta: string;
  padecimiento_actual?: string;
  exploracion_fisica?: string;
  diagnostico_presuntivo?: string;
  diagnostico_definitivo?: string;
  plan_tratamiento?: string;
  indicaciones_paciente?: string;
}

export interface Allergy {
  tipo_alergeno: 'Medicamento' | 'Alimento' | 'Ambiental' | 'Material' | 'Otro';
  nombre_alergeno: string;
  reaccion?: string;
  severidad?: 'Leve' | 'Moderada' | 'Grave' | 'Mortal';
}

export interface PatientQuery {
  tipo_consulta: 'alergias' | 'antecedentes_medicos' | 'tratamientos_previos' | 
                 'ultima_cita' | 'signos_vitales_historico' | 'pagos_pendientes' | 'datos_contacto';
  filtro_fecha?: string;
}

export interface SummaryRequest {
  tipo_resumen: 'consulta_actual' | 'evolucion_tratamiento' | 'historial_completo';
  formato?: 'breve' | 'detallado' | 'para_paciente';
}

export interface FollowUpSchedule {
  tipo_seguimiento: 'cita_revision' | 'recordatorio_tratamiento' | 'llamada_seguimiento';
  dias_adelante: number;
  notas?: string;
}

export type AppSection = 'signos_vitales' | 'nota_clinica' | 'historial_medico' | 
                         'tratamientos' | 'archivos_multimedia' | 'pagos' | 'evolucion';

// Session management types
export interface SessionConfig {
  patientId: string;
  appointmentId: string;
  userId: string;
}

export interface SessionToken {
  token: string;
  expiresAt: Date;
  sessionId: string;
}

export interface ToolCallResult {
  success: boolean;
  data?: any;
  error?: string;
  message?: string;
}

// Voice manager callbacks
export interface VoiceManagerCallbacks {
  onLog: (message: string, type: LogEntryType) => void;
  onToolCall: (name: string, args: any) => Promise<ToolCallResult>;
  onStatusChange: (isConnected: boolean) => void;
  onError: (error: Error) => void;
  onSessionExpired?: () => void;
}

// Configuration for voice controller
export interface VoiceControllerConfig {
  backendUrl: string;
  enableAudioDebug?: boolean;
  autoReconnect?: boolean;
  maxReconnectAttempts?: number;
}
