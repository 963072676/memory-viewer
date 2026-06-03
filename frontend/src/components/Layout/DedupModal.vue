<template>
  <div class="dedup-modal-overlay" @click.self="$emit('close')">
    <div class="dedup-modal">
      <div class="dedup-header">
        <h2>🔍 重复记忆去重</h2>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <div class="dedup-summary">
        <span class="summary-item">发现 <strong>{{ pairs.length }}</strong> 对重复记忆</span>
        <span class="summary-item">已选择 <strong>{{ selectedIndices.length }}</strong> 对待合并</span>
        <label class="select-all">
          <input type="checkbox" v-model="selectAll" @change="toggleSelectAll" />
          全选
        </label>
      </div>

      <div class="pairs-list" v-if="pairs.length > 0">
        <div
          v-for="(pair, idx) in pairs"
          :key="idx"
          class="pair-item"
          :class="{ selected: selectedIndices.includes(idx) }"
        >
          <label class="pair-checkbox">
            <input
              type="checkbox"
              :checked="selectedIndices.includes(idx)"
              @change="togglePair(idx)"
            />
          </label>
          <div class="pair-content">
            <div class="pair-titles">
              <div class="memory-card memory-a">
                <span class="memory-title">{{ pair.memory_a.title }}</span>
                <span class="memory-type" :class="'type-' + pair.memory_a.type">{{ pair.memory_a.type }}</span>
              </div>
              <div class="similarity-badge">
                {{ Math.round(pair.similarity * 100) }}%
              </div>
              <div class="memory-card memory-b">
                <span class="memory-title">{{ pair.memory_b.title }}</span>
                <span class="memory-type" :class="'type-' + pair.memory_b.type">{{ pair.memory_b.type }}</span>
              </div>
            </div>
            <div class="pair-meta">
              <span class="meta-item">概念相似度: {{ Math.round(pair.concepts_similarity * 100) }}%</span>
              <span class="meta-item">标题相似度: {{ Math.round(pair.title_similarity * 100) }}%</span>
              <span class="meta-item" v-if="pair.shared_concepts.length > 0">
                共享概念: {{ pair.shared_concepts.join(', ') }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="empty-state" v-else>
        <div class="empty-icon">✅</div>
        <h3>没有发现重复记忆</h3>
        <p>您的记忆库中没有发现语义相似度超过 70% 的重复记忆</p>
      </div>

      <div class="dedup-footer">
        <span class="footer-hint">选择要合并的记忆对，保留相似度较高的一条</span>
        <div class="footer-actions">
          <button class="action-btn secondary" @click="$emit('close')">取消</button>
          <button
            class="action-btn primary"
            :disabled="selectedIndices.length === 0 || merging"
            @click="handleMerge"
          >
            {{ merging ? '合并中...' : `合并 ${selectedIndices.length} 对` }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { DuplicatePair } from '@/types'

const props = defineProps<{
  pairs: DuplicatePair[]
  selectedPairs: Set<number>
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'merge', pairIndices: number[]): void
  (e: 'refresh'): void
}>()

const merging = ref(false)
const selectAll = ref(true)

const selectedIndices = computed(() => {
  return Array.from(props.selectedPairs)
})

function togglePair(idx: number) {
  const newSet = new Set(props.selectedPairs)
  if (newSet.has(idx)) {
    newSet.delete(idx)
  } else {
    newSet.add(idx)
  }
  // Note: We can't directly modify prop, emit to parent
  // For simplicity, we'll use emit
  emit('merge', Array.from(newSet))
}

function toggleSelectAll() {
  if (selectAll.value) {
    emit('merge', props.pairs.map((_: any, i: number) => i))
  } else {
    emit('merge', [])
  }
}

async function handleMerge() {
  if (selectedIndices.value.length === 0) return
  merging.value = true
  try {
    emit('merge', selectedIndices.value)
  } finally {
    merging.value = false
  }
}
</script>

<style scoped>
.dedup-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.dedup-modal {
  background: var(--card);
  border-radius: 16px;
  width: 95%;
  max-width: 900px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dedup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
}

.dedup-header h2 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--primary);
  margin: 0;
}

/* P38 (round 4): close-btn 全站统一 — Geist ghost 32×32 圆角方块
   （与 ShareModal / WhatsNewModal / MemoryDiffModal 完全同款）。 */
.close-btn {
  width: 32px;
  height: 32px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  line-height: 1;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.close-btn:hover {
  background: var(--tag-bg);
  border-color: var(--border-strong);
  color: var(--primary);
}

.dedup-summary {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 14px 24px;
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  font-size: 0.85rem;
}

.summary-item {
  color: var(--text-secondary);
}

.summary-item strong {
  color: var(--primary);
  font-weight: 600;
}

.select-all {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.select-all input {
  cursor: pointer;
}

.pairs-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pair-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  transition: all 0.2s;
}

/* P38 (round 7): 5% accent 浅蓝背景 + 蓝边 — 之前硬编码 Apple rgba(0,122,255,0.05) */
.pair-item.selected {
  border-color: var(--accent);
  background: var(--accent-soft);
}

.pair-checkbox {
  display: flex;
  align-items: flex-start;
  padding-top: 2px;
}

.pair-checkbox input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.pair-content {
  flex: 1;
}

.pair-titles {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.memory-card {
  flex: 1;
  padding: 10px 14px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.memory-title {
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.memory-type {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 6px;
  text-transform: capitalize;
  flex-shrink: 0;
}

.type-pattern { background: var(--type-pattern-bg); color: var(--type-pattern-text); }
.type-workflow { background: var(--type-workflow-bg); color: var(--type-workflow-text); }
.type-fact { background: var(--type-fact-bg); color: var(--type-fact-text); }
.type-preference { background: var(--type-preference-bg); color: var(--type-preference-text); }
.type-bug { background: var(--type-bug-bg); color: var(--type-bug-text); }
.type-architecture { background: var(--type-architecture-bg); color: var(--type-architecture-text); }

.similarity-badge {
  padding: 6px 12px;
  background: var(--accent);
  color: white;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

.pair-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px;
  color: var(--primary);
}

.empty-state p {
  margin: 0;
  font-size: 0.85rem;
}

.dedup-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-top: 1px solid var(--border);
  background: var(--bg);
}

.footer-hint {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.footer-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--primary);
  cursor: pointer;
  font-size: 0.8rem;
  font-family: var(--font);
  transition: all 0.2s;
}

.action-btn:hover:not(:disabled) {
  background: var(--tag-bg);
}

.action-btn.primary {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}

.action-btn.primary:hover:not(:disabled) {
  background: #0056b3;
}

.action-btn.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.secondary {
  background: var(--bg);
}

@media (max-width: 767px) {
  .pair-titles {
    flex-direction: column;
  }

  .similarity-badge {
    order: -1;
  }

  .memory-card {
    width: 100%;
  }

  .dedup-summary {
    flex-wrap: wrap;
    gap: 12px;
  }
}
</style>