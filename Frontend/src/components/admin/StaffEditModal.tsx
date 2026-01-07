/**
 * Modal de Edición de Usuario con Gestión de Permisos
 * ===================================================
 * Permite editar información del usuario Y gestionar sus permisos
 */

import React, { useState } from 'react';
import { X, Save, Shield, Users } from 'lucide-react';
import type { StaffMember } from '../../services/staffService';

interface StaffEditModalProps {
  member: StaffMember;
  onClose: () => void;
  onSave: (member: StaffMember) => void;
  onManagePatients: (member: StaffMember) => void;
}

export const StaffEditModal: React.FC<StaffEditModalProps> = ({
  member,
  onClose,
  onSave,
  onManagePatients,
}) => {
  const [formData, setFormData] = useState(member);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  const isPodologo = member.rol === 'Podologo';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6 text-blue-600" />
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                Editar Usuario
              </h2>
              <p className="text-sm text-gray-600">
                {member.nombre_completo}
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

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Información Básica */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Información Básica
            </h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre Completo
                </label>
                <input
                  type="text"
                  value={formData.nombre_completo}
                  onChange={(e) => setFormData({...formData, nombre_completo: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Usuario
                </label>
                <input
                  type="text"
                  value={formData.nombre_usuario}
                  disabled
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rol
                </label>
                <select
                  value={formData.rol || ''}
                  onChange={(e) => setFormData({...formData, rol: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Seleccionar rol</option>
                  <option value="Admin">Admin</option>
                  <option value="Podologo">Podólogo</option>
                  <option value="Recepcionista">Recepcionista</option>
                  <option value="Asistente">Asistente</option>
                </select>
              </div>
            </div>

            <div>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.activo}
                  onChange={(e) => setFormData({...formData, activo: e.target.checked})}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">
                  Usuario activo
                </span>
              </label>
            </div>
          </div>

          {/* Gestión de Pacientes (Solo Podólogos) */}
          {isPodologo && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Gestión de Pacientes
              </h3>
              <button
                type="button"
                onClick={() => onManagePatients(member)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <Users className="w-5 h-5" />
                <span>Ver y Gestionar Pacientes Asignados</span>
              </button>
              <p className="text-sm text-gray-600 mt-2">
                Administra los pacientes asignados y podólogos interinos
              </p>
            </div>
          )}

          {/* Footer */}
          <div className="flex justify-end gap-3 pt-6 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Save className="w-4 h-4" />
              Guardar Cambios
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
