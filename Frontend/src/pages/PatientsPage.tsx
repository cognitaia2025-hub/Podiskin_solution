import React, { useState, useEffect } from 'react';
import { Search, Plus, Filter, Users, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { clsx } from 'clsx';
import { useGlobalContext } from '../context/GlobalContext';
import {
  getPatients,
  searchPatients,
  updatePatient,
  type Patient,
  type PatientListResponse,
} from '../services/patientService';
import PatientCard, { type PatientCardData } from '../components/patients/PatientCard';
import PatientAvatar from '../components/patients/PatientAvatar';
import PatientFormModal from '../components/patients/PatientFormModal';

/**
 * PatientsPage Component
 * 
 * Main page for patient management with search, filters, and CRUD operations
 */
const PatientsPage: React.FC = () => {
  const navigate = useNavigate();
  const { setSelectedPatient } = useGlobalContext();

  // State
  const [patients, setPatients] = useState<Patient[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPatientId, setEditingPatientId] = useState<string | undefined>();

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const perPage = 50;

  // Filters
  const [activeFilter, setActiveFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [sortBy, setSortBy] = useState<'name' | 'date'>('name');

  // Load patients
  const loadPatients = async () => {
    setIsLoading(true);
    try {
      const response: PatientListResponse = await getPatients(currentPage, perPage);
      setPatients(response.patients);
      setTotal(response.total);
      setTotalPages(Math.ceil(response.total / perPage));
    } catch (error) {
      console.error('Error loading patients:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Search with debounce
  useEffect(() => {
    if (!searchQuery || searchQuery.length < 2) {
      loadPatients();
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const results = await searchPatients(searchQuery);
        setPatients(results);
        setTotal(results.length);
        setTotalPages(1);
      } catch (error) {
        console.error('Error searching patients:', error);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Load on mount and page change
  useEffect(() => {
    if (!searchQuery) {
      loadPatients();
    }
  }, [currentPage]);

  // Filter and sort patients
  const filteredPatients = React.useMemo(() => {
    let filtered = [...patients];

    // Apply active filter
    if (activeFilter === 'active') {
      filtered = filtered.filter((p: any) => p.activo !== false);
    } else if (activeFilter === 'inactive') {
      filtered = filtered.filter((p: any) => p.activo === false);
    }

    // Apply sorting
    if (sortBy === 'name') {
      filtered.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
    } else if (sortBy === 'date') {
      filtered.sort((a, b) => {
        const dateA = new Date(a.created_at || 0).getTime();
        const dateB = new Date(b.created_at || 0).getTime();
        return dateB - dateA;
      });
    }

    return filtered;
  }, [patients, activeFilter, sortBy]);

  // Handle patient click
  const handlePatientClick = (patient: Patient) => {
    setSelectedPatient(patient);
    navigate('/medical');
  };

  // Handle edit
  const handleEdit = (patient: Patient) => {
    setEditingPatientId(patient.id);
    setIsModalOpen(true);
  };

  // Handle delete (soft delete)
  const handleDelete = async (patient: Patient) => {
    const confirmed = window.confirm(
      `¿Estás seguro de desactivar al paciente ${patient.name}?`
    );

    if (confirmed) {
      try {
        await updatePatient(patient.id, { activo: false } as any);
        loadPatients();
      } catch (error) {
        console.error('Error deleting patient:', error);
        alert('Error al desactivar el paciente. Por favor, intente de nuevo.');
      }
    }
  };

  // Handle create new patient
  const handleNewPatient = () => {
    setEditingPatientId(undefined);
    setIsModalOpen(true);
  };

  // Handle modal success
  const handleModalSuccess = () => {
    loadPatients();
  };

  // Convert Patient to PatientCardData
  const toCardData = (patient: Patient): PatientCardData => {
    const nameParts = (patient.name || '').split(' ');
    return {
      id: patient.id,
      primer_nombre: nameParts[0],
      primer_apellido: nameParts[1],
      telefono_principal: patient.phone,
      correo_electronico: patient.email,
      fecha_nacimiento: patient.fecha_nacimiento,
      activo: (patient as any).activo !== false,
    };
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Pacientes</h1>
          <p className="text-gray-600 mt-2">
            Gestiona la información de tus pacientes
          </p>
        </div>

        {/* Search and Actions Bar */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Buscar por nombre, teléfono o email..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>

            {/* Filters Button */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={clsx(
                'flex items-center gap-2 px-4 py-2 border rounded-lg transition-colors',
                showFilters
                  ? 'bg-teal-50 border-teal-600 text-teal-700'
                  : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              )}
            >
              <Filter className="w-5 h-5" />
              <span className="hidden sm:inline">Filtros</span>
            </button>

            {/* New Patient Button */}
            <button
              onClick={handleNewPatient}
              className="flex items-center gap-2 px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium"
            >
              <Plus className="w-5 h-5" />
              <span className="hidden sm:inline">Nuevo Paciente</span>
              <span className="sm:hidden">Nuevo</span>
            </button>
          </div>

          {/* Filters Panel */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Estado
                  </label>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setActiveFilter('all')}
                      className={clsx(
                        'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                        activeFilter === 'all'
                          ? 'bg-teal-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      )}
                    >
                      Todos
                    </button>
                    <button
                      onClick={() => setActiveFilter('active')}
                      className={clsx(
                        'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                        activeFilter === 'active'
                          ? 'bg-teal-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      )}
                    >
                      Activos
                    </button>
                    <button
                      onClick={() => setActiveFilter('inactive')}
                      className={clsx(
                        'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                        activeFilter === 'inactive'
                          ? 'bg-teal-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      )}
                    >
                      Inactivos
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ordenar por
                  </label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as 'name' | 'date')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  >
                    <option value="name">Nombre (A-Z)</option>
                    <option value="date">Fecha de registro</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Results Count */}
        <div className="mb-4 text-sm text-gray-600">
          {isLoading ? (
            <span>Cargando...</span>
          ) : (
            <span>
              Mostrando {filteredPatients.length} de {total} paciente(s)
            </span>
          )}
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-teal-600" />
          </div>
        )}

        {/* Empty State */}
        {!isLoading && filteredPatients.length === 0 && (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {searchQuery ? 'No se encontraron pacientes' : 'No hay pacientes'}
            </h3>
            <p className="text-gray-600 mb-6">
              {searchQuery
                ? 'Intenta con otros términos de búsqueda'
                : 'Comienza agregando tu primer paciente'}
            </p>
            {!searchQuery && (
              <button
                onClick={handleNewPatient}
                className="inline-flex items-center gap-2 px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium"
              >
                <Plus className="w-5 h-5" />
                Nuevo Paciente
              </button>
            )}
          </div>
        )}

        {/* Desktop Table */}
        {!isLoading && filteredPatients.length > 0 && (
          <>
            <div className="hidden md:block bg-white rounded-lg shadow-sm overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Paciente
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Teléfono
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      F. Nacimiento
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredPatients.map((patient) => {
                    const nameParts = (patient.name || '').split(' ');
                    return (
                      <tr
                        key={patient.id}
                        className="hover:bg-gray-50 cursor-pointer transition-colors"
                        onClick={() => handlePatientClick(patient)}
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-3">
                            <PatientAvatar
                              firstName={nameParts[0] || ''}
                              lastName={nameParts[1] || ''}
                              size="sm"
                            />
                            <div>
                              <div className="font-medium text-gray-900">
                                {patient.name || 'Sin nombre'}
                              </div>
                              {(patient as any).activo === false && (
                                <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full bg-gray-100 text-gray-700">
                                  Inactivo
                                </span>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {patient.phone || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {patient.email || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {patient.fecha_nacimiento
                            ? new Date(patient.fecha_nacimiento).toLocaleDateString('es-ES')
                            : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleEdit(patient);
                              }}
                              className="text-teal-600 hover:text-teal-900 transition-colors"
                            >
                              Editar
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDelete(patient);
                              }}
                              className="text-red-600 hover:text-red-900 transition-colors"
                            >
                              Desactivar
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Mobile Cards */}
            <div className="md:hidden space-y-4">
              {filteredPatients.map((patient) => (
                <PatientCard
                  key={patient.id}
                  patient={toCardData(patient)}
                  onClick={() => handlePatientClick(patient)}
                  onEdit={() => handleEdit(patient)}
                  onDelete={() => handleDelete(patient)}
                />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-6 flex items-center justify-center gap-2">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Anterior
                </button>

                <div className="flex items-center gap-2">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (currentPage <= 3) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i;
                    } else {
                      pageNum = currentPage - 2 + i;
                    }

                    return (
                      <button
                        key={pageNum}
                        onClick={() => setCurrentPage(pageNum)}
                        className={clsx(
                          'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                          currentPage === pageNum
                            ? 'bg-teal-600 text-white'
                            : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                        )}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>

                <button
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Siguiente
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Patient Form Modal */}
      <PatientFormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        patientId={editingPatientId}
        onSuccess={handleModalSuccess}
      />
    </div>
  );
};

export default PatientsPage;
