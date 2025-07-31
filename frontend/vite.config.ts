import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '/build/react',
    emptyOutDir: false,
  },
  server: {
    host: true,
    allowedHosts: ['deliveryplus.local', 'mgmt.local'],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/mgmt': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/tracking': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
