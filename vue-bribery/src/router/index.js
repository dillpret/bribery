import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import(/* webpackChunkName: "home" */ '@/views/Home.vue')
  },
  {
    path: '/game/:id',
    name: 'Game',
    component: () => import(/* webpackChunkName: "game" */ '@/views/Game.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/:catchAll(.*)',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  // Handle authentication requirements
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!store.state.auth.isAuthenticated) {
      next({
        path: '/',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
