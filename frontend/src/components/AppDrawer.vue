<template>
  <teleport to="body">
    <transition name="drawer-fade">
      <div v-if="open" class="drawer-mask" @click.self="$emit('close')">
        <aside class="app-drawer">
          <header class="drawer-profile">
            <div class="avatar">{{ initials }}</div>
            <div>
              <h2>{{ userStore.profile?.name || '智颜用户' }}</h2>
              <p>{{ userStore.displayPhone || '已登录' }}</p>
            </div>
          </header>

          <div class="quick-cards">
            <router-link to="/cabinet" @click="$emit('close')">
              <span>▣</span>
              <strong>产品库</strong>
              <small>管理已有产品</small>
            </router-link>
            <router-link to="/profile" @click="$emit('close')">
              <span>◉</span>
              <strong>美妆档案</strong>
              <small>让推荐更准</small>
            </router-link>
          </div>

          <nav class="drawer-nav">
            <router-link v-for="item in navItems" :key="item.path" :to="item.path" @click="$emit('close')">
              <span>{{ item.icon }}</span>
              {{ item.label }}
            </router-link>
          </nav>

          <section class="recent-panel">
            <div class="panel-title">对话记录</div>
            <button type="button" @click="$emit('new-chat')">今天 · 智颜的护肤建议</button>
            <button type="button" @click="$emit('new-chat')">最近7天 · 底妆服帖方案</button>
            <button type="button" @click="$emit('new-chat')">最近30天 · 产品避雷分析</button>
          </section>

          <footer class="drawer-footer">
            <button type="button" @click="$emit('logout')">退出登录</button>
          </footer>
        </aside>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'

defineProps({
  open: { type: Boolean, default: false },
})

defineEmits(['close', 'logout', 'new-chat'])

const userStore = useUserStore()

const navItems = [
  { path: '/chat', label: 'AI 问答', icon: '✦' },
  { path: '/products', label: '产品百科', icon: '⌕' },
  { path: '/influencers', label: '灵感精选', icon: '★' },
  { path: '/cabinet', label: '我的产品库', icon: '▣' },
  { path: '/profile', label: '个人档案', icon: '◉' },
]

const initials = computed(() => (userStore.profile?.name || '智颜').slice(0, 1))
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.drawer-mask {
  position: fixed;
  inset: 0;
  z-index: 3000;
  background: rgba(20, 22, 40, 0.44);
  display: flex;
  justify-content: flex-start;
}

.app-drawer {
  width: min(86vw, 390px);
  min-height: 100dvh;
  padding: calc(34px + env(safe-area-inset-top)) 22px 22px;
  background:
    radial-gradient(circle at 20% 0%, rgba(207, 238, 241, 0.96), transparent 34%),
    linear-gradient(180deg, #f8feff, #f1fbfc 44%, #ffffff 100%);
  border-radius: 0 30px 30px 0;
  box-shadow: 20px 0 50px rgba(17, 24, 39, 0.14);
  overflow-y: auto;
}

.drawer-profile {
  display: flex;
  align-items: center;
  gap: 14px;

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
  }

  h2 {
    color: $text-primary;
    font-size: 22px;
    line-height: 1.2;
  }

  p {
    margin-top: 4px;
    color: $text-light;
    font-size: 14px;
  }
}

.quick-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin: 28px 0;

  a {
    padding: 18px 16px;
    border: 1px solid rgba(255, 255, 255, 0.74);
    border-radius: 22px;
    background: rgba(255, 255, 255, 0.7);
    box-shadow: 0 14px 30px rgba(10, 166, 194, 0.08);
  }

  span {
    display: block;
    color: $mint-primary;
    font-size: 24px;
  }

  strong {
    display: block;
    margin-top: 10px;
    color: $text-primary;
    font-size: 17px;
  }

  small {
    color: $text-light;
    font-size: 12px;
  }
}

.drawer-nav {
  display: grid;
  gap: 8px;
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

.recent-panel {
  margin-top: 24px;

  .panel-title {
    margin-bottom: 10px;
    color: $text-primary;
    font-size: 18px;
    font-weight: 900;
  }

  button {
    width: 100%;
    min-height: 48px;
    text-align: left;
    color: $text-primary;
    font-size: 15px;
    border-bottom: 1px solid rgba(140, 143, 168, 0.16);
  }
}

.drawer-footer {
  margin-top: 20px;

  button {
    color: $text-light;
    font-size: 14px;
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
