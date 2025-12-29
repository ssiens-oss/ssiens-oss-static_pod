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
}

export interface EditorState {
  scale: number;
  translateX: number;
  translateY: number;
}

export interface ApiCredentials {
  printifyApiKey: string;
  printifyShopId: string;
  shopifyStoreName: string;
  shopifyAccessToken: string;
  tiktokAppKey: string;
  tiktokAppSecret: string;
  tiktokShopId: string;
}

export interface PipelineStatus {
  printify: 'pending' | 'processing' | 'completed' | 'failed';
  shopify: 'pending' | 'processing' | 'completed' | 'failed';
  tiktok: 'pending' | 'processing' | 'completed' | 'failed';
}

export interface PublishResult {
  platform: 'printify' | 'shopify' | 'tiktok';
  productId?: string;
  productUrl?: string;
  status: 'success' | 'failed';
  message: string;
}