/**
 * Music Studio - Complete GUI for AI Music Generation
 *
 * Features:
 * - Tab-based interface (Auto, Manual, Library)
 * - Real-time generation status
 * - Audio player with waveform
 * - Download management
 */

import React, { useState, useEffect } from 'react';
import { Music, Sliders, Library, Sparkles, Download, Play, Pause, Loader2 } from 'lucide-react';
import { AutoMusicGenerator } from './AutoMusicGenerator';
import { MusicControls } from './MusicControls';
import { MusicPlayer } from './MusicPlayer';
import { generateAndWait, getJobStatus, getDownloadUrl } from '../services/musicAPI';


interface GeneratedTrack {
  jobId: string;
  title: string;
  genre?: string;
  mood?: string;
  duration: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  audioUrl?: string;
  stems?: string[];
  timestamp: Date;
}


export function MusicStudio() {
  const [activeTab, setActiveTab] = useState<'auto' | 'manual' | 'library'>('auto');
  const [tracks, setTracks] = useState<GeneratedTrack[]>([]);
  const [currentTrack, setCurrentTrack] = useState<GeneratedTrack | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // Manual mode state
  const [manualSpec, setManualSpec] = useState({
    bpm: 120,
    key: 'C minor',
    duration: 30,
    vibe: {
      energy: 0.5,
      dark: 0.3,
      dreamy: 0.4,
      aggressive: 0.2
    },
    genre_mix: {
      synthwave: 0.6,
      lofi: 0.3,
      techno: 0.1
    },
    instruments: {
      bass: 'analog_mono',
      lead: 'supersaw',
      pad: 'granular_pad',
      drums: '808'
    },
    stems: true
  });

  // Poll for status updates
  useEffect(() => {
    const interval = setInterval(async () => {
      const pendingTracks = tracks.filter(t => t.status === 'pending' || t.status === 'running');

      for (const track of pendingTracks) {
        try {
          const status = await getJobStatus(track.jobId);

          if (status.status !== track.status) {
            setTracks(prev => prev.map(t =>
              t.jobId === track.jobId
                ? {
                    ...t,
                    status: status.status as any,
                    progress: status.progress,
                    audioUrl: status.status === 'completed' ? getDownloadUrl(track.jobId, 'mix') : undefined,
                    stems: status.status === 'completed' && status.output_urls
                      ? Object.keys(status.output_urls).filter(k => k !== 'mix')
                      : []
                  }
                : t
            ));
          }
        } catch (error) {
          console.error('Error polling status:', error);
        }
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [tracks]);

  const handleAutoGenerate = async (config: any) => {
    setIsGenerating(true);

    try {
      let endpoint = '/generate/auto';
      let params: any = {};

      if (config.type === 'preset') {
        endpoint = `/generate/preset/${config.preset}`;
      } else if (config.type === 'playlist') {
        endpoint = '/generate/playlist';
        params = {
          mood: config.mood,
          count: config.count,
          duration_per_song: config.duration_per_song
        };
      } else {
        // Auto generation
        params = {
          genre: config.genre,
          mood: config.mood,
          duration: config.duration,
          include_lyrics: config.include_lyrics
        };
      }

      // Call API
      const apiUrl = import.meta.env.VITE_MUSIC_API_URL || 'http://localhost:8000';
      const url = new URL(endpoint, apiUrl);
      Object.keys(params).forEach(key => {
        if (params[key] !== undefined) {
          url.searchParams.append(key, params[key]);
        }
      });

      const response = await fetch(url.toString(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        throw new Error('Generation failed');
      }

      const result = await response.json();

      // Handle playlist (multiple jobs)
      if (result.job_ids) {
        const newTracks = result.job_ids.map((jobId: string, index: number) => ({
          jobId,
          title: `${result.mood} Playlist - Track ${index + 1}`,
          mood: result.mood,
          duration: params.duration_per_song || 120,
          status: 'pending' as const,
          progress: 0,
          timestamp: new Date()
        }));
        setTracks(prev => [...newTracks, ...prev]);
      } else {
        // Single track
        const newTrack: GeneratedTrack = {
          jobId: result.job_id,
          title: result.song_info?.title || result.preset || 'Generated Track',
          genre: result.song_info?.genre,
          mood: result.song_info?.mood,
          duration: result.song_info?.duration || 120,
          status: 'pending',
          progress: 0,
          timestamp: new Date()
        };
        setTracks(prev => [newTrack, ...prev]);
      }
    } catch (error) {
      console.error('Generation error:', error);
      alert('Failed to generate music. Please check that the API is running.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleManualGenerate = async () => {
    setIsGenerating(true);

    try {
      const { jobId, audioUrl, stems } = await generateAndWait(
        manualSpec,
        (progress) => {
          // Update progress
          setTracks(prev => prev.map(t =>
            t.jobId === jobId ? { ...t, progress } : t
          ));
        }
      );

      const newTrack: GeneratedTrack = {
        jobId,
        title: 'Custom Track',
        duration: manualSpec.duration,
        status: 'completed',
        progress: 100,
        audioUrl,
        stems,
        timestamp: new Date()
      };

      setTracks(prev => [newTrack, ...prev]);
      setCurrentTrack(newTrack);
    } catch (error) {
      console.error('Generation error:', error);
      alert('Failed to generate music');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200">
      {/* Left Sidebar - Controls */}
      <div className="w-96 flex flex-col border-r border-slate-800 bg-slate-900/50">
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center gap-3">
          <div className="p-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg shadow-lg shadow-purple-500/20">
            <Music className="text-white" size={24} />
          </div>
          <div>
            <h1 className="font-bold text-slate-100 leading-tight">Music Studio</h1>
            <p className="text-xs text-purple-400 font-mono">AI GENERATION v2.0</p>
          </div>
        </div>

        {/* Mode Tabs */}
        <div className="flex gap-1 p-2 bg-slate-900 border-b border-slate-800">
          <button
            onClick={() => setActiveTab('auto')}
            className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'auto'
                ? 'bg-purple-600 text-white shadow-lg'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            <Sparkles size={16} />
            Auto
          </button>

          <button
            onClick={() => setActiveTab('manual')}
            className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'manual'
                ? 'bg-purple-600 text-white shadow-lg'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            <Sliders size={16} />
            Manual
          </button>

          <button
            onClick={() => setActiveTab('library')}
            className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'library'
                ? 'bg-purple-600 text-white shadow-lg'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            <Library size={16} />
            Library
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-4 scrollbar-hide">
          {activeTab === 'auto' && (
            <AutoMusicGenerator onGenerate={handleAutoGenerate} />
          )}

          {activeTab === 'manual' && (
            <div className="space-y-4">
              <MusicControls spec={manualSpec} onChange={setManualSpec} />

              <button
                onClick={handleManualGenerate}
                disabled={isGenerating}
                className={`w-full flex items-center justify-center gap-2 py-3 rounded-lg font-semibold shadow-lg transition-all ${
                  isGenerating
                    ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white'
                }`}
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="animate-spin" size={18} />
                    Generating...
                  </>
                ) : (
                  <>
                    <Play size={18} />
                    Generate Music
                  </>
                )}
              </button>
            </div>
          )}

          {activeTab === 'library' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-slate-300">Your Tracks</h3>
                <span className="text-xs bg-slate-800 px-2 py-1 rounded-full text-slate-400">
                  {tracks.length} total
                </span>
              </div>

              {tracks.length === 0 ? (
                <div className="text-center py-12 text-slate-600">
                  <Music size={48} className="mx-auto mb-3 opacity-20" />
                  <p className="text-sm">No tracks yet</p>
                  <p className="text-xs mt-1">Generate some music to get started</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {tracks.map((track) => (
                    <button
                      key={track.jobId}
                      onClick={() => track.status === 'completed' && setCurrentTrack(track)}
                      className={`w-full p-3 rounded-lg border transition-all text-left ${
                        currentTrack?.jobId === track.jobId
                          ? 'bg-purple-900/30 border-purple-500/50'
                          : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-slate-200 truncate text-sm">
                            {track.title}
                          </div>
                          {track.genre && (
                            <div className="text-xs text-slate-500 capitalize">
                              {track.genre} {track.mood && `• ${track.mood}`}
                            </div>
                          )}
                        </div>

                        <div className="ml-2">
                          {track.status === 'completed' && (
                            <Play size={14} className="text-green-500" />
                          )}
                          {track.status === 'running' && (
                            <Loader2 size={14} className="text-blue-500 animate-spin" />
                          )}
                          {track.status === 'pending' && (
                            <Loader2 size={14} className="text-slate-500" />
                          )}
                          {track.status === 'failed' && (
                            <span className="text-xs text-red-500">Failed</span>
                          )}
                        </div>
                      </div>

                      {track.status !== 'completed' && (
                        <div className="mt-2">
                          <div className="h-1 bg-slate-700 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-purple-500 transition-all duration-300"
                              style={{ width: `${track.progress}%` }}
                            />
                          </div>
                          <div className="text-xs text-slate-500 mt-1">
                            {track.status === 'pending' ? 'Queued...' : `${Math.round(track.progress)}%`}
                          </div>
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Right Side - Player & Visualization */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Player Area */}
        <div className="flex-1 p-6 overflow-y-auto">
          {currentTrack ? (
            <div className="max-w-4xl mx-auto space-y-6">
              {/* Track Info */}
              <div className="text-center space-y-2">
                <h2 className="text-3xl font-bold text-slate-100">{currentTrack.title}</h2>
                {currentTrack.genre && (
                  <div className="flex items-center justify-center gap-2 text-sm text-slate-400">
                    <span className="capitalize">{currentTrack.genre}</span>
                    {currentTrack.mood && (
                      <>
                        <span>•</span>
                        <span className="capitalize">{currentTrack.mood}</span>
                      </>
                    )}
                    <span>•</span>
                    <span>{currentTrack.duration}s</span>
                  </div>
                )}
              </div>

              {/* Player */}
              <MusicPlayer
                jobId={currentTrack.jobId}
                audioUrl={currentTrack.audioUrl || null}
                stems={currentTrack.stems || null}
              />

              {/* Download Section */}
              {currentTrack.audioUrl && (
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="flex items-center gap-2 mb-3">
                    <Download size={16} className="text-slate-400" />
                    <span className="text-sm font-semibold text-slate-300">Downloads</span>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <a
                      href={currentTrack.audioUrl}
                      download
                      className="flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg text-sm font-medium text-white transition-colors"
                    >
                      <Download size={14} />
                      Full Mix
                    </a>

                    {currentTrack.stems && currentTrack.stems.length > 0 && (
                      <a
                        href={`http://localhost:8000/download/${currentTrack.jobId}/stems.zip`}
                        download
                        className="flex items-center justify-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm font-medium text-white transition-colors"
                      >
                        <Download size={14} />
                        All Stems
                      </a>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-600">
              <div className="text-center">
                <Music size={64} className="mx-auto mb-4 opacity-20" />
                <h3 className="text-xl font-semibold mb-2">No Track Selected</h3>
                <p className="text-sm">
                  {tracks.length === 0
                    ? 'Generate music from the Auto or Manual tab'
                    : 'Select a track from your library'}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Status Bar */}
        <div className="px-6 py-3 bg-slate-900 border-t border-slate-800">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <div className="flex items-center gap-4">
              <span>{tracks.length} tracks generated</span>
              <span>•</span>
              <span>
                {tracks.filter(t => t.status === 'running').length} processing
              </span>
            </div>

            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span>API Connected</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
