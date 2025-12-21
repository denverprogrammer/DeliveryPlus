import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    root: path.resolve(__dirname, '.'),
    build: {
        outDir: '/staticfiles/imagereview',
        emptyOutDir: true,
    },
    server: {
        host: true,
        port: 3002,
        allowedHosts: ['imagereview.local'],
        proxy: {
            '/api/': {
                target: 'http://web:8000',
                changeOrigin: true,
            },
        },
    },
})

