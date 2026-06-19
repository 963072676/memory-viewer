import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

type Theme = 'light' | 'dark' | 'system'
type ViewMode = 'list' | 'graph' | 'timeline'
const VIEW_MODES: ViewMode[] = ['list', 'graph', 'timeline']

export const useUIStore = defineStore('ui', () => {
  const currentTab = ref<'all' | 'agentmemory' | 'hermes'>('all')
  const searchQuery = ref('')
  const selectedProfile = ref<string | null>(null)
  const sidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true')

  // Persist sidebar collapsed state to localStorage
  watch(sidebarCollapsed, (val) => {
    localStorage.setItem('sidebarCollapsed', String(val))
  })
  const theme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'system')
  const sortBy = ref<'updatedAt' | 'createdAt' | 'strength' | 'type'>('updatedAt')
  const sortOrder = ref<'asc' | 'desc'>('desc')
  const savedViewMode = localStorage.getItem('memoryViewMode') as ViewMode | null
  const viewMode = ref<ViewMode>(savedViewMode && VIEW_MODES.includes(savedViewMode) ? savedViewMode : 'list')
  const allExpanded = ref<boolean | null>(null)
  const showKeyboardHelp = ref(false)
  const showArchived = ref(false)
  // PM-20260612-002 F2: 控制 FeatureTour 弹层显隐 (TourStep.vue @close 触发)
  const showTour = ref(false)

  function setTab(tab: 'all' | 'agentmemory' | 'hermes') {
    currentTab.value = tab
  }

  function setSearch(query: string) {
    searchQuery.value = query
  }

  function setProfile(profile: string | null) {
    selectedProfile.value = profile
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setTheme(t: Theme) {
    theme.value = t
    localStorage.setItem('theme', t)
    applyTheme(t)
  }

  function applyTheme(t: Theme) {
    if (t === 'dark' || (t === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.setAttribute('data-theme', 'dark')
    } else {
      document.documentElement.removeAttribute('data-theme')
    }
  }

  function setSort(field: typeof sortBy.value, order?: typeof sortOrder.value) {
    sortBy.value = field
    if (order) sortOrder.value = order
  }

  function setViewMode(mode: ViewMode) {
    viewMode.value = mode
    localStorage.setItem('memoryViewMode', mode)
  }

  function toggleSortOrder() {
    sortOrder.value = sortOrder.value === 'desc' ? 'asc' : 'desc'
  }

  function toggleAllExpanded() {
    allExpanded.value = allExpanded.value === null ? true : !allExpanded
    if (allExpanded.value === false) allExpanded.value = null
  }

  function toggleKeyboardHelp() {
    showKeyboardHelp.value = !showKeyboardHelp.value
  }

  function setShowTour(v: boolean) {
    showTour.value = v
  }

  // Apply theme on init
  applyTheme(theme.value)

  // Listen for system theme changes
  if (typeof window !== 'undefined') {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (theme.value === 'system') applyTheme('system')
    })
  }

  return {
    currentTab,
    searchQuery,
    selectedProfile,
    sidebarCollapsed,
    theme,
    sortBy,
    sortOrder,
    viewMode,
    allExpanded,
    showKeyboardHelp,
    showArchived,
    showTour,
    setTab,
    setSearch,
    setProfile,
    toggleSidebar,
    setTheme,
    setSort,
    setViewMode,
    toggleSortOrder,
    toggleAllExpanded,
    toggleKeyboardHelp,
    setShowTour,
  }
})
