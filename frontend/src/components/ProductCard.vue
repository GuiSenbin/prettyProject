<template>
  <button class="product-card" type="button" @click="$emit('select', product)">
    <div class="product-card-head">
      <div class="product-title-group">
        <div class="product-icon">{{ product.icon || 'P' }}</div>
        <h4>{{ product.name }}</h4>
        <div class="product-category-tag">{{ product.category_name }}</div>
      </div>
      <div v-if="analysis" class="fit-score" :class="analysis.level">
        <strong>{{ analysis.score }}</strong>
        <span>AI分</span>
      </div>
    </div>
    <p>{{ product.desc }}</p>
    <div v-if="analysis" class="fit-summary">
      {{ analysis.summary }}
    </div>
    <div class="product-skin">
      <span v-for="tag in product.skin_tags" :key="tag">{{ tag }}</span>
    </div>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'

const props = defineProps({
  product: { type: Object, required: true },
})

defineEmits(['select'])

const userStore = useUserStore()

const analysis = computed(() => {
  const profile = userStore.profile
  if (!profile?.skin_type) return null

  const suitable = props.product.suitable || []
  const matchedSkin = suitable.includes(profile.skin_type)
  const matchedConcern = (profile.concerns || []).some((concern) => {
    const text = `${props.product.name} ${props.product.desc}`.toLowerCase()
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
  if (matchedConcern) score += 12
  if (suitable.length >= 5) score += 4
  score = Math.min(score, 96)

  return {
    score,
    level: score >= 80 ? 'high' : score >= 60 ? 'medium' : 'low',
    summary: matchedSkin ? '与你的肤质匹配，建议点开看使用建议' : '肤质匹配度一般，建议先看风险提醒',
  }
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.product-card {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 252, 253, 0.9));
  border-radius: 16px;
  padding: 20px;
  box-shadow: $shadow;
  transition: $transition;
  border: 1px solid rgba(207, 238, 241, 0.78);
  text-align: left;
  cursor: pointer;
  width: 100%;
  font-family: inherit;

  &:hover {
    transform: translateY(-3px);
    box-shadow: $shadow-hover;
    border-color: $mint-pale;
  }

  .product-title-group {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
  }

  .product-icon {
    width: 42px;
    height: 42px;
    background: linear-gradient(180deg, $white, $mint-bg);
    border: 1px solid rgba(207, 238, 241, 0.88);
    border-radius: 14px;
    display: grid;
    place-items: center;
    color: $mint-primary;
    font-size: 20px;
    flex: 0 0 auto;
  }

  .product-card-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
  }

  h4 {
    font-size: 15px;
    font-weight: 700;
    color: $text-primary;
    margin-bottom: 4px;
  }

  .product-category-tag {
    font-size: 12px;
    color: $mint-primary;
    margin-bottom: 8px;
  }

  p {
    font-size: 13px;
    color: $text-light;
    line-height: 1.5;
  }

  .fit-score {
    width: 54px;
    height: 54px;
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;

    strong {
      font-size: 17px;
      font-weight: 900;
      line-height: 1;
    }

    span {
      margin-top: 3px;
      font-size: 10px;
      font-weight: 700;
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

  .fit-summary {
    margin-top: 12px;
    padding: 10px 12px;
    background: $bg-light;
    border-radius: $radius-sm;
    color: $text-secondary;
    font-size: 12px;
    line-height: 1.5;
  }

  .product-skin {
    margin-top: 10px;
    display: flex;
    flex-wrap: wrap;
    gap: 4px;

    span {
      padding: 2px 8px;
      background: $mint-bg;
      border-radius: 8px;
      font-size: 11px;
      color: $mint-medium;
    }
  }
}

@media (max-width: 640px) {
  .product-card {
    padding: 16px;
    box-shadow: none;
    border-color: $mint-pale;

    &:hover {
      transform: none;
    }

    .product-icon {
      font-size: 22px;
    }

    .fit-score {
      width: 50px;
      height: 50px;
    }
  }
}
</style>
