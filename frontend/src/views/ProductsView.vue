<template>
  <div class="products-page">
    <h2 class="page-title">产品百科</h2>
    <p class="page-desc">了解各类美妆护肤产品，找到适合你的那一款</p>

    <div class="product-toolbar">
      <input type="text" v-model="searchQuery" placeholder="搜索产品名称或功效..."
             class="search-input" @input="onSearch" />

      <div class="category-chips">
        <span v-for="cat in categories" :key="cat.key" class="category-chip"
              :class="{ active: activeCategory === cat.key }"
              @click="switchCategory(cat.key)">
          {{ cat.label }}
        </span>
      </div>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>
    <div v-else-if="products.length === 0" class="empty-state">🔍<br>没有找到匹配的产品</div>
    <div v-else class="products-grid">
      <ProductCard v-for="p in products" :key="p.id" :product="p" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ProductCard from '@/components/ProductCard.vue'
import api from '@/api'

const products = ref([])
const loading = ref(true)
const searchQuery = ref('')
const activeCategory = ref('all')

const categories = [
  { key: 'all', label: '全部' },
  { key: 'cleanser', label: '洁面' },
  { key: 'toner', label: '爽肤水' },
  { key: 'essence', label: '精华' },
  { key: 'lotion', label: '乳液/面霜' },
  { key: 'sunscreen', label: '防晒' },
  { key: 'foundation', label: '底妆' },
  { key: 'lip', label: '唇妆' },
  { key: 'eye', label: '眼妆' },
  { key: 'mask', label: '面膜' },
]

async function fetchData() {
  loading.value = true
  try {
    const params = new URLSearchParams({ category: activeCategory.value })
    if (searchQuery.value) params.set('search', searchQuery.value)
    const data = await api.get(`/products/?${params}`)
    products.value = data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function switchCategory(key) {
  activeCategory.value = key
  fetchData()
}

let timer = null
function onSearch() {
  clearTimeout(timer)
  timer = setTimeout(fetchData, 300)
}

onMounted(fetchData)
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.product-toolbar {
  margin-bottom: 24px;

  .search-input {
    width: 100%;
    padding: 14px 20px;
    border: 1.5px solid $mint-pale;
    border-radius: 50px;
    font-size: 15px;
    outline: none;
    font-family: inherit;
    transition: $transition;
    background: $white;

    &:focus {
      border-color: $mint-primary;
      box-shadow: 0 0 0 3px rgba(45, 143, 111, 0.12);
    }
  }

  .category-chips {
    display: flex;
    gap: 8px;
    margin-top: 12px;
    flex-wrap: wrap;

    .category-chip {
      padding: 6px 16px;
      border: 1px solid $mint-pale;
      border-radius: 16px;
      font-size: 13px;
      color: $text-secondary;
      cursor: pointer;
      transition: $transition;
      background: $white;

      &:hover,
      &.active {
        background: $mint-primary;
        color: $white;
        border-color: $mint-primary;
      }
    }
  }
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 16px;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: $text-light;
  font-size: 16px;
}
</style>
