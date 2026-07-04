<template>
  <div class="cabinet-page">
    <div class="page-header">
      <div class="section-hero">
        <h2 class="page-title">我的美妆产品库</h2>
        <p class="page-desc">登记你的护肤与美妆囤货，AI 助手将优先从你的产品库中搭配推荐，并提供智能避雷建议。</p>
      </div>
      <button class="btn btn-primary btn-add" @click="showAddModal = true">
        <span>+</span> 添加产品
      </button>
    </div>

    <section class="smart-panel">
      <div class="smart-summary">
        <div class="score-ring" :class="scoreLevel">
          <strong>{{ cabinetAnalysis.score }}</strong>
          <span>完整度</span>
        </div>
        <div>
          <h3>产品库智能搭配</h3>
          <p>{{ cabinetAnalysis.summary }}</p>
        </div>
      </div>

      <div class="routine-grid">
        <div class="routine-card">
          <div class="routine-head">
            <span>🌤</span>
            <h4>日间流程</h4>
          </div>
          <div class="step-list">
            <div v-for="step in cabinetAnalysis.morningSteps" :key="`am-${step.key}`" class="routine-step" :class="{ missing: !step.product }">
              <span class="step-label">{{ step.label }}</span>
              <strong>{{ step.product?.name || '待补齐' }}</strong>
              <small>{{ step.product ? '来自我的产品库' : step.fallback }}</small>
            </div>
          </div>
        </div>

        <div class="routine-card">
          <div class="routine-head">
            <span>🌙</span>
            <h4>夜间流程</h4>
          </div>
          <div class="step-list">
            <div v-for="step in cabinetAnalysis.eveningSteps" :key="`pm-${step.key}`" class="routine-step" :class="{ missing: !step.product }">
              <span class="step-label">{{ step.label }}</span>
              <strong>{{ step.product?.name || '待补齐' }}</strong>
              <small>{{ step.product ? '来自我的产品库' : step.fallback }}</small>
            </div>
          </div>
        </div>
      </div>

      <div class="insight-grid">
        <div class="insight-card">
          <h4>缺口优先级</h4>
          <div v-if="cabinetAnalysis.missing.length" class="insight-list">
            <div v-for="item in cabinetAnalysis.missing" :key="item.key" class="insight-item">
              <span class="priority">{{ item.priority }}</span>
              <div>
                <strong>{{ item.label }}</strong>
                <p>{{ item.advice }}</p>
              </div>
            </div>
          </div>
          <p v-else class="quiet-text">基础护肤步骤已经比较完整，先用好已有产品。</p>
        </div>

        <div class="insight-card">
          <h4>重复购买提醒</h4>
          <div v-if="cabinetAnalysis.duplicates.length" class="insight-list">
            <div v-for="item in cabinetAnalysis.duplicates" :key="item.role" class="insight-item">
              <span class="priority medium">多件</span>
              <div>
                <strong>{{ item.label }}</strong>
                <p>{{ item.products.join('、') }}</p>
                <small>{{ item.advice }}</small>
              </div>
            </div>
          </div>
          <p v-else class="quiet-text">暂未发现明显同类囤货，购买结构比较克制。</p>
        </div>

        <div class="insight-card">
          <h4>成分冲突提醒</h4>
          <div v-if="cabinetAnalysis.conflicts.length" class="insight-list">
            <div v-for="item in cabinetAnalysis.conflicts" :key="item.title" class="insight-item">
              <span class="priority" :class="{ high: item.level === '高', medium: item.level === '中' }">{{ item.level }}</span>
              <div>
                <strong>{{ item.title }}</strong>
                <p>{{ item.products.join('、') }}</p>
                <small>{{ item.advice }}</small>
              </div>
            </div>
          </div>
          <p v-else class="quiet-text">暂未发现高风险叠加，首次使用新产品仍建议观察耐受。</p>
        </div>

        <div class="insight-card">
          <h4>使用反馈洞察</h4>
          <div v-if="cabinetAnalysis.feedbackInsights.length" class="insight-list">
            <div v-for="item in cabinetAnalysis.feedbackInsights" :key="item.title" class="insight-item">
              <span class="priority" :class="{ high: item.level === '避雷', medium: item.level === '观察', good: item.level === '正向' }">{{ item.level }}</span>
              <div>
                <strong>{{ item.title }}</strong>
                <p>{{ item.products.join('、') }}</p>
                <small>{{ item.advice }}</small>
              </div>
            </div>
          </div>
          <p v-else class="quiet-text">还没有使用反馈。给产品打一次反馈后，后续建议会更准。</p>
        </div>
      </div>
    </section>

    <!-- 筛选标签 -->
    <div class="category-tabs">
      <button v-for="tab in tabs" :key="tab.value" 
              class="tab-item" :class="{ active: activeTab === tab.value }"
              @click="activeTab = tab.value">
        {{ tab.label }}
        <span class="count-badge">{{ getProductCount(tab.value) }}</span>
      </button>
    </div>

    <!-- 产品网格 -->
    <div v-if="filteredProducts.length > 0" class="product-grid">
      <div v-for="product in filteredProducts" :key="product.id" class="product-card" :class="{ 'warning-border': product.alert }">
        <div class="card-header">
          <span class="product-icon">{{ getCategoryIcon(product.category) }}</span>
          <span class="product-category">{{ getCategoryName(product.category) }}</span>
          <button class="btn-delete" @click="handleDelete(product.id)" title="从库中删除">✕</button>
        </div>
        <h3 class="product-name">{{ product.name }}</h3>
        
        <div class="product-ingredients">
          <span v-for="ing in product.ingredients" :key="ing" class="ing-tag">{{ ing }}</span>
        </div>

        <div class="feedback-row">
          <span>使用反馈</span>
          <button v-for="option in feedbackOptions" :key="option.value"
                  type="button"
                  class="feedback-chip"
                  :class="[option.tone, { active: product.feedback?.value === option.value }]"
                  @click="handleFeedback(product.id, option.value)">
            {{ option.label }}
          </button>
        </div>

        <!-- 智能防雷成分避雷警报 -->
        <div v-if="product.alert" class="alert-box">
          <div class="alert-title">⚠️ 避雷建议 ({{ skinTypeLabel }})</div>
          <div class="alert-text">{{ product.alert }}</div>
        </div>
        <div v-else class="success-box">
          <div class="success-text">💚 适合您的肤质使用</div>
        </div>
      </div>
    </div>

    <!-- 空白状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">🧴</div>
      <h3>产品库空空如也</h3>
      <p>立即登记你手头的护肤与彩妆产品，让 AI 开启个性化专属避雷搭配吧！</p>
      <button class="btn btn-primary" @click="showAddModal = true">现在去添加</button>
    </div>

    <!-- 新增产品弹窗 -->
    <div v-if="showAddModal" class="modal-backdrop" @click.self="showAddModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3>登记新产品</h3>
          <button class="btn-close" @click="showAddModal = false">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label for="prod-name">产品名称</label>
            <input id="prod-name" type="text" v-model="newProduct.name" placeholder="例如：雅诗兰黛小棕瓶精华" class="form-input" />
          </div>

          <div class="form-group">
            <label>产品分类</label>
            <div class="category-options">
              <button v-for="cat in categories" :key="cat.value"
                      class="option-btn" :class="{ active: newProduct.category === cat.value }"
                      @click="newProduct.category = cat.value">
                {{ cat.label }}
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>核心成分 / 标签（多选）</label>
            <div class="ingredient-presets">
              <button v-for="ing in presetIngredients" :key="ing"
                      class="preset-btn" :class="{ selected: newProduct.ingredients.includes(ing) }"
                      @click="toggleIngredient(ing)">
                {{ ing }}
              </button>
            </div>
            
            <div class="custom-ing-input">
              <input type="text" v-model="customIngredient" placeholder="手写添加其他成分/标签，按回车加入" 
                     @keydown.enter.prevent="addCustomIngredient" class="form-input" />
              <button class="btn-add-ing" @click="addCustomIngredient">添加</button>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-outline" @click="showAddModal = false">取消</button>
          <button class="btn btn-primary" @click="handleSave" :disabled="!newProduct.name">保存至产品库</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import {
  FEEDBACK_OPTIONS,
  addCabinetProduct,
  analyzeCabinet,
  loadCabinetProducts,
  removeCabinetProduct,
  updateCabinetProductFeedback,
} from '@/utils/cabinet'

const userStore = useUserStore()
const appStore = useAppStore()

const showAddModal = ref(false)
const activeTab = ref('all')
const products = ref([])
const customIngredient = ref('')
const feedbackOptions = FEEDBACK_OPTIONS

const tabs = [
  { value: 'all', label: '全部' },
  { value: 'skincare', label: '护肤品' },
  { value: 'mask', label: '面膜' },
  { value: 'makeup', label: '彩妆' }
]

const categories = [
  { value: 'skincare', label: '🧴 护肤品' },
  { value: 'mask', label: '🎭 面膜' },
  { value: 'makeup', label: '💄 彩妆' }
]

const presetIngredients = [
  '玻尿酸', '神经酰胺', '酒精', '视黄醇(A醇)', '水杨酸', 
  '果酸(AHA)', '矿物油', '维生素C(VC)', '烟酰胺', '积雪草', 
  '茶树精油', '洋甘菊', '可可脂', '高岭土'
]

const newProduct = ref({
  name: '',
  category: 'skincare',
  ingredients: []
})

const cabinetAnalysis = computed(() => analyzeCabinet(products.value, userStore.profile || {}))
const scoreLevel = computed(() => {
  if (cabinetAnalysis.value.score >= 80) return 'high'
  if (cabinetAnalysis.value.score >= 60) return 'medium'
  return 'low'
})

// 肤质标签
const skinTypeLabel = computed(() => {
  const map = {
    dry: '干性肌肤',
    oily: '油性肌肤',
    combination: '混合性肌肤',
    normal: '中性肌肤',
    sensitive: '敏感性肌肤'
  }
  return map[userStore.profile?.skin_type] || '未录入肤质'
})

// 加载列表
onMounted(async () => {
  await userStore.fetchLatest()
  loadProducts()
})

function loadProducts() {
  products.value = loadCabinetProducts(userStore.userId)
}

// 智能防雷成分评估逻辑 (第一性原理)
const processedProducts = computed(() => {
  const skinType = userStore.profile?.skin_type || ''
  
  return products.value.map(p => {
    let alert = ''
    const lowerIngs = p.ingredients.map(i => i.toLowerCase())

    if (skinType === 'sensitive') {
      // 敏感肌避雷警报
      const dangerous = []
      if (lowerIngs.some(i => i.includes('酒精'))) dangerous.push('酒精')
      if (lowerIngs.some(i => i.includes('视黄醇') || i.includes('a醇'))) dangerous.push('视黄醇(A醇)')
      if (lowerIngs.some(i => i.includes('水杨酸'))) dangerous.push('水杨酸')
      if (lowerIngs.some(i => i.includes('果酸'))) dangerous.push('果酸')

      if (dangerous.length > 0) {
        alert = `该产品含有 ${dangerous.join('、')}，可能破坏角质屏障引发敏感刺痛，建议敏感肌停用或进行局部测试。`
      }
    } else if (skinType === 'oily') {
      // 油性肌致痘堵塞毛孔警告
      const dangerous = []
      if (lowerIngs.some(i => i.includes('矿物油'))) dangerous.push('矿物油')
      if (lowerIngs.some(i => i.includes('可可脂'))) dangerous.push('可可脂')

      if (dangerous.length > 0) {
        alert = `该产品含有高封闭性的 ${dangerous.join('、')}，极易诱发粉刺和闷痘，油痘肌建议慎用。`
      }
    } else if (skinType === 'dry') {
      // 干性肌过度剥脱干燥警告
      const dangerous = []
      if (lowerIngs.some(i => i.includes('水杨酸'))) dangerous.push('水杨酸')
      if (lowerIngs.some(i => i.includes('高岭土') || i.includes('粘土'))) dangerous.push('吸油粘土成分')

      if (dangerous.length > 0) {
        alert = `该产品包含 ${dangerous.join('、')}，具有强力吸油或角质剥脱作用，干性肌使用后易起皮紧绷，需加强后续锁水。`
      }
    }

    return { ...p, alert }
  })
})

const filteredProducts = computed(() => {
  if (activeTab.value === 'all') {
    return processedProducts.value
  }
  return processedProducts.value.filter(p => p.category === activeTab.value)
})

function getProductCount(category) {
  if (category === 'all') return products.value.length
  return products.value.filter(p => p.category === category).length
}

function getCategoryIcon(cat) {
  const map = { skincare: '🧴', mask: '🎭', makeup: '💄' }
  return map[cat] || '📦'
}

function getCategoryName(cat) {
  const map = { skincare: '护肤品', mask: '面膜', makeup: '彩妆' }
  return map[cat] || '其他'
}

// 标签切换
function toggleIngredient(ing) {
  const idx = newProduct.value.ingredients.indexOf(ing)
  if (idx > -1) {
    newProduct.value.ingredients.splice(idx, 1)
  } else {
    newProduct.value.ingredients.push(ing)
  }
}

// 自定义成分输入
function addCustomIngredient() {
  const text = customIngredient.value.trim()
  if (text) {
    if (!newProduct.value.ingredients.includes(text)) {
      newProduct.value.ingredients.push(text)
    }
    customIngredient.value = ''
  }
}

// 保存产品
function handleSave() {
  if (!newProduct.value.name.trim()) return
  
  const item = {
    id: Date.now(),
    name: newProduct.value.name.trim(),
    category: newProduct.value.category,
    ingredients: [...newProduct.value.ingredients]
  }

  const result = addCabinetProduct(userStore.userId, products.value, item)
  if (!result.ok) {
    appStore.showToast('产品库里已经有这款产品了', 'warning')
    return
  }
  products.value = result.products
  
  // 重置表单
  newProduct.value = { name: '', category: 'skincare', ingredients: [] }
  showAddModal.value = false
  appStore.showToast('产品成功存入库中！🌱', 'success')
}

// 删除产品
function handleDelete(id) {
  if (confirm('确认要将该产品从您的产品库中移除吗？')) {
    products.value = removeCabinetProduct(userStore.userId, products.value, id)
    appStore.showToast('已移除产品', 'info')
  }
}

function handleFeedback(id, feedbackValue) {
  products.value = updateCabinetProductFeedback(userStore.userId, products.value, id, feedbackValue)
  const product = products.value.find(item => item.id === id)
  if (product?.feedback?.value === feedbackValue) {
    appStore.showToast('已记录使用反馈，后续建议会参考它', 'success')
  } else {
    appStore.showToast('已取消该产品的使用反馈', 'info')
  }
}
</script>

<style lang="scss" scoped>
.cabinet-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: calc(78px + env(safe-area-inset-top)) 18px 34px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;

  .section-hero {
    flex: 1;
    margin-bottom: 0;
  }

  .btn-add {
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 600;
    box-shadow: 0 4px 14px rgba(26, 122, 92, 0.25);
    
    span {
      font-size: 20px;
      line-height: 1;
    }
  }
}

.smart-panel {
  margin-bottom: 28px;
  padding: 24px;
  background: $white;
  border: 1px solid $mint-pale;
  border-radius: $radius;
  box-shadow: $shadow;
}

.smart-summary {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 22px;

  h3 {
    font-size: 20px;
    color: $text-primary;
    margin-bottom: 6px;
  }

  p {
    color: $text-light;
    font-size: 14px;
    line-height: 1.6;
  }
}

.score-ring {
  width: 78px;
  height: 78px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;

  strong {
    font-size: 24px;
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

.routine-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 18px;
}

.routine-card,
.insight-card {
  border: 1px solid $mint-pale;
  border-radius: $radius-sm;
  background: $bg-light;
  padding: 16px;
}

.routine-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;

  h4 {
    color: $mint-dark;
    font-size: 15px;
  }
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.routine-step {
  display: grid;
  grid-template-columns: 76px 1fr;
  gap: 4px 10px;
  padding: 10px 12px;
  border-radius: 8px;
  background: $white;

  .step-label {
    color: $mint-primary;
    font-size: 13px;
    font-weight: 700;
  }

  strong {
    color: $text-primary;
    font-size: 14px;
    min-width: 0;
  }

  small {
    grid-column: 2;
    color: $text-light;
    line-height: 1.5;
  }

  &.missing {
    background: #fffaf0;

    strong {
      color: #946600;
    }
  }
}

.insight-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.insight-card {
  h4 {
    color: $mint-dark;
    font-size: 15px;
    margin-bottom: 12px;
  }
}

.insight-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.insight-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;

  strong {
    display: block;
    color: $text-primary;
    font-size: 14px;
    margin-bottom: 4px;
  }

  p,
  small {
    display: block;
    color: $text-light;
    font-size: 12px;
    line-height: 1.5;
  }
}

.priority {
  min-width: 34px;
  padding: 3px 6px;
  border-radius: 8px;
  background: #fff4d6;
  color: #946600;
  text-align: center;
  font-size: 12px;
  font-weight: 700;

  &.high {
    background: #ffe6e2;
    color: #b54432;
  }

  &.medium {
    background: #fff4d6;
    color: #946600;
  }

  &.good {
    background: #e2f4ed;
    color: #147a55;
  }
}

.quiet-text {
  color: $text-light;
  font-size: 13px;
  line-height: 1.6;
}

.category-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  border-bottom: 1px solid $mint-pale;
  padding-bottom: 12px;

  .tab-item {
    background: none;
    border: none;
    padding: 8px 18px;
    font-size: 15px;
    font-weight: 500;
    color: $text-secondary;
    cursor: pointer;
    border-radius: 8px;
    transition: $transition;
    display: flex;
    align-items: center;
    gap: 8px;

    &.active {
      background: $mint-primary;
      color: $white;

      .count-badge {
        background: rgba(255, 255, 255, 0.25);
        color: $white;
      }
    }

    &:hover:not(.active) {
      background: $mint-bg;
      color: $mint-primary;
    }

    .count-badge {
      font-size: 12px;
      background: $mint-bg;
      color: $mint-primary;
      padding: 2px 8px;
      border-radius: 12px;
      font-weight: 600;
    }
  }
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.product-card {
  background: $white;
  border: 1px solid $mint-pale;
  border-radius: $radius;
  padding: 24px;
  box-shadow: $shadow;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: $transition;

  &:hover {
    transform: translateY(-4px);
    box-shadow: $shadow-hover;
  }

  &.warning-border {
    border-color: #ffd666;
    box-shadow: 0 4px 18px rgba(212, 136, 6, 0.08);
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;

    .product-icon {
      font-size: 20px;
    }

    .product-category {
      font-size: 13px;
      color: $text-light;
      font-weight: 500;
    }

    .btn-delete {
      margin-left: auto;
      background: none;
      border: none;
      color: $text-light;
      cursor: pointer;
      font-size: 14px;
      opacity: 0.5;
      transition: $transition;

      &:hover {
        opacity: 1;
        color: #ff4d4f;
      }
    }
  }

  .product-name {
    font-size: 18px;
    font-weight: 700;
    color: $text-primary;
    margin-bottom: 16px;
  }

  .product-ingredients {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 16px;

    .ing-tag {
      font-size: 12px;
      background: #f5f5f5;
      color: $text-secondary;
      padding: 3px 8px;
      border-radius: 6px;
    }
  }

  .feedback-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
    margin-bottom: 16px;

    > span {
      width: 100%;
      color: $text-light;
      font-size: 12px;
      font-weight: 600;
    }
  }

  .feedback-chip {
    padding: 5px 10px;
    border: 1px solid $mint-pale;
    border-radius: 14px;
    background: $white;
    color: $text-secondary;
    font-size: 12px;
    cursor: pointer;
    transition: $transition;

    &:hover {
      border-color: $mint-primary;
      color: $mint-primary;
    }

    &.active.good {
      background: #e2f4ed;
      border-color: #91d5b8;
      color: #147a55;
      font-weight: 700;
    }

    &.active.neutral {
      background: #f4f5f5;
      border-color: #d9d9d9;
      color: $text-secondary;
      font-weight: 700;
    }

    &.active.warn {
      background: #fff4d6;
      border-color: #ffd666;
      color: #946600;
      font-weight: 700;
    }

    &.active.bad {
      background: #ffe6e2;
      border-color: #ffb4a8;
      color: #b54432;
      font-weight: 700;
    }
  }

  .alert-box {
    margin-top: auto;
    background: #fffbe6;
    border: 1px solid #ffe58f;
    border-radius: $radius-sm;
    padding: 12px;

    .alert-title {
      font-size: 13px;
      font-weight: 700;
      color: #d48806;
      margin-bottom: 4px;
    }

    .alert-text {
      font-size: 12px;
      color: #8c5d00;
      line-height: 1.4;
    }
  }

  .success-box {
    margin-top: auto;
    background: #f6ffed;
    border: 1px solid #b7eb8f;
    border-radius: $radius-sm;
    padding: 10px 12px;

    .success-text {
      font-size: 13px;
      color: $mint-dark;
      font-weight: 500;
    }
  }
}

.empty-state {
  text-align: center;
  padding: 60px 24px;
  background: $white;
  border-radius: $radius;
  box-shadow: $shadow;
  border: 1px dashed $mint-pale;

  .empty-icon {
    font-size: 64px;
    margin-bottom: 16px;
  }

  h3 {
    font-size: 20px;
    font-weight: 700;
    color: $text-primary;
    margin-bottom: 8px;
  }

  p {
    font-size: 14px;
    color: $text-light;
    max-width: 400px;
    margin: 0 auto 24px;
    line-height: 1.6;
  }
}

/* 模态框弹层样式 */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-card {
  background: $white;
  border-radius: $radius;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  animation: modalShow 0.3s ease;

  .modal-header {
    padding: 20px 24px;
    border-bottom: 1px solid $mint-pale;
    display: flex;
    justify-content: space-between;
    align-items: center;

    h3 {
      font-size: 18px;
      font-weight: 700;
      color: $text-primary;
    }

    .btn-close {
      background: none;
      border: none;
      font-size: 18px;
      color: $text-light;
      cursor: pointer;
      &:hover { color: $text-primary; }
    }
  }

  .modal-body {
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    max-height: 400px;
    overflow-y: auto;
  }

  .modal-footer {
    padding: 16px 24px;
    border-top: 1px solid $mint-pale;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;

  label {
    font-size: 14px;
    color: $text-secondary;
    font-weight: 600;
  }

  .form-input {
    width: 100%;
    padding: 10px 14px;
    border: 1px solid $mint-pale;
    border-radius: $radius-sm;
    font-size: 14px;
    transition: $transition;

    &:focus {
      border-color: $mint-primary;
      box-shadow: 0 0 0 3px rgba(45, 143, 111, 0.15);
    }
  }
}

.category-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;

  .option-btn {
    padding: 10px;
    border: 1px solid $mint-pale;
    border-radius: $radius-sm;
    background: $white;
    font-size: 13px;
    cursor: pointer;
    transition: $transition;

    &.active {
      border-color: $mint-primary;
      background: $mint-bg;
      color: $mint-primary;
      font-weight: 600;
    }
  }
}

.ingredient-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;

  .preset-btn {
    padding: 6px 12px;
    border: 1px solid $mint-pale;
    border-radius: 20px;
    background: $white;
    font-size: 12px;
    color: $text-secondary;
    cursor: pointer;
    transition: $transition;

    &.selected {
      background: $mint-primary;
      border-color: $mint-primary;
      color: $white;
    }

    &:hover:not(.selected) {
      background: $mint-bg;
      color: $mint-primary;
    }
  }
}

.custom-ing-input {
  display: flex;
  gap: 10px;

  .btn-add-ing {
    background: $mint-bg;
    color: $mint-primary;
    border: 1px solid $mint-pale;
    padding: 0 16px;
    border-radius: $radius-sm;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: $transition;
    white-space: nowrap;

    &:hover {
      background: $mint-primary;
      color: $white;
      border-color: $mint-primary;
    }
  }
}

@keyframes modalShow {
  from { transform: scale(0.9) translateY(20px); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; }
}

@media (max-width: 768px) {
  .cabinet-page {
    padding: calc(78px + env(safe-area-inset-top)) 14px 34px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
    margin-bottom: 18px;

    .btn-add {
      width: 100%;
      justify-content: center;
    }
  }

  .smart-panel {
    padding: 16px;
    margin-bottom: 20px;
    border-radius: 14px;
    box-shadow: none;
  }

  .smart-summary {
    align-items: flex-start;
    gap: 14px;

    h3 {
      font-size: 18px;
    }
  }

  .score-ring {
    width: 66px;
    height: 66px;

    strong {
      font-size: 21px;
    }
  }

  .routine-grid,
  .insight-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .routine-step {
    grid-template-columns: 64px 1fr;
    padding: 10px;
  }

  .category-tabs {
    margin: 0 -14px 18px;
    overflow-x: auto;
    padding: 0 14px 10px;
    gap: 8px;

    .tab-item {
      flex: 0 0 auto;
      white-space: nowrap;
      padding: 8px 14px;
    }
  }

  .product-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .product-card {
    padding: 18px;
    border-radius: 14px;
    box-shadow: none;

    &:hover {
      transform: none;
    }

    .product-name {
      font-size: 17px;
      margin-bottom: 12px;
    }
  }

  .empty-state {
    padding: 42px 18px;
    box-shadow: none;

    .empty-icon {
      font-size: 48px;
    }
  }

  .modal-backdrop {
    align-items: flex-end;
    padding: 10px;
  }

  .modal-card {
    max-width: none;
    max-height: calc(100dvh - 20px);
    border-radius: 18px 18px 14px 14px;

    .modal-header {
      padding: 18px;
    }

    .modal-body {
      padding: 18px;
      max-height: min(62dvh, 520px);
    }

    .modal-footer {
      display: grid;
      grid-template-columns: 1fr;
      padding: 14px 18px calc(14px + env(safe-area-inset-bottom));
    }
  }

  .category-options {
    grid-template-columns: 1fr;
  }

  .custom-ing-input {
    flex-direction: column;

    .btn-add-ing {
      min-height: 42px;
    }
  }
}
</style>
