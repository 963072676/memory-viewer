<template>
  <header class="app-header" :class="{ 'mobile-only-header': isMobile }">
    <div class="header-content">
      <button class="sidebar-toggle" @click="$emit('toggle-sidebar')" :title="isMobile ? '打开导航' : '切换侧边栏'" :aria-label="isMobile ? '打开导航' : '切换侧边栏'">
        <span aria-hidden="true">☰</span>
      </button>

      <div v-if="!isMobile" class="header-title">
        <h1>Memory Viewer</h1>
        <p>Hermes Agent 记忆系统全景视图</p>
      </div>

      <div v-else class="header-title mobile">
        <h1>{{ mobilePageTitle }}</h1>
      </div>

      <div class="header-right">
        <button class="theme-toggle" @click="toggleTheme" :title="modeLabel()" :aria-label="modeLabel()">
          <span aria-hidden="true">{{ modeIcon() }}</span>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useTheme } from '@/composables/useTheme'

const { toggleTheme, modeLabel, modeIcon } = useTheme()
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
    '/': '首页',
    '/agentmemory': 'AgentMemory',
    '/hermes': 'Hermes Memory',
    '/profiles': 'Profiles',
    '/dashboard': '仪表盘',
    '/collections': '分类',
    '/compare': '对比',
    '/sources': '数据源',
    '/settings': '设置',
  }
  if (map[p]) return map[p]
  if (p.startsWith('/memory/')) return '记忆详情'
  if (p.startsWith('/memory')) return '记忆'
  return 'Memory Viewer'
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
     保证 header 居中轴线与下方内容居中轴线在 800-1280px 区间内完全对齐，无视觉漂移。 */
  max-width: var(--content-max);
  margin: 0 auto;
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
</style>
