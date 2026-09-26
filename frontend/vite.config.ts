import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, __dirname, 'VITE_')

  return {
    base: env.VITE_BASE_PATH ?? '/',
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      proxy: {
        '/api': 'http://localhost:8000',
        '/health': 'http://localhost:8000',
      },
    },
  }
})
