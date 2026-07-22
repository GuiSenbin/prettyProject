// 用户 API：封装企业级账号注册、登录以及基础 CRUD。
import request from '@/utils/request'

export const userApi = {
  login(payload) {
    return request.post('/users/login', payload)
  },

  register(payload) {
    return request.post('/users/register', payload)
  },

  getUser() {
    return request.get('/users/me')
  },

  createUser(payload) {
    return request.post('/users/', payload)
  },

  updateUser(payload) {
    return request.put('/users/me', payload)
  },

  deleteUser() {
    return request.delete('/users/me')
  },

  uploadAvatar(file) {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/users/me/avatar', formData)
  },
}
