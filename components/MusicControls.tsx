/**
 * MusicControls - User interface for music generation
 *
 * Features:
 * - Vibe sliders (energy, dark, dreamy, aggressive)
 * - Genre mixing
 * - Instrument selection
 * - BPM and key controls
 */

import React from 'react';
import { Music, Sliders } from 'lucide-react';


interface MusicSpec {
  bpm: number;
  key: string;
  duration: number;
  vibe: {
    energy: number;
    dark: number;
    dreamy: number;
    aggressive: number;
  };
  genre_mix: {
    synthwave: number;
    lofi: number;
    techno: number;
  };
  instruments: {
    bass: string;
    lead: string;
    pad: string;
    drums: string;
  };
  stems: boolean;
}


interface MusicControlsProps {
  spec: MusicSpec;
  onChange: (spec: MusicSpec) => void;
}


const INSTRUMENT_PRESETS = {
  bass: ['analog_mono', 'sub_bass', 'fm_bass', 'reese'],
  lead: ['supersaw', 'pluck', 'fm_bell', 'acid'],
  pad: ['granular_pad', 'string_pad', 'warm_pad', 'dark_pad'],
  drums: ['808', '909', 'acoustic', 'industrial']
};


const KEYS = [
  'C major', 'C minor',
  'D major', 'D minor',
  'E major', 'E minor',
  'F major', 'F minor',
  'G major', 'G minor',
  'A major', 'A minor',
  'B major', 'B minor'
];


export function MusicControls({ spec, onChange }: MusicControlsProps) {
  const updateVibe = (key: string, value: number) => {
    onChange({
      ...spec,
      vibe: { ...spec.vibe, [key]: value }
    });
  };

  const updateGenre = (genre: string, value: number) => {
    onChange({
      ...spec,
      genre_mix: { ...spec.genre_mix, [genre]: value }
    });
  };

  const updateInstrument = (type: string, preset: string) => {
    onChange({
      ...spec,
      instruments: { ...spec.instruments, [type]: preset }
    });
  };

  const updateField = (field: string, value: any) => {
    onChange({ ...spec, [field]: value });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 pb-4 border-b border-slate-800">
        <div className="p-2 bg-purple-600 rounded-lg">
          <Music size={20} className="text-white" />
        </div>
        <div>
          <h2 className="font-bold text-slate-100">AI Music Generator</h2>
          <p className="text-xs text-slate-400">Create user-generated music</p>
        </div>
      </div>

      {/* Basic Settings */}
      <div className="space-y-4">
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Basic Settings
        </label>

        <div className="grid grid-cols-3 gap-3">
          <div>
            <span className="text-xs text-slate-400 mb-1 block">BPM</span>
            <input
              type="number"
              min="60"
              max="180"
              value={spec.bpm}
              onChange={(e) => updateField('bpm', parseInt(e.target.value))}
              className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-2 text-sm focus:outline-none focus:border-purple-500"
            />
          </div>

          <div className="col-span-2">
            <span className="text-xs text-slate-400 mb-1 block">Key</span>
            <select
              value={spec.key}
              onChange={(e) => updateField('key', e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-2 text-sm focus:outline-none focus:border-purple-500"
            >
              {KEYS.map(key => (
                <option key={key} value={key}>{key}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <span className="text-xs text-slate-400 mb-1 block">Duration (seconds)</span>
          <input
            type="range"
            min="5"
            max="120"
            value={spec.duration}
            onChange={(e) => updateField('duration', parseInt(e.target.value))}
            className="w-full"
          />
          <div className="text-xs text-purple-400 mt-1">{spec.duration}s</div>
        </div>
      </div>

      {/* Vibe Controls */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Sliders size={16} className="text-purple-400" />
          <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Vibe Controls
          </label>
        </div>

        {Object.entries(spec.vibe).map(([key, value]) => (
          <div key={key}>
            <div className="flex justify-between mb-1">
              <span className="text-xs text-slate-400 capitalize">{key}</span>
              <span className="text-xs text-purple-400">{Math.round(value * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={value}
              onChange={(e) => updateVibe(key, parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer
                [&::-webkit-slider-thumb]:appearance-none
                [&::-webkit-slider-thumb]:w-4
                [&::-webkit-slider-thumb]:h-4
                [&::-webkit-slider-thumb]:rounded-full
                [&::-webkit-slider-thumb]:bg-purple-500
                [&::-webkit-slider-thumb]:cursor-pointer"
            />
          </div>
        ))}
      </div>

      {/* Genre Mix */}
      <div className="space-y-3">
        <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Genre Mix
        </label>

        {Object.entries(spec.genre_mix).map(([genre, value]) => (
          <div key={genre}>
            <div className="flex justify-between mb-1">
              <span className="text-xs text-slate-400 capitalize">{genre}</span>
              <span className="text-xs text-purple-400">{Math.round(value * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={value}
              onChange={(e) => updateGenre(genre, parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer
                [&::-webkit-slider-thumb]:appearance-none
                [&::-webkit-slider-thumb]:w-4
                [&::-webkit-slider-thumb]:h-4
                [&::-webkit-slider-thumb]:rounded-full
                [&::-webkit-slider-thumb]:bg-purple-500"
            />
          </div>
        ))}
      </div>

      {/* Instruments */}
      <div className="space-y-3">
        <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Instruments
        </label>

        {Object.entries(spec.instruments).map(([type, preset]) => (
          <div key={type}>
            <span className="text-xs text-slate-400 mb-1 block capitalize">{type}</span>
            <select
              value={preset}
              onChange={(e) => updateInstrument(type, e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-purple-500"
            >
              {INSTRUMENT_PRESETS[type as keyof typeof INSTRUMENT_PRESETS].map(p => (
                <option key={p} value={p}>{p.replace(/_/g, ' ')}</option>
              ))}
            </select>
          </div>
        ))}
      </div>

      {/* Export Options */}
      <div className="space-y-2">
        <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Export Options
        </label>

        <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
          <input
            type="checkbox"
            checked={spec.stems}
            onChange={(e) => updateField('stems', e.target.checked)}
            className="w-4 h-4 bg-slate-800 border border-slate-700 rounded focus:ring-purple-500"
          />
          Export individual stems (+2 credits)
        </label>
      </div>
    </div>
  );
}
