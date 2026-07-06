<!-- 全局 Toast：展示轻量状态反馈。 -->
<template>
  <Teleport to="body">
    <div v-if="store.toast.show" class="toast-msg" :class="'toast-' + store.toast.type">
      <span class="toast-icon">{{ toastIcon }}</span>
      <span class="toast-text">{{ store.toast.msg }}</span>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
const store = useAppStore()

const toastIcon = computed(() => {
  const icons = {
    success: '✓',
    warning: '!',
    error: '!',
    info: 'i',
  }
  return icons[store.toast.type] || icons.info
})
</script>

<style lang="scss" scoped>
.toast-msg {
  position: fixed;
  top: max(34px, calc(4.2vh + env(safe-area-inset-top)));
  left: 50%;
  transform: translateX(-50%);
  width: min(60vw, 280px);
  min-height: 38px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 7px 14px;
  border-radius: 8px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.42), rgba(240, 251, 252, 0.24)),
    linear-gradient(135deg, rgba(7, 116, 130, 0.96), rgba(16, 137, 117, 0.94));
  color: $white;
  font-size: 13px;
  font-weight: 800;
  line-height: 1.45;
  z-index: 9999;
  letter-spacing: 0;
  animation: toastIn 0.26s ease;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.56),
    inset 0 -1px 0 rgba(24, 58, 67, 0.12),
    0 12px 26px rgba(8, 132, 148, 0.22);
  backdrop-filter: blur(18px);
  @include respond(phone) {
    width: min(64vw, 270px);
    min-height: 36px;
    padding: 6px 12px;
    font-size: 13px;
  }
  &.toast-warning,
  &.toast-error,
  &.toast-info,
  &.toast-success {
    background:
      linear-gradient(180deg, rgba(255, 255, 255, 0.42), rgba(240, 251, 252, 0.24)),
      linear-gradient(135deg, rgba(8, 132, 148, 0.96), rgba(18, 156, 132, 0.94));
  }
  .toast-icon {
    width: 15px;
    height: 15px;
    display: grid;
    place-items: center;
    flex: 0 0 auto;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.22);
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.36);
    font-size: 10px;
    font-weight: 900;
  }
  .toast-text {
    min-width: 0;
    flex: 1;
  }
}
@keyframes toastIn {
  from { opacity: 0; transform: translateX(-50%) translateY(-10px) scale(0.98); }
  to { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
}
</style>
