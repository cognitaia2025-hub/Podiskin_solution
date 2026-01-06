/**
 * Medical Attention Page
 * 
 * Página principal para atención médica (podólogos).
 * Integra el modal de selección con el formulario médico existente.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { clsx } from 'clsx';
import type { FormMode } from '../../types/medical';
import { MedicalFormProvider, useMedicalForm } from '../../context/MedicalFormContext';
import PatientSelectionModal from '../../components/medical/PatientSelectionModal';
import PatientSidebar from '../../components/medical/PatientSidebar';
import MedicalRecordForm from '../../components/medical/MedicalRecordForm';
import MayaAssistant from '../../components/medical/MayaAssistant';
import EvolutionSidebar from '../../components/medical/EvolutionSidebar';
import { getMedicalRecord } from '../../services/medicalRecordsService';
import type { MedicalRecord } from '../../services/medicalRecordsService';
import { Save, Send } from 'lucide-react';

// Componente interno que usa el contexto del formulario
const MedicalAttentionContent: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { formState, saveForm, submitForm } = useMedicalForm();
  
  const [showPatientModal, setShowPatientModal] = useState(true);
  const [selectedPatientId, setSelectedPatientId] = useState<number | null>(null);
  const [medicalRecord, setMedicalRecord] = useState<MedicalRecord | null>(null);
  const [loading, setLoading] = useState(false);
  const [formMode, setFormMode] = useState<FormMode>('free');
  const [rightPanelTab, setRightPanelTab] = useState<'maya' | 'evolution'>('maya');

  // Verificar si viene un patientId por URL (desde Expedientes Médicos)
  useEffect(() => {
    const patientIdFromUrl = searchParams.get('patientId');
    if (patientIdFromUrl) {
      const id = parseInt(patientIdFromUrl);
      if (!isNaN(id)) {
        setSelectedPatientId(id);
        setShowPatientModal(false);
      }
    }
  }, [searchParams]);

  useEffect(() => {
    if (selectedPatientId) {
      loadMedicalRecord(selectedPatientId);
    }
  }, [selectedPatientId]);

  const loadMedicalRecord = async (patientId: number) => {
    setLoading(true);
    try {
      const record = await getMedicalRecord(patientId);
      setMedicalRecord(record);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPatient = (patientId: number) => {
    setSelectedPatientId(patientId);
    setShowPatientModal(false);
  };

  const handleSave = async () => {
    try {
      await saveForm();
      // TODO: Mostrar notificación de éxito
    } catch (error) {
      console.error('Error al guardar:', error);
      // TODO: Mostrar notificación de error
    }
  };

  const handleSubmit = async () => {
    try {
      await submitForm();
      // TODO: Mostrar notificación de éxito
      // Volver al modal
      handleBack();
    } catch (error) {
      console.error('Error al enviar:', error);
      // TODO: Mostrar notificación de error
    }
  };

  const handleModeChange = (mode: FormMode) => {
    setFormMode(mode);
  };

  const handleBack = () => {
    setShowPatientModal(true);
    setSelectedPatientId(null);
    setMedicalRecord(null);
  };

  const patientName = medicalRecord?.paciente_nombre || 'Nuevo Paciente';

  // Convertir el formato de MedicalRecord (API) a MedicalRecord (tipo del formulario)
  // Por ahora usamos datos básicos, luego se puede expandir
  const patientDataForForm = medicalRecord ? {
    id_paciente: selectedPatientId?.toString() || '',
    id_podologo: '1', // TODO: Obtener del usuario actual
    informacion_personal: {
      primer_nombre: medicalRecord.paciente_nombre?.split(' ')[0] || '',
      segundo_nombre: '',
      primer_apellido: medicalRecord.paciente_nombre?.split(' ')[1] || '',
      segundo_apellido: medicalRecord.paciente_nombre?.split(' ')[2] || '',
      fecha_nacimiento: medicalRecord.fecha_nacimiento || '',
      sexo: medicalRecord.sexo || 'M',
      curp: '',
      estado_civil: '',
      escolaridad: '',
      ocupacion: '',
      religion: '',
      calle: '',
      numero_exterior: '',
      colonia: '',
      ciudad: '',
      estado: '',
      codigo_postal: '',
      telefono_principal: medicalRecord.telefono || '',
      telefono_secundario: '',
      correo_electronico: medicalRecord.email || '',
      como_supo_de_nosotros: '',
    },
    alergias: medicalRecord.alergias?.map((a: any, idx: number) => ({
      id: idx.toString(),
      tipo_alergeno: a.tipo || 'Medicamento',
      nombre_alergeno: a.sustancia,
      reaccion: a.reaccion,
      severidad: a.severidad,
    })) || [],
  } : null;

  if (showPatientModal || !selectedPatientId) {
    return (
      <PatientSelectionModal
        isOpen={true}
        onClose={() => navigate('/')}
        onSelectPatient={handleSelectPatient}
      />
    );
  }

  if (loading || !patientDataForForm) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-100 overflow-hidden">
      {/* Compact Header con nombre del paciente y acciones */}
      <div className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">{patientName}</h1>
          <p className="text-sm text-gray-500">Expediente Médico • ID: #{selectedPatientId}</p>
        </div>
        <div className="flex items-center gap-2">
          {/* Selector de modo */}
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
          
          {/* Botones de acción */}
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
          <button
            onClick={handleBack}
            className="px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
          >
            Cambiar Paciente
          </button>
        </div>
      </div>

      {/* Contenido Principal - Layout de 3 Columnas */}
      <div className="flex-1 flex overflow-hidden">
        {/* Columna Izquierda - Info del Paciente */}
        <aside className="w-80 flex-shrink-0 hidden lg:block border-r border-gray-200">
          <PatientSidebar patientData={patientDataForForm} className="h-full" />
        </aside>

        {/* Columna Central - Formulario */}
        <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <MedicalRecordForm
            className="flex-1"
            initialMode={formMode}
          />
        </main>

        {/* Columna Derecha - Maya/Evolución */}
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

          {/* Contenido del panel */}
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

// Componente principal exportado con Provider
const MedicalAttentionPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const patientId = searchParams.get('patientId') || 'p1';
  
  return (
    <MedicalFormProvider
      patientId={patientId}
      podologoId="1"
      autoSaveInterval={30000}
    >
      <MedicalAttentionContent />
    </MedicalFormProvider>
  );
};

export default MedicalAttentionPage;
