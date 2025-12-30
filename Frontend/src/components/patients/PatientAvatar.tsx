import React from 'react';
import { clsx } from 'clsx';

interface PatientAvatarProps {
  firstName: string;
  lastName: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

/**
 * PatientAvatar Component
 * 
 * Displays a circular avatar with patient initials
 * Uses a consistent color based on the patient's name
 */
const PatientAvatar: React.FC<PatientAvatarProps> = ({
  firstName,
  lastName,
  size = 'md',
  className,
}) => {
  // Generate initials from first and last name
  const getInitials = (): string => {
    const firstInitial = firstName?.[0]?.toUpperCase() || '';
    const lastInitial = lastName?.[0]?.toUpperCase() || '';
    return `${firstInitial}${lastInitial}` || 'PN';
  };

  // Generate a consistent color based on the name
  const getColor = (): string => {
    const fullName = `${firstName}${lastName}`.toLowerCase();
    let hash = 0;
    
    for (let i = 0; i < fullName.length; i++) {
      hash = fullName.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    // Map hash to a set of predefined colors for better aesthetics
    const colors = [
      'bg-gradient-to-br from-blue-400 to-blue-600',
      'bg-gradient-to-br from-green-400 to-green-600',
      'bg-gradient-to-br from-purple-400 to-purple-600',
      'bg-gradient-to-br from-pink-400 to-pink-600',
      'bg-gradient-to-br from-indigo-400 to-indigo-600',
      'bg-gradient-to-br from-teal-400 to-teal-600',
      'bg-gradient-to-br from-orange-400 to-orange-600',
      'bg-gradient-to-br from-red-400 to-red-600',
    ];
    
    const index = Math.abs(hash) % colors.length;
    return colors[index];
  };

  // Size classes
  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-12 h-12 text-sm',
    lg: 'w-16 h-16 text-lg',
  };

  return (
    <div
      className={clsx(
        'rounded-full flex items-center justify-center text-white font-semibold shadow-md flex-shrink-0',
        getColor(),
        sizeClasses[size],
        className
      )}
    >
      {getInitials()}
    </div>
  );
};

export default PatientAvatar;
