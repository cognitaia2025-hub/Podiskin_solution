/**
 * Staff Management Page (Refactored)
 * Location: Frontend/src/pages/admin/StaffManagement.tsx
 * 
 * Orchestrates staff management operations.
 * Delegates UI rendering to specialized components.
 * 
 * REFACTORED: Reduced from 568 lines to ~160 lines
 * - Extracted StaffTable component
 * - Extracted UserFormModal component
 * - Clean separation of concerns
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../auth/AuthContext';
import { Navigate } from 'react-router-dom';
import { Users, Plus, Search, Loader2 } from 'lucide-react';
import { toast } from 'react-toastify';
import { 
  staffService, 
  type StaffMember, 
  type CreateStaffRequest,
  type UpdateStaffRequest,
  type Role 
} from '../../services/staffService';
import StaffTable from '../../components/admin/StaffTable';
import UserFormModal from '../../components/admin/UserFormModal';

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
      password: '',
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
        const updateData: UpdateStaffRequest = {
          nombre_completo: formData.nombre_completo,
          email: formData.email,
          id_rol: formData.id_rol,
        };
        await staffService.updateStaff(editingStaff.id, updateData);
        toast.success('Usuario actualizado correctamente');
      } else {
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

  // Handle form data change
  const handleFormChange = (data: Partial<CreateStaffRequest>) => {
    setFormData(prev => ({ ...prev, ...data }));
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
      ) : (
        <StaffTable
          staff={staff}
          searchQuery={searchQuery}
          currentUserId={user?.id}
          onEdit={handleOpenEditModal}
          onDelete={handleDelete}
        />
      )}

      {/* Modal */}
      <UserFormModal
        isOpen={isModalOpen}
        editingStaff={editingStaff}
        formData={formData}
        roles={roles}
        onClose={handleCloseModal}
        onSubmit={handleSubmit}
        onChange={handleFormChange}
      />
    </div>
  );
};

export default StaffManagement;
