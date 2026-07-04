<template>
  <nav class="navbar">
    <div class="nav-container">
      <router-link to="/" class="nav-brand">
        <span class="brand-icon">AI</span>
        <span class="brand-text">智颜</span>
      </router-link>
      
      <div class="nav-right">
        <!-- 动态菜单 -->
        <ul class="nav-menu" :class="{ show: menuOpen }">
          <li v-for="item in menuItems" :key="item.path">
            <router-link :to="item.path" class="nav-link" :class="{ active: $route.path === item.path }"
                         @click="menuOpen = false">
              <span class="nav-icon">{{ item.icon }}</span>
              <span class="nav-label">{{ item.label }}</span>
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
  const icons = {
    Home: '⌂',
    Influencers: '★',
    Products: '⌕',
    Chat: '✦',
    Cabinet: '▣',
    Profile: '◉',
  }

  return router.options.routes
    .filter(r => r.meta && r.meta.showInMenu)
    .map(r => ({
      path: r.path,
      label: r.meta.label,
      icon: icons[r.name] || '•',
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
  border-bottom: 1px solid rgba(207, 238, 241, 0.82);
  box-shadow: 0 10px 34px rgba(17, 24, 39, 0.04);

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
      width: 36px;
      height: 36px;
      display: grid;
      place-items: center;
      border: 1px solid rgba(10, 166, 194, 0.22);
      border-radius: 12px;
      background: linear-gradient(180deg, $white, $mint-bg);
      font-size: 13px;
      font-weight: 900;
      color: $mint-primary;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9), 0 8px 18px rgba(10, 166, 194, 0.12);
    }

    .brand-text {
      font-size: 22px;
      font-weight: 900;
      color: $text-primary;
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
      display: inline-flex;
      align-items: center;
      gap: 5px;

      .nav-icon {
        display: none;
      }

      &:hover,
      &.active {
        color: $mint-primary;
        background: rgba(240, 251, 252, 0.9);
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
      background: rgba(240, 251, 252, 0.86);
      border: 1px solid rgba(207, 238, 241, 0.88);
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
      background: #f4f7f8;
      border: 1px solid rgba(207, 238, 241, 0.72);
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
      box-shadow: 0 8px 18px rgba(10, 166, 194, 0.16);
      transition: $transition;
      white-space: nowrap;

      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 22px rgba(10, 166, 194, 0.22);
      }
    }
  }
}

@media (max-width: 768px) {
  .navbar {
    background: rgba(255, 255, 255, 0.96);

    .nav-container {
      height: 56px;
      padding: 0 14px;
    }

    .nav-brand {
      .brand-icon {
        width: 32px;
        height: 32px;
        border-radius: 10px;
        font-size: 12px;
      }

      .brand-text {
        font-size: 20px;
      }
    }

    .nav-right {
      gap: 8px;
    }

    .nav-toggle {
      display: none;
    }

    .nav-menu {
      position: fixed;
      left: 0;
      right: 0;
      top: auto;
      bottom: 0;
      z-index: 1001;
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 0;
      padding: 6px 6px calc(6px + env(safe-area-inset-bottom));
      background: rgba(255, 255, 255, 0.97);
      border-top: 1px solid rgba(207, 238, 241, 0.9);
      box-shadow: 0 -12px 30px rgba(17, 24, 39, 0.08);
      backdrop-filter: blur(16px);

      li:first-child {
        display: none;
      }

      .nav-link {
        min-height: 54px;
        padding: 6px 3px;
        border-radius: 12px;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 2px;
        font-size: 11px;
        line-height: 1.2;

        .nav-icon {
          display: block;
          font-size: 18px;
          line-height: 1;
        }

        .nav-label {
          display: block;
          white-space: nowrap;
          transform: scale(0.92);
        }

        &.active::after {
          display: none;
        }

        &.active {
          background: linear-gradient(180deg, $white, $mint-bg);
          box-shadow: inset 0 0 0 1px rgba(10, 166, 194, 0.16);
        }
      }
    }

    .user-status {
      border-left: none;
      padding-left: 0;
      gap: 8px;
      height: auto;

      .user-name,
      .guest-badge {
        max-width: 112px;
        overflow: hidden;
        text-overflow: ellipsis;
        padding: 4px 9px;
        font-size: 12px;
      }

      .btn-login-guide,
      .btn-logout {
        display: none;
      }
    }
  }
}

@media (max-width: 380px) {
  .navbar .nav-menu {
    padding-left: 4px;
    padding-right: 4px;

    .nav-link {
      font-size: 10px;

      .nav-icon {
        font-size: 17px;
      }
    }
  }
}
</style>
