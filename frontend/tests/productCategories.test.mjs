import { buildCabinetCategoryFilters, filterCabinetProducts } from '../src/utils/productCategories.js'

function assertEqual(actual, expected) {
  if (actual !== expected) {
    throw new Error(`Expected ${expected}, received ${actual}`)
  }
}

function assertDeepEqual(actual, expected) {
  const actualJson = JSON.stringify(actual)
  const expectedJson = JSON.stringify(expected)
  if (actualJson !== expectedJson) {
    throw new Error(`Expected ${expectedJson}, received ${actualJson}`)
  }
}

const products = [
  { id: 1, product: { category: '彩妆' } },
  { id: 2, product: { category: '水乳面霜' } },
  { id: 3, product: { category: '水乳面霜' } },
  { id: 4, product: { category: '洁面' } },
  { id: 5, product: { category: '精华' } },
]

const filters = buildCabinetCategoryFilters(products)

assertDeepEqual(
  filters.filter(item => item.count > 0).map(item => [item.name, item.count]),
  [
    ['洁面', 1],
    ['精华', 1],
    ['水乳面霜', 2],
    ['彩妆', 1],
  ],
)
assertEqual(filterCabinetProducts(products, '水乳面霜').length, 2)
assertEqual(filterCabinetProducts(products, '彩妆').length, 1)
assertEqual(filterCabinetProducts(products, '').length, 5)
