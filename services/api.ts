interface ApiConfig {
  baseUrl: string;
  apiKey?: string;
  timeout: number;
}

interface GenerateDesignRequest {
  prompt: string;
  dropName: string;
  blueprintId: number;
  style?: string;
}

interface GenerateDesignResponse {
  designUrl: string;
  mockupUrl: string;
  designId: string;
}

interface UploadToProviderRequest {
  designUrl: string;
  mockupUrl: string;
  dropName: string;
  providerId: number;
  blueprintId: number;
}

interface UploadToProviderResponse {
  productId: string;
  status: 'success' | 'failed';
  message: string;
}

class ApiService {
  private config: ApiConfig;

  constructor(config?: Partial<ApiConfig>) {
    this.config = {
      baseUrl: config?.baseUrl || '/api',
      apiKey: config?.apiKey || import.meta.env.VITE_API_KEY,
      timeout: config?.timeout || 30000,
    };
  }

  private async fetchWithTimeout(url: string, options: RequestInit, timeout: number): Promise<Response> {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(id);
      return response;
    } catch (error) {
      clearTimeout(id);
      throw error;
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.config.baseUrl}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.config.apiKey) {
      headers['Authorization'] = `Bearer ${this.config.apiKey}`;
    }

    try {
      const response = await this.fetchWithTimeout(
        url,
        {
          ...options,
          headers,
        },
        this.config.timeout
      );

      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: 'Unknown error' }));
        throw new Error(error.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Request timeout - please try again');
        }
        throw error;
      }
      throw new Error('An unexpected error occurred');
    }
  }

  async generateDesign(request: GenerateDesignRequest): Promise<GenerateDesignResponse> {
    return this.request<GenerateDesignResponse>('/design/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async uploadToProvider(request: UploadToProviderRequest): Promise<UploadToProviderResponse> {
    return this.request<UploadToProviderResponse>('/provider/upload', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getProviders(): Promise<{ id: number; name: string }[]> {
    return this.request<{ id: number; name: string }[]>('/providers');
  }

  async getBlueprints(): Promise<{ id: number; name: string; category: string }[]> {
    return this.request<{ id: number; name: string; category: string }[]>('/blueprints');
  }

  async healthCheck(): Promise<{ status: 'ok' | 'error'; message: string }> {
    return this.request<{ status: 'ok' | 'error'; message: string }>('/health');
  }
}

// Create singleton instance
export const apiService = new ApiService();

// Export types
export type {
  GenerateDesignRequest,
  GenerateDesignResponse,
  UploadToProviderRequest,
  UploadToProviderResponse,
};
