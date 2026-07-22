// 个人档案 API：封装护肤档案读取与保存。
import request from '@/utils/request'

export const profileApi = {
  getProfile() {
    return request.get('/profiles/me')
  },

  saveProfile(payload) {
    return request.put('/profiles/me', payload)
  },
}
