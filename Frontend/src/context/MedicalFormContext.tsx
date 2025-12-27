import React, { createContext, useContext, useReducer, useEffect, useCallback, useRef } from 'react';
import { useForm, FormProvider, type UseFormReturn, type FieldPath } from 'react-hook-form';
import type {
  MedicalRecord,
  PersonalInfo,
  Allergy,
  MedicalHistory,
  Lifestyle,
  GynecologicalHistory,
  ConsultationReason,
  VitalSigns,
  PhysicalExam,
  Diagnosis,
  TreatmentPlan,
  Indications,
  Evolution,
  FormMode,
  FormState,
  MedicalFormContextValue,
  Consent,
  PaymentInfo,
  GuidedStep,
  FormSection,
} from '../types/medical';
import {
  FORM_SECTIONS,
  GUIDED_STEPS,
  getProgressPercentage,
  getSectionById,
} from '../utils/formSections';
import { createEmptyMedicalRecord } from '../types/medical';

// ============================================================================
// ESTADO INICIAL Y REDUCER
// ============================================================================

interface MedicalFormAction {
  type: 'SET_FORM_DATA' | 'UPDATE_FIELD' | 'SET_MODE' | 'SET_CURRENT_STEP' | 'MARK_STEP_COMPLETE' |
  'SET_ERRORS' | 'CLEAR_ERRORS' | 'SET_DIRTY' | 'SET_SUBMITTING' | 'SET_SAVING' |
  'SET_LAST_SAVED' | 'SHOW_VALIDATION_ERRORS' | 'RESET_FORM' | 'LOAD_PATIENT';
  payload?: any;
}

const initialFormState: FormState = {
  currentStep: 1,
  completedSteps: [],
  errors: {},
  isDirty: false,
  isSubmitting: false,
  isSaving: false,
  lastSavedAt: null,
  showValidationErrors: false,
};

function formReducer(state: FormState, action: MedicalFormAction): FormState {
  switch (action.type) {
    case 'SET_FORM_DATA':
      return { ...state, ...action.payload };

    case 'UPDATE_FIELD':
      return { ...state, isDirty: true };

    case 'SET_MODE':
      return { ...state };

    case 'SET_CURRENT_STEP':
      return { ...state, currentStep: action.payload };

    case 'MARK_STEP_COMPLETE':
      return {
        ...state,
        completedSteps: state.completedSteps.includes(action.payload)
          ? state.completedSteps
          : [...state.completedSteps, action.payload],
      };

    case 'SET_ERRORS':
      return { ...state, errors: action.payload };

    case 'CLEAR_ERRORS':
      return { ...state, errors: {} };

    case 'SET_DIRTY':
      return { ...state, isDirty: action.payload };

    case 'SET_SUBMITTING':
      return { ...state, isSubmitting: action.payload };

    case 'SET_SAVING':
      return { ...state, isSaving: action.payload };

    case 'SET_LAST_SAVED':
      return { ...state, lastSavedAt: action.payload, isDirty: false };

    case 'SHOW_VALIDATION_ERRORS':
      return { ...state, showValidationErrors: action.payload };

    case 'RESET_FORM':
      return { ...initialFormState, currentStep: 1 };

    default:
      return state;
  }
}

// ============================================================================
// CONTEXTO
// ============================================================================

const MedicalFormContext = createContext<MedicalFormContextValue | null>(null);

// ============================================================================
// HOOK PERSONALIZADO
// ============================================================================

export function useMedicalForm() {
  const context = useContext(MedicalFormContext);
  if (!context) {
    throw new Error('useMedicalForm debe usarse dentro de MedicalFormProvider');
  }
  return context;
}

// ============================================================================
// PROVIDER
// ============================================================================

interface MedicalFormProviderProps {
  children: React.ReactNode;
  patientId?: string;
  podologoId?: string;
  initialData?: Partial<MedicalRecord>;
  autoSaveInterval?: number; // en milisegundos, default 30000
}

export const MedicalFormProvider: React.FC<MedicalFormProviderProps> = ({
  children,
  patientId,
  podologoId,
  initialData,
  autoSaveInterval = 30000,
}) => {
  // Estado del reducer
  const [formState, dispatch] = useReducer(formReducer, initialFormState);

  // Referencia para auto-guardado
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const formRef = useRef<UseFormReturn<MedicalRecord> | null>(null);

  // Datos del paciente actual (mock - vendría de un contexto global)
  const [currentPatient] = React.useState(() => {
    if (patientId) {
      return {
        id: patientId,
        name: initialData?.informacion_personal?.primer_nombre
          ? `${initialData.informacion_personal.primer_nombre} ${initialData.informacion_personal.primer_apellido}`
          : 'Paciente Nuevo',
        phone: initialData?.informacion_personal?.telefono_principal,
        email: initialData?.informacion_personal?.correo_electronico,
      };
    }
    return null;
  });

  // Inicializar formulario con React Hook Form
  const methods = useForm<MedicalRecord>({
    defaultValues: initialData || createEmptyMedicalRecord(patientId || 'unknown', podologoId || 'unknown'),
    mode: 'onChange',
    shouldUnregister: false,
  });

  formRef.current = methods;

  // Auto-guardado
  useEffect(() => {
    if (formState.isDirty && !formState.isSubmitting) {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }

      saveTimeoutRef.current = setTimeout(() => {
        handleAutoSave();
      }, autoSaveInterval);
    }

    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [formState.isDirty, formState.isSubmitting, autoSaveInterval]);

  // Cargar datos guardados localmente al iniciar
  useEffect(() => {
    const savedData = localStorage.getItem(`medical_form_${patientId}`);
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData);
        methods.reset(parsed);
      } catch (error) {
        console.error('Error al cargar datos guardados:', error);
      }
    }
  }, [patientId]);

  // Función de auto-guardado
  const handleAutoSave = useCallback(async () => {
    if (!formRef.current) return;

    dispatch({ type: 'SET_SAVING', payload: true });

    try {
      const formData = formRef.current.getValues();
      localStorage.setItem(`medical_form_${patientId}`, JSON.stringify(formData));
      dispatch({ type: 'SET_LAST_SAVED', payload: new Date() });
    } catch (error) {
      console.error('Error en auto-guardado:', error);
    } finally {
      dispatch({ type: 'SET_SAVING', payload: false });
    }
  }, [patientId]);

  // Actualizar un campo específico usando notación de punto
  const updateFormData = useCallback((path: string, value: any) => {
    if (!formRef.current) return;

    // Usar setValue de react-hook-form para actualizar el campo
    formRef.current.setValue(path as FieldPath<MedicalRecord>, value, {
      shouldDirty: true,
      shouldValidate: false,
    });

    dispatch({ type: 'UPDATE_FIELD' });
  }, []);

  // Obtener valor de un campo
  const getFieldValue = useCallback((path: string): any => {
    if (!formRef.current) return undefined;
    return formRef.current.getValues(path as FieldPath<MedicalRecord>);
  }, []);

  // Cambiar modo de llenado
  const setFormMode = useCallback((mode: FormMode) => {
    dispatch({ type: 'SET_MODE', payload: mode });
  }, []);

  // Navegación en modo guiado
  const setCurrentStep = useCallback((step: number) => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: step });
  }, []);

  // Marcar paso como completado
  const markStepComplete = useCallback((stepId: number) => {
    dispatch({ type: 'MARK_STEP_COMPLETE', payload: stepId });
  }, []);

  // Calcular IMC
  const calculateIMC = useCallback((peso: number, talla: number): number => {
    if (!peso || !talla || peso <= 0 || talla <= 0) return 0;
    const tallaMetros = talla / 100;
    const imc = peso / (tallaMetros * tallaMetros);
    return Math.round(imc * 10) / 10;
  }, []);

  // Validar un campo individual
  const validateField = useCallback((fieldName: string, value: any): string | null => {
    if (!formRef.current) return null;

    // Validaciones básicas según el tipo de campo
    if (fieldName.includes('telefono')) {
      if (value && !/^[0-9]{10}$/.test(value)) {
        return 'El teléfono debe tener 10 dígitos';
      }
    }

    if (fieldName.includes('correo') || fieldName.includes('email')) {
      if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        return 'Correo electrónico inválido';
      }
    }

    if (fieldName.includes('peso') && (value < 0 || value > 300)) {
      return 'Peso inválido';
    }

    if (fieldName.includes('talla') && (value < 0 || value > 250)) {
      return 'Talla inválida';
    }

    return null;
  }, []);

  // Validar formulario completo
  const validateForm = useCallback((): boolean => {
    if (!formRef.current) return false;

    const errors = formRef.current.formState.errors;
    const hasErrors = Object.keys(errors).length > 0;

    if (hasErrors) {
      dispatch({ type: 'SHOW_VALIDATION_ERRORS', payload: true });
    }

    return !hasErrors;
  }, []);

  // Guardar formulario
  const saveForm = useCallback(async (): Promise<void> => {
    if (!formRef.current) return;

    dispatch({ type: 'SET_SAVING', payload: true });

    try {
      // Simular llamada a API
      await new Promise(resolve => setTimeout(resolve, 1000));

      const formData = formRef.current.getValues();
      localStorage.setItem(`medical_form_${patientId}`, JSON.stringify(formData));
      dispatch({ type: 'SET_LAST_SAVED', payload: new Date() });
    } catch (error) {
      console.error('Error al guardar:', error);
      throw error;
    } finally {
      dispatch({ type: 'SET_SAVING', payload: false });
    }
  }, [patientId]);

  // Enviar formulario
  const submitForm = useCallback(async (): Promise<void> => {
    if (!formRef.current) return;

    const isValid = validateForm();
    if (!isValid) {
      throw new Error('El formulario tiene errores. Por favor revísalo.');
    }

    dispatch({ type: 'SET_SUBMITTING', payload: true });

    try {
      // Simular envío a API
      await new Promise(resolve => setTimeout(resolve, 2000));

      const formData = formRef.current.getValues();
      console.log('Formulario enviado:', formData);

      // Limpiar auto-guardado
      localStorage.removeItem(`medical_form_${patientId}`);
    } catch (error) {
      console.error('Error al enviar:', error);
      throw error;
    } finally {
      dispatch({ type: 'SET_SUBMITTING', payload: false });
    }
  }, [patientId, validateForm]);

  // Reiniciar formulario
  const resetForm = useCallback(() => {
    methods.reset(createEmptyMedicalRecord(patientId || 'unknown', podologoId || 'unknown'));
    dispatch({ type: 'RESET_FORM' });
    localStorage.removeItem(`medical_form_${patientId}`);
  }, [patientId, podologoId, methods]);

  // Obtener porcentaje de progreso
  const getProgressPercentageFn = useCallback((): number => {
    return getProgressPercentage(formState.completedSteps);
  }, [formState.completedSteps]);

  // Valor del contexto
  const contextValue: MedicalFormContextValue = {
    formData: formRef.current?.getValues() || {} as Partial<MedicalRecord>,
    formState,
    formMode: formState.currentStep > 0 ? 'guided' : 'free', // Simplificado
    currentPatient,
    updateFormData,
    setFormMode,
    setCurrentStep,
    markStepComplete,
    validateField,
    validateForm,
    saveForm,
    submitForm,
    resetForm,
    getFieldValue,
    calculateIMC,
    getProgressPercentage: getProgressPercentageFn,
  };

  return (
    <MedicalFormContext.Provider value={contextValue}>
      <FormMethodsContext.Provider value={methods}>
        <FormProvider {...methods}>
          {children}
        </FormProvider>
      </FormMethodsContext.Provider>
    </MedicalFormContext.Provider>
  );
};

// ============================================================================
// CONTEXTO ADICIONAL PARA METHODS
// ============================================================================

const FormMethodsContext = createContext<UseFormReturn<MedicalRecord> | null>(null);

export function useFormMethods(): UseFormReturn<MedicalRecord> {
  const context = useContext(FormMethodsContext);
  if (!context) {
    throw new Error('useFormMethods debe usarse dentro de MedicalFormProvider');
  }
  return context;
}

// ============================================================================
// COMPONENTES AUXILIARES
// ============================================================================

// Componente para acceder a los métodos del formulario
export const FormMethodsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const methods = useFormMethods();
  return <>{children}</>;
};

// Hook para usar en modo guiado
export function useGuidedMode() {
  const { formState, setCurrentStep, markStepComplete, getFieldValue } = useMedicalForm();

  const currentGuidedStep = GUIDED_STEPS.find(step => step.order === formState.currentStep);
  const nextStep = GUIDED_STEPS.find(step => step.order === formState.currentStep + 1);
  const previousStep = GUIDED_STEPS.find(step => step.order === formState.currentStep - 1);

  const goToNextStep = useCallback(() => {
    if (nextStep) {
      setCurrentStep(nextStep.order);
    }
  }, [nextStep, setCurrentStep]);

  const goToPreviousStep = useCallback(() => {
    if (previousStep) {
      setCurrentStep(previousStep.order);
    }
  }, [previousStep, setCurrentStep]);

  const goToStep = useCallback((stepOrder: number) => {
    setCurrentStep(stepOrder);
  }, [setCurrentStep]);

  const completeCurrentStep = useCallback(() => {
    markStepComplete(formState.currentStep);
    goToNextStep();
  }, [formState.currentStep, markStepComplete, goToNextStep]);

  const isStepCompleted = useCallback((stepOrder: number) => {
    return formState.completedSteps.includes(stepOrder);
  }, [formState.completedSteps]);

  return {
    currentStep: formState.currentStep,
    currentStepData: currentGuidedStep,
    nextStep,
    previousStep,
    completedSteps: formState.completedSteps,
    totalSteps: GUIDED_STEPS.length,
    goToNextStep,
    goToPreviousStep,
    goToStep,
    completeCurrentStep,
    markStepComplete,
    isStepCompleted,
    getFieldValue,
    progress: getProgressPercentage(formState.completedSteps),
  };
}

// Hook para usar en modo libre
export function useFreeMode() {
  const { formData, formState } = useMedicalForm();

  const getSectionProgress = useCallback((sectionId: string): number => {
    const section = getSectionById(sectionId);
    if (!section) return 0;

    // Calcular progreso basado en campos completados
    let completed = 0;
    let total = 0;

    section.fields.forEach(field => {
      if (field.dependsOn) {
        const depValue = getNestedValue(formData, field.dependsOn.field);
        if (depValue !== field.dependsOn.value) return;
      }

      total += 1;
      const fieldValue = getNestedValue(formData, field.name);
      if (fieldValue && fieldValue !== '' &&
        !(Array.isArray(fieldValue) && fieldValue.length === 0)) {
        completed += 1;
      }
    });

    return total > 0 ? Math.round((completed / total) * 100) : 0;
  }, [formData]);

  const getAllSectionsProgress = useCallback((): Record<string, number> => {
    const progress: Record<string, number> = {};
    FORM_SECTIONS.forEach(section => {
      progress[section.id] = getSectionProgress(section.id);
    });
    return progress;
  }, [getSectionProgress]);

  return {
    sections: FORM_SECTIONS,
    formData,
    getSectionProgress,
    getAllSectionsProgress,
  };
}

// Utilidad para obtener valor anidado
function getNestedValue(obj: any, path: string): any {
  return path.split('.').reduce((acc, part) => acc && acc[part], obj);
}

export default MedicalFormContext;
