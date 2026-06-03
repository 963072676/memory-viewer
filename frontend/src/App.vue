<template>
  <div class="app">
    <AppSidebar ref="sidebarRef" />
    <div class="main-wrapper" :class="{ 'sidebar-collapsed': uiStore.sidebarCollapsed }">
      <div class="container">
        <AppHeader @toggle-sidebar="uiStore.toggleSidebar()" />
        <SearchBar />
        <QuickAccessBar />
        <StatsBar />
        <TabBar />
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
import { ref, onMounted, onUnmounted, watch } from 'vue'
import AppHeader from '@/components/Layout/AppHeader.vue'
import AppSidebar from '@/components/Layout/AppSidebar.vue'
import SearchBar from '@/components/Layout/SearchBar.vue'
import QuickAccessBar from '@/components/QuickAccessBar.vue'
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
import { useKeyboard } from '@/composables/useKeyboard'
import { useChangelog } from '@/composables/useChangelog'
import { useToast } from '@/composables/useToast'
import { bulkAutoTag } from '@/api/p8'
import { useRoute, useRouter } from 'vue-router'

const agentMemoryStore = useAgentMemoryStore()
const hermesMemoryStore = useHermesMemoryStore()
const uiStore = useUIStore()
const route = useRoute()
const router = useRouter()
const { loadChangelog } = useChangelog()
const toast = useToast()

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
  window.removeEventListener('app-refresh', onRefresh)
  window.removeEventListener('toggle-command-palette', onTogglePalette)
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

.main-wrapper {
  flex: 1;
  margin-left: 220px;
  min-height: 100vh;
  max-width: calc(100vw - 220px);
  transition: margin-left 0.2s ease;
}

.main-wrapper .container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 24px;
  padding-bottom: 60px;
}

/* 平板/中等屏幕优化 */
@media (max-width: 1200px) {
  .main-wrapper .container {
    padding: 16px 20px;
  }
}

/* 移动端优化 — sidebar 整体不渲染（display: none），main-wrapper 占满 */
@media (max-width: 768px) {
  .main-wrapper {
    margin-left: 0 !important;
    max-width: 100vw !important;
  }
  .main-wrapper .container {
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
