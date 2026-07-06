// 前端路由：注册核心业务模块入口和登录保护。
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/',
    redirect: '/chat',
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile/index.vue'),
    meta: { label: '个人档案', title: '个人档案', showInMenu: true, requiresAuth: true }
  },
  {
    path: '/cabinet',
    name: 'Cabinet',
    component: () => import('@/views/Product/index.vue'),
    meta: { label: '产品库', title: '产品库', showInMenu: true, requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/Chat/index.vue'),
    meta: { label: 'AI问答', title: 'AI问答', showInMenu: false, requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound/index.vue'),
    meta: { label: '404', title: '404', showInMenu: false, requiresAuth: false, hideHeader: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  if (!userStore.loading) {
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
