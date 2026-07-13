<template>
  <section class="copilot-panel">
    <div class="panel-header">
      <div>
        <h3>{{ $t('i18n.copilot_title') }}</h3>
        <div class="panel-meta">
          <span>{{ $t('i18n.copilot_memory_count', { count: result?.memoryCount ?? 0 }) }}</span>
          <span>{{ providerLabel }}</span>
          <span>{{ sessionStore.activeSessionId || $t('i18n.copilot_all_sessions') }}</span>
        </div>
      </div>
      <div class="filter-row">
        <input
          v-model.trim="filters.provider"
          class="filter-input"
          type="text"
          :placeholder="$t('i18n.copilot_provider_filter')"
          :aria-label="$t('i18n.copilot_provider_filter')"
        />
        <input
          v-model.number="filters.limit"
          class="filter-input filter-input--limit"
          type="number"
          min="1"
          max="500"
          :aria-label="$t('i18n.copilot_limit')"
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
      <button class="action-btn" type="button" @click="run(activeAction)">{{ $t('i18n.retry') }}</button>
    </div>

    <div v-else class="result-panel" :class="{ loading }">
      <div class="result-header">
        <div>
          <div class="result-title">{{ resultTitle }}</div>
          <div class="result-meta">
            <span>{{ statusLabel(result?.status) }}</span>
            <span>{{ providerLabel }}</span>
          </div>
        </div>
        <button class="action-btn action-btn--accent" type="button" :disabled="loading" @click="run(activeAction)">
          {{ loading ? $t('i18n.copilot_running') : $t('i18n.copilot_run') }}
        </button>
      </div>

      <p class="result-message">{{ resultMessage }}</p>

      <div class="result-layout">
        <div class="result-block">
          <div class="block-title">{{ $t('i18n.copilot_recommendations') }}</div>
          <div v-if="!result?.recommendations.length" class="empty-line">{{ $t('i18n.copilot_no_recommendations') }}</div>
          <div v-else class="recommendation-list">
            <component
              v-for="item in result.recommendations.slice(0, 4)"
              :key="`${item.kind}-${item.title}`"
              :is="recommendationTarget(item.kind) ? 'a' : 'div'"
              class="recommendation-row"
              :class="{ 'recommendation-row--actionable': recommendationTarget(item.kind) }"
              :href="recommendationTarget(item.kind) || undefined"
              @click="followRecommendation($event, item.kind)"
            >
              <span class="priority-pill" :class="`priority-${item.priority}`">{{ priorityLabel(item.priority) }}</span>
              <div>
                <strong>{{ recommendationTitle(item) }}</strong>
                <span>{{ recommendationDetail(item) }}</span>
              </div>
              <span
                v-if="recommendationTarget(item.kind)"
                class="recommendation-arrow"
                aria-hidden="true"
              >→</span>
            </component>
          </div>
        </div>

        <div class="result-block">
          <div class="block-title">{{ $t('i18n.copilot_result') }}</div>
          <div v-if="detailRows.length === 0" class="empty-line">{{ $t('i18n.copilot_run_to_populate') }}</div>
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
import { useI18n } from 'vue-i18n'
import {
  runCopilotAction,
  type CopilotAction,
  type CopilotRunResponse,
} from '@/api/copilot'
import { useSessionStore } from '@/stores/sessions'

const sessionStore = useSessionStore()
const { t } = useI18n()
const actions = computed<Array<{ action: CopilotAction; label: string; shortLabel: string }>>(() => [
  { action: 'summarize_session', label: t('i18n.copilot_summarize_session'), shortLabel: t('i18n.copilot_summary') },
  { action: 'compress_memory', label: t('i18n.copilot_compress_memory'), shortLabel: t('i18n.copilot_compress') },
  { action: 'detect_contradictions', label: t('i18n.copilot_detect_contradictions'), shortLabel: t('i18n.copilot_scan') },
  { action: 'optimize_memory_structure', label: t('i18n.copilot_optimize_structure'), shortLabel: t('i18n.copilot_optimize') },
])

const filters = reactive({
  provider: '',
  limit: 200,
})
const activeAction = ref<CopilotAction>('summarize_session')
const result = ref<CopilotRunResponse | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const currentAction = computed(() => actions.value.find(item => item.action === activeAction.value) || actions.value[0])
const providerLabel = computed(() => (
  result.value?.providers.length ? result.value.providers.join(', ') : t('i18n.copilot_all_providers')
))
const sessionParam = computed(() => sessionStore.activeSessionId || undefined)
const resultTitle = computed(() => currentAction.value.label)
const resultMessage = computed(() => {
  if (!result.value) return t('i18n.copilot_no_result')
  if (result.value.status === 'empty') return t('i18n.copilot_no_matching_memories')

  const data = result.value.result || {}
  if (result.value.action === 'detect_contradictions') {
    const total = Number(data.total ?? 0)
    return total
      ? t('i18n.copilot_contradictions_detected', { count: total })
      : t('i18n.copilot_no_contradictions')
  }
  if (result.value.action === 'optimize_memory_structure') return t('i18n.copilot_structure_ready')
  if (result.value.action === 'compress_memory' && !data.compressed) return t('i18n.copilot_nothing_to_compress')
  return result.value.message
})

const detailRows = computed(() => {
  if (!result.value) return []
  const data = result.value.result || {}
  if (result.value.action === 'compress_memory') {
    return [
      { label: t('i18n.copilot_original'), value: String(data.originalCount ?? 0) },
      { label: t('i18n.copilot_compressed'), value: String(data.compressedCount ?? 0) },
      { label: t('i18n.copilot_max_chars'), value: String(data.maxChars ?? 0) },
    ]
  }
  if (result.value.action === 'detect_contradictions') {
    return [
      { label: t('i18n.copilot_candidates'), value: String(data.total ?? 0) },
      { label: t('i18n.copilot_status'), value: statusLabel(result.value.status) },
    ]
  }
  if (result.value.action === 'optimize_memory_structure') {
    return [
      { label: t('i18n.copilot_clusters'), value: String(data.clusters?.total ?? 0) },
      { label: t('i18n.copilot_recommendations'), value: String(result.value.recommendations.length) },
    ]
  }
  return [
    { label: t('i18n.copilot_keywords'), value: String(data.keywords?.length ?? 0) },
    { label: t('i18n.copilot_sessions'), value: String(data.sessionIds?.length ?? 0) },
  ]
})

function statusLabel(status?: string) {
  if (status === 'attention') return t('i18n.copilot_attention')
  if (status === 'empty') return t('i18n.copilot_empty')
  if (status === 'ready' || !status) return t('i18n.copilot_ready')
  return status
}

function priorityLabel(priority: string) {
  if (priority === 'high') return t('i18n.copilot_priority_high')
  if (priority === 'medium') return t('i18n.copilot_priority_medium')
  if (priority === 'low') return t('i18n.copilot_priority_low')
  return priority
}

function numberParam(item: CopilotRunResponse['recommendations'][number], key: string) {
  const value = item.params?.[key]
  return typeof value === 'number' ? value : undefined
}

function recommendationTitle(item: CopilotRunResponse['recommendations'][number]) {
  const titles: Record<string, string> = {
    contradiction: 'i18n.copilot_recommendation_contradiction_title',
    tagging: 'i18n.copilot_recommendation_tagging_title',
    clustering: 'i18n.copilot_recommendation_clustering_title',
    session: 'i18n.copilot_recommendation_session_title',
    archive: 'i18n.copilot_recommendation_archive_title',
    structure: 'i18n.copilot_recommendation_structure_title',
  }
  return titles[item.kind] ? t(titles[item.kind]) : item.title
}

function recommendationDetail(item: CopilotRunResponse['recommendations'][number]) {
  if (item.kind === 'contradiction') {
    const total = numberParam(item, 'total')
    return total === undefined ? item.detail : t('i18n.copilot_recommendation_contradiction_detail', { count: total })
  }
  if (item.kind === 'tagging') {
    const total = numberParam(item, 'total')
    return total === undefined ? item.detail : t('i18n.copilot_recommendation_tagging_detail', { count: total })
  }
  if (item.kind === 'clustering') {
    const clusters = numberParam(item, 'clusters')
    const memories = numberParam(item, 'memories')
    return clusters === undefined || memories === undefined
      ? item.detail
      : t('i18n.copilot_recommendation_clustering_detail', { clusters, memories })
  }
  if (item.kind === 'session') return t('i18n.copilot_recommendation_session_detail')
  if (item.kind === 'archive') {
    const total = numberParam(item, 'total')
    return total === undefined ? item.detail : t('i18n.copilot_recommendation_archive_detail', { count: total })
  }
  if (item.kind === 'structure') return t('i18n.copilot_recommendation_structure_detail')
  return item.detail
}

function recommendationTarget(kind: string) {
  const targets: Record<string, string> = {
    contradiction: '#memory-intelligence-contradictions',
    tagging: '#memory-intelligence-tags',
    clustering: '#memory-intelligence-clusters',
    structure: '#memory-intelligence-summary',
  }
  return targets[kind] || ''
}

function followRecommendation(event: MouseEvent, kind: string) {
  const selector = recommendationTarget(kind)
  if (!selector) return

  const target = document.querySelector<HTMLElement>(selector)
  if (!target) return

  event.preventDefault()
  if (window.location.hash === selector) {
    window.history.replaceState(null, '', selector)
  } else {
    window.history.pushState(null, '', selector)
  }
  target.scrollIntoView({
    behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
    block: 'start',
  })
  target.focus({ preventScroll: true })
}

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
    error.value = e?.message || t('i18n.copilot_run_failed')
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

.recommendation-row--actionable {
  grid-template-columns: auto minmax(0, 1fr) auto;
  margin-inline: calc(var(--space-2) * -1);
  padding: var(--space-2);
  border-radius: var(--radius-sm);
  color: inherit;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}

.recommendation-row--actionable:first-child {
  padding-top: var(--space-2);
}

.recommendation-row--actionable:hover,
.recommendation-row--actionable:focus-visible {
  background: var(--accent-subtle);
}

.recommendation-row--actionable:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.recommendation-arrow {
  align-self: center;
  color: var(--accent) !important;
  font-size: 1rem !important;
  font-weight: 700;
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
