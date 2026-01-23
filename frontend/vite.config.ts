import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // 支持子路径部署，通过环境变量配置
  // 开发环境: base: '/'
  // 生产环境: base: process.env.VITE_BASE_PATH || '/'
  base: process.env.VITE_BASE_PATH || '/',
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:9001',
        changeOrigin: true,
      }
    }
  }
})
