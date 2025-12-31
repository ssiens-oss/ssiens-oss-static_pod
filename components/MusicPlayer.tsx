/**
 * MusicPlayer - Audio player with waveform visualization
 *
 * Features:
 * - Play/pause controls
 * - Waveform visualization
 * - Download options (mix + stems)
 */

import React, { useRef, useEffect, useState } from 'react';
import { Play, Pause, Download, Music2 } from 'lucide-react';


interface MusicPlayerProps {
  jobId: string | null;
  audioUrl: string | null;
  stems: string[] | null;
}


export function MusicPlayer({ jobId, audioUrl, stems }: MusicPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  // Handle play/pause
  const togglePlay = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }

    setIsPlaying(!isPlaying);
  };

  // Update time
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('ended', () => setIsPlaying(false));

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('ended', () => setIsPlaying(false));
    };
  }, [audioUrl]);

  // Draw waveform (simplified visualization)
  useEffect(() => {
    if (!canvasRef.current || !audioUrl) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.fillStyle = '#1e293b';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw simple waveform bars
    const barCount = 60;
    const barWidth = canvas.width / barCount;
    const progress = duration > 0 ? currentTime / duration : 0;

    for (let i = 0; i < barCount; i++) {
      const barHeight = Math.random() * canvas.height * 0.8;
      const x = i * barWidth;
      const y = (canvas.height - barHeight) / 2;

      // Color based on progress
      if (i / barCount <= progress) {
        ctx.fillStyle = '#a855f7';  // Purple for played
      } else {
        ctx.fillStyle = '#475569';  // Gray for unplayed
      }

      ctx.fillRect(x + 2, y, barWidth - 4, barHeight);
    }
  }, [audioUrl, currentTime, duration]);

  // Format time
  const formatTime = (seconds: number) => {
    if (!isFinite(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!audioUrl) {
    return (
      <div className="bg-slate-900 border-2 border-slate-800 rounded-xl p-8 flex flex-col items-center justify-center text-slate-600">
        <Music2 size={48} className="mb-3 opacity-20" />
        <span className="text-sm">No music generated yet</span>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border-2 border-slate-800 rounded-xl overflow-hidden">
      {/* Audio element */}
      <audio ref={audioRef} src={audioUrl} />

      {/* Waveform */}
      <div className="p-4">
        <canvas
          ref={canvasRef}
          width={800}
          height={120}
          className="w-full h-32 rounded-lg"
        />
      </div>

      {/* Controls */}
      <div className="px-4 pb-4 space-y-3">
        {/* Time display */}
        <div className="flex justify-between text-xs text-slate-400">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>

        {/* Progress bar */}
        <div className="h-1 bg-slate-800 rounded-full overflow-hidden cursor-pointer">
          <div
            className="h-full bg-purple-500 transition-all"
            style={{ width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%` }}
          />
        </div>

        {/* Play button */}
        <div className="flex items-center justify-center gap-4">
          <button
            onClick={togglePlay}
            className="p-4 bg-purple-600 hover:bg-purple-500 rounded-full transition-colors shadow-lg shadow-purple-900/20"
          >
            {isPlaying ? (
              <Pause size={24} className="text-white" />
            ) : (
              <Play size={24} className="text-white ml-0.5" />
            )}
          </button>
        </div>

        {/* Download options */}
        {stems && stems.length > 0 && (
          <div className="pt-3 border-t border-slate-800">
            <div className="flex items-center gap-2 mb-2">
              <Download size={14} className="text-slate-400" />
              <span className="text-xs font-semibold text-slate-400">Download</span>
            </div>

            <div className="flex flex-wrap gap-2">
              <a
                href={audioUrl}
                download
                className="px-3 py-1 bg-slate-800 hover:bg-slate-700 rounded text-xs text-slate-300 transition-colors"
              >
                Full Mix
              </a>

              {stems.map(stem => (
                <a
                  key={stem}
                  href={`/api/music/download/${jobId}/${stem}`}
                  download
                  className="px-3 py-1 bg-slate-800 hover:bg-slate-700 rounded text-xs text-slate-300 transition-colors capitalize"
                >
                  {stem}
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
