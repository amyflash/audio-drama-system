import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

// 导入视图组件
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import AlbumDetailView from '@/views/albums/AlbumDetailView.vue'
import PlayerView from '@/views/player/PlayerView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresGuest: true }
  },
  {
    path: '/albums/:id',
    name: 'album-detail',
    component: AlbumDetailView,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/player/:id',
    name: 'player',
    component: PlayerView,
    props: true,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 处理认证和 SSO
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const requiresAuth = to.meta.requiresAuth
  const requiresGuest = to.meta.requiresGuest

  // 需要认证的页面，未登录则跳转到登录页
  if (requiresAuth && !token) {
    next('/login')
    return
  }

  // 登录页只允许未登录用户访问
  if (requiresGuest && token) {
    next('/')
    return
  }

  next()
})

export default router
