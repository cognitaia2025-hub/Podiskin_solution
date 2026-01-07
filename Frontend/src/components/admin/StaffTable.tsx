/**
 * StaffTable Component
 * Location: Frontend/src/components/admin/StaffTable.tsx
 * 
 * Displays the list of staff members in a table format.
 * Handles search filtering and user actions (edit, delete).
 */

import React, { useState } from 'react';
import { Edit2, Trash2, Mail, Shield, UserCheck, UserX } from 'lucide-react';
import type { StaffMember } from '../../services/staffService';
import { StaffEditModal } from './StaffEditModal';
import { PodologistPatientsModal } from './PodologistPatientsModal';

interface StaffTableProps {
  staff: StaffMember[];
  searchQuery: string;
  currentUserId?: number;
  onEdit: (member: StaffMember) => void;
  onDelete: (member: StaffMember) => void;
}

const StaffTable: React.FC<StaffTableProps> = ({
  staff,
  searchQuery,
  currentUserId,
  onEdit,
  onDelete,
}) => {
  const [editingMember, setEditingMember] = useState<StaffMember | null>(null);
  const [managingPatients, setManagingPatients] = useState<StaffMember | null>(null);

  // Filter staff by search query
  const filteredStaff = staff.filter(member => 
    member.nombre_completo.toLowerCase().includes(searchQuery.toLowerCase()) ||
    member.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    member.nombre_usuario.toLowerCase().includes(searchQuery.toLowerCase())
  );

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

  if (filteredStaff.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-12 text-center">
        <Shield className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No se encontraron usuarios
        </h3>
        <p className="text-gray-600">
          {searchQuery ? 'Intenta con otra búsqueda' : 'Agrega el primer miembro del equipo'}
        </p>
      </div>
    );
  }

  const handleEdit = (member: StaffMember) => {
    setEditingMember(member);
  };

  const handleSave = (member: StaffMember) => {
    onEdit(member);
    setEditingMember(null);
  };

  const handleManagePatients = (member: StaffMember) => {
    setManagingPatients(member);
  };

  const handleSavePatientAssignment = (patientId: number, podologoId: number | null) => {
    // TODO: Llamar a API para guardar asignación
    console.log(`Paciente ${patientId} asignado a podólogo ${podologoId}`);
  };

  return (
    <>
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
                    onClick={() => handleEdit(member)}
                    className="text-blue-600 hover:text-blue-900 mr-4"
                    title="Editar"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  {member.activo && member.id !== currentUserId && (
                    <button
                      onClick={() => onDelete(member)}
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

      {/* Modales */}
      {editingMember && (
        <StaffEditModal
          member={editingMember}
          onClose={() => setEditingMember(null)}
          onSave={handleSave}
          onManagePatients={handleManagePatients}
        />
      )}

      {managingPatients && (
        <PodologistPatientsModal
          podologo={managingPatients}
          onClose={() => setManagingPatients(null)}
          onSave={handleSavePatientAssignment}
        />
      )}
    </>
  );
};

export default StaffTable;
