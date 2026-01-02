import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs';

export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: [
          ['@babel/plugin-transform-react-jsx', { runtime: 'automatic' }],
        ],
      },
    }),
    {
      name: 'importmap-script',
      transformIndexHtml: {
        order: 'pre',
        handler(html) {
          const importMapScript = fs.readFileSync('./pod-index.html', 'utf-8').match(/<script type="importmap">[\s\S]*?<\/script>/)?.[0] || '';
          return html.replace('<head>', `<head>${importMapScript}`);
        }
      }
    }
  ],
  build: {
    outDir: 'dist-pod',
    rollupOptions: {
      input: {
        main: './pod-index.html'
      }
    }
  },
  server: {
    port: 5174,
    open: true
  }
});
