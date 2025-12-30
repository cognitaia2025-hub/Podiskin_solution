/**
 * PatientAutocomplete Component
 * 
 * Autocomplete search for patients with debounce
 */

import React, { useState, useEffect } from 'react';
import { User, Search, UserPlus, Phone } from 'lucide-react';
import { searchPatients } from '../../services/patientService';
import type { Patient } from '../../services/patientService';

interface PatientAutocompleteProps {
  value: string | null;
  onChange: (patientId: string, patient: Patient) => void;
  onCreateNew?: () => void;
  error?: string;
}

const PatientAutocomplete: React.FC<PatientAutocompleteProps> = ({
  value,
  onChange,
  onCreateNew,
  error
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  // Debounced search
  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      return;
    }

    setIsSearching(true);
    const timer = setTimeout(async () => {
      try {
        const patients = await searchPatients(query);
        setResults(patients);
      } catch (error) {
        console.error('Error searching patients:', error);
        setResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  // Reset search when value prop changes
  useEffect(() => {
    if (!value) {
      setQuery('');
      setSelectedPatient(null);
    }
  }, [value]);

  const handleSelect = (patient: Patient) => {
    setSelectedPatient(patient);
    setQuery(patient.name);
    setIsOpen(false);
    onChange(patient.id, patient);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value;
    setQuery(newQuery);
    setIsOpen(true);
    
    if (!newQuery) {
      setSelectedPatient(null);
      onChange('', {} as Patient);
    }
  };

  return (
    <div className="relative">
      <div className="relative">
        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          <Search className="w-5 h-5" />
        </div>
        <input
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={() => setIsOpen(true)}
          placeholder="Buscar por nombre o teléfono..."
          className={`
            w-full pl-10 pr-4 py-3 border-2 rounded-lg
            focus:outline-none focus:ring-2 focus:ring-primary-500/20
            transition-all duration-200
            ${error 
              ? 'border-red-300 bg-red-50' 
              : selectedPatient 
                ? 'border-green-300 bg-green-50' 
                : 'border-gray-200 bg-white hover:border-gray-300'
            }
          `}
        />
        {isSearching && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}

      {/* Selected patient info */}
      {selectedPatient && !isOpen && (
        <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
          <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
            <User className="w-5 h-5 text-green-600" />
          </div>
          <div className="flex-1">
            <p className="font-medium text-green-900">{selectedPatient.name}</p>
            {selectedPatient.phone && (
              <p className="text-sm text-green-700 flex items-center gap-1">
                <Phone className="w-3 h-3" />
                {selectedPatient.phone}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Dropdown results */}
      {isOpen && query.length >= 2 && (
        <div className="absolute z-50 w-full mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl max-h-64 overflow-y-auto">
          {results.length > 0 ? (
            <>
              {results.map((patient) => (
                <button
                  key={patient.id}
                  type="button"
                  onClick={() => handleSelect(patient)}
                  className="w-full px-4 py-3 flex items-center gap-3 hover:bg-gray-50 transition-colors text-left border-b border-gray-100 last:border-0"
                >
                  <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <User className="w-5 h-5 text-primary-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">{patient.name}</p>
                    {patient.phone && (
                      <p className="text-sm text-gray-600 flex items-center gap-1">
                        <Phone className="w-3 h-3" />
                        {patient.phone}
                      </p>
                    )}
                  </div>
                </button>
              ))}
            </>
          ) : isSearching ? (
            <div className="px-4 py-6 text-center text-gray-500">
              <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
              <p>Buscando pacientes...</p>
            </div>
          ) : (
            <div className="px-4 py-6 text-center text-gray-500">
              <User className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <p>No se encontraron pacientes</p>
            </div>
          )}

          {/* Create new patient button */}
          {onCreateNew && (
            <button
              type="button"
              onClick={() => {
                setIsOpen(false);
                onCreateNew();
              }}
              className="w-full px-4 py-3 flex items-center gap-3 bg-primary-50 hover:bg-primary-100 transition-colors border-t-2 border-primary-200"
            >
              <div className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center">
                <UserPlus className="w-5 h-5 text-white" />
              </div>
              <div className="text-left">
                <p className="font-semibold text-primary-700">Crear nuevo paciente</p>
                <p className="text-sm text-primary-600">Agregar paciente al sistema</p>
              </div>
            </button>
          )}
        </div>
      )}

      {/* Click outside handler */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default PatientAutocomplete;
