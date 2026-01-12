import React from 'react';
import { Box, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { QueueItem } from '../types';

interface PrintifyQueueProps {
  queue: QueueItem[];
}

export function PrintifyQueue({ queue }: PrintifyQueueProps) {
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Printify Queue
        </label>
        <span className="text-xs bg-slate-800 px-2 py-0.5 rounded-full text-slate-400">
          {queue.length}
        </span>
      </div>
      <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden min-h-[150px]">
        {queue.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-36 text-slate-600">
            <Box size={24} className="mb-2 opacity-50" />
            <span className="text-xs">Queue is empty</span>
          </div>
        ) : (
          <ul className="divide-y divide-slate-800">
            {queue.map(item => (
              <li key={item.id} className="px-3 py-2 flex items-center justify-between text-sm">
                <span className="truncate max-w-[140px] text-slate-300">{item.name}</span>
                <div className="flex items-center gap-2">
                  {item.status === 'pending' && <span className="text-xs text-slate-500">Wait</span>}
                  {item.status === 'uploading' && <Loader2 size={14} className="animate-spin text-blue-400" />}
                  {item.status === 'completed' && <CheckCircle2 size={14} className="text-emerald-500" />}
                  {item.status === 'failed' && <AlertCircle size={14} className="text-red-500" />}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
