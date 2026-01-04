import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist-podengine',
    rollupOptions: {
      input: {
        main: './pod-engine-index.html'
      }
    }
  },
  server: {
    port: 5174,
    open: true
  }
})
