import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Docker 환경 감지: 환경변수 또는 기본값 사용
const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://ml-service:8000'
const USER_SERVICE_URL = process.env.USER_SERVICE_URL || 'http://user-service:8080'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    host: '0.0.0.0',
    proxy: {
      // ML Service API - 모든 /api/admin 경로
      '/api/admin': {
        target: ML_SERVICE_URL,
        changeOrigin: true,
      },
      '/api/ai': {
        target: ML_SERVICE_URL,
        changeOrigin: true,
      },
      // User Service API
      '/api/auth': {
        target: USER_SERVICE_URL,
        changeOrigin: true,
      }
    }
  }
})

