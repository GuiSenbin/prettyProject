// 产品库分类统计：基于接口返回的真实分类生成筛选项。
export const CABINET_CATEGORY_ORDER = ['洁面', '精华', '水乳面霜', '防晒', '面膜', '底妆', '彩妆']

export function productCategory(item) {
  return item?.product?.category || ''
}

export function buildCabinetCategoryFilters(products = []) {
  const counts = products.reduce((result, item) => {
    const category = productCategory(item)
    if (!category) return result
    result.set(category, (result.get(category) || 0) + 1)
    return result
  }, new Map())
  const knownCategories = CABINET_CATEGORY_ORDER.map(name => ({
    name,
    count: counts.get(name) || 0,
  }))
  const extraCategories = Array.from(counts.keys())
    .filter(name => !CABINET_CATEGORY_ORDER.includes(name))
    .sort((a, b) => a.localeCompare(b, 'zh-Hans-CN'))
    .map(name => ({
      name,
      count: counts.get(name) || 0,
    }))
  return [...knownCategories, ...extraCategories]
}

export function filterCabinetProducts(products = [], category = '') {
  if (!category) return products
  return products.filter(item => productCategory(item) === category)
}
