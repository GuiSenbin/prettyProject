// 产品库页面状态：在产品库和详情页之间保留搜索、分页和滚动位置。
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useProductStore = defineStore('product', () => {
  const query = ref('')
  const hasSearched = ref(false)
  const searchResults = ref([])
  const activeCabinetCategory = ref('')
  const loadingMore = ref(false)
  const noMore = ref(false)
  const currentPage = ref(1)
  const scrollTop = ref(0)

  function resetSearch() {
    currentPage.value = 1
    noMore.value = false
    searchResults.value = []
  }

  function clearSearch() {
    query.value = ''
    hasSearched.value = false
    resetSearch()
  }

  function saveScroll(top = window.scrollY) {
    scrollTop.value = top
  }

  return {
    query,
    hasSearched,
    searchResults,
    activeCabinetCategory,
    loadingMore,
    noMore,
    currentPage,
    scrollTop,
    resetSearch,
    clearSearch,
    saveScroll,
  }
})
