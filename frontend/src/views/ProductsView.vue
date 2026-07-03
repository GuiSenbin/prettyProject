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
    <div v-if="!loading && !userStore.profile" class="profile-nudge">
      建立个人美妆档案后，可查看每款产品是否适合你。
      <router-link to="/profile">去建立档案</router-link>
    </div>

    <div v-if="!loading && products.length > 0" class="products-grid">
      <ProductCard v-for="p in products" :key="p.id" :product="p" @select="openProduct" />
    </div>

    <div v-if="selectedProduct" class="product-modal-backdrop" @click.self="closeProduct">
      <div class="product-modal" role="dialog" aria-modal="true">
        <button class="modal-close" type="button" @click="closeProduct">×</button>
        <div class="modal-icon">{{ selectedProduct.icon || '📦' }}</div>
        <div class="modal-heading">
          <div>
            <h3>{{ selectedProduct.name }}</h3>
            <p>{{ selectedProduct.category_name }} · {{ selectedProduct.desc }}</p>
          </div>
          <div v-if="selectedAnalysis" class="modal-score" :class="selectedAnalysis.level">
            <strong>{{ selectedAnalysis.score }}</strong>
            <span>适配分</span>
          </div>
        </div>

        <template v-if="selectedAnalysis">
          <section>
            <h4>AI 适配结论</h4>
            <p>{{ selectedAnalysis.conclusion }}</p>
          </section>
          <section>
            <h4>适合你的原因</h4>
            <ul>
              <li v-for="reason in selectedAnalysis.reasons" :key="reason">{{ reason }}</li>
            </ul>
          </section>
          <section>
            <h4>风险提醒</h4>
            <ul>
              <li v-for="risk in selectedAnalysis.risks" :key="risk">{{ risk }}</li>
            </ul>
          </section>
          <section>
            <h4>使用建议</h4>
            <p>{{ selectedAnalysis.usage }}</p>
          </section>
          <div class="modal-actions">
            <button class="btn btn-primary" type="button" :disabled="selectedAnalysis.inCabinet" @click="addSelectedToCabinet">
              {{ selectedAnalysis.inCabinet ? '已在我的产品库' : '加入我的产品库' }}
            </button>
            <router-link to="/cabinet" class="btn btn-outline">查看产品库</router-link>
          </div>
        </template>

        <div v-else class="modal-empty">
          先建立个人美妆档案，AI 才能判断这款产品是否适合你。
          <router-link to="/profile" class="btn btn-primary">去建立档案</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import ProductCard from '@/components/ProductCard.vue'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import { addCabinetProduct, loadCabinetProducts, mapCatalogProductToCabinet } from '@/utils/cabinet'
import api from '@/api'

const userStore = useUserStore()
const appStore = useAppStore()
const products = ref([])
const loading = ref(true)
const searchQuery = ref('')
const activeCategory = ref('all')
const selectedProduct = ref(null)
const cabinetProducts = ref([])

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

function refreshCabinet() {
  cabinetProducts.value = loadCabinetProducts(userStore.userId)
}

function analyzeProduct(product) {
  const profile = userStore.profile
  if (!profile?.skin_type) return null

  const skinLabels = { dry: '干性肌肤', oily: '油性肌肤', combination: '混合性肌肤', normal: '中性肌肤', sensitive: '敏感肌' }
  const concernLabels = {
    acne: '痘痘/痘印',
    blackhead: '黑头/白头',
    wrinkle: '细纹/抗衰',
    dullness: '暗沉/提亮',
    darkcircle: '黑眼圈',
    pore: '毛孔粗大',
    hydration: '保湿补水',
    sensitive: '屏障修护',
  }
  const text = `${product.name} ${product.desc}`.toLowerCase()
  const suitable = product.suitable || []
  const inCabinet = cabinetProducts.value.some((item) => item.name === product.name)
  const matchedSkin = suitable.includes(profile.skin_type)
  const matchedConcerns = (profile.concerns || []).filter((concern) => {
    const concernMap = {
      acne: ['痘', '水杨酸', '控油'],
      blackhead: ['黑头', '清洁', '泥膜'],
      wrinkle: ['抗皱', '抗衰', '视黄醇'],
      dullness: ['亮肤', '提亮', 'vc', '维生素c', '烟酰胺'],
      darkcircle: ['黑眼圈', '眼'],
      pore: ['毛孔', '控油', '水杨酸'],
      hydration: ['保湿', '补水', '玻尿酸'],
      sensitive: ['修护', '舒缓', '温和', '神经酰胺'],
    }
    return (concernMap[concern] || []).some((keyword) => text.includes(keyword))
  })

  let score = matchedSkin ? 76 : 48
  score += Math.min(matchedConcerns.length * 8, 16)
  if (suitable.length >= 5) score += 4
  if (profile.skin_type === 'sensitive' && /(水杨酸|视黄醇|高浓度|控油|清洁泥膜)/.test(text)) score -= 12
  score = Math.max(30, Math.min(score, 96))

  const reasons = []
  const risks = []

  if (matchedSkin) {
    reasons.push(`产品标记适合${skinLabels[profile.skin_type] || '你的肤质'}。`)
  } else {
    risks.push(`产品未明确标记适合${skinLabels[profile.skin_type] || '你的肤质'}，建议先小范围试用。`)
  }

  if (matchedConcerns.length) {
    reasons.push(`与你关注的${matchedConcerns.map((c) => concernLabels[c]).join('、')}有匹配。`)
  } else if (profile.concerns?.length) {
    risks.push('它和你当前重点关注的问题匹配度不高，可能不是优先购买项。')
  }

  if (profile.skin_type === 'sensitive' && /(水杨酸|视黄醇|高浓度|控油|清洁泥膜)/.test(text)) {
    risks.push('敏感肌使用功效型或强清洁产品要降低频率，先做局部测试。')
  }
  if (product.category === 'sunscreen') {
    reasons.push('防晒属于全年基础品类，通常有较高使用优先级。')
  }
  if (inCabinet) {
    reasons.push('这款产品已经在你的产品库中，AI 可以在后续搭配方案里优先考虑它。')
  }
  if (!risks.length) risks.push('暂无明显风险，但首次使用仍建议先观察 24 小时。')

  const level = score >= 80 ? 'high' : score >= 60 ? 'medium' : 'low'
  const conclusion = score >= 80
    ? inCabinet ? '你已经拥有这款产品，建议优先研究怎么用好它，而不是重复购买。' : '整体比较适合你，可以作为优先考虑的产品。'
    : score >= 60
      ? '可以考虑，但建议结合预算、已有产品和试用反馈再决定。'
      : '当前不建议优先购买，除非你有明确使用场景或试用反馈良好。'
  const usage = product.category === 'sunscreen'
    ? '日间护肤最后一步使用，外出前涂足量，户外场景注意补涂。'
    : product.category === 'essence'
      ? '建议从低频开始，先每周 2-3 次，观察耐受后再调整频率。'
      : '按该品类的常规步骤使用，首次使用先少量试用，避免同时叠加太多新产品。'

  return { score, level, conclusion, reasons, risks, usage, inCabinet }
}

const selectedAnalysis = computed(() => selectedProduct.value ? analyzeProduct(selectedProduct.value) : null)

function openProduct(product) {
  selectedProduct.value = product
}

function closeProduct() {
  selectedProduct.value = null
}

function addSelectedToCabinet() {
  if (!selectedProduct.value) return

  const item = mapCatalogProductToCabinet(selectedProduct.value)
  const result = addCabinetProduct(userStore.userId, cabinetProducts.value, item)
  if (!result.ok) {
    appStore.showToast('这款产品已经在你的产品库里了', 'warning')
    return
  }

  cabinetProducts.value = result.products
  appStore.showToast('已加入我的产品库，后续 AI 会优先参考它', 'success')
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

onMounted(async () => {
  await userStore.fetchLatest()
  refreshCabinet()
  await fetchData()
})
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

.profile-nudge {
  margin-bottom: 18px;
  padding: 14px 16px;
  border: 1px solid $mint-pale;
  border-radius: $radius-sm;
  background: $mint-bg;
  color: $text-secondary;
  font-size: 14px;

  a {
    color: $mint-dark;
    font-weight: 700;
    margin-left: 8px;
  }
}

.product-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(23, 43, 36, 0.42);
}

.product-modal {
  position: relative;
  width: min(680px, 100%);
  max-height: min(720px, calc(100vh - 48px));
  overflow: auto;
  background: $white;
  border-radius: $radius;
  box-shadow: $shadow-hover;
  padding: 28px;

  .modal-close {
    position: absolute;
    top: 16px;
    right: 16px;
    width: 32px;
    height: 32px;
    border: 1px solid $mint-pale;
    border-radius: 50%;
    background: $white;
    color: $text-secondary;
    font-size: 22px;
    line-height: 1;
    cursor: pointer;
  }

  .modal-icon {
    width: 56px;
    height: 56px;
    display: grid;
    place-items: center;
    margin-bottom: 16px;
    border-radius: 14px;
    background: $mint-bg;
    font-size: 28px;
  }

  .modal-heading {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    margin-bottom: 22px;

    h3 {
      color: $text-primary;
      font-size: 24px;
      margin-bottom: 8px;
    }

    p {
      color: $text-light;
      line-height: 1.6;
    }
  }

  .modal-score {
    width: 82px;
    height: 82px;
    border-radius: 18px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;

    strong {
      font-size: 28px;
      line-height: 1;
    }

    span {
      margin-top: 4px;
      font-size: 12px;
    }

    &.high {
      background: #e2f4ed;
      color: #147a55;
    }

    &.medium {
      background: #fff4d6;
      color: #946600;
    }

    &.low {
      background: #ffe6e2;
      color: #b54432;
    }
  }

  section {
    padding: 16px 0;
    border-top: 1px solid $mint-pale;

    h4 {
      margin-bottom: 8px;
      color: $mint-dark;
      font-size: 15px;
    }

    p,
    li {
      color: $text-secondary;
      font-size: 14px;
      line-height: 1.7;
    }

    ul {
      padding-left: 18px;
    }
  }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding-top: 16px;
    border-top: 1px solid $mint-pale;
  }

  .modal-empty {
    padding: 18px;
    border-radius: $radius-sm;
    background: $mint-bg;
    color: $text-secondary;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
  }
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: $text-light;
  font-size: 16px;
}

@media (max-width: 640px) {
  .product-modal-backdrop {
    align-items: flex-end;
    padding: 12px;
  }

  .product-modal {
    max-height: calc(100vh - 24px);
    padding: 22px;

    .modal-heading {
      flex-direction: column;
    }

    .modal-score {
      width: 100%;
      height: 64px;
      flex-direction: row;
      gap: 8px;
    }

    .modal-empty {
      align-items: stretch;
      flex-direction: column;
    }

    .modal-actions {
      flex-direction: column;
    }
  }
}
</style>
