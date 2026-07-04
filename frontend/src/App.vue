<template>
  <div id="app-container" :class="{ 'auth-mode': !userStore.isAuthenticated }">
    <SplashScreen v-if="showSplash" />
    <LoginGate v-else-if="!userStore.isAuthenticated" @logged-in="handleLoggedIn" />
    <main v-else class="main-container">
      <button
        v-if="$route.name !== 'Chat'"
        class="page-menu-trigger"
        type="button"
        aria-label="打开菜单"
        @click="openDrawer"
      >
        <span></span><span></span><span></span>
      </button>
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
      @new-chat="handleNewChat"
    />
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppDrawer from '@/components/AppDrawer.vue'
import LoginGate from '@/components/LoginGate.vue'
import SplashScreen from '@/components/SplashScreen.vue'
import ToastMessage from '@/components/ToastMessage.vue'
import { useChatStore } from '@/stores/chat'
import { useUserStore } from '@/stores/user'

const drawerOpen = ref(false)
const showSplash = ref(true)
const router = useRouter()
const userStore = useUserStore()
const chatStore = useChatStore()

function openDrawer() {
  drawerOpen.value = true
}

function handleLoggedIn() {
  router.replace('/chat')
}

function handleLogout() {
  userStore.logout()
  drawerOpen.value = false
  router.replace('/chat')
}

async function handleNewChat() {
  await chatStore.newSession()
  drawerOpen.value = false
  router.push('/chat')
}

onMounted(() => {
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
@use '@/assets/styles/variables' as *;

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
  padding: 0;
  min-height: 100vh;
  min-height: 100dvh;
  width: 100%;
}

.page-menu-trigger {
  position: fixed;
  top: calc(16px + env(safe-area-inset-top));
  left: 16px;
  z-index: 900;
  width: 46px;
  height: 46px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.84);
  color: $text-primary;
  box-shadow: 0 12px 28px rgba(10, 166, 194, 0.12);

  span {
    width: 20px;
    height: 3px;
    border-radius: 999px;
    background: currentColor;
  }
}

.products-page,
.influencers-page,
.cabinet-page,
.profile-page {
  min-height: 100dvh;
  padding: calc(78px + env(safe-area-inset-top)) 18px 34px;
  background:
    radial-gradient(circle at 20% 0%, rgba(207, 238, 241, 0.9), transparent 32%),
    radial-gradient(circle at 86% 14%, rgba(240, 251, 252, 0.95), transparent 34%),
    linear-gradient(180deg, #f8feff, #ffffff);
}

#app-container {
  min-height: 100vh;
  min-height: 100dvh;
  background: #f6fbfc;
}

@media (max-width: 768px) {
  .main-container {
    max-width: none;
    padding: 0;
    min-height: 100dvh;
  }

  .products-page,
  .influencers-page,
  .cabinet-page,
  .profile-page {
    padding-left: 14px;
    padding-right: 14px;
  }
}

@media (max-width: 380px) {
}
</style>
