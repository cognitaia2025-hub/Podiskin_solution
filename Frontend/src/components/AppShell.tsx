import React, { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import DynamicLogo from './DynamicLogo';
import GlobalNavigation from './GlobalNavigation';
import { useShell } from '../context/ShellContext';
import { useAuth } from '../auth/AuthContext';

const AppShell: React.FC = () => {
    const { sidebarContent } = useShell();
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [showUserMenu, setShowUserMenu] = useState(false);

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    // Get user initials for avatar
    const getUserInitials = () => {
        if (!user) return 'U';
        if (user.nombre_completo) {
            const parts = user.nombre_completo.split(' ');
            return parts.length > 1 
                ? `${parts[0][0]}${parts[1][0]}`.toUpperCase()
                : parts[0][0].toUpperCase();
        }
        return user.username[0].toUpperCase();
    };

    return (
        <div className="flex flex-col h-screen bg-gray-50 overflow-hidden text-gray-900 font-sans">
            {/* Global Top Header */}
            <header className="h-16 bg-white border-b border-gray-200 flex items-center px-4 shrink-0 z-50 shadow-sm">
                <div className="flex items-center space-x-3 w-60">
                    <DynamicLogo />
                    <div className="flex flex-col">
                        <span className="text-xl font-bold text-gray-800 tracking-tight leading-none">Podoskin</span>
                        <span className="text-[10px] text-primary-500 font-medium tracking-widest uppercase mt-0.5">Especialistas</span>
                    </div>
                </div>

                {/* Horizontal Navigation */}
                <div className="flex-1 ml-4 self-stretch">
                    <GlobalNavigation />
                </div>

                {/* Top Right Actions */}
                <div className="flex items-center space-x-4 relative">
                    <div className="hidden sm:flex items-center space-x-2">
                        <button
                            onClick={() => setShowUserMenu(!showUserMenu)}
                            className="flex items-center space-x-2 hover:bg-gray-50 rounded-lg px-3 py-2 transition-colors"
                        >
                            <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 text-xs font-bold ring-2 ring-white">
                                {getUserInitials()}
                            </div>
                            <div className="flex flex-col items-start">
                                <span className="text-sm font-medium text-gray-700">
                                    {user?.nombre_completo || user?.username || 'Usuario'}
                                </span>
                                <span className="text-xs text-gray-500 capitalize">
                                    {user?.rol || 'Usuario'}
                                </span>
                            </div>
                            <svg
                                className={`w-4 h-4 text-gray-400 transition-transform ${showUserMenu ? 'rotate-180' : ''}`}
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>
                    </div>

                    {/* User Menu Dropdown */}
                    {showUserMenu && (
                        <>
                            <div
                                className="fixed inset-0 z-10"
                                onClick={() => setShowUserMenu(false)}
                            />
                            <div className="absolute right-0 top-12 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-20">
                                <div className="px-4 py-3 border-b border-gray-200">
                                    <p className="text-sm font-medium text-gray-900">
                                        {user?.nombre_completo || user?.username}
                                    </p>
                                    <p className="text-xs text-gray-500 mt-1">{user?.email}</p>
                                </div>
                                <button
                                    onClick={handleLogout}
                                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                                >
                                    <svg
                                        className="w-4 h-4"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                                        />
                                    </svg>
                                    <span>Cerrar Sesión</span>
                                </button>
                            </div>
                        </>
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

                {/* Main Area */}
                <main className="flex-1 overflow-auto bg-gray-50 relative">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default AppShell;
