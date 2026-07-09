<!-- 确认弹窗 -->
<template>
  <teleport to="body">
    <transition name="modal-fade">
      <div v-if="modelValue" class="modal-mask" @click.self="handleMaskClick">
        <div class="modal-card">
          <header class="modal-header">
            <h3>{{ title }}</h3>
          </header>
          <div class="modal-body">
            <p>{{ content }}</p>
          </div>
          <footer class="modal-footer">
            <button v-if="showCancel" class="btn btn-secondary" type="button" @click="handleCancel">
              {{ cancelText }}
            </button>
            <button class="btn btn-primary" type="button" @click="handleConfirm">
              {{ confirmText }}
            </button>
          </footer>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '提示' },
  content: { type: String, default: '' },
  confirmText: { type: String, default: '确定' },
  cancelText: { type: String, default: '取消' },
  showCancel: { type: Boolean, default: false },
  maskClosable: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

function handleConfirm() {
  emit('confirm')
  emit('update:modelValue', false)
}

function handleCancel() {
  emit('cancel')
  emit('update:modelValue', false)
}

function handleMaskClick() {
  if (props.maskClosable) {
    handleCancel()
  }
}
</script>

<style lang="scss" scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
  .modal-card {
    transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
  .modal-card {
    transform: scale(0.9) translateY(10px);
  }
}
.modal-mask {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(17, 24, 39, 0.32);
  backdrop-filter: blur(4px);
  .modal-card {
    width: 320px;
    max-width: 85vw;
    background: rgba(255, 255, 255, 0.88);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(207, 238, 241, 0.95);
    border-radius: 24px;
    box-shadow: 0 24px 48px rgba(13, 124, 135, 0.16);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    .modal-header {
      padding: 11px 20px 8px;
      text-align: center;
      h3 {
        margin: 0;
        color: #1f292b;
        font-size: 16px;
        font-weight: 500;
      }
    }
    .modal-body {
      padding: 0 20px 0px;
      text-align: center;
      p {
        margin: 0;
        color: rgba(67, 82, 102, 0.82);
        font-size: 14px;
        line-height: 1.6;
        white-space: pre-wrap;
      }
    }
    .modal-footer {
      display: flex;
      gap: 12px;
      padding: 16px 20px;
      .btn {
        flex: 1;
        --btn-height: 36px;
        --btn-padding-x: 8px;
        height: var(--btn-height) !important;
        min-height: var(--btn-height) !important;
        padding: 0 var(--btn-padding-x) !important;
        font-size: 13px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
      }
    }
  }
}
</style>
