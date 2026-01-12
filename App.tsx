import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Terminal } from './components/Terminal';
import { AppHeader } from './components/AppHeader';
import { ConfigurationForm } from './components/ConfigurationForm';
import { ActionButtons } from './components/ActionButtons';
import { PrintifyQueue } from './components/PrintifyQueue';
import { PreviewPanel } from './components/PreviewPanel';
import { ProgressBar } from './components/ProgressBar';
import { runSimulation } from './services/mockEngine';
import { ComfyUIService } from './services/comfyui';
import { config } from './services/config';
import { generateShortId } from './utils/id';
import { LogEntry, LogType, QueueItem, EngineConfig, EditorState } from './types';

const INITIAL_EDITOR_STATE: EditorState = {
  scale: 1,
  translateX: 0,
  translateY: 0
};

export default function App() {
  // --- State ---
  const [engineConfig, setEngineConfig] = useState<EngineConfig>({
    dropName: 'Drop7',
    designCount: 10,
    blueprintId: 6,
    providerId: 1,
    batchList: ''
  });

  // ComfyUI Service
  const [comfyService, setComfyService] = useState<ComfyUIService | null>(null);

  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [queue, setQueue] = useState<QueueItem[]>([]);
  
  // Images
  const [designImage, setDesignImage] = useState<string | null>(null);
  const [mockupImage, setMockupImage] = useState<string | null>(null);

  // Editor State
  const [editorState, setEditorState] = useState<EditorState>(INITIAL_EDITOR_STATE);

  // Stop Signal
  const stopRef = useRef(false);

  // Initialize ComfyUI Service
  useEffect(() => {
    const service = new ComfyUIService({
      apiUrl: config.comfyui.apiUrl,
      outputDir: config.comfyui.outputDir,
      timeout: config.comfyui.timeout
    });
    setComfyService(service);

    addLog(`ComfyUI configured: ${config.comfyui.apiUrl}`, LogType.INFO);

    return () => {
      service.disconnectWebSocket();
    };
  }, []);

  // --- Handlers ---
  const addLog = useCallback((message: string, type: LogType = LogType.INFO) => {
    setLogs(prev => [...prev, {
      id: generateShortId('log'),
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
      ? engineConfig.batchList.split(',').map(d => d.trim()).filter(Boolean)
      : [engineConfig.dropName];

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
        <AppHeader comfyService={comfyService} />

        <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide">
          <ConfigurationForm config={engineConfig} onChange={setEngineConfig} disabled={isRunning} />
          <ActionButtons
            isRunning={isRunning}
            onRunSingle={() => handleRun(false)}
            onRunBatch={() => handleRun(true)}
          />
          <PrintifyQueue queue={queue} />
        </div>

        <ProgressBar progress={progress} />
      </div>

      {/* --- RIGHT CONTENT: Preview & Logs --- */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <PreviewPanel
          designImage={designImage}
          mockupImage={mockupImage}
          editorState={editorState}
          onZoom={handleZoom}
          onMove={handleMove}
          onSave={handleSaveEdit}
        />

        {/* Bottom Area: Logs */}
        <div className="h-64 p-4 border-t border-slate-800 bg-slate-900/30">
          <Terminal logs={logs} onClear={() => setLogs([])} />
        </div>
      </div>
    </div>
  );
}