<!-- AI 问答：专业闺蜜型美妆护肤顾问，多会话入口。 -->
<template>
  <section class="chat-page">
    <div v-if="!messages.length" class="chat-welcome">
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

    <div v-else class="message-list">
      <article
        v-for="item in messages"
        :key="item.id"
        class="message"
        :class="item.role"
      >
        <p v-if="item.role === 'user'" class="bubble">{{ item.content_text }}</p>
        <div v-else class="answer-card">
          <template v-if="item.structured_payload">
            <header>
              <span>小蜜建议</span>
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
          </template>
          <p v-else>{{ item.content_text }}</p>
        </div>
      </article>
    </div>

    <form class="chat-input" @submit.prevent="handleSend">
      <input
        v-model.trim="draft"
        type="text"
        placeholder="告诉小蜜你的皮肤状态或今天想画什么妆"
        :disabled="chatStore.sending"
      />
      <button class="btn btn-primary" type="submit" :disabled="chatStore.sending || !draft">
        {{ chatStore.sending ? '发送中' : '发送' }}
      </button>
    </form>
  </section>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
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
  '我最近长痘怎么办？',
  '今天早上怎么护肤？',
  '帮我画一个淡妆',
  '我的产品能一起用吗？',
]

onMounted(() => {
  chatStore.fetchSessions(userStore.userId)
  window.addEventListener('chat-new-topic', handleNewTopic)
})

onBeforeUnmount(() => {
  window.removeEventListener('chat-new-topic', handleNewTopic)
})

function handleNewTopic() {
  chatStore.startNewTopic()
  draft.value = ''
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
    await nextTick()
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
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
  &.user {
    justify-content: flex-end;
  }
  &.assistant {
    justify-content: flex-start;
  }
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
    span {
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
</style>
