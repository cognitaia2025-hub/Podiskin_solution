import React, { useState, useEffect } from 'react';
import { format, startOfWeek, addDays, eachDayOfInterval, isSameDay, setHours, setMinutes } from 'date-fns';
import { es } from 'date-fns/locale';
import type { Appointment, Doctor, Patient } from '../types/appointments';
import { User, Clock } from 'lucide-react';
import EventModal from './EventModal';

interface StaffAvailabilityProps {
    appointments: Appointment[];
    doctors: Doctor[];
    patients: Patient[];
    onSave: (appt: Partial<Appointment>) => void;
    triggerCreate?: boolean;
}

const StaffAvailability: React.FC<StaffAvailabilityProps> = ({ appointments, doctors, patients, onSave, triggerCreate }) => {
    const [selectedDate, setSelectedDate] = useState(new Date());
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedAppointment, setSelectedAppointment] = useState<Partial<Appointment> | undefined>(undefined);

    useEffect(() => {
        if (triggerCreate) {
            const now = new Date();
            const minutes = now.getMinutes();
            const roundedMinutes = minutes > 30 ? 0 : 30;
            const start = setMinutes(now, roundedMinutes);
            if (minutes > 30) start.setHours(start.getHours() + 1);
            const end = setMinutes(start, start.getMinutes() + 30);

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

    const startOfCurrentWeek = startOfWeek(selectedDate, { weekStartsOn: 1 });
    const weekDays = eachDayOfInterval({
        start: startOfCurrentWeek,
        end: addDays(startOfCurrentWeek, 4), // Monday to Friday
    });

    const hours = Array.from({ length: 11 }, (_, i) => i + 9); // 9:00 to 19:00

    const getAppointmentForSlot = (doctorId: string, day: Date, hour: number) => {
        return appointments.find(appt =>
            appt.id_podologo === doctorId &&
            isSameDay(new Date(appt.start), day) &&
            new Date(appt.start).getHours() === hour
        );
    };

    const handleSlotClick = (doctorId: string, day: Date, hour: number) => {
        const start = setMinutes(setHours(day, hour), 0);
        const end = setMinutes(setHours(day, hour), 30);

        // Check if there is an appointment (simple overlap check for demo)
        const existingAppt = getAppointmentForSlot(doctorId, day, hour);

        if (existingAppt) {
            setSelectedAppointment(existingAppt);
        } else {
            setSelectedAppointment({
                fecha_hora_inicio: start,
                fecha_hora_fin: end,
                start,
                end,
                id_podologo: doctorId,
                tipo_cita: 'Consulta',
                estado: 'Pendiente',
                es_primera_vez: false,
                color: '#3B82F6',
            });
        }
        setIsModalOpen(true);
    };

    return (
        <div className="flex flex-col h-full bg-white overflow-hidden">
            <div className="border-b border-gray-200 px-6 py-4 flex justify-between items-center">
                <h2 className="text-xl font-bold text-gray-800">Disponibilidad del Personal</h2>
                <div className="flex space-x-2">
                    <button
                        onClick={() => setSelectedDate(addDays(selectedDate, -7))}
                        className="p-1 hover:bg-gray-100 rounded"
                    >
                        Semana Anterior
                    </button>
                    <button
                        onClick={() => setSelectedDate(new Date())}
                        className="px-3 py-1 bg-primary-50 text-primary-700 rounded font-medium"
                    >
                        Hoy
                    </button>
                    <button
                        onClick={() => setSelectedDate(addDays(selectedDate, 7))}
                        className="p-1 hover:bg-gray-100 rounded"
                    >
                        Semana Siguiente
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-auto">
                <div className="min-w-[1000px]">
                    {/* Header Row: Days */}
                    <div className="flex border-b border-gray-200">
                        <div className="w-48 flex-shrink-0 p-4 font-semibold text-gray-500 bg-gray-50 border-r border-gray-200">
                            Doctor / Día
                        </div>
                        {weekDays.map(day => (
                            <div key={day.toString()} className="flex-1 text-center p-2 border-r border-gray-200 last:border-r-0 bg-gray-50">
                                <div className="font-semibold text-gray-700">{format(day, 'EEEE', { locale: es })}</div>
                                <div className={`text-sm ${isSameDay(day, new Date()) ? 'text-primary-600 font-bold' : 'text-gray-500'}`}>
                                    {format(day, 'd MMM')}
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Doctor Rows */}
                    {doctors.map(doctor => (
                        <div key={doctor.id} className="flex border-b border-gray-100 last:border-b-0">
                            {/* Doctor Info Column */}
                            <div className="w-48 flex-shrink-0 p-4 border-r border-gray-200 flex items-center gap-3">
                                <div
                                    className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold shadow-sm"
                                    style={{
                                        backgroundColor: doctor.color.split(' ')[0].replace('bg-', '') === 'blue-100' ? '#3B82F6' :
                                            doctor.color.split(' ')[0].replace('bg-', '') === 'emerald-100' ? '#10B981' : '#8B5CF6'
                                    }}
                                >
                                    {doctor.name.charAt(0)}
                                </div>
                                <div>
                                    <div className="font-medium text-gray-900 text-sm">{doctor.name}</div>
                                    <div className="text-xs text-gray-500">Podólogo</div>
                                </div>
                            </div>

                            {/* Days Columns */}
                            {weekDays.map(day => (
                                <div key={`${doctor.id}-${day}`} className="flex-1 border-r border-gray-100 last:border-r-0 p-2 min-h-[120px]">
                                    <div className="grid grid-cols-1 gap-1">
                                        {hours.map(hour => {
                                            const appt = getAppointmentForSlot(doctor.id, day, hour);
                                            // Mock availability logic: randomize busy slots if no appointment
                                            // In real app, check working hours
                                            const isWorkingHour = true;

                                            return (
                                                <div
                                                    key={hour}
                                                    onClick={() => handleSlotClick(doctor.id, day, hour)}
                                                    className={`
                                                        h-8 rounded text-xs flex items-center px-2 cursor-pointer transition-all
                                                        ${appt
                                                            ? `bg-opacity-20 border-l-2`
                                                            : 'hover:bg-gray-100 bg-white border border-dashed border-gray-200 text-gray-400'
                                                        }
                                                    `}
                                                    style={appt ? {
                                                        backgroundColor: `${appt.color || '#3B82F6'}30`,
                                                        borderLeftColor: appt.color || '#3B82F6',
                                                        color: '#1F2937'
                                                    } : {}}
                                                >
                                                    {appt ? (
                                                        <span className="truncate w-full font-medium">
                                                            {format(new Date(appt.start), 'HH:mm')} - {appt.tipo_cita}
                                                        </span>
                                                    ) : (
                                                        <span className="opacity-0 hover:opacity-100 flex items-center gap-1 mx-auto">
                                                            <Clock className="w-3 h-3" /> {hour}:00
                                                        </span>
                                                    )}
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ))}
                </div>
            </div>

            <EventModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSave={onSave}
                initialData={selectedAppointment}
                doctors={doctors}
                patients={patients}
            />
        </div>
    );
};

export default StaffAvailability;
