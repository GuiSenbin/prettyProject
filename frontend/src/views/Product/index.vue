<!-- 产品库：搜索、产品列表、个人产品库 -->
<template>
  <section class="product-page">
    <form class="search-bar" @submit.prevent="handleSearch">
      <Search :size="17" />
      <input v-model.trim="query" type="search" placeholder="输入产品名或品牌" />
      <button class="btn btn-primary" type="submit" :disabled="searching">
        {{ searching ? '搜索中' : '搜索' }}
      </button>
    </form>

    <div v-if="hasSearched && searchResults.length > 0" class="search-results">
      <div class="product-list">
        <div
          v-for="item in searchResults"
          :key="item.id"
          class="product-card"
          @click="openProductDetail(item.id)"
        >
          <div class="cover">
            <img v-if="item.image_url" :src="item.image_url" :alt="item.name" loading="lazy" />
            <div v-else class="fallback">
              <Package :size="24" />
            </div>
          </div>
          <div class="info">
            <div class="meta-row">
              <span class="brand">{{ item.brand }}</span>
              <span v-if="item.category" class="category-tag">{{ item.category }}</span>
            </div>
            <h3 class="name">{{ item.name }}</h3>
            <div class="tags" :class="{ empty: !productBenefitTags(item).length }">
              <span v-for="tag in productBenefitTags(item)" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>
          <div class="actions" v-if="!isAdded(item.id)">
            <button class="add-btn" @click.stop="addCabinetProduct(item.id)">添加产品</button>
          </div>
        </div>
      </div>

      <div ref="loadMoreTrigger" class="load-more-trigger">
        <span v-if="loadingMore">正在加载更多...</span>
        <span v-else-if="noMore">没有更多产品了</span>
      </div>
    </div>

    <div v-else-if="hasSearched && searchResults.length === 0" class="empty-slate">
      <PackageSearch :size="48" class="icon-sparkles" />
      <h3>暂无匹配结果</h3>
      <p>知识库中未找到相关产品，请尝试其他关键词</p>
    </div>

    <div v-else class="my-cabinet-section">
      <div v-if="loadingCabinet" class="loading-cabinet">
        <span>读取我的产品库中...</span>
      </div>
      <div v-else-if="myProducts.length > 0" class="cabinet-results">
        <div class="category-scroll">
          <button
            class="category-chip category-chip--all"
            :class="{ active: !activeCabinetCategory }"
            type="button"
            @click="selectCabinetCategory('')"
          >
            <span>全部({{ myProducts.length || 0 }})</span>
          </button>
          <button
            v-for="item in cabinetCategoryFilters"
            :key="item.name"
            class="category-chip"
            :class="{ active: activeCabinetCategory === item.name }"
            type="button"
            @click="selectCabinetCategory(item.name)"
          >
            <span>{{ item.name }}</span>
            <em v-if="item.count > 0">{{ item.count }}</em>
          </button>
        </div>
        <div v-if="filteredMyProducts.length > 0" class="product-list">
          <div
            v-for="item in filteredMyProducts"
            :key="item.id"
            class="product-card"
          @click="openProductDetail(item.product?.id || item.product_id)"
          >
            <div class="cover">
              <img v-if="item.product?.image_url" :src="item.product.image_url" :alt="item.product.name" loading="lazy" />
              <div v-else class="fallback">
                <Package :size="24" />
              </div>
            </div>
            <div class="info">
              <div class="meta-row">
                <span class="brand">{{ item.product?.brand || '自定义' }}</span>
                <span v-if="item.product?.category" class="category-tag">{{ item.product.category }}</span>
              </div>
              <h3 class="name">{{ item.product?.name || item.custom_name || '未命名产品' }}</h3>
              <div class="tags" :class="{ empty: !productBenefitTags(item.product).length }">
                <span v-for="tag in productBenefitTags(item.product)" :key="tag" class="tag">{{ tag }}</span>
              </div>
            </div>
            <div class="actions cabinet-actions">
              <button
                class="delete-btn"
                type="button"
                :disabled="deletingProductId === item.id"
                @click.stop="deleteCabinetProduct(item)"
                aria-label="删除产品"
              >
                <Trash2 :size="14" />
                <span>{{ deletingProductId === item.id ? '删除中' : '删除' }}</span>
              </button>
            </div>
          </div>
        </div>
        <div v-else class="empty-slate category-empty">
          <Sparkles :size="42" class="icon-sparkles" />
          <h3>暂无数据</h3>
          <p>该分类还没有产品</p>
          <p class="desc-tips">点击搜索，添加你的私有产品吧</p>
        </div>
      </div>
      <div v-else class="empty-slate">
        <Sparkles :size="48" class="icon-sparkles" />
        <h3>我的产品库暂无数据</h3>
        <p>成分知识库已就绪</p>
        <p class="desc-tips">点击搜索 添加你的私有产品吧</p>
      </div>
    </div>
  </section>
</template>


<script setup>
import { computed, nextTick, ref, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { Search, Sparkles, Package, PackageSearch, Trash2 } from 'lucide-vue-next'
import { productApi } from '@/api/product'
import { useAppStore } from '@/stores/app'
import { useProductStore } from '@/stores/product'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const appStore = useAppStore()
const productStore = useProductStore()
const router = useRouter()
const {
  query,
  hasSearched,
  searchResults,
  activeCabinetCategory,
  loadingMore,
  noMore,
  currentPage,
} = storeToRefs(productStore)
const searching = ref(false)
const CATEGORIES = ['洁面', '精华', '乳液/面霜', '防晒', '面膜', '底妆', '唇妆/彩妆']
const loadMoreTrigger = ref(null)
const pageSize = 12

const myProducts = ref([])
const loadingCabinet = ref(false)
const deletingProductId = ref(null)
const filteredMyProducts = computed(() => {
  if (!activeCabinetCategory.value) return myProducts.value
  return myProducts.value.filter(item => item.product?.category === activeCabinetCategory.value)
})
const cabinetCategoryFilters = computed(() => CATEGORIES
  .map(name => ({
    name,
    count: myProducts.value.filter(item => item.product?.category === name).length,
  }))
)

function isAdded(productId) {
  return myProducts.value.some(item => (item.product?.id || item.product_id) === productId)
}

function productBenefitTags(product) {
  return product?.benefit_tags || []
}

async function addCabinetProduct(productId) {
  if (!userStore.userId) {
    appStore.showToast('请先登录后再添加产品', 'warning')
    return
  }
  try {
    await productApi.addMyProduct(userStore.userId, { product_id: productId })
    await loadCabinetProducts()
    appStore.showToast('已加入我的产品库', 'success')
  } catch (err) {
    console.error('添加失败:', err)
    appStore.showToast(err.message || '添加失败，请稍后再试', 'error')
  }
}

async function deleteCabinetProduct(item) {
  if (!userStore.userId || !item?.id) return
  const productName = item.product?.name || item.custom_name || '这个产品'
  if (!window.confirm(`确定从产品库删除「${productName}」吗？`)) return
  deletingProductId.value = item.id
  try {
    await productApi.deleteMyProduct(userStore.userId, item.id)
    myProducts.value = myProducts.value.filter(product => product.id !== item.id)
    appStore.showToast('已从产品库删除', 'success')
  } catch (err) {
    console.error('删除产品失败:', err)
    appStore.showToast(err.message || '删除失败，请稍后再试', 'error')
  } finally {
    deletingProductId.value = null
  }
}

let observer = null

async function loadCabinetProducts() {
  if (!userStore.userId) return
  loadingCabinet.value = true
  try {
    const res = await productApi.listMyProducts(userStore.userId)
    myProducts.value = res || []
  } catch (err) {
    console.error('获取个人产品库失败:', err)
    appStore.showToast(err.message || '产品库读取失败，请稍后再试', 'error')
  } finally {
    loadingCabinet.value = false
  }
}

async function resetAndSearch() {
  productStore.resetSearch()
  await performSearch(true)
}

async function performSearch(isFirstPage = false) {
  if (isFirstPage) {
    searching.value = true
  } else {
    loadingMore.value = true
  }
  try {
    const res = await productApi.searchProducts(
      query.value,
      currentPage.value,
      pageSize
    )
    const items = res || []
    if (items.length < pageSize) {
      noMore.value = true
    }
    if (isFirstPage) {
      searchResults.value = items
      hasSearched.value = true
    } else {
      searchResults.value.push(...items)
    }
  } catch (err) {
    console.error('搜索失败:', err)
    noMore.value = true
    if (isFirstPage) {
      hasSearched.value = false
    }
    appStore.showToast(err.message || '搜索失败，请稍后再试', 'error')
  } finally {
    searching.value = false
    loadingMore.value = false
  }
}

async function handleSearch() {
  if (!query.value.trim()) {
    hasSearched.value = false
    searchResults.value = []
    noMore.value = false
    await loadCabinetProducts()
    return
  }
  await resetAndSearch()
}

function selectCabinetCategory(catName) {
  activeCabinetCategory.value = catName
}

function openProductDetail(productId) {
  if (!productId) return
  productStore.saveScroll()
  router.push(`/cabinet/products/${productId}`)
}

async function loadNextPage() {
  if (searching.value || loadingMore.value || noMore.value) return
  currentPage.value++
  await performSearch(false)
}

onMounted(async () => {
  await loadCabinetProducts()
  await nextTick()
  if (productStore.scrollTop > 0) {
    window.scrollTo({ top: productStore.scrollTop, behavior: 'auto' })
  }
  observer = new IntersectionObserver((entries) => {
    const entry = entries[0]
    if (entry.isIntersecting && hasSearched.value && !noMore.value && !searching.value && !loadingMore.value) {
      loadNextPage()
    }
  }, {
    rootMargin: '100px',
  })
  if (loadMoreTrigger.value) {
    observer.observe(loadMoreTrigger.value)
  }
})

onUnmounted(() => {
  productStore.saveScroll()
  if (observer) {
    observer.disconnect()
  }
})
</script>

<style lang="scss" scoped>
.product-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 900px;
  margin: 0 auto;
}
.search-bar {
  display: grid;
  grid-template-columns: 20px 1fr auto;
  align-items: center;
  gap: 10px;
  padding: 4px 4px 4px 12px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid rgba(25, 118, 129, 0.12);
  box-shadow: 0 8px 24px rgba(20, 82, 91, 0.05);
  color: #7a8a9d;
  input {
    min-width: 0;
    border: 0;
    outline: 0;
    color: #111827;
    font-size: 14px;
    background: transparent;
  }
  button {
    min-width: 60px;
    --btn-height: 32px;
    --btn-padding-x: 12px;
    height: var(--btn-height);
    min-height: var(--btn-height) !important;
    padding: 0 var(--btn-padding-x);
    font-size: 13px;
  }
}
.category-scroll {
  display: flex;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  gap: 6px;
  padding: 6px 0 8px;
  overflow-x: auto;
  overscroll-behavior-x: contain;
  -webkit-overflow-scrolling: touch;
  touch-action: pan-x;
  scrollbar-width: thin;
  .category-chip {
    flex: 0 0 auto;
    min-height: 28px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    padding: 0 10px;
    border-radius: 13px;
    border: 1.5px solid rgba(207, 238, 241, 0.92);
    background: rgba(255, 255, 255, 0.62);
    color: rgba(67, 82, 102, 0.78);
    font-family: inherit;
    font-size: 12px;
    font-weight: 800;
    white-space: nowrap;
    cursor: pointer;
    transition: $transition;
    &:not(.category-chip--all) {
      position: relative;
      padding: 0 12px;
    }
    em {
      position: absolute;
      top: -7px;
      right: -1px;
      min-width: 14px;
      height: 14px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0 4px;
      border-radius: 999px;
      background: rgba(13, 124, 135, 0.12);
      color: $mint-primary;
      font-size: 9px;
      font-style: normal;
      font-weight: 900;
      line-height: 1;
    }
    &.active {
      background: #0d7c87;
      color: #fff;
      border-color: #0d7c87;
      em {
        background: rgba(255, 255, 255, 0.92);
        color: #0d7c87;
      }
    }
  }
}
.product-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.product-card {
  display: flex;
  align-items: stretch;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(207, 238, 241, 0.72);
  border-radius: 16px;
  padding: 4px 10px 4px 4px;
  gap: 10px;
  transition: transform 0.25s, box-shadow 0.25s, border-color 0.25s;
  cursor: pointer;
  position: relative;
  box-shadow: 0 10px 24px rgba(20, 82, 91, 0.04);
  &:hover {
    transform: translateY(-2px);
    border-color: rgba(207, 238, 241, 0.96);
    box-shadow: 0 12px 28px rgba(10, 166, 194, 0.08);
  }
  .cover {
    width: 80px;
    height: 80px;
    flex-shrink: 0;
    border-radius: 10px;
    background: #f7fbfb;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(25, 118, 129, 0.06);
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .fallback {
      color: #bbb;
    }
  }
  .info {
    flex: 1;
    min-width: 0;
    padding-right: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    .meta-row {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 13px;
      line-height: 1;
      .brand {
        font-weight: 800;
        color: #0d7c87;
      }
      .category-tag {
        padding: 3px 5px;
        border-radius: 8px;
        background: rgba(13, 124, 135, 0.08);
        border: 1px solid rgba(13, 124, 135, 0.12);
        color: #0d7c87;
        font-size: 9px;
        font-weight: 700;
      }
    }
    .name {
      font-size: 15px;
      font-weight: 800;
      color: #111827;
      margin: 2px 0 0;
      overflow: hidden;
      text-overflow: ellipsis;
      line-height: 1.25;
      min-height: 19px;
      white-space: nowrap;
      word-break: normal;
    }
    .tags {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: auto;
      padding-right: 104px;
      min-height: 22px;
      align-items: flex-end;
      &.empty {
        visibility: hidden;
      }
      .tag {
        padding: 4px 8px;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.62);
        border: 1px solid rgba(207, 238, 241, 0.78);
        color: rgba(67, 82, 102, 0.78);
        font-size: 11px;
        font-weight: 800;
        line-height: 1;
      }
    }
  }
  .actions {
    position: absolute;
    right: 10px;
    bottom: 4px;
    display: flex;
    align-items: flex-end;
    &.cabinet-actions {
      right: 12px;
      bottom: 8px;
    }
    .delete-btn {
      min-height: 26px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 0 8px;
      border-radius: 999px;
      border: 1px solid rgba(240, 112, 112, 0.18);
      background: rgba(255, 255, 255, 0.76);
      color: rgba(181, 55, 55, 0.86);
      font-size: 11px;
      font-weight: 800;
      cursor: pointer;
      box-shadow: 0 8px 18px rgba(17, 24, 39, 0.06);
      transition: $transition;
      &:hover:not(:disabled) {
        transform: translateY(-1px);
        background: rgba(255, 244, 244, 0.92);
      }
      &:disabled {
        cursor: not-allowed;
        opacity: 0.62;
      }
    }
    .add-btn {
      min-height: 28px;
      padding: 0 8px;
      border: 0;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 800;
      cursor: pointer;
      transition: $transition;
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.36), transparent), linear-gradient(135deg, #9ccfe8, #319d98 52%, #b7f2ea);
      color: #fff;
      box-shadow:
        0 6px 14px rgba(49, 157, 152, 0.16),
        inset 0 -1.5px 3px rgba(0, 0, 0, 0.08),
        inset 0 1.5px 3px rgba(255, 255, 255, 0.2);
      &:hover {
        transform: translateY(-1px);
        box-shadow:
          0 8px 18px rgba(49, 157, 152, 0.24),
          inset 0 -1.5px 3px rgba(0, 0, 0, 0.08),
          inset 0 1.5px 3px rgba(255, 255, 255, 0.2);
      }
      &:active {
        transform: translateY(0);
        filter: brightness(0.96);
      }
    }
  }
}
.empty-slate {
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 12px;
  padding: 20px;
  color: #7a8a9d;
  .icon-sparkles {
    color: rgba(25, 118, 129, 0.2);
    margin-bottom: 8px;
  }
  h3 {
    color: #111827;
    font-size: 18px;
  }
  p {
    font-size: 14px;
    opacity: 0.8;
  }
}
.category-empty {
  min-height: 300px;
  padding-top: 48px;
  justify-content: flex-start;
}
.load-more-trigger {
  text-align: center;
  padding: 16px 0;
  color: #7a8a9d;
  font-size: 13px;
}
.my-cabinet-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  .loading-cabinet {
    text-align: center;
    padding: 40px 0;
    color: #7a8a9d;
  }
  .cabinet-results {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
}
.desc-tips {
  font-size: 12px;
  opacity: 0.7;
  max-width: 320px;
  margin: 0 auto;
  line-height: 1.5;
}
</style>
