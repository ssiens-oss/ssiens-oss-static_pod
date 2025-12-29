import React, { useState } from 'react';
import { Settings as SettingsIcon, X, Save, RefreshCw } from 'lucide-react';

export interface AppSettings {
  apiBaseUrl: string;
  apiKey: string;
  autoSave: boolean;
  theme: 'dark' | 'light';
  animationsEnabled: boolean;
  simulationSpeed: number;
  maxQueueSize: number;
}

interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
  settings: AppSettings;
  onSave: (settings: AppSettings) => void;
}

export const Settings: React.FC<SettingsProps> = ({ isOpen, onClose, settings, onSave }) => {
  const [localSettings, setLocalSettings] = useState<AppSettings>(settings);

  if (!isOpen) return null;

  const handleSave = () => {
    onSave(localSettings);
    onClose();
  };

  const handleReset = () => {
    setLocalSettings(settings);
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fadeIn">
      <div className="bg-slate-900 border-2 border-slate-700 rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">

        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-600 rounded-lg">
              <SettingsIcon size={20} className="text-white" />
            </div>
            <h2 className="text-xl font-bold text-slate-100">Application Settings</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors text-slate-400 hover:text-slate-200"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">

          {/* API Configuration */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">API Configuration</h3>

            <div>
              <label className="block text-sm text-slate-300 mb-2">API Base URL</label>
              <input
                type="text"
                value={localSettings.apiBaseUrl}
                onChange={(e) => setLocalSettings({ ...localSettings, apiBaseUrl: e.target.value })}
                placeholder="http://localhost:3001/api"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-sm text-slate-300 mb-2">API Key</label>
              <input
                type="password"
                value={localSettings.apiKey}
                onChange={(e) => setLocalSettings({ ...localSettings, apiKey: e.target.value })}
                placeholder="Enter your API key"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
          </div>

          {/* Application Preferences */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Preferences</h3>

            <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-700">
              <div>
                <p className="text-sm font-medium text-slate-200">Auto-save edits</p>
                <p className="text-xs text-slate-500 mt-0.5">Automatically save image edits to local storage</p>
              </div>
              <label className="relative inline-block w-12 h-6">
                <input
                  type="checkbox"
                  checked={localSettings.autoSave}
                  onChange={(e) => setLocalSettings({ ...localSettings, autoSave: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-12 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-6 peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-700">
              <div>
                <p className="text-sm font-medium text-slate-200">Enable animations</p>
                <p className="text-xs text-slate-500 mt-0.5">Show smooth transitions and animations</p>
              </div>
              <label className="relative inline-block w-12 h-6">
                <input
                  type="checkbox"
                  checked={localSettings.animationsEnabled}
                  onChange={(e) => setLocalSettings({ ...localSettings, animationsEnabled: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-12 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-6 peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>

            <div>
              <label className="block text-sm text-slate-300 mb-2">
                Simulation Speed (ms delay)
              </label>
              <input
                type="range"
                min="100"
                max="2000"
                step="100"
                value={localSettings.simulationSpeed}
                onChange={(e) => setLocalSettings({ ...localSettings, simulationSpeed: parseInt(e.target.value) })}
                className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
              <div className="flex justify-between text-xs text-slate-500 mt-1">
                <span>Fast (100ms)</span>
                <span className="text-indigo-400 font-semibold">{localSettings.simulationSpeed}ms</span>
                <span>Slow (2000ms)</span>
              </div>
            </div>

            <div>
              <label className="block text-sm text-slate-300 mb-2">
                Max Queue Size
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={localSettings.maxQueueSize}
                onChange={(e) => setLocalSettings({ ...localSettings, maxQueueSize: parseInt(e.target.value) })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
          </div>

          {/* Theme (Future feature) */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Appearance</h3>

            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setLocalSettings({ ...localSettings, theme: 'dark' })}
                className={`p-4 rounded-lg border-2 transition-all ${
                  localSettings.theme === 'dark'
                    ? 'border-indigo-500 bg-indigo-500/10'
                    : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
                }`}
              >
                <div className="text-sm font-medium text-slate-200">Dark</div>
                <div className="text-xs text-slate-500 mt-1">Default theme</div>
              </button>
              <button
                onClick={() => setLocalSettings({ ...localSettings, theme: 'light' })}
                className={`p-4 rounded-lg border-2 transition-all ${
                  localSettings.theme === 'light'
                    ? 'border-indigo-500 bg-indigo-500/10'
                    : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
                }`}
              >
                <div className="text-sm font-medium text-slate-200">Light</div>
                <div className="text-xs text-slate-500 mt-1">Coming soon</div>
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-slate-700 bg-slate-900/50">
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-400 hover:text-slate-200 transition-colors"
          >
            <RefreshCw size={16} />
            Reset
          </button>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-400 hover:text-slate-200 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="flex items-center gap-2 px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium shadow-lg shadow-indigo-900/20 transition-all"
            >
              <Save size={16} />
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export const DEFAULT_SETTINGS: AppSettings = {
  apiBaseUrl: '/api',
  apiKey: '',
  autoSave: true,
  theme: 'dark',
  animationsEnabled: true,
  simulationSpeed: 400,
  maxQueueSize: 50,
};
