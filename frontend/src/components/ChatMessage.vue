<template>
  <div class="message" :class="msg.role === 'assistant' ? 'bot' : 'user'">
    <div class="message-avatar">{{ msg.role === 'assistant' ? '🤖' : '👤' }}</div>
    <div class="message-content" v-html="renderedContent"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { renderMarkdown } from '@/utils/helpers'

const props = defineProps({
  msg: { type: Object, required: true },
})

const renderedContent = computed(() => renderMarkdown(props.msg.content))
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.message {
  display: flex;
  gap: 12px;
  max-width: 85%;
  animation: msgIn 0.3s ease;

  &.bot { align-self: flex-start; }
  &.user { align-self: flex-end; flex-direction: row-reverse; }

  .message-avatar {
    flex-shrink: 0;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    background: $mint-bg;
  }

  &.user .message-avatar {
    background: $mint-primary;
  }

  .message-content {
    padding: 14px 18px;
    border-radius: 16px;
    font-size: 14px;
    line-height: 1.7;
  }

  &.bot .message-content {
    background: $mint-bg;
    border-bottom-left-radius: 4px;
    color: $text-primary;
  }

  &.user .message-content {
    background: $mint-primary;
    border-bottom-right-radius: 4px;
    color: $white;
  }
}

@keyframes msgIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 640px) {
  .message {
    max-width: 94%;
    gap: 8px;

    .message-avatar {
      width: 30px;
      height: 30px;
      font-size: 15px;
    }

    .message-content {
      padding: 11px 13px;
      border-radius: 14px;
      font-size: 14px;
      line-height: 1.65;
      overflow-wrap: anywhere;
    }
  }
}
</style>
