<!-- 全局侧边抽屉：展示用户信息、核心模块导航和退出入口。 -->
<template>
  <teleport to="body">
    <transition name="drawer-fade">
      <div v-if="open" class="drawer-mask" @click.self="$emit('close')">
        <aside class="app-drawer">
          <header class="drawer-profile" @click="$emit('close'); $router.push('/settings')" style="cursor: pointer;">
            <div class="avatar">
              <img v-if="userStore.session?.avatar_url" :src="userStore.session.avatar_url" alt="avatar" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;" />
              <span v-else>{{ initials }}</span>
            </div>
            <div>
              <h2>{{ userStore.displayName }}</h2>
              <p>{{ userStore.displayPhone || '已登录' }}</p>
            </div>
            <ChevronRight :size="20" color="#cbd5e1" style="margin-left: auto;" />
          </header>

          <nav class="drawer-nav">
            <router-link v-for="item in navItems" :key="item.path" :to="item.path" @click="$emit('close')">
              <span>
                <component :is="item.icon" :size="18" stroke-width="2.4" />
              </span>
              {{ item.label }}
            </router-link>
          </nav>

          <footer class="drawer-footer">
            <button class="btn btn-ghost" type="button" @click="$emit('logout')">退出登录</button>
          </footer>
        </aside>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { computed } from 'vue'
import { ChevronRight } from 'lucide-vue-next'
import { Boxes, UserRound } from 'lucide-vue-next'
import { useUserStore } from '@/stores/user'

defineProps({
  open: { type: Boolean, default: false },
})

defineEmits(['close', 'logout'])

const userStore = useUserStore()

const navItems = [
  { path: '/profile', label: '个人档案', icon: UserRound },
  { path: '/cabinet', label: '产品库', icon: Boxes },
]

const initials = computed(() => userStore.displayName.slice(0, 1))
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
    font-size: 18px;
    line-height: 1;
  }
  p {
    margin-top: 4px;
    color: $text-light;
    font-size: 14px;
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
.drawer-footer {
  margin-top: 20px;
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
