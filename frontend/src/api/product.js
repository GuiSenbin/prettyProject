// 产品库 API：封装本地主库搜索、个人产品库和轻量图片识别入口。
import request from '@/utils/request'

export const productApi = {
  getProductDetail(productId) {
    return request.get(`/products/${productId}`)
  },

  listMyProducts() {
    return request.get('/products/my')
  },

  addMyProduct(payload) {
    return request.post('/products/my', payload)
  },

  deleteMyProduct(userProductId) {
    return request.delete(`/products/my/${userProductId}`)
  },

  analyzeProduct(productId) {
    return request.get(`/products/${productId}/analysis`)
  },
  searchProducts(q = '', page = 1, size = 12) {
    return request.get('/products/search', { params: { q, page, size } })
  },
}
