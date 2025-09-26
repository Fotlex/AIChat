import '@/assets/styles/global.css'

import { createApp } from 'vue'
import App from './App.vue'

import router from './router'
import { createPinia } from 'pinia'
import WebApp from '@twa-dev/sdk'

WebApp.ready()

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.mount('#app')