import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Plus, Calendar, User, Activity, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { clsx } from 'clsx';

interface EvolutionEntry {
  id: string;
  fase: number;
  fecha: string;
  descripcion: string;
  resultado: 'Mejoría' | 'Sin cambios' | 'Empeoramiento';
  indicaciones: string;
  podologo: string;
}

interface EvolutionSidebarProps {
  className?: string;
  evolucion?: EvolutionEntry[];
}

// Datos de ejemplo para demo
const MOCK_EVOLUTION: EvolutionEntry[] = [
  {
    id: '1',
    fase: 1,
    fecha: '2025-12-20',
    descripcion: 'Primera consulta. Paciente refiere dolor en talón derecho de 2 semanas de evolución. Exploración revela punto gatillo en inserción de fascia plantar.',
    resultado: 'Mejoría',
    indicaciones: 'Reposo relativo, hielo local 15 min 3 veces al día, ejercicios de estiramiento de fascia. Próxima cita en 7 días.',
    podologo: 'Dr. Alejandro Martínez',
  },
  {
    id: '2',
    fase: 2,
    fecha: '2025-12-27',
    descripcion: 'Segunda consulta. Paciente reporta disminución del dolor en un 50%. Mejor tolerancia a la marcha. Exploración muestra reducción de sensibilidad en punto gatillo.',
    resultado: 'Mejoría',
    indicaciones: 'Continuar con ejercicios de fortalecimiento de tibial posterior. Iniciar ejercicios de propiocepción. Próxima cita en 14 días.',
    podologo: 'Dr. Alejandro Martínez',
  },
  {
    id: '3',
    fase: 3,
    fecha: '2026-01-03',
    descripcion: 'Tercera consulta. Paciente asintomático en actividades de la vida diaria. Exploración física sin hallazgos patológicos. Prueba de Windlass negativa bilateral.',
    resultado: 'Mejoría',
    indicaciones: 'Alta médica. Recomendaciones: continuar ejercicios de mantenimiento 2 veces por semana, uso de calzado con buen soporte, plantillas de regalo. Seguimiento en 3 meses.',
    podologo: 'Dr. Alejandro Martínez',
  },
];

const EvolutionSidebar: React.FC<EvolutionSidebarProps> = ({
  className,
  evolucion = MOCK_EVOLUTION,
}) => {
  const [expandedEntries, setExpandedEntries] = useState<Record<string, boolean>>({
    [MOCK_EVOLUTION[0]?.id || '']: true,
  });
  const [showAddForm, setShowAddForm] = useState(false);

  const toggleEntry = (id: string) => {
    setExpandedEntries(prev => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const getResultadoIcon = (resultado: string) => {
    switch (resultado) {
      case 'Mejoría':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'Empeoramiento':
        return <TrendingDown className="w-4 h-4 text-red-500" />;
      default:
        return <Minus className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getResultadoColor = (resultado: string) => {
    switch (resultado) {
      case 'Mejoría':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'Empeoramiento':
        return 'bg-red-100 text-red-700 border-red-200';
      default:
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
    }
  };

  // Ordenar evolución por fase (más reciente primero)
  const sortedEvolution = [...evolucion].sort((a, b) => b.fase - a.fase);

  // Calcular estadísticas
  const stats = {
    totalFases: evolucion.length,
    ultimaFase: evolucion.length > 0 ? Math.max(...evolucion.map(e => e.fase)) : 0,
    Mejoría: evolucion.filter(e => e.resultado === 'Mejoría').length,
    SinCambios: evolucion.filter(e => e.resultado === 'Sin cambios').length,
    Empeoramiento: evolucion.filter(e => e.resultado === 'Empeoramiento').length,
  };

  return (
    <div className={clsx('h-full flex flex-col bg-white rounded-lg border border-gray-200', className)}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-600" />
            <h3 className="text-sm font-semibold text-gray-800">Evolución del Tratamiento</h3>
          </div>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="p-1.5 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
        
        {/* Stats */}
        <div className="flex items-center gap-3 mt-3">
          <div className="flex items-center gap-1.5">
            <span className="text-xs text-gray-500">Fases:</span>
            <span className="text-xs font-medium text-gray-700">{stats.totalFases}</span>
          </div>
          <div className={clsx('flex items-center gap-1 px-2 py-0.5 rounded-full text-xs', getResultadoColor('Mejoría'))}>
            {getResultadoIcon('Mejoría')}
            <span>{stats.Mejoría}</span>
          </div>
          <div className={clsx('flex items-center gap-1 px-2 py-0.5 rounded-full text-xs', getResultadoColor('Sin cambios'))}>
            {getResultadoIcon('Sin cambios')}
            <span>{stats.SinCambios}</span>
          </div>
        </div>
      </div>

      {/* Add form */}
      {showAddForm && (
        <div className="p-4 border-b border-gray-200 bg-blue-50">
          <h4 className="text-xs font-semibold text-gray-700 mb-2">Nueva Fase de Evolución</h4>
          <textarea
            placeholder="Descripción de la evolución..."
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
          <div className="flex items-center justify-between mt-2">
            <select className="px-2 py-1 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="Mejoría">Mejoría</option>
              <option value="Sin cambios">Sin cambios</option>
              <option value="Empeoramiento">Empeoramiento</option>
            </select>
            <button className="px-3 py-1 text-xs font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              Guardar
            </button>
          </div>
        </div>
      )}

      {/* Evolution list */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {sortedEvolution.map((entry) => {
          const isExpanded = expandedEntries[entry.id];
          
          return (
            <div
              key={entry.id}
              className="border border-gray-200 rounded-lg overflow-hidden bg-white"
            >
              {/* Entry header */}
              <button
                onClick={() => toggleEntry(entry.id)}
                className="w-full px-3 py-2 flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-medium">
                    {entry.fase}
                  </span>
                  <div className="text-left">
                    <p className="text-xs font-medium text-gray-800">
                      {new Date(entry.fecha).toLocaleDateString('es-ES', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                      })}
                    </p>
                    <p className="text-xs text-gray-500 truncate max-w-[120px]">
                      {entry.descripcion}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={clsx('px-1.5 py-0.5 text-xs font-medium rounded border', getResultadoColor(entry.resultado))}>
                    {entry.resultado}
                  </span>
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  )}
                </div>
              </button>

              {/* Entry details */}
              {isExpanded && (
                <div className="px-3 pb-3 border-t border-gray-100">
                  <div className="pt-2 space-y-2">
                    <div>
                      <p className="text-xs font-medium text-gray-500 mb-1">Descripción</p>
                      <p className="text-xs text-gray-700">{entry.descripcion}</p>
                    </div>
                    
                    <div>
                      <p className="text-xs font-medium text-gray-500 mb-1">Indicaciones</p>
                      <p className="text-xs text-gray-700">{entry.indicaciones}</p>
                    </div>
                    
                    <div className="flex items-center gap-2 pt-2 border-t border-gray-100">
                      <User className="w-3 h-3 text-gray-400" />
                      <span className="text-xs text-gray-500">{entry.podologo}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}

        {evolucion.length === 0 && (
          <div className="text-center py-8">
            <Activity className="w-10 h-10 text-gray-300 mx-auto mb-2" />
            <p className="text-sm text-gray-500">
              No hay registro de evolución
            </p>
            <p className="text-xs text-gray-400 mt-1">
              Agrega la primera fase cuando inicies el tratamiento
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            Última: {evolucion.length > 0 
              ? new Date(MOCK_EVOLUTION[0]?.fecha || '').toLocaleDateString('es-ES')
              : 'N/A'}
          </span>
          <span className="flex items-center gap-1">
            <Activity className="w-3 h-3" />
            {stats.ultimaFase} fases
          </span>
        </div>
      </div>
    </div>
  );
};

export default EvolutionSidebar;
