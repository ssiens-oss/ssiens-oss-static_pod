import React from 'react';
import { ImageIcon, Layers, Box } from 'lucide-react';
import { EditorControls } from './EditorControls';
import { EditorState } from '../types';

interface PreviewPanelProps {
  designImage: string | null;
  mockupImage: string | null;
  editorState: EditorState;
  onZoom: (factor: number) => void;
  onMove: (dx: number, dy: number) => void;
  onSave: () => void;
}

export function PreviewPanel({
  designImage,
  mockupImage,
  editorState,
  onZoom,
  onMove,
  onSave
}: PreviewPanelProps) {
  return (
    <div className="flex-1 p-6 overflow-y-auto">
      <div className="flex items-center gap-2 mb-4">
        <ImageIcon size={20} className="text-indigo-400" />
        <h2 className="text-lg font-bold">Live Preview + Editor</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[500px]">
        {/* Design Preview (Editable) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          <div className="bg-slate-900 border-2 border-slate-800 rounded-xl flex items-center justify-center h-full relative overflow-hidden group">
            <div className="absolute top-3 left-3 bg-black/60 backdrop-blur px-2 py-1 rounded text-xs font-mono text-white z-10">
              RAW DESIGN
            </div>
            {designImage ? (
              <div className="w-[350px] h-[350px] border border-dashed border-slate-700 overflow-hidden relative bg-[#1a1a1a]">
                <img
                  src={designImage}
                  alt="Design Preview"
                  className="w-full h-full object-contain transition-transform duration-75 ease-linear"
                  style={{
                    transform: `scale(${editorState.scale}) translate(${editorState.translateX}px, ${editorState.translateY}px)`
                  }}
                />
              </div>
            ) : (
              <div className="text-slate-600 flex flex-col items-center">
                <Layers size={48} className="mb-2 opacity-20" />
                <span className="text-sm">Waiting for generation...</span>
              </div>
            )}
          </div>
        </div>

        {/* Mockup Preview (Static) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          <div className="bg-slate-900 border-2 border-slate-800 rounded-xl flex items-center justify-center h-full relative overflow-hidden">
            <div className="absolute top-3 left-3 bg-black/60 backdrop-blur px-2 py-1 rounded text-xs font-mono text-white z-10">
              PRODUCT MOCKUP
            </div>
            {mockupImage ? (
              <img
                src={mockupImage}
                alt="Mockup"
                className="max-w-[80%] max-h-[80%] object-contain shadow-2xl"
              />
            ) : (
              <div className="text-slate-600 flex flex-col items-center">
                <Box size={48} className="mb-2 opacity-20" />
                <span className="text-sm">Waiting for mockup...</span>
              </div>
            )}
          </div>
        </div>

        {/* Editor Tools Column */}
        <div className="lg:col-span-2 flex flex-col justify-center">
          <EditorControls onZoom={onZoom} onMove={onMove} onSave={onSave} state={editorState} />
        </div>
      </div>
    </div>
  );
}
