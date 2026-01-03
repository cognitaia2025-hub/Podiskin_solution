import React, { useEffect, useState } from 'react';
import { Package, Plus, Search, Filter, Loader2, Edit2, Trash2 } from 'lucide-react';
import { toast } from 'react-toastify';
import { getServices, createService, updateService, deleteService, TIPOS_SERVICIO, CATEGORIAS_SERVICIO } from '../../services/catalogService';
import type { Service, ServiceCreate, ServiceFilters, TipoServicio, CategoriaServicio } from '../../services/catalogService';
import ServiceFormModal from '../../components/admin/ServiceFormModal';

const ServicesPage: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingService, setEditingService] = useState<Service | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Filtros
  const [filters, setFilters] = useState<ServiceFilters>({
    orden: 'nombre',
    direccion: 'asc',
  });

  const fetchServices = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getServices(filters);
      setServices(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error al cargar servicios:', err);
      setError('Error al cargar los servicios. Verifica que el backend esté corriendo.');
      setServices([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServices();
  }, [filters]);

  const handleFilterChange = (key: keyof ServiceFilters, value: string | boolean | undefined) => {
    setFilters(prev => ({
      ...prev,
      [key]: value === '' ? undefined : value,
    }));
  };

  const handleAdd = () => {
    setEditingService(null);
    setModalOpen(true);
  };

  const handleEdit = (service: Service) => {
    setEditingService(service);
    setModalOpen(true);
  };

  const handleDelete = async (service: Service) => {
    if (window.confirm(`¿Eliminar el servicio "${service.nombre}"?`)) {
      try {
        await deleteService(service.id);
        toast.success('Servicio eliminado correctamente');
        fetchServices();
      } catch (err) {
        toast.error('Error al eliminar el servicio');
      }
    }
  };

  const handleSubmit = async (data: ServiceCreate) => {
    try {
      if (editingService) {
        await updateService(editingService.id, data);
        toast.success('Servicio actualizado correctamente');
      } else {
        await createService(data);
        toast.success('Servicio creado correctamente');
      }
      setModalOpen(false);
      fetchServices();
    } catch (err) {
      toast.error('Error al guardar el servicio');
    }
  };

  // Filtrar por búsqueda local
  const filteredServices = services.filter(s => 
    s.nombre.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (s.descripcion?.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Package className="w-8 h-8" />
          Catálogo de Servicios
        </h1>
        <p className="text-gray-600 mt-2">
          Administra los servicios y tratamientos disponibles
        </p>
      </div>

      {/* Actions Bar */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
          {/* Search */}
          <div className="relative flex-1 w-full lg:w-auto lg:max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por nombre o descripción..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Create button */}
          <button
            onClick={handleAdd}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            <Plus className="w-5 h-5" />
            Nuevo Servicio
          </button>
        </div>

        {/* Filters */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-center gap-2 mb-3 text-sm text-gray-600">
            <Filter className="w-4 h-4" />
            Filtros
          </div>
          <div className="flex flex-wrap gap-3">
            <select
              value={filters.tipo || ''}
              onChange={(e) => handleFilterChange('tipo', e.target.value as TipoServicio)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos los tipos</option>
              {TIPOS_SERVICIO.map(t => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>

            <select
              value={filters.categoria || ''}
              onChange={(e) => handleFilterChange('categoria', e.target.value as CategoriaServicio)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todas las categorías</option>
              {CATEGORIAS_SERVICIO.map(c => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>

            <select
              value={filters.activo === undefined ? '' : String(filters.activo)}
              onChange={(e) => handleFilterChange('activo', e.target.value === '' ? undefined : e.target.value === 'true')}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos los estados</option>
              <option value="true">Solo activos</option>
              <option value="false">Solo inactivos</option>
            </select>

            <select
              value={filters.orden || 'nombre'}
              onChange={(e) => handleFilterChange('orden', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="nombre">Ordenar por nombre</option>
              <option value="precio">Ordenar por precio</option>
              <option value="duracion_minutos">Ordenar por duración</option>
            </select>

            <select
              value={filters.direccion || 'asc'}
              onChange={(e) => handleFilterChange('direccion', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="asc">Ascendente</option>
              <option value="desc">Descendente</option>
            </select>
          </div>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <span className="ml-2 text-gray-600">Cargando servicios...</span>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error}
        </div>
      ) : (
        <>
          <p className="text-sm text-gray-500 mb-4">
            Mostrando {filteredServices.length} de {services.length} servicio(s)
          </p>
          
          {/* Table */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Servicio
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tipo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Categoría
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Precio
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Duración
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredServices.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                        No hay servicios registrados
                      </td>
                    </tr>
                  ) : (
                    filteredServices.map(service => (
                      <tr key={service.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div className="font-medium text-gray-900">{service.nombre}</div>
                          {service.descripcion && (
                            <div className="text-sm text-gray-500 truncate max-w-xs">
                              {service.descripcion}
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            service.tipo === 'tratamiento' 
                              ? 'bg-purple-100 text-purple-800' 
                              : 'bg-blue-100 text-blue-800'
                          }`}>
                            {service.tipo === 'tratamiento' ? '💊 Tratamiento' : '🔧 Servicio'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 capitalize">
                          {service.categoria}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm font-semibold text-green-600">
                            ${service.precio.toFixed(2)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                          {service.duracion_minutos} min
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            service.activo 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {service.activo ? '✓ Activo' : '✗ Inactivo'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                          <button
                            onClick={() => handleEdit(service)}
                            className="text-blue-600 hover:text-blue-800 p-1 rounded hover:bg-blue-50 mr-2"
                            title="Editar"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(service)}
                            className="text-red-600 hover:text-red-800 p-1 rounded hover:bg-red-50"
                            title="Eliminar"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Modal */}
      <ServiceFormModal
        isOpen={modalOpen}
        service={editingService}
        onClose={() => setModalOpen(false)}
        onSubmit={handleSubmit}
      />
    </div>
  );
};

export default ServicesPage;
