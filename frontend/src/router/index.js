import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { label: '首页', showInMenu: true }
  },
  {
    path: '/influencers',
    name: 'Influencers',
    component: () => import('@/views/InfluencersView.vue'),
    meta: { label: '美妆达人', showInMenu: true }
  },
  {
    path: '/products',
    name: 'Products',
    component: () => import('@/views/ProductsView.vue'),
    meta: { label: '产品百科', showInMenu: true }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/ChatView.vue'),
    meta: { label: 'AI 助手', showInMenu: true, requiresAuth: true }
  },
  {
    path: '/cabinet',
    name: 'Cabinet',
    component: () => import('@/views/CabinetView.vue'),
    meta: { label: '我的产品库', showInMenu: true, requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { label: '个人档案', showInMenu: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 优先加载用户资料以核对身份状态
  if (userStore.userId === null && !userStore.loading) {
    await userStore.fetchLatest()
  }

  const isLoggedIn = !!userStore.profile

  if (to.meta.requiresAuth && !isLoggedIn) {
    const { useAppStore } = await import('@/stores/app')
    const appStore = useAppStore()
    appStore.showToast('请先建立个人美妆档案，以开启专属特权功能 ✨', 'warning')
    next({ name: 'Profile' })
  } else {
    next()
  }
})

export default router

