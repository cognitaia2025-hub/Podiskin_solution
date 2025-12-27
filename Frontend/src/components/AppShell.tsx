import React from 'react';
import { Outlet } from 'react-router-dom';
import DynamicLogo from './DynamicLogo';
import GlobalNavigation from './GlobalNavigation';
import { useShell } from '../context/ShellContext';

const AppShell: React.FC = () => {
    const { sidebarContent } = useShell();

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
                <div className="flex items-center space-x-4">
                    <div className="hidden sm:flex items-center space-x-2">
                        <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 text-xs font-bold ring-2 ring-white">
                            PS
                        </div>
                        <span className="text-sm font-medium text-gray-700">Admin</span>
                    </div>
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
