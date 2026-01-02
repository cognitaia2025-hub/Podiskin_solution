import React, { useEffect, useState } from 'react';
import ServicesTable from '../../components/admin/ServicesTable';
import ServiceFormModal from '../../components/admin/ServiceFormModal';
import { getServices, createService, updateService, deleteService, Service, ServiceCreate } from '../../services/catalogService';

const ServicesPage: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingService, setEditingService] = useState<Service | null>(null);

  const fetchServices = async () => {
    const data = await getServices();
    setServices(data);
  };

  useEffect(() => {
    fetchServices();
  }, []);

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
      await deleteService(service.id);
      fetchServices();
    }
  };

  const handleSubmit = async (data: ServiceCreate) => {
    if (editingService) {
      await updateService(editingService.id, data);
    } else {
      await createService(data);
    }
    setModalOpen(false);
    fetchServices();
  };

  return (
    <div>
      <h1>Catálogo de Servicios</h1>
      <button onClick={handleAdd}>Nuevo Servicio</button>
      <ServicesTable services={services} onEdit={handleEdit} onDelete={handleDelete} />
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
