<template>
  <div class="search-bar">
    <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="11" cy="11" r="8"/>
      <path d="M21 21l-4.35-4.35"/>
    </svg>
    <input
      type="text"
      data-search-input
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
      :title="searchMode === 'semantic' ? '切换到关键词搜索' : '切换到语义搜索'"
    >
      <span class="mode-toggle__label">
        {{ searchMode === 'semantic' ? '🧠 Semantic' : '🔤 Keyword' }}
      </span>
    </button>
    <button v-if="uiStore.searchQuery" class="clear-btn" @click="clear">✕</button>
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
  margin: 0 auto 40px;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  width: 18px;
  height: 18px;
  z-index: 1;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 12px 110px 12px 44px;
  font-size: 1rem;
  font-family: var(--font);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
  color: var(--primary);
  outline: none;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.search-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.12), 0 2px 8px rgba(0, 0, 0, 0.06);
  background: var(--input-focus);
}

.search-input--semantic:focus {
  border-color: var(--semantic-accent, #8b5cf6);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
}

.search-input::placeholder {
  color: var(--text-secondary);
}

/* Mode toggle button */
.mode-toggle {
  position: absolute;
  right: 40px;
  top: 50%;
  transform: translateY(-50%);
  background: var(--tag-bg, #f0f0f0);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 3px 8px;
  cursor: pointer;
  font-size: 0.7rem;
  line-height: 1.4;
  color: var(--text-secondary);
  transition: all 0.2s ease;
  z-index: 2;
  white-space: nowrap;
}

.mode-toggle:hover {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}

.mode-toggle--semantic {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.3);
  color: var(--semantic-accent, #8b5cf6);
}

.mode-toggle--semantic:hover {
  background: var(--semantic-accent, #8b5cf6);
  color: #fff;
  border-color: var(--semantic-accent, #8b5cf6);
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
  right: 110px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.875rem;
  padding: 4px;
  z-index: 2;
}

/* Responsive */
@media (max-width: 767px) {
  .search-bar {
    margin: 0 auto 24px;
  }

  .mode-toggle {
    right: 8px;
    padding: 3px 6px;
    font-size: 0.65rem;
  }

  .clear-btn {
    right: 80px;
    font-size: 0.75rem;
  }

  .shortcut-hints {
    display: none;
  }

  .search-input {
    padding: 10px 90px 10px 40px;
  }
}

.clear-btn:hover {
  color: var(--primary);
}

.shortcut-hints {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  gap: 6px;
}

.hint-search,
.hint-palette {
  font-size: 0.7rem;
  padding: 2px 6px;
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--text-secondary);
  background: var(--tag-bg);
  font-family: monospace;
}

.hint-palette {
  color: var(--accent);
  border-color: var(--accent);
  background: rgba(0, 122, 255, 0.08);
}

/* Dark mode: semantic accent adapts automatically via CSS variables */
@media (prefers-color-scheme: dark) {
  .mode-toggle--semantic {
    background: rgba(139, 92, 246, 0.15);
    border-color: rgba(139, 92, 246, 0.4);
  }
}
</style>
