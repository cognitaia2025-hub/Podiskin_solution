/**
 * Staff Management Page
 * 
 * Administrative page for managing system users (staff members).
 * Features:
 * - List all active staff members
 * - Create new staff members
 * - Edit staff member details (name, email, role)
 * - Deactivate staff members (soft delete)
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../auth/AuthContext';
import { Navigate } from 'react-router-dom';
import { Users, Plus, Edit2, Trash2, Search, Loader2, UserCheck, UserX, Mail, Shield } from 'lucide-react';
import { toast } from 'react-toastify';
import { 
  staffService, 
  type StaffMember, 
  type CreateStaffRequest,
  type UpdateStaffRequest,
  type Role 
} from '../services/staffService';

const StaffManagement: React.FC = () => {
  const { user } = useAuth();

  // Redirect non-admin users
  if (user?.rol !== 'Admin') {
    return <Navigate to="/calendar" replace />;
  }

  // State
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingStaff, setEditingStaff] = useState<StaffMember | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showInactive, setShowInactive] = useState(false);

  // Form state
  const [formData, setFormData] = useState<CreateStaffRequest>({
    nombre_usuario: '',
    password: '',
    nombre_completo: '',
    email: '',
    id_rol: 0,
  });

  // Load staff and roles
  const loadData = async () => {
    setIsLoading(true);
    try {
      const [staffData, rolesData] = await Promise.all([
        staffService.getAllStaff(!showInactive),
        staffService.getRoles()
      ]);
      setStaff(staffData);
      setRoles(rolesData.filter(r => r.activo));
    } catch (error: any) {
      toast.error(error.message || 'Error al cargar datos');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [showInactive]);

  // Filter staff by search query
  const filteredStaff = staff.filter(member => 
    member.nombre_completo.toLowerCase().includes(searchQuery.toLowerCase()) ||
    member.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    member.nombre_usuario.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Open modal for creating new staff
  const handleOpenCreateModal = () => {
    setEditingStaff(null);
    setFormData({
      nombre_usuario: '',
      password: '',
      nombre_completo: '',
      email: '',
      id_rol: roles[0]?.id || 0,
    });
    setIsModalOpen(true);
  };

  // Open modal for editing staff
  const handleOpenEditModal = (member: StaffMember) => {
    setEditingStaff(member);
    setFormData({
      nombre_usuario: member.nombre_usuario,
      password: '', // Not editable
      nombre_completo: member.nombre_completo,
      email: member.email,
      id_rol: member.id_rol || 0,
    });
    setIsModalOpen(true);
  };

  // Close modal
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingStaff(null);
    setFormData({
      nombre_usuario: '',
      password: '',
      nombre_completo: '',
      email: '',
      id_rol: 0,
    });
  };

  // Handle form submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (editingStaff) {
        // Update existing staff
        const updateData: UpdateStaffRequest = {
          nombre_completo: formData.nombre_completo,
          email: formData.email,
          id_rol: formData.id_rol,
        };
        await staffService.updateStaff(editingStaff.id, updateData);
        toast.success('Usuario actualizado correctamente');
      } else {
        // Create new staff
        await staffService.createStaff(formData);
        toast.success('Usuario creado correctamente');
      }
      
      handleCloseModal();
      loadData();
    } catch (error: any) {
      toast.error(error.message || 'Error al guardar usuario');
    }
  };

  // Handle delete staff
  const handleDelete = async (member: StaffMember) => {
    if (!confirm(`¿Estás seguro de desactivar a ${member.nombre_completo}?`)) {
      return;
    }

    try {
      await staffService.deleteStaff(member.id);
      toast.success('Usuario desactivado correctamente');
      loadData();
    } catch (error: any) {
      toast.error(error.message || 'Error al desactivar usuario');
    }
  };

  // Get role badge color
  const getRoleColor = (rol: string | null) => {
    switch (rol) {
      case 'Admin':
        return 'bg-purple-100 text-purple-800';
      case 'Podologo':
        return 'bg-blue-100 text-blue-800';
      case 'Recepcionista':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Format date
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Nunca';
    return new Date(dateStr).toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Users className="w-8 h-8" />
          Gestión de Personal
        </h1>
        <p className="text-gray-600 mt-2">
          Administra los usuarios del sistema y sus permisos
        </p>
      </div>

      {/* Actions Bar */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        {/* Search */}
        <div className="relative flex-1 w-full sm:w-auto">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar por nombre, email o usuario..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Toggle inactive */}
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={showInactive}
            onChange={(e) => setShowInactive(e.target.checked)}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700">Mostrar inactivos</span>
        </label>

        {/* Create button */}
        <button
          onClick={handleOpenCreateModal}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 whitespace-nowrap"
        >
          <Plus className="w-5 h-5" />
          Nuevo Miembro
        </button>
      </div>

      {/* Staff List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : filteredStaff.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center">
          <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No se encontraron usuarios
          </h3>
          <p className="text-gray-600">
            {searchQuery ? 'Intenta con otra búsqueda' : 'Agrega el primer miembro del equipo'}
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Usuario
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rol
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Último Acceso
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
              {filteredStaff.map((member) => (
                <tr key={member.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <span className="text-blue-600 font-semibold">
                          {member.nombre_completo.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {member.nombre_completo}
                        </div>
                        <div className="text-sm text-gray-500">
                          @{member.nombre_usuario}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2 text-sm text-gray-900">
                      <Mail className="w-4 h-4 text-gray-400" />
                      {member.email}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleColor(member.rol)}`}>
                      <Shield className="w-3 h-3" />
                      {member.rol || 'Sin rol'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(member.ultimo_login)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {member.activo ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <UserCheck className="w-3 h-3" />
                        Activo
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        <UserX className="w-3 h-3" />
                        Inactivo
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleOpenEditModal(member)}
                      className="text-blue-600 hover:text-blue-900 mr-4"
                      title="Editar"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    {member.activo && member.id !== user?.id && (
                      <button
                        onClick={() => handleDelete(member)}
                        className="text-red-600 hover:text-red-900"
                        title="Desactivar"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">
                {editingStaff ? 'Editar Usuario' : 'Nuevo Miembro del Equipo'}
              </h2>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {/* Nombre completo */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre Completo *
                </label>
                <input
                  type="text"
                  value={formData.nombre_completo}
                  onChange={(e) => setFormData({ ...formData, nombre_completo: e.target.value })}
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
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
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
                    onChange={(e) => setFormData({ ...formData, nombre_usuario: e.target.value })}
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
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
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
                  onChange={(e) => setFormData({ ...formData, id_rol: parseInt(e.target.value) })}
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
                  onClick={handleCloseModal}
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
      )}
    </div>
  );
};

export default StaffManagement;
