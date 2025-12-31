import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Music Studio Vite Config
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist-music',
    rollupOptions: {
      input: {
        main: './music-index.html'
      }
    }
  },
  server: {
    port: 5174,
    proxy: {
      '/api/music': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/music/, '')
      }
    }
  }
});
