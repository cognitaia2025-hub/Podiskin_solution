/**
 * UserFormModal Component
 * Location: Frontend/src/components/admin/UserFormModal.tsx
 * 
 * Modal for creating/editing staff members.
 * Handles form state and validation.
 */

import React from 'react';
import type { CreateStaffRequest, Role, StaffMember } from '../../services/staffService';

interface UserFormModalProps {
  isOpen: boolean;
  editingStaff: StaffMember | null;
  formData: CreateStaffRequest;
  roles: Role[];
  onClose: () => void;
  onSubmit: (e: React.FormEvent) => void;
  onChange: (data: Partial<CreateStaffRequest>) => void;
}

const UserFormModal: React.FC<UserFormModalProps> = ({
  isOpen,
  editingStaff,
  formData,
  roles,
  onClose,
  onSubmit,
  onChange,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {editingStaff ? 'Editar Usuario' : 'Nuevo Miembro del Equipo'}
          </h2>
        </div>

        <form onSubmit={onSubmit} className="p-6 space-y-4">
          {/* Nombre completo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nombre Completo *
            </label>
            <input
              type="text"
              value={formData.nombre_completo}
              onChange={(e) => onChange({ nombre_completo: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email *
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => onChange({ email: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {/* Username (only for new users) */}
          {!editingStaff && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nombre de Usuario *
              </label>
              <input
                type="text"
                value={formData.nombre_usuario}
                onChange={(e) => onChange({ nombre_usuario: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
          )}

          {/* Password (only for new users) */}
          {!editingStaff && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contraseña Temporal *
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => onChange({ password: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                minLength={8}
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Mínimo 8 caracteres. El usuario puede cambiarla después.
              </p>
            </div>
          )}

          {/* Role */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Rol *
            </label>
            <select
              value={formData.id_rol}
              onChange={(e) => onChange({ id_rol: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="">Seleccionar rol</option>
              {roles.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.nombre_rol}
                </option>
              ))}
            </select>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {editingStaff ? 'Actualizar' : 'Crear'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UserFormModal;
