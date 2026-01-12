import React, { useState } from 'react';
import { useNavigate, useLocation, NavLink } from 'react-router-dom';
import { Calendar, FileText, FolderOpen, DollarSign, TrendingUp, BarChart3, Users, Package, Coins, ChevronDown, Stethoscope, MessageSquare } from 'lucide-react';
import { clsx } from 'clsx';
import { useAuth } from '../auth/AuthContext';

interface NavigationTab {
    id: string;
    label: string;
    path: string;
    icon: React.ComponentType<{ className?: string }>;
    enabled: boolean;
}

const NAVIGATION_TABS: NavigationTab[] = [
    {
        id: 'dashboard',
        label: 'Dashboard',
        path: '/dashboard',
        icon: BarChart3,
        enabled: true,
    },
    {
        id: 'calendar',
        label: 'Calendario',
        path: '/calendar',
        icon: Calendar,
        enabled: true,
    },
    {
        id: 'billing',
        label: 'Gestión de cobros',
        path: '/billing',
        icon: DollarSign,
        enabled: true,
    },
    {
        id: 'finances',
        label: 'Finanzas Adm',
        path: '/finances',
        icon: TrendingUp,
        enabled: true,
    },
    {
        id: 'whatsapp',
        label: 'WhatsApp',
        path: '/whatsapp',
        icon: MessageSquare,
        enabled: true,
    },
];

const ADMIN_TABS = [
    {
        id: 'staff',
        label: 'Equipo',
        path: '/admin/staff',
        icon: Users,
    },
    {
        id: 'inventory',
        label: 'Inventario',
        path: '/admin/inventory',
        icon: Package,
    },
    {
        id: 'services',
        label: 'Servicios',
        path: '/admin/services',
        icon: Coins,
    },
];

const GlobalNavigation: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { user } = useAuth();
    const [medicalMenuOpen, setMedicalMenuOpen] = useState(false);

    const isActiveTab = (path: string) => {
        return location.pathname.startsWith(path);
    };

    const handleTabClick = (tab: NavigationTab) => {
        if (tab.enabled) {
            navigate(tab.path);
        }
    };

    const isMedicalActive = location.pathname.startsWith('/medical') || location.pathname.startsWith('/records');

    return (
        <nav className="h-full flex items-center">
            <div className="flex items-center gap-1 px-4 h-full">
                {NAVIGATION_TABS.map((tab) => {
                    const Icon = tab.icon;
                    const isActive = isActiveTab(tab.path);

                    return (
                        <button
                            key={tab.id}
                            onClick={() => handleTabClick(tab)}
                            disabled={!tab.enabled}
                            className={clsx(
                                'flex items-center gap-2 px-4 h-full text-sm font-medium transition-all relative outline-none',
                                isActive && tab.enabled
                                    ? 'text-primary-700 border-b-2 border-primary-600 bg-primary-50/30'
                                    : tab.enabled
                                        ? 'text-gray-500 border-b-2 border-transparent hover:text-gray-800 hover:bg-gray-50/50'
                                        : 'text-gray-400 border-b-2 border-transparent cursor-not-allowed opacity-60'
                            )}
                        >
                            <Icon className={clsx(
                                'w-4 h-4',
                                isActive && tab.enabled ? 'text-primary-600' : ''
                            )} />
                            <span>{tab.label}</span>
                            {!tab.enabled && (
                                <span className="ml-1 text-[10px] bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded leading-none">
                                    Soon
                                </span>
                            )}
                        </button>
                    );
                })}

                {/* Menú Gestión Médica con dropdown */}
                <div className="relative h-full">
                    <button
                        onClick={() => setMedicalMenuOpen(!medicalMenuOpen)}
                        onBlur={() => setTimeout(() => setMedicalMenuOpen(false), 200)}
                        className={clsx(
                            'flex items-center gap-2 px-4 h-full text-sm font-medium transition-all relative outline-none',
                            isMedicalActive
                                ? 'text-primary-700 border-b-2 border-primary-600 bg-primary-50/30'
                                : 'text-gray-500 border-b-2 border-transparent hover:text-gray-800 hover:bg-gray-50/50'
                        )}
                    >
                        <Stethoscope className={clsx(
                            'w-4 h-4',
                            isMedicalActive ? 'text-primary-600' : ''
                        )} />
                        <span>Gestión Médica</span>
                        <ChevronDown className={clsx(
                            'w-3 h-3 transition-transform',
                            medicalMenuOpen && 'rotate-180'
                        )} />
                    </button>

                    {/* Dropdown */}
                    {medicalMenuOpen && (
                        <div className="absolute top-full left-0 mt-0 bg-white shadow-lg border border-gray-200 rounded-b-lg min-w-[200px] z-50">
                            <button
                                onClick={() => {
                                    navigate('/medical/attention');
                                    setMedicalMenuOpen(false);
                                }}
                                className="w-full px-4 py-3 text-left text-sm hover:bg-gray-50 flex items-center gap-2 text-gray-700 hover:text-primary-600"
                            >
                                <FileText className="w-4 h-4" />
                                <span>Atención Médica</span>
                            </button>
                            <button
                                onClick={() => {
                                    navigate('/medical/records');
                                    setMedicalMenuOpen(false);
                                }}
                                className="w-full px-4 py-3 text-left text-sm hover:bg-gray-50 flex items-center gap-2 text-gray-700 hover:text-primary-600 border-t border-gray-100"
                            >
                                <FolderOpen className="w-4 h-4" />
                                <span>Expedientes Médicos</span>
                            </button>
                        </div>
                    )}
                </div>
            </div>
            {/* Sección Administración solo para admin/manager */}
            {(user?.rol === 'Admin' || user?.rol === 'Manager') && (
                <div className="flex items-center gap-1 px-4 h-full border-l border-gray-200 ml-4">
                    <span className="text-xs text-gray-400 uppercase font-bold mr-2">Administración</span>
                    {ADMIN_TABS.map((tab) => {
                        const Icon = tab.icon;
                        return (
                            <NavLink
                                key={tab.id}
                                to={tab.path}
                                className={({ isActive }) =>
                                    clsx(
                                        'flex items-center gap-2 px-4 h-full text-sm font-medium transition-all relative outline-none',
                                        isActive
                                            ? 'text-primary-700 border-b-2 border-primary-600 bg-primary-50/30'
                                            : 'text-gray-500 border-b-2 border-transparent hover:text-gray-800 hover:bg-gray-50/50'
                                    )
                                }
                            >
                                <Icon className="w-4 h-4" />
                                <span>{tab.label}</span>
                            </NavLink>
                        );
                    })}
                </div>
            )}
        </nav>
    );
};

export default GlobalNavigation;
