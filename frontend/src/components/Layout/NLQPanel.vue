<template>
  <div class="nlq-panel">
    <!-- Search bar with mode toggle -->
    <div class="nlq-input-row">
      <div class="mode-switcher">
        <button
          v-for="m in modes"
          :key="m.value"
          class="mode-btn"
          :class="{ active: searchMode === m.value }"
          @click="searchMode = m.value"
          :title="m.label"
        >
          {{ m.icon }}
        </button>
      </div>
      <input
        ref="inputRef"
        v-model="query"
        type="text"
        class="nlq-input"
        :placeholder="currentPlaceholder"
        @keydown.enter="executeSearch"
      />
      <button class="nlq-submit" :disabled="!query.trim() || searching" @click="executeSearch">
        {{ searching ? '...' : '→' }}
      </button>
    </div>

    <!-- History dropdown -->
    <div v-if="showHistory && searchMode === 'nlq' && history.length > 0" class="nlq-history">
      <div class="history-header">
        <span>{{ $t('zh_b749ce') }}</span>
        <button class="history-clear" @click="clearHistory">{{ $t('zh_006813') }}</button>
      </div>
      <div
        v-for="(item, idx) in history"
        :key="idx"
        class="history-item"
        @click="applyHistory(item)"
      >
        <span class="history-icon">🕐</span>
        <span class="history-text">{{ item }}</span>
      </div>
    </div>

    <!-- NLQ parsed conditions display -->
    <div v-if="nlqResult && searchMode === 'nlq'" class="nlq-parsed">
      <div class="parsed-header">
        <span>🤖 AI {{ $t('zh_c9bfa0') }}</span>
        <button class="parsed-edit-btn" @click="editingParsed = !editingParsed">
          {{ editingParsed ? '完成' : '编辑' }}
        </button>
      </div>
      <div v-if="!editingParsed" class="parsed-conditions">
        <div v-for="(cond, key) in nlqResult.parsed_conditions" :key="key" class="parsed-chip">
          <span class="chip-key">{{ key }}</span>
          <span class="chip-value">{{ formatCondition(cond) }}</span>
        </div>
      </div>
      <div v-else class="parsed-editor">
        <textarea
          v-model="editedConditions"
          class="parsed-textarea"
          rows="4"
        />
        <button class="parsed-apply-btn" @click="applyEditedConditions">{{ $t('zh_ce0eec') }}</button>
      </div>
      <div v-if="nlqResult.interpretation" class="nlq-interpretation">
        💡 {{ nlqResult.interpretation }}
      </div>
    </div>

    <!-- Results panel -->
    <div v-if="searching" class="nlq-loading">
      <div class="loading-dots">
        <span></span><span></span><span></span>
      </div>
      <span>{{ searchMode === 'nlq' ? 'AI 正在理解你的问题...' : '搜索中...' }}</span>
    </div>

    <div v-else-if="error" class="nlq-error">
      ⚠️ {{ error }}
    </div>

    <div v-else-if="results.length > 0" class="nlq-results">
      <div class="results-header">
        <span>{{ $t('zh_00666e') }} {{ results.length }} {{ $t('zh_995fbf') }}</span>
        <span v-if="nlqResult?.query_time" class="results-time">
          {{ (nlqResult.query_time * 1000).toFixed(0) }}ms
        </span>
      </div>
      <div
        v-for="result in results"
        :key="result.id"
        class="result-item"
        @click="$emit('select-memory', result.id)"
      >
        <div class="result-title">
          {{ result.title }}
          <span class="result-type" :class="'type-' + result.type">{{ result.type }}</span>
          <span v-if="result.similarity" class="result-score">
            {{ (result.similarity * 100).toFixed(0) }}%
          </span>
        </div>
        <div class="result-snippet">{{ result.snippet }}</div>
        <div v-if="result.tags?.length" class="result-tags">
          <span v-for="tag in result.tags" :key="tag" class="result-tag">{{ tag }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'

// Types
interface NLQResult {
  id: string
  title: string
  type: string
  snippet: string
  tags: string[]
  similarity?: number
}

interface NLQResponse {
  query: string
  interpretation?: string
  parsed_conditions: Record<string, any>
  results: NLQResult[]
  total: number
  query_time?: number
}

interface SearchResult {
  id: string
  title: string
  type: string
  snippet: string
  tags: string[]
  similarity?: number
}

type SearchMode = 'keyword' | 'semantic' | 'nlq'

const emit = defineEmits<{
  (e: 'select-memory', id: string): void
}>()

const toast = useToast()

const inputRef = ref<HTMLInputElement | null>(null)
const query = ref('')
const searchMode = ref<SearchMode>('keyword')
const searching = ref(false)
const error = ref('')
const results = ref<NLQResult[]>([])
const nlqResult = ref<NLQResponse | null>(null)
const showHistory = ref(true)
const editingParsed = ref(false)
const editedConditions = ref('')

const modes = [
  { value: 'keyword' as const, icon: '🔤', label: '关键词搜索' },
  { value: 'semantic' as const, icon: '🧠', label: '语义搜索' },
  { value: 'nlq' as const, icon: '🤖', label: '自然语言查询' },
]

const currentPlaceholder = computed(() => {
  switch (searchMode.value) {
    case 'keyword': return '输入关键词搜索...'
    case 'semantic': return '🧠 输入语义描述搜索...'
    case 'nlq': return '🤖 用自然语言提问，例如 "上周创建的关于 API 的记忆"'
    default: return '搜索...'
  }
})

// Query history (NLQ mode only)
const HISTORY_KEY = 'mv2_nlq_history'
const history = ref<string[]>(loadHistory())

function loadHistory(): string[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY)
    return raw ? JSON.parse(raw).slice(0, 10) : []
  } catch {
    return []
  }
}

function saveHistory() {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history.value.slice(0, 10)))
}

function addToHistory(q: string) {
  history.value = [q, ...history.value.filter(h => h !== q)].slice(0, 10)
  saveHistory()
}

function clearHistory() {
  history.value = []
  saveHistory()
}

function applyHistory(item: string) {
  query.value = item
  showHistory.value = false
  executeSearch()
}

// Search execution
async function executeSearch() {
  const q = query.value.trim()
  if (!q) return

  searching.value = true
  error.value = ''
  results.value = []
  nlqResult.value = null
  editingParsed.value = false
  showHistory.value = false

  try {
    if (searchMode.value === 'nlq') {
      addToHistory(q)
      const res = await request<any>('/search/nlq', {
        method: 'POST',
        body: JSON.stringify({ question: q }),
      })
      nlqResult.value = {
        query: res.question || q,
        interpretation: res.explanation,
        parsed_conditions: res.parsed_conditions || {},
        results: Array.isArray(res.results?.results) ? res.results.results : (Array.isArray(res.results) ? res.results : []),
        total: res.results?.total || 0,
        query_time: res.parse_time_ms ? res.parse_time_ms / 1000 : undefined,
      }
      results.value = nlqResult.value.results
      editedConditions.value = JSON.stringify(res.parsed_conditions, null, 2)
    } else {
      // keyword or semantic search
      const mode = searchMode.value
      const res = await request<{ results: SearchResult[]; query?: string; mode?: string }>(
        `/search/${mode}?q=${encodeURIComponent(q)}`
      )
      results.value = res.results || []
    }
  } catch (e: any) {
    error.value = e.message || '搜索失败'
  } finally {
    searching.value = false
  }
}

// Edit parsed conditions and re-query
async function applyEditedConditions() {
  try {
    const conditions = JSON.parse(editedConditions.value)
    editingParsed.value = false
    searching.value = true
    error.value = ''

    const res = await request<any>('/search/nlq', {
      method: 'POST',
      body: JSON.stringify({
        question: query.value,
        override_conditions: conditions,
      }),
    })
    nlqResult.value = {
      query: res.question || query.value,
      interpretation: res.explanation,
      parsed_conditions: res.parsed_conditions || {},
      results: Array.isArray(res.results?.results) ? res.results.results : (Array.isArray(res.results) ? res.results : []),
      total: res.results?.total || 0,
      query_time: res.parse_time_ms ? res.parse_time_ms / 1000 : undefined,
    }
    results.value = nlqResult.value.results
  } catch (e: any) {
    error.value = '条件格式错误或查询失败: ' + (e.message || '')
  } finally {
    searching.value = false
  }
}

function formatCondition(cond: any): string {
  if (typeof cond === 'string') return cond
  if (Array.isArray(cond)) return cond.join(', ')
  if (typeof cond === 'object' && cond !== null) return JSON.stringify(cond)
  return String(cond)
}

// Focus on mode change
watch(searchMode, () => {
  results.value = []
  nlqResult.value = null
  error.value = ''
  showHistory.value = searchMode.value === 'nlq' && history.value.length > 0
})
</script>

<style scoped>
.nlq-panel {
  position: relative;
}

.nlq-input-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.mode-switcher {
  display: flex;
  background: var(--bg-secondary, #f9f9f9);
  border-radius: 10px;
  padding: 3px;
  flex-shrink: 0;
}

.mode-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.15s ease;
}

.mode-btn.active {
  background: var(--card, #fff);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.nlq-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 10px;
  font-size: 0.9rem;
  font-family: var(--font);
  color: var(--text, #1d1d1f);
  background: var(--card, #fff);
  transition: border-color 0.15s ease;
}

.nlq-input:focus {
  outline: none;
  border-color: var(--primary, #007aff);
}

.nlq-submit {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 10px;
  background: var(--primary, #007aff);
  color: #fff;
  font-size: 1.1rem;
  cursor: pointer;
  flex-shrink: 0;
  transition: opacity 0.15s ease;
}

.nlq-submit:hover {
  opacity: 0.9;
}

.nlq-submit:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* History */
.nlq-history {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 6px;
  background: var(--card, #fff);
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  z-index: 100;
  overflow: hidden;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary, #86868b);
  border-bottom: 1px solid var(--border, #e5e5ea);
}

.history-clear {
  border: none;
  background: none;
  color: var(--primary, #007aff);
  font-size: 0.7rem;
  cursor: pointer;
  font-family: var(--font);
}

.history-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--text, #1d1d1f);
  transition: background 0.1s ease;
}

.history-item:hover {
  background: var(--bg-secondary, #f9f9f9);
}

.history-icon {
  font-size: 0.75rem;
  flex-shrink: 0;
}

.history-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Parsed conditions */
.nlq-parsed {
  margin-top: 12px;
  padding: 12px;
  background: var(--bg-secondary, #f9f9f9);
  border-radius: 10px;
}

.parsed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text, #1d1d1f);
}

.parsed-edit-btn {
  border: none;
  background: none;
  color: var(--primary, #007aff);
  font-size: 0.75rem;
  cursor: pointer;
  font-family: var(--font);
}

.parsed-conditions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.parsed-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: var(--card, #fff);
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px;
  font-size: 0.75rem;
}

.chip-key {
  font-weight: 600;
  color: var(--primary, #007aff);
}

.chip-value {
  color: var(--text, #1d1d1f);
}

.parsed-editor {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.parsed-textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px;
  font-size: 0.8rem;
  font-family: var(--font-mono);
  resize: vertical;
  color: var(--text, #1d1d1f);
  background: var(--card, #fff);
  box-sizing: border-box;
}

.parsed-textarea:focus {
  outline: none;
  border-color: var(--primary, #007aff);
}

.parsed-apply-btn {
  align-self: flex-end;
  padding: 6px 14px;
  border: none;
  border-radius: 8px;
  background: var(--primary, #007aff);
  color: #fff;
  font-size: 0.8rem;
  cursor: pointer;
  font-family: var(--font);
}

.nlq-interpretation {
  margin-top: 8px;
  font-size: 0.8rem;
  color: var(--text-secondary, #86868b);
  font-style: italic;
}

/* Loading */
.nlq-loading {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
  padding: 30px;
  color: var(--text-secondary, #86868b);
  font-size: 0.85rem;
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary, #007aff);
  animation: dot-pulse 1.2s infinite ease-in-out;
}

.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes dot-pulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

/* Error */
.nlq-error {
  padding: 16px;
  text-align: center;
  color: var(--error, #ff3b30);
  font-size: 0.85rem;
}

/* Results */
.nlq-results {
  margin-top: 12px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 0.8rem;
  color: var(--text-secondary, #86868b);
}

.results-time {
  font-size: 0.7rem;
  padding: 2px 6px;
  background: var(--bg-secondary, #f9f9f9);
  border-radius: 4px;
}

.result-item {
  padding: 12px;
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 10px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

/* P38 (round 7): 2% accent 极轻蓝 + 蓝边 — 之前硬编码 Apple rgba(0,122,255,0.02) +
   var(--primary, #007aff) fallback（语义错配，见 ShareModal 注释）。 */
.result-item:hover {
  border-color: var(--accent);
  background: var(--accent-faint);
}

.result-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text, #1d1d1f);
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-type {
  font-size: 0.65rem;
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.result-score {
  font-size: 0.7rem;
  color: var(--primary, #007aff);
  font-weight: 600;
  margin-left: auto;
}

.result-snippet {
  font-size: 0.8rem;
  color: var(--text-secondary, #86868b);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.result-tags {
  display: flex;
  gap: 4px;
  margin-top: 6px;
  flex-wrap: wrap;
}

.result-tag {
  font-size: 0.65rem;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--tag-bg, #f2f2f7);
  color: var(--text-secondary, #86868b);
}

/* P38 (round 5): type-chip token 化 — 与 MemoryCard / CommandPalette / FilterPanel / MemoryDetailView 对齐。
   之前用 Material Design hex，且完全没有 dark 模式覆盖（dark 模式下 chip 仍用浅色背景 + 深色文字，对比度差）。
   修复后 dark 模式自动跟随 variables.css。 */
.type-pattern { background: var(--type-pattern-bg); color: var(--type-pattern-text); }
.type-fact { background: var(--type-fact-bg); color: var(--type-fact-text); }
.type-preference { background: var(--type-preference-bg); color: var(--type-preference-text); }
.type-bug { background: var(--type-bug-bg); color: var(--type-bug-text); }
.type-workflow { background: var(--type-workflow-bg); color: var(--type-workflow-text); }
.type-architecture { background: var(--type-architecture-bg); color: var(--type-architecture-text); }
</style>
