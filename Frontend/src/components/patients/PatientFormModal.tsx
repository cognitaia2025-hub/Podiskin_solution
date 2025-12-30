import React, { useState, useEffect } from 'react';
import { X, User, Phone, Heart } from 'lucide-react';
import { clsx } from 'clsx';
import type { PersonalInfo, Allergy } from '../../types/medical';
import { 
  SEXO_OPCIONES, 
  ESTADO_CIVIL_OPCIONES,
} from '../../types/medical';
import AllergyList from './AllergyList';
import { getPatientById, createPatient, updatePatient } from '../../services/patientService';

interface PatientFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  patientId?: string;
  onSuccess: (patient: any) => void;
}

type TabId = 'personal' | 'contact' | 'medical';

/**
 * PatientFormModal Component
 * 
 * Modal with tabbed form for creating/editing patients
 */
const PatientFormModal: React.FC<PatientFormModalProps> = ({
  isOpen,
  onClose,
  patientId,
  onSuccess,
}) => {
  const [activeTab, setActiveTab] = useState<TabId>('personal');
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Form data
  const [formData, setFormData] = useState<Partial<PersonalInfo> & { 
    tipo_sangre?: string;
    alergias?: Allergy[];
    como_supo_de_nosotros?: string;
  }>({
    primer_nombre: '',
    segundo_nombre: '',
    primer_apellido: '',
    segundo_apellido: '',
    fecha_nacimiento: '',
    sexo: undefined,
    curp: '',
    estado_civil: '',
    ocupacion: '',
    telefono_principal: '',
    telefono_secundario: '',
    correo_electronico: '',
    calle: '',
    numero_exterior: '',
    numero_interior: '',
    colonia: '',
    ciudad: '',
    estado: '',
    codigo_postal: '',
    tipo_sangre: '',
    alergias: [],
    como_supo_de_nosotros: '',
  });

  // Load patient data if editing
  useEffect(() => {
    if (isOpen && patientId) {
      setIsLoading(true);
      getPatientById(patientId)
        .then((patient) => {
          // Map patient data to form data
          setFormData({
            primer_nombre: patient.name?.split(' ')[0] || '',
            primer_apellido: patient.name?.split(' ')[1] || '',
            telefono_principal: patient.phone || '',
            correo_electronico: patient.email || '',
            fecha_nacimiento: patient.fecha_nacimiento || '',
            curp: patient.curp || '',
            estado_civil: patient.estado_civil || '',
            ocupacion: patient.ocupacion || '',
            alergias: [],
          });
        })
        .catch((error) => {
          console.error('Error loading patient:', error);
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else if (isOpen) {
      // Reset form for new patient
      setFormData({
        primer_nombre: '',
        segundo_nombre: '',
        primer_apellido: '',
        segundo_apellido: '',
        fecha_nacimiento: '',
        sexo: undefined,
        curp: '',
        estado_civil: '',
        ocupacion: '',
        telefono_principal: '',
        telefono_secundario: '',
        correo_electronico: '',
        calle: '',
        numero_exterior: '',
        numero_interior: '',
        colonia: '',
        ciudad: '',
        estado: '',
        codigo_postal: '',
        tipo_sangre: '',
        alergias: [],
        como_supo_de_nosotros: '',
      });
      setActiveTab('personal');
      setErrors({});
    }
  }, [isOpen, patientId]);

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user types
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Required fields
    if (!formData.primer_nombre?.trim()) {
      newErrors.primer_nombre = 'El primer nombre es obligatorio';
    }
    if (!formData.primer_apellido?.trim()) {
      newErrors.primer_apellido = 'El primer apellido es obligatorio';
    }
    if (!formData.fecha_nacimiento) {
      newErrors.fecha_nacimiento = 'La fecha de nacimiento es obligatoria';
    } else {
      // Check if date is not in the future
      const birthDate = new Date(formData.fecha_nacimiento);
      if (birthDate > new Date()) {
        newErrors.fecha_nacimiento = 'La fecha de nacimiento no puede ser futura';
      }
    }
    if (!formData.sexo) {
      newErrors.sexo = 'El sexo es obligatorio';
    }
    if (!formData.telefono_principal?.trim()) {
      newErrors.telefono_principal = 'El teléfono principal es obligatorio';
    } else if (!/^\d{10}$/.test(formData.telefono_principal.replace(/\D/g, ''))) {
      newErrors.telefono_principal = 'El teléfono debe tener 10 dígitos';
    }

    // Optional validations
    if (formData.correo_electronico && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.correo_electronico)) {
      newErrors.correo_electronico = 'El correo electrónico no es válido';
    }
    if (formData.curp && formData.curp.length > 0 && formData.curp.length !== 18) {
      newErrors.curp = 'La CURP debe tener 18 caracteres';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      // Switch to the tab with the first error
      const errorField = Object.keys(errors)[0];
      if (['primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'fecha_nacimiento', 'sexo', 'curp', 'estado_civil', 'ocupacion'].includes(errorField)) {
        setActiveTab('personal');
      } else if (['telefono_principal', 'telefono_secundario', 'correo_electronico', 'calle', 'numero_exterior', 'colonia', 'ciudad', 'estado', 'codigo_postal'].includes(errorField)) {
        setActiveTab('contact');
      }
      return;
    }

    setIsSaving(true);

    try {
      // Prepare patient data
      const fullName = [
        formData.primer_nombre,
        formData.segundo_nombre,
        formData.primer_apellido,
        formData.segundo_apellido,
      ].filter(Boolean).join(' ');

      const direccion = [
        formData.calle,
        formData.numero_exterior,
        formData.colonia,
        formData.ciudad,
        formData.estado,
        formData.codigo_postal,
      ].filter(Boolean).join(', ');

      const patientData = {
        name: fullName,
        phone: formData.telefono_principal,
        email: formData.correo_electronico,
        fecha_nacimiento: formData.fecha_nacimiento,
        curp: formData.curp,
        estado_civil: formData.estado_civil,
        ocupacion: formData.ocupacion,
        direccion: direccion || undefined,
      };

      let savedPatient;
      if (patientId) {
        savedPatient = await updatePatient(patientId, patientData);
      } else {
        savedPatient = await createPatient(patientData);
      }

      onSuccess(savedPatient);
      onClose();
    } catch (error) {
      console.error('Error saving patient:', error);
      alert('Error al guardar el paciente. Por favor, intente de nuevo.');
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  const tabs = [
    { id: 'personal' as TabId, label: 'Datos Personales', icon: User },
    { id: 'contact' as TabId, label: 'Contacto', icon: Phone },
    { id: 'medical' as TabId, label: 'Información Médica', icon: Heart },
  ];

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900">
              {patientId ? 'Editar Paciente' : 'Nuevo Paciente'}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <div className="flex gap-4 px-6">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => setActiveTab(tab.id)}
                    className={clsx(
                      'flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm transition-colors',
                      activeTab === tab.id
                        ? 'border-teal-600 text-teal-600'
                        : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto">
            <div className="p-6 space-y-6">
              {isLoading ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 mx-auto"></div>
                  <p className="text-gray-600 mt-4">Cargando datos del paciente...</p>
                </div>
              ) : (
                <>
                  {/* Tab 1: Datos Personales */}
                  {activeTab === 'personal' && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Primer nombre *
                          </label>
                          <input
                            type="text"
                            value={formData.primer_nombre}
                            onChange={(e) => handleChange('primer_nombre', e.target.value)}
                            className={clsx(
                              'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent',
                              errors.primer_nombre ? 'border-red-500' : 'border-gray-300'
                            )}
                            placeholder="Juan"
                          />
                          {errors.primer_nombre && (
                            <p className="text-xs text-red-600 mt-1">{errors.primer_nombre}</p>
                          )}
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Segundo nombre
                          </label>
                          <input
                            type="text"
                            value={formData.segundo_nombre}
                            onChange={(e) => handleChange('segundo_nombre', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                            placeholder="Carlos"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Primer apellido *
                          </label>
                          <input
                            type="text"
                            value={formData.primer_apellido}
                            onChange={(e) => handleChange('primer_apellido', e.target.value)}
                            className={clsx(
                              'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent',
                              errors.primer_apellido ? 'border-red-500' : 'border-gray-300'
                            )}
                            placeholder="Pérez"
                          />
                          {errors.primer_apellido && (
                            <p className="text-xs text-red-600 mt-1">{errors.primer_apellido}</p>
                          )}
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Segundo apellido
                          </label>
                          <input
                            type="text"
                            value={formData.segundo_apellido}
                            onChange={(e) => handleChange('segundo_apellido', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                            placeholder="García"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Fecha de nacimiento *
                          </label>
                          <input
                            type="date"
                            value={formData.fecha_nacimiento}
                            onChange={(e) => handleChange('fecha_nacimiento', e.target.value)}
                            className={clsx(
                              'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent',
                              errors.fecha_nacimiento ? 'border-red-500' : 'border-gray-300'
                            )}
                          />
                          {errors.fecha_nacimiento && (
                            <p className="text-xs text-red-600 mt-1">{errors.fecha_nacimiento}</p>
                          )}
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Sexo *
                          </label>
                          <select
                            value={formData.sexo || ''}
                            onChange={(e) => handleChange('sexo', e.target.value)}
                            className={clsx(
                              'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent',
                              errors.sexo ? 'border-red-500' : 'border-gray-300'
                            )}
                          >
                            <option value="">Seleccionar...</option>
                            {SEXO_OPCIONES.map((option) => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </select>
                          {errors.sexo && (
                            <p className="text-xs text-red-600 mt-1">{errors.sexo}</p>
                          )}
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            CURP
                          </label>
                          <input
                            type="text"
                            value={formData.curp}
                            onChange={(e) => handleChange('curp', e.target.value.toUpperCase())}
                            className={clsx(
                              'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent',
                              errors.curp ? 'border-red-500' : 'border-gray-300'
                            )}
                            placeholder="PEJJ850101HDFRRL01"
                            maxLength={18}
                          />
                          {errors.curp && (
                            <p className="text-xs text-red-600 mt-1">{errors.curp}</p>
                          )}
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Estado civil
                          </label>
                          <select
                            value={formData.estado_civil}
                            onChange={(e) => handleChange('estado_civil', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                          >
                            <option value="">Seleccionar...</option>
                            {ESTADO_CIVIL_OPCIONES.map((option) => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </select>
                        </div>

                        <div className="md:col-span-2">
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Ocupación
                          </label>
                          <input
                            type="text"
                            value={formData.ocupacion}
                            onChange={(e) => handleChange('ocupacion', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                            placeholder="Ingeniero, Contador, Estudiante..."
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Tab 2: Contacto */}
                  {activeTab === 'contact' && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Teléfono principal *
                          </label>
                          <input
                            type="tel"
                            value={formData.telefono_principal}
                            onChange={(e) => handleChange('telefono_principal', e.target.value)}
                            className={clsx(
                              'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent',
                              errors.telefono_principal ? 'border-red-500' : 'border-gray-300'
                            )}
                            placeholder="5551234567"
                          />
                          {errors.telefono_principal && (
                            <p className="text-xs text-red-600 mt-1">{errors.telefono_principal}</p>
                          )}
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Teléfono secundario
                          </label>
                          <input
                            type="tel"
                            value={formData.telefono_secundario}
                            onChange={(e) => handleChange('telefono_secundario', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                            placeholder="5559876543"
                          />
                        </div>

                        <div className="md:col-span-2">
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Email
                          </label>
                          <input
                            type="email"
                            value={formData.correo_electronico}
                            onChange={(e) => handleChange('correo_electronico', e.target.value)}
                            className={clsx(
                              'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent',
                              errors.correo_electronico ? 'border-red-500' : 'border-gray-300'
                            )}
                            placeholder="ejemplo@email.com"
                          />
                          {errors.correo_electronico && (
                            <p className="text-xs text-red-600 mt-1">{errors.correo_electronico}</p>
                          )}
                        </div>
                      </div>

                      <div className="border-t border-gray-200 pt-4 mt-4">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Dirección</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Calle
                            </label>
                            <input
                              type="text"
                              value={formData.calle}
                              onChange={(e) => handleChange('calle', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                              placeholder="Av. Reforma"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Número exterior
                            </label>
                            <input
                              type="text"
                              value={formData.numero_exterior}
                              onChange={(e) => handleChange('numero_exterior', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                              placeholder="123"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Número interior
                            </label>
                            <input
                              type="text"
                              value={formData.numero_interior}
                              onChange={(e) => handleChange('numero_interior', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                              placeholder="A"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Colonia
                            </label>
                            <input
                              type="text"
                              value={formData.colonia}
                              onChange={(e) => handleChange('colonia', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                              placeholder="Centro"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Ciudad
                            </label>
                            <input
                              type="text"
                              value={formData.ciudad}
                              onChange={(e) => handleChange('ciudad', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                              placeholder="Ciudad de México"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Estado
                            </label>
                            <input
                              type="text"
                              value={formData.estado}
                              onChange={(e) => handleChange('estado', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                              placeholder="CDMX"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Código postal
                            </label>
                            <input
                              type="text"
                              value={formData.codigo_postal}
                              onChange={(e) => handleChange('codigo_postal', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                              placeholder="06000"
                              maxLength={5}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Tab 3: Información Médica */}
                  {activeTab === 'medical' && (
                    <div className="space-y-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Tipo de sangre
                        </label>
                        <select
                          value={formData.tipo_sangre}
                          onChange={(e) => handleChange('tipo_sangre', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                        >
                          <option value="">Seleccionar...</option>
                          <option value="A+">A+</option>
                          <option value="A-">A-</option>
                          <option value="B+">B+</option>
                          <option value="B-">B-</option>
                          <option value="O+">O+</option>
                          <option value="O-">O-</option>
                          <option value="AB+">AB+</option>
                          <option value="AB-">AB-</option>
                        </select>
                      </div>

                      <AllergyList
                        allergies={formData.alergias || []}
                        onChange={(allergies) => handleChange('alergias', allergies)}
                      />

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          ¿Cómo supo de nosotros?
                        </label>
                        <input
                          type="text"
                          value={formData.como_supo_de_nosotros}
                          onChange={(e) => handleChange('como_supo_de_nosotros', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                          placeholder="Recomendación, redes sociales, internet..."
                        />
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                disabled={isSaving}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="px-6 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                disabled={isSaving}
              >
                {isSaving ? 'Guardando...' : 'Guardar'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default PatientFormModal;
