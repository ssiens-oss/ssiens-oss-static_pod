/**
 * Automatic Music Generator - One-click music generation
 *
 * Features:
 * - Instant random generation
 * - Smart presets
 * - Playlist generation
 * - Genre exploration
 */

import React, { useState } from 'react';
import { Sparkles, Zap, List, Shuffle, Music4, Coffee, Dumbbell, Moon, PartyPopper, Gamepad2, Flame, Brain } from 'lucide-react';


interface AutoMusicGeneratorProps {
  onGenerate: (config: any) => void;
}


const SMART_PRESETS = [
  { name: 'morning_motivation', icon: Coffee, label: 'Morning Energy', color: 'bg-orange-500' },
  { name: 'deep_focus', icon: Brain, label: 'Deep Focus', color: 'bg-blue-500' },
  { name: 'workout_energy', icon: Dumbbell, label: 'Workout', color: 'bg-red-500' },
  { name: 'sleep_ambient', icon: Moon, label: 'Sleep', color: 'bg-indigo-500' },
  { name: 'party_vibes', icon: PartyPopper, label: 'Party', color: 'bg-pink-500' },
  { name: 'gaming_intensity', icon: Gamepad2, label: 'Gaming', color: 'bg-purple-500' },
  { name: 'meditation', icon: Flame, label: 'Meditation', color: 'bg-green-500' },
  { name: 'creative_flow', icon: Music4, label: 'Creative Flow', color: 'bg-cyan-500' },
];


const PLAYLIST_MOODS = [
  'energetic', 'chill', 'dark', 'dreamy', 'uplifting',
  'aggressive', 'peaceful', 'mysterious', 'euphoric', 'nostalgic'
];


export function AutoMusicGenerator({ onGenerate }: AutoMusicGeneratorProps) {
  const [activeTab, setActiveTab] = useState<'random' | 'presets' | 'playlist'>('random');
  const [selectedGenre, setSelectedGenre] = useState<string>('');
  const [selectedMood, setSelectedMood] = useState<string>('');
  const [playlistMood, setPlaylistMood] = useState<string>('chill');
  const [playlistCount, setPlaylistCount] = useState<number>(5);
  const [duration, setDuration] = useState<number>(120);
  const [includeLyrics, setIncludeLyrics] = useState<boolean>(false);

  const handleRandomGenerate = () => {
    const config = {
      type: 'auto',
      genre: selectedGenre || undefined,
      mood: selectedMood || undefined,
      duration: duration,
      include_lyrics: includeLyrics
    };
    onGenerate(config);
  };

  const handlePresetGenerate = (presetName: string) => {
    const config = {
      type: 'preset',
      preset: presetName
    };
    onGenerate(config);
  };

  const handlePlaylistGenerate = () => {
    const config = {
      type: 'playlist',
      mood: playlistMood,
      count: playlistCount,
      duration_per_song: duration
    };
    onGenerate(config);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 pb-4 border-b border-slate-800">
        <div className="p-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg">
          <Sparkles size={20} className="text-white" />
        </div>
        <div>
          <h2 className="font-bold text-slate-100">Automatic Music Generator</h2>
          <p className="text-xs text-slate-400">One-click song creation with AI</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 p-1 bg-slate-900 rounded-lg">
        <button
          onClick={() => setActiveTab('random')}
          className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'random'
              ? 'bg-purple-600 text-white'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Shuffle size={16} />
          Random Song
        </button>

        <button
          onClick={() => setActiveTab('presets')}
          className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'presets'
              ? 'bg-purple-600 text-white'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Zap size={16} />
          Quick Presets
        </button>

        <button
          onClick={() => setActiveTab('playlist')}
          className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'playlist'
              ? 'bg-purple-600 text-white'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <List size={16} />
          Playlist
        </button>
      </div>

      {/* Random Tab */}
      {activeTab === 'random' && (
        <div className="space-y-4">
          <div className="p-6 bg-gradient-to-br from-purple-900/20 to-pink-900/20 border border-purple-500/30 rounded-xl">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles size={20} className="text-purple-400" />
              <h3 className="font-bold text-white">Generate Random Song</h3>
            </div>
            <p className="text-sm text-slate-400 mb-6">
              Let AI create a completely unique song for you. Optionally customize genre, mood, and duration.
            </p>

            {/* Options */}
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <span className="text-xs text-slate-400 mb-1 block">Genre (Optional)</span>
                  <select
                    value={selectedGenre}
                    onChange={(e) => setSelectedGenre(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-purple-500"
                  >
                    <option value="">Any Genre</option>
                    <option value="synthwave">Synthwave</option>
                    <option value="techno">Techno</option>
                    <option value="house">House</option>
                    <option value="lofi">Lo-Fi</option>
                    <option value="ambient">Ambient</option>
                    <option value="trap">Trap</option>
                    <option value="dubstep">Dubstep</option>
                    <option value="drum_and_bass">Drum & Bass</option>
                  </select>
                </div>

                <div>
                  <span className="text-xs text-slate-400 mb-1 block">Mood (Optional)</span>
                  <select
                    value={selectedMood}
                    onChange={(e) => setSelectedMood(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-purple-500"
                  >
                    <option value="">Any Mood</option>
                    <option value="energetic">Energetic</option>
                    <option value="chill">Chill</option>
                    <option value="dark">Dark</option>
                    <option value="dreamy">Dreamy</option>
                    <option value="uplifting">Uplifting</option>
                    <option value="aggressive">Aggressive</option>
                  </select>
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-xs text-slate-400">Duration</span>
                  <span className="text-xs text-purple-400">{duration}s</span>
                </div>
                <input
                  type="range"
                  min="30"
                  max="300"
                  value={duration}
                  onChange={(e) => setDuration(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeLyrics}
                  onChange={(e) => setIncludeLyrics(e.target.checked)}
                  className="w-4 h-4 bg-slate-800 border border-slate-700 rounded"
                />
                Generate AI lyrics (requires Claude API)
              </label>

              <button
                onClick={handleRandomGenerate}
                className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-semibold rounded-lg transition-all shadow-lg"
              >
                <Shuffle size={18} />
                Generate Random Song
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Presets Tab */}
      {activeTab === 'presets' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            {SMART_PRESETS.map((preset) => {
              const Icon = preset.icon;
              return (
                <button
                  key={preset.name}
                  onClick={() => handlePresetGenerate(preset.name)}
                  className="p-4 bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-purple-500/50 rounded-xl transition-all group"
                >
                  <div className={`w-12 h-12 ${preset.color} rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                    <Icon size={24} className="text-white" />
                  </div>
                  <div className="text-left">
                    <div className="font-semibold text-slate-200 mb-1">{preset.label}</div>
                    <div className="text-xs text-slate-400">Click to generate</div>
                  </div>
                </button>
              );
            })}
          </div>

          <div className="p-4 bg-slate-900/50 border border-slate-800 rounded-lg">
            <p className="text-xs text-slate-400">
              💡 <span className="font-semibold">Tip:</span> Smart presets are AI-optimized for specific activities and moods.
              Each preset generates a unique song tailored to the use case.
            </p>
          </div>
        </div>
      )}

      {/* Playlist Tab */}
      {activeTab === 'playlist' && (
        <div className="space-y-4">
          <div className="p-6 bg-gradient-to-br from-blue-900/20 to-purple-900/20 border border-blue-500/30 rounded-xl">
            <div className="flex items-center gap-2 mb-4">
              <List size={20} className="text-blue-400" />
              <h3 className="font-bold text-white">Generate Playlist</h3>
            </div>
            <p className="text-sm text-slate-400 mb-6">
              Create a cohesive playlist of multiple songs with a unified mood.
            </p>

            <div className="space-y-4">
              <div>
                <span className="text-xs text-slate-400 mb-1 block">Playlist Mood</span>
                <select
                  value={playlistMood}
                  onChange={(e) => setPlaylistMood(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                >
                  {PLAYLIST_MOODS.map(mood => (
                    <option key={mood} value={mood}>{mood}</option>
                  ))}
                </select>
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-xs text-slate-400">Number of Songs</span>
                  <span className="text-xs text-blue-400">{playlistCount} tracks</span>
                </div>
                <input
                  type="range"
                  min="3"
                  max="20"
                  value={playlistCount}
                  onChange={(e) => setPlaylistCount(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-xs text-slate-400">Duration per Song</span>
                  <span className="text-xs text-blue-400">{duration}s</span>
                </div>
                <input
                  type="range"
                  min="60"
                  max="300"
                  value={duration}
                  onChange={(e) => setDuration(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              <div className="p-3 bg-slate-800/50 rounded-lg">
                <div className="text-xs text-slate-400">
                  <strong className="text-slate-300">Estimated:</strong> {playlistCount} songs × {duration}s ={' '}
                  <span className="text-blue-400">{Math.floor((playlistCount * duration) / 60)} minutes</span> of music
                </div>
              </div>

              <button
                onClick={handlePlaylistGenerate}
                className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-semibold rounded-lg transition-all shadow-lg"
              >
                <List size={18} />
                Generate {playlistCount}-Track Playlist
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Info Banner */}
      <div className="p-4 bg-gradient-to-r from-purple-900/30 to-pink-900/30 border border-purple-500/30 rounded-lg">
        <div className="flex items-start gap-3">
          <Sparkles size={20} className="text-purple-400 mt-0.5 flex-shrink-0" />
          <div className="text-xs text-slate-300">
            <strong className="text-purple-400">AI-Powered:</strong> All songs are generated with complete song structure
            (intro, verse, chorus, bridge, outro), genre-specific vibes, and professional mixing.
            No two songs are ever the same!
          </div>
        </div>
      </div>
    </div>
  );
}
