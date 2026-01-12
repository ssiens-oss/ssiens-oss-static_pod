/**
 * ComfyUI Service Types
 */

export interface ComfyUIConfig {
  apiUrl: string;
  outputDir: string;
  timeout?: number;
}

export interface ComfyUIWorkflow {
  prompt: string;
  workflow?: string;
  seed?: number;
  width?: number;
  height?: number;
  steps?: number;
  cfg_scale?: number;
}

export interface GenerationResult {
  images: string[];
  promptId: string;
  status: 'completed' | 'failed';
  error?: string;
}

export interface ComfyUIWorkflowJson {
  [nodeId: string]: ComfyUINode;
}

export interface ComfyUINode {
  inputs: Record<string, unknown>;
  class_type: string;
}

export interface ComfyUIProgressEvent {
  type: 'progress' | 'executing' | 'executed' | 'execution_error';
  data?: {
    node?: string;
    prompt_id?: string;
    value?: number;
    max?: number;
  };
}

export interface ComfyUIHistoryResponse {
  [promptId: string]: {
    status?: {
      completed?: boolean;
      status_str?: string;
    };
    outputs?: {
      [nodeId: string]: {
        images?: Array<{
          filename: string;
          subfolder?: string;
          type: string;
        }>;
      };
    };
  };
}
