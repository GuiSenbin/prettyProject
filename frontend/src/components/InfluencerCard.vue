<template>
  <div class="influencer-card">
    <div class="influencer-banner" :style="{ background: item.bg || 'var(--mint-bg)' }">
      {{ item.banner || '✨' }}
    </div>
    <div class="influencer-body">
      <div class="influencer-avatar" :style="{ background: item.bg || 'var(--mint-bg)' }">
        {{ item.avatar || '👤' }}
      </div>
      <h3>{{ item.name }}</h3>
      <span class="influencer-tag">{{ item.tag }}</span>
      <p>{{ item.content }}</p>
      <div v-if="item.products?.length" class="product-links">
        <span v-for="p in item.products" :key="p" class="product-link-tag">{{ p }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  item: { type: Object, required: true },
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.influencer-card {
  background: $white;
  border-radius: $radius;
  overflow: hidden;
  box-shadow: $shadow;
  transition: $transition;
  border: 1px solid transparent;

  &:hover {
    transform: translateY(-3px);
    box-shadow: $shadow-hover;
    border-color: $mint-pale;
  }

  .influencer-banner {
    height: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48px;
  }

  .influencer-body {
    padding: 20px;

    .influencer-avatar {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      margin-bottom: 12px;
      border: 3px solid $mint-pale;
    }

    h3 {
      font-size: 16px;
      font-weight: 700;
      color: $mint-dark;
      margin-bottom: 4px;
    }

    .influencer-tag {
      display: inline-block;
      padding: 2px 10px;
      background: $mint-bg;
      border-radius: 10px;
      font-size: 12px;
      color: $mint-primary;
      margin-bottom: 10px;
    }

    p {
      font-size: 14px;
      color: $text-secondary;
      line-height: 1.7;
    }

    .product-links {
      margin-top: 12px;
      display: flex;
      flex-wrap: wrap;
      gap: 6px;

      .product-link-tag {
        padding: 3px 10px;
        border: 1px solid $mint-pale;
        border-radius: 10px;
        font-size: 12px;
        color: $mint-primary;
        background: $bg-light;
      }
    }
  }
}
</style>
