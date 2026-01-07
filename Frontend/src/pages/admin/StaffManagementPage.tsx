import { useState } from 'react';
import { Users, Shield } from 'lucide-react';
import StaffTable from '../../components/admin/StaffTable';
import PermissionsManager from '../../components/permissions/PermissionsManager';

export default function StaffManagementPage() {
  const [activeTab, setActiveTab] = useState<'team' | 'permissions'>('team');
  
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Administración de Personal
        </h1>
        <p className="text-gray-600 mt-1">
          Gestiona tu equipo y sus permisos
        </p>
      </div>
      
      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('team')}
            className={`
              group inline-flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm
              ${activeTab === 'team'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }
            `}
          >
            <Users className="w-5 h-5" />
            Miembros del Equipo
          </button>
          
          <button
            onClick={() => setActiveTab('permissions')}
            className={`
              group inline-flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm
              ${activeTab === 'permissions'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }
            `}
          >
            <Shield className="w-5 h-5" />
            Gestión de Permisos
          </button>
        </nav>
      </div>
      
      {/* Content */}
      {activeTab === 'team' && <StaffTable /* ...props */ />}
      {activeTab === 'permissions' && <PermissionsManager />}
    </div>
  );
}
