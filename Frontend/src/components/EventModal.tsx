import React, { useState, useEffect } from 'react';
import { X, Clock, User, Calendar, FileText, CheckCircle2, AlertCircle, Bell, Repeat, Stethoscope, UserPlus } from 'lucide-react';
import { format, addMinutes } from 'date-fns';
import { es } from 'date-fns/locale';
import { useNavigate } from 'react-router-dom';
import type { Appointment, Doctor, Patient, AppointmentStatus, AppointmentType, Reminder, RecurrenceFrequency } from '../types/appointments';
import { createReminder, getReminders, deleteReminder, createSeries } from '../services/appointmentService';
import { getServices, type Service } from '../services/catalogService';
import { createPatient } from '../services/patientService';

interface EventModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (appt: Partial<Appointment>) => void;
    initialData?: Partial<Appointment>;
    doctors: Doctor[];
    patients: Patient[];
}

const EventModal: React.FC<EventModalProps> = ({ isOpen, onClose, onSave, initialData, doctors, patients }) => {
    const navigate = useNavigate();
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
    const [isNewPatient, setIsNewPatient] = useState(false);
    const [newPatientData, setNewPatientData] = useState({
        primer_nombre: '',
        segundo_nombre: '',
        primer_apellido: '',
        segundo_apellido: '',
        telefono: '',
        email: ''
    });
    const [services, setServices] = useState<Service[]>([]);
    const [selectedService, setSelectedService] = useState<Service | null>(null);

    useEffect(() => {
        if (isOpen) {
            setFormData({
                estado: 'Pendiente',
                es_primera_vez: false,
                tipo_cita: 'Consulta',
                recordatorios: [],
                ...initialData
            });
            setSearchPatient('');
            setIsNewPatient(false);
            setNewPatientData({
                primer_nombre: '',
                segundo_nombre: '',
                primer_apellido: '',
                segundo_apellido: '',
                telefono: '',
                email: ''
            });
            
            // Cargar servicios
            getServices({ activo: true })
                .then(data => setServices(data.servicios || data))
                .catch(err => console.error('Error cargando servicios:', err));
            
            // Cargar recordatorios existentes si hay una cita
            if (initialData?.id) {
                getReminders(initialData.id)
                    .then(reminders => {
                        setFormData(prev => ({
                            ...prev,
                            recordatorios: reminders.map(r => ({
                                tiempo: r.tiempo,
                                unidad_tiempo: r.unidad_tiempo,
                                metodo_envio: r.metodo_envio
                            }))
                        }));
                    })
                    .catch(err => console.error('Error cargando recordatorios:', err));
            }
        }
    }, [isOpen, initialData]);

    // Auto-calcular hora fin cuando cambia servicio u hora inicio
    useEffect(() => {
        if (selectedService && formData.fecha_hora_inicio) {
            const newEndTime = addMinutes(formData.fecha_hora_inicio, selectedService.duracion_minutos);
            setFormData(prev => ({ ...prev, fecha_hora_fin: newEndTime }));
        }
    }, [selectedService, formData.fecha_hora_inicio]);

    // Auto-asignar color según podólogo seleccionado
    useEffect(() => {
        if (formData.id_podologo) {
            const doctor = doctors.find(d => d.id === formData.id_podologo);
            if (doctor) {
                // Asignar colores fijos por podólogo
                let color = '#8B5CF6'; // Color por defecto (púrpura)
                
                // Santiago (Jesús Ornelas Reynoso) = Azul
                if (doctor.name.toLowerCase().includes('santiago') || doctor.name.toLowerCase().includes('ornelas')) {
                    color = '#3B82F6';
                }
                // Ibeth = Rosa
                else if (doctor.name.toLowerCase().includes('ibeth')) {
                    color = '#EC4899';
                }
                
                setFormData(prev => ({ ...prev, color }));
            }
        }
    }, [formData.id_podologo, doctors]);

    if (!isOpen) return null;

    const filteredPatients = patients.filter(p =>
        p.name.toLowerCase().includes(searchPatient.toLowerCase()) ||
        p.phone?.includes(searchPatient)
    );

    const selectedPatient = patients.find(p => p.id === formData.id_paciente);

    const handleStartMedicalAttention = () => {
        if (!formData.id_paciente) {
            alert('Por favor selecciona un paciente primero');
            return;
        }

        if (!formData.id) {
            alert('Debes guardar la cita primero antes de aplicar atención médica');
            return;
        }

        // Construir query params con datos de la cita
        const params = new URLSearchParams({
            citaId: formData.id.toString(),
            pacienteId: formData.id_paciente.toString(),
            podologoId: formData.id_podologo?.toString() || '',
            tipoCita: formData.tipo_cita || 'Consulta',
            fechaCita: formData.fecha_hora_inicio?.toISOString() || '',
        });

        // Redirigir a atención médica
        navigate(`/medical-attention?${params.toString()}`);
        onClose();
    };

    const handleSave = async () => {
        // Validar datos básicos
        if (!formData.id_podologo || !formData.fecha_hora_inicio || !formData.fecha_hora_fin) {
            alert('Por favor completa todos los campos obligatorios (Podólogo, Fecha y Hora)');
            return;
        }

        // Si es nuevo paciente, crear primero
        if (isNewPatient) {
            if (!newPatientData.primer_nombre || !newPatientData.primer_apellido || !newPatientData.telefono) {
                alert('Para registrar un nuevo paciente, completa: Primer Nombre, Primer Apellido y Teléfono');
                return;
            }

            try {
                const newPatient = await createPatient({
                    primer_nombre: newPatientData.primer_nombre,
                    segundo_nombre: newPatientData.segundo_nombre || undefined,
                    primer_apellido: newPatientData.primer_apellido,
                    segundo_apellido: newPatientData.segundo_apellido || undefined,
                    telefono_principal: newPatientData.telefono,
                    email: newPatientData.email || undefined,
                    activo: true
                });
                
                // Asignar el nuevo paciente a la cita
                formData.id_paciente = newPatient.id;
            } catch (error) {
                console.error('Error creando paciente:', error);
                alert('Error al registrar el nuevo paciente. Por favor intenta de nuevo.');
                return;
            }
        }

        // Validar que tengamos paciente
        if (!formData.id_paciente) {
            alert('Por favor selecciona o registra un paciente');
            return;
        }

        // Map to legacy fields for compatibility
        const appointmentData = {
            ...formData,
            start: formData.fecha_hora_inicio!,
            end: formData.fecha_hora_fin!,
            patientId: formData.id_paciente,
            doctorId: formData.id_podologo,
            title: `${formData.tipo_cita} - ${selectedPatient?.name || newPatientData.primer_nombre}`,
            type: formData.tipo_cita?.toLowerCase(),
            status: 'programada',
            notes: formData.notas_recepcion,
        };

        // Guardar cita primero
        onSave(appointmentData);
        
        // Si hay recordatorios y tenemos un ID de cita, crearlos
        if (formData.id && formData.recordatorios && formData.recordatorios.length > 0) {
            try {
                for (const recordatorio of formData.recordatorios) {
                    await createReminder(formData.id, recordatorio);
                }
            } catch (error) {
                console.error('Error creando recordatorios:', error);
                alert('La cita se guardó pero hubo un problema al crear los recordatorios');
            }
        }
        
        // Si es recurrente, crear la serie
        if (formData.es_recurrente && formData.id && formData.regla_recurrencia) {
            try {
                await createSeries({
                    id_cita_plantilla: formData.id,
                    regla_recurrencia: formData.regla_recurrencia,
                    fecha_inicio: formData.fecha_hora_inicio!,
                    fecha_fin: formData.regla_recurrencia.until
                });
            } catch (error) {
                console.error('Error creando serie recurrente:', error);
                alert('La cita se guardó pero hubo un problema al crear la serie recurrente');
            }
        }
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
                    {/* Patient Search or New Patient */}
                    <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                                <User className="w-4 h-4 text-primary-600" />
                                Paciente <span className="text-red-500">*</span>
                            </label>
                            <button
                                type="button"
                                onClick={() => {
                                    setIsNewPatient(!isNewPatient);
                                    setFormData({ ...formData, id_paciente: undefined });
                                    setSearchPatient('');
                                }}
                                className="flex items-center gap-1 text-xs font-medium text-primary-600 hover:text-primary-700"
                            >
                                <UserPlus className="w-3.5 h-3.5" />
                                {isNewPatient ? 'Buscar existente' : 'Registrar nuevo'}
                            </button>
                        </div>

                        {!isNewPatient ? (
                            /* Búsqueda de paciente existente */
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
                        ) : (
                            /* Formulario para nuevo paciente */
                            <div className="space-y-3 p-4 bg-gray-50 rounded-lg border-2 border-gray-200">
                                <div className="grid grid-cols-2 gap-3">
                                    <div>
                                        <label className="text-xs font-medium text-gray-600">Primer Nombre *</label>
                                        <input
                                            type="text"
                                            placeholder="Juan"
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-200 outline-none"
                                            value={newPatientData.primer_nombre}
                                            onChange={(e) => setNewPatientData({ ...newPatientData, primer_nombre: e.target.value })}
                                        />
                                    </div>
                                    <div>
                                        <label className="text-xs font-medium text-gray-600">Segundo Nombre</label>
                                        <input
                                            type="text"
                                            placeholder="Carlos"
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-200 outline-none"
                                            value={newPatientData.segundo_nombre}
                                            onChange={(e) => setNewPatientData({ ...newPatientData, segundo_nombre: e.target.value })}
                                        />
                                    </div>
                                    <div>
                                        <label className="text-xs font-medium text-gray-600">Primer Apellido *</label>
                                        <input
                                            type="text"
                                            placeholder="Pérez"
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-200 outline-none"
                                            value={newPatientData.primer_apellido}
                                            onChange={(e) => setNewPatientData({ ...newPatientData, primer_apellido: e.target.value })}
                                        />
                                    </div>
                                    <div>
                                        <label className="text-xs font-medium text-gray-600">Segundo Apellido</label>
                                        <input
                                            type="text"
                                            placeholder="López"
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-200 outline-none"
                                            value={newPatientData.segundo_apellido}
                                            onChange={(e) => setNewPatientData({ ...newPatientData, segundo_apellido: e.target.value })}
                                        />
                                    </div>
                                    <div>
                                        <label className="text-xs font-medium text-gray-600">Teléfono *</label>
                                        <input
                                            type="tel"
                                            placeholder="1234567890"
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-200 outline-none"
                                            value={newPatientData.telefono}
                                            onChange={(e) => setNewPatientData({ ...newPatientData, telefono: e.target.value })}
                                        />
                                    </div>
                                    <div>
                                        <label className="text-xs font-medium text-gray-600">Email</label>
                                        <input
                                            type="email"
                                            placeholder="correo@ejemplo.com"
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-200 outline-none"
                                            value={newPatientData.email}
                                            onChange={(e) => setNewPatientData({ ...newPatientData, email: e.target.value })}
                                        />
                                    </div>
                                </div>
                                <p className="text-xs text-gray-500">El paciente se registrará automáticamente al guardar la cita</p>
                            </div>
                        )}
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

                    {/* Service Selector */}
                    <div className="space-y-2">
                        <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                            <Stethoscope className="w-4 h-4 text-primary-600" />
                            Servicio (Opcional)
                        </label>
                        <select
                            className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all outline-none"
                            value={selectedService?.id || ''}
                            onChange={(e) => {
                                const service = services.find(s => s.id === Number(e.target.value));
                                setSelectedService(service || null);
                            }}
                        >
                            <option value="">Consulta General (sin servicio definido)</option>
                            {services.map(service => (
                                <option key={service.id} value={service.id}>
                                    {service.nombre} - {service.duracion_minutos} min - ${service.precio}
                                </option>
                            ))}
                        </select>
                        {selectedService && (
                            <p className="text-xs text-primary-600">
                                Duración: {selectedService.duracion_minutos} minutos (la hora de fin se calculará automáticamente)
                            </p>
                        )}
                    </div>

                    {/* Date and Time */}
                    <div className="space-y-2">
                        <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                            <Clock className="w-4 h-4 text-primary-600" />
                            Fecha y Hora de Inicio <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="datetime-local"
                            className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all outline-none"
                            value={formData.fecha_hora_inicio ? format(new Date(formData.fecha_hora_inicio), "yyyy-MM-dd'T'HH:mm") : ''}
                            onChange={(e) => {
                                const newStart = new Date(e.target.value);
                                setFormData({ ...formData, fecha_hora_inicio: newStart });
                                // Si hay servicio seleccionado, calcular hora fin
                                if (selectedService) {
                                    setFormData(prev => ({ 
                                        ...prev, 
                                        fecha_hora_inicio: newStart,
                                        fecha_hora_fin: addMinutes(newStart, selectedService.duracion_minutos) 
                                    }));
                                } else {
                                    // Duración por defecto: 30 minutos
                                    setFormData(prev => ({ 
                                        ...prev, 
                                        fecha_hora_inicio: newStart,
                                        fecha_hora_fin: addMinutes(newStart, 30) 
                                    }));
                                }
                            }}
                        />
                        {formData.fecha_hora_inicio && formData.fecha_hora_fin && (
                            <p className="text-xs text-gray-500">
                                Hora de fin calculada: {format(new Date(formData.fecha_hora_fin), "HH:mm", { locale: es })}
                                {selectedService && ` (${selectedService.duracion_minutos} min)`}
                            </p>
                        )}
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
                    <div className="flex items-center gap-3">
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

                        {/* Botón Aplicar Atención Médica - Solo visible para citas existentes */}
                        {formData.id && formData.id_paciente && (
                            <button
                                onClick={handleStartMedicalAttention}
                                className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-white bg-teal-600 hover:bg-teal-700 rounded-lg shadow-sm transition-colors"
                                title="Abrir expediente médico para este paciente"
                            >
                                <Stethoscope className="w-4 h-4" />
                                Aplicar Atención Médica
                            </button>
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
