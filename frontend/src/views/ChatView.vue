<template>
  <div class="chat-page">
    <div class="chat-container">
      <!-- 侧边栏 -->
      <aside class="chat-sidebar">
        <div class="sidebar-header">
          <h3>💬 对话</h3>
          <button class="btn btn-sm" @click="handleNewSession">+ 新对话</button>
        </div>
      </aside>

      <!-- 主聊天区 -->
      <div class="chat-main">
        <div class="chat-messages" ref="msgContainer">
          <!-- 欢迎消息 -->
          <div v-if="chatStore.messages.length === 0 && !chatStore.loading" class="message bot-message">
            <div class="message-avatar">🤖</div>
            <div class="message-content welcome-content">
              <p>你好呀！我是蜜漾 AI 美妆助手 <strong>小蜜</strong> 🌸</p>
              <p>我能帮你：</p>
              <ul>
                <li>💄 根据肤质推荐妆容</li>
                <li>🧴 推荐适合你的护肤品</li>
                <li>✨ 解答美妆护肤疑问</li>
                <li>🎨 教你化妆技巧</li>
              </ul>
              <p>试试问我：<em>"我今天要去约会想画一个淡妆"</em></p>
              <div class="suggestion-chips">
                <span v-for="chip in chips" :key="chip.text" class="chip"
                      @click="quickSend(chip.text)">{{ chip.label }}</span>
              </div>
            </div>
          </div>

          <!-- 消息列表 -->
          <ChatMessage v-for="msg in chatStore.messages" :key="msg.id" :msg="msg" />

          <!-- 加载指示器 -->
          <div v-if="chatStore.loading" class="message bot-message">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
              <div class="typing-dots"><span>·</span><span>·</span><span>·</span></div>
            </div>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="chat-input-area">
          <div class="input-wrapper">
            <textarea v-model="inputText" @keydown.enter.exact.prevent="handleSend"
                      placeholder="输入你的美妆护肤问题..." rows="1"
                      @input="autoResize" ref="inputEl"></textarea>
            <button class="btn-send" @click="handleSend" :disabled="chatStore.loading || !inputText.trim()">
              发送
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import ChatMessage from '@/components/ChatMessage.vue'
import { useChatStore } from '@/stores/chat'
import { useUserStore } from '@/stores/user'

const chatStore = useChatStore()
const userStore = useUserStore()
const msgContainer = ref(null)
const inputEl = ref(null)
const inputText = ref('')

const chips = [
  { text: '我适合什么妆容', label: '我适合什么妆容？' },
  { text: '日常护肤步骤', label: '日常护肤步骤' },
  { text: '推荐适合我的护肤品', label: '推荐护肤品' },
  { text: '约会淡妆教程', label: '约会淡妆教程' },
]

onMounted(async () => {
  await chatStore.loadHistory()
  await userStore.fetchLatest()
})

watch(() => chatStore.messages.length, async () => {
  await nextTick()
  if (msgContainer.value) {
    msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  }
})

function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || chatStore.loading) return
  inputText.value = ''
  if (inputEl.value) {
    inputEl.value.style.height = 'auto'
  }
  await chatStore.send(text, userStore.userId)
}

async function quickSend(text) {
  inputText.value = text
  await handleSend()
}

async function handleNewSession() {
  await chatStore.newSession()
}
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.chat-container {
  display: flex;
  background: $white;
  border-radius: $radius;
  box-shadow: $shadow;
  height: calc(100vh - 180px);
  min-height: 500px;
  overflow: hidden;

  .chat-sidebar {
    flex: 0 0 200px;
    background: $mint-bg;
    border-right: 1px solid $mint-pale;

    .sidebar-header {
      padding: 16px;
      border-bottom: 1px solid $mint-pale;
      display: flex;
      align-items: center;
      justify-content: space-between;

      h3 { font-size: 15px; color: $mint-dark; }
    }
  }

  .chat-main {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;

    .welcome-content ul { margin: 6px 0; padding-left: 20px; }
  }

  .suggestion-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;

    .chip {
      padding: 6px 14px;
      background: $white;
      border: 1px solid $mint-pale;
      border-radius: 20px;
      font-size: 12px;
      color: $mint-primary;
      cursor: pointer;
      transition: $transition;

      &:hover {
        background: $mint-primary;
        color: $white;
        border-color: $mint-primary;
      }
    }
  }

  .typing-dots {
    display: flex;
    gap: 4px;
    padding: 4px 0;

    span {
      animation: tb 1.4s infinite;
      font-size: 28px;
      line-height: 1;
      color: $mint-primary;

      &:nth-child(2) { animation-delay: 0.2s; }
      &:nth-child(3) { animation-delay: 0.4s; }
    }
  }

  .chat-input-area {
    padding: 16px 24px;
    border-top: 1px solid $mint-pale;
    background: $white;

    .input-wrapper {
      display: flex;
      gap: 12px;
      align-items: flex-end;

      textarea {
        flex: 1;
        padding: 12px 16px;
        border: 1.5px solid $mint-pale;
        border-radius: 24px;
        font-size: 14px;
        resize: none;
        outline: none;
        font-family: inherit;
        line-height: 1.5;
        max-height: 120px;
        transition: $transition;

        &:focus {
          border-color: $mint-primary;
          box-shadow: 0 0 0 3px rgba(45, 143, 111, 0.12);
        }
      }

      .btn-send {
        padding: 12px 24px;
        background: $gradient-primary;
        color: $white;
        border: none;
        border-radius: 24px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: $transition;
        white-space: nowrap;

        &:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(26, 122, 92, 0.3);
        }

        &:disabled { opacity: 0.5; cursor: not-allowed; }
      }
    }
  }
}

@keyframes tb {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

@media (max-width: 768px) {
  .chat-container {
    flex-direction: column;
    height: calc(100vh - 160px);

    .chat-sidebar { flex: 0 0 auto; }
  }
}
</style>
