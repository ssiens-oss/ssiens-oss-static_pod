import React from 'react';
import { PipelineStatus as PipelineStatusType } from '../types';
import { CheckCircle2, Loader2, AlertCircle, Circle } from 'lucide-react';

interface PipelineStatusProps {
  status: PipelineStatusType;
}

export const PipelineStatus: React.FC<PipelineStatusProps> = ({ status }) => {
  const getStatusIcon = (state: string) => {
    switch (state) {
      case 'completed':
        return <CheckCircle2 size={18} className="text-emerald-500" />;
      case 'processing':
        return <Loader2 size={18} className="animate-spin text-blue-400" />;
      case 'failed':
        return <AlertCircle size={18} className="text-red-500" />;
      default:
        return <Circle size={18} className="text-slate-600" />;
    }
  };

  const getStatusColor = (state: string) => {
    switch (state) {
      case 'completed':
        return 'text-emerald-400';
      case 'processing':
        return 'text-blue-400';
      case 'failed':
        return 'text-red-400';
      default:
        return 'text-slate-500';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
      <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
        Pipeline Status
      </div>
      <div className="space-y-3">
        {/* Printify */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon(status.printify)}
            <span className={`text-sm font-medium ${getStatusColor(status.printify)}`}>
              Printify
            </span>
          </div>
          <span className="text-xs text-slate-600 uppercase">{status.printify}</span>
        </div>

        {/* Connector Line */}
        <div className="flex items-center gap-2 pl-2">
          <div className="w-px h-4 bg-slate-700"></div>
        </div>

        {/* Shopify */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon(status.shopify)}
            <span className={`text-sm font-medium ${getStatusColor(status.shopify)}`}>
              Shopify
            </span>
          </div>
          <span className="text-xs text-slate-600 uppercase">{status.shopify}</span>
        </div>

        {/* Connector Line */}
        <div className="flex items-center gap-2 pl-2">
          <div className="w-px h-4 bg-slate-700"></div>
        </div>

        {/* TikTok */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon(status.tiktok)}
            <span className={`text-sm font-medium ${getStatusColor(status.tiktok)}`}>
              TikTok Shop
            </span>
          </div>
          <span className="text-xs text-slate-600 uppercase">{status.tiktok}</span>
        </div>
      </div>
    </div>
  );
};
