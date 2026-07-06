// API 请求客户端：统一处理后端 baseURL、fallback 地址、拦截器和错误消息。
import axios from 'axios'

const fallbackBaseURL = import.meta.env.VITE_API_FALLBACK_URL || ''

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

request.interceptors.response.use(
  (res) => res.data,
  async (err) => {
    const canRetryFallback = !!fallbackBaseURL
      && !err.config?._retryFallback
      && err.config?.baseURL === '/api'
      && (err.code === 'ERR_NETWORK' || !err.response || err.response?.status === 404)

    if (canRetryFallback) {
      err.config._retryFallback = true
      err.config.baseURL = fallbackBaseURL
      try {
        return await request.request(err.config)
      } catch (fallbackError) {
        err = fallbackError
      }
    }

    const msg = err.code === 'ERR_NETWORK'
      ? '无法连接后端服务，请确认后端已启动，默认端口 8000 可访问'
      : err.response?.data?.detail || err.message || '请求失败'
    console.error('API Error:', msg)
    const errorObj = new Error(msg)
    errorObj.response = err.response
    return Promise.reject(errorObj)
  },
)

export default request
