import React from 'react';
import { VoiceName } from '../types';

interface VoiceControlsProps {
  selectedVoice: VoiceName;
  onVoiceChange: (voice: VoiceName) => void;
  systemInstruction: string;
  onSystemInstructionChange: (instruction: string) => void;
  disabled: boolean;
}

export const VoiceControls: React.FC<VoiceControlsProps> = ({
  selectedVoice,
  onVoiceChange,
  systemInstruction,
  onSystemInstructionChange,
  disabled
}) => {
  return (
    <div className="bg-slate-900 rounded-xl p-6 border border-slate-800 shadow-sm">
      <h2 className="text-lg font-semibold mb-4 text-white flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        Voice Configuration
      </h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-400 mb-1">Voice Selection</label>
          <select
            value={selectedVoice}
            onChange={(e) => onVoiceChange(e.target.value as VoiceName)}
            disabled={disabled}
            className="w-full bg-slate-800 border-slate-700 text-white rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 transition-colors"
          >
            {Object.values(VoiceName).map((voice) => (
              <option key={voice} value={voice}>{voice}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-400 mb-1">System Instructions (Prompt)</label>
          <textarea
            value={systemInstruction}
            onChange={(e) => onSystemInstructionChange(e.target.value)}
            disabled={disabled}
            rows={4}
            className="w-full bg-slate-800 border-slate-700 text-white rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 transition-colors text-sm font-mono leading-relaxed"
            placeholder="Describe how the AI should behave..."
          />
        </div>
      </div>
    </div>
  );
};