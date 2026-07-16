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
                @click="openHistory(session.id)"
              >
                <span class="history-title">{{ session.title }}</span>
                <span
                  class="history-menu"
                  role="button"
                  tabindex="0"
                  aria-label="会话操作"
                  @click.stop="openHistoryMenu(session)"
                  @keydown.enter.stop.prevent="openHistoryMenu(session)"
                  @keydown.space.stop.prevent="openHistoryMenu(session)"
                >
                  <MoreHorizontal :size="16" />
                </span>
              </button>
            </div>
            <p v-else class="history-empty">暂无历史会话</p>
          </section>

          <footer class="drawer-footer">
            <button class="btn btn-ghost" type="button" @click="$emit('logout')">退出登录</button>
          </footer>
        </aside>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { ChevronRight, MoreHorizontal } from 'lucide-vue-next'
import { Boxes, UserRound } from 'lucide-vue-next'
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
  try {
    await chatStore.openSession(userStore.userId, sessionId)
    router.replace('/chat')
    emit('close')
  } catch (err) {
    appStore.showToast(err.message || '历史会话读取失败', 'error')
  }
}

async function openHistoryMenu(session) {
  const action = window.prompt('输入 1 重命名，输入 2 删除', '1')
  if (action === '1') {
    const title = window.prompt('请输入新的会话标题', session.title)
    if (!title?.trim()) return
    try {
      await chatStore.renameSession(userStore.userId, session.id, title.trim())
      appStore.showToast('会话标题已更新', 'success')
    } catch (err) {
      appStore.showToast(err.message || '重命名失败', 'error')
    }
  }
  if (action === '2') {
    if (!window.confirm(`确定删除「${session.title}」吗？`)) return
    try {
      await chatStore.deleteSession(userStore.userId, session.id)
      appStore.showToast('会话已删除', 'success')
    } catch (err) {
      appStore.showToast(err.message || '删除失败', 'error')
    }
  }
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
  grid-template-columns: 1fr 22px;
  align-items: center;
  gap: 6px;
  padding: 0 6px 0 10px;
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
.history-menu {
  width: 22px;
  height: 22px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  svg {
    color: $text-light;
  }
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
