import React, { useState, useCallback, useEffect, useRef } from 'react';
import { VoiceControls } from './components/VoiceControls';
import { DemoApp } from './components/DemoApp';
import { Logger } from './components/Logger';
import { LiveManager } from './services/liveManager';
import { VoiceName, AppSection, FormDataState, LogEntry } from './types';
import { DEFAULT_SYSTEM_INSTRUCTION, DEFAULT_VOICE } from './constants';

const App: React.FC = () => {
  // App State
  const [activeSection, setActiveSection] = useState<AppSection>('dashboard');
  const [formData, setFormData] = useState<FormDataState>({
    firstName: 'Jane',
    lastName: 'Doe',
    email: 'jane.doe@example.com',
    bio: 'Software Engineer based in SF.'
  });

  // Voice & API State
  const [isConnected, setIsConnected] = useState(false);
  const [voiceName, setVoiceName] = useState<VoiceName>(DEFAULT_VOICE);
  const [systemInstruction, setSystemInstruction] = useState(DEFAULT_SYSTEM_INSTRUCTION);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  
  const liveManagerRef = useRef<LiveManager | null>(null);

  // Helper to add logs
  const addLog = useCallback((message: string, type: LogEntry['type']) => {
    setLogs(prev => [...prev, { timestamp: new Date(), message, type }]);
  }, []);

  // Tool Implementation: Change Tab
  const handleNavigate = useCallback((args: any) => {
    const section = args.section;
    if (['dashboard', 'settings', 'profile'].includes(section)) {
      setActiveSection(section as AppSection);
      return `Navigated to ${section}.`;
    }
    return `Failed to navigate. Unknown section: ${section}`;
  }, []);

  // Tool Implementation: Fill Form
  const handleFillForm = useCallback((args: any) => {
    const { fieldName, value } = args;
    if (fieldName in formData) {
      setFormData(prev => ({ ...prev, [fieldName]: value }));
      return `Updated field ${fieldName} to "${value}".`;
    }
    return `Failed to update. Unknown field: ${fieldName}`;
  }, [formData]);

  // Setup LiveManager
  useEffect(() => {
    const apiKey = process.env.API_KEY || "";
    if (!apiKey) {
      addLog("API_KEY not found in environment variables.", "system");
    }

    liveManagerRef.current = new LiveManager(apiKey, {
      onLog: addLog,
      onStatusChange: setIsConnected,
      onError: (err) => {
        addLog(`Error: ${err.message}`, "system");
        setIsConnected(false);
      },
      onToolCall: async (name, args) => {
        if (name === 'navigate_to_section') {
          return handleNavigate(args);
        } else if (name === 'fill_form_field') {
          return handleFillForm(args);
        }
        throw new Error(`Unknown tool: ${name}`);
      }
    });

    return () => {
      liveManagerRef.current?.disconnect();
    };
  }, [addLog, handleNavigate, handleFillForm]);

  const toggleConnection = async () => {
    if (isConnected) {
      liveManagerRef.current?.disconnect();
    } else {
      await liveManagerRef.current?.connect(voiceName, systemInstruction);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 p-4 md:p-8 flex items-center justify-center">
      <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Panel: Control & Logs */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          <header className="mb-2">
            <h1 className="text-3xl font-bold text-white tracking-tight">Gemini <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">Live</span></h1>
            <p className="text-slate-400 mt-1">Conversational Voice Integration Kit</p>
          </header>

          <VoiceControls 
            selectedVoice={voiceName}
            onVoiceChange={setVoiceName}
            systemInstruction={systemInstruction}
            onSystemInstructionChange={setSystemInstruction}
            disabled={isConnected}
          />

          <button
            onClick={toggleConnection}
            className={`w-full py-4 rounded-xl font-bold text-lg shadow-lg transition-all transform hover:scale-[1.02] active:scale-100 flex items-center justify-center gap-3 ${
              isConnected 
                ? 'bg-red-500 hover:bg-red-600 text-white shadow-red-500/20' 
                : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-500/20'
            }`}
          >
            {isConnected ? (
              <>
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
                </span>
                End Conversation
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
                Start Live Session
              </>
            )}
          </button>

          <Logger logs={logs} />
          
          <div className="text-xs text-slate-500 text-center">
            *Requires Microphone Permission. Gemini 2.5 Flash Native Audio Model.
          </div>
        </div>

        {/* Right Panel: The Demo App */}
        <div className="lg:col-span-7 h-[600px] lg:h-auto relative group">
           <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-cyan-500 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-1000"></div>
           <div className="relative h-full">
            <DemoApp 
              currentSection={activeSection}
              formData={formData}
              onSectionChange={setActiveSection}
              onFormChange={(field, value) => setFormData(prev => ({ ...prev, [field]: value }))}
            />
            
            {!isConnected && (
              <div className="absolute inset-0 bg-white/5 backdrop-blur-[1px] flex items-center justify-center rounded-xl pointer-events-none z-10">
                 <div className="bg-slate-900/80 backdrop-blur-md text-white px-6 py-3 rounded-full border border-slate-700 shadow-2xl flex items-center gap-3">
                    <span className="text-2xl">🎙️</span>
                    <div>
                      <div className="font-bold text-sm">Voice Control Ready</div>
                      <div className="text-xs text-slate-300">Click "Start Live Session" to interact</div>
                    </div>
                 </div>
              </div>
            )}
           </div>
        </div>

      </div>
    </div>
  );
};

export default App;