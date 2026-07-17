<!-- 全局侧边抽屉：展示用户信息、核心模块导航和退出入口。 -->
<template>
  <teleport to="body">
    <transition name="drawer-fade">
      <div v-if="open" class="drawer-mask" @click.self="$emit('close')">
        <aside class="app-drawer">
          <header class="drawer-profile" @click="$emit('close'); $router.push('/settings')">
            <div class="avatar">
              <img v-if="userStore.session?.avatar_url" :src="userStore.session.avatar_url" alt="avatar" />
              <span v-else>{{ initials }}</span>
            </div>
            <div>
              <h2>{{ userStore.displayName }}</h2>
              <p>{{ userStore.displayPhone || '已登录' }}</p>
            </div>
            <ChevronRight class="profile-arrow" :size="20" color="#cbd5e1" />
          </header>

          <nav class="drawer-nav">
            <router-link v-for="item in navItems" :key="item.path" :to="item.path" @click="$emit('close')">
              <span>
                <component :is="item.icon" :size="18" stroke-width="2.4" />
              </span>
              {{ item.label }}
            </router-link>
          </nav>

          <section class="drawer-history">
            <header>
              <span>历史会话</span>
              <small v-if="chatStore.loadingSessions">读取中</small>
            </header>
            <div v-if="sessions.length" class="history-list">
              <button
                v-for="session in sessions"
                :key="session.id"
                class="btn btn-ghost history-item"
                :class="{ active: chatStore.currentSessionId === session.id }"
                type="button"
                @touchstart.passive="startLongPress(session)"
                @touchend="endLongPress"
                @touchcancel="cancelLongPress"
                @mousedown="startLongPress(session)"
                @mouseup="endLongPress"
                @mouseleave="cancelLongPress"
                @contextmenu.prevent="openActionMenu(session)"
                @click="openHistory(session.id)"
              >
                <span class="history-title">{{ session.title }}</span>
                <time class="history-time">{{ formatSessionTime(session.updated_at || session.created_at) }}</time>
              </button>
            </div>
            <p v-else class="history-empty">暂无历史会话</p>
          </section>

          <footer class="drawer-footer">
            <button class="btn btn-ghost" type="button" @click="$emit('logout')">退出登录</button>
          </footer>
        </aside>
        <div v-if="actionMenuSession" class="history-action-mask" @click.stop="closeActionMenu">
          <div class="history-action-card" @click.stop>
            <button type="button" @click="showRenameModal">
              <PencilLine :size="18" />
              修改标题
            </button>
            <button type="button" class="danger" @click="showDeleteModal">
              <Trash2 :size="18" />
              删除
            </button>
          </div>
        </div>
      </div>
    </transition>
    <InputModal
      v-model="renameVisible"
      v-model:inputValue="renameTitle"
      title="修改标题"
      content="给这段会话取一个更好找的名字"
      placeholder="请输入会话标题"
      :maxlength="40"
      :saving="savingAction"
      :errorMessage="renameError"
      confirmText="保存"
      @confirm="confirmRename"
    />
    <ConfirmModal
      v-model="deleteVisible"
      title="删除会话"
      :content="`确定删除「${actionMenuSession?.title || ''}」吗？删除后不会在历史会话中显示。`"
      confirmText="删除"
      cancelText="取消"
      :showCancel="true"
      :maskClosable="true"
      @confirm="confirmDelete"
    />
  </teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { ChevronRight, PencilLine, Trash2 } from 'lucide-vue-next'
import { Boxes, UserRound } from 'lucide-vue-next'
import ConfirmModal from '@/components/confirm-modal.vue'
import InputModal from '@/components/input-modal.vue'
import { useAppStore } from '@/stores/app'
import { useChatStore } from '@/stores/chat'
import { useUserStore } from '@/stores/user'

const props = defineProps({
  open: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'logout'])

const router = useRouter()
const appStore = useAppStore()
const chatStore = useChatStore()
const userStore = useUserStore()
const { sessions } = storeToRefs(chatStore)
const actionMenuSession = ref(null)
const renameVisible = ref(false)
const deleteVisible = ref(false)
const renameTitle = ref('')
const renameError = ref('')
const savingAction = ref(false)
const longPressTimer = ref(null)
const longPressTriggered = ref(false)

const navItems = [
  { path: '/profile', label: '个人档案', icon: UserRound },
  { path: '/cabinet', label: '产品库', icon: Boxes },
]

const initials = computed(() => userStore.displayName.slice(0, 1))

watch(() => props.open, (open) => {
  if (open) {
    chatStore.fetchSessions(userStore.userId)
  }
})

async function openHistory(sessionId) {
  if (longPressTriggered.value) {
    longPressTriggered.value = false
    return
  }
  try {
    await chatStore.openSession(userStore.userId, sessionId)
    router.replace('/chat')
    emit('close')
  } catch (err) {
    appStore.showToast(err.message || '历史会话读取失败', 'error')
  }
}

function startLongPress(session) {
  cancelLongPress()
  longPressTimer.value = window.setTimeout(() => {
    longPressTriggered.value = true
    openActionMenu(session)
  }, 550)
}

function endLongPress() {
  cancelLongPress()
}

function cancelLongPress() {
  if (longPressTimer.value) {
    window.clearTimeout(longPressTimer.value)
    longPressTimer.value = null
  }
}

function openActionMenu(session) {
  cancelLongPress()
  actionMenuSession.value = session
}

function closeActionMenu() {
  actionMenuSession.value = null
}

function showRenameModal() {
  renameTitle.value = actionMenuSession.value?.title || ''
  renameError.value = ''
  renameVisible.value = true
}

function showDeleteModal() {
  deleteVisible.value = true
}

async function confirmRename() {
  const title = renameTitle.value.trim()
  if (!title) {
    renameError.value = '请输入会话标题'
    return
  }
  if (!actionMenuSession.value) return
  savingAction.value = true
  try {
    await chatStore.renameSession(userStore.userId, actionMenuSession.value.id, title)
    appStore.showToast('会话标题已更新', 'success')
    renameVisible.value = false
    closeActionMenu()
  } catch (err) {
    renameError.value = err.message || '重命名失败'
  } finally {
    savingAction.value = false
  }
}

async function confirmDelete() {
  if (!actionMenuSession.value) return
  savingAction.value = true
  try {
    await chatStore.deleteSession(userStore.userId, actionMenuSession.value.id)
    appStore.showToast('会话已删除', 'success')
    closeActionMenu()
  } catch (err) {
    appStore.showToast(err.message || '删除失败', 'error')
  } finally {
    savingAction.value = false
  }
}

function formatSessionTime(value) {
  if (!value) return ''
  const date = new Date(value)
  const now = new Date()
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false })
  }
  const dayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const targetStart = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const diffDays = Math.floor((dayStart - targetStart) / 86400000)
  if (diffDays >= 0 && diffDays < 7) {
    const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
    return weekdays[date.getDay()]
  }
  return `${date.getMonth() + 1}月${date.getDate()}日`
}
</script>

<style lang="scss" scoped>
.drawer-mask {
  position: fixed;
  inset: 0;
  z-index: 3000;
  background: rgba(20, 22, 40, 0.44);
  display: flex;
  justify-content: flex-start;
}
.app-drawer {
  width: min(64vw, 390px);
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  padding: calc(15px + env(safe-area-inset-top)) 10px 21px;
  background:
    radial-gradient(circle at 20% 0%, rgba(207, 238, 241, 0.96), transparent 34%),
    linear-gradient(180deg, #f8feff, #f1fbfc 44%, #ffffff 100%);
  border-radius: 0 23px 23px 0;
  box-shadow: 20px 0 50px rgba(17, 24, 39, 0.14);
  overflow-y: auto;
}
.drawer-profile {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  .avatar {
    width: 68px;
    height: 68px;
    border-radius: 28px;
    display: grid;
    place-items: center;
    background: linear-gradient(135deg, #fff, $mint-bg);
    color: $mint-primary;
    font-size: 28px;
    font-weight: 900;
    box-shadow: 0 14px 28px rgba(10, 166, 194, 0.12);
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      border-radius: 50%;
    }
  }
  h2 {
    color: $text-primary;
    font-size: 18px;
    line-height: 1;
  }
  p {
    margin-top: 4px;
    color: $text-light;
    font-size: 14px;
  }
  .profile-arrow {
    margin-left: auto;
  }
}
.drawer-nav {
  display: grid;
  gap: 8px;
  margin-top: 28px;
  padding: 16px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.66);
  a {
    display: flex;
    align-items: center;
    gap: 12px;
    min-height: 46px;
    color: $text-primary;
    font-size: 16px;
    font-weight: 800;
  }
  span {
    width: 30px;
    height: 30px;
    display: grid;
    place-items: center;
    border-radius: 12px;
    background: $mint-bg;
    color: $mint-primary;
  }
}
.drawer-history {
  display: grid;
  gap: 8px;
  margin-top: 14px;
  padding: 12px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.52);
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: $text-light;
    font-size: 12px;
    font-weight: 900;
  }
  small {
    font-size: 11px;
    font-weight: 700;
  }
}
.history-list {
  display: grid;
  gap: 4px;
}
.history-item {
  min-height: 34px;
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 8px;
  padding: 0 10px;
  border-radius: 12px;
  color: rgba(67, 82, 102, 0.86);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0;
  text-align: left;
  .history-title {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .history-time {
    color: rgba(67, 82, 102, 0.52);
    font-size: 10px;
    font-weight: 800;
    white-space: nowrap;
  }
  &.active {
    background: rgba(13, 124, 135, 0.1);
    color: $mint-primary;
  }
}
.history-empty {
  color: $text-light;
  font-size: 12px;
}
.drawer-footer {
  margin-top: auto;
  padding-top: 20px;
}
.history-action-mask {
  position: fixed;
  inset: 0;
  z-index: 3001;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(17, 24, 39, 0.18);
}
.history-action-card {
  width: 180px;
  padding: 8px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(207, 238, 241, 0.86);
  box-shadow: 0 24px 48px rgba(17, 24, 39, 0.16);
  backdrop-filter: blur(18px);
  button {
    width: 100%;
    min-height: 44px;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 14px;
    border: 0;
    border-radius: 14px;
    background: transparent;
    color: $text-primary;
    font-size: 15px;
    font-weight: 800;
    text-align: left;
    + button {
      border-top: 1px solid rgba(148, 163, 184, 0.14);
    }
    svg {
      color: currentColor;
    }
    &.danger {
      color: #e54862;
    }
  }
}
.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.22s ease;
  .app-drawer {
    transition: transform 0.24s ease;
  }
}
.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
  .app-drawer {
    transform: translateX(-16px);
  }
}
</style>
