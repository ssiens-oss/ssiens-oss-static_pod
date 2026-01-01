export enum LogType {
  INFO = 'INFO',
  SUCCESS = 'SUCCESS',
  WARNING = 'WARNING',
  ERROR = 'ERROR'
}

export interface LogEntry {
  id: string;
  timestamp: string;
  message: string;
  type: LogType;
}

export interface QueueItem {
  id: string;
  name: string;
  status: 'pending' | 'uploading' | 'completed' | 'failed';
}

export interface EngineConfig {
  dropName: string;
  designCount: number;
  blueprintId: number;
  providerId: number;
  batchList: string;
  useClaudePrompts?: boolean;
  customPrompt?: string;
  theme?: string;
  style?: string;
}

export interface EditorState {
  scale: number;
  translateX: number;
  translateY: number;
}