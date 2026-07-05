// 用户 API：封装纯净版基础身份的读取、创建、更新和删除接口。
import request from '@/utils/request'

export const userApi = {
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
