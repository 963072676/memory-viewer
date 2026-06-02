<template>
  <div class="filter-panel" :class="{ open: isOpen }">
    <button class="filter-toggle" @click="isOpen = !isOpen">
      <span>🔍</span>
      <span>高级筛选</span>
      <span class="toggle-arrow">{{ isOpen ? '▲' : '▼' }}</span>
      <span v-if="activeFilterCount > 0" class="filter-badge">{{ activeFilterCount }}</span>
    </button>
    <transition name="slide">
      <div v-if="isOpen" class="filter-content">
        <!-- Type Filter -->
        <div class="filter-section">
          <h4>记忆类型</h4>
          <div class="type-checkboxes">
            <label v-for="t in memoryTypes" :key="t.value" class="checkbox-label">
              <input type="checkbox" :value="t.value" v-model="selectedTypes" />
              <span class="type-chip" :class="'type-' + t.value">{{ t.label }}</span>
            </label>
          </div>
        </div>

        <!-- Strength Range -->
        <div class="filter-section">
          <h4>Strength 范围</h4>
          <div class="range-row">
            <div class="range-group">
              <label>最小</label>
              <input v-model.number="strengthMin" type="range" min="0" max="10" />
              <span class="range-val">{{ strengthMin }}</span>
            </div>
            <div class="range-group">
              <label>最大</label>
              <input v-model.number="strengthMax" type="range" min="0" max="10" />
              <span class="range-val">{{ strengthMax }}</span>
            </div>
          </div>
        </div>

        <!-- Date Range -->
        <div class="filter-section">
          <h4>时间范围</h4>
          <div class="date-row">
            <div class="date-group">
              <label>从</label>
              <input v-model="dateFrom" type="date" />
            </div>
            <div class="date-group">
              <label>至</label>
              <input v-model="dateTo" type="date" />
            </div>
          </div>
        </div>

        <!-- Source Toggle -->
        <div class="filter-section">
          <h4>数据源</h4>
          <div class="source-toggle">
            <button
              v-for="s in sources"
              :key="s.value"
              class="source-btn"
              :class="{ active: selectedSource === s.value }"
              @click="selectedSource = s.value"
            >
              {{ s.label }}
            </button>
          </div>
        </div>

        <!-- Show Archived Toggle (F-15) -->
        <div class="filter-section">
          <h4>归档记忆</h4>
          <label class="checkbox-label">
            <input type="checkbox" v-model="showArchived" />
            <span>显示已归档的记忆</span>
          </label>
        </div>

        <!-- F46: Tag Filter -->
        <div class="filter-section">
          <h4>标签过滤</h4>
          <div v-if="allTagsList.length === 0" class="no-tags">暂无标签</div>
          <div v-else class="tag-checkboxes">
            <label v-for="t in allTagsList" :key="t" class="checkbox-label">
              <input type="checkbox" :value="t" v-model="selectedTags" />
              <span class="tag-chip">{{ t }}</span>
            </label>
          </div>
        </div>

        <!-- Actions -->
        <div class="filter-actions">
          <button class="btn-reset" @click="resetFilters">重置</button>
          <button class="btn-apply" @click="applyFilters">应用筛选</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useSearchStore } from '@/stores/search'
import { useAgentMemoryStore } from '@/stores/agentmemory'
import { useUIStore } from '@/stores/ui'
import { useRoute, useRouter } from 'vue-router'

const searchStore = useSearchStore()
const agentMemoryStore = useAgentMemoryStore()
const uiStore = useUIStore()
const route = useRoute()
const router = useRouter()

const isOpen = ref(false)

const memoryTypes = [
  { value: 'pattern', label: 'Pattern' },
  { value: 'fact', label: 'Fact' },
  { value: 'preference', label: 'Preference' },
  { value: 'bug', label: 'Bug' },
  { value: 'workflow', label: 'Workflow' },
  { value: 'architecture', label: 'Architecture' },
]

const sources = [
  { value: 'all', label: '全部' },
  { value: 'agentmemory', label: 'AgentMemory' },
  { value: 'hermes', label: 'Hermes' },
]

const selectedTypes = ref<string[]>([])
const strengthMin = ref(0)
const strengthMax = ref(10)
const dateFrom = ref('')
const dateTo = ref('')
const selectedSource = ref('all')
const selectedTags = ref<string[]>([])

// F46: Load tags on mount
agentMemoryStore.loadAllTags()
const allTagsList = computed(() => agentMemoryStore.allTags.map(t => t.tag))

// Two-way binding for archived toggle via UI store
const showArchived = computed({
  get: () => uiStore.showArchived,
  set: (val: boolean) => { uiStore.showArchived = val },
})

const activeFilterCount = computed(() => {
  let count = 0
  if (selectedTypes.value.length > 0) count++
  if (strengthMin.value > 0 || strengthMax.value < 10) count++
  if (dateFrom.value || dateTo.value) count++
  if (selectedSource.value !== 'all') count++
  if (selectedTags.value.length > 0) count++
  return count
})

function applyFilters() {
  searchStore.setFilters({
    types: selectedTypes.value.length > 0 ? selectedTypes.value.join(',') : undefined,
    strengthMin: strengthMin.value > 0 ? strengthMin.value : undefined,
    strengthMax: strengthMax.value < 10 ? strengthMax.value : undefined,
    dateFrom: dateFrom.value || undefined,
    dateTo: dateTo.value || undefined,
    source: selectedSource.value !== 'all' ? selectedSource.value : undefined,
    tags: selectedTags.value.length > 0 ? selectedTags.value.join(',') : undefined,
  })

  // Sync to URL
  const query: Record<string, string> = {}
  if (selectedTypes.value.length > 0) query.types = selectedTypes.value.join(',')
  if (strengthMin.value > 0) query.strength_min = String(strengthMin.value)
  if (strengthMax.value < 10) query.strength_max = String(strengthMax.value)
  if (dateFrom.value) query.date_from = dateFrom.value
  if (dateTo.value) query.date_to = dateTo.value
  if (selectedSource.value !== 'all') query.source = selectedSource.value
  if (selectedTags.value.length > 0) query.tag = selectedTags.value.join(',')
  router.replace({ query })

  searchStore.search(searchStore.query || '', {
    types: selectedTypes.value.length > 0 ? selectedTypes.value.join(',') : undefined,
    strengthMin: strengthMin.value > 0 ? strengthMin.value : undefined,
    strengthMax: strengthMax.value < 10 ? strengthMax.value : undefined,
    dateFrom: dateFrom.value || undefined,
    dateTo: dateTo.value || undefined,
    source: selectedSource.value !== 'all' ? selectedSource.value : undefined,
    tags: selectedTags.value.length > 0 ? selectedTags.value.join(',') : undefined,
  })
}

function resetFilters() {
  selectedTypes.value = []
  strengthMin.value = 0
  strengthMax.value = 10
  dateFrom.value = ''
  dateTo.value = ''
  selectedSource.value = 'all'
  selectedTags.value = []
  searchStore.clearFilters()
  router.replace({ query: {} })
}

// Restore from URL on mount
function restoreFromUrl() {
  const q = route.query
  if (q.types) {
    selectedTypes.value = (q.types as string).split(',')
    isOpen.value = true
  }
  if (q.strength_min) {
    strengthMin.value = Number(q.strength_min)
    isOpen.value = true
  }
  if (q.strength_max) {
    strengthMax.value = Number(q.strength_max)
    isOpen.value = true
  }
  if (q.date_from) {
    dateFrom.value = q.date_from as string
    isOpen.value = true
  }
  if (q.date_to) {
    dateTo.value = q.date_to as string
    isOpen.value = true
  }
  if (q.source) {
    selectedSource.value = q.source as string
    isOpen.value = true
  }
  // F46: Restore tag filter from URL
  if (q.tag) {
    selectedTags.value = (q.tag as string).split(',')
    isOpen.value = true
  }
}

restoreFromUrl()
</script>

<style scoped>
.filter-panel {
  max-width: 560px;
  margin: -24px auto 24px;
}

.filter-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.8rem;
  font-family: var(--font);
  transition: background 0.2s;
  position: relative;
}

.filter-toggle:hover {
  background: var(--tag-bg);
}

.toggle-arrow {
  font-size: 0.7rem;
  margin-left: auto;
}

.filter-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: var(--accent);
  color: white;
  font-size: 0.65rem;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.filter-content {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  margin-top: 8px;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-section:last-of-type {
  margin-bottom: 0;
}

.filter-section h4 {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.type-checkboxes,
.tag-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.checkbox-label input[type='checkbox'] {
  width: 16px;
  height: 16px;
  accent-color: var(--accent);
}

.type-chip {
  font-size: 0.7rem;
  padding: 3px 10px;
  border-radius: 12px;
  background: var(--tag-bg);
  color: var(--text-secondary);
  text-transform: capitalize;
}

.tag-chip {
  font-size: 0.7rem;
  padding: 3px 10px;
  border-radius: 12px;
  background: var(--tag-bg);
  color: var(--accent);
}

.no-tags {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.type-pattern { background: #e8f5e9; color: #2e7d32; }
.type-fact { background: #e3f2fd; color: #1565c0; }
.type-preference { background: #fce4ec; color: #c62828; }
.type-bug { background: #fff3e0; color: #e65100; }
.type-workflow { background: #f3e5f5; color: #7b1fa2; }
.type-architecture { background: #e0f2f1; color: #00695c; }

[data-theme='dark'] .type-pattern { background: #1b3a1b; color: #66bb6a; }
[data-theme='dark'] .type-fact { background: #0d2744; color: #64b5f6; }
[data-theme='dark'] .type-preference { background: #3e1a1a; color: #ef9a9a; }
[data-theme='dark'] .type-bug { background: #3e2a0a; color: #ffcc80; }
[data-theme='dark'] .type-workflow { background: #2a1a3a; color: #ce93d8; }
[data-theme='dark'] .type-architecture { background: #0a2a2a; color: #80cbc4; }

.range-row {
  display: flex;
  gap: 16px;
}

.range-group {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-group label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  min-width: 28px;
}

.range-group input[type='range'] {
  flex: 1;
}

.range-val {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--accent);
  min-width: 20px;
  text-align: right;
}

.date-row {
  display: flex;
  gap: 16px;
}

.date-group {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-group label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.date-group input[type='date'] {
  flex: 1;
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--primary);
  font-size: 0.8rem;
  font-family: var(--font);
}

.source-toggle {
  display: flex;
  gap: 6px;
}

.source-btn {
  padding: 6px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.8rem;
  font-family: var(--font);
  transition: all 0.2s;
}

.source-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

.btn-reset {
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.8rem;
  font-family: var(--font);
}

.btn-apply {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: var(--accent);
  color: white;
  cursor: pointer;
  font-size: 0.8rem;
  font-family: var(--font);
  font-weight: 500;
}

/* Slide transition */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
  margin-top: 0;
  padding: 0;
}

.slide-enter-to,
.slide-leave-from {
  opacity: 1;
  max-height: 600px;
}

/* Responsive */
@media (max-width: 767px) {
  .filter-panel {
    max-width: 100%;
    margin: -16px 0 16px;
  }

  .filter-toggle {
    width: 100%;
    justify-content: center;
  }

  .range-row,
  .date-row {
    flex-direction: column;
    gap: 10px;
  }

  .source-toggle {
    flex-wrap: wrap;
  }

  .filter-actions {
    flex-direction: column;
  }

  .filter-actions button {
    width: 100%;
  }
}
</style>
