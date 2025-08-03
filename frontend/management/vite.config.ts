import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    root: path.resolve(__dirname, '.'),
    build: {
        outDir: '../../apps/staticfiles/management',
        emptyOutDir: false,
    },
    server: {
        host: true,
        allowedHosts: ['mgmt.local'],
        proxy: {
            '/api/': {
                target: 'http://web:8080',
                changeOrigin: true,
            },
            '/admin/': {
                target: 'http://web:8080',
                changeOrigin: true,
            },
        },
    },
}) 