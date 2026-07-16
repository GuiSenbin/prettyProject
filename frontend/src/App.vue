<!-- 应用根组件：控制开屏、登录态、业务页框架和全局抽屉。 -->
<template>
  <div id="app-container" :class="{ 'auth-mode': !userStore.isAuthenticated }">
    <SplashScreen v-if="showSplash" />
    <LoginView v-else-if="!userStore.isAuthenticated" @logged-in="handleLoggedIn" />
    <main v-else class="main-container" :class="{ 'no-header': route.meta.hideHeader }">
      <header v-if="!route.meta.hideHeader" class="app-page-header">
        <button
          v-if="route.meta.backTo"
          class="nav-btn left-btn"
          type="button"
          aria-label="返回"
          @click="goRouteBack"
        >
          <ChevronLeft :size="28" stroke-width="2.6" />
        </button>
        <button v-else class="nav-btn left-btn" type="button" aria-label="打开菜单" @click="openDrawer">
          <TextAlignStart :size="28" stroke-width="2.6" />
        </button>
        <h1>{{ routeTitle }}</h1>
        <button v-if="route.path === '/chat'" class="nav-btn right-btn" type="button" aria-label="新话题" @click="startNewChatTopic">
          <SquarePen :size="25" stroke-width="2.5" />
        </button>
        <button v-else-if="!route.meta.backTo" class="nav-btn right-btn" type="button" aria-label="返回AI问答" @click="goChat">
          <MessageCircle :size="26" stroke-width="2.5" />
        </button>
        <span v-else class="header-spacer" aria-hidden="true"></span>
      </header>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <ToastMessage />
    <AppDrawer
      :open="drawerOpen"
      @close="drawerOpen = false"
      @logout="handleLogout"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChevronLeft, MessageCircle, SquarePen, TextAlignStart } from 'lucide-vue-next'
import AppDrawer from '@/components/AppDrawer.vue'
import LoginView from '@/views/Login/index.vue'
import SplashScreen from '@/views/Splash/index.vue'
import ToastMessage from '@/components/ToastMessage.vue'
import { useChatStore } from '@/stores/chat'
import { useUserStore } from '@/stores/user'

const drawerOpen = ref(false)
const showSplash = ref(true)
const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()
const userStore = useUserStore()
const routeTitle = computed(() => route.meta.title || route.meta.label || '智颜')

function openDrawer() {
  drawerOpen.value = true
}

function handleLoggedIn() {
  chatStore.startNewTopic()
  router.replace('/chat')
}

function goChat() {
  router.replace('/chat')
}

function startNewChatTopic() {
  window.dispatchEvent(new CustomEvent('chat-new-topic'))
}

function goRouteBack() {
  router.replace(route.meta.backTo)
}

function handleLogout() {
  chatStore.startNewTopic()
  chatStore.sessions = []
  userStore.logout()
  drawerOpen.value = false
  router.replace('/chat')
}

onMounted(async () => {
  // 初始化时从本地 localStorage 复原登录态，免除刷新重复登录的故障
  await userStore.fetchLatest()
  window.addEventListener('open-app-drawer', openDrawer)
  const splashDuration = userStore.isAuthenticated ? 800 : 1600
  window.setTimeout(() => {
    showSplash.value = false
    if (userStore.isAuthenticated && (router.currentRoute.value.path === '/' || router.currentRoute.value.path === '/login')) {
      router.replace('/chat')
    }
  }, splashDuration)
})

onBeforeUnmount(() => {
  window.removeEventListener('open-app-drawer', openDrawer)
})
</script>

<style lang="scss">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
html {
  scroll-behavior: smooth;
  min-height: 100%;
}
body {
  font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
  background:
    linear-gradient(180deg, #fbfeff 0%, #f1f8fa 48%, #ffffff 100%),
    $bg-light;
  color: $text-primary;
  line-height: 1.6;
  min-height: 100vh;
  min-height: 100dvh;
  overflow-x: hidden;
  overscroll-behavior-y: none;
}
a {
  text-decoration: none;
  color: inherit;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
.main-container {
  position: relative;
  max-width: none;
  margin: 0 auto;
  padding: calc(52px + env(safe-area-inset-top)) 18px 34px;
  min-height: 100vh;
  min-height: 100dvh;
  width: 100%;
  background:
    radial-gradient(circle at 20% 0%, rgba(207, 238, 241, 0.9), transparent 32%),
    radial-gradient(circle at 86% 14%, rgba(240, 251, 252, 0.95), transparent 34%),
    linear-gradient(180deg, #f8feff, #ffffff);
}
.app-page-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 900;
  display: grid;
  grid-template-columns: 36px 1fr 36px;
  align-items: center;
  min-height: 40px;
  padding: calc(6px + env(safe-area-inset-top)) 20px 6px;
  background: rgba(221, 247, 248, 0.65);
  backdrop-filter: blur(12px);
  h1 {
    color: #111827;
    font-size: 17px;
    font-weight: 500;
    line-height: 1.2;
    text-align: center;
    letter-spacing: 0.08em;
    margin: 0;
  }
  .nav-btn {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    border: 0;
    border-radius: 0;
    background: transparent;
    color: #111827;
    cursor: pointer;
    padding: 0;
    svg {
      display: block;
    }
    &.left-btn {
      justify-content: flex-start;
      margin-left: -8px;
    }
    &.right-btn {
      justify-self: end;
      justify-content: flex-end;
      margin-right: -8px;
    }
  }
  .header-spacer {
    width: 28px;
    height: 28px;
  }
}
#app-container {
  min-height: 100vh;
  min-height: 100dvh;
  background: #f6fbfc;
}
@include respond(phone) {
  .main-container {
    max-width: none;
    padding: calc(52px + env(safe-area-inset-top)) 14px 28px;
    min-height: 100dvh;
  }
}
@include respond(phone-sm) {
  .app-page-header {
    h1 {
      font-size: 21px;
    }
    .nav-btn, .header-spacer {
      width: 36px;
      height: 36px;
    }
  }
}
.main-container.no-header {
  padding: 0;
}
</style>
