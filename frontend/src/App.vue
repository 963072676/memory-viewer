<template>
  <div class="app">
    <!-- P38 r31: scroll progress bar — 顶部 1px accent 进度条，反映 main-wrapper 滚动位置。
         之前 router-view 切换有 page fade (r9) + card stagger (r28) 三阶段载入感，但
         页面滚动时无任何反馈。0.5px 高度在 light/dark 都"贴着但不被注意"，100% 时整条
         满满前进感。transform scaleX 而非 width 避免 layout thrash。 -->
    <div class="scroll-progress" :style="{ transform: `scaleX(${scrollProgress})` }" aria-hidden="true"></div>
    <AppSidebar ref="sidebarRef" />
    <div class="main-wrapper" :class="{ 'sidebar-collapsed': uiStore.sidebarCollapsed }">
      <AppHeader @toggle-sidebar="onToggleSidebar" @open-more="onOpenMore" />
      <div class="container">
        <div v-if="showMemoryWorkspaceToolbar" class="memory-workspace-toolbar">
          <SearchBar />
          <QuickAccessBar />
          <SessionSwitcher />
          <StatsBar />
          <TabBar />
        </div>
        <ErrorBanner v-if="agentMemoryStore.error || hermesMemoryStore.error" />
        <!-- P38 r9: 页面切换 transition fade — 路由变化时 150ms 淡入淡出，
             避免瞬切带来的"割裂感"。不重不浮，符合 Geist 克制风格。 -->
        <router-view v-slot="{ Component, route: r }">
          <transition name="page" mode="out-in">
            <component :is="Component" :key="r.fullPath" />
          </transition>
        </router-view>
        <KeyboardHelp v-if="uiStore.showKeyboardHelp" />
      </div>
    </div>
    <WhatsNewModal />
    <OnboardingTour />
    <Toast />
    <CommandPalette v-model="showCommandPalette" @command="handleCommand" />
    <SetupWizard />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import AppHeader from '@/components/Layout/AppHeader.vue'
import AppSidebar from '@/components/Layout/AppSidebar.vue'
import SearchBar from '@/components/Layout/SearchBar.vue'
import QuickAccessBar from '@/components/QuickAccessBar.vue'
import SessionSwitcher from '@/components/Layout/SessionSwitcher.vue'
import StatsBar from '@/components/Layout/StatsBar.vue'
import TabBar from '@/components/Layout/TabBar.vue'
import ErrorBanner from '@/components/Layout/ErrorBanner.vue'
import KeyboardHelp from '@/components/Layout/KeyboardHelp.vue'
import WhatsNewModal from '@/components/Layout/WhatsNewModal.vue'
import OnboardingTour from '@/components/OnboardingTour.vue'
import Toast from '@/components/Layout/Toast.vue'
import CommandPalette from '@/components/Layout/CommandPalette.vue'
import SetupWizard from '@/components/SetupWizard.vue'
import { useAgentMemoryStore } from '@/stores/agentmemory'
import { useHermesMemoryStore } from '@/stores/hermes-memory'
import { useUIStore } from '@/stores/ui'
import { useSessionStore } from '@/stores/sessions'
import { useKeyboard } from '@/composables/useKeyboard'
import { useChangelog } from '@/composables/useChangelog'
import { useToast } from '@/composables/useToast'
import { useWebSocket } from '@/composables/useWebSocket'
import { bulkAutoTag } from '@/api/p8'
import { useRoute, useRouter } from 'vue-router'

const agentMemoryStore = useAgentMemoryStore()
const hermesMemoryStore = useHermesMemoryStore()
const uiStore = useUIStore()
const sessionStore = useSessionStore()
const route = useRoute()
const router = useRouter()
const { loadChangelog } = useChangelog()
const toast = useToast()
const realtime = useWebSocket({ userId: 'memory-viewer-ui' })
let realtimeRefreshTimer: ReturnType<typeof setTimeout> | null = null

const memoryWorkspacePaths = new Set(['/', '/agentmemory', '/hermes', '/graph'])
const showMemoryWorkspaceToolbar = computed(() => memoryWorkspacePaths.has(route.path))

// F47: Command Palette state
const showCommandPalette = ref(false)
const sidebarRef = ref()

// 顶栏菜单按钮：desktop 切换侧栏收起/展开；mobile 打开底部 More 抽屉
function onToggleSidebar() {
  if (typeof window !== 'undefined' && window.innerWidth < 768) {
    sidebarRef.value?.openMoreSheet?.()
  } else {
    uiStore.toggleSidebar()
  }
}

function onOpenMore() {
  sidebarRef.value?.openMoreSheet?.()
}

useKeyboard()

function scheduleRealtimeRefresh() {
  if (realtimeRefreshTimer) {
    clearTimeout(realtimeRefreshTimer)
  }
  realtimeRefreshTimer = setTimeout(() => {
    agentMemoryStore.refresh()
    agentMemoryStore.loadAllTags()
    sessionStore.load().catch(() => {
      sessionStore.mergeDerivedSessions(agentMemoryStore.memories)
    })
  }, 150)
}

realtime.on('memory.created', scheduleRealtimeRefresh)
realtime.on('memory.updated', scheduleRealtimeRefresh)
realtime.on('memory.deleted', scheduleRealtimeRefresh)

// Close mobile sidebar on navigation
watch(() => route.path, () => {
  if (sidebarRef.value?.closeMobileSidebar) {
    sidebarRef.value.closeMobileSidebar()
  }
})

onMounted(async () => {
  await Promise.all([
    agentMemoryStore.fetchMemories(),
    hermesMemoryStore.fetchMemory(),
    loadChangelog(),
  ])
})

// Listen for refresh events from keyboard shortcuts
const onRefresh = () => {
  agentMemoryStore.refresh()
  hermesMemoryStore.refresh()
}
window.addEventListener('app-refresh', onRefresh)

// F47: Listen for command palette toggle from keyboard composable
const onTogglePalette = () => {
  showCommandPalette.value = !showCommandPalette.value
}
window.addEventListener('toggle-command-palette', onTogglePalette)

onUnmounted(() => {
  if (realtimeRefreshTimer) clearTimeout(realtimeRefreshTimer)
  window.removeEventListener('app-refresh', onRefresh)
  window.removeEventListener('toggle-command-palette', onTogglePalette)
  window.removeEventListener('scroll', onScrollProgress, { capture: true } as any)
})

// P38 r31: scroll progress — 0~1, requestAnimationFrame 节流避免 60fps 主线程阻塞。
// 用 capture: true 监 window 滚动，兼容子元素 overflow:auto 滚动容器。
const scrollProgress = ref(0)
let _progressRaf = 0
function onScrollProgress() {
  if (_progressRaf) return
  _progressRaf = requestAnimationFrame(() => {
    _progressRaf = 0
    const doc = document.documentElement
    const max = (doc.scrollHeight - doc.clientHeight) || 1
    scrollProgress.value = Math.min(1, Math.max(0, doc.scrollTop / max))
  })
}
onMounted(() => {
  window.addEventListener('scroll', onScrollProgress, { passive: true, capture: true } as any)
  onScrollProgress()
})

// F47: Handle command palette commands
function handleCommand(name: string) {
  switch (name) {
    case 'create':
      // Dispatch a global event that the create modal can listen to
      window.dispatchEvent(new CustomEvent('app-create-memory'))
      break
    case 'refresh':
      agentMemoryStore.refresh()
      hermesMemoryStore.refresh()
      toast.info('正在刷新记忆...')
      break
    case 'export':
      // Navigate to backup view for export
      window.dispatchEvent(new CustomEvent('app-export'))
      toast.info('正在导出数据...')
      break
    case 'bulk-autotag':
      handleBulkAutoTagFromPalette()
      break
  }
}

// F-34: Bulk Auto-Tag from command palette
async function handleBulkAutoTagFromPalette() {
  toast.info('✨ 正在批量自动标注...')
  try {
    const resp = await bulkAutoTag(undefined)
    if (resp.success) {
      toast.success(`✨ 已为 ${resp.processed} 条记忆自动生成标签`)
      await agentMemoryStore.refresh()
      agentMemoryStore.loadAllTags()
    } else {
      toast.error('批量自动标注失败')
    }
  } catch (e: any) {
    toast.error('批量自动标注失败: ' + (e.message || ''))
  }
}
</script>

<style scoped>
.app {
  display: flex;
  min-height: 100vh;
  /* P38 r9: --bg-primary 不存在（设计系统用 --bg），修复潜在 fallback 问题。
     light 模式 #fafafa，dark 模式 #0a0a0a。 */
  background: var(--bg);
}

/* P38 r31: scroll progress bar — 顶部 0.5px accent bar。
   fixed 而非 sticky，避免 header 滚动时跟随抖动。
   0 → 100% transform: scaleX 一次性 GPU 合成，不触发 layout。
   120ms ease-out 缓动让滚动"松手后最后 1 秒" 进度条仍有惯性。 */
.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 0.5px;
  background: var(--accent);
  transform-origin: 0 50%;
  transform: scaleX(0);
  z-index: 10001; /* 高于 Toast (10000) 与 command palette */
  pointer-events: none;
  transition: transform 120ms ease-out;
  will-change: transform;
}

@media (prefers-reduced-motion: reduce) {
  .scroll-progress { transition: none; }
}

.main-wrapper {
  flex: 1;
  margin-left: 220px;
  min-height: 100vh;
  max-width: calc(100vw - 220px);
  transition: margin-left 0.2s ease;
}

/* P38 r24: 主内容区 max-width → clamp() 流体 — 替代静态 1200px。
   旧 1200px 在 1920+ 显示器（开发者常见工作屏）让内容"死贴左侧 360px 空白"，
   因为 main-wrapper 已经被 sidebar 占去 220px，可用空间 1700px，但内容
   永远卡在 1200px → 右边 500px 死区。
   改用 --content-max token（见 variables.css）：clamp(800px, 92%, 1280px) 3 段语义。
   与 AppHeader .header-content 共用同一 token，保证 header 居中轴线与内容轴线对齐。 */
.main-wrapper .container {
  max-width: var(--content-max);
  margin-left: 32px;
  margin-right: auto;
  padding: 16px 24px;
  padding-bottom: 40px;
}

/* 平板/中等屏幕优化 */
@media (max-width: 1200px) {
  .main-wrapper .container {
    padding: 16px 20px;
  }
}

/* 移动端优化 — sidebar 整体不渲染（display: none），main-wrapper 占满
   关键：顶栏 AppHeader 是 fixed (56px) + 底 Tab Bar fixed (64px)，
   main-wrapper 需要 padding 让内容不被遮挡 */
@media (max-width: 768px) {
  .main-wrapper {
    margin-left: 0 !important;
    max-width: 100vw !important;
    padding-top: 56px;
    padding-bottom: calc(64px + env(safe-area-inset-bottom, 0px));
  }
  .main-wrapper .container {
    max-width: none;
    margin: 0;
    padding: 12px 16px;
  }
}

/* 小屏手机优化 */
@media (max-width: 480px) {
  .main-wrapper .container {
    padding: 10px 12px;
  }
}

/* P38 r9: 页面切换 fade — 150ms out-in，避免瞬切。
   - out-in 先让旧页面 fade-out 完毕再 fade-in 新页面（避免重叠导致视觉混乱）
   - 150ms：足够感知"切换"又不会觉得"卡"（Apple HIG 推荐 200-350ms，
     Geist 偏克制取下界）。ease-out 曲线强调"进入"感。 */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.15s ease-out;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
}

/* 减少动效偏好用户：完全跳过 fade（无障碍） */
@media (prefers-reduced-motion: reduce) {
  .page-enter-active,
  .page-leave-active {
    transition: none;
  }
}
</style>
