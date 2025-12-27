import React, { useState, useEffect } from 'react';
import { format, isSameDay, startOfDay, setHours, setMinutes } from 'date-fns';
import { es } from 'date-fns/locale';
import type { Appointment, Doctor, Patient } from '../services/mockData';
import EventModal from './EventModal';
import { Clock, User, FileText, Calendar } from 'lucide-react';

interface AgendaViewProps {
    appointments: Appointment[];
    doctors: Doctor[];
    patients: Patient[];
    onSave: (appt: Partial<Appointment>) => void;
    triggerCreate?: boolean;
}

const AgendaView: React.FC<AgendaViewProps> = ({ appointments, doctors, patients, onSave, triggerCreate }) => {
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

    // Sort appointments by date
    const sortedAppointments = [...appointments].sort((a, b) =>
        new Date(a.start).getTime() - new Date(b.start).getTime()
    );

    // Group by date
    const groupedAppointments: { [key: string]: Appointment[] } = {};
    sortedAppointments.forEach(appt => {
        const dateKey = format(startOfDay(new Date(appt.start)), 'yyyy-MM-dd');
        if (!groupedAppointments[dateKey]) {
            groupedAppointments[dateKey] = [];
        }
        groupedAppointments[dateKey].push(appt);
    });

    const getPatientName = (patientId: string) => {
        return patients.find(p => p.id === patientId)?.name || 'Paciente';
    };

    const getDoctorName = (doctorId: string) => {
        return doctors.find(d => d.id === doctorId)?.name || 'Doctor';
    };

    return (
        <div className="flex flex-col h-full bg-gray-50">
            {/* Header */}
            <div className="bg-white border-b border-gray-200 px-6 py-4">
                <h2 className="text-2xl font-bold text-gray-800">Agenda de Citas</h2>
                <p className="text-sm text-gray-500 mt-1">Lista cronológica de próximas citas</p>
            </div>

            {/* Appointments List */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {Object.keys(groupedAppointments).length === 0 ? (
                    <div className="text-center py-12 text-gray-500">
                        <Calendar className="w-16 h-16 mx-auto mb-4 opacity-50" />
                        <p>No hay citas programadas</p>
                    </div>
                ) : (
                    Object.entries(groupedAppointments).map(([dateKey, dayAppointments]) => {
                        const date = new Date(dateKey);
                        const isToday = isSameDay(date, new Date());

                        return (
                            <div key={dateKey} className="space-y-3">
                                {/* Date Header */}
                                <div className={`flex items-center gap-3 ${isToday ? 'text-primary-600' : 'text-gray-700'}`}>
                                    <div className="flex-shrink-0">
                                        <div className={`text-3xl font-bold ${isToday ? 'text-primary-600' : 'text-gray-800'}`}>
                                            {format(date, 'd')}
                                        </div>
                                        <div className="text-xs uppercase font-medium">
                                            {format(date, 'MMM', { locale: es })}
                                        </div>
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="text-lg font-semibold capitalize">
                                            {format(date, "EEEE, d 'de' MMMM", { locale: es })}
                                        </h3>
                                        {isToday && <span className="text-sm text-primary-600 font-medium">Hoy</span>}
                                    </div>
                                    <div className="text-sm text-gray-500">
                                        {dayAppointments.length} {dayAppointments.length === 1 ? 'cita' : 'citas'}
                                    </div>
                                </div>

                                {/* Appointments */}
                                <div className="space-y-2 ml-16">
                                    {dayAppointments.map((appt) => (
                                        <div
                                            key={appt.id}
                                            className="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer border-l-4"
                                            style={{ borderLeftColor: appt.color || '#3B82F6' }}
                                            onClick={() => {
                                                setSelectedAppointment(appt);
                                                setIsModalOpen(true);
                                            }}
                                        >
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <h4 className="font-semibold text-gray-900 mb-2">{appt.title}</h4>

                                                    <div className="space-y-1 text-sm text-gray-600">
                                                        <div className="flex items-center gap-2">
                                                            <Clock className="w-4 h-4 text-gray-400" />
                                                            <span>
                                                                {format(new Date(appt.start), 'HH:mm')} - {format(new Date(appt.end), 'HH:mm')}
                                                            </span>
                                                        </div>

                                                        <div className="flex items-center gap-2">
                                                            <User className="w-4 h-4 text-gray-400" />
                                                            <span>{getPatientName(appt.id_paciente)}</span>
                                                        </div>

                                                        <div className="flex items-center gap-2">
                                                            <User className="w-4 h-4 text-gray-400" />
                                                            <span className="text-gray-500">{getDoctorName(appt.id_podologo)}</span>
                                                        </div>

                                                        {appt.notas_recepcion && (
                                                            <div className="flex items-start gap-2 mt-2">
                                                                <FileText className="w-4 h-4 text-gray-400 mt-0.5" />
                                                                <span className="text-gray-500 text-xs line-clamp-2">{appt.notas_recepcion}</span>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>

                                                <div className="flex-shrink-0 ml-4">
                                                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${appt.estado === 'Confirmada' ? 'bg-emerald-100 text-emerald-700' :
                                                        appt.estado === 'Pendiente' ? 'bg-amber-100 text-amber-700' :
                                                            appt.estado === 'Completada' ? 'bg-blue-100 text-blue-700' :
                                                                'bg-gray-100 text-gray-700'
                                                        }`}>
                                                        {appt.estado}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        );
                    })
                )}
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

export default AgendaView;
