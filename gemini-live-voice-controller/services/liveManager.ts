import { GoogleGenAI, LiveServerMessage, Modality } from "@google/genai";
import { TOOLS } from "../constants";
import { VoiceName } from "../types";
import { createPcmBlob, decodeAudioData, base64ToUint8Array } from "./audioUtils";

interface LiveManagerCallbacks {
  onLog: (message: string, type: 'user' | 'model' | 'tool' | 'system') => void;
  onToolCall: (name: string, args: any) => Promise<any>;
  onStatusChange: (isConnected: boolean) => void;
  onError: (error: Error) => void;
}

export class LiveManager {
  private ai: GoogleGenAI;
  private inputAudioContext: AudioContext | null = null;
  private outputAudioContext: AudioContext | null = null;
  private nextStartTime = 0;
  private sources = new Set<AudioBufferSourceNode>();
  private sessionPromise: Promise<any> | null = null;
  private callbacks: LiveManagerCallbacks;
  private active = false;

  constructor(apiKey: string, callbacks: LiveManagerCallbacks) {
    this.ai = new GoogleGenAI({ apiKey });
    this.callbacks = callbacks;
  }

  public async connect(voiceName: VoiceName, systemInstruction: string) {
    if (this.active) return;

    try {
      this.callbacks.onLog("Initializing audio contexts...", "system");
      
      this.inputAudioContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
      this.outputAudioContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      this.callbacks.onLog("Connecting to Gemini Live API...", "system");

      this.sessionPromise = this.ai.live.connect({
        model: 'gemini-2.5-flash-native-audio-preview-09-2025',
        config: {
          responseModalities: [Modality.AUDIO],
          speechConfig: {
            voiceConfig: { prebuiltVoiceConfig: { voiceName } },
          },
          systemInstruction: systemInstruction,
          tools: [{ functionDeclarations: TOOLS }],
        },
        callbacks: {
          onopen: () => {
            this.callbacks.onStatusChange(true);
            this.callbacks.onLog("Connection established.", "system");
            this.startAudioInput(stream);
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

  private startAudioInput(stream: MediaStream) {
    if (!this.inputAudioContext) return;

    const source = this.inputAudioContext.createMediaStreamSource(stream);
    // Use ScriptProcessor for raw PCM access (standard for this API usage example)
    const scriptProcessor = this.inputAudioContext.createScriptProcessor(4096, 1, 1);
    
    scriptProcessor.onaudioprocess = (e) => {
      if (!this.active) return;
      const inputData = e.inputBuffer.getChannelData(0);
      const pcmBlob = createPcmBlob(inputData);
      
      this.sessionPromise?.then((session) => {
        session.sendRealtimeInput({ media: pcmBlob });
      });
    };

    source.connect(scriptProcessor);
    scriptProcessor.connect(this.inputAudioContext.destination);
  }

  private async handleMessage(message: LiveServerMessage) {
    // 1. Handle Audio Output
    const base64Audio = message.serverContent?.modelTurn?.parts?.[0]?.inlineData?.data;
    if (base64Audio && this.outputAudioContext) {
      try {
        this.nextStartTime = Math.max(this.nextStartTime, this.outputAudioContext.currentTime);
        const audioBuffer = await decodeAudioData(
            base64ToUint8Array(base64Audio),
            this.outputAudioContext
        );
        
        const source = this.outputAudioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(this.outputAudioContext.destination);
        source.addEventListener('ended', () => this.sources.delete(source));
        source.start(this.nextStartTime);
        this.sources.add(source);
        
        this.nextStartTime += audioBuffer.duration;
      } catch (e) {
        console.error("Error decoding audio", e);
      }
    }

    // 2. Handle Interruption
    if (message.serverContent?.interrupted) {
      this.callbacks.onLog("Model interrupted by user.", "system");
      this.sources.forEach(source => source.stop());
      this.sources.clear();
      this.nextStartTime = 0;
    }

    // 3. Handle Tool Calling (Function Calls)
    if (message.toolCall) {
      this.callbacks.onLog(`Received tool call(s): ${message.toolCall.functionCalls.length}`, "system");
      
      for (const fc of message.toolCall.functionCalls) {
        this.callbacks.onLog(`Executing tool: ${fc.name}`, "tool");
        
        try {
          const result = await this.callbacks.onToolCall(fc.name, fc.args);
          
          this.sessionPromise?.then((session) => {
            session.sendToolResponse({
              functionResponses: {
                id: fc.id,
                name: fc.name,
                response: { result: result }
              }
            });
          });
          this.callbacks.onLog(`Tool ${fc.name} completed successfully.`, "tool");
        } catch (error) {
           this.callbacks.onLog(`Tool ${fc.name} failed: ${error}`, "system");
           // Ideally send error back to model, but we'll just log locally for now
        }
      }
    }
  }

  public disconnect() {
    this.active = false;
    this.sessionPromise?.then(session => session.close());
    this.sessionPromise = null;

    if (this.inputAudioContext) {
      this.inputAudioContext.close();
      this.inputAudioContext = null;
    }
    if (this.outputAudioContext) {
      this.outputAudioContext.close();
      this.outputAudioContext = null;
    }
    this.sources.clear();
    this.callbacks.onStatusChange(false);
  }
}