<template>
  <div id="app-container">
    <NavBar />
    <main class="main-container">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <ToastMessage />
    <footer class="footer">
      <p>智颜 v1.0 — 用算力解析肌理状态，以光影重塑面部轮廓</p>
      <p class="footer-sub">本平台建议仅供参考，严重皮肤问题请咨询专业医生</p>
    </footer>
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import ToastMessage from '@/components/ToastMessage.vue'
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 24px 40px;
  min-height: calc(100vh - 100px);
  width: 100%;
}

#app-container {
  min-height: 100vh;
  min-height: 100dvh;
  background:
    linear-gradient(90deg, rgba(10, 166, 194, 0.035) 1px, transparent 1px),
    linear-gradient(180deg, rgba(10, 166, 194, 0.035) 1px, transparent 1px);
  background-size: 42px 42px;
}

.footer {
  text-align: center;
  padding: 24px;
  color: $text-light;
  font-size: 14px;
  border-top: 1px solid $mint-pale;

  .footer-sub {
    font-size: 12px;
    margin-top: 4px;
    opacity: 0.7;
  }
}

@media (max-width: 768px) {
  body {
    background: #f8fcfd;
  }

  .main-container {
    max-width: none;
    padding: 72px 14px calc(86px + env(safe-area-inset-bottom));
    min-height: 100dvh;
  }

  .footer {
    display: none;
  }
}

@media (max-width: 380px) {
  .main-container {
    padding-left: 10px;
    padding-right: 10px;
  }
}
</style>
