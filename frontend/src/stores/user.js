import { defineStore } from 'pinia'
import { userApi } from '@/api/user'

const SESSION_KEY = 'beauty_login_session'

function loadSession() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY) || 'null')
  } catch {
    localStorage.removeItem(SESSION_KEY)
    return null
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    session: loadSession(),
    loading: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.session?.token,
    displayPhone: (state) => state.session?.phone || '',
    displayName: (state) => state.session?.name || '智颜用户',
  },

  actions: {
    async login(username, password) {
      this.loading = true
      try {
        let user
        try {
          // 1. 尝试以账号密码登录
          user = await userApi.login({ username, password })
        } catch (err) {
          // 2. 如果账号不存在 (401 且含有账号不存在关键字)，则为用户提供静默注册体验
          const detail = err.response?.data?.detail
          if (err.response?.status === 401 && detail && (detail.includes('不存在') || detail.includes('not exist'))) {
            // 静默创建新账户
            await userApi.register({ username, password, display_name: '智颜用户' })
            // 注册成功后重新登录
            user = await userApi.login({ username, password })
          } else {
            // 密码错误等其他异常，直接向上抛出
            throw err
          }
        }

        // 3. 登录成功，本地状态持久化
        this.session = {
          token: `token-${user.id}-${Date.now()}`,
          phone: user.phone || username,
          name: user.display_name || '智颜用户',
          createdAt: user.created_at || new Date().toISOString(),
        }
        localStorage.setItem(SESSION_KEY, JSON.stringify(this.session))
        return { ok: true }
      } catch (err) {
        const errorMsg = err.response?.data?.detail || '账号或密码错误，登录失败'
        return { ok: false, error: errorMsg }
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.session = null
      localStorage.removeItem(SESSION_KEY)
      return { ok: true }
    },

    async fetchLatest() {
      this.session = loadSession()
    },
  },
})
