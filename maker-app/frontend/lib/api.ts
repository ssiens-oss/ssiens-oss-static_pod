/**
 * API Client for StaticWaves Maker
 * Handles all backend and Printify API calls
 */

import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const PRINTIFY_API_URL = 'https://api.printify.com/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ==================== MAKER API ====================

export interface GenerateRequest {
  prompt: string;
  style?: string;
  output_format?: string;
}

export interface GenerateResponse {
  job_id: number;
  status: string;
  tokens_used: number;
  estimated_completion: number;
}

export interface Job {
  job_id: number;
  type: string;
  status: string;
  output_url?: string;
  output_format?: string;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

export const makerAPI = {
  // Generate content
  generateImage: (req: GenerateRequest) =>
    api.post<GenerateResponse>('/maker/generate/image', req),

  generateVideo: (req: GenerateRequest) =>
    api.post<GenerateResponse>('/maker/generate/video', req),

  generateMusic: (req: GenerateRequest) =>
    api.post<GenerateResponse>('/maker/generate/music', req),

  generateBook: (req: GenerateRequest) =>
    api.post<GenerateResponse>('/maker/generate/book', req),

  // Get job status
  getJob: (jobId: number) =>
    api.get<Job>(`/maker/job/${jobId}`),

  // Get queue
  getQueue: (limit = 20) =>
    api.get<{ jobs: Job[] }>(`/maker/queue?limit=${limit}`),
};

// ==================== BILLING API ====================

export interface Subscription {
  tier: string;
  status: string;
  monthly_tokens: number;
  current_period_end?: string;
}

export const billingAPI = {
  // Subscribe
  subscribe: (tier: string) =>
    api.post<{ checkout_url: string }>('/billing/subscribe', { tier }),

  // Buy tokens
  buyTokens: (pack: string) =>
    api.post<{ checkout_url: string }>('/billing/buy-tokens', { pack }),

  // Get subscription
  getSubscription: () =>
    api.get<Subscription>('/billing/subscription'),

  // Cancel subscription
  cancelSubscription: () =>
    api.post('/billing/cancel-subscription'),
};

// ==================== REWARDS API ====================

export interface TokenBalance {
  balance: number;
  total_earned: number;
  total_spent: number;
  last_updated: string;
}

export interface AdAvailability {
  available: boolean;
  watched_today: number;
  limit: number;
  remaining: number;
}

export const rewardsAPI = {
  // Complete ad
  completeAd: (adNetwork: string, adUnitId: string) =>
    api.post('/rewards/ad-complete', { ad_network: adNetwork, ad_unit_id: adUnitId }),

  // Get balance
  getBalance: () =>
    api.get<TokenBalance>('/rewards/balance'),

  // Check ad availability
  getAdAvailability: () =>
    api.get<AdAvailability>('/rewards/ad-availability'),
};

// ==================== LIBRARY API ====================

export interface LibraryItem {
  id: number;
  job_id: number;
  title: string;
  type: string;
  output_url: string;
  output_format: string;
  favorited: boolean;
  downloads: number;
  created_at: string;
}

export const libraryAPI = {
  // Get library
  getLibrary: (limit = 50, offset = 0) =>
    api.get<{ items: LibraryItem[]; total: number }>(`/library/?limit=${limit}&offset=${offset}`),

  // Save to library
  save: (jobId: number, title?: string) =>
    api.post('/library/save', { job_id: jobId, title }),

  // Toggle favorite
  toggleFavorite: (itemId: number) =>
    api.post(`/library/${itemId}/favorite`),

  // Delete
  delete: (itemId: number) =>
    api.delete(`/library/${itemId}`),

  // Track download
  trackDownload: (itemId: number) =>
    api.post(`/library/${itemId}/download`),
};

// ==================== PRINTIFY API ====================

const printifyAPI = axios.create({
  baseURL: PRINTIFY_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add Printify auth token
printifyAPI.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('printify_token') : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface PrintifyShop {
  id: number;
  title: string;
}

export interface PrintifyBlueprint {
  id: number;
  title: string;
  description: string;
  brand: string;
  model: string;
  images: string[];
}

export interface PrintifyProduct {
  id: string;
  title: string;
  description: string;
  tags: string[];
  images: Array<{ src: string }>;
  variants: Array<{
    id: number;
    price: number;
    is_enabled: boolean;
  }>;
  is_locked: boolean;
}

export interface CreateProductRequest {
  title: string;
  description: string;
  blueprint_id: number;
  print_provider_id: number;
  variants: Array<{
    id: number;
    price: number;
    is_enabled: boolean;
  }>;
  print_areas: Array<{
    variant_ids: number[];
    placeholders: Array<{
      position: string;
      images: Array<{
        id: string;
        x: number;
        y: number;
        scale: number;
        angle: number;
      }>;
    }>;
  }>;
}

export const printify = {
  // Get shops
  getShops: () =>
    printifyAPI.get<PrintifyShop[]>('/shops.json'),

  // Get blueprints (product templates)
  getBlueprints: () =>
    printifyAPI.get<PrintifyBlueprint[]>('/catalog/blueprints.json'),

  // Get blueprint by ID
  getBlueprint: (id: number) =>
    printifyAPI.get<PrintifyBlueprint>(`/catalog/blueprints/${id}.json`),

  // Upload image
  uploadImage: (shopId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return printifyAPI.post(`/shops/${shopId}/uploads/images.json`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Upload image from URL
  uploadImageFromUrl: (shopId: number, url: string, fileName: string) =>
    printifyAPI.post(`/shops/${shopId}/uploads/images.json`, {
      file_name: fileName,
      url: url,
    }),

  // Create product
  createProduct: (shopId: number, product: CreateProductRequest) =>
    printifyAPI.post<PrintifyProduct>(`/shops/${shopId}/products.json`, product),

  // Get products
  getProducts: (shopId: number, page = 1, limit = 100) =>
    printifyAPI.get<{ data: PrintifyProduct[] }>(`/shops/${shopId}/products.json?page=${page}&limit=${limit}`),

  // Publish product
  publishProduct: (shopId: number, productId: string) =>
    printifyAPI.post(`/shops/${shopId}/products/${productId}/publish.json`, {
      title: true,
      description: true,
      images: true,
      variants: true,
      tags: true,
    }),

  // Delete product
  deleteProduct: (shopId: number, productId: string) =>
    printifyAPI.delete(`/shops/${shopId}/products/${productId}.json`),
};

export default api;
