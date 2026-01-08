import React, { type ReactNode } from 'react';
import { Menu, Search, HelpCircle, Settings, ChevronLeft, ChevronRight } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import ViewSelector, { type ViewType } from './ViewSelector';
import { useGlobalContext } from '../context/GlobalContext';

interface LayoutProps {
    children: ReactNode;
    onCreateClick?: () => void;
    currentView?: ViewType;
    onViewChange?: (view: ViewType) => void;
    selectedDoctors?: string[];
    onDoctorFilterChange?: (doctorId: string) => void;
    onTodayClick?: () => void;
    onSearch?: (query: string) => void;
    doctors?: Array<{ id: string; name: string; color?: string }>;
}

/**
 * Layout - Calendar Content Wrapper
 * 
 * This component manages calendar-specific sidebar content and toolbar.
 * The global header and navigation are handled by AppLayout.
 */
const Layout: React.FC<LayoutProps> = ({
    children,
    onCreateClick,
    currentView = 'week',
    onViewChange,
    selectedDoctors = [],
    onDoctorFilterChange,
    onTodayClick,
    onSearch,
    doctors = []
}) => {
    const [searchValue, setSearchValue] = React.useState('');
    const { setSidebarContent } = useGlobalContext();

    // Inject sidebar content for calendar
    React.useEffect(() => {
        setSidebarContent(
            <div className="p-4 flex-1 overflow-y-auto">
                <div className="mb-6">
                    <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-2">Mis Calendarios</h3>
                    <div className="space-y-2">
                        {doctors.length > 0 ? (
                            doctors.map((doctor) => (
                                <div key={doctor.id} className="flex items-center px-2 py-1 text-gray-700 hover:bg-gray-100 rounded-md cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={selectedDoctors.includes(doctor.id)}
                                        onChange={() => onDoctorFilterChange?.(doctor.id)}
                                        className="rounded text-primary-600 focus:ring-primary-500 mr-3 border-gray-300"
                                    />
                                    <span className="text-sm">{doctor.name}</span>
                                </div>
                            ))
                        ) : (
                            <div className="px-2 py-3 text-sm text-gray-500 text-center">
                                No hay podólogos disponibles
                            </div>
                        )}
                    </div>
                </div>
            </div>
        );

        // Cleanup: remove content when leaving calendar
        return () => setSidebarContent(null);
    }, [selectedDoctors, onDoctorFilterChange, setSidebarContent, doctors]);

    const handleSearchSubmit = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && onSearch) {
            onSearch(searchValue);
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-50 min-w-0">
            {/* Calendar Toolbar - integrated into global layout */}
            <div className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-4 lg:px-8 shrink-0">
                <div className="flex items-center">
                    <button className="md:hidden p-2 mr-2 text-gray-600 hover:bg-gray-100 rounded-full">
                        <Menu className="w-5 h-5" />
                    </button>
                    <button
                        onClick={onTodayClick}
                        className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 mr-4"
                    >
                        Hoy
                    </button>
                    <div className="flex items-center space-x-1 mr-4">
                        <button className="p-1 rounded-full hover:bg-gray-100 text-gray-600">
                            <ChevronLeft className="w-5 h-5" />
                        </button>
                        <button className="p-1 rounded-full hover:bg-gray-100 text-gray-600">
                            <ChevronRight className="w-5 h-5" />
                        </button>
                    </div>
                    <h1 className="text-xl font-medium text-gray-800 hidden sm:block">
                        {format(new Date(), 'MMMM yyyy', { locale: es }).replace(/^\w/, (c) => c.toUpperCase())}
                    </h1>
                </div>
                <div className="flex items-center gap-4">
                    {/* Global Create Button */}
                    <button
                        onClick={onCreateClick}
                        className="hidden md:flex bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium items-center shadow-sm transition-all active:scale-95"
                    >
                        <span className="text-lg mr-1 font-light leading-none">+</span> Agendar Cita
                    </button>
                </div>

                {/* View Selector */}
                {onViewChange && (
                    <div className="hidden lg:block">
                        <ViewSelector currentView={currentView} onViewChange={onViewChange} />
                    </div>
                )}

                <div className="flex items-center space-x-2 sm:space-x-4">
                    <div className="hidden md:flex items-center bg-gray-100 rounded-md px-3 py-2 transition-colors focus-within:ring-2 focus-within:ring-primary-500 focus-within:bg-white border border-transparent focus-within:border-primary-300">
                        <Search className="w-4 h-4 text-gray-500 mr-2" />
                        <input
                            type="text"
                            placeholder="Buscar..."
                            className="bg-transparent border-none focus:ring-0 text-sm p-0 w-32 focus:w-48 transition-all outline-none text-gray-700 placeholder-gray-400"
                            value={searchValue}
                            onChange={(e) => setSearchValue(e.target.value)}
                            onKeyDown={handleSearchSubmit}
                        />
                    </div>
                    <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-full">
                        <HelpCircle className="w-5 h-5" />
                    </button>
                    <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-full">
                        <Settings className="w-5 h-5" />
                    </button>
                </div>
            </div>

            {/* Calendar Content Area */}
            <main className="flex-1 overflow-auto bg-white relative">
                {children}
            </main>
        </div>
    );
};

export default Layout;
