<template>
  <!-- P38 r14: a11y — role/aria-modal/aria-labelledby + Esc to close -->
  <div class="diff-modal-overlay" @click.self="$emit('close')" @keydown.esc="$emit('close')">
    <div
      class="diff-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="diff-modal-title"
    >
      <div class="diff-header">
        <h2 id="diff-modal-title">📋 记忆内容对比</h2>
        <button class="close-btn" @click="$emit('close')" aria-label="关闭对比对话框">✕</button>
      </div>

      <div class="diff-meta">
        <div class="meta-card left">
          <div class="meta-title">{{ memoryA?.title }}</div>
          <div class="meta-info">
            <span class="type-badge" :class="'type-' + memoryA?.type">{{ memoryA?.type }}</span>
            <span class="meta-date">更新: {{ formatDate(memoryA?.updatedAt) }}</span>
          </div>
        </div>
        <div class="meta-card right">
          <div class="meta-title">{{ memoryB?.title }}</div>
          <div class="meta-info">
            <span class="type-badge" :class="'type-' + memoryB?.type">{{ memoryB?.type }}</span>
            <span class="meta-date">更新: {{ formatDate(memoryB?.updatedAt) }}</span>
          </div>
        </div>
      </div>

      <div class="diff-stats">
        <span class="stat-item">相似度: <strong>{{ similarityPercent }}%</strong></span>
        <span class="stat-item added">+{{ diffStats.added }} 行</span>
        <span class="stat-item removed">-{{ diffStats.removed }} 行</span>
        <span class="stat-item unchanged">{{ diffStats.unchanged }} 行未变</span>
      </div>

      <div class="diff-content" ref="diffContentRef">
        <div class="diff-panel left-panel">
          <div class="panel-header">A 版本</div>
          <div class="panel-body">
            <template v-for="(line, idx) in diffLines" :key="'left-' + idx">
              <div v-if="line.type === 'removed'" class="diff-line removed">
                <span class="line-num">{{ line.leftLineNum }}</span>
                <span class="line-content">{{ line.content }}</span>
              </div>
              <div v-else-if="line.type === 'changed'" class="diff-line changed">
                <span class="line-num">{{ line.leftLineNum }}</span>
                <span class="line-content">{{ line.leftContent }}</span>
              </div>
              <div v-else class="diff-line unchanged">
                <span class="line-num">{{ line.leftLineNum }}</span>
                <span class="line-content">{{ line.content }}</span>
              </div>
            </template>
          </div>
        </div>

        <div class="diff-panel right-panel">
          <div class="panel-header">B 版本</div>
          <div class="panel-body">
            <template v-for="(line, idx) in diffLines" :key="'right-' + idx">
              <div v-if="line.type === 'added'" class="diff-line added">
                <span class="line-num">{{ line.rightLineNum }}</span>
                <span class="line-content">{{ line.content }}</span>
              </div>
              <div v-else-if="line.type === 'changed'" class="diff-line changed">
                <span class="line-num">{{ line.rightLineNum }}</span>
                <span class="line-content">{{ line.rightContent }}</span>
              </div>
              <div v-else class="diff-line unchanged">
                <span class="line-num">{{ line.rightLineNum }}</span>
                <span class="line-content">{{ line.content }}</span>
              </div>
            </template>
          </div>
        </div>
      </div>

      <div class="diff-footer">
        <span class="diff-hint">使用黄色高亮标记差异内容</span>
        <button class="action-btn" @click="$emit('close')">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { AgentMemory } from '@/types'

const props = defineProps<{
  memoryA: AgentMemory
  memoryB: AgentMemory
}>()

defineEmits<{
  (e: 'close'): void
}>()

interface DiffLine {
  type: 'unchanged' | 'added' | 'removed' | 'changed'
  content: string
  leftContent?: string
  rightContent?: string
  leftLineNum: number | null
  rightLineNum: number | null
}

const diffContentRef = ref<HTMLElement | null>(null)

const diffLines = computed<DiffLine[]>(() => {
  const contentA = props.memoryA?.content || ''
  const contentB = props.memoryB?.content || ''
  
  const linesA = contentA.split('\n')
  const linesB = contentB.split('\n')
  
  return computeDiff(linesA, linesB)
})

function computeDiff(linesA: string[], linesB: string[]): DiffLine[] {
  const result: DiffLine[] = []
  
  // Simple line-by-line diff algorithm
  let leftIdx = 0
  let rightIdx = 0
  
  while (leftIdx < linesA.length || rightIdx < linesB.length) {
    const leftLine = linesA[leftIdx]
    const rightLine = linesB[rightIdx]
    
    if (leftIdx >= linesA.length) {
      // Remaining lines in B are additions
      result.push({
        type: 'added',
        content: rightLine,
        leftLineNum: null,
        rightLineNum: rightIdx + 1,
      })
      rightIdx++
    } else if (rightIdx >= linesB.length) {
      // Remaining lines in A are removals
      result.push({
        type: 'removed',
        content: leftLine,
        leftLineNum: leftIdx + 1,
        rightLineNum: null,
      })
      leftIdx++
    } else if (leftLine === rightLine) {
      // Lines match
      result.push({
        type: 'unchanged',
        content: leftLine,
        leftLineNum: leftIdx + 1,
        rightLineNum: rightIdx + 1,
      })
      leftIdx++
      rightIdx++
    } else {
      // Lines differ - try to find matching lines
      const lookAhead = 3
      let foundMatch = false
      
      for (let i = 1; i <= lookAhead; i++) {
        if (leftIdx + i < linesA.length && linesA[leftIdx + i] === rightLine) {
          // Lines removed from A before match
          for (let j = 0; j < i; j++) {
            result.push({
              type: 'removed',
              content: linesA[leftIdx + j],
              leftLineNum: leftIdx + j + 1,
              rightLineNum: null,
            })
          }
          leftIdx += i
          foundMatch = true
          break
        }
        if (rightIdx + i < linesB.length && linesB[rightIdx + i] === leftLine) {
          // Lines added to B before match
          for (let j = 0; j < i; j++) {
            result.push({
              type: 'added',
              content: linesB[rightIdx + j],
              leftLineNum: null,
              rightLineNum: rightIdx + j + 1,
            })
          }
          rightIdx += i
          foundMatch = true
          break
        }
      }
      
      if (!foundMatch) {
        // Both lines changed
        result.push({
          type: 'changed',
          content: leftLine,
          leftContent: leftLine,
          rightContent: rightLine,
          leftLineNum: leftIdx + 1,
          rightLineNum: rightIdx + 1,
        })
        leftIdx++
        rightIdx++
      }
    }
  }
  
  return result
}

const diffStats = computed(() => {
  let added = 0
  let removed = 0
  let unchanged = 0
  
  for (const line of diffLines.value) {
    if (line.type === 'added') added++
    else if (line.type === 'removed') removed++
    else if (line.type === 'unchanged') unchanged++
    else if (line.type === 'changed') { added++; removed++ }
  }
  
  return { added, removed, unchanged }
})

const similarityPercent = computed(() => {
  const total = diffLines.value.length
  if (total === 0) return 100
  
  let matched = 0
  for (const line of diffLines.value) {
    if (line.type === 'unchanged') matched++
  }
  
  return Math.round((matched / total) * 100)
})

function formatDate(dateStr: string | undefined): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.diff-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  /* P38 r10: backdrop fade-in (与 CreateMemoryModal 节奏一致) */
  animation: modal-backdrop-in 200ms ease-out;
}

.diff-modal {
  background: var(--card);
  border-radius: 16px;
  width: 95%;
  max-width: 1200px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  /* P38 r10: 弹窗弹出动画 (与 CreateMemoryModal 一致) */
  animation: modal-pop-in 200ms cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modal-backdrop-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modal-pop-in {
  from {
    opacity: 0;
    transform: scale(0.96) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .diff-modal-overlay,
  .diff-modal {
    animation: none;
  }
}

.diff-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
}

.diff-header h2 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--primary);
  margin: 0;
}

/* P38 (round 4): close-btn 全站统一 — Geist ghost 32×32 圆角方块
   （与 ShareModal / WhatsNewModal / DedupModal 完全同款）。 */
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

.diff-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 16px 24px;
  background: var(--bg);
}

.meta-card {
  padding: 12px 16px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
}

.meta-title {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--primary);
  margin-bottom: 6px;
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.type-badge {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 10px;
  text-transform: capitalize;
}

.type-pattern { background: var(--type-pattern-bg); color: var(--type-pattern-text); }
.type-workflow { background: var(--type-workflow-bg); color: var(--type-workflow-text); }
.type-fact { background: var(--type-fact-bg); color: var(--type-fact-text); }
.type-preference { background: var(--type-preference-bg); color: var(--type-preference-text); }
.type-bug { background: var(--type-bug-bg); color: var(--type-bug-text); }
.type-architecture { background: var(--type-architecture-bg); color: var(--type-architecture-text); }

.meta-date {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.diff-stats {
  display: flex;
  gap: 20px;
  padding: 12px 24px;
  border-bottom: 1px solid var(--border);
  font-size: 0.8rem;
}

.stat-item {
  color: var(--text-secondary);
}

.stat-item strong {
  color: var(--primary);
  font-weight: 600;
}

/* P38 (round 6): 与 MemoryCard 健康度共用 token — 绿色 "added" 与 strength-high-fill
   同源（健康度 = 强），视觉上保持一致 */
.stat-item.added {
  color: var(--health-good);
}

.stat-item.removed {
  color: var(--health-bad);
}

.diff-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  flex: 1;
  overflow: hidden;
}

.diff-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.left-panel {
  border-right: 1px solid var(--border);
}

.panel-header {
  padding: 10px 16px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.panel-body {
  flex: 1;
  overflow-y: auto;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  font-size: 0.8rem;
  line-height: 1.6;
}

.diff-line {
  display: flex;
  padding: 2px 0;
  min-height: 24px;
}

.diff-line.unchanged {
  background: transparent;
  color: var(--primary);
}

/* P38 (round 6): diff 行 token 化 — 6 个 hex + 6 个 rgba → 6 个 var()，
   删除 6 行手动 [data-theme='dark'] 覆盖（light/dark 由 variables.css 接管） */
.diff-line.added {
  background: var(--diff-add-bg);
  color: var(--diff-add-ink);
}

.diff-line.removed {
  background: var(--diff-remove-bg);
  color: var(--diff-remove-ink);
}

.diff-line.changed {
  background: var(--diff-change-bg);
  color: var(--diff-change-ink);
}

.line-num {
  width: 40px;
  padding: 0 8px;
  text-align: right;
  color: var(--text-secondary);
  opacity: 0.5;
  user-select: none;
  flex-shrink: 0;
  font-size: 0.7rem;
}

.line-content {
  flex: 1;
  padding: 0 8px;
  white-space: pre-wrap;
  word-break: break-word;
}

.diff-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-top: 1px solid var(--border);
  background: var(--bg);
}

.diff-hint {
  font-size: 0.75rem;
  color: var(--text-secondary);
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
}

.action-btn:hover {
  background: var(--tag-bg);
}

@media (max-width: 767px) {
  .diff-meta {
    grid-template-columns: 1fr;
  }

  .diff-content {
    grid-template-columns: 1fr;
  }

  .left-panel {
    border-right: none;
    border-bottom: 1px solid var(--border);
    max-height: 40vh;
  }

  .diff-stats {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>