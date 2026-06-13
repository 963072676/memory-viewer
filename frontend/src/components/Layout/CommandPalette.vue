<template>
  <Teleport to="body">
    <transition name="palette-fade">
      <div v-if="modelValue" class="palette-backdrop" @mousedown.self="close">
        <div class="palette-panel">
          <!-- Search input -->
          <div class="palette-input-wrapper">
            <span class="palette-icon">⌘</span>
            <input
              ref="inputRef"
              v-model="query"
              class="palette-input"
              :placeholder="`${$t('i18n.search_memories')}...`"
              autofocus
              @keydown.down.prevent="moveDown"
              @keydown.up.prevent="moveUp"
              @keydown.enter.prevent="executeSelected"
              @keydown.escape.prevent="close"
            />
            <kbd class="palette-kbd">{{ $t('en_esc') }}</kbd>
          </div>

          <!-- Results list -->
          <div v-if="displayItems.length > 0" class="palette-results">
            <div class="palette-results-header">
              <span v-if="mode === 'command'">{{ $t('i18n.command') }}</span>
              <span v-else>
                {{ $t('i18n.search.results') }}
                <template v-if="totalResults > 0">（{{ totalResults }}）</template>
              </span>
            </div>
            <ul class="palette-list" role="listbox">
              <li
                v-for="(item, index) in displayItems"
                :key="item.id"
                class="palette-item"
                :class="{ 'palette-item--selected': index === selectedIndex }"
                role="option"
                :aria-selected="index === selectedIndex"
                @mouseenter="selectedIndex = index"
                @mousedown.prevent="executeItem(item)"
              >
                <span class="palette-item-icon">{{ item.icon }}</span>
                <div class="palette-item-content">
                  <span
                    class="palette-item-title"
                    v-html="highlightMatch(item.title, queryForHighlight)"
                  />
                  <span v-if="item.snippet" class="palette-item-snippet">
                    {{ item.snippet }}
                  </span>
                </div>
                <div class="palette-item-meta">
                  <span
                    v-if="item.badge"
                    class="palette-item-badge"
                    :class="'type-' + item.badge"
                  >
                    {{ item.badge }}
                  </span>
                  <span v-if="item.shortcut" class="palette-item-shortcut">
                    {{ item.shortcut }}
                  </span>
                </div>
              </li>
            </ul>
          </div>

          <!-- Empty state -->
          <div v-else-if="query.length > 0 && !searching" class="palette-empty">
            无匹配结果
          </div>

          <!-- Hints -->
          <div class="palette-footer">
            <span class="palette-hint">
              <kbd>↑</kbd><kbd>↓</kbd> 导航
              <kbd>↵</kbd> 执行
              <kbd>Esc</kbd> 关闭
            </span>
            <span class="palette-hint">
              输入 <kbd>&gt;</kbd> 进入命令模式
            </span>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { quickSearch } from '@/api/search'
import { useAgentMemoryStore } from '@/stores/agentmemory'
import { useTheme } from '@/composables/useTheme'
import { debounce } from '@/utils/debounce'
import type { QuickSearchResult } from '@/types'

// ─── Props & Emits ───

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  command: [name: string]
}>()

// ─── Refs & State ───

const router = useRouter()
const { t } = useI18n()
const agentMemoryStore = useAgentMemoryStore()
const { toggleTheme } = useTheme()

const inputRef = ref<HTMLInputElement | null>(null)
const query = ref('')
const selectedIndex = ref(0)
const searching = ref(false)
const searchResults = ref<QuickSearchResult[]>([])
const totalResults = ref(0)

// ─── Built-in Commands ───

interface CommandItem {
  id: string
  titleKey: string
  title?: string
  icon: string
  shortcut?: string
  action: () => void
  keywords: string[]
}

const commands: CommandItem[] = [
  {
    id: 'cmd-dashboard',
    titleKey: 'en_cmd_dashboard',
    icon: '📊',
    shortcut: '',
    keywords: ['dashboard', '仪表盘', '统计', '概览', 'stats', 'overview'],
    action: () => router.push('/dashboard'),
  },
  {
    id: 'cmd-graph',
    titleKey: 'en_cmd_graph',
    icon: '🕸️',
    keywords: ['graph', '关系图', '图谱', '网络', 'network'],
    action: () => router.push('/graph'),
  },
  {
    id: 'cmd-timeline',
    titleKey: 'en_cmd_timeline',
    icon: '📅',
    keywords: ['timeline', '时间线', '历史', 'history'],
    action: () => router.push('/timeline'),
  },
  {
    id: 'cmd-create',
    titleKey: 'en_cmd_create',
    icon: '✏️',
    keywords: ['create', '创建', '新建', '添加', '新增', 'new', 'add'],
    action: () => emit('command', 'create'),
  },
  {
    id: 'cmd-refresh',
    titleKey: 'en_cmd_refresh',
    icon: '🔄',
    keywords: ['refresh', '刷新', 'reload', '重新加载'],
    action: () => emit('command', 'refresh'),
  },
  {
    id: 'cmd-export',
    titleKey: 'en_cmd_export',
    icon: '📦',
    keywords: ['export', '导出', '下载', 'download', 'backup'],
    action: () => emit('command', 'export'),
  },
  {
    id: 'cmd-dark-mode',
    titleKey: 'en_cmd_dark_mode',
    icon: '🌙',
    keywords: ['dark', '深色', '暗色', '主题', 'theme', 'settings', '设置', 'mode'],
    action: () => toggleTheme(),
  },
  {
    id: 'cmd-home',
    titleKey: 'en_cmd_home',
    icon: '🏠',
    keywords: ['home', '首页', '主页'],
    action: () => router.push('/'),
  },
  {
    id: 'cmd-diag',
    titleKey: 'en_cmd_diag',
    icon: '🩺',
    keywords: ['diagnostics', '诊断', '检查', 'diagnostic'],
    action: () => router.push('/diagnostics'),
  },
  {
    id: 'cmd-backup',
    titleKey: 'en_cmd_backup',
    icon: '💾',
    keywords: ['backup', '备份', '恢复', 'restore'],
    action: () => router.push('/backup'),
  },
  {
    id: 'cmd-plugins',
    titleKey: 'en_cmd_plugins',
    icon: '🧩',
    keywords: ['plugins', '插件', '扩展', 'plugin', 'extension'],
    action: () => router.push('/plugins'),
  },
  {
    id: 'cmd-subscriptions',
    titleKey: 'en_cmd_subscriptions',
    icon: '🔔',
    keywords: ['subscriptions', '订阅', 'webhook', '通知', 'subscribe'],
    action: () => router.push('/subscriptions'),
  },
  {
    id: 'cmd-metrics',
    titleKey: 'en_cmd_metrics',
    icon: '📈',
    keywords: ['metrics', '性能', '指标', '监控', 'performance', 'monitor'],
    action: () => router.push('/metrics'),
  },
  {
    id: 'cmd-audit',
    titleKey: 'en_cmd_audit',
    icon: '📋',
    keywords: ['audit', '审计', '日志', 'log', 'logs'],
    action: () => router.push('/audit'),
  },
  {
    id: 'cmd-bulk-autotag',
    titleKey: 'en_cmd_bulk_autotag',
    icon: '✨',
    keywords: ['autotag', '自动标注', '标签', 'ai', 'tag', 'bulk'],
    action: () => emit('command', 'bulk-autotag'),
  },
]

// ─── Mode Detection ───

const mode = computed<'command' | 'search'>(() => {
  return query.value.startsWith('>') ? 'command' : 'search'
})

const queryForHighlight = computed(() => {
  if (mode.value === 'command') {
    return query.value.slice(1).trim()
  }
  return query.value.trim()
})

// ─── Command Filtering ───

const filteredCommands = computed(() => {
  const q = queryForHighlight.value.toLowerCase()
  if (!q) return commands
  return commands.filter((cmd) => {
    const haystack = [t(cmd.titleKey), ...cmd.keywords].join(' ').toLowerCase()
    return fuzzyMatch(q, haystack)
  })
})

// ─── Fuzzy Match Helper ───
function fuzzyMatch(query: string, text: string): boolean {
  // Exact substring match
  if (text.includes(query)) return true
  // Fuzzy: all query chars appear in order in text
  let qi = 0
  for (let ti = 0; ti < text.length && qi < query.length; ti++) {
    if (text[ti] === query[qi]) qi++
  }
  return qi === query.length
}

// ─── Display Items ───

interface DisplayItem {
  id: string
  title: string
  icon: string
  snippet?: string
  badge?: string
  shortcut?: string
}

const displayItems = computed<DisplayItem[]>(() => {
  if (mode.value === 'command') {
    return filteredCommands.value.map((cmd) => ({
      id: cmd.id,
      title: t(cmd.titleKey),
      icon: cmd.icon,
      shortcut: cmd.shortcut,
    }))
  }
  return searchResults.value.map((r) => ({
    id: r.id,
    title: r.title,
    icon: typeIcon(r.type),
    snippet: r.snippet,
    badge: r.type,
  }))
})

// ─── Debounced Search ───

const debouncedSearch = debounce(async (q: string) => {
  if (!q) {
    searchResults.value = []
    totalResults.value = 0
    return
  }
  searching.value = true
  try {
    const resp = await quickSearch(q, 10)
    searchResults.value = resp.results
    totalResults.value = resp.total
  } catch {
    searchResults.value = []
    totalResults.value = 0
  } finally {
    searching.value = false
  }
}, 200)

// ─── Watch query changes ───

watch(query, () => {
  selectedIndex.value = 0
  if (mode.value === 'search') {
    debouncedSearch(query.value.trim())
  }
})

// ─── Focus input on open ───

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      query.value = ''
      selectedIndex.value = 0
      searchResults.value = []
      totalResults.value = 0
      nextTick(() => {
        inputRef.value?.focus()
      })
    }
  }
)

// ─── Keyboard Navigation ───

function moveDown() {
  const len = displayItems.value.length
  if (len === 0) return
  selectedIndex.value = (selectedIndex.value + 1) % len
}

function moveUp() {
  const len = displayItems.value.length
  if (len === 0) return
  selectedIndex.value = (selectedIndex.value - 1 + len) % len
}

function executeSelected() {
  const item = displayItems.value[selectedIndex.value]
  if (item) {
    executeItem(item)
  }
}

function executeItem(item: DisplayItem) {
  if (mode.value === 'command') {
    const cmd = commands.find((c) => c.id === item.id)
    if (cmd) {
      close()
      cmd.action()
    }
  } else {
    // Navigate to memory detail
    close()
    router.push({ name: 'agentmemory', query: { highlight: item.id } })
  }
}

function close() {
  emit('update:modelValue', false)
}

// ─── Helpers ───

function typeIcon(type: string): string {
  const map: Record<string, string> = {
    pattern: '🧩',
    fact: '📌',
    preference: '⚙️',
    bug: '🐛',
    workflow: '📋',
    architecture: '🏗️',
  }
  return map[type] || '📝'
}

function highlightMatch(text: string, q: string): string {
  if (!q || !text) return escapeHtml(text)
  const escaped = q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(`(${escaped})`, 'gi')
  return escapeHtml(text).replace(regex, '<mark>$1</mark>')
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

// ─── Global Ctrl+K Listener (fallback) ───

function handleGlobalKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    emit('update:modelValue', !props.modelValue)
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<style scoped>
/* ─── Backdrop ─── */
/* P42: CommandPalette Geist 化 — 硬编码颜色全部走 token；圆角/阴影/font-mono 统一 */
.palette-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: var(--modal-backdrop);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 15vh;
  backdrop-filter: blur(2px);
}

/* ─── Panel ─── */
.palette-panel {
  width: 100%;
  max-width: 640px;
  background: var(--card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-elevated);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 70vh;
}

/* ─── Input ─── */
.palette-input-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-1) 20px;
  border-bottom: 1px solid var(--border);
}

.palette-icon {
  font-size: 1.2rem;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.palette-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 1.1rem;
  padding: 14px 0;
  color: var(--primary);
  font-family: var(--font);
}

.palette-input::placeholder {
  color: var(--text-secondary);
}

.palette-kbd {
  display: inline-flex;
  align-items: center;
  padding: 1px 5px;
  font-size: 0.7rem;
  /* P42: 与 TabBar.tab-key 对齐（Geist mono 字体 + 统一圆角 3px） */
  font-family: var(--font-mono);
  background: var(--tag-bg);
  color: var(--text-secondary);
  border-radius: 3px;
  border: 1px solid var(--border);
  flex-shrink: 0;
}

/* ─── Results ─── */
.palette-results {
  overflow-y: auto;
  max-height: 400px;
}

.palette-results-header {
  padding: var(--space-2) 20px var(--space-1);
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

.palette-list {
  list-style: none;
  padding: var(--space-1) var(--space-2);
  margin: 0;
}

/* ─── Item ─── */
.palette-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 10px var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background 0.1s;
}

.palette-item--selected {
  background: var(--tag-bg);
}

.palette-item-icon {
  font-size: 1.2rem;
  width: 28px;
  text-align: center;
  flex-shrink: 0;
}

.palette-item-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.palette-item-title {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.palette-item-title :deep(mark) {
  background: var(--highlight-bg);
  padding: 0 2px;
  border-radius: 2px;
  color: inherit;
}

.palette-item-snippet {
  font-size: 0.8rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.palette-item-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-shrink: 0;
}

.palette-item-badge {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 4px;
  background: var(--tag-bg);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  font-weight: 600;
}

.palette-item-shortcut {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

/* ─── Type badge colors ─── */
/* P42: Geist 化 — 14 处硬编码 hex（Material Design 配色）替换为项目自身的 type token。
   之前 light/dark 用了 Google Material 配色（#e8f0fe / #1a73e8 等），与 Geist 风格不一致；
   而且 dark 模式下 preference 与 architecture 撞色（都是 #1b3a1b / #81c995），用户无法区分。 */
.type-pattern {
  background: var(--type-pattern-bg);
  color: var(--type-pattern-text);
}
.type-fact {
  background: var(--type-fact-bg);
  color: var(--type-fact-text);
}
.type-preference {
  background: var(--type-preference-bg);
  color: var(--type-preference-text);
}
.type-bug {
  background: var(--type-bug-bg);
  color: var(--type-bug-text);
}
.type-workflow {
  background: var(--type-workflow-bg);
  color: var(--type-workflow-text);
}
.type-architecture {
  background: var(--type-architecture-bg);
  color: var(--type-architecture-text);
}

/* Dark 模式由 [data-theme='dark'] 在 :root 重新定义 --type-*-* 接管，无需此处重复 */

/* ─── Empty ─── */
.palette-empty {
  padding: var(--space-7) 20px;
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* ─── Footer ─── */
.palette-footer {
  display: flex;
  justify-content: space-between;
  padding: var(--space-2) 20px;
  border-top: 1px solid var(--border);
  font-size: 0.72rem;
  color: var(--text-secondary);
  gap: var(--space-3);
  flex-wrap: wrap;
}

.palette-hint {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.palette-hint kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  font-size: 0.65rem;
  /* P42: footer 的 kbd 也用 --font-mono（原 inherit 会回退到系统字体，与 Geist mono 体系脱节） */
  font-family: var(--font-mono);
  background: var(--tag-bg);
  color: var(--text-secondary);
  border-radius: 3px;
  border: 1px solid var(--border);
}

/* ─── Transition ─── */
.palette-fade-enter-active,
.palette-fade-leave-active {
  transition: opacity 0.15s ease;
}

.palette-fade-enter-active .palette-panel,
.palette-fade-leave-active .palette-panel {
  transition: transform 0.15s ease, opacity 0.15s ease;
}

.palette-fade-enter-from,
.palette-fade-leave-to {
  opacity: 0;
}

.palette-fade-enter-from .palette-panel,
.palette-fade-leave-to .palette-panel {
  transform: translateY(-12px) scale(0.98);
  opacity: 0;
}

/* ─── Mobile ─── */
@media (max-width: 767px) {
  .palette-backdrop {
    padding-top: 8vh;
    padding-left: var(--space-3);
    padding-right: var(--space-3);
  }

  .palette-panel {
    max-width: 100%;
    max-height: 80vh;
  }

  .palette-footer {
    flex-direction: column;
    gap: var(--space-1);
  }
}
</style>
