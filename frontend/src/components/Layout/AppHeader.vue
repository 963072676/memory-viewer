<template>
  <header class="app-header" :class="{ 'mobile-only-header': isMobile }">
    <div class="header-content">
      <button
        class="sidebar-toggle"
        @click="$emit('toggle-sidebar')"
        :title="isMobile ? $t('i18n.open_navigation') : $t('i18n.toggle_sidebar')"
        :aria-label="isMobile ? $t('i18n.open_navigation') : $t('i18n.toggle_sidebar')"
      >
        <span aria-hidden="true">☰</span>
      </button>

      <div v-if="!isMobile" class="header-title">
        <h1>{{ $t('en_app_title') }}</h1>
        <!-- P45 r3: 副标题路由变化淡入 (P28 §遗留 #5). 之前副标题 "Hermes Agent {noun}"
             是 static 字符串, 路由切换时无视觉反馈. 现在包 <Transition> + :key 触发
             enter 动画, 每次路由变化副标题 "上新". 桌面 + 移动 page title 共用同一
             模式 (mobile 用 v-else 块) — 移动端 mobilePageTitle 也加上动画. -->
        <Transition name="subtitle-fade" mode="out-in">
          <p :key="route.fullPath">Hermes Agent {{ $t('i18n.memory_system') }}</p>
        </Transition>
      </div>

      <div v-else class="header-title mobile">
        <Transition name="subtitle-fade" mode="out-in">
          <h1 :key="route.fullPath">{{ mobilePageTitle }}</h1>
        </Transition>
      </div>

      <div class="header-right">
        <ConnectionStatus />
        <ProviderStatusBadge />
        <LanguageSwitcher />
        <button class="theme-toggle" @click="toggleTheme" :title="modeLabel()" :aria-label="modeLabel()">
          <span aria-hidden="true">{{ modeIcon() }}</span>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import ProviderStatusBadge from '@/components/Layout/ProviderStatusBadge.vue'
import ConnectionStatus from '@/components/Layout/ConnectionStatus.vue'

const { toggleTheme, modeLabel, modeIcon } = useTheme()
const { t } = useI18n()
const route = useRoute()

defineEmits<{
  'toggle-sidebar': []
  'open-more': []
}>()

// 响应式：mobile 断点 768px
const isMobile = ref(false)
function updateIsMobile() {
  isMobile.value = window.innerWidth < 768
}
onMounted(() => {
  updateIsMobile()
  window.addEventListener('resize', updateIsMobile)
})
onUnmounted(() => {
  window.removeEventListener('resize', updateIsMobile)
})

const mobilePageTitle = computed(() => {
  const p = route.path
  const map: Record<string, string> = {
    '/': 'en_nav_home',
    '/agentmemory': 'en_nav_agentmemory',
    '/hermes': 'en_nav_hermes',
    '/profiles': 'en_nav_profiles',
    '/dashboard': 'en_nav_dashboard',
    '/graph': 'i18n.memory_graph',
    '/collections': 'en_nav_collections',
    '/compare': 'en_nav_compare',
    '/sources': 'en_nav_sources',
    '/plugins': 'en_nav_plugins',
    '/settings': 'en_nav_settings',
  }
  if (map[p]) return t(map[p])
  if (p.startsWith('/memory/')) return t('i18n.page_memory_detail')
  return t('en_app_title')
})
</script>

<style scoped>
/* P37: Header 视觉边界 — sticky + blur + border */
/* P40: max-width 从 1400px → 1200px，与下方 .main-wrapper .container 一致。
   原 1400px 让 header 在 1920+ 屏上比内容"漂"出 100px，header 居中轴线和
   内容居中轴线错位 → 视觉不严谨。统一 1200px 后 header / 搜索 / 卡片栅格
   三者的左右边界完全对齐。 */
.app-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--header-bg);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid var(--header-border);
  padding: 0;
  transition: background 0.2s ease;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 24px;
  /* P38 r24: 与 App.vue .main-wrapper .container 共用 --content-max token —
     保证 header 轴线与下方内容轴线在视觉上完全对齐，无视觉漂移。 */
  max-width: var(--content-max);
  margin-left: 32px;
  margin-right: auto;
}

.header-title {
  flex: 1;
  text-align: center;
  min-width: 0; /* 允许收缩 */
}

.header-title h1 {
  font-size: 1.6rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-title p {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-toggle {
  background: var(--tag-bg);
  border: none;
  border-radius: 10px;
  width: 38px;
  height: 38px;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
  transition: all 0.2s;
  flex-shrink: 0;
}

.sidebar-toggle:hover {
  background: var(--border);
  transform: scale(1.05);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.theme-toggle {
  background: var(--tag-bg);
  border: none;
  border-radius: 50%;
  width: 38px;
  height: 38px;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.theme-toggle:hover {
  transform: scale(1.1);
}

@media (max-width: 767px) {
  /* 移动端：top header fixed 占 56px，让内容 padding-top 避开 */
  .app-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 56px;
    padding: 0;
    box-shadow: 0 1px 3px var(--border);
  }

  .header-content {
    padding: 0 12px;
    height: 56px;
    max-width: 100%;
  }

  .header-title h1 {
    font-size: 1rem;
  }

  .header-title p {
    display: none;
  }

  .sidebar-toggle,
  .theme-toggle {
    width: 36px;
    height: 36px;
    font-size: 1.1rem;
  }
}

/* P45 r3: 副标题路由变化淡入 (P28 §遗留 #5). 180ms 淡入 + 4px 上移,
   比 P38 r31 scroll-progress / r32 toast-overshoot 慢一些 (180 vs 120/450)
   因为 header 是 sticky, 用户视线停留时间更长, 不需要"硬切".
   移动端 mobile page title 共用同一动画, 因为 :key=route.fullPath
   在桌面/移动两个 v-else 块都触发 Transition. */
.subtitle-fade-enter-active,
.subtitle-fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.subtitle-fade-enter-from {
  opacity: 0;
  transform: translateY(4px);
}
.subtitle-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (prefers-reduced-motion: reduce) {
  .subtitle-fade-enter-active,
  .subtitle-fade-leave-active {
    transition: opacity 0.12s ease;
  }
  .subtitle-fade-enter-from,
  .subtitle-fade-leave-to {
    transform: none;
  }
}
</style>
