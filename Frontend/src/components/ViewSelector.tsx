import { Calendar, CalendarDays, Grid3x3, List, User } from 'lucide-react';

export type ViewType = 'day' | 'week' | 'month' | 'agenda' | 'staff';

interface ViewSelectorProps {
    currentView: ViewType;
    onViewChange: (view: ViewType) => void;
}

const ViewSelector: React.FC<ViewSelectorProps> = ({ currentView, onViewChange }) => {
    const views: { type: ViewType; label: string; icon: React.ReactNode }[] = [
        { type: 'day', label: 'Día', icon: <Calendar className="w-4 h-4" /> },
        { type: 'week', label: 'Semana', icon: <CalendarDays className="w-4 h-4" /> },
        { type: 'month', label: 'Mes', icon: <Grid3x3 className="w-4 h-4" /> },
        { type: 'agenda', label: 'Agenda', icon: <List className="w-4 h-4" /> },
        { type: 'staff', label: 'Disponibilidad', icon: <User className="w-4 h-4" /> },
    ];

    return (
        <div className="flex bg-gray-100 rounded-lg p-1 gap-1">
            {views.map((view) => (
                <button
                    key={view.type}
                    onClick={() => onViewChange(view.type)}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all ${currentView === view.type
                        ? 'bg-white text-primary-700 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                        }`}
                >
                    {view.icon}
                    <span className="hidden sm:inline">{view.label}</span>
                </button>
            ))}
        </div>
    );
};

export default ViewSelector;
