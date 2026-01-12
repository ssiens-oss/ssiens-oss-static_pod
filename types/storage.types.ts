/**
 * Storage Service Types
 */

export interface ImageMetadata {
  prompt?: string;
  title?: string;
  tags?: string[];
  description?: string;
  dropName?: string;
  designId?: string;
  generatedAt?: string;
  comfyuiPromptId?: string;
  [key: string]: unknown; // Allow additional custom fields
}

export interface SavedImage {
  id: string;
  filename: string;
  path: string;
  url: string;
  hash: string;
  size: number;
  timestamp: Date;
  metadata?: ImageMetadata;
}

export interface StorageConfig {
  type: 'local' | 's3' | 'gcs';
  basePath: string;
  s3Config?: S3Config;
  gcsConfig?: GCSConfig;
}

export interface S3Config {
  bucket: string;
  region: string;
  accessKeyId: string;
  secretAccessKey: string;
}

export interface GCSConfig {
  bucket: string;
  projectId: string;
  keyFilename: string;
}
