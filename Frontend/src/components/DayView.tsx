import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import type { Appointment, Doctor, Patient } from '../services/mockData';
import EventModal from './EventModal';
import { setHours, setMinutes } from 'date-fns';

interface DayViewProps {
    selectedDate: Date;
    appointments: Appointment[];
    doctors: Doctor[];
    patients: Patient[];
    onSave: (appt: Partial<Appointment>) => void;
    triggerCreate?: boolean;
}

const DayView: React.FC<DayViewProps> = ({ selectedDate, appointments, doctors, patients, onSave, triggerCreate }) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedAppointment, setSelectedAppointment] = useState<Partial<Appointment> | undefined>(undefined);

    const hours = Array.from({ length: 13 }, (_, i) => i + 8);
    const quarters = [0, 15, 30, 45]; // 15-minute intervals

    const dayAppointments = appointments.filter(appt =>
        format(new Date(appt.start), 'yyyy-MM-dd') === format(selectedDate, 'yyyy-MM-dd')
    );

    useEffect(() => {
        if (triggerCreate) {
            // Default to next 30 min slot from now if today, or 9am on selected day
            const now = new Date();
            let start = now;

            if (format(selectedDate, 'yyyy-MM-dd') !== format(now, 'yyyy-MM-dd')) {
                start = setHours(setMinutes(selectedDate, 0), 9);
            } else {
                const minutes = now.getMinutes();
                const roundedMinutes = minutes > 30 ? 0 : 30;
                start = setMinutes(now, roundedMinutes);
                if (minutes > 30) start.setHours(start.getHours() + 1);
            }

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
    }, [triggerCreate, selectedDate, doctors]);

    const handleSlotClick = (hour: number, minute: number) => {
        const start = setMinutes(setHours(selectedDate, hour), minute);
        const end = new Date(start.getTime() + 30 * 60000);

        setSelectedAppointment({
            fecha_hora_inicio: start,
            fecha_hora_fin: end,
            start,
            end,
            id_podologo: doctors[0].id,
            tipo_cita: 'Consulta',
            estado: 'Pendiente',
            es_primera_vez: false,
            color: '#3B82F6',
        });
        setIsModalOpen(true);
    };

    const handleEventClick = (appt: Appointment) => {
        setSelectedAppointment(appt);
        setIsModalOpen(true);
    };

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="bg-white border-b border-gray-200 px-6 py-4">
                <h2 className="text-2xl font-bold text-gray-800">
                    {format(selectedDate, "EEEE, d 'de' MMMM", { locale: es })}
                </h2>
            </div>

            {/* Time Grid */}
            <div className="flex-1 overflow-y-auto">
                <div className="flex">
                    {/* Time labels */}
                    <div className="w-20 flex-shrink-0 border-r border-gray-200">
                        {hours.map((hour) => (
                            <div key={hour} className="h-32 border-b border-gray-100 relative">
                                <span className="absolute -top-3 right-2 text-sm text-gray-500 font-medium">
                                    {hour}:00
                                </span>
                            </div>
                        ))}
                    </div>

                    {/* Events area */}
                    <div className="flex-1 relative">
                        {hours.map((hour) => (
                            <div key={hour} className="h-32 border-b border-gray-100">
                                {quarters.map((minute) => (
                                    <div
                                        key={`${hour}-${minute}`}
                                        className="h-8 border-b border-gray-50 hover:bg-primary-50 cursor-pointer transition-colors group"
                                        onClick={() => handleSlotClick(hour, minute)}
                                    >
                                        <div className="hidden group-hover:flex items-center justify-center h-full opacity-50">
                                            <span className="text-primary-400 text-xs">+</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ))}

                        {/* Render appointments */}
                        {dayAppointments.map((appt) => {
                            const startHour = new Date(appt.start).getHours();
                            const startMin = new Date(appt.start).getMinutes();
                            const durationMinutes = (new Date(appt.end).getTime() - new Date(appt.start).getTime()) / (1000 * 60);

                            const topOffset = ((startHour - 8) * 128) + ((startMin / 60) * 128);
                            const height = (durationMinutes / 60) * 128;

                            return (
                                <div
                                    key={appt.id}
                                    className="absolute left-2 right-2 rounded-lg p-3 shadow-md cursor-pointer hover:shadow-lg transition-shadow"
                                    style={{
                                        top: `${topOffset}px`,
                                        height: `${height}px`,
                                        backgroundColor: `${appt.color || '#3B82F6'}30`,
                                        borderLeft: `4px solid ${appt.color || '#2563EB'}`,
                                    }}
                                    onClick={() => handleEventClick(appt)}
                                >
                                    <div className="font-bold text-sm">{appt.title}</div>
                                    <div className="text-xs text-gray-600 mt-1">
                                        {format(new Date(appt.start), 'HH:mm')} - {format(new Date(appt.end), 'HH:mm')}
                                    </div>
                                    {appt.notas_recepcion && (
                                        <div className="text-xs text-gray-500 mt-1 line-clamp-2">{appt.notas_recepcion}</div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
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

export default DayView;
