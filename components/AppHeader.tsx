import React from 'react';
import { Layers } from 'lucide-react';
import { ConnectionStatus } from './ConnectionStatus';
import { ComfyUIService } from '../services/comfyui';

interface AppHeaderProps {
  comfyService: ComfyUIService | null;
}

export function AppHeader({ comfyService }: AppHeaderProps) {
  return (
    <div className="p-4 border-b border-slate-800">
      <div className="flex items-center gap-3 mb-3">
        <div className="p-2 bg-indigo-600 rounded-lg shadow-lg shadow-indigo-500/20">
          <Layers className="text-white" size={24} />
        </div>
        <div>
          <h1 className="font-bold text-slate-100 leading-tight">StaticWaves</h1>
          <p className="text-xs text-indigo-400 font-mono">POD STUDIO v6.0</p>
        </div>
      </div>
      <ConnectionStatus comfyService={comfyService} />
    </div>
  );
}
