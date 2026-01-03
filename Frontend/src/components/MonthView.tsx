import React, { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, startOfWeek, endOfWeek, setHours, setMinutes } from 'date-fns';
import { es } from 'date-fns/locale';
import type { Appointment, Doctor, Patient } from '../types/appointments';
import EventModal from './EventModal';
import { clsx } from 'clsx';

interface MonthViewProps {
    selectedDate: Date;
    appointments: Appointment[];
    doctors: Doctor[];
    patients: Patient[];
    onSave: (appt: Partial<Appointment>) => void;
    onDayClick: (date: Date) => void;
    triggerCreate?: boolean;
}

const MonthView: React.FC<MonthViewProps> = ({ selectedDate, appointments, doctors, patients, onSave, onDayClick, triggerCreate }) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedAppointment, setSelectedAppointment] = useState<Partial<Appointment> | undefined>(undefined);

    useEffect(() => {
        if (triggerCreate) {
            const now = new Date();
            const minutes = now.getMinutes();
            const roundedMinutes = minutes > 30 ? 0 : 30;
            const start = setMinutes(now, roundedMinutes);
            if (minutes > 30) start.setHours(start.getHours() + 1);
            const end = new Date(start.getTime() + 30 * 60000);

            setSelectedAppointment({
                fecha_hora_inicio: start,
                fecha_hora_fin: end,
                start,
                end,
                id_podologo: doctors.length > 0 ? doctors[0].id : '',
                tipo_cita: 'Consulta',
                estado: 'Pendiente',
                color: '#3B82F6',
            });
            setIsModalOpen(true);
        }
    }, [triggerCreate, doctors]);

    const monthStart = startOfMonth(selectedDate);
    const monthEnd = endOfMonth(selectedDate);
    const calendarStart = startOfWeek(monthStart, { weekStartsOn: 1 });
    const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 1 });

    const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });
    const weekDays = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];

    const getAppointmentsForDay = (day: Date) => {
        return appointments.filter(appt => isSameDay(new Date(appt.start), day));
    };

    const handleDayClick = (day: Date) => {
        if (isSameMonth(day, selectedDate)) {
            onDayClick(day);
        }
    };

    return (
        <div className="flex flex-col h-full bg-white">
            {/* Header */}
            <div className="border-b border-gray-200 px-6 py-4">
                <h2 className="text-2xl font-bold text-gray-800 capitalize">
                    {format(selectedDate, 'MMMM yyyy', { locale: es })}
                </h2>
            </div>

            {/* Calendar Grid */}
            <div className="flex-1 flex flex-col p-4">
                {/* Week day headers */}
                <div className="grid grid-cols-7 gap-2 mb-2">
                    {weekDays.map((day) => (
                        <div key={day} className="text-center text-sm font-semibold text-gray-600 py-2">
                            {day}
                        </div>
                    ))}
                </div>

                {/* Days grid */}
                <div className="grid grid-cols-7 gap-2 flex-1">
                    {days.map((day) => {
                        const dayAppointments = getAppointmentsForDay(day);
                        const isCurrentMonth = isSameMonth(day, selectedDate);
                        const isToday = isSameDay(day, new Date());

                        return (
                            <div
                                key={day.toString()}
                                onClick={() => handleDayClick(day)}
                                className={clsx(
                                    "border rounded-lg p-2 cursor-pointer transition-all hover:shadow-md min-h-[100px]",
                                    isCurrentMonth ? "bg-white border-gray-200" : "bg-gray-50 border-gray-100",
                                    isToday && "ring-2 ring-primary-500"
                                )}
                            >
                                <div className={clsx(
                                    "text-sm font-semibold mb-1",
                                    isCurrentMonth ? "text-gray-900" : "text-gray-400",
                                    isToday && "text-primary-600"
                                )}>
                                    {format(day, 'd')}
                                </div>

                                <div className="space-y-1">
                                    {dayAppointments.slice(0, 3).map((appt) => (
                                        <div
                                            key={appt.id}
                                            className="text-xs px-2 py-1 rounded truncate"
                                            style={{
                                                backgroundColor: `${appt.color || '#3B82F6'}40`,
                                                borderLeft: `3px solid ${appt.color || '#2563EB'}`,
                                            }}
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setSelectedAppointment(appt);
                                                setIsModalOpen(true);
                                            }}
                                        >
                                            {format(new Date(appt.start), 'HH:mm')} {appt.title?.split('-')[0]}
                                        </div>
                                    ))}
                                    {dayAppointments.length > 3 && (
                                        <div className="text-xs text-gray-500 px-2">
                                            +{dayAppointments.length - 3} más
                                        </div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            <EventModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSave={(appt) => {
                    onSave(appt);
                    setIsModalOpen(false);
                }}
                initialData={selectedAppointment}
                doctors={doctors}
                patients={patients}
            />
        </div>
    );
};

export default MonthView;
