import React from 'react';
import { EngineConfig } from '../types';

interface ConfigurationFormProps {
  config: EngineConfig;
  onChange: (config: EngineConfig) => void;
  disabled?: boolean;
}

export function ConfigurationForm({ config, onChange, disabled = false }: ConfigurationFormProps) {
  return (
    <div className="space-y-4">
      <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
        Configuration
      </label>

      <div className="space-y-3">
        <div>
          <span className="text-xs text-slate-400 mb-1 block">Drop Name</span>
          <input
            type="text"
            value={config.dropName}
            onChange={e => onChange({ ...config, dropName: e.target.value })}
            disabled={disabled}
            className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        <div className="grid grid-cols-3 gap-2">
          <div>
            <span className="text-xs text-slate-400 mb-1 block">Count</span>
            <input
              type="number"
              value={config.designCount}
              onChange={e => onChange({ ...config, designCount: parseInt(e.target.value) || 0 })}
              disabled={disabled}
              className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-2 text-sm focus:outline-none focus:border-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>
          <div>
            <span className="text-xs text-slate-400 mb-1 block">Blueprint</span>
            <input
              type="number"
              value={config.blueprintId}
              onChange={e => onChange({ ...config, blueprintId: parseInt(e.target.value) || 0 })}
              disabled={disabled}
              className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-2 text-sm focus:outline-none focus:border-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>
          <div>
            <span className="text-xs text-slate-400 mb-1 block">Provider</span>
            <input
              type="number"
              value={config.providerId}
              onChange={e => onChange({ ...config, providerId: parseInt(e.target.value) || 0 })}
              disabled={disabled}
              className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-2 text-sm focus:outline-none focus:border-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>
        </div>

        <div>
          <span className="text-xs text-slate-400 mb-1 block">Batch List (Comma separated)</span>
          <input
            type="text"
            placeholder="Drop1, Drop2, Drop3"
            value={config.batchList}
            onChange={e => onChange({ ...config, batchList: e.target.value })}
            disabled={disabled}
            className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>
      </div>
    </div>
  );
}
