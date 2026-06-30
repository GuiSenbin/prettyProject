<template>
  <Teleport to="body">
    <div v-if="store.toast.show" class="toast-msg" :class="'toast-' + store.toast.type">
      {{ store.toast.msg }}
    </div>
  </Teleport>
</template>

<script setup>
import { useAppStore } from '@/stores/app'
const store = useAppStore()
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.toast-msg {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 28px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  z-index: 9999;
  animation: fadeIn 0.3s ease;
  color: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);

  &.toast-success { background: $mint-dark; }
  &.toast-warning { background: #e8a838; }
  &.toast-info { background: $text-secondary; }
  &.toast-error { background: #d9534f; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateX(-50%) translateY(-8px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}
</style>
