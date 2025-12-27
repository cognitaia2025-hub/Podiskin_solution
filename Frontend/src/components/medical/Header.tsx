import React from 'react';
import { Save, Send, Clock, X, FileText, Settings } from 'lucide-react';
import { clsx } from 'clsx';
import type { FormMode, FormState } from '../../types/medical';
import FormModeToggle from './FormModeToggle';
import { ProgressBar } from './ProgressIndicator';

interface HeaderProps {
  patientName?: string;
  formState: FormState;
  formMode: FormMode;
  onModeChange: (mode: FormMode) => void;
  onSave: () => Promise<void>;
  onSubmit: () => Promise<void>;
  onClose?: () => void;
  className?: string;
}

const Header: React.FC<HeaderProps> = ({
  patientName = 'Nuevo Expediente',
  formState,
  formMode,
  onModeChange,
  onSave,
  onSubmit,
  onClose,
  className,
}) => {
  return (
    <header className={clsx(
      'h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 lg:px-6',
      className
    )}>
      {/* Left section - Patient info */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-teal-100 rounded-lg flex items-center justify-center">
            <FileText className="w-5 h-5 text-teal-600" />
          </div>
          <div>
            <h1 className="text-base font-semibold text-gray-800 truncate max-w-xs">
              {patientName}
            </h1>
            <p className="text-xs text-gray-500">
              Expediente Médico
            </p>
          </div>
        </div>

        {/* Mode toggle */}
        <div className="hidden md:block ml-4">
          <FormModeToggle 
            currentMode={formMode} 
            onModeChange={onModeChange}
          />
        </div>
      </div>

      {/* Center section - Progress */}
      <div className="hidden lg:flex flex-col items-center min-w-[200px]">
        <div className="text-xs text-gray-500 mb-1">
          Progreso del Expediente
        </div>
        <div className="w-full max-w-[180px]">
          <ProgressBar 
            percentage={formState.isDirty 
              ? formState.completedSteps.length > 0 
                ? Math.round((formState.completedSteps.length / 12) * 100)
                : 75 // Partial progress when dirty
              : formState.completedSteps.length > 0 
                ? Math.round((formState.completedSteps.length / 12) * 100)
                : 0
            }
            showLabel={false}
            color="teal"
          />
        </div>
      </div>

      {/* Right section - Actions */}
      <div className="flex items-center gap-2">
        {/* Auto-save status */}
        <div className="hidden md:flex items-center gap-1.5 text-xs text-gray-500 mr-2">
          <Clock className="w-3.5 h-3.5" />
          {formState.isSaving ? (
            <span className="text-blue-600">Guardando...</span>
          ) : formState.lastSavedAt ? (
            <span>
              Guardado {formState.lastSavedAt.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </span>
          ) : (
            <span>Sin guardar</span>
          )}
        </div>

        {/* Save button */}
        <button
          onClick={onSave}
          disabled={formState.isSaving || formState.isSubmitting}
          className={clsx(
            'flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
            formState.isSaving || formState.isSubmitting
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
          )}
        >
          <Save className="w-4 h-4" />
          <span className="hidden sm:inline">Guardar</span>
        </button>

        {/* Submit button */}
        <button
          onClick={onSubmit}
          disabled={formState.isSubmitting}
          className={clsx(
            'flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all',
            formState.isSubmitting
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-teal-600 text-white hover:bg-teal-700 shadow-sm'
          )}
        >
          <Send className="w-4 h-4" />
          <span className="hidden sm:inline">
            {formState.isSubmitting ? 'Enviando...' : 'Finalizar'}
          </span>
        </button>

        {/* Close button */}
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        )}

        {/* Settings (for future use) */}
        <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors hidden">
          <Settings className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
};

export default Header;
