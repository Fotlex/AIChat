import { createRouter, createWebHistory } from 'vue-router'
import CharactersView from '@/views/CharactersView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'characters',
      component: CharactersView,
    },
  ],
})

export default router