<!-- 产品详情页：展示产品事实、成分分组、安全提示和个人适配分析。 -->
<template>
  <section class="detail-page">
    <div v-if="loading" class="loading-panel">读取中...</div>
    <template v-else-if="detail">
      <section class="product-summary">
        <img
          v-if="product.image_url"
          class="product-image"
          :src="product.image_url"
          :alt="product.name"
          loading="lazy"
          @error="hideBrokenImage"
        />
        <div v-else class="product-image placeholder">{{ product.brand?.slice(0, 1) || '产' }}</div>

        <div class="summary-meta">
          <div class="meta-line">
            <span>{{ product.brand || '未知品牌' }}</span>
            <small>{{ product.category || '未分类' }}</small>
            <small v-if="product.brand_origin_country">起源 {{ product.brand_origin_country }}</small>
          </div>
          <h2>{{ product.name }}</h2>
          <p>{{ ingredientText }}</p>
          <p>{{ registrationText }}</p>
          <div class="summary-actions">
            <button class="btn btn-primary" type="button" @click="addProduct">
              <Plus :size="16" />
              加入我的产品库
            </button>
            <a v-if="product.source_url" :href="product.source_url" target="_blank" rel="noreferrer">
              <ExternalLink :size="15" />
              来源
            </a>
          </div>
        </div>
      </section>

      <section class="detail-section ingredient-section">
        <header>
          <h3>完整成分表</h3>
          <span>{{ product.ingredient_count }} 个</span>
        </header>
        <div v-if="product.ingredients.length" class="ingredient-table-wrap">
          <table class="ingredient-table">
            <thead>
              <tr>
                <th>成分名称</th>
                <th>是否安全</th>
                <th>使用目的</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ingredient in product.ingredients" :key="ingredient.id">
                <td>
                  <strong>{{ ingredientName(ingredient) }}</strong>
                  <small v-if="ingredient.inci_name">{{ ingredient.inci_name }}</small>
                </td>
                <td>
                  <span :class="['safety-badge', safetyClass(ingredient)]">{{ safetyText(ingredient) }}</span>
                </td>
                <td>{{ purposeText(ingredient) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="analysis-box">
          <strong>缺少成分，无法分析</strong>
        </div>
      </section>

      <section class="detail-section">
        <header>
          <h3>适配结果</h3>
          <span :class="['status-pill', detail.analysis.status]">{{ statusText(detail.analysis.status) }}</span>
        </header>
        <div class="analysis-box">
          <strong>{{ detail.analysis.summary }}</strong>
          <ul v-if="detail.analysis.reasons.length">
            <li v-for="reason in detail.analysis.reasons" :key="reason">{{ reason }}</li>
          </ul>
        </div>
      </section>

      <section class="detail-section">
        <header>
          <h3>产品功效</h3>
          <span>{{ visibleBenefitGroups.length }} 类</span>
        </header>
        <div class="group-grid">
          <article v-for="group in visibleBenefitGroups" :key="group.name" class="group-card">
            <Leaf :size="18" />
            <div>
              <strong>{{ group.name }}</strong>
              <p>{{ group.count }} 个成分</p>
            </div>
          </article>
        </div>
      </section>

      <section class="detail-section">
        <header>
          <h3>安全提示</h3>
          <span>{{ detail.safety_summary }}</span>
        </header>
        <div class="group-grid">
          <article v-for="group in visibleSafetyGroups" :key="group.name" class="group-card warning">
            <AlertTriangle :size="18" />
            <div>
              <strong>{{ group.name }}</strong>
              <p>{{ group.count }} 个成分</p>
            </div>
          </article>
          <article v-if="!visibleSafetyGroups.length" class="group-card calm">
            <ShieldCheck :size="18" />
            <div>
              <strong>未标记高关注成分</strong>
              <p>基于当前成分标签</p>
            </div>
          </article>
        </div>
      </section>

    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { AlertTriangle, ExternalLink, Leaf, Plus, ShieldCheck } from 'lucide-vue-next'
import { productApi } from '@/api/product'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()
const loading = ref(false)
const detail = ref(null)
const product = computed(() => detail.value?.product || {})
const visibleBenefitGroups = computed(() => (detail.value?.benefit_groups || []).filter((group) => group.count > 0))
const visibleSafetyGroups = computed(() => (detail.value?.safety_groups || []).filter((group) => group.count > 0))
const ingredientText = computed(() => {
  if (!product.value.has_ingredients) return '成分待完善'
  return `${product.value.ingredient_count || product.value.ingredients?.length || 0} 个成分已收录`
})
const registrationText = computed(() => product.value.registration_number ? `备案号：${product.value.registration_number}` : '备案号待核验')

onMounted(loadDetail)

async function loadDetail() {
  loading.value = true
  try {
    detail.value = await productApi.getProductDetail(route.params.id, userStore.userId)
  } catch (err) {
    appStore.showToast(err.message || '产品详情读取失败', 'error')
    router.replace('/cabinet')
  } finally {
    loading.value = false
  }
}

async function addProduct() {
  try {
    await productApi.addMyProduct(userStore.userId, { product_id: product.value.id })
    appStore.showToast('已加入我的产品库', 'success')
  } catch (err) {
    appStore.showToast(err.message || '添加失败', 'error')
  }
}

function statusText(status) {
  const map = {
    suitable: '适合',
    caution: '谨慎',
    avoid: '避雷',
    incomplete: '待完善',
  }
  return map[status] || '待确认'
}

function ingredientName(ingredient) {
  const position = ingredient.position ? `${ingredient.position}. ` : ''
  return `${position}${ingredient.display_name || ingredient.zh_name || ingredient.inci_name || '未知成分'}`
}

function safetyText(ingredient) {
  if (ingredient.safety_level && ingredient.safety_level !== 'unknown') {
    return ingredient.safety_level
  }
  const tags = ingredient.tags || []
  if (tags.some((tag) => ['fragrance', 'alcohol', 'acid', 'retinoid', 'irritant', 'comedogenic', 'heavy_oil'].includes(tag))) {
    return '需留意'
  }
  return '常规安全'
}

function safetyClass(ingredient) {
  const text = safetyText(ingredient)
  if (text.includes('高') || text.includes('避') || text.includes('留意')) return 'warning'
  if (text.includes('中')) return 'caution'
  return 'safe'
}

function purposeText(ingredient) {
  const purposes = ingredient.purposes || []
  if (purposes.length) return purposes.join('、')
  const purposeMap = {
    moisturizing: '保湿',
    humectant: '保湿',
    soothing: '舒缓',
    barrier: '屏障修护',
    skin_protecting: '皮肤保护',
    brightening: '美白/提亮',
    antioxidant: '抗氧化',
    anti_aging: '抗老',
    retinoid: '高活性护理',
    uv_filter: '防晒',
    sebum_control: '控油',
    acne_care: '祛痘',
    surfactant: '清洁',
    emulsifier: '乳化',
    solvent: '溶剂',
    base: '基底',
    thickener: '增稠',
    preservative: '防腐',
    fragrance: '赋香',
  }
  const mapped = (ingredient.tags || []).map((tag) => purposeMap[tag]).filter(Boolean)
  return [...new Set(mapped)].join('、') || '配方辅助'
}

function hideBrokenImage(event) {
  event.currentTarget.style.display = 'none'
}
</script>

<style lang="scss" scoped>
.detail-page {
  display: grid;
  gap: 14px;
  max-width: 720px;
  margin: 0 auto;
}
.product-summary,
.detail-section,
.loading-panel {
  border: 1px solid rgba(25, 118, 129, 0.1);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 10px 26px rgba(20, 82, 91, 0.06);
}
.product-summary {
  display: grid;
  grid-template-columns: 112px 1fr;
  gap: 16px;
  align-items: center;
  padding: 18px;
}
.product-image {
  width: 112px;
  height: 132px;
  object-fit: contain;
  border-radius: 8px;
  background: #f7fbfb;
  border: 1px solid rgba(25, 118, 129, 0.08);
  &.placeholder {
    display: grid;
    place-items: center;
    color: $mint-primary;
    font-size: 28px;
    font-weight: 900;
  }
}
.summary-meta {
  min-width: 0;
  .meta-line {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    span {
      color: $mint-primary;
      font-size: 13px;
      font-weight: 900;
    }
    small {
      padding: 2px 8px;
      border-radius: 999px;
      background: rgba(25, 118, 129, 0.08);
      color: $text-light;
      font-size: 12px;
      font-weight: 800;
    }
  }
  h2 {
    margin-top: 7px;
    color: $text-primary;
    font-size: 21px;
    line-height: 1.3;
  }
  p {
    margin-top: 6px;
    color: $text-light;
    font-size: 13px;
  }
}
.summary-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 12px;
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  a {
    min-height: 34px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    color: $mint-primary;
    font-size: 13px;
    font-weight: 900;
  }
}
.detail-section {
  display: grid;
  gap: 12px;
  padding: 16px;
  header {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: center;
    h3 {
      color: $text-primary;
      font-size: 17px;
    }
    span {
      color: $text-light;
      font-size: 13px;
      text-align: right;
    }
  }
}
.status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
  &.suitable {
    background: rgba(33, 150, 83, 0.12);
    color: #187244;
  }
  &.caution {
    background: rgba(245, 158, 11, 0.16);
    color: #9a5d00;
  }
  &.avoid {
    background: rgba(220, 38, 38, 0.12);
    color: #b91c1c;
  }
  &.incomplete {
    background: rgba(100, 116, 139, 0.14);
    color: #475569;
  }
}
.analysis-box {
  display: grid;
  gap: 8px;
  padding: 12px;
  border-radius: 8px;
  background: rgba(244, 250, 250, 0.84);
  strong {
    color: $text-primary;
    font-size: 14px;
  }
  ul {
    display: grid;
    gap: 4px;
    padding-left: 17px;
    color: $text-light;
    font-size: 13px;
  }
}
.group-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.group-card {
  min-height: 58px;
  display: grid;
  grid-template-columns: 24px 1fr;
  align-items: center;
  gap: 8px;
  padding: 10px;
  border-radius: 8px;
  background: rgba(244, 250, 250, 0.82);
  color: $mint-primary;
  strong {
    color: $text-primary;
    font-size: 14px;
  }
  p {
    color: $text-light;
    font-size: 12px;
  }
  &.warning {
    color: #9a5d00;
    background: rgba(245, 158, 11, 0.1);
  }
  &.calm {
    color: #187244;
    background: rgba(33, 150, 83, 0.1);
  }
}
.ingredient-table-wrap {
  width: 100%;
  overflow-x: auto;
  border: 1px solid rgba(25, 118, 129, 0.08);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.78);
}
.ingredient-table {
  width: 100%;
  min-width: 620px;
  border-collapse: collapse;
  table-layout: fixed;
  th,
  td {
    border: 1px solid rgba(25, 118, 129, 0.12);
    padding: 11px 12px;
    text-align: left;
    vertical-align: middle;
  }
  th {
    background: rgba(244, 250, 250, 0.98);
    color: $text-primary;
    font-size: 12px;
    font-weight: 900;
    white-space: nowrap;
  }
  td {
    color: $text-light;
    font-size: 13px;
    line-height: 1.45;
    word-break: break-word;
  }
  th:nth-child(1),
  td:nth-child(1) {
    width: 48%;
  }
  th:nth-child(2),
  td:nth-child(2) {
    width: 18%;
  }
  th:nth-child(3),
  td:nth-child(3) {
    width: 34%;
  }
  strong {
    display: block;
    color: $text-primary;
    font-size: 13px;
    line-height: 1.35;
  }
  small {
    display: block;
    margin-top: 3px;
    color: rgba(122, 138, 157, 0.86);
    font-size: 11px;
    line-height: 1.35;
  }
}
.safety-badge {
  width: fit-content;
  min-height: 24px;
  display: inline-flex;
  align-items: center;
  padding: 0 9px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
  &.safe {
    background: rgba(33, 150, 83, 0.1);
    color: #187244;
  }
  &.caution {
    background: rgba(245, 158, 11, 0.14);
    color: #9a5d00;
  }
  &.warning {
    background: rgba(220, 38, 38, 0.1);
    color: #b91c1c;
  }
}
.loading-panel {
  min-height: 160px;
  display: grid;
  place-items: center;
  color: $text-light;
}

@include respond(phone-sm) {
  .product-summary {
    grid-template-columns: 88px 1fr;
    gap: 12px;
  }
  .product-image {
    width: 88px;
    height: 108px;
  }
  .summary-meta h2 {
    font-size: 18px;
  }
  .group-grid {
    grid-template-columns: 1fr;
  }
}
</style>
