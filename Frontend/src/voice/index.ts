/**
 * Voice Module - Main Exports
 * Sistema de Voz Gemini Live para Podoskin Solution
 */

// Components
export { VoiceController } from './components/VoiceController';

// Services
export { SecureLiveManager } from './services/secureLiveManager';
export { SecureSessionService } from './services/secureSession';

// Types
export * from './types';

// Constants
export {
  MEDICAL_SYSTEM_INSTRUCTION,
  MEDICAL_TOOLS,
  SIMPLE_FUNCTIONS,
  COMPLEX_FUNCTIONS,
  UPDATE_VITAL_SIGNS,
  CREATE_CLINICAL_NOTE,
  QUERY_PATIENT_DATA,
  SEARCH_PATIENT_HISTORY,
  ADD_ALLERGY,
  GENERATE_SUMMARY,
  NAVIGATE_TO_SECTION,
  SCHEDULE_FOLLOWUP
} from './constants';

// Audio Utilities
export {
  resampleTo16k,
  floatTo16BitPCMBase64,
  decodeAudioData,
  createSilentGainNode,
  resumeAudioContext,
  supportsAudioWorklet
} from './services/audioUtils';
