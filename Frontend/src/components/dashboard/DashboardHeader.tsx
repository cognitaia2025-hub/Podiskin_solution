/**
 * Dashboard Header Component
 * 
 * Header with title and refresh button.
 */

import React, { useState } from 'react';
import { RefreshCw } from 'lucide-react';

interface DashboardHeaderProps {
  onRefresh: () => Promise<void>;
  lastUpdated?: Date;
}

const DashboardHeader: React.FC<DashboardHeaderProps> = ({ onRefresh, lastUpdated }) => {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">📊 Dashboard</h1>
        {lastUpdated && (
          <p className="text-sm text-gray-500 mt-1">
            Última actualización: {lastUpdated.toLocaleTimeString('es-MX', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </p>
        )}
      </div>
      <button
        onClick={handleRefresh}
        disabled={isRefreshing}
        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
        Actualizar
      </button>
    </div>
  );
};

export default DashboardHeader;
