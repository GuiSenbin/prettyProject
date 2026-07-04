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
              <p>我是 <strong>智颜 AI 美妆决策助手</strong>，会结合你的肤质档案、已有产品和使用目标给出建议。</p>
              <p>你可以让我判断：</p>
              <ul>
                <li>某个产品是否适合当前肤质</li>
                <li>一套护肤流程是否存在冲突</li>
                <li>不同场景下适合的妆容方向</li>
                <li>已有产品应该如何搭配使用</li>
              </ul>
              <p>试试问我：<em>"我今天要见客户，想要干净但有气色的妆容"</em></p>
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
import { getCabinetProductNames } from '@/utils/cabinet'

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
  
  const userProducts = getCabinetProductNames(userStore.userId)

  await chatStore.send(text, userStore.userId, userProducts)
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
  .chat-page {
    margin: -8px -14px calc(-86px - env(safe-area-inset-bottom));
  }

  .chat-container {
    flex-direction: column;
    height: calc(100dvh - 56px);
    min-height: 0;
    border-radius: 0;
    box-shadow: none;

    .chat-sidebar {
      display: none;
    }

    .chat-main {
      min-height: 0;
      background: $white;
    }

    .chat-messages {
      padding: 16px 14px calc(94px + env(safe-area-inset-bottom));
      gap: 12px;
      -webkit-overflow-scrolling: touch;

      .welcome-content ul {
        padding-left: 18px;
      }
    }

    .suggestion-chips {
      flex-wrap: nowrap;
      overflow-x: auto;
      margin-right: -14px;
      padding-bottom: 4px;

      .chip {
        flex: 0 0 auto;
      }
    }

    .chat-input-area {
      position: sticky;
      bottom: 0;
      z-index: 5;
      padding: 10px 12px calc(10px + env(safe-area-inset-bottom));
      box-shadow: 0 -8px 18px rgba(26, 122, 92, 0.08);

      .input-wrapper {
        gap: 8px;

        textarea {
          min-height: 44px;
          padding: 11px 14px;
          border-radius: 18px;
          font-size: 16px;
          max-height: 108px;
        }

        .btn-send {
          min-width: 64px;
          min-height: 44px;
          padding: 0 15px;
          border-radius: 18px;
        }
      }
    }
  }
}

@media (max-width: 380px) {
  .chat-page {
    margin-left: -10px;
    margin-right: -10px;
  }
}
</style>
