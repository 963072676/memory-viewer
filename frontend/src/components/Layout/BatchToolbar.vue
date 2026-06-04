<template>
  <transition name="toolbar">
    <div v-if="store.hasSelection" class="batch-toolbar">
      <div class="toolbar-info">
        <span class="selection-count">{{ $t('zh_006616_1') }} {{ store.selectionCount }} 条</span>
        <button class="toolbar-link" @click="store.clearSelection()">{{ $t('zh_ac3abf') }}</button>
        <button class="toolbar-link" @click="store.selectAll()">{{ $t('zh_006478') }}</button>
      </div>
      <div class="toolbar-actions">
        <button class="toolbar-btn" @click="$emit('batch', 'archive')" :disabled="loading">📦 {{ $t('zh_00661c') }}</button>
        <button class="toolbar-btn" @click="$emit('batch', 'unarchive')" :disabled="loading">📂 {{ $t('zh_ac347d') }}</button>
        <button class="toolbar-btn danger" @click="$emit('batch', 'delete')" :disabled="loading">🗑️ 删除</button>
        <button class="toolbar-btn" @click="$emit('export')" :disabled="loading">📥 {{ $t('zh_006597') }}</button>
        <div class="tag-batch-wrapper">
          <button class="toolbar-btn" @click="showTagInput = !showTagInput" :disabled="loading">🏷️ {{ $t('zh_ba195e') }}</button>
          <transition name="fade">
            <div v-if="showTagInput" class="tag-batch-popover">
              <input
                v-model="batchTagInput"
                type="text"
                class="tag-batch-input"
                :placeholder="$t('zh_7c705f')"
                @keydown.enter.prevent="submitBatchTag"
              />
              <button class="tag-batch-confirm" @click="submitBatchTag">{{ $t('zh_00694c') }}</button>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAgentMemoryStore } from '@/stores/agentmemory'

defineProps<{ loading?: boolean }>()
const emit = defineEmits<{
  (e: 'batch', action: string, params?: Record<string, any>): void
  (e: 'export'): void
}>()

const store = useAgentMemoryStore()
const showTagInput = ref(false)
const batchTagInput = ref('')

function submitBatchTag() {
  const tags = batchTagInput.value
    .split(',')
    .map(t => t.trim().toLowerCase())
    .filter(Boolean)
  if (tags.length > 0) {
    emit('batch', 'add_tags', { tags })
    batchTagInput.value = ''
    showTagInput.value = false
  }
}
</script>

<style scoped>
.batch-toolbar {
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--accent);
  /* P38 r19: 改 hardcoded white → var(--card), 与全站 token 对齐 */
  color: var(--card);
  padding: 12px 20px;
  border-radius: var(--radius);
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  box-shadow: var(--shadow-toolbar);
}

.toolbar-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selection-count {
  font-weight: 600;
  font-size: 0.9rem;
}

.toolbar-link {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  font-size: 0.8rem;
  font-family: var(--font);
  text-decoration: underline;
  padding: 0;
}

.toolbar-link:hover {
  color: white;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.toolbar-btn {
  padding: 6px 14px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.15);
  color: white;
  font-size: 0.8rem;
  font-family: var(--font);
  cursor: pointer;
  transition: background 0.2s;
}

.toolbar-btn:hover {
  background: rgba(255, 255, 255, 0.25);
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toolbar-btn.danger {
  background: rgba(229, 57, 53, 0.8);
  border-color: rgba(229, 57, 53, 0.5);
}

.toolbar-btn.danger:hover {
  background: rgba(229, 57, 53, 1);
}

/* F46: Tag batch popover */
.tag-batch-wrapper {
  position: relative;
}

.tag-batch-popover {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px;
  display: flex;
  gap: 6px;
  box-shadow: var(--shadow-toolbar);
  z-index: 60;
  min-width: 220px;
}

.tag-batch-input {
  flex: 1;
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--primary);
  font-size: 0.8rem;
  font-family: var(--font);
  outline: none;
}

.tag-batch-input:focus {
  border-color: var(--accent);
}

.tag-batch-confirm {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  background: var(--accent);
  /* P38 r19: 改 hardcoded white → var(--card), 与全站 token 对齐 */
  color: var(--card);
  font-size: 0.75rem;
  font-family: var(--font);
  cursor: pointer;
}

/* Transition */
.toolbar-enter-active,
.toolbar-leave-active {
  transition: all 0.3s ease;
}

.toolbar-enter-from,
.toolbar-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 767px) {
  .batch-toolbar {
    flex-direction: column;
    gap: 12px;
  }
  .toolbar-actions {
    flex-wrap: wrap;
  }
}
</style>
