<template>
  <div class="diagnostics-view">
    <div class="view-header">
      <h2>🔍 记忆系统诊断</h2>
      <button class="action-btn" @click="runDiagnostics" :disabled="loading">
        {{ loading ? '诊断中...' : '重新诊断' }}
      </button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <EmptyState v-else-if="loadError" icon="⚠️" message="诊断加载失败" action-text="点击重试" @action="runDiagnostics" />

    <div v-else-if="data" class="diagnostics-content">
      <!-- Summary -->
      <div class="summary-row">
        <div class="summary-card">
          <div class="summary-value">{{ data.total_memories }}</div>
          <div class="summary-label">总记忆数</div>
        </div>
        <div class="summary-card" :class="{ warn: data.duplicates.length > 0 }">
          <div class="summary-value">{{ data.duplicates.length }}</div>
          <div class="summary-label">重复项</div>
        </div>
        <div class="summary-card" :class="{ warn: data.orphaned_concepts.length > 0 }">
          <div class="summary-value">{{ data.orphaned_concepts.length }}</div>
          <div class="summary-label">孤立概念</div>
        </div>
        <div class="summary-card" :class="{ warn: data.strength_anomalies.length > 0 }">
          <div class="summary-value">{{ data.strength_anomalies.length }}</div>
          <div class="summary-label">Strength 异常</div>
        </div>
      </div>

      <!-- Duplicates -->
      <section class="diag-section">
        <h3>重复记忆 (Jaccard > 0.6)</h3>
        <div v-if="data.duplicates.length === 0" class="empty">✅ 无重复项</div>
        <div v-else class="issue-list">
          <div v-for="(d, i) in data.duplicates" :key="i" class="issue-card">
            <span class="similarity">相似度: {{ (d.jaccard_similarity * 100).toFixed(1) }}%</span>
            <p><strong>{{ d.memory_a_title }}</strong> ↔ <strong>{{ d.memory_b_title }}</strong></p>
          </div>
        </div>
      </section>

      <!-- Orphaned concepts -->
      <section class="diag-section">
        <h3>孤立概念 (出现 &lt; 2 次)</h3>
        <div v-if="data.orphaned_concepts.length === 0" class="empty">✅ 无孤立概念</div>
        <div v-else class="tag-list">
          <span v-for="c in data.orphaned_concepts" :key="c.concept" class="orphan-tag">
            {{ c.concept }} ({{ c.count }})
          </span>
        </div>
      </section>

      <!-- Strength anomalies -->
      <section class="diag-section">
        <h3>Strength 异常 (&lt; 1 或 &gt; 9)</h3>
        <div v-if="data.strength_anomalies.length === 0" class="empty">✅ 无异常</div>
        <div v-else class="issue-list">
          <div v-for="a in data.strength_anomalies" :key="a.id" class="issue-card">
            <p><strong>{{ a.title }}</strong> — strength: {{ a.strength }}</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import EmptyState from '@/components/Layout/EmptyState.vue'

interface Duplicate { memory_a_id: string; memory_a_title: string; memory_b_id: string; memory_b_title: string; jaccard_similarity: number }
interface OrphanedConcept { concept: string; count: number }
interface StrengthAnomaly { id: string; title: string; strength: number }
interface DiagnosticsData { total_memories: number; duplicates: Duplicate[]; orphaned_concepts: OrphanedConcept[]; strength_anomalies: StrengthAnomaly[] }

const loading = ref(false)
const data = ref<DiagnosticsData | null>(null)
const loadError = ref(false)

async function runDiagnostics() {
  loading.value = true
  loadError.value = false
  try {
    const res = await fetch('/api/diagnostics')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    data.value = await res.json()
  } catch (e) {
    console.error('Diagnostics failed:', e)
    loadError.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => runDiagnostics())
</script>

<style scoped>
.diagnostics-view { padding-bottom: 40px; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
h2 { font-size: 1.5rem; font-weight: 600; color: var(--primary); }
.action-btn { padding: 8px 16px; border: 1px solid var(--border); border-radius: 8px; background: var(--card); color: var(--primary); cursor: pointer; font-size: 0.85rem; }
.action-btn:hover { background: var(--tag-bg); }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.loading { text-align: center; padding: 40px; color: var(--text-secondary); }
.summary-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 32px; }
.summary-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; text-align: center; }
.summary-card.warn { border-color: var(--error-text); }
.summary-value { font-size: 2rem; font-weight: 700; color: var(--primary); }
.summary-label { font-size: 0.8rem; color: var(--text-secondary); margin-top: 4px; }
.diag-section { margin-bottom: 28px; }
h3 { font-size: 1.1rem; font-weight: 600; margin-bottom: 12px; color: var(--primary); }
.empty { color: var(--text-secondary); font-size: 0.9rem; padding: 8px 0; }
.issue-list { display: flex; flex-direction: column; gap: 8px; }
.issue-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 12px 16px; font-size: 0.875rem; }
.similarity { font-size: 0.75rem; color: var(--error-text); font-weight: 600; }
.tag-list { display: flex; flex-wrap: wrap; gap: 8px; }
.orphan-tag { background: var(--tag-bg); padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; color: var(--text-secondary); }

/* Responsive */
@media (max-width: 767px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .summary-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .summary-value {
    font-size: 1.5rem;
  }
}
</style>
