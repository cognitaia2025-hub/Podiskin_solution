/**
 * Global Context
 * 
 * Centralized state management for the entire application.
 * Handles cross-module communication (e.g., Calendar -> Medical Attention)
 */

import React, { createContext, useContext, useState, type ReactNode } from 'react';
import type { GlobalContextValue, User } from './types';
import type { Patient } from '../services/patientService';
import type { Appointment } from '../types/appointments';

const GlobalContext = createContext<GlobalContextValue | undefined>(undefined);

interface GlobalProviderProps {
  children: ReactNode;
}

export const GlobalProvider: React.FC<GlobalProviderProps> = ({ children }) => {
  // User state
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  
  // Selected entities
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  
  // UI state
  const [isLoading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Sidebar state
  const [sidebarContent, setSidebarContent] = useState<ReactNode>(null);
  
  /**
   * Clear all selections
   */
  const clearSelections = () => {
    setSelectedPatient(null);
    setSelectedAppointment(null);
  };
  
  const value: GlobalContextValue = {
    // State
    currentUser,
    selectedPatient,
    selectedAppointment,
    isLoading,
    error,
    sidebarContent,
    
    // Actions
    setCurrentUser,
    setSelectedPatient,
    setSelectedAppointment,
    clearSelections,
    setLoading,
    setError,
    setSidebarContent,
  };
  
  return (
    <GlobalContext.Provider value={value}>
      {children}
    </GlobalContext.Provider>
  );
};

/**
 * Hook to access global context
 */
export const useGlobalContext = () => {
  const context = useContext(GlobalContext);
  
  if (!context) {
    throw new Error('useGlobalContext must be used within a GlobalProvider');
  }
  
  return context;
};

export default GlobalContext;
