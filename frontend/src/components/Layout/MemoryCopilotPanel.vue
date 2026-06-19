<template>
  <section class="copilot-panel">
    <div class="panel-header">
      <div>
        <h3>AI Copilot</h3>
        <div class="panel-meta">
          <span>{{ result?.memoryCount ?? 0 }} memories</span>
          <span>{{ providerLabel }}</span>
          <span>{{ sessionStore.activeSessionId || 'all sessions' }}</span>
        </div>
      </div>
      <div class="filter-row">
        <input
          v-model.trim="filters.provider"
          class="filter-input"
          type="text"
          placeholder="Provider"
          aria-label="Provider"
        />
        <input
          v-model.number="filters.limit"
          class="filter-input filter-input--limit"
          type="number"
          min="1"
          max="500"
          aria-label="Limit"
        />
      </div>
    </div>

    <div class="action-grid">
      <button
        v-for="item in actions"
        :key="item.action"
        class="copilot-action"
        :class="{ active: activeAction === item.action }"
        type="button"
        :disabled="loading"
        @click="run(item.action)"
      >
        <span>{{ item.label }}</span>
        <strong>{{ item.shortLabel }}</strong>
      </button>
    </div>

    <div v-if="error" class="result-state result-state--error">
      <p>{{ error }}</p>
      <button class="action-btn" type="button" @click="run(activeAction)">Retry</button>
    </div>

    <div v-else class="result-panel" :class="{ loading }">
      <div class="result-header">
        <div>
          <div class="result-title">{{ result?.title || currentAction.label }}</div>
          <div class="result-meta">
            <span>{{ result?.status || 'ready' }}</span>
            <span>{{ result?.providers.join(', ') || 'all providers' }}</span>
          </div>
        </div>
        <button class="action-btn action-btn--accent" type="button" :disabled="loading" @click="run(activeAction)">
          {{ loading ? 'Running...' : 'Run' }}
        </button>
      </div>

      <p class="result-message">{{ result?.message || 'No copilot result yet.' }}</p>

      <div class="result-layout">
        <div class="result-block">
          <div class="block-title">Recommendations</div>
          <div v-if="!result?.recommendations.length" class="empty-line">No recommendations yet.</div>
          <div v-else class="recommendation-list">
            <div
              v-for="item in result.recommendations.slice(0, 4)"
              :key="`${item.kind}-${item.title}`"
              class="recommendation-row"
            >
              <span class="priority-pill" :class="`priority-${item.priority}`">{{ item.priority }}</span>
              <div>
                <strong>{{ item.title }}</strong>
                <span>{{ item.detail }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="result-block">
          <div class="block-title">Result</div>
          <div v-if="detailRows.length === 0" class="empty-line">Run an action to populate this panel.</div>
          <div v-else class="detail-list">
            <div v-for="row in detailRows" :key="row.label" class="detail-row">
              <span>{{ row.label }}</span>
              <strong>{{ row.value }}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import {
  runCopilotAction,
  type CopilotAction,
  type CopilotRunResponse,
} from '@/api/copilot'
import { useSessionStore } from '@/stores/sessions'

const sessionStore = useSessionStore()
const actions: Array<{ action: CopilotAction; label: string; shortLabel: string }> = [
  { action: 'summarize_session', label: 'Summarize session', shortLabel: 'Summary' },
  { action: 'compress_memory', label: 'Compress memory', shortLabel: 'Compress' },
  { action: 'detect_contradictions', label: 'Detect contradictions', shortLabel: 'Scan' },
  { action: 'optimize_memory_structure', label: 'Optimize structure', shortLabel: 'Optimize' },
]

const filters = reactive({
  provider: '',
  limit: 200,
})
const activeAction = ref<CopilotAction>('summarize_session')
const result = ref<CopilotRunResponse | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const currentAction = computed(() => actions.find(item => item.action === activeAction.value) || actions[0])
const providerLabel = computed(() => (
  result.value?.providers.length ? result.value.providers.join(', ') : 'all providers'
))
const sessionParam = computed(() => sessionStore.activeSessionId || undefined)

const detailRows = computed(() => {
  if (!result.value) return []
  const data = result.value.result || {}
  if (result.value.action === 'compress_memory') {
    return [
      { label: 'Original', value: String(data.originalCount ?? 0) },
      { label: 'Compressed', value: String(data.compressedCount ?? 0) },
      { label: 'Max chars', value: String(data.maxChars ?? 0) },
    ]
  }
  if (result.value.action === 'detect_contradictions') {
    return [
      { label: 'Candidates', value: String(data.total ?? 0) },
      { label: 'Status', value: result.value.status },
    ]
  }
  if (result.value.action === 'optimize_memory_structure') {
    return [
      { label: 'Clusters', value: String(data.clusters?.total ?? 0) },
      { label: 'Recommendations', value: String(result.value.recommendations.length) },
    ]
  }
  return [
    { label: 'Keywords', value: String(data.keywords?.length ?? 0) },
    { label: 'Sessions', value: String(data.sessionIds?.length ?? 0) },
  ]
})

async function run(action: CopilotAction) {
  activeAction.value = action
  loading.value = true
  error.value = null
  try {
    result.value = await runCopilotAction({
      action,
      provider: filters.provider || undefined,
      sessionId: sessionParam.value,
      limit: Number(filters.limit) || 200,
      maxChars: 800,
    })
  } catch (e: any) {
    error.value = e?.message || 'Failed to run copilot action'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  run(activeAction.value)
})

watch(() => sessionStore.activeSessionId, () => {
  run(activeAction.value)
})
</script>

<style scoped>
.copilot-panel {
  margin-bottom: var(--space-7);
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.panel-header h3,
.result-title,
.block-title {
  color: var(--primary);
  font-weight: 700;
}

.panel-header h3 {
  margin: 0;
  font-size: 1rem;
}

.panel-meta,
.filter-row,
.result-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.panel-meta,
.result-meta {
  margin-top: var(--space-2);
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.filter-row {
  justify-content: flex-end;
}

.filter-input {
  width: 140px;
  min-height: 36px;
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--card);
  color: var(--primary);
  font-size: 0.82rem;
}

.filter-input--limit {
  width: 82px;
}

.filter-input:focus {
  border-color: var(--accent);
  outline: none;
  box-shadow: 0 0 0 4px var(--accent-glow);
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.copilot-action {
  min-height: 82px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: space-between;
  padding: var(--space-4);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--card);
  color: var(--primary);
  cursor: pointer;
  text-align: left;
  box-shadow: var(--shadow);
}

.copilot-action:hover:not(:disabled),
.copilot-action.active {
  border-color: color-mix(in srgb, var(--accent) 35%, var(--border));
  background: var(--accent-subtle);
}

.copilot-action:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.copilot-action span {
  color: var(--text-secondary);
  font-size: 0.76rem;
}

.copilot-action strong {
  color: var(--primary);
  font-size: 1rem;
}

.result-panel,
.result-state {
  border-radius: var(--radius-md);
  background: var(--card);
  box-shadow: var(--shadow);
}

.result-panel {
  padding: var(--space-5);
}

.result-panel.loading {
  opacity: 0.75;
}

.result-state {
  padding: var(--space-7);
  color: var(--text-secondary);
  text-align: center;
}

.result-state--error {
  color: var(--error-text);
}

.result-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.result-title {
  font-size: 0.95rem;
}

.result-message {
  margin-bottom: var(--space-4);
  color: var(--text-secondary);
  font-size: 0.86rem;
  line-height: 1.6;
}

.result-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(220px, 0.6fr);
  gap: var(--space-3);
}

.result-block {
  min-width: 0;
  padding-top: var(--space-4);
  border-top: 1px solid var(--border);
}

.block-title {
  margin-bottom: var(--space-3);
  font-size: 0.84rem;
}

.empty-line {
  color: var(--text-secondary);
  font-size: 0.84rem;
}

.recommendation-list,
.detail-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.recommendation-row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: var(--space-3);
  padding-top: var(--space-2);
  border-top: 1px solid var(--border);
}

.recommendation-row:first-child,
.detail-row:first-child {
  border-top: none;
  padding-top: 0;
}

.recommendation-row strong,
.recommendation-row span,
.detail-row span,
.detail-row strong {
  display: block;
}

.recommendation-row strong,
.detail-row strong {
  color: var(--primary);
  font-size: 0.82rem;
}

.recommendation-row span,
.detail-row span {
  color: var(--text-secondary);
  font-size: 0.76rem;
  line-height: 1.45;
}

.priority-pill {
  display: inline-flex;
  align-items: center;
  align-self: start;
  min-height: 24px;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: var(--tag-bg);
  color: var(--text-secondary);
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
}

.priority-high {
  background: var(--error-bg);
  color: var(--error-text);
}

.priority-medium {
  background: var(--warn-bg);
  color: var(--warn-text);
}

.detail-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  min-height: 34px;
  padding-top: var(--space-2);
  border-top: 1px solid var(--border);
}

@media (max-width: 767px) {
  .panel-header,
  .filter-row,
  .result-header {
    align-items: stretch;
    flex-direction: column;
  }

  .filter-input,
  .filter-input--limit {
    width: 100%;
  }

  .result-layout {
    grid-template-columns: 1fr;
  }
}
</style>
