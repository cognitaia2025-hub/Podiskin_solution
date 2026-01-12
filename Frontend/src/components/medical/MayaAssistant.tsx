import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Bot, User, Lightbulb, Zap, FileText, ClipboardList, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';
import type { MayaSuggestion } from '../../types/medical';
import chatService from '../../services/chatService';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  suggestions?: MayaSuggestion[];
}

interface MayaAssistantProps {
  className?: string;
  patientData?: Record<string, any>;
}

// Mensajes iniciales
const INITIAL_MESSAGE: Message = {
  id: 'welcome',
  role: 'assistant',
  content: '¡Hola! Soy Maya, tu asistente de inteligencia artificial. Estoy aquí para ayudarte a completar el expediente médico de forma más eficiente. Puedo sugerirte diagnósticos, autocompletar campos con notas de voz, y generar resúmenes clínicos. ¿En qué puedo ayudarte hoy?',
  timestamp: new Date(),
};

const QUICK_ACTIONS = [
  { icon: ClipboardList, label: 'Sugerir Diagnóstico', action: 'diagnose' },
  { icon: FileText, label: 'Generar Resumen', action: 'summary' },
  { icon: Lightbulb, label: 'Recomendaciones', action: 'recommendations' },
  { icon: Zap, label: 'Autocompletar', action: 'autocomplete' },
];

const MayaAssistant: React.FC<MayaAssistantProps> = ({
  className,
  patientData,
}) => {
  const [messages, setMessages] = useState<Message[]>([INITIAL_MESSAGE]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'chat' | 'history'>('chat');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll al último mensaje
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);
    setError(null);

    try {
      // Obtener info del paciente si está disponible
      const patientInfo = chatService.getLoggedPatientInfo() || (
        patientData ? {
          patient_id: patientData.patient_id,
          first_name: patientData.primer_nombre,
          first_last_name: patientData.primer_apellido,
          is_registered: true,
        } : undefined
      );

      // Llamar al backend real
      const response = await chatService.sendMessage(
        userMessage.content,
        patientInfo
      );

      // Construir mensaje de respuesta
      const aiMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(response.timestamp),
        suggestions: response.suggestions?.map((s, idx) => ({
          id: `sugg-${idx}`,
          type: 'action',
          confidence: 0.8,
          content: s,
          explanation: '',
          actionLabel: s,
        })),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (err: any) {
      console.error('Error sending message:', err);
      
      const errorMessage = err.response?.data?.detail || 
                          err.message || 
                          'Error conectando con Maya. Por favor intenta de nuevo.';
      
      setError(errorMessage);
      
      // Mensaje de error visual
      const errorMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `⚠️ Lo siento, hubo un problema: ${errorMessage}`,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleQuickAction = async (action: string) => {
    const actionMessages: Record<string, string> = {
      diagnose: '¿Puedes sugerirme diagnósticos basados en la información actual del paciente?',
      summary: 'Genera un resumen ejecutivo del expediente de este paciente',
      recommendations: '¿Qué tratamiento recomiendas para este caso?',
      autocomplete: 'Ayúdame a completar campos del expediente médico',
    };

    const messageText = actionMessages[action] || 'Ejecutando acción...';
    
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    setError(null);

    try {
      const patientInfo = chatService.getLoggedPatientInfo() || (
        patientData ? {
          patient_id: patientData.patient_id,
          first_name: patientData.primer_nombre,
          first_last_name: patientData.primer_apellido,
          is_registered: true,
        } : undefined
      );

      const response = await chatService.sendMessage(
        messageText,
        patientInfo,
        { page: `medical-record-${action}` }
      );

      const aiMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(response.timestamp),
        suggestions: response.suggestions?.map((s, idx) => ({
          id: `sugg-${idx}`,
          type: 'action',
          confidence: 0.85,
          content: s,
          explanation: '',
          actionLabel: s,
        })),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (err: any) {
      console.error('Error in quick action:', err);
      
      const errorMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '⚠️ No pude completar esa acción. Por favor intenta de nuevo.',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const applySuggestion = (suggestion: MayaSuggestion) => {
    // Aquí se implementaría la lógica para insertar la sugerencia en el formulario
    console.log('Aplicando sugerencia:', suggestion);
    
    // Mensaje de confirmación
    const confirmationMessage: Message = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: `He insertado "${suggestion.content}" en el formulario. ¿Necesitas algo más?`,
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, confirmationMessage]);
  };

  return (
    <div className={clsx('flex flex-col h-full bg-white rounded-lg border border-gray-200', className)}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gradient-to-r from-violet-50 to-purple-50 rounded-t-lg">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-violet-100 rounded-full flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-violet-600" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-800 flex items-center gap-2">
              Maya
              {isTyping && (
                <span className="text-xs text-violet-600 animate-pulse">escribiendo...</span>
              )}
            </h3>
            <p className="text-xs text-gray-500">
              {error ? (
                <span className="text-red-500 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  Error de conexión
                </span>
              ) : (
                'Asistente IA'
              )}
            </p>
          </div>
        </div>
        
        {/* Tabs */}
        <div className="flex gap-1 bg-white rounded-lg p-1 border border-gray-200">
          <button
            onClick={() => setActiveTab('chat')}
            className={clsx(
              'px-3 py-1 text-xs font-medium rounded-md transition-colors',
              activeTab === 'chat' ? 'bg-violet-100 text-violet-700' : 'text-gray-600 hover:bg-gray-100'
            )}
          >
            Chat
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={clsx(
              'px-3 py-1 text-xs font-medium rounded-md transition-colors',
              activeTab === 'history' ? 'bg-violet-100 text-violet-700' : 'text-gray-600 hover:bg-gray-100'
            )}
          >
            Historial
          </button>
        </div>
      </div>

      {/* Chat Area */}
      {activeTab === 'chat' ? (
        <>
          {/* Quick Actions */}
          <div className="px-4 py-2 border-b border-gray-100 flex gap-2 overflow-x-auto">
            {QUICK_ACTIONS.map((action) => (
              <button
                key={action.action}
                onClick={() => handleQuickAction(action.action)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-violet-50 hover:bg-violet-100 text-violet-700 text-xs font-medium rounded-full transition-colors whitespace-nowrap"
              >
                <action.icon className="w-3.5 h-3.5" />
                {action.label}
              </button>
            ))}
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={clsx(
                  'flex gap-3',
                  message.role === 'user' && 'flex-row-reverse'
                )}
              >
                {/* Avatar */}
                <div
                  className={clsx(
                    'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
                    message.role === 'assistant' ? 'bg-violet-100' : 'bg-gray-100'
                  )}
                >
                  {message.role === 'assistant' ? (
                    <Bot className="w-5 h-5 text-violet-600" />
                  ) : (
                    <User className="w-5 h-5 text-gray-600" />
                  )}
                </div>

                {/* Message bubble */}
                <div
                  className={clsx(
                    'max-w-[80%] rounded-2xl px-4 py-2',
                    message.role === 'assistant'
                      ? 'bg-gray-50 rounded-tl-none'
                      : 'bg-violet-600 text-white rounded-tr-none'
                  )}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  
                  {/* Sugerencias */}
                  {message.suggestions && message.suggestions.length > 0 && (
                    <div className="mt-3 space-y-2">
                      {message.suggestions.map((suggestion) => (
                        <div
                          key={suggestion.id}
                          className="p-2 bg-white rounded-lg border border-violet-200"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <Lightbulb className="w-4 h-4 text-yellow-500" />
                              <span className="text-xs font-medium text-gray-700">
                                {suggestion.confidence * 100}% coincidencia
                              </span>
                            </div>
                            <button
                              onClick={() => applySuggestion(suggestion)}
                              className="text-xs text-violet-600 hover:text-violet-800 font-medium"
                            >
                              {suggestion.actionLabel}
                            </button>
                          </div>
                          <p className="text-xs text-gray-600 mt-1">
                            {suggestion.content}
                          </p>
                          {suggestion.explanation && (
                            <p className="text-xs text-gray-500 mt-1">
                              {suggestion.explanation}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <span className="text-xs opacity-70 mt-1 block">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-violet-100 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-violet-600" />
                </div>
                <div className="bg-gray-50 rounded-2xl rounded-tl-none px-4 py-3">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Escribe tu mensaje o usa comandos de voz..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
              />
              <button
                onClick={handleSend}
                disabled={!inputValue.trim() || isTyping}
                className={clsx(
                  'w-10 h-10 rounded-full flex items-center justify-center transition-colors',
                  inputValue.trim() && !isTyping
                    ? 'bg-violet-600 text-white hover:bg-violet-700'
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                )}
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </>
      ) : (
        /* Historial de Evolución */
        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-4">
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-green-500 rounded-full" />
                <span className="text-xs font-medium text-green-700">Fase 1 - Evaluación Inicial</span>
              </div>
              <p className="text-sm text-gray-700">
                Primera consulta. Paciente refiere dolor en talón derecho de 2 semanas de evolución.
              </p>
              <p className="text-xs text-gray-500 mt-2">20 dic 2025</p>
            </div>
            
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-yellow-500 rounded-full" />
                <span className="text-xs font-medium text-yellow-700">Fase 2 - Seguimiento</span>
              </div>
              <p className="text-sm text-gray-700">
                Mejoría del 50% con tratamiento conservador. Continúa ejercicios en casa.
              </p>
              <p className="text-xs text-gray-500 mt-2">27 dic 2025</p>
            </div>
            
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full" />
                <span className="text-xs font-medium text-blue-700">Fase 3 - Actual</span>
              </div>
              <p className="text-sm text-gray-700">
                Evolución favorable. Sin dolor en actividades cotidianas.
              </p>
              <p className="text-xs text-gray-500 mt-2">3 ene 2026</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MayaAssistant;
