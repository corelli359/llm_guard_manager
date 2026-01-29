import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // 支持子路径部署，通过环境变量配置
  // 开发环境: base: '/'
  // 生产环境: base: process.env.VITE_BASE_PATH || '/web-manager/'
  base: process.env.VITE_BASE_PATH || '/web-manager/',
  server: {
    proxy: {
      '/api': {
        // 支持 k8s 环境配置后端地址
        // 本地开发: http://127.0.0.1:9001
        // k8s 环境: http://backend:9001
        target: process.env.VITE_BACKEND_URL || 'http://127.0.0.1:9001',
        changeOrigin: true,
      }
    }
  }
})
