<template>
  <div class="home-view">
    <!-- Search Results -->
    <div v-if="uiStore.searchQuery && (searchStore.results || searchStore.semanticResults)" class="search-results">
      <div class="search-header">
        <h2>{{ searchStore.searchMode === 'semantic' ? '🧠 语义搜索结果' : '搜索结果' }}</h2>
        <span v-if="searchStore.results" class="result-count">找到 {{ searchStore.results.total }} 条结果</span>
        <span v-else-if="searchStore.semanticResults" class="result-count">找到 {{ searchStore.semanticResults.results.length }} 条结果</span>
      </div>
      <!-- Keyword results -->
      <div v-if="searchStore.results" class="card-grid">
        <div v-for="result in searchStore.results.results" :key="result.id || result.index" class="search-result-card">
          <div class="result-source">{{ result.source === 'agentmemory' ? '🤖 AgentMemory' : '🧠 Hermes' }}</div>
          <h3 v-if="result.title">{{ result.title }}</h3>
          <p class="match-snippet" v-html="sanitizeHighlight(result.matchSnippet)"></p>
          <div class="result-meta">
            <span v-if="result.type" class="type-badge">{{ result.type }}</span>
            <span v-if="result.profile" class="profile-badge">{{ result.profile }}</span>
          </div>
        </div>
      </div>
      <!-- Semantic results -->
      <div v-if="searchStore.semanticResults" class="card-grid">
        <div v-for="result in searchStore.semanticResults.results" :key="result.id" class="search-result-card search-result-card--semantic">
          <div class="result-source">
            <span class="semantic-badge">🧠</span>
            <span class="similarity-score">相似度: {{ (result.similarity * 100).toFixed(1) }}%</span>
          </div>
          <h3 v-if="result.title">{{ result.title }}</h3>
          <p class="match-snippet">{{ result.snippet }}</p>
          <div class="result-meta">
            <span v-if="result.type" class="type-badge">{{ result.type }}</span>
            <span v-for="tag in result.tags" :key="tag" class="type-badge">{{ tag }}</span>
            <span class="match-type-badge" :class="'match-type--' + result.match_type">
              {{ result.match_type === 'semantic' ? '语义匹配' : '关键词匹配' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Normal View -->
    <template v-else>
      <!-- Unified Memories Section (P16) -->
      <section class="section unified-section">
        <div class="section-header">
          <h2>🗂️ 统一记忆视图</h2>
          <div class="unified-controls">
            <label class="source-filter-label">数据源</label>
            <select v-model="selectedSource" class="source-filter-select" @change="onSourceChange">
              <option value="">All</option>
              <option value="hermes">hermes</option>
              <option value="agentmemory">agentmemory</option>
              <option value="mem0">mem0</option>
            </select>
          </div>
        </div>

        <div v-if="unifiedLoading" class="card-grid">
          <div v-for="i in 4" :key="'us-' + i" class="skeleton-card"></div>
        </div>
        <div v-else-if="unifiedMemories.length === 0" class="empty-state">
          <EmptyState
            icon="🗂️"
            title="还没有统一记忆"
            message="导入或创建第一批记忆，开始构建你的知识库。所有来源的记忆都会汇聚在这里。"
            action-text="导入记忆"
            @action="showImportModal = true"
          />
        </div>
        <div v-else class="card-grid">
          <div v-for="m in unifiedMemories" :key="m.id" class="unified-card">
            <div class="unified-card-header">
              <span class="source-badge" :class="'source-' + (m.source || 'unknown')">{{ m.source || 'unknown' }}</span>
              <span class="unified-type" v-if="m.type">{{ m.type }}</span>
            </div>
            <div class="unified-card-body">
              <h3 class="unified-title">{{ m.title }}</h3>
              <p class="unified-content">{{ m.content }}</p>
            </div>
            <div class="unified-card-footer">
              <span v-if="m.strength" class="unified-strength">强度: {{ m.strength }}</span>
              <span v-for="c in (m.concepts || []).slice(0, 3)" :key="c" class="unified-concept">{{ c }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Filter Panel -->
      <FilterPanel />

      <!-- Dedup Panel (F-21) -->
      <DuplicatePanel :show="showDedupPanel" @close="showDedupPanel = false" />

      <!-- AgentMemory Section -->
      <section v-if="uiStore.currentTab !== 'hermes'" class="section">
        <div class="section-header">
          <h2>AgentMemory</h2>
          <div class="section-actions">
            <button class="action-btn" @click="showCreateModal = true">+ 创建</button>
            <button class="action-btn" @click="showImportModal = true">📥 导入</button>
            <ExportButton />
            <button class="action-btn" @click="showDedupPanel = !showDedupPanel">🔍 去重</button>
          </div>
        </div>
        <div v-if="agentMemoryStore.loading" class="card-grid">
          <div v-for="i in 6" :key="i" class="skeleton-card"></div>
        </div>
        <div v-else-if="filteredMemories.length === 0" class="empty-state">
          <EmptyState
            icon="🤖"
            title="还没有 AgentMemory 记忆"
            message="点击右上角「创建」手动添加，或「导入」从其它来源批量导入。"
            action-text="创建记忆"
            @action="showCreateModal = true"
          />
        </div>
        <VirtualCardGrid
          v-else-if="filteredMemories.length > 200"
          :items="filteredMemories"
          :item-size="200"
          :key-field="'id'"
        >
          <template #default="{ item }">
            <MemoryCard
              :memory="item"
              :force-expanded="uiStore.allExpanded"
            />
          </template>
        </VirtualCardGrid>
        <div v-else class="card-grid">
          <MemoryCard
            v-for="m in filteredMemories"
            :key="m.id"
            :memory="m"
            :force-expanded="uiStore.allExpanded"
          />
        </div>
      </section>

      <!-- Hermes Memory Section -->
      <section v-if="uiStore.currentTab !== 'agentmemory'" class="section">
        <h2>Hermes Memory</h2>
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
import { useRoute } from 'vue-router'
import { useAgentMemoryStore } from '@/stores/agentmemory'
import { useHermesMemoryStore } from '@/stores/hermes-memory'
import { useUIStore } from '@/stores/ui'
import { useSearchStore } from '@/stores/search'
import { fetchUnifiedMemories, type UnifiedMemory } from '@/api/sources'
import MemoryCard from '@/components/Layout/MemoryCard.vue'
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

const showCreateModal = ref(false)
const showImportModal = ref(false)
const showDedupPanel = ref(false)
const route = useRoute()

// Listen for command palette create-memory shortcut
function onCreateFromPalette() {
  showCreateModal.value = true
}
window.addEventListener('app-create-memory', onCreateFromPalette)

// P16: Unified memories state
const selectedSource = ref((route.query.source as string) || '')
const unifiedMemories = ref<UnifiedMemory[]>([])
const unifiedLoading = ref(false)

async function loadUnifiedMemories() {
  unifiedLoading.value = true
  try {
    const res = await fetchUnifiedMemories({ limit: 50, source: selectedSource.value })
    unifiedMemories.value = res.memories
  } catch (e) {
    console.error('Failed to load unified memories:', e)
  } finally {
    unifiedLoading.value = false
  }
}

function onSourceChange() {
  loadUnifiedMemories()
}

onMounted(() => loadUnifiedMemories())
watch(() => route.query.source, (val) => {
  if (val && typeof val === 'string') {
    selectedSource.value = val
    loadUnifiedMemories()
  }
})

const filteredMemories = computed(() => {
  let memories = [...agentMemoryStore.memories]

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

.section {
  margin-bottom: 48px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.section-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 8px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--primary);
  font-size: 0.8rem;
  font-family: var(--font);
  cursor: pointer;
  transition: background 0.2s;
}

.action-btn:hover {
  background: var(--tag-bg);
}

h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 20px;
}

.section-header h2 {
  margin-bottom: 0;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

/* P37: 重复 unified-card 块已合并到下方 "Card layout" 段（更具体位置），这里不再重复 */

/* Profile section (memory viewer list) */
.profile-section {
  margin-bottom: 32px;
}

.profile-heading {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--primary);
  letter-spacing: -0.01em;
}

.hermes-card {
  background: var(--card);
  border-radius: var(--radius);
  padding: 16px;
  box-shadow: var(--shadow);
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

.result-count {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.search-result-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
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
  border-left: 3px solid var(--semantic-accent, #8b5cf6);
}

.semantic-badge {
  font-size: 0.85rem;
  margin-right: 4px;
}

.similarity-score {
  font-size: 0.75rem;
  color: var(--semantic-accent, #8b5cf6);
  font-weight: 500;
}

.match-type-badge {
  font-weight: 500;
}

.match-type--semantic {
  background: rgba(139, 92, 246, 0.1);
  color: var(--semantic-accent, #8b5cf6);
}

.match-type--keyword {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
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

.source-filter-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.source-filter-select {
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

/* P37: Card layout (desktop) — shadow-as-border */
.unified-card {
  background: var(--card);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
  cursor: pointer;
  position: relative;
  box-shadow: var(--shadow);
}

.unified-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--accent-secondary, #6366f1));
  opacity: 0;
  transition: opacity 0.2s ease;
}

.unified-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
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
  font-size: 0.65rem;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.source-badge.source-hermes {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.source-badge.source-agentmemory {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.source-badge.source-mem0 {
  background: rgba(168, 85, 247, 0.1);
  color: #a855f7;
}

.source-badge.source-unknown {
  background: var(--tag-bg);
  color: var(--text-secondary);
}

.unified-type {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 8px;
  background: var(--tag-bg);
  color: var(--text-secondary);
}

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
  background: rgba(251, 191, 36, 0.1);
  color: #f59e0b;
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

  .card-grid {
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
}
</style>
