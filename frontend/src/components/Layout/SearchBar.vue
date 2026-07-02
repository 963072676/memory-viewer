<template>
  <div class="search-bar">
    <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="11" cy="11" r="8"/>
      <path d="M21 21l-4.35-4.35"/>
    </svg>
    <input
      type="text"
      data-search-input
      aria-label="搜索记忆"
      :value="uiStore.searchQuery"
      @input="onInput"
      :placeholder="searchMode === 'semantic' ? '🧠 语义搜索记忆...' : '搜索记忆... (按 / 聚焦)'"
      class="search-input"
      :class="{ 'search-input--semantic': searchMode === 'semantic' }"
    />
    <button
      class="mode-toggle"
      :class="{ 'mode-toggle--semantic': searchMode === 'semantic' }"
      @click="toggleMode"
      :aria-label="searchMode === 'semantic' ? '切换到关键词搜索' : '切换到语义搜索'"
      :title="searchMode === 'semantic' ? '切换到关键词搜索' : '切换到语义搜索'"
    >
      <span class="mode-toggle__label">
        {{ searchMode === 'semantic' ? '🧠 Semantic' : '🔤 Keyword' }}
      </span>
    </button>
    <button v-if="uiStore.searchQuery" class="clear-btn" @click="clear" :aria-label="$t('i18n.clear_search')">✕</button>
    <div class="shortcut-hints">
      <kbd v-if="!uiStore.searchQuery" class="hint-search">/</kbd>
      <kbd class="hint-palette">⌘K</kbd>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useUIStore } from '@/stores/ui'
import { useSearchStore, type SearchMode } from '@/stores/search'
import { debounce } from '@/utils/debounce'

const uiStore = useUIStore()
const searchStore = useSearchStore()

const searchMode = computed(() => searchStore.searchMode)

const debouncedKeywordSearch = debounce((q: string) => {
  uiStore.setSearch(q)
  if (q.trim()) {
    searchStore.search(q)
  } else {
    searchStore.clear()
  }
}, 300)

const debouncedSemanticSearch = debounce((q: string) => {
  uiStore.setSearch(q)
  if (q.trim()) {
    searchStore.doSemanticSearch(q)
  } else {
    searchStore.clear()
  }
}, 400)

function onInput(e: Event) {
  const val = (e.target as HTMLInputElement).value
  if (searchMode.value === 'semantic') {
    debouncedSemanticSearch(val)
  } else {
    debouncedKeywordSearch(val)
  }
}

function toggleMode() {
  const newMode: SearchMode = searchMode.value === 'keyword' ? 'semantic' : 'keyword'
  searchStore.setSearchMode(newMode)
  // Re-trigger search in the new mode if there's an active query
  const q = uiStore.searchQuery
  if (q && q.trim()) {
    if (newMode === 'semantic') {
      searchStore.doSemanticSearch(q)
    } else {
      searchStore.search(q)
    }
  }
}

function clear() {
  uiStore.setSearch('')
  searchStore.clear()
}
</script>

<style scoped>
.search-bar {
  max-width: 560px;
  margin: 0 auto 16px;
  position: relative;
}

/* P38: Geist 化 — recessed 输入背景，更克制的边框，hover 微亮 */
.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  width: 18px;
  height: 18px;
  z-index: 1;
  pointer-events: none;
  transition: color 0.2s ease;
}

.search-input {
  width: 100%;
  padding: 11px 168px 11px 42px;
  font-size: 0.95rem;
  font-family: var(--font);
  border: 1px solid transparent;
  border-radius: var(--radius);
  background: var(--bg-recessed);
  color: var(--primary);
  outline: none;
  transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.search-input:hover {
  background: var(--tag-bg);
  border-color: var(--border);
}

.search-input:focus {
  background: var(--input-focus);
  border-color: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-glow);
}

.search-input:focus ~ .search-icon,
.search-bar:focus-within .search-icon {
  color: var(--accent);
}

.search-input--semantic:focus {
  border-color: var(--semantic-accent);
  box-shadow: 0 0 0 4px var(--semantic-accent-glow);
}

.search-input--semantic:focus ~ .search-icon,
.search-bar:focus-within .search-input--semantic ~ .search-icon {
  color: var(--semantic-accent);
}

.search-input::placeholder {
  color: var(--text-secondary);
}

/* Mode toggle button — Geist pill */
.mode-toggle {
  position: absolute;
  right: 56px;
  top: 50%;
  transform: translateY(-50%);
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 0.72rem;
  line-height: 1.4;
  color: var(--text-secondary);
  transition: all 0.15s ease;
  z-index: 2;
  white-space: nowrap;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.mode-toggle:hover {
  background: var(--tag-bg);
  border-color: var(--border-strong);
  color: var(--primary);
}

.mode-toggle--semantic {
  background: var(--semantic-accent-subtle);
  border-color: var(--semantic-accent);
  color: var(--semantic-accent);
}

.mode-toggle--semantic:hover {
  background: var(--semantic-accent);
  border-color: var(--semantic-accent);
  color: var(--card);
}

.mode-toggle__label {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-family: var(--font);
  font-weight: 500;
}

.clear-btn {
  position: absolute;
  right: 148px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.875rem;
  padding: 4px;
  z-index: 2;
  border-radius: 4px;
  transition: color 0.15s ease, background 0.15s ease;
}

.clear-btn:hover {
  color: var(--primary);
  background: var(--tag-bg);
}

/* Responsive */
@media (max-width: 767px) {
  .search-bar {
    margin: 0 auto 12px;
  }

  .mode-toggle {
    right: 10px;
    padding: 3px 7px;
    font-size: 0.65rem;
  }

  .clear-btn {
    right: 96px;
    font-size: 0.75rem;
  }

  .shortcut-hints {
    display: none;
  }

  .search-input {
    padding: 10px 106px 10px 38px;
    font-size: 0.9rem;
  }

  .search-icon {
    left: 12px;
    width: 16px;
    height: 16px;
  }
}

.shortcut-hints {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  gap: 6px;
  pointer-events: none;
}

.hint-search,
.hint-palette {
  font-size: 0.68rem;
  padding: 2px 6px;
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--text-secondary);
  background: var(--card);
  font-family: var(--font-mono);
  font-weight: 500;
}

.hint-palette {
  color: var(--accent);
  border-color: var(--accent);
  background: var(--accent-subtle);
}
</style>
