import React from 'react';
import { Service } from '../../services/catalogService';

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
        <th>Descripción</th>
        <th>Precio</th>
        <th>Duración (min)</th>
        <th>Activo</th>
        <th>Acciones</th>
      </tr>
    </thead>
    <tbody>
      {services.map(service => (
        <tr key={service.id}>
          <td>{service.nombre}</td>
          <td>{service.descripcion}</td>
          <td>${service.precio.toFixed(2)}</td>
          <td>{service.duracion_minutos}</td>
          <td>{service.activo ? 'Sí' : 'No'}</td>
          <td>
            <button onClick={() => onEdit(service)}>Editar</button>
            <button onClick={() => onDelete(service)}>Eliminar</button>
          </td>
        </tr>
      ))}
    </tbody>
  </table>
);

export default ServicesTable;
