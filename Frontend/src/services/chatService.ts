/**
 * Chat Service - Integración con Maya (Agente IA)
 * Conecta el componente MayaAssistant con el backend web_chat_api
 */

import api from './api';

// ============================================================================
// TIPOS
// ============================================================================

export interface PatientInfo {
  patient_id?: string;
  first_name?: string;
  first_last_name?: string;
  is_registered?: boolean;
  partial_id?: string;
}

export interface UserContext {
  page: string;
  previous_messages: number;
  user_agent: string;
}

export interface ChatMessage {
  message: string;
  session_id: string;
  timestamp: string;
  patient_info?: PatientInfo;
  user_context?: UserContext;
}

export interface ChatAction {
  type: string; // schedule_appointment, call, whatsapp, redirect
  label: string;
  data: Record<string, any>;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  timestamp: string;
  patient_id?: string;
  actions?: ChatAction[];
  suggestions?: string[];
}

export interface ConversationHistory {
  conversation_id: string;
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }>;
  patient_info?: PatientInfo;
  created_at: string;
  last_activity: string;
}

// ============================================================================
// SERVICIO DE CHAT
// ============================================================================

class ChatService {
  private sessionId: string | null = null;

  /**
   * Obtener o generar session_id
   */
  getSessionId(): string {
    if (!this.sessionId) {
      // Buscar en localStorage
      const stored = localStorage.getItem('maya_session_id');
      if (stored) {
        this.sessionId = stored;
      } else {
        // Generar nuevo UUID v4
        this.sessionId = crypto.randomUUID();
        localStorage.setItem('maya_session_id', this.sessionId);
      }
    }
    return this.sessionId;
  }

  /**
   * Resetear sesión (útil para logout o nueva conversación)
   */
  resetSession(): void {
    this.sessionId = crypto.randomUUID();
    localStorage.setItem('maya_session_id', this.sessionId);
  }

  /**
   * Enviar mensaje a Maya
   */
  async sendMessage(
    message: string,
    patientInfo?: PatientInfo,
    userContext?: Partial<UserContext>
  ): Promise<ChatResponse> {
    const sessionId = this.getSessionId();
    
    const payload: ChatMessage = {
      message: message.trim(),
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      patient_info: patientInfo,
      user_context: {
        page: window.location.pathname,
        previous_messages: this.getMessageCount(),
        user_agent: navigator.userAgent,
        ...userContext,
      },
    };

    const response = await api.post<ChatResponse>('/chatbot/message', payload, {
      headers: {
        'X-Session-ID': sessionId,
        'X-Client-Type': 'web',
      },
    });

    // Incrementar contador de mensajes
    this.incrementMessageCount();

    return response.data;
  }

  /**
   * Obtener historial de conversación
   */
  async getHistory(limit: number = 50): Promise<ConversationHistory> {
    const sessionId = this.getSessionId();
    
    const response = await api.get<ConversationHistory>('/chatbot/history', {
      params: {
        session_id: sessionId,
        limit,
      },
    });

    return response.data;
  }

  /**
   * Registrar nuevo paciente desde el chat
   */
  async registerPatient(data: {
    first_name: string;
    second_name?: string;
    first_last_name: string;
    second_last_name?: string;
    birth_date: string;
  }): Promise<{
    success: boolean;
    patient_id: string;
    message: string;
  }> {
    const response = await api.post('/chatbot/register-patient', data);
    return response.data;
  }

  /**
   * Buscar paciente existente
   */
  async lookupPatient(query: {
    patient_id?: string;
    first_name?: string;
    first_last_name?: string;
    birth_date?: string;
  }): Promise<{
    found: boolean;
    patient_id?: string;
    first_name?: string;
    first_last_name?: string;
    registration_date?: string;
  }> {
    const response = await api.post('/chatbot/lookup-patient', query);
    return response.data;
  }

  /**
   * Obtener contexto del paciente actual
   */
  async getPatientContext(patientId: string): Promise<{
    patient: any;
    last_appointment?: any;
    pending_appointment?: any;
    medical_history_summary?: string;
  }> {
    const response = await api.get(`/chatbot/patient-context/${patientId}`);
    return response.data;
  }

  // ============================================================================
  // HELPERS PRIVADOS
  // ============================================================================

  private getMessageCount(): number {
    const count = localStorage.getItem('maya_message_count');
    return count ? parseInt(count, 10) : 0;
  }

  private incrementMessageCount(): void {
    const count = this.getMessageCount();
    localStorage.setItem('maya_message_count', (count + 1).toString());
  }

  /**
   * Obtener info del paciente logueado (si existe)
   */
  getLoggedPatientInfo(): PatientInfo | undefined {
    try {
      const userStr = localStorage.getItem('user');
      if (!userStr) return undefined;

      const user = JSON.parse(userStr);
      
      // Verificar si es paciente
      if (user.role === 'patient' || user.patient_id) {
        return {
          patient_id: user.patient_id,
          first_name: user.primer_nombre || user.first_name,
          first_last_name: user.primer_apellido || user.last_name,
          is_registered: true,
        };
      }
    } catch (error) {
      console.error('Error parsing user data:', error);
    }
    return undefined;
  }
}

// Exportar instancia singleton
export const chatService = new ChatService();
export default chatService;
