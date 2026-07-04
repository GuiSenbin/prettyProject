<template>
  <div class="influencers-page">
    <header class="section-hero">
      <h2 class="page-title">灵感精选</h2>
      <p class="page-desc">保留真正有参考价值的妆容、护肤与产品测评，减少被种草时的信息噪音。</p>
    </header>

    <div class="tabs">
      <button v-for="tab in tabs" :key="tab.key" class="tab-btn"
              :class="{ active: activeTab === tab.key }" @click="switchTab(tab.key)">
        {{ tab.label }}
      </button>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>
    <div v-else-if="list.length === 0" class="empty-state">暂无内容</div>
    <div v-else class="influencer-grid">
      <InfluencerCard v-for="item in list" :key="item.id" :item="item" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import InfluencerCard from '@/components/InfluencerCard.vue'
import api from '@/api'

const list = ref([])
const loading = ref(true)
const activeTab = ref('all')

const tabs = [
  { key: 'all', label: '全部' },
  { key: 'makeup', label: '妆容教程' },
  { key: 'skincare', label: '护肤心得' },
  { key: 'review', label: '产品测评' },
]

async function fetchData() {
  loading.value = true
  try {
    const data = await api.get(`/influencers/?category=${activeTab.value}`)
    list.value = data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function switchTab(key) {
  activeTab.value = key
  fetchData()
}

onMounted(fetchData)
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 24px;
  flex-wrap: wrap;

  .tab-btn {
    padding: 8px 20px;
    border: 1.5px solid $mint-pale;
    border-radius: 20px;
    background: $white;
    color: $text-secondary;
    font-size: 14px;
    cursor: pointer;
    transition: $transition;
    font-family: inherit;

    &:hover,
    &.active {
      background: $mint-primary;
      color: $white;
      border-color: $mint-primary;
    }
  }
}

.influencer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: $text-light;
  font-size: 16px;
}

@media (max-width: 768px) {
  .tabs {
    flex-wrap: nowrap;
    overflow-x: auto;
    margin: 0 -14px 18px;
    padding: 0 14px 6px;

    .tab-btn {
      flex: 0 0 auto;
      min-height: 40px;
      padding: 8px 16px;
    }
  }

  .influencer-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .loading-state,
  .empty-state {
    padding: 42px 16px;
  }
}
</style>
