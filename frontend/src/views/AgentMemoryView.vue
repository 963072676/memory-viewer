<template>
  <div class="agentmemory-view">
    <div class="view-header">
      <h2 class="section-title">AgentMemory</h2>
      <div class="view-actions">
        <!-- P38 (round 3): button hierarchy — 5 个按钮全平铺违反"primary 唯一"原则。
             「+ 创建」是最高频动作（用户主要操作）→ primary 药丸。
             其它（导入/导出/bulk-autotag/去重）都是次级批量操作 → secondary 统一处理。
             ai-autotag/dedup 之前用 var(--accent) 描边属于"伪 primary"，与真 primary 撞色，改为普通 secondary。 -->
        <button class="action-btn action-btn--primary" @click="showCreateModal = true">+ {{ $t('zh_00645e') }}</button>
        <button class="action-btn" @click="showImportModal = true">📥 {{ $t('zh_006597_1') }}</button>
        <ExportButton />
        <button
          class="action-btn"
          :disabled="autoTagLoading"
          @click="handleBulkAutoTag"
        >
          {{ autoTagLoading ? '⏳ 标注中...' : '✨ Bulk Auto-Tag' }}
        </button>
        <button
          class="action-btn"
          :disabled="dedupLoading"
          @click="handleFindDuplicates"
        >
          {{ dedupLoading ? '⏳ 查找中...' : '🔍 去重' }}
        </button>
      </div>
    </div>
    <div v-if="activeCollection" class="collection-filter-bar">
      <span class="filter-icon">{{ activeCollectionInfo?.icon }}</span>
      <span class="filter-label">{{ activeCollectionInfo?.name || activeCollection }}</span>
      <button class="filter-clear" @click="clearCollection">✕</button>
    </div>
    <FilterPanel />
    <!-- P21-T4: Quick filter/sort controls -->
    <div class="quick-controls">
      <select v-model="quickTypeFilter" class="control-select" @change="applyQuickFilter">
        <option value="">{{ $t('zh_ab7996') }}</option>
        <option value="pattern">Pattern</option>
        <option value="fact">Fact</option>
        <option value="preference">Preference</option>
        <option value="bug">Bug</option>
        <option value="workflow">Workflow</option>
        <option value="architecture">Architecture</option>
      </select>
      <select v-model="quickSortOrder" class="control-select" @change="applyQuickFilter">
        <option value="updatedAt-desc">{{ $t('zh_b69653') }}</option>
        <option value="updatedAt-asc">{{ $t('zh_b69745') }}</option>
        <option value="createdAt-desc">{{ $t('zh_b6939c') }}</option>
        <option value="createdAt-asc">{{ $t('zh_b6948f') }}</option>
        <option value="strength-desc">{{ $t('zh_0d2896') }}→低</option>
        <option value="strength-asc">{{ $t('zh_0d284b') }}→高</option>
      </select>
    </div>
    <div v-if="store.loading" class="card-grid">
      <div v-for="i in 6" :key="i" class="skeleton-card"></div>
    </div>
    <div v-else-if="filteredMemories.length === 0">
      <EmptyState
        icon="🧠"
        :title="activeCollection ? '该集合暂无记忆' : '暂无记忆'"
        :message="activeCollection ? '尝试切换到其他集合，或创建新的记忆' : '创建第一条记忆开始你的知识管理之旅'"
      />
    </div>
    <div v-else class="card-grid">
      <BatchToolbar :loading="batchLoading" @batch="handleBatch" @export="handleBatchExport" />
      <ConfirmDialog
        v-if="showDeleteConfirm"
        title="$t('zh_0ade99')"
        :message="`确定要删除选中的 ${store.selectionCount} 条记忆吗？此操作不可撤销。`"
        confirm-text="删除"
        cancel-text="取消"
        @confirm="confirmDelete"
        @cancel="showDeleteConfirm = false"
      />
      <MemoryCard
        v-for="m in filteredMemories"
        :key="m.id"
        :memory="m"
        :force-expanded="uiStore.allExpanded"
        @tag-click="onTagClick"
        @compare="onCompare"
      />
    </div>
    <CreateMemoryModal v-if="showCreateModal" @close="showCreateModal = false" @created="refresh" />
    <ImportModal v-if="showImportModal" @close="showImportModal = false" @imported="refresh" />
    <MemoryDiffModal
      v-if="showDiffModal && compareMemoryA && compareMemoryB"
      :memory-a="compareMemoryA"
      :memory-b="compareMemoryB"
      @close="closeDiffModal"
    />
    <DedupModal
      v-if="showDedupModal"
      :pairs="duplicatePairs"
      :selected-pairs="selectedPairs"
      @close="showDedupModal = false"
      @merge="handleMergeDuplicates"
      @refresh="refresh"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAgentMemoryStore } from '@/stores/agentmemory'
import { useUIStore } from '@/stores/ui'
import MemoryCard from '@/components/Layout/MemoryCard.vue'
import ExportButton from '@/components/Layout/ExportButton.vue'
import CreateMemoryModal from '@/components/Layout/CreateMemoryModal.vue'
import ImportModal from '@/components/Layout/ImportModal.vue'
import BatchToolbar from '@/components/Layout/BatchToolbar.vue'
import ConfirmDialog from '@/components/Layout/ConfirmDialog.vue'
import MemoryDiffModal from '@/components/Layout/MemoryDiffModal.vue'
import FilterPanel from '@/components/Layout/FilterPanel.vue'
import { batchAction } from '@/api/agentmemory'
import EmptyState from '@/components/Layout/EmptyState.vue'
import { exportAgentMemory } from '@/api/agentmemory'
import { bulkAutoTag } from '@/api/p8'
import { getDuplicates, mergeMemories } from '@/api/agentmemory'
import { useToast } from '@/composables/useToast'
import { useRouter, useRoute } from 'vue-router'
import type { AgentMemory, DuplicatePair } from '@/types'
import DedupModal from '@/components/Layout/DedupModal.vue'

const store = useAgentMemoryStore()
const uiStore = useUIStore()
const toast = useToast()
const router = useRouter()
const route = useRoute()
const showCreateModal = ref(false)
const showImportModal = ref(false)
const batchLoading = ref(false)
const showDeleteConfirm = ref(false)
const pendingBatchAction = ref<string | null>(null)
const autoTagLoading = ref(false)
const dedupLoading = ref(false)
const showDedupModal = ref(false)
const duplicatePairs = ref<DuplicatePair[]>([])
const selectedPairs = ref<Set<number>>(new Set())

// P18-2: Memory comparison state
const showDiffModal = ref(false)
const compareMemoryA = ref<AgentMemory | null>(null)
const compareMemoryB = ref<AgentMemory | null>(null)

// P21-T4: Quick filter/sort state
const quickTypeFilter = ref('')
const quickSortOrder = ref('updatedAt-desc')

function applyQuickFilter() {
  // Parse sort order
  const [sortField, sortDir] = quickSortOrder.value.split('-')
  uiStore.sortBy = sortField as any
  uiStore.sortOrder = sortDir as any

  // Apply type filter via search store if set
  if (quickTypeFilter.value) {
    // Filter in the computed result
  }
}

// P21-T4: Extend filteredMemories to include quick type filter
const filteredMemories = computed(() => {
  let result = sortedMemories.value

  // Apply quick type filter
  if (quickTypeFilter.value) {
    result = result.filter(m => m.type === quickTypeFilter.value)
  }

  // Apply collection filter
  const collection = activeCollection.value
  if (collection) {
    result = applyCollectionFilter(result, collection)
  }

  // F-15: Respect showArchived toggle
  if (!uiStore.showArchived) {
    result = result.filter(m => !m.archived)
  }

  return result
})

// P18-2: Handle compare event from MemoryCard
function onCompare(memory: AgentMemory) {
  if (!compareMemoryA.value) {
    // First memory selected
    compareMemoryA.value = memory
    toast.info('已选择第一个记忆，再点击另一记忆的"对比"按钮进行对比')
  } else if (compareMemoryA.value.id === memory.id) {
    // Same memory clicked again - deselect
    compareMemoryA.value = null
    toast.info('已取消选择')
  } else {
    // Second memory selected
    compareMemoryB.value = memory
    showDiffModal.value = true
  }
}

function closeDiffModal() {
  showDiffModal.value = false
  compareMemoryA.value = null
  compareMemoryB.value = null
}

// F48: Smart Collections
const activeCollection = computed(() => {
  const q = route.query.collection
  return typeof q === 'string' ? q : null
})

const activeCollectionInfo = computed(() => {
  if (!activeCollection.value) return null
  return store.collections.find(c => c.id === activeCollection.value) || null
})

function applyCollectionFilter(memories: AgentMemory[], collectionId: string): AgentMemory[] {
  const now = new Date()
  switch (collectionId) {
    case 'recent_7d': {
      const cutoff = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      return memories
        .filter(m => new Date(m.updatedAt) >= cutoff)
        .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    }
    case 'high_strength':
      return memories.filter(m => m.strength >= 8)
    case 'low_health':
      return memories.filter(m => (m.health_score ?? 100) < 40)
    case 'untagged':
      return memories.filter(m => !m.tags || m.tags.length === 0)
    case 'stale': {
      const cutoff = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
      return memories.filter(m => new Date(m.updatedAt) < cutoff)
    }
    case 'archived':
      return memories.filter(m => m.archived === true)
    default:
      return memories
  }
}

function clearCollection() {
  router.push({ query: { ...route.query, collection: undefined } })
}

const sortedMemories = computed(() => {
  const memories = [...store.memories]
  const field = uiStore.sortBy
  const order = uiStore.sortOrder === 'desc' ? -1 : 1
  memories.sort((a, b) => {
    if (field === 'strength') return (a.strength - b.strength) * order
    if (field === 'type') return a.type.localeCompare(b.type) * order
    return ((a[field] || '') as string).localeCompare((b[field] || '') as string) * order
  })
  return memories
})

// F48: Filtered memories — apply collection filter if active, then archived filter

function refresh() {
  store.refresh()
}

async function handleBatch(action: string, params?: Record<string, any>) {
  if (action === 'delete') {
    showDeleteConfirm.value = true
    pendingBatchAction.value = 'delete'
    return
  }
  await executeBatch(action, params)
}

async function confirmDelete() {
  showDeleteConfirm.value = false
  await executeBatch('delete')
}

async function executeBatch(action: string, params?: Record<string, any>) {
  batchLoading.value = true
  try {
    const ids = Array.from(store.selectedIds)
    await batchAction(action, ids, params)
    toast.success(`批量${action === 'delete' ? '删除' : action === 'archive' ? '归档' : action === 'add_tags' ? '添加标签' : '取消归档'}成功`)
    store.clearSelection()
    await store.refresh()
    if (action === 'add_tags') {
      store.loadAllTags()
    }
  } catch (e: any) {
    toast.error(`批量操作失败: ${e.message}`)
  } finally {
    batchLoading.value = false
  }
}

function handleBatchExport() {
  const ids = Array.from(store.selectedIds).join(',')
  const url = exportAgentMemory('json', ids)
  const a = document.createElement('a')
  a.href = url
  a.download = ''
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  store.clearSelection()
  toast.success('导出已开始')
}

// F-34: Bulk Auto-Tag via AI
async function handleBulkAutoTag() {
  autoTagLoading.value = true
  try {
    // If memories are selected, tag only those; otherwise tag all
    const ids = store.hasSelection ? Array.from(store.selectedIds) : undefined
    const resp = await bulkAutoTag(ids)
    if (resp.success) {
      toast.success(`✨ 已为 ${resp.processed} 条记忆自动生成标签`)
      await store.refresh()
      store.loadAllTags()
    } else {
      toast.error('批量自动标注失败')
    }
  } catch (e: any) {
    toast.error('批量自动标注失败: ' + (e.message || ''))
  } finally {
    autoTagLoading.value = false
  }
}

// F-21: Find duplicates
async function handleFindDuplicates() {
  dedupLoading.value = true
  try {
    const resp = await getDuplicates(0.7)
    duplicatePairs.value = resp.pairs
    selectedPairs.value = new Set(resp.pairs.map((_: any, i: number) => i))
    showDedupModal.value = true
    if (resp.pairs.length === 0) {
      toast.info('未发现重复记忆')
    }
  } catch (e: any) {
    toast.error('查找重复失败: ' + (e.message || ''))
  } finally {
    dedupLoading.value = false
  }
}

// F-21: Merge selected duplicate pairs
async function handleMergeDuplicates(pairIndices: number[]) {
  let merged = 0
  for (const idx of pairIndices) {
    const pair = duplicatePairs.value[idx]
    if (!pair) continue
    try {
      await mergeMemories(pair.memory_a.id, pair.memory_b.id)
      merged++
    } catch (e: any) {
      toast.error(`合并失败: ${pair.memory_a.title} - ${e.message}`)
    }
  }
  if (merged > 0) {
    toast.success(`已合并 ${merged} 对重复记忆`)
    showDedupModal.value = false
    await refresh()
  }
}

// F46: Handle tag click from MemoryCard — navigate to filtered view
function onTagClick(tag: string) {
  router.push({ query: { tag } })
}

// Load all tags on mount
store.loadAllTags()
</script>

<style scoped>
.agentmemory-view {
  padding-bottom: 40px;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.view-actions {
  display: flex;
  gap: 8px;
}

h2 {
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: -0.02em;
}

/* P38 r20: section-title 左侧 3px accent bar — 与 HomeView / AppSidebar / HermesMemoryView 同源 (r15 模式).
   全站 section title 现在共享同一视觉锚点语言 (3px rail + 12px padding-left). */
.section-title {
  position: relative;
  padding-left: 12px;
}

.section-title::before {
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

.action-btn {
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--primary);
  font-size: 0.8rem;
  font-family: var(--font);
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.action-btn:hover {
  background: var(--tag-bg);
  box-shadow: var(--shadow);
  transform: translateY(-1px);
}

/* P38 (round 3): primary 药丸 — 与 HomeView .action-btn--primary (P39) / CollectionsView (P41) 对齐
   几何上：实色填充（黑底白字，dark mode 下自动反转）+ 与 secondary 同 8px 圆角（保持一致性，不引入 pill）。
   视觉权重：比 secondary 高一档（实色 vs 描边），确保「+ 创建」是页面最强的视觉锚点。
   用 var(--primary-muted) 作为 hover 而非 color-mix — 与 HomeView 保持完全同款 hover 行为。 */
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
  transform: translateY(-1px);
}

.action-btn--primary:active {
  transform: translateY(0) scale(0.98);
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.skeleton-card {
  height: 140px;
  background: linear-gradient(90deg, var(--tag-bg) 25%, var(--border) 50%, var(--tag-bg) 75%);
  background-size: 200% 100%;
  border-radius: var(--radius);
  animation: shimmer 1.5s infinite;
  border: 1px solid var(--border);
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* F48: Collection filter bar */
.collection-filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  margin-bottom: 16px;
  background: var(--tag-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 0.85rem;
}

.filter-icon {
  font-size: 1.1rem;
}

.filter-label {
  flex: 1;
  font-weight: 600;
  color: var(--primary);
}

.filter-clear {
  background: none;
  border: 1px solid var(--border);
  border-radius: 50%;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.7rem;
  color: var(--text-secondary);
  transition: background 0.2s, color 0.2s;
}

.filter-clear:hover {
  background: var(--accent);
  color: var(--card);
  border-color: var(--accent);
}

/* Responsive */
@media (max-width: 767px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .view-actions {
    flex-wrap: wrap;
  }

  .card-grid {
    grid-template-columns: 1fr;
  }
}
</style>
