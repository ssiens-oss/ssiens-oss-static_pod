import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Terminal } from './components/Terminal';
import { EditorControls } from './components/EditorControls';
import { LogEntry, LogType, QueueItem, EngineConfig, EditorState } from './types';
import {
  Rocket,
  Layers,
  Box,
  Settings,
  Play,
  Image as ImageIcon,
  CheckCircle2,
  Loader2,
  AlertCircle,
  Wifi,
  WifiOff
} from 'lucide-react';

const INITIAL_EDITOR_STATE: EditorState = {
  scale: 1,
  translateX: 0,
  translateY: 0
};

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

export default function ProductionApp() {
  // --- State ---
  const [config, setConfig] = useState<EngineConfig>({
    dropName: 'Drop7',
    designCount: 10,
    blueprintId: 6,
    providerId: 1,
    batchList: ''
  });

  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [pipelineId, setPipelineId] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  // Images
  const [designImage, setDesignImage] = useState<string | null>(null);
  const [mockupImage, setMockupImage] = useState<string | null>(null);

  // Editor State
  const [editorState, setEditorState] = useState<EditorState>(INITIAL_EDITOR_STATE);

  // Polling interval
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // --- Check API Status ---
  useEffect(() => {
    checkApiStatus();
    const interval = setInterval(checkApiStatus, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const checkApiStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);
      if (response.ok) {
        setApiStatus('online');
      } else {
        setApiStatus('offline');
      }
    } catch (error) {
      setApiStatus('offline');
    }
  };

  // --- Poll pipeline status ---
  const startPolling = useCallback((pipelineId: string) => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }

    pollIntervalRef.current = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/api/pipeline/${pipelineId}/logs`);
        if (!response.ok) throw new Error('Failed to fetch logs');

        const data = await response.json();

        setLogs(data.logs);
        setProgress(data.progress || 0);

        if (data.status === 'completed' || data.status === 'failed') {
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
          setIsRunning(false);

          // Fetch final result
          const resultResponse = await fetch(`${API_URL}/api/pipeline/${pipelineId}`);
          const resultData = await resultResponse.json();

          if (resultData.result?.generatedImages?.length > 0) {
            setDesignImage(resultData.result.generatedImages[0].url);
          }
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, 2000); // Poll every 2 seconds
  }, []);

  // --- Handlers ---
  const addLog = useCallback((message: string, type: LogType = LogType.INFO) => {
    setLogs(prev => [...prev, {
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
      message,
      type
    }]);
  }, []);

  const handleRun = async () => {
    if (isRunning || apiStatus === 'offline') return;

    setIsRunning(true);
    setProgress(0);
    setQueue([]);
    setLogs([]);
    setDesignImage(null);
    setMockupImage(null);
    setEditorState(INITIAL_EDITOR_STATE);

    try {
      addLog('🚀 Starting POD automation pipeline...', LogType.INFO);

      const response = await fetch(`${API_URL}/api/pipeline/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          dropName: config.dropName,
          designCount: config.designCount,
          theme: 'Modern streetwear',
          style: 'Bold graphic design',
          niche: 'Urban fashion',
          productTypes: ['tshirt', 'hoodie']
        })
      });

      if (!response.ok) {
        throw new Error('Failed to start pipeline');
      }

      const data = await response.json();
      setPipelineId(data.pipelineId);

      addLog(`✓ Pipeline started: ${data.pipelineId}`, LogType.SUCCESS);

      // Start polling for updates
      startPolling(data.pipelineId);
    } catch (error) {
      addLog(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`, LogType.ERROR);
      setIsRunning(false);
    }
  };

  // Editor Handlers
  const handleZoom = (factor: number) => {
    setEditorState(prev => ({ ...prev, scale: prev.scale * factor }));
  };

  const handleMove = (dx: number, dy: number) => {
    setEditorState(prev => ({
      ...prev,
      translateX: prev.translateX + dx,
      translateY: prev.translateY + dy
    }));
  };

  const handleSaveEdit = () => {
    addLog(`Edited image saved locally with transform applied.`, LogType.SUCCESS);
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200">

      {/* --- LEFT SIDEBAR: Controls & Queue --- */}
      <div className="w-96 flex flex-col border-r border-slate-800 bg-slate-900/50">

        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center gap-3">
          <div className="p-2 bg-indigo-600 rounded-lg shadow-lg shadow-indigo-500/20">
            <Layers className="text-white" size={24} />
          </div>
          <div className="flex-1">
            <h1 className="font-bold text-slate-100 leading-tight">StaticWaves</h1>
            <p className="text-xs text-indigo-400 font-mono">POD STUDIO (PRODUCTION)</p>
          </div>
          <div className="flex items-center gap-1">
            {apiStatus === 'online' ? (
              <Wifi size={16} className="text-emerald-500" />
            ) : apiStatus === 'offline' ? (
              <WifiOff size={16} className="text-red-500" />
            ) : (
              <Loader2 size={16} className="text-slate-500 animate-spin" />
            )}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide">

          {/* API Status Banner */}
          {apiStatus === 'offline' && (
            <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3">
              <div className="flex items-center gap-2 text-red-400 text-sm">
                <AlertCircle size={16} />
                <span>API Server Offline</span>
              </div>
              <p className="text-xs text-red-300/70 mt-1">
                Make sure the backend server is running on port 3000
              </p>
            </div>
          )}

          {/* Main Controls Form */}
          <div className="space-y-4">
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Configuration</label>

            <div className="space-y-3">
              <div>
                <span className="text-xs text-slate-400 mb-1 block">Drop Name</span>
                <input
                  type="text"
                  value={config.dropName}
                  onChange={e => setConfig({...config, dropName: e.target.value})}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
                  disabled={isRunning}
                />
              </div>

              <div className="grid grid-cols-3 gap-2">
                 <div>
                    <span className="text-xs text-slate-400 mb-1 block">Count</span>
                    <input
                      type="number"
                      value={config.designCount}
                      onChange={e => setConfig({...config, designCount: parseInt(e.target.value)})}
                      className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-2 text-sm focus:outline-none focus:border-indigo-500"
                      disabled={isRunning}
                    />
                 </div>
                 <div>
                    <span className="text-xs text-slate-400 mb-1 block">Blueprint</span>
                    <input
                      type="number"
                      value={config.blueprintId}
                      onChange={e => setConfig({...config, blueprintId: parseInt(e.target.value)})}
                      className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-2 text-sm focus:outline-none focus:border-indigo-500"
                      disabled={isRunning}
                    />
                 </div>
                 <div>
                    <span className="text-xs text-slate-400 mb-1 block">Provider</span>
                    <input
                      type="number"
                      value={config.providerId}
                      onChange={e => setConfig({...config, providerId: parseInt(e.target.value)})}
                      className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-2 text-sm focus:outline-none focus:border-indigo-500"
                      disabled={isRunning}
                    />
                 </div>
              </div>
            </div>
          </div>

          {/* Action Button */}
          <div className="grid grid-cols-1 gap-3">
            <button
              onClick={handleRun}
              disabled={isRunning || apiStatus === 'offline'}
              className={`flex items-center justify-center gap-2 py-3 rounded-lg font-semibold shadow-lg transition-all ${
                isRunning || apiStatus === 'offline'
                  ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-900/20'
              }`}
            >
              {isRunning ? <Loader2 className="animate-spin" size={18} /> : <Play size={18} />}
              {apiStatus === 'offline' ? 'Server Offline' : isRunning ? 'Running Pipeline...' : 'Run Pipeline'}
            </button>
          </div>

          {/* Upload Queue */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Printify Queue</label>
              <span className="text-xs bg-slate-800 px-2 py-0.5 rounded-full text-slate-400">{queue.length}</span>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden min-h-[150px]">
              {queue.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-36 text-slate-600">
                  <Box size={24} className="mb-2 opacity-50"/>
                  <span className="text-xs">Queue is empty</span>
                </div>
              ) : (
                <ul className="divide-y divide-slate-800">
                  {queue.map(item => (
                    <li key={item.id} className="px-3 py-2 flex items-center justify-between text-sm">
                      <span className="truncate max-w-[140px] text-slate-300">{item.name}</span>
                      <div className="flex items-center gap-2">
                        {item.status === 'pending' && <span className="text-xs text-slate-500">Wait</span>}
                        {item.status === 'uploading' && <Loader2 size={14} className="animate-spin text-blue-400"/>}
                        {item.status === 'completed' && <CheckCircle2 size={14} className="text-emerald-500"/>}
                        {item.status === 'failed' && <AlertCircle size={14} className="text-red-500"/>}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>

        {/* Global Progress Bar */}
        <div className="p-4 bg-slate-900 border-t border-slate-800">
          <div className="flex justify-between text-xs text-slate-400 mb-1">
             <span>Global Progress</span>
             <span>{Math.round(progress)}%</span>
          </div>
          <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-500 transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* --- RIGHT CONTENT: Preview & Logs --- */}
      <div className="flex-1 flex flex-col overflow-hidden">

        {/* Top Area: Previews & Editor */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="flex items-center gap-2 mb-4">
            <ImageIcon size={20} className="text-indigo-400"/>
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
                       <Layers size={48} className="mb-2 opacity-20"/>
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
                       <Box size={48} className="mb-2 opacity-20"/>
                       <span className="text-sm">Waiting for mockup...</span>
                    </div>
                   )}
                </div>
            </div>

            {/* Editor Tools Column */}
            <div className="lg:col-span-2 flex flex-col justify-center">
               <EditorControls
                  onZoom={handleZoom}
                  onMove={handleMove}
                  onSave={handleSaveEdit}
                  state={editorState}
               />
            </div>
          </div>
        </div>

        {/* Bottom Area: Logs */}
        <div className="h-64 p-4 border-t border-slate-800 bg-slate-900/30">
          <Terminal logs={logs} onClear={() => setLogs([])} />
        </div>

      </div>
    </div>
  );
}
