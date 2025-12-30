import React, { useState } from 'react';
import { X } from 'lucide-react';
import { clsx } from 'clsx';
import type { Allergy } from '../../types/medical';
import { TIPO_ALERGENO_OPCIONES, SEVERIDAD_ALERGIA_OPCIONES } from '../../types/medical';

interface AllergyFormProps {
  onSave: (allergy: Omit<Allergy, 'id'>) => void;
  onCancel: () => void;
  className?: string;
}

/**
 * AllergyForm Component
 * 
 * Inline form for adding a new allergy
 */
const AllergyForm: React.FC<AllergyFormProps> = ({
  onSave,
  onCancel,
  className,
}) => {
  const [formData, setFormData] = useState({
    tipo_alergeno: 'Medicamento' as Allergy['tipo_alergeno'],
    nombre_alergeno: '',
    reaccion: '',
    severidad: 'Moderada' as Allergy['severidad'],
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (field: string, value: string) => {
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

    if (!formData.nombre_alergeno.trim()) {
      newErrors.nombre_alergeno = 'El nombre del alérgeno es obligatorio';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validate()) {
      onSave(formData);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className={clsx(
        'bg-gray-50 border border-gray-200 rounded-lg p-4',
        className
      )}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Tipo de alérgeno */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tipo de alérgeno *
          </label>
          <select
            value={formData.tipo_alergeno}
            onChange={(e) => handleChange('tipo_alergeno', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
          >
            {TIPO_ALERGENO_OPCIONES.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Nombre del alérgeno */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nombre del alérgeno *
          </label>
          <input
            type="text"
            value={formData.nombre_alergeno}
            onChange={(e) => handleChange('nombre_alergeno', e.target.value)}
            placeholder="Ej: Penicilina, Mariscos..."
            className={clsx(
              'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent',
              errors.nombre_alergeno ? 'border-red-500' : 'border-gray-300'
            )}
          />
          {errors.nombre_alergeno && (
            <p className="text-xs text-red-600 mt-1">{errors.nombre_alergeno}</p>
          )}
        </div>

        {/* Reacción */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Reacción
          </label>
          <input
            type="text"
            value={formData.reaccion}
            onChange={(e) => handleChange('reaccion', e.target.value)}
            placeholder="Ej: Urticaria, hinchazón..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
          />
        </div>

        {/* Severidad */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Severidad *
          </label>
          <select
            value={formData.severidad}
            onChange={(e) => handleChange('severidad', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
          >
            {SEVERIDAD_ALERGIA_OPCIONES.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-end gap-2 mt-4">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Cancelar
        </button>
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors"
        >
          Agregar
        </button>
      </div>
    </form>
  );
};

export default AllergyForm;
