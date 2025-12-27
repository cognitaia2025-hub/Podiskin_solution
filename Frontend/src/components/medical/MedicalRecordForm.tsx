import React, { useState } from 'react';
import { useFormContext } from 'react-hook-form';
import { FileText, ChevronDown, ChevronUp } from 'lucide-react';
import { clsx } from 'clsx';
import type { MedicalRecord, FormMode, FormSection } from '../../types/medical';
import { FORM_SECTIONS } from '../../utils/formSections';
import SectionAccordion from './SectionAccordion';
import FormModeToggle from './FormModeToggle';
import ProgressIndicator, { ProgressBar } from './ProgressIndicator';
import { useMedicalForm, useGuidedMode, useFreeMode } from '../../context/MedicalFormContext';

interface MedicalRecordFormProps {
  className?: string;
  initialMode?: FormMode;
}

const MedicalRecordForm: React.FC<MedicalRecordFormProps> = ({
  className,
  initialMode = 'free',
}) => {
  const { formState, setFormMode, updateFormData } = useMedicalForm();
  const [mode, setMode] = useState<FormMode>(initialMode);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});

  const handleModeChange = (newMode: FormMode) => {
    setMode(newMode);
    setFormMode(newMode);
  };

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId],
    }));
  };

  const allSectionsExpanded = Object.values(expandedSections).every(v => v);
  const toggleAllSections = () => {
    const newState = !allSectionsExpanded;
    const newExpanded: Record<string, boolean> = {};
    FORM_SECTIONS.forEach(s => {
      newExpanded[s.id] = newState;
    });
    setExpandedSections(newExpanded);
  };

  return (
    <div className={clsx('h-full flex flex-col', className)}>
      {/* Mode selector and expand/collapse */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <FormModeToggle 
            currentMode={mode} 
            onModeChange={handleModeChange}
          />
          
          {/* Progress indicator for guided mode */}
          {mode === 'guided' && (
            <div className="hidden md:block">
              <ProgressIndicator
                steps={[]}
                currentStep={formState.currentStep}
                completedSteps={formState.completedSteps}
              />
            </div>
          )}
        </div>

        <button
          onClick={toggleAllSections}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
        >
          {allSectionsExpanded ? (
            <>
              <ChevronUp className="w-3.5 h-3.5" />
              Contraer todo
            </>
          ) : (
            <>
              <ChevronDown className="w-3.5 h-3.5" />
              Expandir todo
            </>
          )}
        </button>
      </div>

      {/* Progress bar for free mode */}
      {mode === 'free' && (
        <div className="px-4 py-2 bg-white border-b border-gray-200">
          <ProgressBar
            percentage={Math.round((formState.completedSteps.length / FORM_SECTIONS.length) * 100)}
            className="max-w-xs"
          />
        </div>
      )}

      {/* Form content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-100">
        {mode === 'free' ? (
          <FreeModeView 
            expandedSections={expandedSections}
            toggleSection={toggleSection}
          />
        ) : (
          <GuidedModeView />
        )}
      </div>
    </div>
  );
};

// Vista del modo libre (formulario con acordeones)
interface FreeModeViewProps {
  expandedSections: Record<string, boolean>;
  toggleSection: (sectionId: string) => void;
}

const FreeModeView: React.FC<FreeModeViewProps> = ({
  expandedSections,
  toggleSection,
}) => {
  return (
    <div className="space-y-4">
      {FORM_SECTIONS.map((section) => {
        const isExpanded = expandedSections[section.id] ?? true;
        
        return (
          <SectionAccordion
            key={section.id}
            section={section}
            isOpen={isExpanded}
            onToggle={() => toggleSection(section.id)}
            showProgress={true}
          />
        );
      })}
    </div>
  );
};

// Vista del modo guiado (wizard)
const GuidedModeView: React.FC = () => {
  const { currentStep, currentStepData, goToNextStep, goToPreviousStep, completeCurrentStep, progress } = useGuidedMode();
  const { formState } = useMedicalForm();

  // Find current section
  const currentSection = FORM_SECTIONS.find(s => s.id === currentStepData?.sectionId);

  return (
    <div className="max-w-3xl mx-auto">
      {/* Step header */}
      <div className="mb-6 p-4 bg-white rounded-lg border border-gray-200 shadow-sm">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-teal-600 uppercase tracking-wider">
            Paso {currentStep} de 12
          </span>
          <span className="text-sm text-gray-500">
            {progress}% completado
          </span>
        </div>
        <h2 className="text-xl font-semibold text-gray-800">
          {currentStepData?.title}
        </h2>
        {currentStepData?.description && (
          <p className="text-sm text-gray-600 mt-1">
            {currentStepData.description}
          </p>
        )}
        
        {/* Progress bar */}
        <div className="mt-3">
          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-teal-500 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Step content */}
      {currentSection && (
        <div className="mb-6">
          <SectionAccordion
            section={currentSection}
            isOpen={true}
            showProgress={true}
          />
        </div>
      )}

      {/* Navigation buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <button
          onClick={goToPreviousStep}
          disabled={currentStep === 1}
          className={clsx(
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            currentStep === 1
              ? 'text-gray-300 cursor-not-allowed'
              : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
          )}
        >
          Anterior
        </button>

        <div className="flex items-center gap-2">
          {/* Step dots */}
          <div className="flex gap-1">
            {Array.from({ length: 12 }).map((_, i) => (
              <div
                key={i}
                className={clsx(
                  'w-2 h-2 rounded-full transition-colors',
                  i + 1 === currentStep
                    ? 'bg-teal-500'
                    : formState.completedSteps.includes(i + 1)
                    ? 'bg-green-500'
                    : 'bg-gray-300'
                )}
              />
            ))}
          </div>
        </div>

        {currentStep < 12 ? (
          <button
            onClick={completeCurrentStep}
            className="px-4 py-2 rounded-lg text-sm font-medium bg-teal-600 text-white hover:bg-teal-700 transition-colors"
          >
            Siguiente
          </button>
        ) : (
          <button
            className="px-4 py-2 rounded-lg text-sm font-medium bg-green-600 text-white hover:bg-green-700 transition-colors"
          >
            Finalizar
          </button>
        )}
      </div>
    </div>
  );
};

export default MedicalRecordForm;
