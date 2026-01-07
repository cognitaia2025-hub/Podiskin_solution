/**
 * Modal de Gestión de Pacientes del Podólogo
 * ===========================================
 * Muestra pacientes asignados y permite asignar podólogo interino
 */

import React, { useState, useEffect } from 'react';
import { X, User, Phone, Calendar, Save, AlertCircle } from 'lucide-react';
import type { StaffMember } from '../../services/staffService';
import {
  getPodologoPatients,
  getAvailablePodologos,
  assignInterinoToPaciente,
  type PatientWithInterino,
  type AvailablePodologo,
} from '../../services/podologosService';

interface Patient {
  id: number;
  nombre_completo: string;
  telefono: string;
  ultimo_tratamiento: string;
  fecha_ultimo_tratamiento: string;
  podologo_interino_id?: number;
}

interface PodologistPatientsModalProps {
  podologo: StaffMember;
  onClose: () => void;
  onSave: (patientId: number, interinoPodologoId: number | null) => void;
}

export const PodologistPatientsModal: React.FC<PodologistPatientsModalProps> = ({
  podologo,
  onClose,
  onSave,
}) => {
  const [patients, setPatients] = useState<PatientWithInterino[]>([]);
  const [availablePodologos, setAvailablePodologos] = useState<AvailablePodologo[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [changes, setChanges] = useState<Record<number, number | null>>({});

  useEffect(() => {
    loadData();
  }, [podologo.id]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Cargar pacientes del podólogo
      const patientsData = await getPodologoPatients(podologo.id);
      setPatients(patientsData);
      
      // Cargar podólogos disponibles (excluyendo el actual)
      const podologosData = await getAvailablePodologos(podologo.id);
      setAvailablePodologos(podologosData);
      
    } catch (error) {
      console.error('Error loading data:', error);
      alert('Error al cargar datos. Por favor, intente nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleInterinoChange = (patientId: number, podologoId: string) => {
    const newValue = podologoId === '' ? null : parseInt(podologoId);
    setChanges({
      ...changes,
      [patientId]: newValue,
    });
  };

  const handleSaveChanges = async () => {
    try {
      setSaving(true);
      
      // Guardar cada cambio
      for (const [patientId, podologoInterinoId] of Object.entries(changes)) {
        await assignInterinoToPaciente(podologo.id, {
          paciente_id: parseInt(patientId),
          podologo_interino_id: podologoInterinoId,
          motivo: `Asignación temporal desde panel de administración`,
        });
        
        // Llamar callback si existe
        onSave(parseInt(patientId), podologoInterinoId);
      }
      
      alert(`${Object.keys(changes).length} asignación(es) guardada(s) correctamente`);
      onClose();
      
    } catch (error) {
      console.error('Error saving changes:', error);
      alert('Error al guardar cambios. Por favor, intente nuevamente.');
    } finally {
      setSaving(false);
    }
  };

  const hasChanges = Object.keys(changes).length > 0;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b bg-blue-50">
          <div className="flex items-center gap-3">
            <User className="w-6 h-6 text-blue-600" />
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                Pacientes de {podologo.nombre_completo}
              </h2>
              <p className="text-sm text-gray-600">
                Gestión de pacientes y podólogos interinos
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Info Alert */}
        <div className="m-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-yellow-800">
            <p className="font-medium mb-1">Asignación de Podólogo Interino</p>
            <p>
              Selecciona un podólogo interino para cubrir temporalmente los pacientes 
              de {podologo.nombre_completo.split(' ')[0]} durante su ausencia.
            </p>
          </div>
        </div>

        {/* Body */}
        <div className="p-6">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-600 mt-4">Cargando pacientes...</p>
            </div>
          ) : patients.length === 0 ? (
            <div className="text-center py-12">
              <User className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No hay pacientes asignados</p>
            </div>
          ) : (
            <div className="space-y-4">
              {patients.map((patient) => (
                <div
                  key={patient.paciente_id}
                  className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    {/* Información del Paciente */}
                    <div className="flex-1 grid grid-cols-3 gap-4">
                      <div>
                        <label className="text-xs font-medium text-gray-500 uppercase">
                          Paciente
                        </label>
                        <p className="text-sm font-semibold text-gray-900 mt-1">
                          {patient.nombre_completo}
                        </p>
                        <p className="text-xs text-gray-500">
                          ID: #{patient.paciente_id}
                        </p>
                      </div>

                      <div>
                        <label className="text-xs font-medium text-gray-500 uppercase flex items-center gap-1">
                          <Phone className="w-3 h-3" />
                          Teléfono
                        </label>
                        <p className="text-sm text-gray-900 mt-1">
                          {patient.telefono || 'No registrado'}
                        </p>
                      </div>

                      <div>
                        <label className="text-xs font-medium text-gray-500 uppercase flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          Último Tratamiento
                        </label>
                        <p className="text-sm text-gray-900 mt-1">
                          {patient.ultimo_tratamiento || 'Sin tratamientos'}
                        </p>
                        {patient.fecha_ultimo_tratamiento && (
                          <p className="text-xs text-gray-500">
                            {new Date(patient.fecha_ultimo_tratamiento).toLocaleDateString('es-MX')}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Selector de Podólogo Interino */}
                    <div className="w-64">
                      <label className="text-xs font-medium text-gray-500 uppercase block mb-2">
                        Podólogo Interino
                      </label>
                      <div className="flex gap-2">
                        <select
                          value={
                            changes[patient.paciente_id] !== undefined
                              ? changes[patient.paciente_id] ?? ''
                              : patient.podologo_interino_id ?? ''
                          }
                          onChange={(e) => handleInterinoChange(patient.paciente_id, e.target.value)}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
                          disabled={saving}
                        >
                          <option value="">Sin asignar</option>
                          {availablePodologos.map((p) => (
                            <option key={p.id} value={p.id}>
                              {p.nombre_completo}
                            </option>
                          ))}
                        </select>
                        {changes[patient.paciente_id] !== undefined && (
                          <span className="flex items-center px-2 text-xs text-blue-600 bg-blue-50 rounded">
                            •
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t bg-gray-50">
          <div className="text-sm text-gray-600">
            {hasChanges && (
              <span className="flex items-center gap-2 text-blue-600">
                <span className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></span>
                {Object.keys(changes).length} cambio(s) pendiente(s)
              </span>
            )}
          </div>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              disabled={saving}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              onClick={handleSaveChanges}
              disabled={!hasChanges || saving}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                hasChanges && !saving
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Guardando...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Guardar Cambios
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
