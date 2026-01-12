import React, { useState, useEffect, useCallback } from 'react';
import { Wifi, WifiOff, Loader2, Cloud } from 'lucide-react';
import { ComfyUIService } from '../services/comfyui';
import { config } from '../services/config';
import { TIMEOUTS } from '../constants/timings';

interface ConnectionStatusProps {
  comfyService: ComfyUIService | null;
}

export function ConnectionStatus({ comfyService }: ConnectionStatusProps) {
  const [status, setStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  const checkConnection = useCallback(async () => {
    if (!comfyService) {
      setStatus('disconnected');
      return;
    }

    setStatus('checking');
    const isHealthy = await comfyService.healthCheck();
    setStatus(isHealthy ? 'connected' : 'disconnected');
    setLastCheck(new Date());
  }, [comfyService]);

  useEffect(() => {
    checkConnection();

    // Check every 30 seconds
    const interval = setInterval(checkConnection, TIMEOUTS.CONNECTION_CHECK_INTERVAL);

    return () => clearInterval(interval);
  }, [checkConnection]);

  const getStatusColor = () => {
    switch (status) {
      case 'connected': return 'bg-emerald-500';
      case 'disconnected': return 'bg-red-500';
      case 'checking': return 'bg-yellow-500';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'connected': return 'Connected';
      case 'disconnected': return 'Disconnected';
      case 'checking': return 'Checking...';
    }
  };

  const getIcon = () => {
    if (status === 'checking') return <Loader2 className="animate-spin" size={14} />;
    if (status === 'connected') return config.runpod.isRunPod ? <Cloud size={14} /> : <Wifi size={14} />;
    return <WifiOff size={14} />;
  };

  return (
    <div className="flex items-center gap-2 px-3 py-2 bg-slate-800/50 rounded-lg border border-slate-700">
      <div className={`w-2 h-2 rounded-full ${getStatusColor()} ${status === 'checking' ? 'animate-pulse' : ''}`}></div>
      <div className="flex items-center gap-2 text-xs">
        {getIcon()}
        <span className="font-medium">{getStatusText()}</span>
        {config.runpod.isRunPod && status === 'connected' && (
          <span className="text-slate-500">RunPod</span>
        )}
      </div>
      {lastCheck && status !== 'checking' && (
        <button
          onClick={checkConnection}
          className="ml-2 text-xs text-slate-500 hover:text-slate-300 transition-colors"
        >
          Retry
        </button>
      )}
    </div>
  );
}
