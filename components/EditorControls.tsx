import React from 'react';
import { ZoomIn, ZoomOut, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Save, RotateCw, RotateCcw, RefreshCw, Download } from 'lucide-react';
import { EditorState } from '../types';

interface EditorControlsProps {
  onZoom: (factor: number) => void;
  onMove: (dx: number, dy: number) => void;
  onRotate: (degrees: number) => void;
  onReset: () => void;
  onSave: () => void;
  onDownload: () => void;
  state: EditorState;
}

export const EditorControls: React.FC<EditorControlsProps> = ({ onZoom, onMove, onRotate, onReset, onSave, onDownload, state }) => {
  return (
    <div className="bg-slate-800 p-3 rounded-lg border border-slate-700 space-y-3">
      <div className="flex items-center justify-between text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1">
        <span>Editor Tools</span>
        <span className="text-slate-500">{Math.round(state.scale * 100)}%</span>
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

      {/* Rotation Controls */}
      <div className="grid grid-cols-2 gap-2">
        <button onClick={() => onRotate(-15)} className="flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 text-slate-200 py-2 rounded transition-colors text-sm font-medium">
          <RotateCcw size={16} /> -15°
        </button>
        <button onClick={() => onRotate(15)} className="flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 text-slate-200 py-2 rounded transition-colors text-sm font-medium">
          <RotateCw size={16} /> +15°
        </button>
      </div>
      <div className="text-xs text-center text-slate-500">
        Rotation: {state.rotation}°
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

      {/* Reset Button */}
      <button onClick={onReset} className="w-full flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 text-slate-300 py-2 rounded font-medium transition-all">
        <RefreshCw size={16} />
        Reset Transform
      </button>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-2">
        <button onClick={onSave} className="flex items-center justify-center gap-1 bg-emerald-600 hover:bg-emerald-500 text-white py-2 rounded font-medium shadow-lg shadow-emerald-900/20 transition-all active:scale-95 text-sm">
          <Save size={14} />
          Save
        </button>
        <button onClick={onDownload} className="flex items-center justify-center gap-1 bg-blue-600 hover:bg-blue-500 text-white py-2 rounded font-medium shadow-lg shadow-blue-900/20 transition-all active:scale-95 text-sm">
          <Download size={14} />
          Export
        </button>
      </div>
    </div>
  );
};
