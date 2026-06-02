<template>
  <div class="stats-bar">
    <div class="stats">
      <div class="stat-item">
        <strong>{{ agentMemoryStore.memories.length }}</strong>
        <span>AgentMemory 条目</span>
      </div>
      <div class="stat-item">
        <strong>{{ hermesMemoryStore.totalEntries }}</strong>
        <span>Hermes Memory 条目</span>
      </div>
      <div class="stat-item">
        <strong>{{ Object.keys(hermesMemoryStore.profiles).length }}</strong>
        <span>Profiles</span>
      </div>
    </div>
    <SortDropdown />
  </div>
</template>

<script setup lang="ts">
import { useAgentMemoryStore } from '@/stores/agentmemory'
import { useHermesMemoryStore } from '@/stores/hermes-memory'
import SortDropdown from './SortDropdown.vue'

const agentMemoryStore = useAgentMemoryStore()
const hermesMemoryStore = useHermesMemoryStore()
</script>

<style scoped>
.stats-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}

.stats {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.stat-item {
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-align: center;
}

.stat-item strong {
  display: block;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--primary);
}

.stat-item span {
  display: block;
  margin-top: 2px;
}

/* Responsive */
@media (max-width: 767px) {
  .stats-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  .stats {
    gap: 16px;
    width: 100%;
    justify-content: space-between;
  }

  .stat-item {
    font-size: 0.75rem;
    flex: 1;
    min-width: 80px;
  }

  .stat-item strong {
    font-size: 1.1rem;
  }
}
</style>
