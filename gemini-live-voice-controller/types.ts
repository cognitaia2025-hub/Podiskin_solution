import { FunctionDeclaration } from "@google/genai";

export enum VoiceName {
  Puck = 'Puck',
  Charon = 'Charon',
  Kore = 'Kore',
  Fenrir = 'Fenrir',
  Zephyr = 'Zephyr',
}

export interface LiveConfig {
  voiceName: VoiceName;
  systemInstruction: string;
}

// App State Types for the Demo
export type AppSection = 'dashboard' | 'settings' | 'profile';

export interface FormDataState {
  firstName: string;
  lastName: string;
  email: string;
  bio: string;
}

export interface LogEntry {
  timestamp: Date;
  type: 'user' | 'model' | 'tool' | 'system';
  message: string;
}
