import React from 'react';
import { ZoomIn, ZoomOut, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Save } from 'lucide-react';
import { EditorState } from '../types';

interface EditorControlsProps {
  onZoom: (factor: number) => void;
  onMove: (dx: number, dy: number) => void;
  onSave: () => void;
  state: EditorState;
}

export const EditorControls: React.FC<EditorControlsProps> = ({ onZoom, onMove, onSave, state }) => {
  return (
    <div className="bg-slate-800 p-3 rounded-lg border border-slate-700 space-y-3">
      <div className="flex items-center justify-between text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1">
        <span>Editor Tools</span>
        <span className="text-slate-500">Scale: {Math.round(state.scale * 100)}%</span>
      </div>

      {/* Zoom Controls */}
      <div className="grid grid-cols-2 gap-2">
        <button onClick={() => onZoom(0.9)} className="flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 text-slate-200 py-2 rounded transition-colors text-sm font-medium">
          <ZoomOut size={16} /> 90%
        </button>
        <button onClick={() => onZoom(1.1)} className="flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 text-slate-200 py-2 rounded transition-colors text-sm font-medium">
          <ZoomIn size={16} /> 110%
        </button>
      </div>

      {/* Directional Pad */}
      <div className="flex flex-col items-center gap-1">
        <button onClick={() => onMove(0, -20)} className="w-12 h-8 bg-slate-700 hover:bg-slate-600 rounded flex items-center justify-center transition-colors">
            <ArrowUp size={16} />
        </button>
        <div className="flex gap-1">
            <button onClick={() => onMove(-20, 0)} className="w-12 h-8 bg-slate-700 hover:bg-slate-600 rounded flex items-center justify-center transition-colors">
                <ArrowLeft size={16} />
            </button>
            <button onClick={() => onMove(20, 0)} className="w-12 h-8 bg-slate-700 hover:bg-slate-600 rounded flex items-center justify-center transition-colors">
                <ArrowRight size={16} />
            </button>
        </div>
        <button onClick={() => onMove(0, 20)} className="w-12 h-8 bg-slate-700 hover:bg-slate-600 rounded flex items-center justify-center transition-colors">
            <ArrowDown size={16} />
        </button>
      </div>

      <div className="h-px bg-slate-700 my-2"></div>

      {/* Save Button */}
      <button onClick={onSave} className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white py-2 rounded font-medium shadow-lg shadow-emerald-900/20 transition-all active:scale-95">
        <Save size={16} />
        Save Edited Image
      </button>
    </div>
  );
};