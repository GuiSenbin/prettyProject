const BASE_KEY = 'my_cabinet_products'

const DEFAULT_PRODUCTS = [
  { id: 1, name: '极光透亮平衡柔肤水', category: 'skincare', ingredients: ['酒精', '果酸(AHA)', '烟酰胺'] },
  { id: 2, name: 'B5 密集修护补水面膜', category: 'mask', ingredients: ['玻尿酸', '积雪草', '神经酰胺'] },
  { id: 3, name: '柔焦哑光无瑕粉底液', category: 'makeup', ingredients: ['矿物油', '维生素C(VC)'] },
]

const CATEGORY_MAP = {
  cleanser: 'skincare',
  toner: 'skincare',
  essence: 'skincare',
  lotion: 'skincare',
  sunscreen: 'skincare',
  mask: 'mask',
  foundation: 'makeup',
  lip: 'makeup',
  eye: 'makeup',
}

const INGREDIENT_KEYWORDS = [
  '玻尿酸',
  '神经酰胺',
  '酒精',
  '视黄醇',
  '水杨酸',
  '果酸',
  '维生素C',
  'VC',
  '烟酰胺',
  '积雪草',
  '茶树',
  '高岭土',
]

export const FEEDBACK_OPTIONS = [
  { value: 'love', label: '好用', tone: 'good' },
  { value: 'neutral', label: '无感', tone: 'neutral' },
  { value: 'sting', label: '刺痛', tone: 'warn' },
  { value: 'acne', label: '爆痘', tone: 'bad' },
]

export function getCabinetStorageKey(userId) {
  return userId ? `${BASE_KEY}_${userId}` : BASE_KEY
}

export function loadCabinetProducts(userId) {
  const key = getCabinetStorageKey(userId)
  const raw = localStorage.getItem(key) || (!userId ? null : localStorage.getItem(BASE_KEY))
  if (raw) {
    try {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed)) {
        if (userId && !localStorage.getItem(key)) {
          localStorage.setItem(key, JSON.stringify(parsed))
        }
        return parsed
      }
    } catch (e) {
      console.warn('读取产品库失败', e)
    }
  }

  const products = userId ? [] : DEFAULT_PRODUCTS.map((item) => ({ ...item, imported: false }))
  localStorage.setItem(key, JSON.stringify(products))
  return products
}

export function saveCabinetProducts(userId, products) {
  localStorage.setItem(getCabinetStorageKey(userId), JSON.stringify(products))
}

export function removeCabinetProduct(userId, products, id) {
  const next = products.filter((product) => product.id !== id)
  saveCabinetProducts(userId, next)
  return next
}

export function updateCabinetProductFeedback(userId, products, id, feedbackValue) {
  const next = products.map((product) => {
    if (product.id !== id) return product

    const current = product.feedback || {}
    const feedback = current.value === feedbackValue
      ? null
      : {
        value: feedbackValue,
        updated_at: new Date().toISOString(),
      }

    return { ...product, feedback }
  })
  saveCabinetProducts(userId, next)
  return next
}

export function addCabinetProduct(userId, products, product) {
  const exists = products.some((item) => item.name.trim() === product.name.trim())
  if (exists) {
    return { ok: false, reason: 'exists', products }
  }

  const next = [{ ...product, id: product.id || Date.now() }, ...products]
  saveCabinetProducts(userId, next)
  return { ok: true, products: next }
}

export function mapCatalogProductToCabinet(product) {
  const text = `${product.name || ''} ${product.desc || ''}`
  const ingredients = INGREDIENT_KEYWORDS.filter((keyword) => text.includes(keyword))
  const tags = [...new Set([...(ingredients.length ? ingredients : product.skin_tags || []), product.category_name].filter(Boolean))]

  return {
    id: Date.now(),
    name: product.name,
    category: CATEGORY_MAP[product.category] || 'skincare',
    ingredients: tags.slice(0, 6),
    source: '百科',
  }
}

export function getCabinetProductNames(userId) {
  return loadCabinetProducts(userId).map((product) => product.name)
}

function getProductText(product) {
  return `${product.name || ''} ${(product.ingredients || []).join(' ')} ${product.category || ''}`.toLowerCase()
}

function detectProductRole(product) {
  const text = getProductText(product)
  if (/洁面|洗面奶|cleanser/.test(text)) return 'cleanser'
  if (/爽肤水|柔肤水|化妆水|toner/.test(text)) return 'toner'
  if (/精华|serum|essence|视黄醇|烟酰胺|维生素c|vc/.test(text)) return 'essence'
  if (/乳液|面霜|霜|lotion|cream|神经酰胺/.test(text)) return 'moisturizer'
  if (/防晒|spf|sunscreen/.test(text)) return 'sunscreen'
  if (/面膜|mask|泥膜/.test(text) || product.category === 'mask') return 'mask'
  if (/粉底|气垫|遮瑕|底妆/.test(text)) return 'foundation'
  if (/唇|口红|唇釉/.test(text)) return 'lip'
  if (/眼影|眼线|睫毛/.test(text)) return 'eye'
  return product.category === 'makeup' ? 'makeup' : 'skincare'
}

function hasIngredient(product, patterns) {
  const text = getProductText(product)
  return patterns.some((pattern) => text.includes(pattern))
}

function pickFirstByRole(products, role) {
  return products.find((product) => detectProductRole(product) === role)
}

export function analyzeCabinet(products, profile = {}) {
  const items = products || []
  const lovedProducts = items.filter((product) => product.feedback?.value === 'love')
  const neutralProducts = items.filter((product) => product.feedback?.value === 'neutral')
  const stingProducts = items.filter((product) => product.feedback?.value === 'sting')
  const acneProducts = items.filter((product) => product.feedback?.value === 'acne')
  const roleGroups = items.reduce((acc, product) => {
    const role = detectProductRole(product)
    acc[role] = acc[role] || []
    acc[role].push(product)
    return acc
  }, {})

  const morningSteps = [
    { key: 'cleanser', label: '洁面', product: pickFirstByRole(items, 'cleanser'), fallback: '温和洁面，避免过度清洁。' },
    { key: 'toner', label: '爽肤水', product: pickFirstByRole(items, 'toner'), fallback: '补一款温和保湿型化妆水。' },
    { key: 'essence', label: '精华', product: pickFirstByRole(items, 'essence'), fallback: '按主要诉求选择一款精华即可，先不要叠太多。' },
    { key: 'moisturizer', label: '乳液/面霜', product: pickFirstByRole(items, 'moisturizer'), fallback: '补一款基础保湿产品，用来稳定屏障。' },
    { key: 'sunscreen', label: '防晒', product: pickFirstByRole(items, 'sunscreen'), fallback: '缺少防晒，这是最优先补齐的一步。' },
  ]

  const eveningSteps = [
    { key: 'cleanser', label: '清洁', product: pickFirstByRole(items, 'cleanser'), fallback: '夜间至少保证温和清洁。' },
    { key: 'toner', label: '爽肤水', product: pickFirstByRole(items, 'toner'), fallback: '可选步骤，皮肤不稳定时不用强求。' },
    { key: 'essence', label: '功效精华', product: pickFirstByRole(items, 'essence'), fallback: '先根据痘痘、提亮、抗老等主诉补一款。' },
    { key: 'moisturizer', label: '修护保湿', product: pickFirstByRole(items, 'moisturizer'), fallback: '夜间需要一款保湿收尾产品。' },
    { key: 'mask', label: '周期护理', product: pickFirstByRole(items, 'mask'), fallback: '面膜不是必需，缺基础流程时先不急着买。' },
  ]

  const missing = morningSteps
    .filter((step) => !step.product && ['cleanser', 'moisturizer', 'sunscreen'].includes(step.key))
    .map((step) => ({
      key: step.key,
      label: step.label,
      priority: step.key === 'sunscreen' ? '高' : '中',
      advice: step.fallback,
    }))

  const duplicates = Object.entries(roleGroups)
    .filter(([, group]) => group.length >= 2)
    .map(([role, group]) => ({
      role,
      label: {
        cleanser: '洁面',
        toner: '爽肤水',
        essence: '精华',
        moisturizer: '乳液/面霜',
        sunscreen: '防晒',
        mask: '面膜',
        foundation: '底妆',
        lip: '唇妆',
        eye: '眼妆',
        makeup: '彩妆',
        skincare: '护肤品',
      }[role] || '同类产品',
      products: group.map((product) => product.name),
      advice: '同类产品较多，建议先用完已开封产品，再考虑补买。',
    }))

  const conflicts = []
  const acidProducts = items.filter((product) => hasIngredient(product, ['水杨酸', '果酸', 'aha']))
  const retinolProducts = items.filter((product) => hasIngredient(product, ['视黄醇', 'a醇']))
  const vcProducts = items.filter((product) => hasIngredient(product, ['维生素c', 'vc']))
  const alcoholProducts = items.filter((product) => hasIngredient(product, ['酒精']))
  const clayProducts = items.filter((product) => hasIngredient(product, ['高岭土', '泥膜', '粘土']))

  if (acidProducts.length && retinolProducts.length) {
    conflicts.push({
      level: '高',
      title: '酸类与视黄醇不要同晚叠加',
      products: [...acidProducts, ...retinolProducts].map((product) => product.name),
      advice: '建议错开日期使用，先建立耐受，再逐步调整频率。',
    })
  }
  if (profile.skin_type === 'sensitive' && [...acidProducts, ...retinolProducts, ...alcoholProducts].length) {
    conflicts.push({
      level: '高',
      title: '敏感肌功效刺激风险',
      products: [...acidProducts, ...retinolProducts, ...alcoholProducts].map((product) => product.name),
      advice: '敏感肌先以修护保湿为主，功效型产品从低频和局部测试开始。',
    })
  }
  if (profile.skin_type === 'dry' && clayProducts.length) {
    conflicts.push({
      level: '中',
      title: '干皮强清洁后容易紧绷',
      products: clayProducts.map((product) => product.name),
      advice: '清洁面膜降低频率，使用后立刻补水和封闭保湿。',
    })
  }
  if (profile.skin_type === 'oily' && items.some((product) => hasIngredient(product, ['矿物油', '可可脂']))) {
    conflicts.push({
      level: '中',
      title: '油痘肌注意封闭性成分',
      products: items.filter((product) => hasIngredient(product, ['矿物油', '可可脂'])).map((product) => product.name),
      advice: '容易闷痘时先减少厚重底妆或高封闭产品的使用频率。',
    })
  }
  if (vcProducts.length && acidProducts.length) {
    conflicts.push({
      level: '中',
      title: '提亮类产品不宜一次叠太满',
      products: [...vcProducts, ...acidProducts].map((product) => product.name),
      advice: '先选一种作为主力，避免为了提亮同时叠加多种刺激源。',
    })
  }

  if (stingProducts.length) {
    conflicts.push({
      level: '高',
      title: '已有刺痛反馈，先暂停或降频',
      products: stingProducts.map((product) => product.name),
      advice: '这类真实反馈比通用规则更重要。建议暂停叠加功效产品，等皮肤稳定后再低频尝试。',
    })
  }
  if (acneProducts.length) {
    conflicts.push({
      level: '高',
      title: '已有爆痘反馈，暂不建议继续加量',
      products: acneProducts.map((product) => product.name),
      advice: '先停用观察，后续推荐会降低这类产品的优先级。',
    })
  }

  const feedbackInsights = []
  if (lovedProducts.length) {
    feedbackInsights.push({
      level: '正向',
      title: '优先保留',
      products: lovedProducts.map((product) => product.name),
      advice: '这些产品有正向反馈，后续搭配方案可以优先围绕它们展开。',
    })
  }
  if (neutralProducts.length) {
    feedbackInsights.push({
      level: '观察',
      title: '效果不明显',
      products: neutralProducts.map((product) => product.name),
      advice: '无感产品不一定没用，但不是补买优先项。用完后再决定是否替换。',
    })
  }
  if (stingProducts.length || acneProducts.length) {
    feedbackInsights.push({
      level: '避雷',
      title: '真实负反馈',
      products: [...stingProducts, ...acneProducts].map((product) => product.name),
      advice: '已经出现不适反馈，后续推荐应降低同类功效或同类质地的优先级。',
    })
  }

  const score = Math.min(100, Math.max(20,
    40 +
    morningSteps.filter((step) => step.product).length * 8 +
    eveningSteps.filter((step) => step.product).length * 5 -
    conflicts.filter((item) => item.level === '高').length * 10 -
    duplicates.length * 3 +
    lovedProducts.length * 4 -
    (stingProducts.length + acneProducts.length) * 8,
  ))

  return {
    score,
    morningSteps,
    eveningSteps,
    missing,
    duplicates,
    conflicts,
    feedbackInsights,
    summary: items.length
      ? `当前产品库已覆盖 ${morningSteps.filter((step) => step.product).length}/5 个日间关键步骤。`
      : '产品库为空，先登记手头产品后才能生成搭配方案。',
  }
}
