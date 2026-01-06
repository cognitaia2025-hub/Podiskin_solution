/**
 * Patient Selection Modal
 * 
 * Modal para seleccionar paciente antes de iniciar atención médica.
 * Muestra citas próximas arriba y todos los pacientes abajo en grid.
 */

import React, { useState, useEffect } from 'react';
import { X, Search, Clock, Phone, Calendar, AlertCircle, FileText, Sparkles } from 'lucide-react';
import type { Patient, UpcomingAppointment } from '../../services/medicalRecordsService';
import { searchPatients, getAllPatients, getUpcomingAppointments } from '../../services/medicalRecordsService';

interface PatientSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectPatient: (patientId: number) => void;
}

const PatientSelectionModal: React.FC<PatientSelectionModalProps> = ({
  isOpen,
  onClose,
  onSelectPatient,
}) => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [upcomingAppointments, setUpcomingAppointments] = useState<UpcomingAppointment[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Búsqueda simple (ID, teléfono, nombre)
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);
  
  // Filtros inteligentes (solo UI por ahora)
  const [intelligentFilter, setIntelligentFilter] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [appointments, allPatients] = await Promise.all([
        getUpcomingAppointments(3),
        getAllPatients(),
      ]);
      setUpcomingAppointments(appointments);
      setPatients(allPatients);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    
    if (query.trim().length < 2) {
      loadData();
      return;
    }

    setSearching(true);
    try {
      const results = await searchPatients(query);
      setPatients(results);
    } finally {
      setSearching(false);
    }
  };

  const handleIntelligentFilterChange = (value: string) => {
    setIntelligentFilter(value);
    // Por ahora solo actualiza el estado, sin funcionalidad backend
  };

  const calculateAge = (birthDate: string) => {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  const formatLastVisit = (date?: string) => {
    if (!date) return 'Primera vez';
    const lastVisit = new Date(date);
    const today = new Date();
    const diffTime = Math.abs(today.getTime() - lastVisit.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Hoy';
    if (diffDays === 1) return 'Ayer';
    if (diffDays < 7) return `Hace ${diffDays} días`;
    if (diffDays < 30) return `Hace ${Math.floor(diffDays / 7)} semanas`;
    if (diffDays < 365) return `Hace ${Math.floor(diffDays / 30)} meses`;
    return `Hace ${Math.floor(diffDays / 365)} años`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-7xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6 text-blue-600" />
            <div>
              <h2 className="text-xl font-bold text-gray-900">Seleccionar Paciente</h2>
              <p className="text-sm text-gray-500">Elige un paciente para iniciar atención médica</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Search and Filters Bar */}
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200 space-y-3">
          {/* Búsqueda simple */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Buscar por nombre, teléfono o ID de paciente..."
              className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            {searching && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
              </div>
            )}
          </div>

          {/* Filtros inteligentes (solo UI) */}
          <div className="relative">
            <Sparkles className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-400" />
            <input
              type="text"
              value={intelligentFilter}
              onChange={(e) => handleIntelligentFilterChange(e.target.value)}
              placeholder='🤖 Filtros inteligentes: ej. "pacientes con alergias entre enero y marzo" (Próximamente)'
              className="w-full pl-10 pr-4 py-2.5 border border-purple-200 bg-purple-50/30 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm italic"
              disabled
            />
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <>
              {/* Citas Próximas */}
              {upcomingAppointments.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Clock className="w-5 h-5 text-blue-600" />
                    Citas Próximas
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {upcomingAppointments.map((appointment) => (
                      <button
                        key={appointment.id}
                        onClick={() => onSelectPatient(appointment.paciente_id)}
                        className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 hover:bg-blue-100 hover:border-blue-300 transition-all text-left"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Calendar className="w-4 h-4 text-blue-600" />
                            <span className="text-sm font-medium text-blue-900">
                              {new Date(appointment.fecha_hora).toLocaleTimeString('es-MX', {
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </span>
                          </div>
                          {appointment.alergias_importantes && appointment.alergias_importantes.length > 0 && (
                            <AlertCircle className="w-4 h-4 text-red-500" />
                          )}
                        </div>
                        <p className="font-bold text-gray-900 mb-1">{appointment.paciente_nombre}</p>
                        <div className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                          <Phone className="w-3 h-3" />
                          {appointment.telefono}
                        </div>
                        {appointment.motivo_consulta && (
                          <p className="text-sm text-gray-700 mb-2">📋 {appointment.motivo_consulta}</p>
                        )}
                        {appointment.alergias_importantes && appointment.alergias_importantes.length > 0 && (
                          <div className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">
                            ⚠️ {appointment.alergias_importantes.join(', ')}
                          </div>
                        )}
                        {appointment.ultima_visita && (
                          <p className="text-xs text-gray-500 mt-2">
                            Última visita: {formatLastVisit(appointment.ultima_visita)}
                          </p>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Línea divisoria */}
              {upcomingAppointments.length > 0 && (
                <div className="border-t border-gray-300 my-6"></div>
              )}

              {/* Todos los Pacientes */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Todos los Pacientes ({patients.length})
                </h3>
                {patients.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    {searchQuery ? 'No se encontraron pacientes' : 'No hay pacientes registrados'}
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {patients.map((patient) => (
                      <button
                        key={patient.id}
                        onClick={() => onSelectPatient(patient.id)}
                        className="bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all text-left"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <span className="text-xs font-mono text-gray-400">#{patient.id}</span>
                          {patient.tiene_alergias && (
                            <AlertCircle className="w-4 h-4 text-red-500" />
                          )}
                        </div>
                        <p className="font-bold text-gray-900 mb-1">{patient.nombre_completo}</p>
                        <div className="space-y-1 text-sm text-gray-600">
                          <p>🎂 {calculateAge(patient.fecha_nacimiento)} años</p>
                          <p>📞 {patient.telefono}</p>
                          <p>🏥 {formatLastVisit(patient.ultima_visita)}</p>
                          <p className="text-xs">📊 {patient.total_consultas} consultas</p>
                        </div>
                        {patient.diagnostico_reciente && (
                          <p className="text-xs text-gray-500 mt-2 line-clamp-1">
                            🩺 {patient.diagnostico_reciente}
                          </p>
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default PatientSelectionModal;
