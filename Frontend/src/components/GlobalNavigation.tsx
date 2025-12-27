import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Calendar, FileText, FolderOpen, DollarSign, TrendingUp } from 'lucide-react';
import { clsx } from 'clsx';

interface NavigationTab {
    id: string;
    label: string;
    path: string;
    icon: React.ComponentType<{ className?: string }>;
    enabled: boolean;
}

const NAVIGATION_TABS: NavigationTab[] = [
    {
        id: 'records',
        label: 'Expedientes médicos',
        path: '/records',
        icon: FolderOpen,
        enabled: false, // Placeholder
    },
    {
        id: 'medical',
        label: 'Atención médica',
        path: '/medical',
        icon: FileText,
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
        enabled: false, // Placeholder
    },
    {
        id: 'finances',
        label: 'Finanzas Adm',
        path: '/finances',
        icon: TrendingUp,
        enabled: false, // Placeholder
    },
];

const GlobalNavigation: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const isActiveTab = (path: string) => {
        return location.pathname.startsWith(path);
    };

    const handleTabClick = (tab: NavigationTab) => {
        if (tab.enabled) {
            navigate(tab.path);
        }
    };

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
            </div>
        </nav>
    );
};

export default GlobalNavigation;
