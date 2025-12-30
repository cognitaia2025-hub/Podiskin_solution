/**
 * AppLayout - Unified Global Layout
 * 
 * This layout wraps all authenticated routes and ensures:
 * - Persistent navigation across all sections
 * - Consistent header and sidebar
 * - Global state management
 */

import React from 'react';
import { Outlet } from 'react-router-dom';
import DynamicLogo from '../components/DynamicLogo';
import GlobalNavigation from '../components/GlobalNavigation';
import { useGlobalContext } from '../context/GlobalContext';
import { useAuth } from '../auth/AuthContext';
import { LogOut, User } from 'lucide-react';

const AppLayout: React.FC = () => {
  const { sidebarContent } = useGlobalContext();
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = React.useState(false);
  
  const handleLogout = () => {
    logout();
    setShowUserMenu(false);
  };
  
  // Get user initials
  const getUserInitials = () => {
    if (!user) return '??';
    const names = user.nombre_completo.split(' ');
    if (names.length >= 2) {
      return `${names[0][0]}${names[1][0]}`.toUpperCase();
    }
    return user.nombre_completo.substring(0, 2).toUpperCase();
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 overflow-hidden text-gray-900 font-sans">
      {/* Global Top Header */}
      <header className="h-16 bg-white border-b border-gray-200 flex items-center px-4 shrink-0 z-50 shadow-sm">
        <div className="flex items-center space-x-3 w-60">
          <DynamicLogo />
          <div className="flex flex-col">
            <span className="text-xl font-bold text-gray-800 tracking-tight leading-none">
              Podoskin
            </span>
            <span className="text-[10px] text-primary-500 font-medium tracking-widest uppercase mt-0.5">
              Especialistas
            </span>
          </div>
        </div>

        {/* Horizontal Navigation */}
        <div className="flex-1 ml-4 self-stretch">
          <GlobalNavigation />
        </div>

        {/* Top Right Actions - User Menu */}
        <div className="flex items-center space-x-4 relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center space-x-2 hover:bg-gray-100 rounded-lg px-3 py-2 transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 text-xs font-bold ring-2 ring-white">
              {getUserInitials()}
            </div>
            <div className="hidden sm:flex flex-col items-start">
              <span className="text-sm font-medium text-gray-700">
                {user?.nombre_completo || 'Usuario'}
              </span>
              <span className="text-xs text-gray-500">{user?.rol || 'Rol'}</span>
            </div>
          </button>
          
          {/* User Dropdown Menu */}
          {showUserMenu && (
            <div className="absolute right-0 top-12 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
              <div className="px-4 py-3 border-b border-gray-100">
                <p className="text-sm font-medium text-gray-900">{user?.nombre_completo}</p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
              <button
                onClick={handleLogout}
                className="w-full px-4 py-2 text-sm text-left text-red-600 hover:bg-red-50 flex items-center space-x-2"
              >
                <LogOut className="w-4 h-4" />
                <span>Cerrar Sesión</span>
              </button>
            </div>
          )}
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Global Sidebar (Conditional content) */}
        {sidebarContent && (
          <aside className="w-64 bg-white border-r border-gray-200 hidden md:flex flex-col animate-fadeIn">
            <div id="sidebar-content" className="flex-1 overflow-y-auto">
              {sidebarContent}
            </div>
          </aside>
        )}

        {/* Main Content Area */}
        <main className="flex-1 overflow-auto bg-gray-50 relative">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
