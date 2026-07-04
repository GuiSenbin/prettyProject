<template>
  <div class="chat-app">
    <header class="ai-header">
      <button class="icon-btn menu-btn" type="button" aria-label="打开菜单" @click="openDrawer">
        <span></span><span></span><span></span>
      </button>
      <div class="title-block">
        <strong>智颜</strong>
        <small>AI 美妆决策助手</small>
      </div>
      <div class="header-actions">
        <button class="gift-btn" type="button" title="任务中心">▥</button>
        <button class="agent-pill" type="button">✦ 智能体</button>
        <button class="more-btn" type="button" title="更多">•••</button>
      </div>
    </header>

    <main class="conversation" ref="msgContainer">
      <section v-if="chatStore.messages.length === 0 && !chatStore.loading" class="welcome-stage">
        <div class="avatar-scene">
          <div class="ai-portrait" aria-hidden="true">
            <span class="hair"></span>
            <span class="face">
              <i class="eye left"></i>
              <i class="eye right"></i>
              <i class="mouth"></i>
            </span>
            <span class="coat"></span>
          </div>
          <div class="greeting">
            <span>{{ greeting }}</span>
            <strong>一起把变美这件事，做得更清醒</strong>
          </div>
        </div>

        <section class="insight-card">
          <div class="card-title">
            <span></span>
            <strong>今日可以问我</strong>
            <button type="button">美妆数据⌄</button>
          </div>
          <button v-for="item in heroQuestions" :key="item" class="question-row" type="button" @click="quickSend(item)">
            <span>#</span>
            {{ item }}
            <i>›</i>
          </button>
        </section>

        <div v-if="!userStore.hasProfile" class="profile-nudge">
          <strong>还没有美妆档案</strong>
          <span>现在也可以直接提问；完善肤质后，产品避雷和妆容推荐会更准。</span>
          <router-link to="/profile">完善档案</router-link>
        </div>
      </section>

      <ChatMessage v-for="msg in chatStore.messages" :key="msg.id" :msg="msg" />

      <div v-if="chatStore.loading" class="message bot-message">
        <div class="message-avatar">AI</div>
        <div class="message-content loading-bubble">
          <span></span><span></span><span></span>
        </div>
      </div>
    </main>

    <footer class="composer-wrap">
      <div class="quick-tools">
        <button v-for="tool in tools" :key="tool.label" type="button" @click="quickSend(tool.prompt)">
          <span>{{ tool.icon }}</span>{{ tool.label }}
        </button>
      </div>
      <div class="composer">
        <button class="voice-btn" type="button" aria-label="语音输入">◖</button>
        <textarea
          v-model="inputText"
          rows="1"
          placeholder="问产品、肤质、妆容或护肤流程..."
          @input="autoResize"
          @keydown.enter.exact.prevent="handleSend"
          ref="inputEl"
        ></textarea>
        <button class="camera-btn" type="button" aria-label="拍肤">⌑</button>
        <button class="send-btn" type="button" :disabled="chatStore.loading || !inputText.trim()" @click="handleSend">
          +
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import ChatMessage from '@/components/ChatMessage.vue'
import { useChatStore } from '@/stores/chat'
import { useUserStore } from '@/stores/user'
import { getCabinetProductNames } from '@/utils/cabinet'

const chatStore = useChatStore()
const userStore = useUserStore()
const msgContainer = ref(null)
const inputEl = ref(null)
const inputText = ref('')

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 12) return '早安'
  if (hour < 18) return '午安'
  return '晚上好'
})

const heroQuestions = [
  '我现在的护肤流程有什么风险？',
  '今天通勤适合什么妆容？',
  '这个产品适合敏感肌吗？',
]

const tools = [
  { label: 'AI 问答', icon: '✦', prompt: '请根据我的肤质给我一个基础护肤建议' },
  { label: '报告解读', icon: '▤', prompt: '我有一份护肤检测报告，应该重点看哪些指标？' },
  { label: '拍肤', icon: '⌑', prompt: '如果我要拍肤分析，需要拍哪些角度？' },
  { label: '产品避雷', icon: '▣', prompt: '帮我判断一个产品是否适合我' },
]

onMounted(async () => {
  await userStore.fetchLatest()
  await chatStore.loadHistory()
})

watch(() => chatStore.messages.length, async () => {
  await nextTick()
  if (msgContainer.value) {
    msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  }
})

function openDrawer() {
  window.dispatchEvent(new CustomEvent('open-app-drawer'))
}

function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 110) + 'px'
}

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || chatStore.loading) return
  inputText.value = ''
  if (inputEl.value) inputEl.value.style.height = 'auto'

  const userProducts = getCabinetProductNames(userStore.userId)
  await chatStore.send(text, userStore.userId, userProducts)
}

async function quickSend(text) {
  inputText.value = text
  await handleSend()
}
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.chat-app {
  position: relative;
  min-height: 100dvh;
  height: 100dvh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background:
    radial-gradient(circle at 18% 8%, rgba(207, 238, 241, 0.94), transparent 36%),
    radial-gradient(circle at 84% 18%, rgba(240, 251, 252, 0.96), transparent 34%),
    linear-gradient(180deg, #f8feff 0%, #f1fbfc 44%, #ffffff 100%);
  color: $text-primary;
}

.ai-header {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: calc(18px + env(safe-area-inset-top)) 18px 12px;
}

.icon-btn,
.gift-btn,
.agent-pill,
.more-btn {
  height: 46px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  color: $text-primary;
  border: 1px solid rgba(207, 238, 241, 0.78);
  box-shadow: 0 12px 28px rgba(10, 166, 194, 0.1);
}

.menu-btn {
  width: 46px;
  display: grid;
  place-items: center;

  span {
    width: 20px;
    height: 3px;
    border-radius: 999px;
    background: currentColor;
  }
}

.title-block {
  min-width: 0;
  flex: 1;

  strong {
    display: block;
    font-size: 30px;
    line-height: 1;
    font-weight: 900;
  }

  small {
    display: block;
    margin-top: 6px;
    color: $text-light;
    font-size: 12px;
    font-weight: 800;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.gift-btn,
.more-btn {
  width: 46px;
  font-size: 22px;
  font-weight: 900;
}

.agent-pill {
  padding: 0 16px;
  font-size: 15px;
  font-weight: 900;
}

.conversation {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 4px 18px 178px;
  -webkit-overflow-scrolling: touch;
}

.welcome-stage {
  min-height: 100%;
}

.avatar-scene {
  display: grid;
  grid-template-columns: 128px 1fr;
  align-items: center;
  gap: 18px;
  min-height: 176px;
}

.ai-portrait {
  position: relative;
  width: 128px;
  height: 150px;
}

.hair,
.face,
.coat {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.hair {
  top: 4px;
  width: 78px;
  height: 58px;
  border-radius: 50% 50% 40% 42%;
  background: #2b2434;
}

.face {
  top: 38px;
  width: 76px;
  height: 82px;
  border-radius: 46% 46% 44% 44%;
  background: #ffd1b7;
}

.eye {
  position: absolute;
  top: 34px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: $text-primary;

  &.left { left: 20px; }
  &.right { right: 20px; }
}

.mouth {
  position: absolute;
  left: 50%;
  bottom: 18px;
  width: 18px;
  height: 8px;
  border-bottom: 2px solid #bf5966;
  border-radius: 0 0 18px 18px;
  transform: translateX(-50%);
}

.coat {
  bottom: 0;
  width: 112px;
  height: 62px;
  border-radius: 36px 36px 16px 16px;
  background: linear-gradient(180deg, #fff, #e6f1ff);
}

.greeting {
  span {
    display: block;
    color: $mint-primary;
    font-size: 28px;
    font-weight: 900;
  }

  strong {
    display: block;
    margin-top: 6px;
    color: $text-primary;
    font-size: 25px;
    line-height: 1.25;
  }
}

.insight-card {
  margin-top: 18px;
  padding: 20px 18px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.56);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.46), 0 20px 40px rgba(10, 166, 194, 0.08);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;

  > span {
    width: 6px;
    height: 28px;
    border-radius: 999px;
    background: $mint-primary;
  }

  strong {
    flex: 1;
    color: $text-primary;
    font-size: 21px;
    font-weight: 900;
  }

  button {
    height: 38px;
    padding: 0 14px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.78);
    color: $text-light;
    font-size: 14px;
    font-weight: 800;
  }
}

.question-row {
  width: 100%;
  min-height: 72px;
  display: grid;
  grid-template-columns: 38px 1fr 18px;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
  padding: 0 16px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.78);
  color: $text-primary;
  text-align: left;
  font-size: 17px;
  font-weight: 800;

  span {
    width: 32px;
    height: 32px;
    display: grid;
    place-items: center;
    border-radius: 12px;
    background: $mint-primary;
    color: #fff;
    box-shadow: 0 10px 20px rgba(10, 166, 194, 0.2);
  }

  i {
    color: #adb0c3;
    font-style: normal;
    font-size: 24px;
  }
}

.profile-nudge {
  display: grid;
  gap: 6px;
  margin-top: 18px;
  padding: 16px 18px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.56);
  color: $text-light;
  font-size: 13px;

  strong {
    color: $text-primary;
    font-size: 16px;
  }

  a {
    width: max-content;
    color: $mint-primary;
    font-weight: 900;
  }
}

.message.bot-message {
  display: flex;
  gap: 10px;
}

.message-avatar {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: $mint-primary;
  color: #fff;
  font-size: 12px;
  font-weight: 900;
}

.message-content {
  max-width: 78%;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.78);
}

.loading-bubble {
  display: flex;
  gap: 4px;

  span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: $mint-primary;
    animation: pulse 1.2s infinite ease-in-out;

    &:nth-child(2) { animation-delay: 0.16s; }
    &:nth-child(3) { animation-delay: 0.32s; }
  }
}

.composer-wrap {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 0 18px calc(18px + env(safe-area-inset-bottom));
  background: linear-gradient(180deg, transparent, rgba(246, 251, 252, 0.92) 24%, rgba(246, 251, 252, 0.98));
}

.quick-tools {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 8px 0 14px;

  button {
    flex: 0 0 auto;
    height: 44px;
    padding: 0 16px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.8);
    color: $text-primary;
    font-size: 15px;
    font-weight: 800;
    box-shadow: 0 10px 24px rgba(10, 166, 194, 0.08);
  }

  span {
    margin-right: 7px;
    color: $mint-primary;
  }
}

.composer {
  min-height: 64px;
  display: flex;
  align-items: flex-end;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(207, 238, 241, 0.9);
  box-shadow: 0 16px 36px rgba(10, 166, 194, 0.12);
}

.voice-btn,
.camera-btn,
.send-btn {
  width: 44px;
  height: 44px;
  flex: 0 0 auto;
  border-radius: 50%;
  color: $text-primary;
  font-size: 24px;
  font-weight: 900;
}

.voice-btn {
  border: 2px solid $text-primary;
}

.composer textarea {
  min-width: 0;
  flex: 1;
  max-height: 110px;
  min-height: 42px;
  padding: 11px 0;
  border: 0;
  resize: none;
  background: transparent;
  color: $text-primary;
  font-size: 16px;
  line-height: 1.4;
  outline: none;
}

.camera-btn,
.send-btn {
  background: $mint-bg;
  color: $text-primary;

  &:disabled {
    opacity: 0.35;
  }
}

@keyframes pulse {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.35; }
  40% { transform: translateY(-4px); opacity: 1; }
}

@media (min-width: 769px) {
  .chat-app {
    max-width: 430px;
    margin: 0 auto;
    box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.04), 0 20px 60px rgba(17, 24, 39, 0.12);
  }
}

@media (max-width: 380px) {
  .ai-header {
    padding-left: 14px;
    padding-right: 14px;
    gap: 10px;
  }

  .agent-pill {
    display: none;
  }

  .conversation {
    padding-left: 14px;
    padding-right: 14px;
  }

  .avatar-scene {
    grid-template-columns: 112px 1fr;
  }

  .greeting strong {
    font-size: 22px;
  }

  .composer-wrap {
    padding-left: 14px;
    padding-right: 14px;
  }
}
</style>
