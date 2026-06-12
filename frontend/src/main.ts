import { createApp, watch } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import router from './router'
import './styles/variables.css'
import './styles/main.css'

// AC-11 PM-20260612-001: i18n 按需加载 — 首启只加载 zh-CN (约 20K)，
// 切到 en-US 时再 async import。每个 locale 加载一次后缓存到 messagesCache。
// 暴露 loadMessages 供 LanguageSwitcher / 任何切语言组件复用。
export const STORAGE_KEY = 'mv-locale'
const messagesCache: Record<string, any> = {}

export async function loadMessages(locale: string) {
  if (messagesCache[locale]) return messagesCache[locale]
  // vite 静态分析会把这两个 import 切成独立 chunk，rollupOptions 还能进一步 tree-shake
  const m = await import(`./locales/${locale}.json`)
  messagesCache[locale] = m.default
  return messagesCache[locale]
}

export async function createAppI18n() {
  const savedLocale = (() => {
    try { return localStorage.getItem(STORAGE_KEY) || 'zh-CN' } catch { return 'zh-CN' }
  })()
  const messages = await loadMessages(savedLocale)
  return createI18n({
    legacy: false,
    globalInjection: true,
    locale: savedLocale,
    fallbackLocale: 'zh-CN',
    messages: { [savedLocale]: messages },
  })
}

const app = createApp(App)
app.use(createPinia())
app.use(router)

// 异步初始化 i18n, 然后挂载
createAppI18n().then((i18n) => {
  app.use(i18n)
  // AC-4 PM-20260612-001: <html lang> 跟随 locale 切换
  const syncHtmlLang = (l: string) => {
    document.documentElement.lang = l === 'en-US' ? 'en' : 'zh-CN'
  }
  syncHtmlLang(i18n.global.locale.value as string)
  watch(() => i18n.global.locale.value, syncHtmlLang)
  app.mount('#app')
})
