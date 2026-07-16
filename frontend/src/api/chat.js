// AI 问答 API：封装多会话、消息发送、历史、重命名和删除。
import request from '@/utils/request'

export const chatApi = {
  listSessions() {
    return request.get('/chat/sessions')
  },

  getSession(sessionId) {
    return request.get(`/chat/sessions/${sessionId}`)
  },

  sendMessage(payload) {
    return request.post('/chat/messages', payload)
  },

  renameSession(sessionId, title) {
    return request.patch(`/chat/sessions/${sessionId}`, { title })
  },

  deleteSession(sessionId) {
    return request.delete(`/chat/sessions/${sessionId}`)
  },
}
