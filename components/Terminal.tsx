import React, { useEffect, useRef } from 'react';
import { LogEntry, LogType } from '../types';
import { Terminal as TerminalIcon, Trash2, Download } from 'lucide-react';

interface TerminalProps {
  logs: LogEntry[];
  onClear: () => void;
  onExport?: () => void;
}

export const Terminal: React.FC<TerminalProps> = ({ logs, onClear, onExport }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const getColor = (type: LogType) => {
    switch (type) {
      case LogType.SUCCESS: return 'text-green-400';
      case LogType.ERROR: return 'text-red-400';
      case LogType.WARNING: return 'text-yellow-400';
      default: return 'text-slate-300';
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-700 rounded-lg overflow-hidden shadow-inner">
      <div className="flex items-center justify-between px-3 py-2 bg-slate-800 border-b border-slate-700">
        <div className="flex items-center gap-2 text-xs font-mono text-slate-400 uppercase tracking-wider">
          <TerminalIcon size={14} />
          <span>System Output</span>
        </div>
        <div className="flex items-center gap-2">
          {onExport && logs.length > 0 && (
            <button
              onClick={onExport}
              className="text-slate-500 hover:text-indigo-400 transition-colors"
              title="Export Logs as CSV"
            >
              <Download size={14} />
            </button>
          )}
          <button
            onClick={onClear}
            className="text-slate-500 hover:text-red-400 transition-colors"
            title="Clear Logs"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>
      <div className="flex-1 p-3 overflow-y-auto font-mono text-xs terminal-scroll space-y-1">
        {logs.length === 0 && (
            <div className="text-slate-600 italic">Ready for input...</div>
        )}
        {logs.map((log) => (
          <div key={log.id} className="flex gap-2">
            <span className="text-slate-600 shrink-0">[{log.timestamp}]</span>
            <span className={`${getColor(log.type)} break-all`}>{log.message}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};