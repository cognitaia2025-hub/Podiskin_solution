import React from 'react';
import { FolderOpen } from 'lucide-react';

const RecordsPage: React.FC = () => {
    return (
        <div className="flex items-center justify-center h-full bg-gray-50">
            <div className="text-center">
                <FolderOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h2 className="text-2xl font-semibold text-gray-700 mb-2">
                    Expedientes Médicos
                </h2>
                <p className="text-gray-500">
                    Esta sección estará disponible próximamente
                </p>
            </div>
        </div>
    );
};

export default RecordsPage;
