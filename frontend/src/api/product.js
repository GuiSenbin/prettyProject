// 产品库 API：封装本地主库搜索、个人产品库和轻量图片识别入口。
import request from '@/utils/request'

export const productApi = {
  getProductDetail(productId, userId) {
    return request.get(`/products/${productId}`, { params: { user_id: userId } })
  },

  listMyProducts(userId) {
    return request.get(`/products/my/${userId}`)
  },

  addMyProduct(userId, payload) {
    return request.post(`/products/my/${userId}`, payload)
  },

  deleteMyProduct(userId, userProductId) {
    return request.delete(`/products/my/${userId}/${userProductId}`)
  },

  analyzeProduct(productId, userId) {
    return request.get(`/products/${productId}/analysis`, { params: { user_id: userId } })
  },
  searchProducts(q = '', page = 1, size = 12) {
    return request.get('/products/search', { params: { q, page, size } })
  },
}
