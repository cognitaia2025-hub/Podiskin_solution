import React, { useState, useRef, useEffect } from 'react';
import { HelpCircle } from 'lucide-react';
import { clsx } from 'clsx';

interface HelpTooltipProps {
  text: string;
  className?: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

const HelpTooltip: React.FC<HelpTooltipProps> = ({ 
  text, 
  className,
  position = 'top' 
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (tooltipRef.current && !tooltipRef.current.contains(event.target as Node)) {
        setIsVisible(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const positionClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  const arrowClasses = {
    top: 'top-full left-1/2 -translate-x-1/2 border-t-gray-900',
    bottom: 'bottom-full left-1/2 -translate-x-1/2 border-b-gray-900',
    left: 'left-full top-1/2 -translate-y-1/2 border-l-gray-900',
    right: 'right-full top-1/2 -translate-y-1/2 border-r-gray-900',
  };

  return (
    <div className={clsx('relative inline-flex', className)}>
      <button
        ref={buttonRef}
        type="button"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        onClick={() => setIsVisible(!isVisible)}
        className="inline-flex items-center justify-center w-4 h-4 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors cursor-help"
      >
        <HelpCircle className="w-3.5 h-3.5" />
      </button>

      {isVisible && (
        <div
          ref={tooltipRef}
          className={clsx(
            'absolute z-50 w-64 p-3 text-sm text-white bg-gray-900 rounded-lg shadow-lg',
            'opacity-100 scale-100 transition-all duration-200',
            positionClasses[position]
          )}
          style={{ 
            transform: position === 'top' || position === 'bottom' 
              ? 'translateX(-50%)' 
              : undefined 
          }}
        >
          {text}
          <div 
            className={clsx(
              'absolute w-0 h-0 border-4 border-transparent',
              arrowClasses[position]
            )}
            style={{ 
              borderWidth: '6px',
              [position === 'top' ? 'borderTopColor' : position === 'bottom' ? 'borderBottomColor' : position === 'left' ? 'borderLeftColor' : 'borderRightColor']: '#111827'
            }}
          />
        </div>
      )}
    </div>
  );
};

export default HelpTooltip;
