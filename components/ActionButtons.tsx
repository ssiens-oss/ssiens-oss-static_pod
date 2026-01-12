import React from 'react';
import { Play, Rocket, Loader2 } from 'lucide-react';

interface ActionButtonsProps {
  isRunning: boolean;
  onRunSingle: () => void;
  onRunBatch: () => void;
}

export function ActionButtons({ isRunning, onRunSingle, onRunBatch }: ActionButtonsProps) {
  return (
    <div className="grid grid-cols-1 gap-3">
      <button
        onClick={onRunSingle}
        disabled={isRunning}
        className={`flex items-center justify-center gap-2 py-3 rounded-lg font-semibold shadow-lg transition-all ${
          isRunning
            ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
            : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-900/20'
        }`}
      >
        {isRunning ? <Loader2 className="animate-spin" size={18} /> : <Play size={18} />}
        Run Single Drop
      </button>
      <button
        onClick={onRunBatch}
        disabled={isRunning}
        className={`flex items-center justify-center gap-2 py-3 rounded-lg font-semibold shadow-lg transition-all border border-slate-700 ${
          isRunning
            ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
            : 'bg-slate-800 hover:bg-slate-700 text-indigo-300'
        }`}
      >
        <Rocket size={18} />
        Run Batch Mode
      </button>
    </div>
  );
}
