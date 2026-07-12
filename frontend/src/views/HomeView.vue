<template>
  <div class="home-view">
    <!-- Search Results -->
    <div v-if="uiStore.searchQuery && (searchStore.results || searchStore.semanticResults)" class="search-results">
      <!-- P38 r27: search-header h2 → section-title 视觉锚点统一.
           之前 <h2> 直接在 .search-header (flex container) 里, 无 3px accent bar.
           与全站 7 个 view section-title 系统不一致 (AgentMemory/HermesMemory/Profiles/Sources/Dashboard/Compare/Collections 都有).
           加 class="section-title" + flex 安全 padding 复用 r20 模式. -->
      <div class="search-header">
        <h2 class="section-title">{{ searchStore.searchMode === 'semantic' ? '🧠 ' + $t('i18n.truly_become') : $t('i18n.search_memories') }}</h2>
        <span v-if="searchStore.results" class="result-count">{{ $t('i18n.found') }} {{ searchStore.results.total }} {{ $t('i18n.results') }}</span>
        <span v-else-if="searchStore.semanticResults" class="result-count">{{ $t('i18n.found') }} {{ searchStore.semanticResults.results.length }} {{ $t('i18n.results') }}</span>
      </div>
      <!-- Keyword results -->
      <div v-if="searchStore.results" class="card-grid">
        <div v-for="result in searchStore.results.results" :key="result.id || result.index" class="search-result-card">
          <div class="result-source">{{ result.source === 'agentmemory' ? '🤖 AgentMemory' : '🧠 Hermes' }}</div>
          <h3 v-if="result.title">{{ result.title }}</h3>
          <p class="match-snippet" v-html="sanitizeHighlight(result.matchSnippet)"></p>
          <div class="result-meta">
            <span v-if="result.type" class="unified-type chip" :class="'chip--' + result.type">{{ result.type }}</span>
            <span v-if="result.profile" class="profile-badge">{{ result.profile }}</span>
          </div>
        </div>
      </div>
      <!-- Semantic results -->
      <div v-if="searchStore.semanticResults" class="card-grid">
        <div v-for="result in searchStore.semanticResults.results" :key="result.id" class="search-result-card search-result-card--semantic">
          <div class="result-source">
            <span class="semantic-badge">🧠</span>
            <span class="similarity-score">{{ $t('i18n.similarity') }}: {{ (result.similarity * 100).toFixed(1) }}%</span>
          </div>
          <h3 v-if="result.title">{{ result.title }}</h3>
          <p class="match-snippet">{{ result.snippet }}</p>
          <div class="result-meta">
            <span v-if="result.type" class="unified-type chip" :class="'chip--' + result.type">{{ result.type }}</span>
            <span v-for="tag in result.tags" :key="tag" class="type-badge">{{ tag }}</span>
            <span class="match-type-badge" :class="'match-type--' + result.match_type">
              {{ result.match_type === 'semantic' ? $t('tour.feature_intro') : $t('i18n.show_archived') }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Normal View -->
    <template v-else>
      <!-- Unified Memories Section (P16) -->
      <section v-if="uiStore.currentTab === 'all' && explorerViewMode === 'list'" class="section unified-section">
        <div class="section-header">
          <h2>🗂️ {{ $t('i18n.unified_memory') }}</h2>
          <div class="unified-controls">
            <div class="source-filter-control">
              <label for="unified-source-filter" class="source-filter-label">{{ $t('i18n.data_source') }}</label>
              <div class="source-filter-input">
                <select
                  id="unified-source-filter"
                  v-model="selectedSource"
                  class="source-filter-select"
                  :aria-busy="sourceOptionsLoading"
                  @change="onSourceChange"
                >
                  <option value="">{{ $t('en_all') }}</option>
                  <option v-for="source in sourceOptions" :key="source" :value="source">
                    {{ source }}
                  </option>
                </select>
                <span v-if="sourceOptionsLoading" class="source-filter-state" role="status">
                  {{ $t('i18n.source_filter_loading') }}
                </span>
                <button
                  v-else-if="sourceOptionsError"
                  type="button"
                  class="source-filter-refresh"
                  :aria-label="$t('i18n.source_filter_retry')"
                  :title="$t('i18n.source_filter_retry')"
                  @click="loadSourceOptions"
                >
                  ↻
                </button>
              </div>
            </div>
            <div class="view-mode-switch" :aria-label="$t('i18n.memory_view_mode')">
              <button
                v-for="mode in viewModes"
                :key="mode.value"
                type="button"
                class="view-mode-btn"
                :class="{ active: explorerViewMode === mode.value }"
                :aria-pressed="explorerViewMode === mode.value"
                @click="setExplorerViewMode(mode.value)"
              >
                {{ $t(mode.labelKey) }}
              </button>
            </div>
          </div>
        </div>

        <div v-if="unifiedLoading" class="card-grid">
          <div v-for="i in 4" :key="'us-' + i" class="skeleton-card"></div>
        </div>
        <!-- P38 r30: EmptyState prop 改 v-bind — 原 $t() 字符串在 prop 里是死的，
             渲染时直接显示 "$t('i18n.unified_memories')" 原文。现在用 :title="..." 触发 i18n 计算。 -->
        <div v-else-if="unifiedError" class="unified-error-state" role="alert">
          <div class="unified-error-copy">
            <strong>{{ $t('i18n.load_failed') }}</strong>
            <span>{{ $t('i18n.source_filter_load_failed', { source: selectedSource || $t('en_all') }) }}</span>
          </div>
          <button type="button" class="action-btn" @click="retryUnifiedView">
            {{ $t('i18n.retry') }}
          </button>
        </div>
        <div v-else-if="unifiedMemories.length === 0" class="empty-state">
          <EmptyState
            icon="🗂️"
            :title="selectedSource ? $t('i18n.source_filter_empty_title', { source: selectedSource }) : $t('i18n.unified_memories')"
            :message="selectedSource ? $t('i18n.source_filter_empty_message') : `${$t('i18n.import_create')}，${$t('i18n.start_building')}。${$t('i18n.memories_all')}。`"
            :action-text="selectedSource ? $t('i18n.source_management') : $t('i18n.import_memory')"
            @action="handleUnifiedEmptyAction"
          />
        </div>
        <div
          v-else
          class="explorer-shell"
          :class="{ 'explorer-shell--with-preview': selectedUnifiedMemory }"
        >
          <div class="explorer-main">
            <div class="card-grid">
              <button
                v-for="m in unifiedMemories"
                :key="m.id"
                type="button"
                class="unified-card"
                :class="{ 'unified-card--selected': selectedUnifiedMemoryId === m.id }"
                :aria-pressed="selectedUnifiedMemoryId === m.id"
                @click="selectUnifiedMemory(m.id)"
              >
                <div class="unified-card-header">
                  <span class="source-badge" :class="'source-' + (m.source || 'unknown')">{{ m.source || 'unknown' }}</span>
                  <span v-if="m.type" class="unified-type chip" :class="'chip--' + m.type">{{ m.type }}</span>
                </div>
                <div class="unified-card-body">
                  <h3 class="unified-title">{{ m.title }}</h3>
                  <p class="unified-content">{{ m.content }}</p>
                </div>
                <div class="unified-card-footer">
                  <span v-if="m.strength" class="unified-strength">{{ $t('i18n.preview_strength') }}: {{ m.strength }}</span>
                  <span v-for="c in (m.concepts || []).slice(0, 3)" :key="c" class="unified-concept">{{ c }}</span>
                </div>
              </button>
            </div>
          </div>
          <MemoryPreviewPanel
            v-if="selectedUnifiedMemory"
            :unified-memory="selectedUnifiedMemory"
            @close="closeUnifiedMemoryPreview"
          />
        </div>
      </section>

      <!-- Filter Panel -->
      <FilterPanel v-if="uiStore.currentTab === 'agentmemory'" />

      <!-- Dedup Panel (F-21) -->
      <DuplicatePanel
        v-if="uiStore.currentTab === 'agentmemory'"
        :show="showDedupPanel"
        @close="showDedupPanel = false"
      />

      <!-- AgentMemory Section -->
      <section v-if="uiStore.currentTab !== 'all' || explorerViewMode !== 'list'" class="section">
        <div class="section-header">
          <h2>{{ uiStore.currentTab === 'agentmemory' ? 'AgentMemory' : $t('i18n.memory_explorer') }}</h2>
          <div class="section-actions">
            <div class="view-mode-switch" :aria-label="$t('i18n.memory_view_mode')">
              <button
                v-for="mode in viewModes"
                :key="mode.value"
                type="button"
                class="view-mode-btn"
                :class="{ active: explorerViewMode === mode.value }"
                :aria-pressed="explorerViewMode === mode.value"
                @click="setExplorerViewMode(mode.value)"
              >
                {{ $t(mode.labelKey) }}
              </button>
            </div>
            <template v-if="uiStore.currentTab === 'agentmemory'">
              <!-- P39: button hierarchy — 创建 is the most common action → primary, others secondary -->
              <button class="action-btn action-btn--primary" @click="showCreateModal = true">+ {{ $t('i18n.create.action') }}</button>
              <button class="action-btn" @click="showImportModal = true">📥 {{ $t('i18n.import') }}</button>
              <ExportButton />
              <button class="action-btn" @click="showDedupPanel = !showDedupPanel">🔍 {{ $t('i18n.deduplicate') }}</button>
            </template>
          </div>
        </div>
        <div v-if="uiStore.currentTab === 'agentmemory' && agentMemoryStore.loading" class="card-grid">
          <div v-for="i in 6" :key="i" class="skeleton-card"></div>
        </div>
        <div v-else-if="uiStore.currentTab === 'agentmemory' && filteredMemories.length === 0" class="empty-state">
          <!-- P38 r30: EmptyState prop 改 v-bind (同 r30 上一组) -->
          <EmptyState
            icon="🤖"
            :title="`${$t('i18n.nohas')} AgentMemory 记忆`"
            :message="`${$t('i18n.top_right')}「${$t('i18n.create')}」${$t('i18n.add_manually')}，或「${$t('i18n.import')}」${$t('i18n.bulk_import')}。`"
            :action-text="$t('i18n.create.action')"
            @action="showCreateModal = true"
          />
        </div>
        <div
          class="explorer-shell"
          :class="{ 'explorer-shell--with-preview': selectedPreviewNode }"
        >
          <div class="explorer-main">
            <MemoryGraphPanel
              v-if="explorerViewMode === 'graph'"
              embedded
              :selected-node-id="selectedGraphNodeId"
              :show-node-detail="false"
              @select-node="selectGraphNode"
              @clear-selection="closeMemoryPreview"
            />
            <MemoryTimeline
              v-else-if="explorerViewMode === 'timeline'"
              :memories="filteredMemories"
              :selected-id="selectedMemoryId"
              @select="selectMemory"
            />
            <VirtualCardGrid
              v-if="uiStore.currentTab === 'agentmemory' && explorerViewMode === 'list' && filteredMemories.length > 200"
              :items="filteredMemories"
              :item-size="200"
              :key-field="'id'"
            >
              <template #default="{ item }">
                <div
                  class="memory-card-shell"
                  :class="{ 'memory-card-shell--selected': selectedMemoryId === item.id }"
                  @click="selectMemory(item.id)"
                >
                  <MemoryCard
                    :memory="item"
                    :force-expanded="uiStore.allExpanded"
                  />
                </div>
              </template>
            </VirtualCardGrid>
            <div
              v-else-if="uiStore.currentTab === 'agentmemory' && explorerViewMode === 'list' && filteredMemories.length > 0"
              class="card-grid"
            >
              <div
                v-for="m in filteredMemories"
                :key="m.id"
                class="memory-card-shell"
                :class="{ 'memory-card-shell--selected': selectedMemoryId === m.id }"
                @click="selectMemory(m.id)"
              >
                <MemoryCard
                  :memory="m"
                  :force-expanded="uiStore.allExpanded"
                />
              </div>
            </div>
          </div>
          <MemoryPreviewPanel
            v-if="selectedPreviewNode"
            :memory="selectedMemory"
            :graph-node="selectedGraphPreviewNode"
            :graph-connection-count="selectedGraphConnectionCount"
            @close="closeMemoryPreview"
          />
        </div>
      </section>

      <!-- Hermes Memory Section -->
      <section v-if="uiStore.currentTab === 'hermes'" class="section">
        <!-- P38 r27: section-header wrapper + section-title class — 3px accent bar.
             之前 <h2> 直接在 <section> 里, 无 section-header 父级, 无 3px accent bar.
             与上方 AgentMemory section (line 96-106) + 7 个 view 顶层 section-title 系统不一致.
             复用 r15 + r20 模式 (3px rail + 12px padding-left). -->
        <div class="section-header">
          <h2 class="section-title">Hermes Memory</h2>
        </div>
        <div v-if="hermesMemoryStore.loading" class="card-grid">
          <div v-for="i in 4" :key="i" class="skeleton-card"></div>
        </div>
        <div v-else-if="hermesMemoryStore.totalEntries === 0" class="empty-state">
          <EmptyState
            icon="🧠"
            title="还没有 Hermes Memory"
            message="从 Hermes Agent 同步记忆数据，或在「数据源」中配置连接。"
            action-text="配置数据源"
            @action="$router.push('/sources')"
          />
        </div>
        <template v-else>
          <!-- Global -->
          <div class="profile-section">
            <h3 class="profile-heading">🌐 Global</h3>
            <div class="card-grid">
              <div v-for="(entry, i) in hermesMemoryStore.globalData.memory" :key="'gm-' + i" class="hermes-card">
                <div class="hermes-label">MEMORY.md</div>
                <p>{{ entry }}</p>
              </div>
              <div v-for="(entry, i) in hermesMemoryStore.globalData.user" :key="'gu-' + i" class="hermes-card">
                <div class="hermes-label">USER.md</div>
                <p>{{ entry }}</p>
              </div>
            </div>
          </div>
          <!-- Profiles -->
          <div v-for="(data, name) in hermesMemoryStore.profiles" :key="name" class="profile-section">
            <h3 class="profile-heading">👤 {{ name }}</h3>
            <div class="card-grid">
              <div v-for="(entry, i) in data.memory" :key="'pm-' + i" class="hermes-card">
                <div class="hermes-label">MEMORY.md</div>
                <p>{{ entry }}</p>
              </div>
              <div v-for="(entry, i) in data.user" :key="'pu-' + i" class="hermes-card">
                <div class="hermes-label">USER.md</div>
                <p>{{ entry }}</p>
              </div>
            </div>
          </div>
        </template>
      </section>
    </template>

    <CreateMemoryModal v-if="showCreateModal" @close="showCreateModal = false" @created="onCreated" />
    <ImportModal v-if="showImportModal" @close="showImportModal = false" @imported="onImported" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAgentMemoryStore } from '@/stores/agentmemory'
import { useHermesMemoryStore } from '@/stores/hermes-memory'
import { useUIStore } from '@/stores/ui'
import { useSearchStore } from '@/stores/search'
import { useSessionStore } from '@/stores/sessions'
import { fetchSources, fetchUnifiedMemories, type UnifiedMemory } from '@/api/sources'
import type { MemoryGraphNode } from '@/api/graph'
import MemoryCard from '@/components/Layout/MemoryCard.vue'
import MemoryGraphPanel from '@/components/Layout/MemoryGraphPanel.vue'
import MemoryPreviewPanel from '@/components/Layout/MemoryPreviewPanel.vue'
import MemoryTimeline from '@/components/Layout/MemoryTimeline.vue'
import VirtualCardGrid from '@/components/Layout/VirtualCardGrid.vue'
import ExportButton from '@/components/Layout/ExportButton.vue'
import CreateMemoryModal from '@/components/Layout/CreateMemoryModal.vue'
import ImportModal from '@/components/Layout/ImportModal.vue'
import FilterPanel from '@/components/Layout/FilterPanel.vue'
import DuplicatePanel from '@/components/Layout/DuplicatePanel.vue'
import EmptyState from '@/components/Layout/EmptyState.vue'
import { sanitizeHighlight } from '@/utils/highlight'

const agentMemoryStore = useAgentMemoryStore()
const hermesMemoryStore = useHermesMemoryStore()
const uiStore = useUIStore()
const searchStore = useSearchStore()
const sessionStore = useSessionStore()

const showCreateModal = ref(false)
const showImportModal = ref(false)
const showDedupPanel = ref(false)
const selectedUnifiedMemoryId = ref('')
const selectedMemoryId = ref('')
const selectedGraphNodeId = ref('')
const selectedGraphNode = ref<MemoryGraphNode | null>(null)
const selectedGraphConnectionCount = ref(0)
const route = useRoute()
const router = useRouter()

// Listen for command palette create-memory shortcut
function onCreateFromPalette() {
  showCreateModal.value = true
}
window.addEventListener('app-create-memory', onCreateFromPalette)

// P16: Unified memories state
const initialSource = firstQueryValue(route.query.source)
const selectedSource = ref(typeof initialSource === 'string' ? initialSource : '')
const registeredSourceNames = ref<string[]>([])
const discoveredSourceNames = ref<string[]>([])
const sourceOptionsLoading = ref(false)
const sourceOptionsError = ref(false)
const unifiedMemories = ref<UnifiedMemory[]>([])
const unifiedLoading = ref(false)
const unifiedError = ref(false)
let unifiedRequestId = 0
const selectedUnifiedMemory = computed(() => (
  unifiedMemories.value.find(memory => memory.id === selectedUnifiedMemoryId.value) || null
))
const sourceOptions = computed(() => {
  const names = Array.from(new Set(registeredSourceNames.value))
  for (const name of discoveredSourceNames.value) {
    if (!names.includes(name)) names.push(name)
  }
  if (selectedSource.value && !names.includes(selectedSource.value)) {
    names.push(selectedSource.value)
  }
  return names
})
const viewModes = [
  { value: 'list' as const, labelKey: 'i18n.explorer_list' },
  { value: 'graph' as const, labelKey: 'i18n.explorer_graph' },
  { value: 'timeline' as const, labelKey: 'i18n.explorer_timeline' },
]

type ExplorerViewMode = typeof viewModes[number]['value']
const explorerViewMode = computed<ExplorerViewMode>(() => (
  uiStore.viewMode === 'graph' || uiStore.viewMode === 'timeline' ? uiStore.viewMode : 'list'
))

function firstQueryValue(value: unknown) {
  return Array.isArray(value) ? value[0] : value
}

function normalizeExplorerViewMode(value: unknown): ExplorerViewMode | '' {
  const raw = firstQueryValue(value)
  return raw === 'list' || raw === 'graph' || raw === 'timeline' ? raw : ''
}

function applyRouteViewMode(value: unknown) {
  const mode = normalizeExplorerViewMode(value)
  if (mode && uiStore.viewMode !== mode) {
    uiStore.setViewMode(mode)
  }
}

function setExplorerViewMode(mode: ExplorerViewMode) {
  uiStore.setViewMode(mode)
  const query = { ...route.query }
  const nextView = mode === 'list' ? undefined : mode
  const currentView = firstQueryValue(route.query.view) || undefined

  if (currentView === nextView) return
  if (nextView) {
    query.view = nextView
  } else {
    delete query.view
  }
  router.replace({ query })
}

function applyRouteMemoryId(value: unknown) {
  const raw = firstQueryValue(value)
  const id = typeof raw === 'string' ? raw : ''
  if (id && uiStore.currentTab === 'all') {
    uiStore.setTab('agentmemory')
  }
  selectedMemoryId.value = id
  selectedGraphNodeId.value = id
  if (!id || selectedGraphNode.value?.id !== id) {
    selectedGraphNode.value = null
    selectedGraphConnectionCount.value = 0
  }
}

function selectMemory(id: string) {
  selectedUnifiedMemoryId.value = ''
  selectedMemoryId.value = id
  selectedGraphNodeId.value = id
  if (firstQueryValue(route.query.memory) === id) return
  router.replace({ query: { ...route.query, memory: id } })
}

function selectGraphNode(selection: { node: MemoryGraphNode; connectionCount: number }) {
  selectedGraphNode.value = selection.node
  selectedGraphConnectionCount.value = selection.connectionCount
  selectMemory(selection.node.id)
}

function closeMemoryPreview() {
  selectedMemoryId.value = ''
  selectedGraphNodeId.value = ''
  selectedGraphNode.value = null
  selectedGraphConnectionCount.value = 0
  const query = { ...route.query }
  delete query.memory
  router.replace({ query })
}

async function loadUnifiedMemories() {
  const requestId = ++unifiedRequestId
  const source = selectedSource.value
  unifiedLoading.value = true
  unifiedError.value = false
  try {
    const res = await fetchUnifiedMemories({ limit: 50, source })
    if (requestId !== unifiedRequestId) return
    unifiedMemories.value = res.memories
    const discovered = new Set(discoveredSourceNames.value)
    for (const memory of res.memories) {
      if (memory.source) discovered.add(memory.source)
    }
    discoveredSourceNames.value = Array.from(discovered)
    if (!res.memories.some(memory => memory.id === selectedUnifiedMemoryId.value)) {
      selectedUnifiedMemoryId.value = ''
    }
  } catch (e) {
    if (requestId !== unifiedRequestId) return
    console.error('Failed to load unified memories:', e)
    unifiedMemories.value = []
    selectedUnifiedMemoryId.value = ''
    unifiedError.value = true
  } finally {
    if (requestId === unifiedRequestId) unifiedLoading.value = false
  }
}

async function loadSourceOptions() {
  sourceOptionsLoading.value = true
  sourceOptionsError.value = false
  try {
    const res = await fetchSources()
    registeredSourceNames.value = res.sources.map(source => source.name)
  } catch (e) {
    console.error('Failed to load source options:', e)
    sourceOptionsError.value = true
  } finally {
    sourceOptionsLoading.value = false
  }
}

function retryUnifiedView() {
  loadSourceOptions()
  loadUnifiedMemories()
}

function onSourceChange() {
  selectedUnifiedMemoryId.value = ''
  const query = { ...route.query }
  if (selectedSource.value) {
    query.source = selectedSource.value
  } else {
    delete query.source
  }
  router.push({ query })
  loadUnifiedMemories()
}

function handleUnifiedEmptyAction() {
  if (selectedSource.value) {
    router.push('/sources')
    return
  }
  showImportModal.value = true
}

function selectUnifiedMemory(id: string) {
  selectedUnifiedMemoryId.value = id
  selectedMemoryId.value = ''
  selectedGraphNodeId.value = ''
  selectedGraphNode.value = null
  selectedGraphConnectionCount.value = 0

  if (route.query.memory) {
    const query = { ...route.query }
    delete query.memory
    router.replace({ query })
  }
}

function closeUnifiedMemoryPreview() {
  selectedUnifiedMemoryId.value = ''
}

onMounted(() => {
  applyRouteViewMode(route.query.view)
  applyRouteMemoryId(route.query.memory)
  loadSourceOptions()
  loadUnifiedMemories()
})
watch(() => route.query.view, applyRouteViewMode)
watch(() => route.query.memory, applyRouteMemoryId)
watch(() => route.query.source, (val) => {
  const raw = firstQueryValue(val)
  const source = typeof raw === 'string' ? raw : ''
  if (selectedSource.value === source) return
  selectedSource.value = source
  selectedUnifiedMemoryId.value = ''
  loadUnifiedMemories()
})

const filteredMemories = computed(() => {
  let memories = [...agentMemoryStore.memories]

  if (sessionStore.activeSessionId) {
    memories = memories.filter(m => (m.sessionIds || []).includes(sessionStore.activeSessionId))
  }

  // Filter archived (F-15)
  if (!uiStore.showArchived) {
    memories = memories.filter(m => !m.archived)
  }

  // Filter by search
  if (uiStore.searchQuery) {
    const q = uiStore.searchQuery.toLowerCase()
    memories = memories.filter(m =>
      m.title.toLowerCase().includes(q) ||
      m.content.toLowerCase().includes(q) ||
      m.concepts.some(c => c.toLowerCase().includes(q))
    )
  }

  // Sort
  const sortField = uiStore.sortBy
  const order = uiStore.sortOrder === 'desc' ? -1 : 1
  memories.sort((a, b) => {
    if (sortField === 'strength') return (a.strength - b.strength) * order
    if (sortField === 'type') return a.type.localeCompare(b.type) * order
    const aVal = a[sortField] || ''
    const bVal = b[sortField] || ''
    return aVal.localeCompare(bVal) * order
  })

  return memories
})

const selectedMemory = computed(() => (
  filteredMemories.value.find(memory => memory.id === selectedMemoryId.value) || null
))

const selectedGraphPreviewNode = computed(() => (
  explorerViewMode.value === 'graph' ? selectedGraphNode.value : null
))

const selectedPreviewNode = computed(() => (
  selectedMemory.value || selectedGraphPreviewNode.value
))

function onCreated() {
  agentMemoryStore.refresh()
}

function onImported() {
  agentMemoryStore.refresh()
}
</script>

<style scoped>
.home-view {
  padding-bottom: 40px;
}

/* P40: section 间距改用 spacing token，节奏系统化 */
.section {
  margin-bottom: var(--space-section-gap);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-header-gap);
  flex-wrap: wrap;
  gap: var(--space-3);
}

.section-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.view-mode-switch {
  display: inline-flex;
  flex: 0 0 auto;
  overflow: hidden;
  min-height: 34px;
  padding: 2px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--tag-bg);
}

.view-mode-btn {
  min-width: 74px;
  padding: 5px 10px;
  border: 0;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-family: var(--font);
  font-size: 0.78rem;
  font-weight: 600;
  transition: background 0.15s ease, color 0.15s ease, box-shadow 0.15s ease;
}

.view-mode-btn:hover {
  color: var(--primary);
}

.view-mode-btn.active {
  background: var(--card);
  color: var(--primary);
  box-shadow: var(--shadow-press);
}

.action-btn {
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--card);
  color: var(--primary);
  font-size: 0.8rem;
  font-family: var(--font);
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease, transform 0.1s ease;
}

.action-btn:hover {
  background: var(--tag-bg);
  border-color: var(--border-strong);
}

.action-btn:active {
  transform: translateY(1px);
}

/* P39: primary action — used for the dominant CTA in a section.
   Filled with --primary (ink) so it visually outranks the outline siblings
   without needing a brand color. White text reads cleanly in both themes. */
.action-btn--primary {
  background: var(--primary);
  color: var(--card);
  border-color: var(--primary);
  font-weight: 500;
  box-shadow: var(--shadow-press);
}

.action-btn--primary:hover {
  background: var(--primary-muted);
  border-color: var(--primary-muted);
  filter: none;
}

h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: var(--space-5);
}

.section-header h2 {
  margin-bottom: 0;
  /* P38 r15: section title 左侧 3px accent bar — 视觉锚点，区分 section title 与 card title。
     模仿 AppSidebar 已有的 .nav-item.active::before 设计语言 (3px rail + accent),
     形成全站一致的"被选中/重要"视觉语言。 */
  padding-left: 12px;
  position: relative;
}

.section-header h2::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: var(--accent);
  border-radius: 0 2px 2px 0;
}

/* P40: card-grid 间距改用 token */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-card-gap);
}

.explorer-shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--space-5);
  align-items: start;
}

.explorer-shell--with-preview {
  grid-template-columns: minmax(0, 1fr) minmax(300px, 360px);
}

.explorer-main {
  min-width: 0;
}

.memory-card-shell {
  min-width: 0;
  border-radius: var(--radius-md);
}

.memory-card-shell--selected {
  outline: 2px solid var(--accent);
  outline-offset: 3px;
}

/* P37: 重复 unified-card 块已合并到下方 "Card layout" 段（更具体位置），这里不再重复 */

/* Profile section (memory viewer list) */
.profile-section {
  margin-bottom: 32px;
}

.profile-heading {
  position: relative;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--primary);
  letter-spacing: -0.01em;
  /* P38 r28: h3 视觉锚点 — 2px accent bar 左侧 rail.
     与 HermesMemoryView .profile-heading 同源 (r27 section-title 3px bar 的 h3 变体).
     HermesMemoryView 在 P38 r20 升级时漏了这条, HomeView 跟着 HermesMemoryView 漏.
     2px bar + 10px padding-left 让 h3 与下方 hermes-card 视觉断点更清晰. */
  padding-left: 10px;
}

.profile-heading::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 2px;
  height: 70%;
  background: var(--accent);
  border-radius: 0 2px 2px 0;
}

/* P38 r35: .hermes-card 视觉对齐统一卡片家族 (r13 全站 4 套 + 现在的 5 套).
   之前 .hermes-card 是无 border / 无 hover / 无 transition 的"裸 box",
   与同页面 .unified-card (带 box-shadow + border + hover lift + ::before 渐变 bar) 视觉差 2 个档次,
   用户在 home 页上感觉"两块卡片来自两个项目".
   现在补齐: 1px border (与 MemoryCard / CollectionCard / DashboardWidget / TemplateCard 同源),
   box-shadow (var(--shadow) token), hover 上升 2px (比 unified-card 的 3px 轻一档,
   因为 hermes-card 内部是文本块, 不需要太多 lift), transition 0.25s cubic-bezier 同手感. */
.hermes-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  box-shadow: var(--shadow);
  transition: box-shadow 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              transform 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              border-color 0.2s ease;
}

.hermes-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
}

.hermes-label {
  font-size: 0.7rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.hermes-card p {
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.skeleton-card {
  height: 120px;
  background: linear-gradient(90deg, var(--tag-bg) 25%, var(--border) 50%, var(--tag-bg) 75%);
  background-size: 200% 100%;
  border-radius: var(--radius);
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* P37: empty-state wrapper 让 EmptyState 组件居中显示 */
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Search results */
.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

/* P38 r27: search-header h2.section-title 3px accent bar — 与全站 7 个 view section-title 同源.
   search-header 是 flex container, 之前 h2 没有视觉锚点, 与下方 section-header h2 系统不一致.
   flex + ::before absolute: left 0 紧贴 h2 左缘, padding-left 12px 给文字留空间.
   复用 r20 模式 (3px rail + 60% height + accent color + 2px right border-radius). */
.search-header h2.section-title {
  position: relative;
  padding-left: 12px;
  margin-bottom: 0;  /* search-header 自己控制 margin-bottom, 避免双重 margin */
}

.search-header h2.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: var(--accent);
  border-radius: 0 2px 2px 0;
}

.result-count {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* P38 r26: search-result-card hover — 复用 r12/r13 全站 4 套 Card 同源 hover 语言
   (transition 0.25s cubic-bezier, box-shadow 强 + transform translateY(-2px))。
   之前 .search-result-card 只有静态 border + radius, 无 hover, 与上下
   MemoryCard / unified-card / hermes-card / collection-card 形成 "粗糙" 对比.
   加上 hover 后跨 view 切换无视觉跳变. */
.search-result-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  transition: box-shadow 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              transform 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              border-color 0.2s ease;
}

.search-result-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
  border-color: var(--border-strong);
}

.result-source {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.search-result-card h3 {
  font-size: 0.95rem;
  margin-bottom: 8px;
  color: var(--primary);
}

.match-snippet {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.match-snippet :deep(em) {
  background: var(--highlight-bg);
  padding: 1px 2px;
  border-radius: 2px;
  font-style: normal;
}

.result-meta {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.type-badge,
.profile-badge,
.match-type-badge {
  font-size: 0.7rem;
  padding: 3px 8px;
  border-radius: 12px;
  background: var(--tag-bg);
  color: var(--text-secondary);
}

/* Semantic result styles */
.search-result-card--semantic {
  /* P38 r13: 删除硬编码 #8b5cf6 fallback — --semantic-accent token 已稳定在 variables.css */
  border-left: 3px solid var(--semantic-accent);
}

.semantic-badge {
  font-size: 0.85rem;
  margin-right: 4px;
}

.similarity-score {
  font-size: 0.75rem;
  /* P38 r13: 同上 */
  color: var(--semantic-accent);
  font-weight: 500;
}

.match-type-badge {
  font-weight: 500;
}

.match-type--semantic {
  /* P38 r13: token 化 — 复用 --semantic-accent + 0.1 alpha (用 color-mix 同源表达).
     之前 rgba(139, 92, 246, 0.1) + var(--semantic-accent, #8b5cf6) 双重硬编码 */
  background: color-mix(in srgb, var(--semantic-accent) 10%, transparent);
  color: var(--semantic-accent);
}

.match-type--keyword {
  /* P38 r13: token 化 — 复用 --accent (Vercel 蓝，与全站按钮/链接同源) + 0.1 alpha.
     之前 rgba(59, 130, 246, 0.1) + #3b82f6 是 Tailwind blue-500 hardcoded，dark 模式无覆盖，
     且与 --accent (#0072f5) 偏差 13 蓝度。 */
  background: color-mix(in srgb, var(--accent) 10%, transparent);
  color: var(--accent);
}

/* Unified memories section (P16) */
.unified-section {
  border-bottom: 1px solid var(--border);
  padding-bottom: 32px;
  margin-bottom: 32px;
}

.unified-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.source-filter-control,
.source-filter-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.source-filter-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
  white-space: nowrap;
}

.source-filter-select {
  min-width: 140px;
  padding: 6px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--primary);
  font-size: 0.85rem;
  font-family: var(--font);
  cursor: pointer;
  outline: none;
}

.source-filter-select:focus {
  border-color: var(--accent);
}

.source-filter-state {
  color: var(--text-tertiary);
  font-size: 0.75rem;
  white-space: nowrap;
}

.source-filter-refresh {
  width: 30px;
  height: 30px;
  flex: 0 0 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--card);
  color: var(--text-secondary);
  font: inherit;
  cursor: pointer;
}

.source-filter-refresh:hover,
.source-filter-refresh:focus-visible {
  border-color: var(--accent);
  color: var(--accent);
  outline: none;
}

.unified-error-state {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px;
  border: 1px solid var(--error-border);
  border-radius: var(--radius);
  background: var(--error-bg);
}

.unified-error-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: var(--error);
}

.unified-error-copy span {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

/* P37: Card layout (desktop) - shadow-as-border */
.unified-card {
  width: 100%;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--primary);
  font: inherit;
  text-align: left;
  border-radius: var(--radius-md);
  overflow: hidden;
  /* P38 r13: 与 P38 r12 全站 4 套 Card (MemoryCard / CollectionCard / DashboardWidget / TemplateCard)
     hover 视觉同源。transition 由 0.2s ease → 0.25s cubic-bezier (与 ring 0.5s / count-up 同手感)，
     并补 border-color 0.2s ease 让 hover 时 border-strong 平滑切换（之前无 border-color 过渡）。 */
  transition: box-shadow 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              transform 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              border-color 0.2s ease;
  cursor: pointer;
  position: relative;
  box-shadow: var(--shadow);
}

.unified-card--selected,
.unified-card:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 3px;
}

.unified-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--accent-secondary));
  opacity: 0;
  transition: opacity 0.2s ease;
}

.unified-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
  /* P38 r13: 补 border-strong hover，与 r12 4 套 Card 同源 */
  border-color: var(--border-strong);
}

.unified-card:hover::before {
  opacity: 1;
}

.unified-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding: 16px 16px 0 16px;
}

.unified-card-body {
  padding: 0 16px;
}

.unified-card-footer {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 12px 16px 16px 16px;
}

.source-badge {
  /* P38 r19: unify with .unified-type.chip — 6px radius + 1px border, no dot
     (color already encodes source identity, dot would be redundant).
     Previously 12px pill + no border, drifted from the row's adjacent type chip. */
  font-size: 0.625rem;
  padding: 3px 8px;
  border-radius: 6px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  border: 1px solid transparent;
  display: inline-flex;
  align-items: center;
}

/* P38 (round 6): source-badge token 化 — 之前 6 个 hex (3 bg + 3 text) + 0 个 dark
   适配 → 6 个 var() 引用，dark 模式由 variables.css 接管（与 type-chip 一致） */
.source-badge.source-hermes {
  background: var(--source-hermes-bg);
  color: var(--source-hermes-text);
  border-color: color-mix(in srgb, var(--source-hermes-text) 18%, transparent);
}

.source-badge.source-agentmemory {
  background: var(--source-agentmemory-bg);
  color: var(--source-agentmemory-text);
  border-color: color-mix(in srgb, var(--source-agentmemory-text) 18%, transparent);
}

.source-badge.source-mem0 {
  background: var(--source-mem0-bg);
  color: var(--source-mem0-text);
  border-color: color-mix(in srgb, var(--source-mem0-text) 18%, transparent);
}

.source-badge.source-unknown {
  background: var(--tag-bg);
  color: var(--text-secondary);
  border-color: var(--border);
}

/* P39: type chip — matches MemoryCard's badge system (uppercase + colored dot + bordered) */
.unified-type.chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.625rem;
  font-weight: 600;
  padding: 3px 8px 3px 7px;
  border-radius: 6px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  background: var(--tag-bg);
  color: var(--text-secondary);
  border: 1px solid transparent;
}

.unified-type.chip::before {
  content: '';
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.75;
  flex-shrink: 0;
}

.unified-type.chip--pattern     { background: var(--type-pattern-bg);     color: var(--type-pattern-text);     border-color: color-mix(in srgb, var(--type-pattern-text) 18%, transparent); }
.unified-type.chip--workflow    { background: var(--type-workflow-bg);    color: var(--type-workflow-text);    border-color: color-mix(in srgb, var(--type-workflow-text) 18%, transparent); }
.unified-type.chip--fact        { background: var(--type-fact-bg);        color: var(--type-fact-text);        border-color: color-mix(in srgb, var(--type-fact-text) 18%, transparent); }
.unified-type.chip--preference  { background: var(--type-preference-bg);  color: var(--type-preference-text);  border-color: color-mix(in srgb, var(--type-preference-text) 18%, transparent); }
.unified-type.chip--bug         { background: var(--type-bug-bg);         color: var(--type-bug-text);         border-color: color-mix(in srgb, var(--type-bug-text) 18%, transparent); }
.unified-type.chip--architecture{ background: var(--type-architecture-bg);color: var(--type-architecture-text);border-color: color-mix(in srgb, var(--type-architecture-text) 18%, transparent); }

.unified-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 8px;
  line-height: 1.4;
}

.unified-content {
  font-size: 0.85rem;
  line-height: 1.6;
  color: var(--text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 12px;
}

.unified-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.unified-strength {
  font-size: 0.7rem;
  padding: 3px 10px;
  border-radius: 12px;
  /* P38 r13: token 化 — 复用 --strength-mid-fill/--strength-mid-ink (黄色，与 MemoryCard ring 同源)
     之前 rgba(251, 191, 36, 0.1) / #f59e0b 是 Tailwind amber-400/100 hardcoded，dark 模式无覆盖 */
  background: color-mix(in srgb, var(--strength-mid-fill) 10%, transparent);
  color: var(--strength-mid-ink);
  font-weight: 500;
}

.unified-concept {
  font-size: 0.7rem;
  padding: 3px 10px;
  border-radius: 12px;
  background: var(--tag-bg);
  color: var(--text-secondary);
}

/* Responsive */
@media (max-width: 767px) {
  h2 {
    font-size: 1.2rem;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .section-actions {
    flex-wrap: wrap;
  }

  .unified-controls {
    width: 100%;
    min-width: 0;
    flex-direction: column;
    align-items: stretch;
  }

  .source-filter-select {
    width: 100%;
  }

  .source-filter-control {
    width: 100%;
    align-items: stretch;
    flex-direction: column;
  }

  .source-filter-input {
    width: 100%;
  }

  .source-filter-select {
    min-width: 0;
    flex: 1;
  }

  .unified-error-state {
    align-items: stretch;
    flex-direction: column;
  }

  .view-mode-switch {
    width: 100%;
    min-width: 0;
  }

  .view-mode-btn {
    flex: 1;
  }

  .card-grid {
    grid-template-columns: 1fr;
  }

  .explorer-shell,
  .explorer-shell--with-preview {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 768px) and (max-width: 1024px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .unified-controls {
    flex-direction: column;
    align-items: flex-start;
  }

  .explorer-shell,
  .explorer-shell--with-preview {
    grid-template-columns: 1fr;
  }
}
</style>
