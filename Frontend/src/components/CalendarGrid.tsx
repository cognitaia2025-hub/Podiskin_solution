import React, { useState, useEffect } from 'react';
import { format, startOfWeek, addDays, eachDayOfInterval, isSameDay, isSameHour, addHours, setHours, setMinutes } from 'date-fns';
import { es } from 'date-fns/locale';
import { ChevronLeft, ChevronRight, Clock, Calendar as CalendarIcon, MoreVertical } from 'lucide-react';
import { useDroppable, useDraggable, DndContext, DragOverlay, useSensors, useSensor, PointerSensor } from '@dnd-kit/core';
import type { DragEndEvent } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import EventModal from './EventModal';
import type { Appointment, Doctor } from '../types/appointments';
import { getDoctors } from '../services/doctorService';
import { getPatients } from '../services/patientService';
import { getAppointments, createAppointment } from '../services/appointmentService';

// Utility to check overlap
const doEventsOverlap = (a: Appointment, b: Appointment) => {
    const startA = new Date(a.start).getTime();
    const endA = new Date(a.end).getTime();
    const startB = new Date(b.start).getTime();
    const endB = new Date(b.end).getTime();
    return startA < endB && endA > startB;
};

// Layout Algorithm
const calculateLayout = (appointments: Appointment[]) => {
    const layout: Record<string, { left: string, width: string, zIndex: number }> = {};
    if (appointments.length === 0) return layout;

    const sorted = [...appointments].sort((a, b) => {
        const startDiff = new Date(a.start).getTime() - new Date(b.start).getTime();
        if (startDiff !== 0) return startDiff;
        return new Date(b.end).getTime() - new Date(a.end).getTime();
    });

    const columns: Appointment[][] = [];

    sorted.forEach(event => {
        let placed = false;
        for (let i = 0; i < columns.length; i++) {
            const col = columns[i];
            const hasOverlap = col.some(e => doEventsOverlap(e, event));
            if (!hasOverlap) {
                col.push(event);
                placed = true;
                break;
            }
        }

        if (!placed) {
            columns.push([event]);
        }
    });

    const totalCols = columns.length;
    const colWidth = 95 / totalCols; // Use 95% to leave some padding

    columns.forEach((col, colIndex) => {
        col.forEach(event => {
            layout[event.id] = {
                left: `${colIndex * colWidth}%`,
                width: `${colWidth}%`,
                zIndex: colIndex + 10
            };
        });
    });

    return layout;
};

interface CalendarGridProps {
    triggerCreate?: boolean;
    appointments?: Appointment[];
    doctors?: Doctor[];
    onSave?: (appt: Partial<Appointment>) => void;
}

interface DroppableSlotProps {
    day: Date;
    hour: number;
    onSlotClick: (day: Date, hour: number, minute?: number) => void;
    children: React.ReactNode;
    doctors?: Doctor[];
}

interface DraggableEventProps {
    appointment: Appointment;
    topOffset: number;
    height: number;
    onClick: (e: React.MouseEvent, appt: Appointment) => void;
    styleOverrides?: { left: string, width: string, zIndex?: number };
}

const DroppableSlot: React.FC<DroppableSlotProps> = ({ day, hour, children, onSlotClick }) => {
    const { setNodeRef, isOver } = useDroppable({
        id: `${format(day, 'yyyy-MM-dd')}-${hour}`,
        data: { day, hour }
    });

    return (
        <div
            ref={setNodeRef}
            className={clsx(
                "h-20 border-b border-gray-50 transition-colors cursor-pointer group relative",
                isOver ? "bg-primary-50 ring-2 ring-primary-300" : "hover:bg-gray-50",
                // Simple visual queue for non-working hours (e.g. before 9am or after 6pm generically for now, or could pass doctor specific)
                (hour < 9 || hour > 18) && "bg-gray-50/50"
            )}
            onClick={() => onSlotClick(day, hour)}
        >
            <div className="hidden group-hover:flex w-full h-full items-center justify-center opacity-50">
                <span className="text-primary-300 font-bold">+</span>
            </div>
            {children}
        </div>
    );
};

const DraggableEvent: React.FC<DraggableEventProps> = ({ appointment, topOffset, height, onClick, styleOverrides }) => {
    const { attributes, listeners, setNodeRef, isDragging } = useDraggable({
        id: appointment.id,
        data: appointment
    });

    const bgColor = appointment.color || '#3B82F6';
    const borderColor = appointment.color ? `${appointment.color}CC` : '#2563EB';

    return (
        <div
            ref={setNodeRef}
            {...listeners}
            {...attributes}
            className={clsx(
                "absolute rounded-md p-1 text-xs shadow-sm cursor-grab active:cursor-grabbing hover:shadow-md transition-shadow z-10 overflow-hidden flex flex-col pointer-events-auto",
                isDragging && "opacity-50"
            )}
            style={{
                top: `${topOffset}px`,
                height: `${height}px`,
                backgroundColor: `${bgColor}20`,
                borderLeft: `4px solid ${borderColor}`,
                color: '#1F2937',
                left: styleOverrides?.left || '2.5%',
                width: styleOverrides?.width || '95%',
                zIndex: styleOverrides?.zIndex || 10
            }}
            onClick={(e) => {
                e.stopPropagation();
                onClick(e, appointment);
            }}
        >
            <div className="font-bold truncate text-[10px]">{appointment.title}</div>
            <div className="opacity-75 truncate text-[9px]">
                {format(new Date(appointment.start), 'HH:mm')} - {format(new Date(appointment.end), 'HH:mm')}
            </div>
        </div>
    );
};

const CalendarGrid: React.FC<CalendarGridProps> = ({ triggerCreate, appointments: propAppointments, doctors: propDoctors, onSave }) => {
    const [localAppointments, setLocalAppointments] = useState<Appointment[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedAppointment, setSelectedAppointment] = useState<Partial<Appointment> | undefined>(undefined);
    const [activeId, setActiveId] = useState<string | null>(null);
    const [doctors, setDoctors] = useState<Doctor[]>(propDoctors || []);
    const [patients, setPatients] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    // Load doctors if not provided
    useEffect(() => {
        if (!propDoctors || propDoctors.length === 0) {
            const loadDoctors = async () => {
                try {
                    const fetchedDoctors = await getDoctors();
                    setDoctors(fetchedDoctors);
                } catch (error) {
                    console.error('Error loading doctors:', error);
                }
            };
            loadDoctors();
        }
    }, [propDoctors]);

    // Load patients
    useEffect(() => {
        const loadPatients = async () => {
            setIsLoading(true);
            try {
                const response = await getPatients(1, 100);
                setPatients(response.patients || []);
            } catch (error) {
                console.error('Error loading patients:', error);
                setPatients([]);
            } finally {
                setIsLoading(false);
            }
        };
        loadPatients();
    }, []);

    // Use prop appointments if available, otherwise use local state (legacy behavior support)
    const appointments = propAppointments || localAppointments;

    const today = new Date();
    const startOfCurrentWeek = startOfWeek(today, { weekStartsOn: 1 });
    const weekDays = eachDayOfInterval({
        start: startOfCurrentWeek,
        end: addDays(startOfCurrentWeek, 6),
    });

    const hours = Array.from({ length: 13 }, (_, i) => i + 8);

    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: {
                distance: 8,
            },
        })
    );

    useEffect(() => {
        if (!propAppointments) {
            getAppointments().then(setLocalAppointments);
        }
    }, [propAppointments]);

    useEffect(() => {
        if (triggerCreate) {
            const now = new Date();
            // Round to next 30 mins
            const minutes = now.getMinutes();
            const roundedMinutes = minutes > 30 ? 0 : 30;
            const start = setMinutes(now, roundedMinutes);
            if (minutes > 30) start.setHours(start.getHours() + 1);

            const end = addHours(start, 0.5);

            const defaultDoctor = doctors.length > 0 ? doctors[0].id : '';

            setSelectedAppointment({
                start,
                end,
                fecha_hora_inicio: start, // Sync new fields
                fecha_hora_fin: end,
                tipo_cita: 'Consulta',
                estado: 'Pendiente',
                id_podologo: defaultDoctor,
                color: '#3B82F6' // Default color
            });
            setIsModalOpen(true);
        }
    }, [triggerCreate, doctors]);

    const handleSlotClick = (day: Date, hour: number) => {
        const start = setMinutes(setHours(day, hour), 0);
        const end = addHours(start, 0.5); // Default 30 min duration

        // Default to first doctor available or generic
        const defaultDoctor = doctors.length > 0 ? doctors[0].id : '';

        setSelectedAppointment({
            start,
            end,
            fecha_hora_inicio: start,
            fecha_hora_fin: end,
            tipo_cita: 'Consulta',
            estado: 'Pendiente',
            id_podologo: defaultDoctor,
            color: '#3B82F6'
        });
        setIsModalOpen(true);
    };

    const handleAppointmentClick = (e: React.MouseEvent, appt: Appointment) => {
        e.stopPropagation();
        setSelectedAppointment(appt);
        setIsModalOpen(true);
    };

    const handleSaveAppointment = async (apptData: Partial<Appointment>) => {
        // If controlled via props (onSave exists), use it
        if (onSave) {
            onSave(apptData);
            setIsModalOpen(false);
            return;
        }

        // Legacy local state handling (fallback)
        if (apptData.id) {
            const updatedAppt = { ...selectedAppointment, ...apptData } as Appointment;
            // Update local state
            setLocalAppointments(prev => prev.map(a => a.id === updatedAppt.id ? updatedAppt : a));
        } else {
            // New appointment
            const newAppt = await createAppointment(apptData as any);
            setLocalAppointments(prev => [...prev, newAppt]);
        }
        setIsModalOpen(false);
    };

    const handleDragStart = (event: any) => {
        setActiveId(event.active.id);
    };

    const handleDragEnd = (event: any) => {
        const { active, over } = event;

        if (over && active.id !== over.id) {
            const activeAppt = appointments.find(a => a.id === active.id);
            const { day, hour } = over.data.current || {};

            if (activeAppt && day && hour !== undefined) {
                // Calculate new start time based on drop slot
                const newStart = setMinutes(setHours(day, hour), 0);
                // Calculate duration to keep it same
                const duration = new Date(activeAppt.end).getTime() - new Date(activeAppt.start).getTime();
                const newEnd = new Date(newStart.getTime() + duration);

                const updatedAppt = {
                    ...activeAppt,
                    start: newStart,
                    end: newEnd,
                    fecha_hora_inicio: newStart,
                    fecha_hora_fin: newEnd
                };

                // Use onSave if available to persist change
                if (onSave) {
                    onSave(updatedAppt);
                } else {
                    setLocalAppointments(prev => prev.map(a => a.id === updatedAppt.id ? updatedAppt : a));
                }
            }
        }
        setActiveId(null);
    };

    const activeAppointment = activeId ? appointments.find(a => a.id === activeId) : null;

    // Memoized layout calculation per day
    const dayLayouts = React.useMemo(() => {
        const layouts: Record<string, { left: string, width: string, zIndex: number }> = {};

        const eventsByDay: Record<string, Appointment[]> = {};
        appointments.forEach(appt => {
            const dayKey = format(new Date(appt.start), 'yyyy-MM-dd');
            if (!eventsByDay[dayKey]) eventsByDay[dayKey] = [];
            eventsByDay[dayKey].push(appt);
        });

        Object.keys(eventsByDay).forEach(dayKey => {
            const dayEvents = eventsByDay[dayKey];
            const dayLayout = calculateLayout(dayEvents);
            Object.assign(layouts, dayLayout);
        });

        return layouts;
    }, [appointments]);

    return (
        <DndContext sensors={sensors} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
            <div className="flex flex-col h-full relative">
                <div className="flex border-b border-gray-200">
                    <div className="w-16 border-r border-gray-100 bg-gray-50 flex-shrink-0"></div>
                    <div className="flex-1 grid grid-cols-7">
                        {weekDays.map((day) => (
                            <div
                                key={day.toString()}
                                className={twMerge(
                                    "py-3 text-center border-r border-gray-100 last:border-r-0 flex flex-col items-center justify-center",
                                    isSameDay(day, today) ? "bg-blue-50/30" : ""
                                )}
                            >
                                <span className={clsx("text-xs font-semibold uppercase mb-1", isSameDay(day, today) ? "text-primary-600" : "text-gray-500")}>
                                    {format(day, 'EEE', { locale: es })}
                                </span>
                                <div
                                    className={clsx(
                                        "w-8 h-8 flex items-center justify-center rounded-full text-lg",
                                        isSameDay(day, today)
                                            ? "bg-primary-600 text-white font-bold shadow-md"
                                            : "text-gray-700"
                                    )}
                                >
                                    {format(day, 'd')}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto flex relative">
                    <div className="w-16 flex-shrink-0 border-r border-gray-100 bg-white">
                        {hours.map((hour) => (
                            <div key={hour} className="h-20 border-b border-gray-50 relative">
                                <span className="absolute -top-3 right-2 text-xs text-gray-400 font-medium">
                                    {hour}:00
                                </span>
                            </div>
                        ))}
                    </div>

                    <div className="flex-1 grid grid-cols-7 relative min-w-[800px]">
                        {weekDays.map((day) => (
                            <div key={day.toString()} className="border-r border-gray-100 relative h-full">
                                {hours.map((hour) => (
                                    <DroppableSlot
                                        key={`${day}-${hour}`}
                                        day={day}
                                        hour={hour}
                                        onSlotClick={handleSlotClick}
                                        doctors={doctors}
                                    >
                                        {appointments
                                            .filter(appt =>
                                                isSameDay(new Date(appt.start), day) &&
                                                new Date(appt.start).getHours() === hour
                                            )
                                            .map(appt => {
                                                const startMin = new Date(appt.start).getMinutes();
                                                const durationMinutes = (new Date(appt.end).getTime() - new Date(appt.start).getTime()) / (1000 * 60);
                                                const topOffset = (startMin / 60) * 80; // 80px height per hour slot
                                                const height = (durationMinutes / 60) * 80;
                                                const layout = dayLayouts[appt.id];

                                                return (
                                                    <DraggableEvent
                                                        key={appt.id}
                                                        appointment={appt}
                                                        topOffset={topOffset}
                                                        height={height}
                                                        onClick={(e) => handleAppointmentClick(e, appt)}
                                                        styleOverrides={layout}
                                                    />
                                                );
                                            })
                                        }
                                    </DroppableSlot>
                                ))}
                            </div>
                        ))}
                    </div>
                </div>

                <EventModal
                    isOpen={isModalOpen}
                    onClose={() => setIsModalOpen(false)}
                    onSave={handleSaveAppointment}
                    initialData={selectedAppointment}
                    doctors={doctors}
                    patients={patients}
                />

                <DragOverlay>
                    {activeAppointment ? (
                        <div
                            className="rounded-md p-2 text-xs shadow-lg opacity-90"
                            style={{
                                backgroundColor: `${activeAppointment.color || '#3B82F6'}40`,
                                borderLeft: `4px solid ${activeAppointment.color || '#2563EB'}`,
                                width: '200px',
                                color: '#1F2937'
                            }}
                        >
                            <div className="font-bold">{activeAppointment.title}</div>
                            <div className="opacity-75 text-[10px]">
                                {format(new Date(activeAppointment.start), 'HH:mm')}
                            </div>
                        </div>
                    ) : null}
                </DragOverlay>
            </div>
        </DndContext>
    );
};

export default CalendarGrid;
