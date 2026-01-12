import React, { useState, useEffect } from 'react';
import { clsx } from 'clsx';
import { useSearchParams } from 'react-router-dom';
import type { MedicalRecord, FormMode } from '../types/medical';
import { MedicalFormProvider, useMedicalForm } from '../context/MedicalFormContext';
import { useGlobalContext } from '../context/GlobalContext';
import { getPatientById } from '../services/patientService';
import PatientSidebar from '../components/medical/PatientSidebar';
import MedicalRecordForm from '../components/medical/MedicalRecordForm';
import MayaAssistant from '../components/medical/MayaAssistant';
import EvolutionSidebar from '../components/medical/EvolutionSidebar';
import { Save, Send, Loader2 } from 'lucide-react';

// Componente interno que usa el contexto
const MedicalAttentionContent: React.FC = () => {
  const { formState, saveForm, submitForm } = useMedicalForm();
  const { selectedPatient } = useGlobalContext();
  const [formMode, setFormMode] = useState<FormMode>('free');
  const [rightPanelTab, setRightPanelTab] = useState<'maya' | 'evolution'>('maya');

  // Use selectedPatient from global context if available, otherwise use mock data
  const patientData: Partial<MedicalRecord> = selectedPatient ? {
    id_paciente: selectedPatient.id,
    id_podologo: '1',
    informacion_personal: {
      primer_nombre: selectedPatient.name.split(' ')[0] || 'Paciente',
      segundo_nombre: '',
      primer_apellido: selectedPatient.name.split(' ')[1] || '',
      segundo_apellido: selectedPatient.name.split(' ')[2] || '',
      fecha_nacimiento: selectedPatient.fecha_nacimiento || '',
      sexo: 'M',
      curp: selectedPatient.curp || '',
      estado_civil: selectedPatient.estado_civil || '',
      escolaridad: '',
      ocupacion: selectedPatient.ocupacion || '',
      religion: '',
      calle: '',
      numero_exterior: '',
      colonia: '',
      ciudad: '',
      estado: '',
      codigo_postal: '',
      telefono_principal: selectedPatient.phone || '',
      telefono_secundario: '',
      correo_electronico: selectedPatient.email || '',
      como_supo_de_nosotros: '',
    },
  } : {
    id_paciente: 'p1',
    id_podologo: '1',
    informacion_personal: {
      primer_nombre: 'Juan',
      segundo_nombre: 'Carlos',
      primer_apellido: 'Pérez',
      segundo_apellido: 'García',
      fecha_nacimiento: '1985-03-15',
      sexo: 'M',
      curp: 'PEGJ850315HDFRNN00',
      estado_civil: 'Casado',
      escolaridad: 'Licenciatura',
      ocupacion: 'Ingeniero',
      religion: 'Católica',
      calle: 'Av. Principal',
      numero_exterior: '123',
      colonia: 'Centro',
      ciudad: 'México',
      estado: 'CDMX',
      codigo_postal: '01000',
      telefono_principal: '555-123-4567',
      telefono_secundario: '555-987-6543',
      correo_electronico: 'juan.perez@email.com',
      como_supo_de_nosotros: 'Recomendación',
    },
    alergias: [
      {
        id: '1',
        tipo_alergeno: 'Medicamento',
        nombre_alergeno: 'Penicilina',
        reaccion: 'Urticaria y dificultad respiratoria',
        severidad: 'Grave',
      },
      {
        id: '2',
        tipo_alergeno: 'Alimento',
        nombre_alergeno: 'Mariscos',
        reaccion: 'Hinchazón',
        severidad: 'Moderada',
      },
    ],
    estilo_vida: {
      dieta: 'Normal',
      fuma: false,
      consume_alcohol: false,
      consume_drogas: false,
      vacunas_completas: true,
      frecuencia_ejercicio: '3-4 veces por semana',
      horas_sueno: 7,
    },
    motivo_consulta: {
      sintomas_principales: 'Dolor en talón derecho al caminar, especialmente por las mañanas',
      fecha_inicio_sintomas: 'Hace 2 semanas',
      evolucion_sintomas: 'Ha empeorado gradualmente',
      automedicacion: 'Ibuprofeno 400mg cada 8 horas',
    },
  };

  const handleSave = async () => {
    try {
      await saveForm();
    } catch (error) {
      console.error('Error al guardar:', error);
    }
  };

  const handleSubmit = async () => {
    try {
      await submitForm();
    } catch (error) {
      console.error('Error al enviar:', error);
    }
  };

  const handleModeChange = (mode: FormMode) => {
    setFormMode(mode);
  };

  const patientName = patientData.informacion_personal
    ? `${patientData.informacion_personal.primer_nombre} ${patientData.informacion_personal.primer_apellido}`
    : 'Nuevo Paciente';

  return (
    <div className="flex flex-col h-full bg-gray-100 overflow-hidden">
      {/* Medical Toolbar - integrated into global layout */}
      <div className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shrink-0">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">{patientName}</h2>
          <p className="text-xs text-gray-500">Expediente Médico</p>
        </div>
        <div className="flex items-center gap-2">
          {/* Mode selector */}
          <div className="flex rounded-md border border-gray-300 overflow-hidden">
            <button
              onClick={() => handleModeChange('free')}
              className={clsx(
                'px-3 py-1 text-sm font-medium transition-colors',
                formMode === 'free'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              )}
            >
              Libre
            </button>
            <button
              onClick={() => handleModeChange('guided')}
              className={clsx(
                'px-3 py-1 text-sm font-medium transition-colors border-l border-gray-300',
                formMode === 'guided'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              )}
            >
              Guiado
            </button>
          </div>

          {/* Action buttons */}
          <button
            onClick={handleSave}
            disabled={!formState.isDirty || formState.isSaving}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save className="w-4 h-4" />
            Guardar
          </button>
          <button
            onClick={handleSubmit}
            disabled={formState.isSubmitting}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-md text-sm font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
            Finalizar
          </button>
        </div>
      </div>

      {/* Main Content - 3 Column Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Column - Patient Info */}
        <aside className="w-80 flex-shrink-0 hidden lg:block border-r border-gray-200">
          <PatientSidebar patientData={patientData} className="h-full" />
        </aside>

        {/* Center Column - Form */}
        <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <MedicalRecordForm
            className="flex-1"
            initialMode={formMode}
          />
        </main>

        {/* Right Column - Maya/Evolution */}
        <aside className="w-96 flex-shrink-0 hidden xl:block border-l border-gray-200">
          {/* Toggle entre Maya y Evolución */}
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setRightPanelTab('maya')}
              className={clsx(
                'flex-1 px-4 py-2 text-sm font-medium transition-colors',
                rightPanelTab === 'maya'
                  ? 'bg-white text-gray-900 border-b-2 border-teal-500'
                  : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
              )}
            >
              Maya IA
            </button>
            <button
              onClick={() => setRightPanelTab('evolution')}
              className={clsx(
                'flex-1 px-4 py-2 text-sm font-medium transition-colors',
                rightPanelTab === 'evolution'
                  ? 'bg-white text-gray-900 border-b-2 border-teal-500'
                  : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
              )}
            >
              Evolución
            </button>
          </div>

          {/* Panel content */}
          <div className="h-[calc(100%-44px)]">
            {rightPanelTab === 'maya' ? (
              <MayaAssistant className="h-full rounded-none border-0" />
            ) : (
              <EvolutionSidebar className="h-full rounded-none border-0" />
            )}
          </div>
        </aside>
      </div>
    </div>
  );
};

// Componente principal exportado
const MedicalAttention: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [initialData, setInitialData] = useState<Partial<MedicalRecord> | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadAppointmentData = async () => {
      const citaId = searchParams.get('citaId');
      const pacienteId = searchParams.get('pacienteId');
      const podologoId = searchParams.get('podologoId');
      const tipoCita = searchParams.get('tipoCita');

      // Si no hay parámetros, usar datos por defecto
      if (!citaId || !pacienteId) {
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        // Cargar datos del paciente desde el backend
        const patient = await getPatientById(pacienteId);

        // Preparar datos iniciales para el formulario
        const data: Partial<MedicalRecord> = {
          id_paciente: pacienteId,
          id_podologo: podologoId || '1',
          informacion_personal: {
            primer_nombre: patient.name.split(' ')[0] || '',
            segundo_nombre: patient.name.split(' ')[1] || '',
            primer_apellido: patient.name.split(' ')[2] || patient.name.split(' ')[1] || '',
            segundo_apellido: patient.name.split(' ')[3] || '',
            fecha_nacimiento: patient.fecha_nacimiento || '',
            sexo: 'M', // Por defecto, debería venir del backend
            curp: patient.curp || '',
            estado_civil: patient.estado_civil || '',
            escolaridad: '',
            ocupacion: patient.ocupacion || '',
            religion: '',
            calle: '',
            numero_exterior: '',
            colonia: '',
            ciudad: '',
            estado: '',
            codigo_postal: '',
            telefono_principal: patient.phone || '',
            telefono_secundario: '',
            correo_electronico: patient.email || '',
            como_supo_de_nosotros: '',
          },
          motivo_consulta: {
            sintomas_principales: `Cita programada: ${tipoCita || 'Consulta'}`,
            fecha_inicio_sintomas: '',
            evolucion_sintomas: '',
            automedicacion: '',
          },
        };

        setInitialData(data);
      } catch (err) {
        console.error('Error cargando datos de cita:', err);
        setError('No se pudieron cargar los datos del paciente. Usando datos por defecto.');
      } finally {
        setIsLoading(false);
      }
    };

    loadAppointmentData();
  }, [searchParams]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-100">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-primary-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600 font-medium">Cargando datos del paciente...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-100">
        <div className="bg-white p-6 rounded-lg shadow-md max-w-md">
          <div className="text-amber-600 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <p className="text-gray-700 text-center mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="w-full px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <MedicalFormProvider
      patientId={searchParams.get('pacienteId') || 'p1'}
      podologoId={searchParams.get('podologoId') || '1'}
      initialData={initialData}
      autoSaveInterval={30000}
    >
      <MedicalAttentionContent />
    </MedicalFormProvider>
  );
};

export default MedicalAttention;
