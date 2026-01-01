/**
 * AudioPlayer Component
 * Advanced audio player with waveform visualization
 */

import { useEffect, useRef, useState } from 'react';
import { Play, Pause, Volume2, VolumeX, Download } from 'lucide-react';
import { clsx } from 'clsx';
import useStore from '../store';
import Button from './Button';

const AudioPlayer = ({ src, title, showWaveform = true, className = '' }) => {
  const audioRef = useRef(null);
  const canvasRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [waveformData, setWaveformData] = useState([]);

  // Initialize audio
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !src) return;

    audio.src = src;
    audio.volume = volume;

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
      if (showWaveform) {
        generateWaveform();
      }
    };

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
    };

    const handleEnded = () => {
      setIsPlaying(false);
    };

    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [src, showWaveform]);

  // Generate waveform visualization
  const generateWaveform = async () => {
    if (!src) return;

    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const response = await fetch(src);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

      const rawData = audioBuffer.getChannelData(0);
      const samples = 100;
      const blockSize = Math.floor(rawData.length / samples);
      const filteredData = [];

      for (let i = 0; i < samples; i++) {
        let blockStart = blockSize * i;
        let sum = 0;
        for (let j = 0; j < blockSize; j++) {
          sum += Math.abs(rawData[blockStart + j]);
        }
        filteredData.push(sum / blockSize);
      }

      const multiplier = Math.max(...filteredData) ** -1;
      const normalizedData = filteredData.map((n) => n * multiplier);
      setWaveformData(normalizedData);
    } catch (error) {
      console.error('Error generating waveform:', error);
    }
  };

  // Draw waveform on canvas
  useEffect(() => {
    if (!showWaveform || !canvasRef.current || waveformData.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;

    canvas.width = canvas.offsetWidth * dpr;
    canvas.height = canvas.offsetHeight * dpr;
    ctx.scale(dpr, dpr);

    const width = canvas.offsetWidth;
    const height = canvas.offsetHeight;
    const barWidth = width / waveformData.length;
    const progress = currentTime / duration;

    ctx.clearRect(0, 0, width, height);

    waveformData.forEach((value, index) => {
      const barHeight = value * height * 0.8;
      const x = index * barWidth;
      const y = (height - barHeight) / 2;

      // Color bars based on progress
      if (index / waveformData.length < progress) {
        ctx.fillStyle = '#8b5cf6'; // Accent color for played
      } else {
        ctx.fillStyle = '#4a4a5e'; // Gray for unplayed
      }

      ctx.fillRect(x, y, barWidth - 1, barHeight);
    });
  }, [waveformData, currentTime, duration, showWaveform]);

  const togglePlayPause = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (e) => {
    const audio = audioRef.current;
    if (!audio) return;

    const bounds = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - bounds.left;
    const percentage = x / bounds.width;
    const newTime = percentage * duration;

    audio.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const toggleMute = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isMuted) {
      audio.volume = volume;
      setIsMuted(false);
    } else {
      audio.volume = 0;
      setIsMuted(true);
    }
  };

  const handleVolumeChange = (e) => {
    const audio = audioRef.current;
    const newVolume = parseFloat(e.target.value);

    setVolume(newVolume);
    if (audio) {
      audio.volume = newVolume;
    }
    if (newVolume > 0) {
      setIsMuted(false);
    }
  };

  const formatTime = (time) => {
    if (isNaN(time)) return '0:00';
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleDownload = () => {
    const a = document.createElement('a');
    a.href = src;
    a.download = title || 'audio.mp3';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  if (!src) return null;

  return (
    <div className={clsx('bg-secondary/50 border border-white/10 rounded-lg p-4', className)}>
      <audio ref={audioRef} />

      {title && (
        <div className="mb-3">
          <h4 className="font-semibold text-white">{title}</h4>
        </div>
      )}

      {/* Waveform */}
      {showWaveform && (
        <div className="mb-3">
          <canvas
            ref={canvasRef}
            className="w-full h-16 cursor-pointer rounded"
            onClick={handleSeek}
          />
        </div>
      )}

      {/* Progress Bar */}
      {!showWaveform && (
        <div
          className="mb-3 h-2 bg-secondary rounded-full cursor-pointer overflow-hidden"
          onClick={handleSeek}
        >
          <div
            className="h-full bg-accent transition-all"
            style={{ width: `${(currentTime / duration) * 100}%` }}
          />
        </div>
      )}

      {/* Controls */}
      <div className="flex items-center gap-4">
        <button
          onClick={togglePlayPause}
          className="w-10 h-10 flex items-center justify-center bg-accent hover:bg-accent/90 rounded-full transition-colors"
        >
          {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
        </button>

        <div className="flex-1">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={toggleMute}
            className="p-2 hover:bg-white/10 rounded transition-colors"
          >
            {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
          </button>

          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={isMuted ? 0 : volume}
            onChange={handleVolumeChange}
            className="w-20 accent-accent"
          />

          <button
            onClick={handleDownload}
            className="p-2 hover:bg-white/10 rounded transition-colors"
            title="Download"
          >
            <Download className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AudioPlayer;
