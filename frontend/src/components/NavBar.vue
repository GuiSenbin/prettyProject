<template>
  <nav class="navbar">
    <div class="nav-container">
      <router-link to="/" class="nav-brand">
        <span class="brand-icon">✦</span>
        <span class="brand-text">智颜</span>
      </router-link>
      <button class="nav-toggle" @click="menuOpen = !menuOpen" :aria-label="menuOpen ? '关闭菜单' : '打开菜单'">
        ☰
      </button>
      <ul class="nav-menu" :class="{ show: menuOpen }">
        <li v-for="item in menuItems" :key="item.path">
          <router-link :to="item.path" class="nav-link" :class="{ active: $route.path === item.path }"
                       @click="menuOpen = false">
            {{ item.label }}
          </router-link>
        </li>
      </ul>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'

const menuOpen = ref(false)

const menuItems = [
  { path: '/', label: '首页' },
  { path: '/profile', label: '个人档案' },
  { path: '/chat', label: 'AI 助手' },
  { path: '/influencers', label: '美妆达人' },
  { path: '/products', label: '产品百科' },
]
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid $mint-pale;

  .nav-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
  }

  .nav-brand {
    display: flex;
    align-items: center;
    gap: 8px;

    .brand-icon {
      font-size: 28px;
      color: $mint-primary;
    }

    .brand-text {
      font-size: 22px;
      font-weight: 900;
      background: $gradient-primary;
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }

  .nav-toggle {
    display: none;
    font-size: 24px;
    cursor: pointer;
    color: $mint-dark;
    background: none;
    border: none;
  }

  .nav-menu {
    display: flex;
    gap: 4px;

    .nav-link {
      padding: 8px 18px;
      border-radius: 8px;
      color: $text-secondary;
      font-size: 15px;
      font-weight: 500;
      transition: $transition;
      position: relative;

      &:hover,
      &.active {
        color: $mint-primary;
        background: $mint-bg;
      }

      &.active::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 50%;
        transform: translateX(-50%);
        width: 20px;
        height: 3px;
        background: $mint-primary;
        border-radius: 2px;
      }
    }
  }
}

@media (max-width: 768px) {
  .navbar {
    .nav-toggle {
      display: block;
    }
    .nav-menu {
      display: none;
      position: absolute;
      top: 64px;
      left: 0;
      right: 0;
      background: $white;
      flex-direction: column;
      padding: 16px;
      border-bottom: 1px solid $mint-pale;
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);

      &.show {
        display: flex;
      }

      .nav-link {
        padding: 12px 18px;
      }
    }
  }
}
</style>
