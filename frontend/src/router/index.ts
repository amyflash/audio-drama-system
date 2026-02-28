import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/AlbumListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/albums/:id',
      name: 'album-detail',
      component: () => import('@/views/AlbumDetailView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/player/:id',
      name: 'player',
      component: () => import('@/views/PlayerView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, _from) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return '/login'
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    return '/'
  }
})

export default router
