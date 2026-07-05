<!-- 全局图标按钮：统一圆形图标按钮的尺寸、状态和可访问标签。 -->
<template>
  <button class="btn-icon" :class="variantClass" :type="type" :aria-label="label">
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  type: { type: String, default: 'button' },
  variant: { type: String, default: 'soft' },
})

const variantClass = computed(() => `btn-icon-${props.variant}`)
</script>

<style lang="scss" scoped>
.btn-icon {
  flex: 0 0 auto;
}
.btn-icon-solid {
  background: $mint-primary;
  color: $white;
}
.btn-icon-outline {
  background: rgba(255, 255, 255, 0.68);
  border: 2px solid $text-primary;
}
.btn-icon:disabled {
  cursor: not-allowed;
  opacity: 0.4;
}
</style>
