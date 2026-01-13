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

export enum QueueItemStatus {
  PENDING = 'pending',
  UPLOADING = 'uploading',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export interface QueueItem {
  id: string;
  name: string;
  status: QueueItemStatus | 'pending' | 'uploading' | 'completed' | 'failed';
}

export interface EngineConfig {
  dropName: string;
  designCount: number;
  blueprintId: number;
  providerId: number;
  batchList: string;
}

export interface EditorState {
  scale: number;
  translateX: number;
  translateY: number;
}

export interface PromptData {
  prompt: string;
  title: string;
  tags: string[];
  description: string;
}

export interface SavedImageData {
  id: string;
  url: string;
  prompt: string;
}

export interface ProductResult {
  platform: string;
  productId: string;
  url: string;
  type: 'tshirt' | 'hoodie';
}