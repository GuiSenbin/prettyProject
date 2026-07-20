// AI 问答状态：管理当前会话、历史会话和消息流。
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { chatApi } from '@/api/chat'

export const useChatStore = defineStore('chat', () => {
  const sessions = ref([])
  const currentSession = ref(null)
  const messages = ref([])
  const loadingSessions = ref(false)
  const loadingMessages = ref(false)
  const sending = ref(false)
  const showGuide = ref(true)

  const currentSessionId = computed(() => currentSession.value?.id || null)

  function startNewTopic() {
    currentSession.value = null
    messages.value = []
    showGuide.value = true
  }

  async function fetchSessions(userId) {
    if (!userId) return
    loadingSessions.value = true
    try {
      sessions.value = await chatApi.listSessions() || []
    } finally {
      loadingSessions.value = false
    }
  }

  async function openSession(userId, sessionId) {
    if (!userId || !sessionId) return
    loadingMessages.value = true
    try {
      const detail = await chatApi.getSession(sessionId)
      currentSession.value = detail.session
      messages.value = detail.messages || []
      showGuide.value = false
      await fetchSessions(userId)
    } finally {
      loadingMessages.value = false
    }
  }

  async function sendMessage(userId, text) {
    const message = text.trim()
    if (!userId || !message || sending.value) return null
    const createdAt = new Date().toISOString()
    const userMessage = {
      id: `local-${Date.now()}`,
      role: 'user',
      content_text: message,
      structured_payload: null,
      created_at: createdAt,
      local: true,
    }
    const thinkingMessage = {
      id: `thinking-${Date.now()}`,
      role: 'assistant',
      content_text: '小蜜正在结合你的档案和产品库思考',
      structured_payload: null,
      created_at: createdAt,
      loading: true,
    }
    messages.value.push(userMessage, thinkingMessage)
    sending.value = true
    try {
      const result = await chatApi.sendMessage({
        session_id: currentSessionId.value,
        message,
      })
      currentSession.value = result.session
      messages.value = messages.value.filter(item => item.id !== userMessage.id && item.id !== thinkingMessage.id)
      messages.value.push(result.user_message, result.message)
      await fetchSessions(userId)
      return result
    } catch (err) {
      messages.value = messages.value.map(item => {
        if (item.id !== thinkingMessage.id) return item
        return {
          ...item,
          loading: false,
          error: true,
          content_text: '这次没有连接成功，可以再发一次。',
        }
      })
      throw err
    } finally {
      sending.value = false
    }
  }

  async function renameSession(userId, sessionId, title) {
    const updated = await chatApi.renameSession(sessionId, title)
    sessions.value = sessions.value.map(item => item.id === sessionId ? updated : item)
    if (currentSession.value?.id === sessionId) {
      currentSession.value = updated
    }
    return updated
  }

  async function deleteSession(userId, sessionId) {
    await chatApi.deleteSession(sessionId)
    sessions.value = sessions.value.filter(item => item.id !== sessionId)
    if (currentSession.value?.id === sessionId) {
      startNewTopic()
    }
  }

  return {
    sessions,
    currentSession,
    messages,
    loadingSessions,
    loadingMessages,
    sending,
    showGuide,
    currentSessionId,
    startNewTopic,
    fetchSessions,
    openSession,
    sendMessage,
    renameSession,
    deleteSession,
  }
})
