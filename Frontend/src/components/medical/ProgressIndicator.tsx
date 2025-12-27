import React from 'react';
import { Check } from 'lucide-react';
import { clsx } from 'clsx';
import type { GuidedStep } from '../../types/medical';

interface ProgressIndicatorProps {
  steps: GuidedStep[];
  currentStep: number;
  completedSteps: number[];
  onStepClick?: (step: number) => void;
  className?: string;
}

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  steps,
  currentStep,
  completedSteps,
  onStepClick,
  className,
}) => {
  return (
    <div className={clsx('flex items-center gap-2 overflow-x-auto pb-2', className)}>
      {steps.map((step, index) => {
        const isCompleted = completedSteps.includes(step.order);
        const isCurrent = step.order === currentStep;
        const isFuture = step.order > currentStep;
        
        return (
          <React.Fragment key={step.id}>
            {/* Connector line */}
            {index > 0 && (
              <div 
                className={clsx(
                  'flex-1 h-0.5 transition-colors duration-300',
                  isCompleted ? 'bg-teal-500' : 'bg-gray-200'
                )}
                style={{ minWidth: '20px', maxWidth: '40px' }}
              />
            )}
            
            {/* Step indicator */}
            <button
              type="button"
              onClick={() => onStepClick?.(step.order)}
              disabled={isFuture && !isCompleted}
              className={clsx(
                'flex-shrink-0 relative flex items-center justify-center rounded-full transition-all duration-300',
                'w-8 h-8 text-sm font-medium',
                isCompleted && 'bg-teal-500 text-white',
                isCurrent && !isCompleted && 'bg-teal-600 text-white ring-4 ring-teal-100',
                isFuture && !isCompleted && 'bg-gray-200 text-gray-400 cursor-not-allowed',
                !isCurrent && !isFuture && !isCompleted && 'bg-gray-100 text-gray-600',
                (isCurrent || isCompleted) && 'hover:scale-110',
                onStepClick && !isFuture && 'cursor-pointer'
              )}
            >
              {isCompleted ? (
                <Check className="w-4 h-4" />
              ) : (
                <span>{step.order}</span>
              )}
              
              {/* Tooltip */}
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded whitespace-nowrap opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                {step.title}
              </div>
            </button>
          </React.Fragment>
        );
      })}
    </div>
  );
};

// Progress Bar simple
interface ProgressBarProps {
  percentage: number;
  className?: string;
  showLabel?: boolean;
  color?: 'teal' | 'green' | 'blue';
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  percentage,
  className,
  showLabel = true,
  color = 'teal',
}) => {
  const colorClasses = {
    teal: 'bg-teal-500',
    green: 'bg-green-500',
    blue: 'bg-blue-500',
  };

  return (
    <div className={clsx('w-full', className)}>
      <div className="flex justify-between items-center mb-1">
        {showLabel && (
          <span className="text-sm text-gray-600">
            Progreso: {percentage}%
          </span>
        )}
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className={clsx(
            'h-full rounded-full transition-all duration-500',
            colorClasses[color]
          )}
          style={{ width: `${Math.min(100, Math.max(0, percentage))}%` }}
        />
      </div>
    </div>
  );
};

// Circular Progress
interface CircularProgressProps {
  percentage: number;
  size?: number;
  strokeWidth?: number;
  className?: string;
}

export const CircularProgress: React.FC<CircularProgressProps> = ({
  percentage,
  size = 80,
  strokeWidth = 8,
  className,
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div className={clsx('relative inline-flex items-center justify-center', className)}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#14b8a6"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-500"
        />
      </svg>
      <span className="absolute text-lg font-semibold text-gray-700">
        {percentage}%
      </span>
    </div>
  );
};

export default ProgressIndicator;
