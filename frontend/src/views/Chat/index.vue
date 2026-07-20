<!-- AI 问答：专业闺蜜型美妆护肤顾问，多会话入口。 -->
<template>
  <section class="chat-page">
    <div v-if="chatStore.showGuide" class="chat-welcome">
      <span class="eyebrow">小蜜 AI 顾问</span>
      <h2>今天想聊聊皮肤，还是妆容？</h2>
      <p>我会结合你的个人档案和产品库，给你专属建议。</p>
      <div class="suggestion-scroll">
        <button
          v-for="item in suggestions"
          :key="item"
          class="btn btn-secondary suggestion-btn"
          type="button"
          @click="sendSuggested(item)"
        >
          {{ item }}
        </button>
      </div>
    </div>

    <div v-if="messages.length" class="message-list">
      <article
        v-for="item in messages"
        :key="item.id"
        class="message"
        :class="[item.role, { thinking: item.loading, failed: item.error }]"
      >
        <time class="message-time">{{ formatMessageTime(item.created_at) }}</time>
        <p v-if="item.role === 'user'" class="bubble">{{ item.content_text }}</p>
        <div v-else-if="item.loading" class="thinking-card">
          <div class="thinking-copy">
            <span>小蜜正在结合你的档案和产品库思考</span>
            <small>正在整理更适合你的建议</small>
          </div>
          <span class="thinking-dots" aria-hidden="true">
            <i></i>
            <i></i>
            <i></i>
          </span>
        </div>
        <div v-else-if="item.error" class="thinking-card error-card">
          <div class="thinking-copy">
            <span>{{ item.content_text }}</span>
            <small>网络或模型暂时没有回应</small>
          </div>
        </div>
        <div v-else class="answer-card">
          <template v-if="item.structured_payload">
            <header>
              <div class="answer-meta">
                <span>{{ sourceLabel(item.structured_payload.source) }}</span>
                <span>{{ levelLabel(item.structured_payload.answer_level) }}</span>
                <span>{{ contextLabel(item.structured_payload.context_policy) }}</span>
              </div>
              <h3>{{ item.structured_payload.title }}</h3>
              <p>{{ item.structured_payload.summary }}</p>
            </header>
            <section
              v-for="section in item.structured_payload.sections"
              :key="section.heading"
              :class="['answer-section', section.type]"
            >
              <h4>{{ section.heading }}</h4>
              <p v-if="section.body">{{ section.body }}</p>
              <ol v-if="section.type === 'questions'">
                <li v-for="question in section.items" :key="question.strong">
                  <strong>{{ question.strong }}</strong>
                  <span>{{ question.text }}</span>
                </li>
              </ol>
              <ul v-else-if="section.items?.length">
                <li v-for="text in section.items" :key="text">{{ text }}</li>
              </ul>
            </section>
            <section v-if="item.structured_payload.safety_note" class="answer-section warning">
              <h4>安全提醒</h4>
              <p>{{ item.structured_payload.safety_note }}</p>
            </section>
            <section v-if="item.structured_payload.follow_up_questions?.length" class="answer-section follow-up">
              <h4>我还想确认</h4>
              <ul>
                <li v-for="question in item.structured_payload.follow_up_questions" :key="question">{{ question }}</li>
              </ul>
            </section>
          </template>
          <p v-else>{{ item.content_text }}</p>
        </div>
      </article>
    </div>

    <form class="chat-input" @submit.prevent="handleSend">
      <input
        v-model.trim="draft"
        type="text"
        placeholder="对话内容以开启隐私保护"
        :disabled="chatStore.sending"
      />
      <button class="btn btn-primary" type="submit" :disabled="chatStore.sending || !draft">
        {{ chatStore.sending ? '发送中' : '发送' }}
      </button>
    </form>
  </section>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useAppStore } from '@/stores/app'
import { useChatStore } from '@/stores/chat'
import { useUserStore } from '@/stores/user'

const appStore = useAppStore()
const chatStore = useChatStore()
const userStore = useUserStore()
const draft = ref('')
const { messages } = storeToRefs(chatStore)
const suggestions = [
  '我最近总长痘痘为什么?',
  '早上护肤涂什么?',
  '我想化一个淡妆',
]

onMounted(() => {
  chatStore.fetchSessions(userStore.userId)
  window.addEventListener('chat-new-topic', handleNewTopic)
})

onBeforeUnmount(() => {
  window.removeEventListener('chat-new-topic', handleNewTopic)
})

watch(
  () => messages.value.length,
  async () => {
    await nextTick()
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
  }
)

function handleNewTopic() {
  chatStore.startNewTopic()
  draft.value = ''
}

function levelLabel(level) {
  const labels = {
    daily: '日常建议',
    cautious: '谨慎建议',
    high_risk: '高风险',
    refuse: '范围外',
  }
  return labels[level] || '建议'
}

function contextLabel(policy) {
  if (!policy) return '未使用档案'
  if (policy.use_profile && policy.use_products) return '参考档案和产品库'
  if (policy.use_profile) return '参考个人档案'
  if (policy.use_products) return '参考产品库'
  return '通用建议'
}

function sourceLabel(source) {
  const labels = {
    model: 'AI 生成',
    local_rule: '安全兜底',
    fallback: '安全兜底',
  }
  return labels[source] || 'AI 建议'
}

function formatMessageTime(value) {
  const date = value ? new Date(value) : new Date()
  const now = new Date()
  const sameDay = date.toDateString() === now.toDateString()
  const time = date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
  if (sameDay) return time
  const dayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const targetStart = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const diffDays = Math.floor((dayStart - targetStart) / 86400000)
  if (diffDays >= 0 && diffDays < 7) {
    const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
    return `${weekdays[date.getDay()]} ${time}`
  }
  return `${date.getMonth() + 1}月${date.getDate()}日 ${time}`
}

function sendSuggested(text) {
  draft.value = text
  handleSend()
}

async function handleSend() {
  if (!draft.value || chatStore.sending) return
  const message = draft.value
  draft.value = ''
  try {
    await chatStore.sendMessage(userStore.userId, message)
  } catch (err) {
    appStore.showToast(err.message || '小蜜暂时没有回应，请稍后再试', 'error')
  }
}
</script>

<style lang="scss" scoped>
.chat-page {
  min-height: calc(100dvh - 86px);
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding-bottom: 72px;
}
.chat-welcome {
  margin-top: 5px;
  padding: 18px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(207, 238, 241, 0.72);
  box-shadow: 0 14px 34px rgba(20, 82, 91, 0.06);
  .eyebrow {
    color: $mint-primary;
    font-size: 12px;
    font-weight: 900;
  }
  h2 {
    margin-top: 8px;
    color: $text-primary;
    font-size: 21px;
    line-height: 1.25;
  }
  p {
    margin-top: 8px;
    color: $text-light;
    font-size: 13px;
  }
}
.suggestion-scroll {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  .suggestion-btn {
    flex: 0 0 auto;
    min-height: 32px;
    padding: 0 12px;
    font-size: 12px;
    letter-spacing: 0;
    box-shadow: none;
  }
}
.message-list {
  display: grid;
  gap: 14px;
}
.message {
  display: flex;
  flex-direction: column;
  gap: 6px;
  &.user {
    align-items: flex-end;
  }
  &.assistant {
    align-items: flex-start;
  }
}
.message-time {
  align-self: center;
  color: rgba(67, 82, 102, 0.56);
  font-size: 11px;
  font-weight: 700;
}
.bubble {
  max-width: 82%;
  padding: 10px 12px;
  border-radius: 8px;
  background: $mint-primary;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
}
.answer-card {
  width: 100%;
  display: grid;
  gap: 10px;
  padding: 14px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(207, 238, 241, 0.78);
  box-shadow: 0 12px 28px rgba(20, 82, 91, 0.06);
  header {
    .answer-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      span {
        padding: 3px 7px;
        border-radius: 8px;
        background: rgba(13, 124, 135, 0.08);
        border: 1px solid rgba(13, 124, 135, 0.12);
        color: $mint-primary;
        font-size: 10px;
        font-weight: 900;
      }
    }
    > span {
      color: $mint-primary;
      font-size: 11px;
      font-weight: 900;
    }
    h3 {
      margin-top: 4px;
      color: $text-primary;
      font-size: 17px;
      line-height: 1.3;
    }
    p {
      margin-top: 6px;
      color: $text-light;
      font-size: 13px;
    }
  }
}
.thinking-card {
  width: min(86%, 360px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 13px 14px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(207, 238, 241, 0.78);
  box-shadow: 0 12px 28px rgba(20, 82, 91, 0.06);
}
.thinking-copy {
  display: grid;
  gap: 4px;
  span {
    color: $text-primary;
    font-size: 13px;
    font-weight: 900;
  }
  small {
    color: rgba(67, 82, 102, 0.62);
    font-size: 11px;
    font-weight: 700;
  }
}
.thinking-dots {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  flex: 0 0 auto;
  i {
    width: 6px;
    height: 6px;
    border-radius: 999px;
    background: $mint-primary;
    animation: thinkingPulse 1.1s ease-in-out infinite;
    &:nth-child(2) {
      animation-delay: 0.16s;
    }
    &:nth-child(3) {
      animation-delay: 0.32s;
    }
  }
}
.error-card {
  border-color: rgba(245, 158, 11, 0.22);
  background: rgba(255, 251, 235, 0.88);
  .thinking-copy span {
    color: #9a5d00;
  }
}
.answer-section {
  padding: 10px;
  border-radius: 8px;
  background: rgba(244, 250, 250, 0.82);
  h4 {
    color: $mint-primary;
    font-size: 13px;
    margin-bottom: 6px;
  }
  p,
  li {
    color: $text-light;
    font-size: 13px;
    line-height: 1.55;
  }
  ul,
  ol {
    display: grid;
    gap: 6px;
    padding-left: 18px;
  }
  strong {
    display: block;
    color: $text-primary;
    font-weight: 900;
  }
  &.warning {
    background: rgba(245, 158, 11, 0.1);
    h4 {
      color: #9a5d00;
    }
  }
}
.chat-input {
  position: fixed;
  left: 14px;
  right: 14px;
  bottom: calc(14px + env(safe-area-inset-bottom));
  z-index: 880;
  display: flex;
  gap: 8px;
  padding: 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(207, 238, 241, 0.72);
  box-shadow: 0 12px 30px rgba(20, 82, 91, 0.12);
  input {
    flex: 1;
    min-width: 0;
    border: 0;
    outline: 0;
    background: transparent;
    padding: 0 8px;
    color: $text-primary;
    font-size: 14px;
  }
  button {
    min-width: 58px;
    --btn-height: 32px;
    height: var(--btn-height);
    min-height: var(--btn-height) !important;
    padding: 0 12px;
    font-size: 13px;
  }
}
@keyframes thinkingPulse {
  0%,
  80%,
  100% {
    opacity: 0.28;
    transform: translateY(0);
  }
  40% {
    opacity: 1;
    transform: translateY(-3px);
  }
}
</style>
