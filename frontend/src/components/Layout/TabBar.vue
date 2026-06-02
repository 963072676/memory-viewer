<template>
  <div class="search-bar">
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        class="tab-btn"
        :class="{ active: uiStore.currentTab === tab.value }"
        @click="uiStore.setTab(tab.value)"
      >
        {{ tab.label }}
        <kbd class="tab-key">{{ tab.key }}</kbd>
      </button>
    </div>
    <div class="expand-controls">
      <button class="expand-btn" @click="uiStore.toggleAllExpanded()">
        {{ uiStore.allExpanded ? '全部折叠' : '全部展开' }}
      </button>
      <button class="help-btn" @click="uiStore.toggleKeyboardHelp()" title="快捷键帮助 (?)">⌨️</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUIStore } from '@/stores/ui'

const uiStore = useUIStore()

const tabs = [
  { label: '全部', value: 'all' as const, key: '1' },
  { label: 'AgentMemory', value: 'agentmemory' as const, key: '2' },
  { label: 'Hermes Memory', value: 'hermes' as const, key: '3' },
]
</script>

<style scoped>
.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.tabs {
  display: flex;
  gap: 4px;
  background: var(--tag-bg);
  border-radius: 10px;
  padding: 4px;
}

.tab-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-family: var(--font);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-btn.active {
  background: var(--card);
  color: var(--primary);
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* P40: kbd 字体改用 --font-mono token（与 P38 搜索框的 hint-search/hint-palette 一致），
   原 monospace generic 在 Chrome 上会回退到 Courier New / Times，视觉与 Geist 风格冲突。 */
.tab-key {
  font-size: 0.65rem;
  padding: 1px 4px;
  border: 1px solid var(--border);
  border-radius: 3px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  background: var(--card);
  line-height: 1.2;
}

.expand-controls {
  display: flex;
  gap: 8px;
}

.expand-btn {
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

.expand-btn:hover {
  background: var(--tag-bg);
}

.help-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  transition: background 0.2s;
}

.help-btn:hover {
  background: var(--tag-bg);
}

/* Responsive */
@media (max-width: 767px) {
  .search-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .tabs {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    white-space: nowrap;
    padding-bottom: 4px;
  }

  .tab-btn {
    padding: 6px 12px;
    font-size: 0.8rem;
  }

  .expand-controls {
    justify-content: flex-end;
  }

  .help-btn {
    width: 32px;
    height: 32px;
    font-size: 0.9rem;
  }
}
</style>
