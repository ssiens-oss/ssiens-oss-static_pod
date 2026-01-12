import React from 'react';

interface ProgressBarProps {
  progress: number;
  label?: string;
}

export function ProgressBar({ progress, label = 'Global Progress' }: ProgressBarProps) {
  return (
    <div className="p-4 bg-slate-900 border-t border-slate-800">
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>{label}</span>
        <span>{Math.round(progress)}%</span>
      </div>
      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-indigo-500 transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
    </div>
  );
}
