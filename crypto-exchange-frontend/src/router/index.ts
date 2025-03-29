import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/add-coin',
      name: 'add-coin',
      component: () => import('../views/AddCoinView.vue')
    },
    {
      path: '/compare/:id',
      name: 'compare',
      component: () => import('../views/CompareView.vue'),
      props: true
    }
  ]
})

export default router 