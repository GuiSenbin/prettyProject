import axios from 'axios'

const fallbackBaseURL = import.meta.env.VITE_API_FALLBACK_URL || 'http://localhost:8001/api'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// 响应拦截
api.interceptors.response.use(
  (res) => res.data,
  async (err) => {
    const canRetryFallback = !err.config?._retryFallback
      && err.config?.baseURL === '/api'
      && (err.code === 'ERR_NETWORK' || !err.response || err.response?.status === 404)

    if (canRetryFallback) {
      err.config._retryFallback = true
      err.config.baseURL = fallbackBaseURL
      try {
        return await api.request(err.config)
      } catch (fallbackError) {
        err = fallbackError
      }
    }

    const msg = err.code === 'ERR_NETWORK'
      ? '无法连接后端服务，请确认后端已启动，默认端口 8000 或备用端口 8001 可访问'
      : err.response?.data?.detail || err.message || '请求失败'
    console.error('API Error:', msg)
    return Promise.reject(new Error(msg))
  },
)

export default api
