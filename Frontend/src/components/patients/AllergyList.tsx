import React, { useState } from 'react';
import { AlertCircle, Plus, X } from 'lucide-react';
import { clsx } from 'clsx';
import type { Allergy } from '../../types/medical';
import AllergyForm from './AllergyForm';

interface AllergyListProps {
  allergies: Allergy[];
  onChange: (allergies: Allergy[]) => void;
  className?: string;
}

/**
 * AllergyList Component
 * 
 * Displays and manages a list of allergies
 */
const AllergyList: React.FC<AllergyListProps> = ({
  allergies,
  onChange,
  className,
}) => {
  const [showForm, setShowForm] = useState(false);

  const handleAddAllergy = (allergyData: Omit<Allergy, 'id'>) => {
    const newAllergy: Allergy = {
      ...allergyData,
      id: crypto.randomUUID(),
    };
    onChange([...allergies, newAllergy]);
    setShowForm(false);
  };

  const handleRemoveAllergy = (id: string) => {
    onChange(allergies.filter(a => a.id !== id));
  };

  // Get icon for allergy type
  const getAllergyIcon = (tipo: Allergy['tipo_alergeno']): string => {
    const icons: Record<Allergy['tipo_alergeno'], string> = {
      'Medicamento': '💊',
      'Alimento': '🥜',
      'Ambiental': '🌿',
      'Material': '🧪',
      'Otro': '⚠️',
    };
    return icons[tipo] || '⚠️';
  };

  // Get severity color
  const getSeverityColor = (severidad: Allergy['severidad']): string => {
    const colors: Record<Allergy['severidad'], string> = {
      'Leve': 'bg-yellow-100 text-yellow-700 border-yellow-200',
      'Moderada': 'bg-orange-100 text-orange-700 border-orange-200',
      'Grave': 'bg-red-100 text-red-700 border-red-200',
      'Mortal': 'bg-red-200 text-red-900 border-red-300 font-bold',
    };
    return colors[severidad];
  };

  return (
    <div className={clsx('space-y-3', className)}>
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">
          Alergias conocidas
        </label>
        {!showForm && (
          <button
            type="button"
            onClick={() => setShowForm(true)}
            className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-teal-700 bg-teal-50 border border-teal-200 rounded-lg hover:bg-teal-100 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Agregar alergia
          </button>
        )}
      </div>

      {/* Allergies List */}
      {allergies.length > 0 && (
        <div className="space-y-2">
          {allergies.map((allergy) => (
            <div
              key={allergy.id}
              className="bg-white border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-shadow"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{getAllergyIcon(allergy.tipo_alergeno)}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-medium text-gray-900">
                          {allergy.nombre_alergeno}
                        </span>
                        <span className="text-xs text-gray-500">
                          ({allergy.tipo_alergeno})
                        </span>
                        <span
                          className={clsx(
                            'px-2 py-0.5 text-xs font-medium rounded-full border',
                            getSeverityColor(allergy.severidad)
                          )}
                        >
                          {allergy.severidad}
                        </span>
                      </div>
                      {allergy.reaccion && (
                        <p className="text-sm text-gray-600 mt-1">
                          Reacción: {allergy.reaccion}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => handleRemoveAllergy(allergy.id)}
                  className="text-gray-400 hover:text-red-600 transition-colors"
                  title="Eliminar alergia"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {allergies.length === 0 && !showForm && (
        <div className="text-center py-6 bg-gray-50 border border-dashed border-gray-300 rounded-lg">
          <AlertCircle className="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p className="text-sm text-gray-600">
            No hay alergias registradas
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Haz clic en "Agregar alergia" para comenzar
          </p>
        </div>
      )}

      {/* Add Form */}
      {showForm && (
        <AllergyForm
          onSave={handleAddAllergy}
          onCancel={() => setShowForm(false)}
        />
      )}
    </div>
  );
};

export default AllergyList;
