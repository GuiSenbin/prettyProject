import { defineStore } from 'pinia'
import { userApi } from '@/api/user'

const SESSION_KEY = 'beauty_login_session'

function loadSession() {
  try {
    const session = JSON.parse(localStorage.getItem(SESSION_KEY) || 'null')
    if (session?.token && !session.userId) {
      const tokenParts = session.token.split('-')
      if (tokenParts.length > 2) {
        session.userId = tokenParts.slice(1, -1).join('-')
        localStorage.setItem(SESSION_KEY, JSON.stringify(session))
      }
    }
    return session
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
    userId: (state) => state.session?.userId || '',
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
          // 2. 如果账号不存在 (404)，则为用户提供静默注册体验
          const detail = err.response?.data?.detail
          if (err.response?.status === 404) {
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
          userId: user.id,
          phone: user.phone || '',
          name: user.display_name || '智颜用户',
          avatar_url: user.avatar_url || '',
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

    saveSession() {
      if (this.session) {
        localStorage.setItem(SESSION_KEY, JSON.stringify(this.session))
      }
    },
  },
})
