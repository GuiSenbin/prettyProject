<!-- 应用根组件：控制开屏、登录态、业务页框架和全局抽屉。 -->
<template>
  <div id="app-container" :class="{ 'auth-mode': !userStore.isAuthenticated }">
    <SplashScreen v-if="showSplash" />
    <LoginView v-else-if="!userStore.isAuthenticated" @logged-in="handleLoggedIn" />
    <main v-else class="main-container">
      <header class="app-page-header">
        <button class="btn-icon" type="button" aria-label="返回" @click="handleBack">
          <ChevronLeft :size="24" stroke-width="2.6" />
        </button>
        <h1>{{ routeTitle }}</h1>
        <button class="btn-icon" type="button" aria-label="打开菜单" @click="openDrawer">
          <TextAlignStart :size="24" stroke-width="2.6" />
        </button>
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
import { ChevronLeft, TextAlignStart } from 'lucide-vue-next'
import AppDrawer from '@/components/AppDrawer.vue'
import LoginView from '@/views/Login/index.vue'
import SplashScreen from '@/views/Splash/index.vue'
import ToastMessage from '@/components/ToastMessage.vue'
import { useUserStore } from '@/stores/user'

const drawerOpen = ref(false)
const showSplash = ref(true)
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const routeTitle = computed(() => route.meta.title || route.meta.label || '智颜')

function openDrawer() {
  drawerOpen.value = true
}

function handleLoggedIn() {
  router.replace('/chat')
}

function handleBack() {
  if (window.history.length > 1) {
    router.back()
    return
  }
  router.replace('/chat')
}

function handleLogout() {
  userStore.logout()
  drawerOpen.value = false
  router.replace('/chat')
}

onMounted(() => {
  // 初始化时强制清空登录态，确保每次重新进入或刷新都能在开屏页后展示登录页
  userStore.logout()

  window.addEventListener('open-app-drawer', openDrawer)
  const splashDuration = userStore.isAuthenticated ? 800 : 1600
  window.setTimeout(() => {
    showSplash.value = false
    if (userStore.isAuthenticated && router.currentRoute.value.path === '/') {
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
  padding: calc(78px + env(safe-area-inset-top)) 18px 34px;
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
  top: calc(16px + env(safe-area-inset-top));
  left: 16px;
  right: 16px;
  z-index: 900;
  display: grid;
  grid-template-columns: 44px 1fr 44px;
  align-items: center;
  gap: 10px;
  h1 {
    color: $text-primary;
    font-size: 18px;
    font-weight: 900;
    line-height: 1.2;
    text-align: center;
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
    padding: calc(78px + env(safe-area-inset-top)) 14px 28px;
    min-height: 100dvh;
  }
}
</style>
