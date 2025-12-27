import React, { useEffect, useRef } from 'react';
import { LogEntry } from '../types';

interface LoggerProps {
  logs: LogEntry[];
}

export const Logger: React.FC<LoggerProps> = ({ logs }) => {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="bg-black/50 rounded-xl p-4 border border-slate-800 h-64 flex flex-col font-mono text-xs overflow-hidden">
      <div className="text-slate-400 font-semibold mb-2 border-b border-slate-800 pb-2">Live Logs & Tool Activity</div>
      <div className="overflow-y-auto flex-1 space-y-2 pr-2 custom-scrollbar">
        {logs.length === 0 && (
            <div className="text-slate-600 italic text-center mt-10">Waiting for connection...</div>
        )}
        {logs.map((log, i) => (
          <div key={i} className="flex gap-2">
            <span className="text-slate-500 whitespace-nowrap">
              [{log.timestamp.toLocaleTimeString([], { hour12: false, second: '2-digit', minute: '2-digit' })}]
            </span>
            <span className={`${
              log.type === 'tool' ? 'text-emerald-400' :
              log.type === 'system' ? 'text-amber-400' :
              log.type === 'model' ? 'text-indigo-300' :
              'text-slate-300'
            }`}>
              {log.type === 'tool' && '🔧 '}
              {log.message}
            </span>
          </div>
        ))}
        <div ref={endRef} />
      </div>
    </div>
  );
};