import React from 'react';
import { List, Wand2 } from 'lucide-react';
import { clsx } from 'clsx';
import type { FormMode } from '../../types/medical';

interface FormModeToggleProps {
  currentMode: FormMode;
  onModeChange: (mode: FormMode) => void;
  className?: string;
}

const FormModeToggle: React.FC<FormModeToggleProps> = ({
  currentMode,
  onModeChange,
  className,
}) => {
  return (
    <div className={clsx('flex items-center gap-1 bg-gray-100 p-1 rounded-lg', className)}>
      <button
        type="button"
        onClick={() => onModeChange('free')}
        className={clsx(
          'flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200',
          currentMode === 'free'
            ? 'bg-white text-gray-900 shadow-sm'
            : 'text-gray-600 hover:text-gray-900'
        )}
      >
        <List className="w-4 h-4" />
        <span className="hidden sm:inline">Libre</span>
      </button>
      
      <button
        type="button"
        onClick={() => onModeChange('guided')}
        className={clsx(
          'flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200',
          currentMode === 'guided'
            ? 'bg-white text-gray-900 shadow-sm'
            : 'text-gray-600 hover:text-gray-900'
        )}
      >
        <Wand2 className="w-4 h-4" />
        <span className="hidden sm:inline">Guiado</span>
      </button>
    </div>
  );
};

export default FormModeToggle;
