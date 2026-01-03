import React from 'react';
import type { Service } from '../../services/catalogService';

interface ServicesTableProps {
  services: Service[];
  onEdit: (service: Service) => void;
  onDelete: (service: Service) => void;
}

const ServicesTable: React.FC<ServicesTableProps> = ({ services, onEdit, onDelete }) => (
  <table className="services-table">
    <thead>
      <tr>
        <th>Nombre</th>
        <th>Tipo</th>
        <th>Categoría</th>
        <th>Precio</th>
        <th>Duración</th>
        <th>Activo</th>
        <th>Acciones</th>
      </tr>
    </thead>
    <tbody>
      {services.length === 0 ? (
        <tr>
          <td colSpan={7} style={{ textAlign: 'center', padding: '20px' }}>
            No hay servicios registrados
          </td>
        </tr>
      ) : (
        services.map(service => (
          <tr key={service.id}>
            <td>
              <strong>{service.nombre}</strong>
              {service.descripcion && (
                <small style={{ display: 'block', color: '#666' }}>{service.descripcion}</small>
              )}
            </td>
            <td>
              <span className={`badge badge-${service.tipo}`}>
                {service.tipo === 'servicio' ? '🔧 Servicio' : '💊 Tratamiento'}
              </span>
            </td>
            <td style={{ textTransform: 'capitalize' }}>{service.categoria}</td>
            <td>${service.precio.toFixed(2)}</td>
            <td>{service.duracion_minutos} min</td>
            <td>{service.activo ? '✅ Sí' : '❌ No'}</td>
            <td>
              <button onClick={() => onEdit(service)} title="Editar">✏️</button>
              <button onClick={() => onDelete(service)} title="Eliminar">🗑️</button>
            </td>
          </tr>
        ))
      )}
    </tbody>
  </table>
);

export default ServicesTable;
