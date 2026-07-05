// 前端入口：挂载 Vue、Pinia、Router 和全局样式。
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/global.scss'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
