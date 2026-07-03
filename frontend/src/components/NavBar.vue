<template>
  <nav class="navbar">
    <div class="nav-container">
      <router-link to="/" class="nav-brand">
        <span class="brand-icon">✦</span>
        <span class="brand-text">智颜</span>
      </router-link>
      
      <div class="nav-right">
        <!-- 动态菜单 -->
        <ul class="nav-menu" :class="{ show: menuOpen }">
          <li v-for="item in menuItems" :key="item.path">
            <router-link :to="item.path" class="nav-link" :class="{ active: $route.path === item.path }"
                         @click="menuOpen = false">
              {{ item.label }}
              <span v-if="item.requiresAuth && !isLoggedIn" class="lock-icon" title="建档后开启">🔒</span>
            </router-link>
          </li>
        </ul>

        <!-- 身份状态栏 -->
        <div class="user-status">
          <template v-if="isLoggedIn">
            <span class="user-name" title="已登录美妆会员">🧴 {{ userStore.profile.name }}</span>
            <button class="btn-logout" @click="handleLogout" title="退出并重置档案">退出</button>
          </template>
          <template v-else>
            <span class="guest-badge">👤 游客</span>
            <router-link to="/profile" class="btn-login-guide">创建档案</router-link>
          </template>
        </div>

        <button class="nav-toggle" @click="menuOpen = !menuOpen" :aria-label="menuOpen ? '关闭菜单' : '打开菜单'">
          ☰
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'

const menuOpen = ref(false)
const userStore = useUserStore()
const appStore = useAppStore()
const router = useRouter()

// 动态从路由表中提取并结构化菜单
const menuItems = computed(() => {
  return router.options.routes
    .filter(r => r.meta && r.meta.showInMenu)
    .map(r => ({
      path: r.path,
      label: r.meta.label,
      requiresAuth: r.meta.requiresAuth || false
    }))
})

// 用户是否已登录/已创建档案
const isLoggedIn = computed(() => !!userStore.profile)

// 退出登录，清除档案
async function handleLogout() {
  if (confirm('确认要清除个人档案并返回游客模式吗？')) {
    const result = await userStore.reset()
    if (result.ok) {
      appStore.showToast('已清除档案，返回游客身份 👤', 'info')
      router.push('/')
    } else {
      appStore.showToast('重置失败: ' + result.error, 'error')
    }
  }
}
</script>

<style lang="scss" scoped>

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

  .nav-right {
    display: flex;
    align-items: center;
    gap: 24px;
    height: 100%;
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

    .lock-icon {
      font-size: 11px;
      margin-left: 4px;
      vertical-align: middle;
      opacity: 0.7;
    }
  }

  .user-status {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 14px;
    padding-left: 16px;
    border-left: 1px solid $mint-pale;
    height: 32px;

    .user-name {
      color: $mint-dark;
      font-weight: 600;
      background: $mint-bg;
      padding: 4px 10px;
      border-radius: 20px;
      white-space: nowrap;
    }

    .btn-logout {
      color: $text-light;
      cursor: pointer;
      font-size: 13px;
      padding: 2px 6px;
      border: 1px solid transparent;
      border-radius: 4px;
      transition: $transition;

      &:hover {
        color: #ff4d4f;
        background: rgba(255, 77, 79, 0.06);
      }
    }

    .guest-badge {
      color: $text-light;
      background: #f0f0f0;
      padding: 4px 10px;
      border-radius: 20px;
      white-space: nowrap;
    }

    .btn-login-guide {
      background: $gradient-primary;
      color: $white;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      box-shadow: 0 2px 8px rgba(26, 122, 92, 0.2);
      transition: $transition;
      white-space: nowrap;

      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(26, 122, 92, 0.3);
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
    .user-status {
      border-left: none;
      padding-left: 0;
    }
  }
}
</style>

