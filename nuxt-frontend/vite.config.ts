import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: process.env.API_BASE_URL || 'http://localhost:8001',
        changeOrigin: true,
        secure: false
      },
      '/docs': {
        target: process.env.API_BASE_URL || 'http://localhost:8001',
        changeOrigin: true,
        secure: false
      },
      '/openapi.json': {
        target: process.env.API_BASE_URL || 'http://localhost:8001',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'static',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'http-vendor': ['axios']
        }
      }
    }
  }
})
