import React, { useState, useEffect } from 'react';
import { X, Clock, User, Calendar, FileText, CheckCircle2, AlertCircle, Bell, Repeat } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import type { Appointment, Doctor, Patient, AppointmentStatus, AppointmentType, Reminder, RecurrenceFrequency } from '../types/appointments';

interface EventModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (appt: Partial<Appointment>) => void;
    initialData?: Partial<Appointment>;
    doctors: Doctor[];
    patients: Patient[];
}

const EventModal: React.FC<EventModalProps> = ({ isOpen, onClose, onSave, initialData, doctors, patients }) => {
    const [formData, setFormData] = useState<Partial<Appointment>>({
        estado: 'Pendiente',
        es_primera_vez: false,
        tipo_cita: 'Consulta',
        ...initialData
    });

    const [searchPatient, setSearchPatient] = useState('');
    const [showPatientDropdown, setShowPatientDropdown] = useState(false);
    const [showReminders, setShowReminders] = useState(false);
    const [showRecurrence, setShowRecurrence] = useState(false);

    useEffect(() => {
        if (isOpen) {
            setFormData({
                estado: 'Pendiente',
                es_primera_vez: false,
                tipo_cita: 'Consulta',
                ...initialData
            });
            setSearchPatient('');
        }
    }, [isOpen, initialData]);

    if (!isOpen) return null;

    const filteredPatients = patients.filter(p =>
        p.name.toLowerCase().includes(searchPatient.toLowerCase()) ||
        p.phone?.includes(searchPatient)
    );

    const selectedPatient = patients.find(p => p.id === formData.id_paciente);

    const handleSave = () => {
        if (!formData.id_paciente || !formData.id_podologo || !formData.fecha_hora_inicio || !formData.fecha_hora_fin) {
            alert('Por favor completa todos los campos obligatorios');
            return;
        }

        // Map to legacy fields for compatibility
        const appointmentData = {
            ...formData,
            start: formData.fecha_hora_inicio!,
            end: formData.fecha_hora_fin!,
            patientId: formData.id_paciente,
            doctorId: formData.id_podologo,
            title: `${formData.tipo_cita} - ${selectedPatient?.name || 'Paciente'}`,
            type: formData.tipo_cita?.toLowerCase(),
            status: 'programada',
            notes: formData.notas_recepcion,
        };

        onSave(appointmentData);
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden transform transition-all scale-100 animate-in slide-in-from-bottom-4 duration-300">
                {/* Header */}
                <div className="bg-gradient-to-r from-primary-600 to-primary-700 px-6 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                            <Calendar className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-white">
                                {formData.id ? 'Editar Cita' : 'Nueva Cita Médica'}
                            </h3>
                            <p className="text-primary-100 text-sm">Completa los datos del paciente</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="text-white/80 hover:text-white p-2 hover:bg-white/10 rounded-full transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="p-6 space-y-5 overflow-y-auto max-h-[calc(90vh-180px)]">
                    {/* Patient Search */}
                    <div className="space-y-2">
                        <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                            <User className="w-4 h-4 text-primary-600" />
                            Paciente <span className="text-red-500">*</span>
                        </label>
                        <div className="relative">
                            <input
                                type="text"
                                placeholder="Buscar por nombre o teléfono..."
                                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all outline-none"
                                value={selectedPatient ? selectedPatient.name : searchPatient}
                                onChange={(e) => {
                                    setSearchPatient(e.target.value);
                                    setShowPatientDropdown(true);
                                    setFormData({ ...formData, id_paciente: undefined });
                                }}
                                onFocus={() => setShowPatientDropdown(true)}
                            />
                            {showPatientDropdown && searchPatient && !selectedPatient && (
                                <div className="absolute z-10 w-full mt-1 bg-white border-2 border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                                    {filteredPatients.length > 0 ? (
                                        filteredPatients.map(patient => (
                                            <button
                                                key={patient.id}
                                                onClick={() => {
                                                    setFormData({ ...formData, id_paciente: patient.id });
                                                    setSearchPatient('');
                                                    setShowPatientDropdown(false);
                                                }}
                                                className="w-full px-4 py-3 text-left hover:bg-primary-50 transition-colors border-b border-gray-100 last:border-0"
                                            >
                                                <div className="font-medium text-gray-900">{patient.name}</div>
                                                <div className="text-sm text-gray-500">{patient.phone}</div>
                                            </button>
                                        ))
                                    ) : (
                                        <div className="px-4 py-3 text-gray-500 text-sm">No se encontraron pacientes</div>
                                    )}
                                </div>
                            )}
                            {selectedPatient && (
                                <div className="mt-2 p-3 bg-primary-50 border border-primary-200 rounded-lg flex items-center justify-between">
                                    <div>
                                        <div className="font-medium text-primary-900">{selectedPatient.name}</div>
                                        <div className="text-sm text-primary-700">{selectedPatient.phone} • {selectedPatient.email}</div>
                                    </div>
                                    <button
                                        onClick={() => {
                                            setFormData({ ...formData, id_paciente: undefined });
                                            setSearchPatient('');
                                        }}
                                        className="text-primary-600 hover:text-primary-800"
                                    >
                                        <X className="w-5 h-5" />
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Doctor Selector */}
                    <div className="space-y-2">
                        <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                            <User className="w-4 h-4 text-primary-600" />
                            Podólogo <span className="text-red-500">*</span>
                        </label>
                        <div className="grid grid-cols-3 gap-2">
                            {doctors.map(doc => (
                                <button
                                    key={doc.id}
                                    onClick={() => setFormData({ ...formData, id_podologo: doc.id })}
                                    className={`px-4 py-3 rounded-lg border-2 transition-all text-sm font-medium ${formData.id_podologo === doc.id
                                        ? 'border-primary-500 bg-primary-50 text-primary-700 ring-2 ring-primary-200'
                                        : 'border-gray-200 hover:border-gray-300 text-gray-700'
                                        }`}
                                >
                                    {doc.name.split(' ')[0]} {doc.name.split(' ')[1]?.[0]}.
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Date and Time */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                                <Clock className="w-4 h-4 text-primary-600" />
                                Hora de Inicio <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="datetime-local"
                                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all outline-none"
                                value={formData.fecha_hora_inicio ? format(new Date(formData.fecha_hora_inicio), "yyyy-MM-dd'T'HH:mm") : ''}
                                onChange={(e) => setFormData({ ...formData, fecha_hora_inicio: new Date(e.target.value) })}
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                                <Clock className="w-4 h-4 text-primary-600" />
                                Hora de Fin <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="datetime-local"
                                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all outline-none"
                                value={formData.fecha_hora_fin ? format(new Date(formData.fecha_hora_fin), "yyyy-MM-dd'T'HH:mm") : ''}
                                onChange={(e) => setFormData({ ...formData, fecha_hora_fin: new Date(e.target.value) })}
                            />
                        </div>
                    </div>

                    {/* Appointment Type */}
                    <div className="space-y-2">
                        <label className="text-sm font-semibold text-gray-700">Tipo de Cita</label>
                        <div className="flex gap-2">
                            {(['Consulta', 'Seguimiento', 'Urgencia'] as AppointmentType[]).map((type) => (
                                <button
                                    key={type}
                                    onClick={() => setFormData({ ...formData, tipo_cita: type })}
                                    className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-medium border-2 transition-all ${formData.tipo_cita === type
                                        ? 'bg-primary-50 text-primary-700 border-primary-500 ring-2 ring-primary-200'
                                        : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
                                        }`}
                                >
                                    {type}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Color Picker */}
                    <div className="space-y-2">
                        <label className="text-sm font-semibold text-gray-700">Color de la Cita</label>
                        <div className="flex gap-2">
                            {['#3B82F6', '#10B981', '#EF4444', '#8B5CF6', '#F59E0B', '#EC4899'].map((color) => (
                                <button
                                    key={color}
                                    onClick={() => setFormData({ ...formData, color })}
                                    className={`w-10 h-10 rounded-full border-2 transition-all ${formData.color === color
                                        ? 'border-gray-800 ring-2 ring-offset-2 ring-gray-400 scale-110'
                                        : 'border-gray-200 hover:scale-105'
                                        }`}
                                    style={{ backgroundColor: color }}
                                    title={color}
                                />
                            ))}
                        </div>
                    </div>

                    {/* Status and First Time */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-gray-700">Estado</label>
                            <select
                                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all outline-none"
                                value={formData.estado}
                                onChange={(e) => setFormData({ ...formData, estado: e.target.value as AppointmentStatus })}
                            >
                                <option value="Pendiente">Pendiente</option>
                                <option value="Confirmada">Confirmada</option>
                                <option value="En_Curso">En Curso</option>
                                <option value="Completada">Completada</option>
                                <option value="Cancelada">Cancelada</option>
                                <option value="No_Asistio">No Asistió</option>
                            </select>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-gray-700">¿Primera vez?</label>
                            <div className="flex gap-2 h-[50px]">
                                <button
                                    onClick={() => setFormData({ ...formData, es_primera_vez: true })}
                                    className={`flex-1 px-4 py-3 rounded-lg text-sm font-medium border-2 transition-all ${formData.es_primera_vez
                                        ? 'bg-emerald-50 text-emerald-700 border-emerald-500'
                                        : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
                                        }`}
                                >
                                    Sí
                                </button>
                                <button
                                    onClick={() => setFormData({ ...formData, es_primera_vez: false })}
                                    className={`flex-1 px-4 py-3 rounded-lg text-sm font-medium border-2 transition-all ${!formData.es_primera_vez
                                        ? 'bg-gray-50 text-gray-700 border-gray-300'
                                        : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
                                        }`}
                                >
                                    No
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Reminders Section */}
                    <div className="space-y-2">
                        <button
                            type="button"
                            onClick={() => setShowReminders(!showReminders)}
                            className="flex items-center gap-2 text-sm font-semibold text-gray-700 hover:text-primary-600 transition-colors"
                        >
                            <Bell className="w-4 h-4" />
                            Recordatorios
                            <span className="text-xs text-gray-500">
                                {formData.recordatorios?.length || 0} configurados
                            </span>
                        </button>

                        {showReminders && (
                            <div className="pl-6 space-y-2">
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => {
                                            const newReminders = formData.recordatorios || [];
                                            setFormData({
                                                ...formData,
                                                recordatorios: [...newReminders, { tiempo: 30, unidad: 'minutos' }]
                                            });
                                        }}
                                        className="text-sm text-primary-600 hover:text-primary-700"
                                    >
                                        + Agregar recordatorio
                                    </button>
                                </div>

                                {formData.recordatorios?.map((reminder, index) => (
                                    <div key={index} className="flex gap-2 items-center">
                                        <input
                                            type="number"
                                            value={reminder.tiempo}
                                            onChange={(e) => {
                                                const newReminders = [...(formData.recordatorios || [])];
                                                newReminders[index].tiempo = parseInt(e.target.value);
                                                setFormData({ ...formData, recordatorios: newReminders });
                                            }}
                                            className="w-20 px-2 py-1 border border-gray-200 rounded text-sm"
                                        />
                                        <select
                                            value={reminder.unidad}
                                            onChange={(e) => {
                                                const newReminders = [...(formData.recordatorios || [])];
                                                newReminders[index].unidad = e.target.value as any;
                                                setFormData({ ...formData, recordatorios: newReminders });
                                            }}
                                            className="px-2 py-1 border border-gray-200 rounded text-sm"
                                        >
                                            <option value="minutos">minutos antes</option>
                                            <option value="horas">horas antes</option>
                                            <option value="días">días antes</option>
                                        </select>
                                        <button
                                            onClick={() => {
                                                const newReminders = formData.recordatorios?.filter((_, i) => i !== index);
                                                setFormData({ ...formData, recordatorios: newReminders });
                                            }}
                                            className="text-red-500 hover:text-red-700 text-sm"
                                        >
                                            <X className="w-4 h-4" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Recurrence Section */}
                    <div className="space-y-2">
                        <button
                            type="button"
                            onClick={() => {
                                setShowRecurrence(!showRecurrence);
                                if (!showRecurrence && !formData.es_recurrente) {
                                    setFormData({
                                        ...formData,
                                        es_recurrente: true,
                                        regla_recurrencia: { frequency: 'WEEKLY', interval: 1 }
                                    });
                                }
                            }}
                            className="flex items-center gap-2 text-sm font-semibold text-gray-700 hover:text-primary-600 transition-colors"
                        >
                            <Repeat className="w-4 h-4" />
                            Repetir cita
                            {formData.es_recurrente && (
                                <span className="text-xs text-emerald-600 font-medium">Activado</span>
                            )}
                        </button>

                        {showRecurrence && formData.es_recurrente && (
                            <div className="pl-6 space-y-3">
                                <div className="flex gap-2">
                                    {(['DAILY', 'WEEKLY', 'MONTHLY'] as RecurrenceFrequency[]).map((freq) => (
                                        <button
                                            key={freq}
                                            onClick={() => setFormData({
                                                ...formData,
                                                regla_recurrencia: { ...formData.regla_recurrencia!, frequency: freq }
                                            })}
                                            className={`px-3 py-1 rounded text-xs font-medium ${formData.regla_recurrencia?.frequency === freq
                                                    ? 'bg-primary-100 text-primary-700'
                                                    : 'bg-gray-100 text-gray-600'
                                                }`}
                                        >
                                            {freq === 'DAILY' ? 'Diario' : freq === 'WEEKLY' ? 'Semanal' : 'Mensual'}
                                        </button>
                                    ))}
                                </div>

                                <div className="flex gap-2 items-center text-sm">
                                    <span>Cada</span>
                                    <input
                                        type="number"
                                        min="1"
                                        value={formData.regla_recurrencia?.interval || 1}
                                        onChange={(e) => setFormData({
                                            ...formData,
                                            regla_recurrencia: {
                                                ...formData.regla_recurrencia!,
                                                interval: parseInt(e.target.value)
                                            }
                                        })}
                                        className="w-16 px-2 py-1 border border-gray-200 rounded"
                                    />
                                    <span>
                                        {formData.regla_recurrencia?.frequency === 'DAILY' ? 'días' :
                                            formData.regla_recurrencia?.frequency === 'WEEKLY' ? 'semanas' : 'meses'}
                                    </span>
                                </div>

                                <div className="flex gap-2 items-center text-sm">
                                    <span>Termina después de</span>
                                    <input
                                        type="number"
                                        min="1"
                                        placeholder="10"
                                        value={formData.regla_recurrencia?.count || ''}
                                        onChange={(e) => setFormData({
                                            ...formData,
                                            regla_recurrencia: {
                                                ...formData.regla_recurrencia!,
                                                count: parseInt(e.target.value) || undefined
                                            }
                                        })}
                                        className="w-20 px-2 py-1 border border-gray-200 rounded"
                                    />
                                    <span>ocurrencias</span>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Notes */}
                    <div className="space-y-2">
                        <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                            <FileText className="w-4 h-4 text-primary-600" />
                            Notas de Recepción
                        </label>
                        <textarea
                            placeholder="Observaciones, motivo de la cita, síntomas..."
                            className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 min-h-[100px] transition-all outline-none resize-none"
                            value={formData.notas_recepcion || ''}
                            onChange={(e) => setFormData({ ...formData, notas_recepcion: e.target.value })}
                        />
                    </div>
                </div>

                {/* Footer */}
                <div className="bg-gray-50 px-6 py-4 flex justify-between items-center border-t border-gray-200">
                    <div className="text-sm text-gray-500">
                        {!formData.id_paciente || !formData.id_podologo || !formData.fecha_hora_inicio || !formData.fecha_hora_fin ? (
                            <span className="flex items-center gap-1.5 text-amber-600">
                                <AlertCircle className="w-4 h-4" />
                                Completa los campos obligatorios (*)
                            </span>
                        ) : (
                            <span className="flex items-center gap-1.5 text-emerald-600">
                                <CheckCircle2 className="w-4 h-4" />
                                Listo para guardar
                            </span>
                        )}
                    </div>
                    <div className="flex gap-3">
                        <button onClick={onClose} className="px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-200 rounded-lg transition-colors">
                            Cancelar
                        </button>
                        <button onClick={handleSave} className="px-6 py-2.5 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg shadow-sm transition-colors flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4" />
                            Guardar Cita
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default EventModal;
