/**
 * Secure Live Manager for Gemini Live API
 * Uses backend for API key management and secure sessions
 */

import { GoogleGenAI, LiveServerMessage, Modality } from "@google/genai";
import { MEDICAL_TOOLS } from "../constants";
import { VoiceName, VoiceManagerCallbacks, SessionConfig } from "../types";
import { 
  resampleTo16k, 
  floatTo16BitPCMBase64, 
  decodeAudioData,
  createSilentGainNode,
  resumeAudioContext 
} from "./audioUtils";
import { SecureSessionService } from "./secureSession";

export class SecureLiveManager {
  private inputAudioContext: AudioContext | null = null;
  private outputAudioContext: AudioContext | null = null;
  private nextStartTime = 0;
  private sources = new Set<AudioBufferSourceNode>();
  private sessionPromise: Promise<any> | null = null;
  private callbacks: VoiceManagerCallbacks;
  private active = false;
  private scriptProcessor: ScriptProcessorNode | null = null;
  private mediaStream: MediaStream | null = null;
  private sessionService: SecureSessionService;
  private geminiApiKey: string | null = null;

  constructor(backendUrl: string, callbacks: VoiceManagerCallbacks) {
    this.callbacks = callbacks;
    this.sessionService = new SecureSessionService(backendUrl);
  }

  /**
   * Connect to Gemini Live with secure session
   */
  public async connect(
    voiceName: VoiceName, 
    systemInstruction: string,
    sessionConfig: SessionConfig
  ): Promise<void> {
    if (this.active) return;

    try {
      this.callbacks.onLog("Starting secure session...", "system");
      
      // Get secure session token from backend
      const sessionToken = await this.sessionService.startSession(sessionConfig);
      this.callbacks.onLog("Secure session created", "system");

      // Initialize audio contexts
      this.callbacks.onLog("Initializing audio contexts...", "system");
      
      this.inputAudioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      this.outputAudioContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
      
      // Resume contexts (required after user interaction)
      await resumeAudioContext(this.inputAudioContext);
      await resumeAudioContext(this.outputAudioContext);

      // Get microphone access
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });
      
      this.callbacks.onLog("Connecting to Gemini Live API...", "system");

      // For demo purposes, we still need the API key client-side for Gemini Live
      // In production, consider using a proxy or Gemini's session token API when available
      this.geminiApiKey = await this.fetchApiKeyFromBackend();
      
      const ai = new GoogleGenAI({ apiKey: this.geminiApiKey });

      this.sessionPromise = ai.live.connect({
        model: 'gemini-2.0-flash-exp',
        config: {
          responseModalities: [Modality.AUDIO],
          speechConfig: {
            voiceConfig: { prebuiltVoiceConfig: { voiceName } },
          },
          systemInstruction: systemInstruction,
          tools: [{ functionDeclarations: MEDICAL_TOOLS }],
        },
        callbacks: {
          onopen: () => {
            this.callbacks.onStatusChange(true);
            this.callbacks.onLog("Connection established.", "system");
            this.startAudioInput();
          },
          onmessage: (message: LiveServerMessage) => this.handleMessage(message),
          onclose: () => {
            this.callbacks.onStatusChange(false);
            this.callbacks.onLog("Connection closed.", "system");
            this.disconnect();
          },
          onerror: (e) => {
            this.callbacks.onError(new Error("Live API Error"));
            this.disconnect();
          }
        }
      });

      this.active = true;

    } catch (err: any) {
      this.callbacks.onError(err);
      this.disconnect();
    }
  }

  /**
   * Fetch API key from backend (temporary - until Gemini supports server-side sessions)
   */
  private async fetchApiKeyFromBackend(): Promise<string> {
    // In production, backend should provide session credentials
    // For now, this is a placeholder
    const token = this.sessionService.getCurrentToken();
    if (!token) {
      throw new Error("No active session");
    }
    
    // This endpoint should return a temporary/scoped API key
    const response = await fetch(`/api/live/session/${token.sessionId}/credentials`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        'X-Session-Token': token.token
      }
    });
    
    if (!response.ok) {
      throw new Error("Failed to get session credentials");
    }
    
    const data = await response.json();
    return data.apiKey;
  }

  /**
   * Start audio input with proper resampling
   */
  private startAudioInput(): void {
    if (!this.inputAudioContext || !this.mediaStream) return;

    const source = this.inputAudioContext.createMediaStreamSource(this.mediaStream);
    
    // Use ScriptProcessor for audio capture (will be replaced by AudioWorklet in future)
    this.scriptProcessor = this.inputAudioContext.createScriptProcessor(4096, 1, 1);
    
    // Create silent gain node to prevent feedback
    const silentGain = createSilentGainNode(this.inputAudioContext);
    
    this.scriptProcessor.onaudioprocess = async (e) => {
      if (!this.active) return;
      
      try {
        const inputData = e.inputBuffer.getChannelData(0);
        
        // Create audio buffer for resampling
        const buffer = this.inputAudioContext!.createBuffer(
          1, 
          inputData.length, 
          this.inputAudioContext!.sampleRate
        );
        buffer.copyToChannel(inputData, 0);
        
        // Resample to 16kHz
        const resampled = await resampleTo16k(buffer);
        
        // Convert to PCM16 base64
        const pcmBlob = floatTo16BitPCMBase64(resampled);
        
        // Send to Gemini Live
        this.sessionPromise?.then((session) => {
          session.sendRealtimeInput({ media: pcmBlob });
        }).catch(err => {
          console.error('Error sending audio:', err);
        });
      } catch (error) {
        console.error('Error processing audio:', error);
      }
    };

    // Connect through silent gain to prevent feedback
    source.connect(this.scriptProcessor);
    this.scriptProcessor.connect(silentGain);
    silentGain.connect(this.inputAudioContext.destination);
  }

  /**
   * Handle incoming messages from Gemini Live
   */
  private async handleMessage(message: LiveServerMessage): Promise<void> {
    try {
      // Handle audio output
      if (message.serverContent?.modelTurn?.parts) {
        for (const part of message.serverContent.modelTurn.parts) {
          if (part.inlineData?.mimeType?.startsWith('audio/pcm')) {
            await this.playAudio(part.inlineData.data);
          }
          if (part.text) {
            this.callbacks.onLog(part.text, 'model');
          }
        }
      }

      // Handle tool calls
      if (message.toolCall) {
        await this.handleToolCall(message.toolCall);
      }

      // Handle tool call cancellation
      if (message.toolCallCancellation) {
        this.callbacks.onLog(`Tool call cancelled: ${message.toolCallCancellation.ids.join(', ')}`, 'system');
      }

    } catch (error) {
      console.error('Error handling message:', error);
      this.callbacks.onError(error as Error);
    }
  }

  /**
   * Handle tool calls
   */
  private async handleToolCall(toolCall: any): Promise<void> {
    const functionCalls = toolCall.functionCalls || [];
    
    for (const fc of functionCalls) {
      try {
        this.callbacks.onLog(`Tool call: ${fc.name}(${JSON.stringify(fc.args)})`, 'tool');
        
        // Execute tool through callback
        const result = await this.callbacks.onToolCall(fc.name, fc.args);
        
        // Send function response back to Gemini
        const session = await this.sessionPromise;
        if (session) {
          await session.send({
            toolResponse: {
              functionResponses: [{
                id: fc.id,
                name: fc.name,
                response: result
              }]
            }
          });
        }
        
        this.callbacks.onLog(`Tool result: ${JSON.stringify(result)}`, 'tool');
        
      } catch (error: any) {
        console.error(`Error executing tool ${fc.name}:`, error);
        
        // Send error response
        const session = await this.sessionPromise;
        if (session) {
          await session.send({
            toolResponse: {
              functionResponses: [{
                id: fc.id,
                name: fc.name,
                response: { 
                  success: false, 
                  error: error.message || 'Tool execution failed' 
                }
              }]
            }
          });
        }
      }
    }
  }

  /**
   * Play audio output
   */
  private async playAudio(base64Data: string): Promise<void> {
    if (!this.outputAudioContext) return;

    try {
      const audioBuffer = await decodeAudioData(this.outputAudioContext, base64Data, 24000);
      
      const source = this.outputAudioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(this.outputAudioContext.destination);
      
      // Schedule playback
      const startTime = Math.max(this.outputAudioContext.currentTime, this.nextStartTime);
      source.start(startTime);
      this.nextStartTime = startTime + audioBuffer.duration;
      
      // Track source for cleanup
      this.sources.add(source);
      source.onended = () => {
        this.sources.delete(source);
      };
      
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  }

  /**
   * Disconnect and cleanup
   */
  public async disconnect(): Promise<void> {
    this.active = false;

    // Stop all audio sources
    this.sources.forEach(source => {
      try {
        source.stop();
      } catch (e) {
        // Source may already be stopped
      }
    });
    this.sources.clear();

    // Disconnect audio processing
    if (this.scriptProcessor) {
      this.scriptProcessor.disconnect();
      this.scriptProcessor = null;
    }

    // Stop media stream
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }

    // Close audio contexts
    if (this.inputAudioContext) {
      await this.inputAudioContext.close();
      this.inputAudioContext = null;
    }
    if (this.outputAudioContext) {
      await this.outputAudioContext.close();
      this.outputAudioContext = null;
    }

    // Close Gemini session
    if (this.sessionPromise) {
      try {
        const session = await this.sessionPromise;
        if (session && session.close) {
          session.close();
        }
      } catch (e) {
        // Session may already be closed
      }
      this.sessionPromise = null;
    }

    // Stop secure session
    await this.sessionService.stopSession();

    this.nextStartTime = 0;
    this.callbacks.onStatusChange(false);
  }

  /**
   * Check if currently connected
   */
  public isConnected(): boolean {
    return this.active;
  }
}
