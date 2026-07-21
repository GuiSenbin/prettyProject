import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiProxyTarget = env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:8000'
  const proxyErrorHandler = (proxy) => {
    proxy.on('error', (_err, _req, res) => {
      if (res.headersSent) return
      res.writeHead(503, { 'Content-Type': 'application/json; charset=utf-8' })
      res.end(JSON.stringify({ detail: '无法连接后端服务，请确认后端已启动' }))
    })
  }

  return {
    plugins: [vue()],
    assetsInclude: ['**/*.JPG'],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    css: {
      preprocessorOptions: {
        scss: {
          api: 'modern',
          additionalData: `@use "@/assets/styles/_variables.scss" as *;`,
        },
      },
    },
    server: {
      port: 6688,
      proxy: {
        '/api': {
          target: apiProxyTarget,
          changeOrigin: true,
          configure: proxyErrorHandler,
        },
        '/static': {
          target: apiProxyTarget,
          changeOrigin: true,
          configure: proxyErrorHandler,
        },
      },
    },
  }
})
