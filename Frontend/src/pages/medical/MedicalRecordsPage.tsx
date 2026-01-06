/**
 * Medical Records Page
 * 
 * Página de expedientes médicos (solo lectura para staff).
 * Muestra la misma información que MedicalAttentionPage pero deshabilitada.
 * Podólogos y admins pueden editar usando el botón "Editar".
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FileText, 
  Edit2, 
  AlertCircle, 
  User, 
  Activity,
  Heart,
  Stethoscope,
  ClipboardList,
  FileImage,
  History,
  Loader2,
  ChevronLeft,
  Lock
} from 'lucide-react';
import { useAuth } from '../../auth/AuthContext';
import PatientSelectionModal from '../../components/medical/PatientSelectionModal';
import type { MedicalRecord } from '../../services/medicalRecordsService';
import { getMedicalRecord } from '../../services/medicalRecordsService';

type TabId = 'identificacion' | 'alergias' | 'antecedentes' | 'estilo_vida' | 'ginecologia' | 
             'motivo' | 'signos_vitales' | 'exploracion' | 'diagnosticos' | 'tratamiento' | 
             'archivos' | 'historial';

interface Tab {
  id: TabId;
  label: string;
  icon: React.ReactNode;
}

const TABS: Tab[] = [
  { id: 'identificacion', label: 'Identificación', icon: <User className="w-4 h-4" /> },
  { id: 'alergias', label: 'Alergias', icon: <AlertCircle className="w-4 h-4" /> },
  { id: 'antecedentes', label: 'Antecedentes', icon: <ClipboardList className="w-4 h-4" /> },
  { id: 'estilo_vida', label: 'Estilo de Vida', icon: <Heart className="w-4 h-4" /> },
  { id: 'ginecologia', label: 'Ginecología', icon: <Activity className="w-4 h-4" /> },
  { id: 'motivo', label: 'Motivo Consulta', icon: <FileText className="w-4 h-4" /> },
  { id: 'signos_vitales', label: 'Signos Vitales', icon: <Activity className="w-4 h-4" /> },
  { id: 'exploracion', label: 'Exploración', icon: <Stethoscope className="w-4 h-4" /> },
  { id: 'diagnosticos', label: 'Diagnósticos', icon: <ClipboardList className="w-4 h-4" /> },
  { id: 'tratamiento', label: 'Tratamiento', icon: <FileText className="w-4 h-4" /> },
  { id: 'archivos', label: 'Archivos', icon: <FileImage className="w-4 h-4" /> },
  { id: 'historial', label: 'Historial', icon: <History className="w-4 h-4" /> },
];

const MedicalRecordsPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [showPatientModal, setShowPatientModal] = useState(true);
  const [selectedPatientId, setSelectedPatientId] = useState<number | null>(null);
  const [medicalRecord, setMedicalRecord] = useState<MedicalRecord | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>('identificacion');
  const [loading, setLoading] = useState(false);

  // Verificar si el usuario puede editar (Podologo o Admin)
  const canEdit = user?.rol === 'Podologo' || user?.rol === 'Admin';

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

  const handleEdit = () => {
    if (selectedPatientId && canEdit) {
      // Redirigir a la página de atención médica con el paciente seleccionado
      navigate(`/medical/attention?patientId=${selectedPatientId}`);
    }
  };

  const handleBack = () => {
    setShowPatientModal(true);
    setSelectedPatientId(null);
    setMedicalRecord(null);
  };

  const renderTabContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      );
    }

    if (!medicalRecord) {
      return (
        <div className="text-center py-12 text-gray-500">
          No se encontró expediente médico
        </div>
      );
    }

    // Contenido de solo lectura
    return (
      <div className="space-y-4">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">{TABS.find(t => t.id === activeTab)?.label}</h3>
            <Lock className="w-5 h-5 text-gray-400" />
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-gray-500 italic">
            <p>Vista de solo lectura - Contenido de {activeTab}</p>
            {!canEdit && (
              <p className="text-sm text-amber-600 mt-2">
                ⚠️ Solo los podólogos pueden editar expedientes médicos
              </p>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <>
      <PatientSelectionModal
        isOpen={showPatientModal}
        onClose={() => navigate('/')}
        onSelectPatient={handleSelectPatient}
      />

      {selectedPatientId && (
        <div className="min-h-screen bg-gray-50">
          {/* Header */}
          <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <button
                    onClick={handleBack}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                      <FileText className="w-6 h-6 text-blue-600" />
                      Expedientes Médicos
                    </h1>
                    {medicalRecord && (
                      <p className="text-sm text-gray-600">
                        Paciente: {medicalRecord.paciente_nombre} • ID: #{selectedPatientId}
                        {!canEdit && <span className="ml-2 text-amber-600">🔒 Solo lectura</span>}
                      </p>
                    )}
                  </div>
                </div>
                {canEdit && (
                  <button
                    onClick={handleEdit}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Edit2 className="w-4 h-4" />
                    Editar Expediente
                  </button>
                )}
              </div>
            </div>

            {/* Tabs */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-gray-300">
                {TABS.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-t-lg whitespace-nowrap transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-600 font-semibold'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    {tab.icon}
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Main Content - 2/3 */}
              <div className="lg:col-span-2">
                {renderTabContent()}
              </div>

              {/* Info Panel - 1/3 */}
              <div className="lg:col-span-1">
                <div className="bg-blue-50 rounded-lg border-2 border-blue-200 p-6 sticky top-24">
                  <div className="flex items-center gap-2 mb-4">
                    <FileText className="w-8 h-8 text-blue-600" />
                    <div>
                      <h3 className="font-bold text-gray-900">Información</h3>
                      <p className="text-xs text-gray-600">Expediente Médico</p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    {medicalRecord && (
                      <>
                        <div className="bg-white rounded-lg p-3 text-sm">
                          <p className="text-gray-600 mb-1">Última actualización:</p>
                          <p className="font-semibold text-gray-900">
                            {medicalRecord.fecha_ultima_actualizacion 
                              ? new Date(medicalRecord.fecha_ultima_actualizacion).toLocaleDateString('es-MX')
                              : 'Sin actualizar'
                            }
                          </p>
                        </div>
                        <div className="bg-white rounded-lg p-3 text-sm">
                          <p className="text-gray-600 mb-1">Consultas totales:</p>
                          <p className="font-semibold text-gray-900">
                            {medicalRecord.consultas?.length || 0}
                          </p>
                        </div>
                        {medicalRecord.alergias && medicalRecord.alergias.length > 0 && (
                          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm">
                            <p className="font-semibold text-red-900 mb-1 flex items-center gap-1">
                              <AlertCircle className="w-4 h-4" />
                              Alergias
                            </p>
                            <ul className="text-red-800 space-y-1">
                              {medicalRecord.alergias.map((alergia, idx) => (
                                <li key={idx}>• {alergia.sustancia}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </>
                    )}
                    {!canEdit && (
                      <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800">
                        <p className="font-semibold mb-1">🔒 Vista de solo lectura</p>
                        <p className="text-xs">
                          Solo los podólogos y administradores pueden editar expedientes médicos.
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default MedicalRecordsPage;
