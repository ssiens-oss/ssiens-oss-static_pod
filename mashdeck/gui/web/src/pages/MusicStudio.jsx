/**
 * StaticWaves Music Studio
 * Complete AI music generation interface with real-time controls
 */

import { useState, useEffect, useRef } from 'react';
import { Play, Pause, Download, Settings, Sliders, Waveform, Music, Layers } from 'lucide-react';
import axios from 'axios';

// WebAudio context for visualization
let audioContext;
let analyser;
let gainNode;

const MusicStudio = () => {
  // State management
  const [isConnected, setIsConnected] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentJob, setCurrentJob] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);

  // Music parameters
  const [vibe, setVibe] = useState({
    energy: 0.5,
    tension: 0.5,
    darkness: 0.5,
    complexity: 0.5
  });

  const [genreМix, setGenreMix] = useState({
    synthwave: 0.6,
    lofi: 0.3,
    ambient: 0.1
  });

  const [musicSpec, setMusicSpec] = useState({
    bpm: 120,
    key: 'C minor',
    duration: 60,
    stems: true
  });

  const [selectedInstrument, setSelectedInstrument] = useState('violin');
  const [pitch, setPitch] = useState(60); // Middle C

  // Refs
  const wsRef = useRef(null);
  const canvasRef = useRef(null);
  const spectrumCanvasRef = useRef(null);
  const animationRef = useRef(null);

  // Available instruments
  const instruments = [
    { id: 'violin', name: 'Violin', category: 'strings' },
    { id: 'cello', name: 'Cello', category: 'strings' },
    { id: 'trumpet', name: 'Trumpet', category: 'brass' },
    { id: 'flute', name: 'Flute', category: 'woodwind' },
    { id: 'analog_bass', name: 'Analog Bass', category: 'synth' },
    { id: 'supersaw', name: 'Supersaw', category: 'synth' }
  ];

  // Initialize WebAudio
  useEffect(() => {
    if (!audioContext) {
      audioContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: 32000
      });

      analyser = audioContext.createAnalyser();
      analyser.fftSize = 2048;

      gainNode = audioContext.createGain();
      gainNode.gain.value = 1.0;

      analyser.connect(gainNode);
      gainNode.connect(audioContext.destination);
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  // Connect to WebSocket server
  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8765');
    ws.binaryType = 'arraybuffer';

    ws.onopen = () => {
      console.log('✓ Connected to DDSP server');
      setIsConnected(true);
      wsRef.current = ws;
    };

    ws.onmessage = (event) => {
      if (event.data instanceof ArrayBuffer) {
        playPCMAudio(event.data);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('✗ Disconnected from DDSP server');
      setIsConnected(false);
      wsRef.current = null;
    };
  };

  // Play PCM audio through WebAudio
  const playPCMAudio = (arrayBuffer) => {
    const pcmData = new Int16Array(arrayBuffer);
    const floatData = new Float32Array(pcmData.length);

    // Convert Int16 to Float32
    for (let i = 0; i < pcmData.length; i++) {
      floatData[i] = pcmData[i] / 32768.0;
    }

    // Create audio buffer
    const buffer = audioContext.createBuffer(1, floatData.length, 32000);
    buffer.getChannelData(0).set(floatData);

    // Play buffer
    const source = audioContext.createBufferSource();
    source.buffer = buffer;
    source.connect(analyser);
    source.start();
  };

  // Send control update to server
  const sendControl = (updates) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        ...updates,
        instrument: selectedInstrument,
        playing: isPlaying
      }));
    }
  };

  // Handle vibe slider changes
  const handleVibeChange = (param, value) => {
    const newVibe = { ...vibe, [param]: value };
    setVibe(newVibe);
    sendControl({ ...newVibe, pitch });
  };

  // Toggle playback
  const togglePlayback = () => {
    const newPlaying = !isPlaying;
    setIsPlaying(newPlaying);

    if (newPlaying && !isConnected) {
      connectWebSocket();
    }

    sendControl({ playing: newPlaying });
  };

  // Draw waveform visualization
  const drawWaveform = () => {
    if (!analyser || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    const dataArray = new Uint8Array(analyser.fftSize);
    analyser.getByteTimeDomainData(dataArray);

    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, width, height);

    ctx.lineWidth = 2;
    ctx.strokeStyle = '#00ffff';
    ctx.beginPath();

    const sliceWidth = width / dataArray.length;
    let x = 0;

    for (let i = 0; i < dataArray.length; i++) {
      const v = dataArray[i] / 255.0;
      const y = v * height;

      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }

      x += sliceWidth;
    }

    ctx.stroke();

    animationRef.current = requestAnimationFrame(drawWaveform);
  };

  // Draw spectrum visualization
  const drawSpectrum = () => {
    if (!analyser || !spectrumCanvasRef.current) return;

    const canvas = spectrumCanvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(dataArray);

    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, width, height);

    const barWidth = width / dataArray.length * 2.5;
    let x = 0;

    for (let i = 0; i < dataArray.length; i++) {
      const barHeight = (dataArray[i] / 255) * height;

      const hue = (i / dataArray.length) * 360;
      ctx.fillStyle = `hsl(${hue}, 100%, 50%)`;
      ctx.fillRect(x, height - barHeight, barWidth, barHeight);

      x += barWidth + 1;
    }
  };

  // Start visualization
  useEffect(() => {
    if (isPlaying) {
      drawWaveform();
      const spectrumInterval = setInterval(drawSpectrum, 50);
      return () => clearInterval(spectrumInterval);
    }
  }, [isPlaying]);

  // Generate full track
  const generateTrack = async () => {
    try {
      const spec = {
        ...musicSpec,
        vibe,
        genre_mix: genreMix,
        instruments: {
          rhythm: '808',
          bass: 'analog_mono',
          harmony: 'warm_pad',
          melody: selectedInstrument
        }
      };

      const response = await axios.post('http://localhost:8000/generate', spec);
      setCurrentJob(response.data.job_id);

      // Start polling for status
      pollJobStatus(response.data.job_id);
    } catch (error) {
      console.error('Error generating track:', error);
    }
  };

  // Poll job status
  const pollJobStatus = async (jobId) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`http://localhost:8000/status/${jobId}`);
        setJobStatus(response.data);

        if (response.data.status === 'completed' || response.data.status === 'failed') {
          clearInterval(interval);
        }
      } catch (error) {
        console.error('Error polling status:', error);
        clearInterval(interval);
      }
    }, 2000);
  };

  // Download generated track
  const downloadTrack = (fileType = 'mix') => {
    if (!currentJob) return;
    window.open(`http://localhost:8000/download/${currentJob}/${fileType}`, '_blank');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-600">
              StaticWaves Music Studio
            </h1>
            <p className="text-gray-400 mt-2">Real-time AI music generation & synthesis</p>
          </div>
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${isConnected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
              {isConnected ? 'Connected' : 'Disconnected'}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel - Controls */}
          <div className="lg:col-span-2 space-y-6">
            {/* Playback Controls */}
            <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <Music className="w-5 h-5" />
                  Live Performance
                </h2>
                <button
                  onClick={togglePlayback}
                  className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
                    isPlaying
                      ? 'bg-red-500 hover:bg-red-600'
                      : 'bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700'
                  }`}
                >
                  {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                  {isPlaying ? 'Stop' : 'Play Live'}
                </button>
              </div>

              {/* Pitch Control */}
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">
                  Pitch: {pitch} ({['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][pitch % 12]}{Math.floor(pitch / 12) - 1})
                </label>
                <input
                  type="range"
                  min="36"
                  max="84"
                  value={pitch}
                  onChange={(e) => {
                    const newPitch = Number(e.target.value);
                    setPitch(newPitch);
                    sendControl({ pitch: newPitch });
                  }}
                  className="w-full accent-cyan-500"
                />
              </div>

              {/* Instrument Selector */}
              <div>
                <label className="block text-sm font-medium mb-2">Instrument</label>
                <div className="grid grid-cols-3 gap-2">
                  {instruments.map(inst => (
                    <button
                      key={inst.id}
                      onClick={() => {
                        setSelectedInstrument(inst.id);
                        sendControl({ instrument: inst.id });
                      }}
                      className={`px-4 py-2 rounded-lg transition-all ${
                        selectedInstrument === inst.id
                          ? 'bg-cyan-500 text-white'
                          : 'bg-gray-700 hover:bg-gray-600'
                      }`}
                    >
                      {inst.name}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Vibe Controls */}
            <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <Sliders className="w-5 h-5" />
                Vibe Controls
              </h2>
              <div className="space-y-4">
                {Object.entries(vibe).map(([param, value]) => (
                  <div key={param}>
                    <label className="block text-sm font-medium mb-2 capitalize">
                      {param}: {value.toFixed(2)}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.01"
                      value={value}
                      onChange={(e) => handleVibeChange(param, Number(e.target.value))}
                      className="w-full accent-purple-500"
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Visualization */}
            <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <Waveform className="w-5 h-5" />
                Audio Visualization
              </h2>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-400 mb-2">Waveform</p>
                  <canvas
                    ref={canvasRef}
                    width="800"
                    height="150"
                    className="w-full rounded-lg border border-gray-700"
                  />
                </div>
                <div>
                  <p className="text-sm text-gray-400 mb-2">Spectrum</p>
                  <canvas
                    ref={spectrumCanvasRef}
                    width="800"
                    height="150"
                    className="w-full rounded-lg border border-gray-700"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Right Panel - Track Generation */}
          <div className="space-y-6">
            {/* Track Generation */}
            <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Generate Track
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">BPM</label>
                  <input
                    type="number"
                    value={musicSpec.bpm}
                    onChange={(e) => setMusicSpec({ ...musicSpec, bpm: Number(e.target.value) })}
                    className="w-full bg-gray-700 rounded-lg px-4 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Key</label>
                  <select
                    value={musicSpec.key}
                    onChange={(e) => setMusicSpec({ ...musicSpec, key: e.target.value })}
                    className="w-full bg-gray-700 rounded-lg px-4 py-2"
                  >
                    <option>C major</option>
                    <option>C minor</option>
                    <option>D minor</option>
                    <option>E minor</option>
                    <option>F major</option>
                    <option>G major</option>
                    <option>A minor</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Duration (seconds)</label>
                  <input
                    type="number"
                    value={musicSpec.duration}
                    onChange={(e) => setMusicSpec({ ...musicSpec, duration: Number(e.target.value) })}
                    className="w-full bg-gray-700 rounded-lg px-4 py-2"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="stems"
                    checked={musicSpec.stems}
                    onChange={(e) => setMusicSpec({ ...musicSpec, stems: e.target.checked })}
                    className="accent-cyan-500"
                  />
                  <label htmlFor="stems" className="text-sm">Export stems</label>
                </div>
                <button
                  onClick={generateTrack}
                  className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 py-3 rounded-lg font-semibold transition-all"
                >
                  Generate Track
                </button>
              </div>
            </div>

            {/* Job Status */}
            {jobStatus && (
              <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700">
                <h3 className="text-lg font-semibold mb-4">Generation Status</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Status:</span>
                    <span className={`font-semibold ${
                      jobStatus.status === 'completed' ? 'text-green-400' :
                      jobStatus.status === 'failed' ? 'text-red-400' :
                      'text-yellow-400'
                    }`}>{jobStatus.status}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Progress:</span>
                    <span>{Math.round(jobStatus.progress || 0)}%</span>
                  </div>
                  {jobStatus.status === 'completed' && (
                    <div className="mt-4 space-y-2">
                      <button
                        onClick={() => downloadTrack('mix')}
                        className="w-full bg-green-600 hover:bg-green-700 py-2 rounded-lg flex items-center justify-center gap-2"
                      >
                        <Download className="w-4 h-4" />
                        Download Mix
                      </button>
                      {musicSpec.stems && (
                        <>
                          <button onClick={() => downloadTrack('bass')} className="w-full bg-gray-700 hover:bg-gray-600 py-2 rounded-lg text-sm">
                            Download Bass Stem
                          </button>
                          <button onClick={() => downloadTrack('lead')} className="w-full bg-gray-700 hover:bg-gray-600 py-2 rounded-lg text-sm">
                            Download Lead Stem
                          </button>
                        </>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MusicStudio;
