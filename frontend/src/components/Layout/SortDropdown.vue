<template>
  <div class="sort-dropdown">
    <label for="sort-select" class="sr-only">排序方式</label>
    <select id="sort-select" :value="uiStore.sortBy" @change="onSortChange" class="sort-select">
      <option value="updatedAt">{{ $t('i18n.time') }}</option>
      <option value="strength">{{ $t('i18n.strength') }}</option>
      <option value="type">{{ $t('i18n.type_0d3c5f') }}</option>
    </select>
    <button class="order-btn" @click="uiStore.toggleSortOrder()" :title="uiStore.sortOrder === 'desc' ? '降序' : '升序'">
      {{ uiStore.sortOrder === 'desc' ? '↓' : '↑' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { useUIStore } from '@/stores/ui'

const uiStore = useUIStore()

function onSortChange(e: Event) {
  const val = (e.target as HTMLSelectElement).value as any
  uiStore.setSort(val)
}
</script>

<style scoped>
.sort-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-select {
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--primary);
  font-size: 0.875rem;
  font-family: var(--font);
  cursor: pointer;
  outline: none;
}

.sort-select:focus {
  border-color: var(--accent);
}

.order-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--primary);
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.order-btn:hover {
  background: var(--tag-bg);
}
</style>
