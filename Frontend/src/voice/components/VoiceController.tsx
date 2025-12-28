/**
 * Voice Controller Component
 * Main component for Gemini Live voice integration in medical consultations
 */

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { SecureLiveManager } from '../services/secureLiveManager';
import { VoiceName, LogEntry, SessionConfig, ToolCallResult } from '../types';
import { MEDICAL_SYSTEM_INSTRUCTION, SIMPLE_FUNCTIONS, COMPLEX_FUNCTIONS } from '../constants';

interface VoiceControllerProps {
  backendUrl: string;
  sessionConfig: SessionConfig;
  onNavigate?: (section: string) => void;
  onDataUpdate?: (data: any) => void;
}

export const VoiceController: React.FC<VoiceControllerProps> = ({
  backendUrl,
  sessionConfig,
  onNavigate,
  onDataUpdate
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [voiceName, setVoiceName] = useState<VoiceName>(VoiceName.Kore);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const liveManagerRef = useRef<SecureLiveManager | null>(null);

  // Add log entry
  const addLog = useCallback((message: string, type: LogEntry['type']) => {
    setLogs(prev => [...prev, { timestamp: new Date(), message, type }]);
  }, []);

  // Handle tool calls
  const handleToolCall = useCallback(async (name: string, args: any): Promise<ToolCallResult> => {
    try {
      // Determine if this is a simple or complex function
      const isSimple = SIMPLE_FUNCTIONS.includes(name);
      const isComplex = COMPLEX_FUNCTIONS.includes(name);

      if (isSimple) {
        // Simple functions go to direct REST endpoints
        return await handleSimpleToolCall(name, args);
      } else if (isComplex) {
        // Complex functions go through Orchestrator
        return await handleComplexToolCall(name, args);
      } else {
        throw new Error(`Unknown tool: ${name}`);
      }
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Tool execution failed'
      };
    }
  }, [backendUrl, sessionConfig]);

  // Handle simple tool calls (direct REST endpoints)
  const handleSimpleToolCall = async (name: string, args: any): Promise<ToolCallResult> => {
    const authToken = localStorage.getItem('authToken');
    
    switch (name) {
      case 'update_vital_signs':
        const response = await fetch(`${backendUrl}/api/citas/${sessionConfig.appointmentId}/signos-vitales`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
          },
          body: JSON.stringify(args)
        });
        
        if (!response.ok) {
          throw new Error('Failed to update vital signs');
        }
        
        const vitalSignsData = await response.json();
        onDataUpdate?.({ type: 'vital_signs', data: vitalSignsData });
        
        return {
          success: true,
          data: vitalSignsData,
          message: `Signos vitales actualizados correctamente. ${args.peso_kg && args.talla_cm ? `IMC: ${vitalSignsData.imc?.toFixed(1)}` : ''}`
        };

      case 'create_clinical_note':
        const noteResponse = await fetch(`${backendUrl}/api/citas/${sessionConfig.appointmentId}/nota-clinica`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
          },
          body: JSON.stringify(args)
        });
        
        if (!noteResponse.ok) {
          throw new Error('Failed to create clinical note');
        }
        
        const noteData = await noteResponse.json();
        onDataUpdate?.({ type: 'clinical_note', data: noteData });
        
        return {
          success: true,
          data: noteData,
          message: 'Nota clínica actualizada correctamente'
        };

      case 'query_patient_data':
        const queryResponse = await fetch(`${backendUrl}/api/pacientes/${sessionConfig.patientId}/query`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
          },
          body: JSON.stringify(args)
        });
        
        if (!queryResponse.ok) {
          throw new Error('Failed to query patient data');
        }
        
        const queryData = await queryResponse.json();
        
        return {
          success: true,
          data: queryData,
          message: formatPatientDataResponse(args.tipo_consulta, queryData)
        };

      case 'add_allergy':
        const allergyResponse = await fetch(`${backendUrl}/api/pacientes/${sessionConfig.patientId}/alergias`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
          },
          body: JSON.stringify(args)
        });
        
        if (!allergyResponse.ok) {
          throw new Error('Failed to add allergy');
        }
        
        const allergyData = await allergyResponse.json();
        onDataUpdate?.({ type: 'allergy', data: allergyData });
        
        return {
          success: true,
          data: allergyData,
          message: `Alergia a ${args.nombre_alergeno} registrada correctamente`
        };

      case 'navigate_to_section':
        onNavigate?.(args.seccion);
        return {
          success: true,
          message: `Navegando a ${args.seccion}`
        };

      case 'schedule_followup':
        const followupResponse = await fetch(`${backendUrl}/api/seguimientos`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
          },
          body: JSON.stringify({
            id_paciente: sessionConfig.patientId,
            tipo_seguimiento: args.tipo_seguimiento,
            dias_adelante: args.dias_adelante,
            notas: args.notas
          })
        });
        
        if (!followupResponse.ok) {
          throw new Error('Failed to schedule followup');
        }
        
        const followupData = await followupResponse.json();
        
        return {
          success: true,
          data: followupData,
          message: `Seguimiento programado para dentro de ${args.dias_adelante} días`
        };

      default:
        throw new Error(`Unknown simple tool: ${name}`);
    }
  };

  // Handle complex tool calls (through Orchestrator)
  const handleComplexToolCall = async (name: string, args: any): Promise<ToolCallResult> => {
    const authToken = localStorage.getItem('authToken');
    
    const response = await fetch(`${backendUrl}/api/orchestrator/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        function_name: name,
        args: args,
        context: {
          patient_id: sessionConfig.patientId,
          appointment_id: sessionConfig.appointmentId,
          user_id: sessionConfig.userId
        }
      })
    });

    if (!response.ok) {
      throw new Error('Orchestrator execution failed');
    }

    const result = await response.json();
    
    return {
      success: true,
      data: result.data,
      message: result.message || 'Operación completada'
    };
  };

  // Format patient data response for voice output
  const formatPatientDataResponse = (tipo: string, data: any): string => {
    switch (tipo) {
      case 'alergias':
        if (!data || data.length === 0) {
          return 'El paciente no tiene alergias registradas';
        }
        return `El paciente tiene ${data.length} alergia(s): ${data.map((a: any) => a.nombre_alergeno).join(', ')}`;
      
      case 'ultima_cita':
        if (!data) {
          return 'No hay citas previas registradas';
        }
        return `Última cita: ${data.fecha}, motivo: ${data.motivo_consulta}`;
      
      default:
        return 'Información consultada correctamente';
    }
  };

  // Initialize LiveManager
  useEffect(() => {
    liveManagerRef.current = new SecureLiveManager(backendUrl, {
      onLog: addLog,
      onStatusChange: setIsConnected,
      onError: (err) => {
        addLog(`Error: ${err.message}`, "error");
        setIsConnected(false);
      },
      onToolCall: handleToolCall
    });

    return () => {
      liveManagerRef.current?.disconnect();
    };
  }, [backendUrl, addLog, handleToolCall]);

  // Toggle connection
  const toggleConnection = async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    try {
      if (isConnected) {
        await liveManagerRef.current?.disconnect();
      } else {
        await liveManagerRef.current?.connect(
          voiceName,
          MEDICAL_SYSTEM_INSTRUCTION,
          sessionConfig
        );
      }
    } catch (error: any) {
      addLog(`Error: ${error.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="voice-controller">
      <div className="voice-controls">
        <button
          onClick={toggleConnection}
          disabled={isLoading}
          className={`voice-button ${isConnected ? 'connected' : 'disconnected'}`}
        >
          {isLoading ? 'Conectando...' : isConnected ? '🎤 Detener' : '🎤 Iniciar Voz'}
        </button>
        
        <select
          value={voiceName}
          onChange={(e) => setVoiceName(e.target.value as VoiceName)}
          disabled={isConnected}
          className="voice-select"
        >
          {Object.values(VoiceName).map(voice => (
            <option key={voice} value={voice}>{voice}</option>
          ))}
        </select>
      </div>

      <div className="voice-logs">
        <h3>Registro de Voz</h3>
        <div className="logs-container">
          {logs.map((log, idx) => (
            <div key={idx} className={`log-entry log-${log.type}`}>
              <span className="log-time">
                {log.timestamp.toLocaleTimeString()}
              </span>
              <span className="log-message">{log.message}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
