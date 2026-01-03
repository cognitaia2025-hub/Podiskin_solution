/**
 * Global Context Types
 * 
 * Shared type definitions for the global application context
 */

import type { Patient } from '../services/patientService';
import type { Appointment } from '../types/appointments';

export interface User {
  id: number;
  username: string;
  email: string;
  rol: string;
  nombre_completo: string;
}

export interface GlobalState {
  // User state
  currentUser: User | null;
  
  // Selected entities (for cross-module communication)
  selectedPatient: Patient | null;
  selectedAppointment: Appointment | null;
  
  // UI state
  isLoading: boolean;
  error: string | null;
  
  // Sidebar state (inherited from ShellContext, but centralized here)
  sidebarContent: React.ReactNode;
}

export interface GlobalContextActions {
  // Patient selection
  setSelectedPatient: (patient: Patient | null) => void;
  
  // Appointment selection
  setSelectedAppointment: (appointment: Appointment | null) => void;
  
  // Clear selections
  clearSelections: () => void;
  
  // Loading and error states
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // User management
  setCurrentUser: (user: User | null) => void;
  
  // Sidebar management
  setSidebarContent: (content: React.ReactNode) => void;
}

export interface GlobalContextValue extends GlobalState, GlobalContextActions {}
