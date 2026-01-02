import React, { useState, useEffect } from 'react';
import { Service, ServiceCreate } from '../../services/catalogService';

interface ServiceFormModalProps {
  isOpen: boolean;
  service: Service | null;
  onClose: () => void;
  onSubmit: (data: ServiceCreate) => Promise<void>;
}

const initialForm: ServiceCreate = {
  nombre: '',
  descripcion: '',
  precio: 0,
  duracion_minutos: 0,
  activo: true,
};

const ServiceFormModal: React.FC<ServiceFormModalProps> = ({ isOpen, service, onClose, onSubmit }) => {
  const [form, setForm] = useState<ServiceCreate>(initialForm);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (service) {
      setForm({
        nombre: service.nombre,
        descripcion: service.descripcion || '',
        precio: service.precio,
        duracion_minutos: service.duracion_minutos,
        activo: service.activo,
      });
    } else {
      setForm(initialForm);
    }
  }, [service, isOpen]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : type === 'number' ? Number(value) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    await onSubmit(form);
    setLoading(false);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>{service ? 'Editar Servicio' : 'Nuevo Servicio'}</h2>
        <form onSubmit={handleSubmit}>
          <label>
            Nombre:
            <input name="nombre" value={form.nombre} onChange={handleChange} required />
          </label>
          <label>
            Descripción:
            <textarea name="descripcion" value={form.descripcion} onChange={handleChange} />
          </label>
          <label>
            Precio:
            <input name="precio" type="number" value={form.precio} onChange={handleChange} required min={0} step={0.01} />
          </label>
          <label>
            Duración (minutos):
            <input name="duracion_minutos" type="number" value={form.duracion_minutos} onChange={handleChange} required min={1} />
          </label>
          <label>
            Activo:
            <input name="activo" type="checkbox" checked={form.activo} onChange={handleChange} />
          </label>
          <div className="modal-actions">
            <button type="submit" disabled={loading}>{loading ? 'Guardando...' : 'Guardar'}</button>
            <button type="button" onClick={onClose}>Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ServiceFormModal;
