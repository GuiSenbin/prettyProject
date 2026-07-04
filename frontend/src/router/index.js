import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/',
    redirect: '/chat',
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { label: '首页', showInMenu: false }
  },
  {
    path: '/influencers',
    name: 'Influencers',
    component: () => import('@/views/InfluencersView.vue'),
    meta: { label: '灵感', showInMenu: true }
  },
  {
    path: '/products',
    name: 'Products',
    component: () => import('@/views/ProductsView.vue'),
    meta: { label: '百科', showInMenu: true }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/ChatView.vue'),
    meta: { label: 'AI', showInMenu: true, requiresAuth: true }
  },
  {
    path: '/cabinet',
    name: 'Cabinet',
    component: () => import('@/views/CabinetView.vue'),
    meta: { label: '产品库', showInMenu: true, requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { label: '我的', showInMenu: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 登录态和档案态分离：AI 可直接使用，档案只增强推荐精度
  if (userStore.userId === null && !userStore.loading) {
    await userStore.fetchLatest()
  }

  const isLoggedIn = userStore.isAuthenticated

  if (to.meta.requiresAuth && !isLoggedIn) {
    next(false)
  } else {
    next()
  }
})

export default router
