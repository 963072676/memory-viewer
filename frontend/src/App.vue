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
        <router-view />
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
  background: var(--bg-primary);
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
</style>
