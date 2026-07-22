<!-- 产品详情页：展示产品事实、成分分组、安全提示和个人适配分析。 -->
<template>
  <section class="detail-page">
    <div v-if="loading" class="loading-panel">读取中...</div>
    <template v-else-if="detail">
      <section class="product-summary">
        <div class="summary-content">
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
            <h2>{{ product.name }}</h2>
            <p class="registration-line">{{ registrationText }}</p>
            <p class="origin-line">{{ originText }}</p>
            <div class="meta-line">
              <span>{{ product.brand || '未知品牌' }}</span>
              <small class="category-tag">{{ product.category || '未分类' }}</small>
            </div>
          </div>
        </div>
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
      </section>

      <section class="detail-section ingredient-section">
        <div v-if="product.ingredients.length" class="ingredient-table-wrap">
          <table class="ingredient-table">
            <thead>
              <tr>
                <th>成分名称（{{ product.ingredient_count || '-' }}种）</th>
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

      <section class="detail-section benefit-section">
        <header>
          <h3>产品功效</h3>
          <span>{{ visibleBenefitGroups.length }} 类</span>
        </header>
        <div class="benefit-scroll">
          <article v-for="group in visibleBenefitGroups" :key="group.name" class="benefit-card">
            <component :is="benefitIcon(group.name)" :size="20" stroke-width="1.8" />
            <strong>{{ group.name }}</strong>
          </article>
        </div>
        <div class="fit-panel">
          <div class="fit-copy-grid">
            <article class="fit-copy-block">
              <h4>亮点</h4>
              <ul v-if="analysisHighlights.length">
                <li v-for="item in analysisHighlights" :key="item">{{ item }}</li>
              </ul>
              <p v-else>暂无明显特色</p>
            </article>
            <article class="fit-copy-block">
              <h4>Tips</h4>
              <p v-if="missingProfileFields.length">
                去
                <button class="fit-profile-text-link" type="button" @click="goProfile">个人档案</button>
                生成专属方案推荐
              </p>
              <ul v-else-if="analysisTips.length">
                <li v-for="item in analysisTips" :key="item">{{ item }}</li>
              </ul>
              <p v-else>暂无明显冲突</p>
            </article>
          </div>
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
import {
  AlertTriangle,
  Brush,
  ChessQueen,
  CloudSunRain,
  Droplets,
  ExternalLink,
  Film,
  HeartPulse,
  Leaf,
  Plus,
  ScanFace,
  ShieldCheck,
  Sparkles,
  WandSparkles,
  Wind,
} from 'lucide-vue-next'
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
const analysis = computed(() => detail.value?.analysis || {})
const visibleBenefitGroups = computed(() => (detail.value?.benefit_groups || []).filter((group) => group.count > 0))
const visibleSafetyGroups = computed(() => (detail.value?.safety_groups || []).filter((group) => group.count > 0))
const analysisHighlights = computed(() => analysis.value.highlights_text || [])
const analysisTips = computed(() => analysis.value.tips || analysis.value.reasons || [])
const missingProfileFields = computed(() => analysis.value.missing_profile_fields || [])
const registrationText = computed(() => product.value.registration_number ? `备案号:${product.value.registration_number}` : '备案号待核验')
const originText = computed(() => product.value.brand_origin_country ? `品牌起源:${product.value.brand_origin_country}` : '品牌起源待核验')

onMounted(loadDetail)

async function loadDetail() {
  loading.value = true
  try {
    detail.value = await productApi.getProductDetail(route.params.id)
  } catch (err) {
    appStore.showToast(err.message || '产品详情读取失败', 'error')
    router.replace('/cabinet')
  } finally {
    loading.value = false
  }
}

async function addProduct() {
  try {
    await productApi.addMyProduct({ product_id: product.value.id })
    appStore.showToast('已加入我的产品库', 'success')
  } catch (err) {
    appStore.showToast(err.message || '添加失败', 'error')
  }
}

function goProfile() {
  router.push({ path: '/profile', query: { redirect: route.fullPath } })
}

function benefitIcon(name) {
  const map = {
    保湿: Droplets,
    舒缓: HeartPulse,
    修护: ShieldCheck,
    抗氧化: Sparkles,
    '美白/提亮': ScanFace,
    防晒: CloudSunRain,
    抗老: ChessQueen,
    '控油/祛痘': Wind,
    清洁: Brush,
    柔润: Leaf,
    '成膜/持妆': Film,
    修饰妆效: WandSparkles,
  }
  return map[name] || Sparkles
}

function ingredientName(ingredient) {
  return ingredient.display_name || ingredient.zh_name || ingredient.inci_name || '未知成分'
}

function safetyText(ingredient) {
  if (ingredient.safety_level && ingredient.safety_level !== 'unknown') {
    return ingredient.safety_level
  }
  const tags = ingredient.tags || []
  if (tags.some((tag) => ['fragrance', 'alcohol', 'acid', 'retinoid', 'irritant', 'comedogenic', 'heavy_oil'].includes(tag))) {
    return '需留意'
  }
  return '安全'
}

function safetyClass(ingredient) {
  const text = safetyText(ingredient)
  if (text.includes('危险') || text.includes('高') || text.includes('避') || text.includes('留意')) return 'warning'
  if (text.includes('有风险') || text.includes('中')) return 'caution'
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
.detail-section,
.loading-panel {
  border: 1px solid rgba(25, 118, 129, 0.1);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 10px 26px rgba(20, 82, 91, 0.06);
}
.product-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 5px;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}
.summary-content {
  display: grid;
  grid-template-columns: 112px 1fr;
  gap: 16px;
  align-items: center;
}
.product-image {
  width: 112px;
  height: 132px;
  object-fit: cover;
  object-position: center;
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
    margin-top: 8px;
    span {
      color: $mint-primary;
      font-size: 13px;
      font-weight: 900;
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
  h2 {
    margin: 0;
    color: $text-primary;
    font-size: 21px;
    line-height: 1.3;
  }
  p {
    margin-top: 6px;
    color: $text-light;
    font-size: 13px;
  }
  .registration-line {
    font-size: 12px;
  }
  .origin-line {
    font-size: 12px;
  }
}
.summary-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  margin-top: 0;
  .btn {
    flex: 1;
    width: 100%;
    height: calc(var(--btn-height) - 10px);
    min-height: calc(var(--btn-height) - 10px) !important;
    display: inline-flex;
    align-items: center;
    justify-content: center;
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
.benefit-section {
  gap: 8px;
  padding: 10px 14px 14px;
  header {
    margin-bottom: 4px;
    align-items: center;
    h3 {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      color: #0f2430;
      font-size: 17px;
      font-weight: 800;
      letter-spacing: 0;
      &::before {
        content: '';
        width: 4px;
        height: 17px;
        border-radius: 999px;
        background: linear-gradient(180deg, #7bd8d2 0%, #0d7c87 100%);
      }
    }
    span {
      min-width: 38px;
      min-height: 22px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      background: rgba(13, 124, 135, 0.08);
      color: #0d7c87;
      font-size: 12px;
      font-weight: 800;
    }
  }
}
.ingredient-section {
  gap: 0;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
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
.benefit-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 2px 2px 2px;
  scroll-snap-type: x proximity;
  -webkit-overflow-scrolling: touch;
}
.benefit-card {
  flex: 0 0 54px;
  min-height: 52px;
  display: grid;
  grid-template-rows: 20px auto;
  place-items: center;
  scroll-snap-align: start;
  color: $mint-primary;
  text-align: center;
  svg {
    display: block;
    color: inherit;
  }
  strong {
    color: $text-primary;
    font-size: 11px;
    font-weight: 400;
    line-height: 1.25;
    word-break: keep-all;
  }
}
.fit-panel {
  display: grid;
  gap: 0;
  margin-top: 0;
  padding-top: 10px;
  border-top: 1px solid rgba(25, 118, 129, 0.1);
}
.fit-copy-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}
.fit-copy-block {
  min-width: 0;
  h4 {
    margin: 0 0 7px;
    color: $mint-primary;
    font-size: 14px;
    font-weight: 900;
  }
  ul {
    display: grid;
    gap: 4px;
    margin: 0;
    padding-left: 16px;
  }
  li,
  p {
    margin: 0;
    color: $text-light;
    font-size: 13px;
    line-height: 1.45;
  }
}
.fit-profile-text-link {
  display: inline;
  border: 0;
  background: transparent;
  color: $mint-primary;
  font-size: 13px;
  font-weight: 900;
  text-decoration: underline;
  text-underline-offset: 3px;
  padding: 0;
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
  border-radius: 8px;
  border: 1px solid rgba(25, 118, 129, 0.12);
  background: rgba(255, 255, 255, 0.78);
  overflow: hidden;
}
.ingredient-table {
  width: 100%;
  min-width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  table-layout: fixed;
  th,
  td {
    border-right: 1px solid rgba(25, 118, 129, 0.12);
    border-bottom: 1px solid rgba(25, 118, 129, 0.12);
    padding: 5px 4px;
    text-align: left;
    vertical-align: middle;
  }
  th:last-child,
  td:last-child {
    border-right: 0;
  }
  tbody tr:last-child td {
    border-bottom: 0;
  }
  th {
    background: rgba(221, 247, 248, 0.72);
    color: #0d7c87;
    font-size: 12px;
    font-weight: 900;
    line-height: 1.2;
    text-align: center;
    white-space: nowrap;
  }
  td {
    color: $text-light;
    font-size: 12px;
    line-height: 1.35;
    word-break: break-word;
  }
  th:nth-child(1),
  td:nth-child(1) {
    width: 42%;
  }
  th:nth-child(2),
  td:nth-child(2) {
    width: 20%;
    text-align: center;
  }
  th:nth-child(3),
  td:nth-child(3) {
    width: 38%;
  }
  strong {
    display: block;
    color: $text-primary;
    font-size: 13px;
    line-height: 1.3;
  }
  small {
    display: block;
    margin-top: 3px;
    color: rgba(122, 138, 157, 0.86);
    font-size: 9px;
    line-height: 1.35;
  }
}
.safety-badge {
  width: fit-content;
  min-height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
  border-radius: 999px;
  font-size: 11px;
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
  .summary-content {
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
