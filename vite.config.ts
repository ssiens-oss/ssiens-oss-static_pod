import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, '.', '');
    return {
      server: {
        port: 3000,
        host: '0.0.0.0',
      },
      plugins: [react()],
      define: {
        'import.meta.env.VITE_COMFYUI_API_URL': JSON.stringify(env.COMFYUI_API_URL || 'http://localhost:8188'),
        'import.meta.env.VITE_RUNPOD_POD_ID': JSON.stringify(env.RUNPOD_POD_ID || ''),
        'import.meta.env.VITE_ANTHROPIC_API_KEY': JSON.stringify(env.ANTHROPIC_API_KEY || ''),
        'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
        'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY)
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      }
    };
});
