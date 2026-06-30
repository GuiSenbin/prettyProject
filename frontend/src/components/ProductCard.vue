<template>
  <div class="product-card">
    <div class="product-icon">{{ product.icon || '📦' }}</div>
    <h4>{{ product.name }}</h4>
    <div class="product-category-tag">{{ product.category_name }}</div>
    <p>{{ product.desc }}</p>
    <div class="product-skin">
      <span v-for="tag in product.skin_tags" :key="tag">{{ tag }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  product: { type: Object, required: true },
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.product-card {
  background: $white;
  border-radius: $radius-sm;
  padding: 20px;
  box-shadow: $shadow;
  transition: $transition;
  border: 1px solid transparent;

  &:hover {
    transform: translateY(-3px);
    box-shadow: $shadow-hover;
    border-color: $mint-pale;
  }

  .product-icon {
    width: 48px;
    height: 48px;
    background: $mint-bg;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-bottom: 12px;
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
</style>
