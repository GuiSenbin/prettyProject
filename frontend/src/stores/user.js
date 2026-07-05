// 用户状态：管理纯净版 App 的本地登录会话。
import { defineStore } from 'pinia'

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
    login(phone = '186****0905') {
      const normalizedPhone = phone || '186****0905'
      this.session = {
        token: `local-${Date.now()}`,
        phone: normalizedPhone,
        name: normalizedPhone.includes('用户') ? normalizedPhone : '智颜用户',
        createdAt: new Date().toISOString(),
      }
      localStorage.setItem(SESSION_KEY, JSON.stringify(this.session))
      return { ok: true }
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
