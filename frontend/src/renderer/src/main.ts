import './assets/styles/index.scss'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import { createPinia } from 'pinia'
import 'element-plus/dist/index.css'
import 'virtual:uno.css'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
const pinia = createPinia()

const app = createApp(App).use(pinia).use(ElementPlus).use(router)

app.use(Antd)

app.mount('#app')
