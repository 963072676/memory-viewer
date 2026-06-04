import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import router from './router'
import zhCN from './locales/zh-CN.json'
import enUS from './locales/en-US.json'
import './styles/variables.css'
import './styles/main.css'

const STORAGE_KEY = 'mv-locale'
const savedLocale = (() => {
  try { return localStorage.getItem(STORAGE_KEY) || 'zh-CN' } catch { return 'zh-CN' }
})()

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: savedLocale,
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS,
  },
})

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

app.mount('#app')
