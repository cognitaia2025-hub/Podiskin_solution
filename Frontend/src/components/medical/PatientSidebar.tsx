import React from 'react';
import { User, Phone, Mail, Calendar, AlertCircle, Activity } from 'lucide-react';
import { clsx } from 'clsx';
import type { MedicalRecord } from '../../types/medical';
import { useGlobalContext } from '../../context/GlobalContext';

interface PatientSidebarProps {
  patientData?: Partial<MedicalRecord>;
  className?: string;
}

const PatientSidebar: React.FC<PatientSidebarProps> = ({
  patientData,
  className,
}) => {
  const { selectedPatient } = useGlobalContext();
  
  // Use selectedPatient from context if available, otherwise use patientData prop
  const patient = selectedPatient || patientData;
  
  // If using selectedPatient from context, create a mock informacion_personal
  const informacion_personal = patient && 'name' in patient
    ? {
        primer_nombre: patient.name?.split(' ')[0] || '',
        primer_apellido: patient.name?.split(' ')[1] || '',
        telefono_principal: patient.phone,
        correo_electronico: patient.email,
        fecha_nacimiento: patient.fecha_nacimiento,
      }
    : patientData?.informacion_personal;
  
  const alergias = patientData?.alergias;
  const estilo_vida = patientData?.estilo_vida;
  
  // Calcular edad desde fecha de nacimiento
  const calculateAge = (birthDate?: string): number | null => {
    if (!birthDate) return null;
    const birth = new Date(birthDate);
    const today = new Date();
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  const age = calculateAge(informacion_personal?.fecha_nacimiento);
  
  // Obtener iniciales del nombre
  const getInitials = () => {
    const first = informacion_personal?.primer_nombre?.[0] || '';
    const last = informacion_personal?.primer_apellido?.[0] || '';
    return `${first}${last}`.toUpperCase() || 'PN';
  };

  // Determinar riesgo basado en antecedentes
  const getRiskLevel = (): { level: 'low' | 'medium' | 'high'; label: string } => {
    let riskPoints = 0;
    
    // Factores de riesgo
    if (estilo_vida?.fuma) riskPoints += 1;
    if (estilo_vida?.dieta === 'Diabética') riskPoints += 2;
    if (estilo_vida?.diabetes) riskPoints += 2;
    if (alergias && alergias.length > 0) riskPoints += 0.5;
    
    if (riskPoints >= 3) return { level: 'high', label: 'Alto Riesgo' };
    if (riskPoints >= 1) return { level: 'medium', label: 'Riesgo Moderado' };
    return { level: 'low', label: 'Bajo Riesgo' };
  };

  const risk = getRiskLevel();

  const riskColors = {
    low: 'bg-green-100 text-green-700 border-green-200',
    medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    high: 'bg-red-100 text-red-700 border-red-200',
  };

  // Empty state if no patient selected
  if (!patient && !patientData) {
    return (
      <div className={clsx('h-full flex flex-col bg-white border-r border-gray-200', className)}>
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center">
            <User className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No hay paciente seleccionado
            </h3>
            <p className="text-sm text-gray-600">
              Selecciona un paciente de la lista para ver su información
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={clsx('h-full flex flex-col bg-white border-r border-gray-200', className)}>
      {/* Header del paciente */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-14 h-14 bg-gradient-to-br from-teal-400 to-teal-600 rounded-full flex items-center justify-center text-white text-lg font-semibold shadow-lg">
            {getInitials()}
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="text-lg font-semibold text-gray-800 truncate">
              {informacion_personal?.primer_nombre} {informacion_personal?.primer_apellido}
            </h2>
            <div className="flex items-center gap-2 mt-1">
              <span className={clsx(
                'px-2 py-0.5 text-xs font-medium rounded-full border',
                riskColors[risk.level]
              )}>
                {risk.label}
              </span>
              {age && (
                <span className="text-xs text-gray-500">
                  {age} años
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Información de contacto */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
          Información de Contacto
        </h3>
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-gray-700">
            <Phone className="w-4 h-4 text-gray-400 flex-shrink-0" />
            <span className="truncate">
              {informacion_personal?.telefono_principal || 'Sin teléfono'}
            </span>
          </div>
          {informacion_personal?.correo_electronico && (
            <div className="flex items-center gap-2 text-sm text-gray-700">
              <Mail className="w-4 h-4 text-gray-400 flex-shrink-0" />
              <span className="truncate">{informacion_personal.correo_electronico}</span>
            </div>
          )}
          <div className="flex items-center gap-2 text-sm text-gray-700">
            <Calendar className="w-4 h-4 text-gray-400 flex-shrink-0" />
            <span>
              Nac: {informacion_personal?.fecha_nacimiento 
                ? new Date(informacion_personal.fecha_nacimiento).toLocaleDateString('es-ES')
                : 'No especificada'}
            </span>
          </div>
        </div>
      </div>

      {/* Alertas de alergias */}
      {alergias && alergias.length > 0 && (
        <div className="p-4 border-b border-gray-200 bg-red-50">
          <h3 className="text-xs font-semibold text-red-600 uppercase tracking-wider mb-3 flex items-center gap-1">
            <AlertCircle className="w-3.5 h-3.5" />
            Alergias ({alergias.length})
          </h3>
          <div className="space-y-2">
            {alergias.map((alergia, index) => (
              <div 
                key={index} 
                className="p-2 bg-white rounded-lg border border-red-100"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-800">
                    {alergia.nombre_alergeno}
                  </span>
                  <span className={clsx(
                    'text-xs px-1.5 py-0.5 rounded',
                    alergia.severidad === 'Grave' || alergia.severidad === 'Mortal'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-yellow-100 text-yellow-700'
                  )}>
                    {alergia.severidad}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {alergia.tipo_alergeno}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Resumen generado por IA */}
      <div className="flex-1 p-4 overflow-y-auto">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-1">
          <Activity className="w-3.5 h-3.5" />
          Resumen IA
        </h3>
        
        <div className="p-3 bg-gradient-to-br from-violet-50 to-purple-50 rounded-lg border border-violet-100">
          <p className="text-xs text-gray-700 leading-relaxed">
            <strong className="text-violet-700">Paciente:</strong>{' '}
            {informacion_personal?.primer_nombre} {informacion_personal?.primer_apellido}
            {age && `, ${age} años`}. 
            {informacion_personal?.sexo === 'F' ? ' Mujer' : informacion_personal?.sexo === 'M' ? ' Hombre' : ''}.
          </p>
          
          <p className="text-xs text-gray-700 leading-relaxed mt-2">
            <strong className="text-violet-700">Motivo:</strong>{' '}
            En evaluación inicial. Presenta sintomatología que requiere valoración podológica completa.
          </p>
          
          <p className="text-xs text-gray-700 leading-relaxed mt-2">
            <strong className="text-violet-700">Observaciones:</strong>{' '}
            {alergias && alergias.length > 0
              ? `Alérgico a ${alergias.map(a => a.nombre_alergeno).join(', ')}. `
              : 'Sin alergias reportadas. '}
            {estilo_vida?.fuma ? 'Fumador activo. ' : 'No fumador. '}
            Estilo de vida: {estilo_vida?.dieta || 'No especificado'}.
          </p>

          <p className="text-xs text-gray-500 mt-3 pt-2 border-t border-violet-200">
            Generado por Maya • {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>ID: {(patient && 'id' in patient ? patient.id : patientData?.id_paciente) || 'N/A'}</span>
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            En consulta
          </span>
        </div>
      </div>
    </div>
  );
};

export default PatientSidebar;
