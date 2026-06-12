<template>
  <div class="duplicate-panel" v-if="show">
    <div class="panel-header">
      <h3>🔍 {{ $t('i18n.deduplication_check') }}</h3>
      <div class="panel-controls">
        <label class="threshold-label">
          {{ $t('i18n.threshold') }}:
          <input type="range" v-model.number="threshold" min="0.3" max="1" step="0.05" class="threshold-slider" />
          <span>{{ threshold.toFixed(2) }}</span>
        </label>
        <button class="action-btn" @click="scan" :disabled="scanning">
          {{ scanning ? '扫描中...' : '扫描' }}
        </button>
        <button class="action-btn close-btn" @click="$emit('close')">✕</button>
      </div>
    </div>

    <div v-if="scanning" class="scanning-state">{{ $t('i18n.scanning_duplicates') }}...</div>

    <div v-else-if="pairs.length === 0 && scanned" class="empty-state">
      ✅ {{ $t('i18n.duplicates_found') }}
    </div>

    <div v-else class="pairs-list">
      <div v-for="(pair, idx) in pairs" :key="idx" class="pair-card">
        <div class="pair-similarity">
          <span class="similarity-badge">{{ (pair.similarity * 100).toFixed(0) }}%</span>
          <span class="similarity-detail">
            {{ $t('i18n.concepts') }}: {{ (pair.concepts_similarity * 100).toFixed(0) }}% |
            {{ $t('i18n.title') }}: {{ (pair.title_similarity * 100).toFixed(0) }}%
          </span>
        </div>
        <div class="pair-items">
          <div class="pair-item">
            <div class="pair-item-title">{{ pair.memory_a.title }}</div>
            <div class="pair-item-strength">强度: {{ pair.memory_a.strength }}</div>
          </div>
          <div class="pair-arrow">⟷</div>
          <div class="pair-item">
            <div class="pair-item-title">{{ pair.memory_b.title }}</div>
            <div class="pair-item-strength">强度: {{ pair.memory_b.strength }}</div>
          </div>
        </div>
        <div class="pair-shared" v-if="pair.shared_concepts.length">
          {{ $t('i18n.shared_concepts') }}:
          <span class="shared-tag" v-for="c in pair.shared_concepts" :key="c">{{ c }}</span>
        </div>
        <div class="pair-actions">
          <button class="merge-btn" @click="merge(pair.memory_a.id, pair.memory_b.id)" :disabled="merging">
            {{ $t('i18n.merge') }}（{{ $t('i18n.keep_00642b') }}「{{ pair.memory_a.strength >= pair.memory_b.strength ? pair.memory_a.title : pair.memory_b.title }}」）
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { getDuplicates, mergeMemories } from '@/api/agentmemory'
import { useAgentMemoryStore } from '@/stores/agentmemory'
import { useToast } from '@/composables/useToast'
import type { DuplicatePair } from '@/types'

defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const agentMemoryStore = useAgentMemoryStore()
const toast = useToast()
const threshold = ref(0.7)
const scanning = ref(false)
const scanned = ref(false)
const merging = ref(false)
const pairs = ref<DuplicatePair[]>([])

async function scan() {
  scanning.value = true
  scanned.value = false
  try {
    const data = await getDuplicates(threshold.value)
    pairs.value = data.pairs
  } catch (e) {
    console.error('Duplicate scan failed:', e)
    toast.error('重复扫描失败')
  } finally {
    scanning.value = false
    scanned.value = true
  }
}

async function merge(keepId: string, mergeId: string) {
  merging.value = true
  try {
    await mergeMemories(keepId, mergeId)
    toast.success('记忆合并成功')
    await agentMemoryStore.refresh()
    // Re-scan after merge
    await scan()
  } catch (e) {
    console.error('Merge failed:', e)
    toast.error('记忆合并失败')
  } finally {
    merging.value = false
  }
}
</script>

<style scoped>
.duplicate-panel {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 24px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.panel-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary);
  margin: 0;
}

.panel-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.threshold-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.threshold-slider {
  width: 80px;
  accent-color: var(--accent);
}

.action-btn {
  padding: 6px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--primary);
  font-size: 0.75rem;
  font-family: var(--font);
  cursor: pointer;
  transition: background 0.2s;
}

.action-btn:hover { background: var(--tag-bg); }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.close-btn { border: none; font-size: 1rem; }

.scanning-state,
.empty-state {
  text-align: center;
  padding: 24px;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.pairs-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pair-card {
  background: var(--tag-bg);
  border-radius: 8px;
  padding: 12px;
}

.pair-similarity {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.similarity-badge {
  font-size: 0.8rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 12px;
  background: var(--accent);
  /* P38 r33: on-accent 文字 token 化 — 旧 color: white 在 dark 模式 --accent 不变,
     但用户偏好"白上加白"刺眼。改 var(--card) 让 dark 模式下文字自动变深色 ink。 */
  color: var(--card);
}

.similarity-detail {
  font-size: 0.65rem;
  color: var(--text-secondary);
}

.pair-items {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.pair-item {
  flex: 1;
}

.pair-item-title {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--primary);
}

.pair-item-strength {
  font-size: 0.65rem;
  color: var(--text-secondary);
}

.pair-arrow {
  font-size: 1rem;
  color: var(--text-secondary);
}

.pair-shared {
  font-size: 0.7rem;
  color: var(--text-secondary);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.shared-tag {
  font-size: 0.6rem;
  padding: 1px 5px;
  border-radius: 8px;
  background: var(--card);
  border: 1px solid var(--border);
}

.pair-actions {
  margin-top: 4px;
}

.merge-btn {
  padding: 5px 12px;
  border: 1px solid var(--accent);
  border-radius: 6px;
  background: transparent;
  color: var(--accent);
  font-size: 0.7rem;
  font-family: var(--font);
  cursor: pointer;
  transition: all 0.2s;
}

.merge-btn:hover {
  background: var(--accent);
  /* P38 r33: on-accent 文字 token 化 — 配 r33 .similarity-badge 修复，dark 模式自动跟随 */
  color: var(--card);
}

.merge-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 767px) {
  .panel-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .panel-controls {
    flex-wrap: wrap;
    width: 100%;
  }

  .pair-items {
    flex-direction: column;
    gap: 8px;
  }

  .pair-arrow {
    text-align: center;
  }
}
</style>
