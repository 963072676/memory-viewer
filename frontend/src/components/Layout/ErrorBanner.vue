<template>
  <div class="error-banner">
    <span class="error-icon">⚠️</span>
    <span class="error-text">
      {{ agentMemoryStore.error || hermesMemoryStore.error }}
    </span>
    <button class="retry-btn" @click="retry">重试</button>
  </div>
</template>

<script setup lang="ts">
import { useAgentMemoryStore } from '@/stores/agentmemory'
import { useHermesMemoryStore } from '@/stores/hermes-memory'

const agentMemoryStore = useAgentMemoryStore()
const hermesMemoryStore = useHermesMemoryStore()

function retry() {
  agentMemoryStore.refresh()
  hermesMemoryStore.refresh()
}
</script>

<style scoped>
.error-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: var(--radius);
  margin-bottom: 24px;
}

[data-theme='dark'] .error-banner {
  background: #3e1a1a;
  border-color: #5a2020;
}

.error-icon {
  font-size: 1.2rem;
}

.error-text {
  flex: 1;
  font-size: 0.875rem;
  color: var(--error);
}

.retry-btn {
  padding: 6px 14px;
  border: 1px solid var(--error);
  border-radius: 6px;
  background: transparent;
  color: var(--error);
  font-size: 0.8rem;
  cursor: pointer;
  font-family: var(--font);
}

.retry-btn:hover {
  background: rgba(255, 59, 48, 0.1);
}
</style>
