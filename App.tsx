import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Terminal } from './components/Terminal';
import { EditorControls } from './components/EditorControls';
import { Settings as SettingsPanel, AppSettings, DEFAULT_SETTINGS } from './components/Settings';
import { ShortcutsHelp } from './components/ShortcutsHelp';
import { ErrorBoundary } from './components/ErrorBoundary';
import { runSimulation } from './services/mockEngine';
import { LogEntry, LogType, QueueItem, EngineConfig, EditorState } from './types';
import { useKeyboardShortcuts, KeyboardShortcut } from './utils/useKeyboardShortcuts';
import { useHistory } from './utils/useHistory';
import { saveToStorage, loadFromStorage, StorageKeys } from './utils/storage';
import { exportTransformedImage, exportLogs, exportQueueData } from './utils/export';
import {
  Rocket,
  Layers,
  Box,
  Settings as SettingsIcon,
  Play,
  Image as ImageIcon,
  CheckCircle2,
  Loader2,
  AlertCircle,
  Download,
  Undo,
  Redo,
  Keyboard,
  StopCircle
} from 'lucide-react';

const INITIAL_EDITOR_STATE: EditorState = {
  scale: 1,
  translateX: 0,
  translateY: 0
};

function AppContent() {
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

  // Images
  const [designImage, setDesignImage] = useState<string | null>(null);
  const [mockupImage, setMockupImage] = useState<string | null>(null);

  // Editor State with History
  const [editorState, setEditorStateRaw, historyActions] = useHistory<EditorState>(
    INITIAL_EDITOR_STATE,
    50
  );

  // UI State
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [shortcutsOpen, setShortcutsOpen] = useState(false);
  const [settings, setSettings] = useState<AppSettings>(() =>
    loadFromStorage(StorageKeys.SETTINGS, DEFAULT_SETTINGS)
  );

  // Stop Signal
  const stopRef = useRef(false);

  // --- Local Storage Persistence ---
  useEffect(() => {
    saveToStorage(StorageKeys.SETTINGS, settings);
  }, [settings]);

  useEffect(() => {
    if (settings.autoSave) {
      saveToStorage(StorageKeys.EDITOR_STATE, editorState);
    }
  }, [editorState, settings.autoSave]);

  // --- Handlers ---
  const addLog = useCallback((message: string, type: LogType = LogType.INFO) => {
    setLogs(prev => [...prev, {
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
      message,
      type
    }]);
  }, []);

  const handleRun = async (isBatch: boolean) => {
    if (isRunning) return;
    
    stopRef.current = false;
    setIsRunning(true);
    setProgress(0);
    setQueue([]); // Clear queue for new run
    setLogs([]);  // Clear logs (optional)
    
    // Reset images if starting new run
    setDesignImage(null);
    setMockupImage(null);
    setEditorState(INITIAL_EDITOR_STATE);

    const drops = isBatch 
      ? config.batchList.split(',').map(d => d.trim()).filter(Boolean)
      : [config.dropName];

    if (drops.length === 0) {
      addLog("No drops specified!", LogType.ERROR);
      setIsRunning(false);
      return;
    }

    try {
      for (let i = 0; i < drops.length; i++) {
        if (stopRef.current) break;
        
        await runSimulation(
          drops[i],
          isBatch,
          (log) => setLogs(prev => [...prev, log]),
          (prog) => {
            // Calculate total progress based on current batch index
            const baseProgress = (i / drops.length) * 100;
            const currentStepProgress = (prog / 100) * (100 / drops.length);
            setProgress(baseProgress + currentStepProgress);
          },
          (item) => setQueue(prev => {
             const existing = prev.findIndex(q => q.id === item.id);
             if (existing >= 0) {
               const copy = [...prev];
               copy[existing] = item;
               return copy;
             }
             return [...prev, item];
          }),
          (type, url) => {
            if (type === 'design') setDesignImage(url);
            if (type === 'mockup') setMockupImage(url);
          },
          () => stopRef.current
        );
      }
    } catch (err) {
      addLog(`Critical Error: ${err}`, LogType.ERROR);
    } finally {
      setIsRunning(false);
      setProgress(100);
    }
  };

  // Editor Handlers
  const handleZoom = (factor: number) => {
    setEditorStateRaw({ ...editorState, scale: editorState.scale * factor });
  };

  const handleMove = (dx: number, dy: number) => {
    setEditorStateRaw({
      ...editorState,
      translateX: editorState.translateX + dx,
      translateY: editorState.translateY + dy
    });
  };

  const handleSaveEdit = async () => {
    if (!designImage) {
      addLog('No design image to save', LogType.WARNING);
      return;
    }

    try {
      await exportTransformedImage(designImage, editorState, {
        filename: `${config.dropName}_edited`,
        format: 'png',
        quality: 0.95
      });
      addLog('Edited image saved successfully', LogType.SUCCESS);
    } catch (error) {
      addLog(`Failed to save image: ${error}`, LogType.ERROR);
    }
  };

  const handleStop = () => {
    stopRef.current = true;
    addLog('Stopping simulation...', LogType.WARNING);
  };

  const handleExportLogs = () => {
    exportLogs(logs, `logs_${new Date().toISOString().slice(0, 10)}`);
    addLog('Logs exported successfully', LogType.SUCCESS);
  };

  const handleExportQueue = () => {
    exportQueueData(queue, `queue_${new Date().toISOString().slice(0, 10)}`);
    addLog('Queue data exported successfully', LogType.SUCCESS);
  };

  // --- Keyboard Shortcuts ---
  const shortcuts: KeyboardShortcut[] = [
    {
      key: 'r',
      ctrl: true,
      description: 'Run single drop',
      action: () => !isRunning && handleRun(false)
    },
    {
      key: 's',
      ctrl: true,
      description: 'Save edited design',
      action: handleSaveEdit
    },
    {
      key: 'z',
      ctrl: true,
      description: 'Undo editor change',
      action: historyActions.undo
    },
    {
      key: 'y',
      ctrl: true,
      description: 'Redo editor change',
      action: historyActions.redo
    },
    {
      key: ',',
      ctrl: true,
      description: 'Open settings',
      action: () => setSettingsOpen(true)
    },
    {
      key: '?',
      shift: true,
      description: 'Show keyboard shortcuts',
      action: () => setShortcutsOpen(true)
    },
    {
      key: 'Escape',
      description: 'Stop simulation',
      action: handleStop
    },
    {
      key: 'e',
      ctrl: true,
      description: 'Export logs',
      action: handleExportLogs
    }
  ];

  useKeyboardShortcuts(shortcuts, true);

  return (
    <>
      <div className="flex h-screen bg-slate-950 text-slate-200">

        {/* --- LEFT SIDEBAR: Controls & Queue --- */}
        <div className="w-96 flex flex-col border-r border-slate-800 bg-slate-900/50">

          {/* Header */}
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-indigo-600 rounded-lg shadow-lg shadow-indigo-500/20">
                <Layers className="text-white" size={24} />
              </div>
              <div>
                <h1 className="font-bold text-slate-100 leading-tight">StaticWaves</h1>
                <p className="text-xs text-indigo-400 font-mono">POD STUDIO v6.1</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShortcutsOpen(true)}
                className="p-2 hover:bg-slate-800 rounded-lg transition-colors text-slate-400 hover:text-slate-200"
                title="Keyboard Shortcuts (?)"
              >
                <Keyboard size={18} />
              </button>
              <button
                onClick={() => setSettingsOpen(true)}
                className="p-2 hover:bg-slate-800 rounded-lg transition-colors text-slate-400 hover:text-slate-200"
                title="Settings (Ctrl+,)"
              >
                <SettingsIcon size={18} />
              </button>
            </div>
          </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide">
          
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
                />
              </div>

              <div className="grid grid-cols-3 gap-2">
                 <div>
                    <span className="text-xs text-slate-400 mb-1 block">Count</span>
                    <input type="number" value={config.designCount} onChange={e => setConfig({...config, designCount: parseInt(e.target.value)})} className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-2 text-sm focus:outline-none focus:border-indigo-500" />
                 </div>
                 <div>
                    <span className="text-xs text-slate-400 mb-1 block">Blueprint</span>
                    <input type="number" value={config.blueprintId} onChange={e => setConfig({...config, blueprintId: parseInt(e.target.value)})} className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-2 text-sm focus:outline-none focus:border-indigo-500" />
                 </div>
                 <div>
                    <span className="text-xs text-slate-400 mb-1 block">Provider</span>
                    <input type="number" value={config.providerId} onChange={e => setConfig({...config, providerId: parseInt(e.target.value)})} className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-2 text-sm focus:outline-none focus:border-indigo-500" />
                 </div>
              </div>

              <div>
                <span className="text-xs text-slate-400 mb-1 block">Batch List (Comma separated)</span>
                <input 
                  type="text" 
                  placeholder="Drop1, Drop2, Drop3"
                  value={config.batchList}
                  onChange={e => setConfig({...config, batchList: e.target.value})}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-1 gap-3">
            <button
              onClick={() => handleRun(false)}
              disabled={isRunning}
              className={`flex items-center justify-center gap-2 py-3 rounded-lg font-semibold shadow-lg transition-all ${isRunning ? 'bg-slate-700 text-slate-500 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-900/20'}`}
            >
              {isRunning ? <Loader2 className="animate-spin" size={18} /> : <Play size={18} />}
              Run Single Drop {!isRunning && <span className="text-xs opacity-75">(Ctrl+R)</span>}
            </button>
            <button
              onClick={() => handleRun(true)}
              disabled={isRunning}
              className={`flex items-center justify-center gap-2 py-3 rounded-lg font-semibold shadow-lg transition-all border border-slate-700 ${isRunning ? 'bg-slate-800 text-slate-500 cursor-not-allowed' : 'bg-slate-800 hover:bg-slate-700 text-indigo-300'}`}
            >
              <Rocket size={18} />
              Run Batch Mode
            </button>
            {isRunning && (
              <button
                onClick={handleStop}
                className="flex items-center justify-center gap-2 py-3 rounded-lg font-semibold shadow-lg transition-all bg-red-600 hover:bg-red-500 text-white border border-red-700"
              >
                <StopCircle size={18} />
                Stop (ESC)
              </button>
            )}
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
            <div className="lg:col-span-2 flex flex-col justify-center gap-3">
               <EditorControls
                  onZoom={handleZoom}
                  onMove={handleMove}
                  onSave={handleSaveEdit}
                  state={editorState}
               />

               {/* History Controls */}
               <div className="bg-slate-800 p-3 rounded-lg border border-slate-700 space-y-2">
                 <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider mb-2">
                   History
                 </div>
                 <div className="grid grid-cols-2 gap-2">
                   <button
                     onClick={historyActions.undo}
                     disabled={!historyActions.canUndo}
                     className="flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:text-slate-600 text-slate-200 py-2 rounded transition-colors text-sm font-medium"
                     title="Undo (Ctrl+Z)"
                   >
                     <Undo size={16} /> Undo
                   </button>
                   <button
                     onClick={historyActions.redo}
                     disabled={!historyActions.canRedo}
                     className="flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:text-slate-600 text-slate-200 py-2 rounded transition-colors text-sm font-medium"
                     title="Redo (Ctrl+Y)"
                   >
                     <Redo size={16} /> Redo
                   </button>
                 </div>
               </div>

               {/* Export Controls */}
               <div className="bg-slate-800 p-3 rounded-lg border border-slate-700 space-y-2">
                 <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider mb-2">
                   Export
                 </div>
                 <button
                   onClick={handleExportLogs}
                   disabled={logs.length === 0}
                   className="w-full flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:text-slate-600 text-slate-200 py-2 rounded transition-colors text-sm font-medium"
                 >
                   <Download size={14} /> Logs
                 </button>
                 <button
                   onClick={handleExportQueue}
                   disabled={queue.length === 0}
                   className="w-full flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:text-slate-600 text-slate-200 py-2 rounded transition-colors text-sm font-medium"
                 >
                   <Download size={14} /> Queue
                 </button>
               </div>
            </div>
          </div>
        </div>

        {/* Bottom Area: Logs */}
        <div className="h-64 p-4 border-t border-slate-800 bg-slate-900/30">
          <Terminal logs={logs} onClear={() => setLogs([])} />
        </div>

      </div>
    </div>

      {/* Modals */}
      <SettingsPanel
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        settings={settings}
        onSave={setSettings}
      />

      <ShortcutsHelp
        isOpen={shortcutsOpen}
        onClose={() => setShortcutsOpen(false)}
        shortcuts={shortcuts}
      />
    </>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <AppContent />
    </ErrorBoundary>
  );
}