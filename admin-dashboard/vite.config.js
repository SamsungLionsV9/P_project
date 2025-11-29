import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,  // 관리자 대시보드는 3001 (Flutter 앱은 3000 사용)
    proxy: {
      // ML Service API (포트 8000) - 더 구체적인 경로 먼저
      '/api/admin/dashboard-stats': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api/admin/daily-requests': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api/admin/vehicle-stats': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api/admin/vehicles': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api/admin/vehicle': {  // 차량 상세정보 (옵션, 사고이력)
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api/admin/history': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api/admin/ai-logs': {  // AI 로그 (네고 대본 생성 기록)
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // User Service API (포트 8080)
      '/api/admin': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/api/auth': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      }
    }
  }
})

