/**
 * Schemas de Validación Centralizados
 * ====================================
 * Usa Zod para validar todos los formularios del sistema
 */

import { z } from 'zod';

// ========================================================================
// PACIENTE
// ========================================================================

export const patientSchema = z.object({
  nombre: z.string()
    .min(2, 'El nombre debe tener al menos 2 caracteres')
    .max(50, 'El nombre no puede exceder 50 caracteres')
    .regex(/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/, 'Solo se permiten letras'),
  
  apellidos: z.string()
    .min(2, 'Los apellidos deben tener al menos 2 caracteres')
    .max(50, 'Los apellidos no pueden exceder 50 caracteres')
    .regex(/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/, 'Solo se permiten letras'),
  
  email: z.string()
    .email('Email inválido')
    .optional()
    .or(z.literal('')),
  
  telefono: z.string()
    .regex(/^\d{10}$/, 'El teléfono debe tener 10 dígitos')
    .optional()
    .or(z.literal('')),
  
  fecha_nacimiento: z.string()
    .refine((date) => {
      const birthDate = new Date(date);
      const today = new Date();
      const age = today.getFullYear() - birthDate.getFullYear();
      return age >= 0 && age <= 120;
    }, 'Fecha de nacimiento inválida'),
  
  genero: z.enum(['Masculino', 'Femenino', 'Otro']).optional(),
  
  direccion: z.string().max(200).optional(),
  ciudad: z.string().max(100).optional(),
  estado: z.string().max(100).optional(),
  codigo_postal: z.string().regex(/^\d{5}$/, 'Código postal inválido').optional().or(z.literal('')),
});

export type PatientFormData = z.infer<typeof patientSchema>;

// ========================================================================
// CITA
// ========================================================================

export const appointmentSchema = z.object({
  paciente_id: z.number().int().positive('Debe seleccionar un paciente'),
  
  podologo_id: z.number().int().positive('Debe seleccionar un podólogo'),
  
  fecha: z.string()
    .refine((date) => {
      const appointmentDate = new Date(date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      return appointmentDate >= today;
    }, 'La fecha no puede ser anterior a hoy'),
  
  hora_inicio: z.string()
    .regex(/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/, 'Formato de hora inválido (HH:MM)'),
  
  hora_fin: z.string()
    .regex(/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/, 'Formato de hora inválido (HH:MM)'),
  
  tipo: z.enum(['consulta', 'seguimiento', 'urgencia', 'cirugia']),
  
  motivo: z.string().max(500, 'El motivo no puede exceder 500 caracteres').optional(),
  
  notas: z.string().max(1000, 'Las notas no pueden exceder 1000 caracteres').optional(),
}).refine((data) => {
  const inicio = new Date(`2000-01-01T${data.hora_inicio}`);
  const fin = new Date(`2000-01-01T${data.hora_fin}`);
  return fin > inicio;
}, {
  message: 'La hora de fin debe ser posterior a la hora de inicio',
  path: ['hora_fin'],
});

export type AppointmentFormData = z.infer<typeof appointmentSchema>;

// ========================================================================
// PAGO
// ========================================================================

export const paymentSchema = z.object({
  paciente_id: z.number().int().positive('Debe seleccionar un paciente'),
  
  cita_id: z.number().int().positive().optional(),
  
  monto: z.number()
    .positive('El monto debe ser mayor a 0')
    .max(100000, 'El monto no puede exceder $100,000'),
  
  metodo_pago: z.enum(['efectivo', 'tarjeta', 'transferencia']),
  
  requiere_factura: z.boolean(),
  
  concepto: z.string()
    .min(3, 'El concepto debe tener al menos 3 caracteres')
    .max(200, 'El concepto no puede exceder 200 caracteres')
    .optional(),
  
  notas: z.string().max(500, 'Las notas no pueden exceder 500 caracteres').optional(),
});

export type PaymentFormData = z.infer<typeof paymentSchema>;

// ========================================================================
// EXPEDIENTE MÉDICO
// ========================================================================

export const medicalRecordSchema = z.object({
  antecedentes_personales: z.string().max(2000).optional(),
  antecedentes_familiares: z.string().max(2000).optional(),
  
  alergias: z.array(z.string()).optional(),
  medicamentos_actuales: z.array(z.string()).optional(),
  
  presion_arterial: z.string()
    .regex(/^\d{2,3}\/\d{2,3}$/, 'Formato inválido (ej: 120/80)')
    .optional()
    .or(z.literal('')),
  
  frecuencia_cardiaca: z.number().int().min(40).max(200).optional(),
  temperatura: z.number().min(35).max(42).optional(),
  peso: z.number().positive().max(500).optional(),
  altura: z.number().positive().max(250).optional(),
  
  diagnostico_principal: z.string().max(500).optional(),
  plan_tratamiento: z.string().max(2000).optional(),
});

export type MedicalRecordFormData = z.infer<typeof medicalRecordSchema>;

// ========================================================================
// USUARIO / LOGIN
// ========================================================================

export const loginSchema = z.object({
  username: z.string()
    .min(3, 'El usuario debe tener al menos 3 caracteres')
    .max(50, 'El usuario no puede exceder 50 caracteres'),
  
  password: z.string()
    .min(8, 'La contraseña debe tener al menos 8 caracteres')
    .max(100, 'La contraseña no puede exceder 100 caracteres'),
});

export type LoginFormData = z.infer<typeof loginSchema>;

export const changePasswordSchema = z.object({
  currentPassword: z.string().min(1, 'Ingrese la contraseña actual'),
  
  newPassword: z.string()
    .min(8, 'La contraseña debe tener al menos 8 caracteres')
    .regex(/[A-Z]/, 'Debe contener al menos una mayúscula')
    .regex(/[a-z]/, 'Debe contener al menos una minúscula')
    .regex(/[0-9]/, 'Debe contener al menos un número'),
  
  confirmPassword: z.string(),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: 'Las contraseñas no coinciden',
  path: ['confirmPassword'],
});

export type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

// ========================================================================
// EXPORTS
// ========================================================================

export default {
  patientSchema,
  appointmentSchema,
  paymentSchema,
  medicalRecordSchema,
  loginSchema,
  changePasswordSchema,
};
