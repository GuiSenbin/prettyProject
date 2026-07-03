import { defineStore } from 'pinia'
import api from '@/api'

export const useChatStore = defineStore('chat', {
  state: () => ({
    sessionId: localStorage.getItem('miyang_session') || 'default',
    messages: [],
    loading: false,
  }),

  actions: {
    async loadHistory() {
      try {
        const data = await api.get(`/chat/history?session_id=${this.sessionId}`)
        this.messages = data
      } catch (e) {
        console.warn('加载历史失败', e)
      }
    },

    async send(text, userId, userProducts = []) {
      this.loading = true
      // 添加用户消息到本地
      this.messages.push({ role: 'user', content: text, id: Date.now() })

      try {
        const data = await api.post('/chat/', {
          message: text,
          user_id: userId,
          session_id: this.sessionId,
          user_products: userProducts,
        })
        this.messages.push({ role: 'assistant', content: data.reply, id: Date.now() + 1 })
        return { ok: true, reply: data.reply }
      } catch (e) {
        this.messages.push({
          role: 'assistant',
          content: '😅 抱歉，我暂时遇到了一些问题，请稍后再试。',
          id: Date.now() + 1,
        })
        return { ok: false, error: e.message }
      } finally {
        this.loading = false
      }
    },

    async newSession() {
      try {
        const data = await api.post('/chat/new-session')
        this.sessionId = data.session_id
      } catch {
        this.sessionId = 's' + Date.now()
      }
      localStorage.setItem('miyang_session', this.sessionId)
      this.messages = []
    },
  },
})
