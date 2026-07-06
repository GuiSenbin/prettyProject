// 用户 API：封装企业级账号注册、登录以及基础 CRUD。
import request from '@/utils/request'

export const userApi = {
  login(payload) {
    return request.post('/users/login', payload)
  },

  register(payload) {
    return request.post('/users/register', payload)
  },

  getUser(id) {
    return request.get(`/users/${id}`)
  },

  createUser(payload) {
    return request.post('/users/', payload)
  },

  updateUser(id, payload) {
    return request.put(`/users/${id}`, payload)
  },

  deleteUser(id) {
    return request.delete(`/users/${id}`)
  },
}
