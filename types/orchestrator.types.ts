/**
 * Orchestrator Service Types
 */

export interface PromptData {
  prompt: string;
  title: string;
  tags: string[];
  description: string;
  seed?: number;
}

export interface OrchestratorConfig {
  comfyui: {
    apiUrl: string;
    outputDir: string;
  };
  claude: {
    apiKey: string;
    model?: string;
  };
  storage: {
    type: 'local' | 's3' | 'gcs';
    basePath: string;
  };
  printify?: {
    apiKey: string;
    shopId: string;
  };
  shopify?: {
    storeUrl: string;
    accessToken: string;
  };
  tiktok?: {
    appKey: string;
    appSecret: string;
    shopId: string;
    accessToken: string;
  };
  etsy?: {
    apiKey: string;
    shopId: string;
    accessToken: string;
  };
  instagram?: {
    accessToken: string;
    businessAccountId: string;
  };
  facebook?: {
    pageId: string;
    accessToken: string;
    catalogId: string;
  };
  options?: {
    enabledPlatforms?: string[];
    autoPublish?: boolean;
    tshirtPrice?: number;
    hoodiePrice?: number;
  };
}

export interface PipelineOptions {
  dropName: string;
  designCount: number;
  autoPublish: boolean;
  platforms: string[];
}

export interface PipelineResult {
  success: boolean;
  designs: DesignResult[];
  errors: string[];
}

export interface DesignResult {
  id: string;
  imageUrl: string;
  productIds: Record<string, string>; // platform -> productId
  prompt: PromptData;
  status: 'completed' | 'failed';
  error?: string;
}
