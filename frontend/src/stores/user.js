import { defineStore } from 'pinia'
import api from '@/api'

const STORAGE_KEY = 'beauty_user_id'
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
    userId: null,
    profile: null,
    loading: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.session?.token,
    displayPhone: (state) => state.session?.phone || '',
    hasProfile: (state) => !!state.profile?.skin_type,
    summary: (state) => {
      if (!state.profile) return null
      const map = {
        skin_type: { dry: '干性肌肤', oily: '油性肌肤', combination: '混合性肌肤', normal: '中性肌肤', sensitive: '敏感性肌肤' },
        face_shape: { round: '圆脸', square: '方脸', oval: '鹅蛋脸', heart: '心形脸', diamond: '菱形脸' },
      }
      return {
        name: state.profile.name,
        skin_type: state.profile.skin_type,
        skin_type_label: map.skin_type[state.profile.skin_type] || '',
        face_shape: state.profile.face_shape,
        concerns: state.profile.concerns || [],
      }
    },
  },

  actions: {
    login(phone = '186****0905') {
      const normalizedPhone = phone || '186****0905'
      this.session = {
        token: `mock-${Date.now()}`,
        phone: normalizedPhone,
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
      const storedUserId = localStorage.getItem(STORAGE_KEY)
      if (!storedUserId) {
        this.profile = null
        this.userId = null
        return
      }

      this.loading = true
      try {
        const data = await api.get(`/users/${storedUserId}`)
        this.profile = data
        this.userId = data.id
      } catch (e) {
        console.warn('加载用户资料失败', e)
        localStorage.removeItem(STORAGE_KEY)
        this.profile = null
        this.userId = null
      } finally {
        this.loading = false
      }
    },

    async save(form) {
      const payload = {
        name: form.name || '用户',
        age: form.age || '',
        gender: form.gender || '',
        skin_type: form.skin_type || '',
        face_shape: form.face_shape || '',
        skin_tone: form.skin_tone || '',
        concerns: form.concerns || [],
      }
      try {
        const data = this.userId
          ? await api.put(`/users/${this.userId}`, payload)
          : await api.post('/users/', payload)
        this.profile = data
        this.userId = data.id
        localStorage.setItem(STORAGE_KEY, String(data.id))
        return { ok: true }
      } catch (e) {
        if (this.userId) {
          try {
            const data = await api.post('/users/', payload)
            this.profile = data
            this.userId = data.id
            localStorage.setItem(STORAGE_KEY, String(data.id))
            return { ok: true }
          } catch (retryError) {
            return { ok: false, error: retryError.message }
          }
        }
        return { ok: false, error: e.message }
      }
    },

    async reset() {
      if (!this.userId) return { ok: true }
      try {
        await api.delete(`/users/${this.userId}`)
        this.profile = null
        this.userId = null
        localStorage.removeItem(STORAGE_KEY)
        return { ok: true }
      } catch (e) {
        return { ok: false, error: e.message }
      }
    },
  },
})
