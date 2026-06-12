<template>
  <div class="error-banner">
    <span class="error-icon">⚠️</span>
    <span class="error-text">
      {{ agentMemoryStore.error || hermesMemoryStore.error }}
    </span>
    <button class="retry-btn" @click="retry">{{ $t('i18n.retry') }}</button>
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
  background: var(--error-bg);
  border: 1px solid var(--error-border);
  border-radius: var(--radius);
  margin-bottom: 24px;
}

/* P38 r19: --error-bg / --error-border 已自带 dark 模式覆盖, 删除冗余 [data-theme='dark'] 手动 hex */

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
