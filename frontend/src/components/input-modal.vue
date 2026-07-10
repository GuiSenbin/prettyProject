<!-- 输入弹窗 -->
<template>
  <teleport to="body">
    <transition name="modal-fade">
      <div v-if="modelValue" class="modal-mask" @click.self="handleCancel">
        <div class="modal-card">
          <header class="modal-header">
            <h3>{{ title }}</h3>
            <p v-if="content">{{ content }}</p>
          </header>
          <div class="modal-body">
            <input 
              :value="inputValue"
              @input="$emit('update:inputValue', $event.target.value)"
              type="text" 
              class="settings-input"
              :placeholder="placeholder"
              :maxlength="maxlength"
            />
            <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>
          </div>
          <footer class="modal-footer">
            <button v-if="showCancel" class="btn btn-secondary" type="button" @click="handleCancel">
              {{ cancelText }}
            </button>
            <button class="btn btn-primary" type="button" @click="handleConfirm" :disabled="saving">
              {{ saving ? savingText : confirmText }}
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
  inputValue: { type: String, default: '' },
  title: { type: String, required: true },
  content: { type: String, default: '' },
  placeholder: { type: String, default: '请输入内容' },
  maxlength: { type: Number, default: 20 },
  errorMessage: { type: String, default: '' },
  saving: { type: Boolean, default: false },
  confirmText: { type: String, default: '保存' },
  savingText: { type: String, default: '保存中...' },
  cancelText: { type: String, default: '取消' },
  showCancel: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue', 'update:inputValue', 'confirm', 'cancel'])

function handleCancel() {
  if (props.saving) return
  emit('cancel')
  emit('update:modelValue', false)
}

function handleConfirm() {
  if (props.saving) return
  emit('confirm')
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
      p {
        margin: 6px 0 0;
        color: rgba(67, 82, 102, 0.82);
        font-size: 13px;
        line-height: 1.4;
      }
    }
    .modal-body {
      padding: 10px 20px 0;
      text-align: center;
      .settings-input {
        width: 100%;
        box-sizing: border-box;
        padding: 10px 14px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        background: #f8fafc;
        font-size: 14px;
        color: #1f292b;
        outline: none;
        transition: border-color 0.2s, background 0.2s;
        text-align: left;
        &:focus {
          border-color: #0d7c87;
          background: #ffffff;
        }
      }
      .error-msg {
        margin: 6px 0 0;
        color: #e11d48;
        font-size: 12px;
        text-align: left;
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
