<template>
  <section class="intelligence-panel">
    <div class="panel-header">
      <div>
        <h3>Memory Intelligence</h3>
        <div class="panel-meta">
          <span>{{ summary?.memoryCount ?? 0 }} memories</span>
          <span>{{ providerLabel }}</span>
          <span>{{ sessionStore.activeSessionId || 'all sessions' }}</span>
        </div>
      </div>
      <div class="panel-actions">
        <button class="action-btn" type="button" :disabled="loading" @click="loadAll">
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
        <button class="action-btn action-btn--accent" type="button" :disabled="compressing" @click="compress">
          {{ compressing ? 'Compressing...' : 'Compress' }}
        </button>
      </div>
    </div>

    <div v-if="loading && !summary" class="panel-state">Loading intelligence...</div>
    <div v-else-if="error" class="panel-state panel-state--error">
      <p>{{ error }}</p>
      <button class="action-btn" type="button" @click="loadAll">Retry</button>
    </div>

    <template v-else>
      <div class="intelligence-stats">
        <div class="stat-tile">
          <span class="stat-label">Keywords</span>
          <strong>{{ summary?.keywords.length ?? 0 }}</strong>
        </div>
        <div class="stat-tile">
          <span class="stat-label">Clusters</span>
          <strong>{{ clusters?.total ?? 0 }}</strong>
        </div>
        <div class="stat-tile">
          <span class="stat-label">Contradictions</span>
          <strong>{{ contradictions?.total ?? 0 }}</strong>
        </div>
        <div class="stat-tile">
          <span class="stat-label">Compressed</span>
          <strong>{{ compression?.compressedCount ?? 0 }}</strong>
        </div>
      </div>

      <div class="intelligence-layout">
        <div class="intelligence-block">
          <div class="block-title">Summary</div>
          <p class="summary-text">{{ summary?.summary || 'No memories available.' }}</p>
          <div class="keyword-row">
            <span v-for="keyword in keywords" :key="keyword" class="keyword-chip">{{ keyword }}</span>
          </div>
        </div>

        <div class="intelligence-block">
          <div class="block-title">Compression</div>
          <p class="compressed-text">{{ compression?.compressed || summary?.summary || 'No compressed memory yet.' }}</p>
        </div>

        <div class="intelligence-block">
          <div class="block-title">Clusters</div>
          <div v-if="!clusters?.clusters.length" class="empty-line">No clusters yet.</div>
          <div v-else class="cluster-list">
            <div v-for="cluster in clusters.clusters.slice(0, 5)" :key="cluster.id" class="cluster-row">
              <div>
                <strong>{{ cluster.name }}</strong>
                <span>{{ cluster.providers.join(', ') }}</span>
              </div>
              <span class="count-badge">{{ cluster.count }}</span>
            </div>
          </div>
        </div>

        <div class="intelligence-block">
          <div class="block-title">Contradictions</div>
          <div v-if="!contradictions?.contradictions.length" class="empty-line">None detected.</div>
          <div v-else class="contradiction-list">
            <div
              v-for="item in contradictions.contradictions.slice(0, 3)"
              :key="item.id"
              class="contradiction-row"
            >
              <span class="severity-pill">{{ item.severity }}</span>
              <span>{{ item.sharedTerms.slice(0, 4).join(', ') }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  compressIntelligenceMemories,
  fetchIntelligenceClusters,
  fetchIntelligenceContradictions,
  fetchIntelligenceSummary,
  type IntelligenceClusters,
  type IntelligenceCompression,
  type IntelligenceContradictions,
  type IntelligenceSummary,
} from '@/api/intelligence'
import { useSessionStore } from '@/stores/sessions'

const sessionStore = useSessionStore()
const summary = ref<IntelligenceSummary | null>(null)
const compression = ref<IntelligenceCompression | null>(null)
const clusters = ref<IntelligenceClusters | null>(null)
const contradictions = ref<IntelligenceContradictions | null>(null)
const loading = ref(false)
const compressing = ref(false)
const error = ref<string | null>(null)

const providerLabel = computed(() => (
  summary.value?.providers.length ? summary.value.providers.join(', ') : 'all providers'
))
const sessionParam = computed(() => sessionStore.activeSessionId || undefined)
const keywords = computed(() => summary.value?.keywords.slice(0, 8) || [])

async function loadAll() {
  loading.value = true
  error.value = null
  try {
    const [nextSummary, nextClusters, nextContradictions] = await Promise.all([
      fetchIntelligenceSummary({ sessionId: sessionParam.value, limit: 200 }),
      fetchIntelligenceClusters({ sessionId: sessionParam.value, limit: 200 }),
      fetchIntelligenceContradictions({ sessionId: sessionParam.value, limit: 200 }),
    ])
    summary.value = nextSummary
    clusters.value = nextClusters
    contradictions.value = nextContradictions
  } catch (e: any) {
    error.value = e?.message || 'Failed to load memory intelligence'
  } finally {
    loading.value = false
  }
}

async function compress() {
  compressing.value = true
  error.value = null
  try {
    compression.value = await compressIntelligenceMemories({
      sessionId: sessionParam.value,
      limit: 200,
      maxChars: 700,
    })
  } catch (e: any) {
    error.value = e?.message || 'Failed to compress memories'
  } finally {
    compressing.value = false
  }
}

onMounted(() => {
  loadAll()
})

watch(() => sessionStore.activeSessionId, () => {
  compression.value = null
  loadAll()
})
</script>

<style scoped>
.intelligence-panel {
  margin-bottom: var(--space-7);
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.panel-header h3 {
  color: var(--primary);
  font-size: 1rem;
  font-weight: 700;
  margin: 0;
}

.panel-meta,
.panel-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.panel-meta {
  margin-top: var(--space-2);
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.panel-state {
  padding: var(--space-7);
  border: 1px dashed var(--border);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  text-align: center;
}

.panel-state--error {
  color: var(--error-text);
}

.intelligence-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.stat-tile,
.intelligence-block {
  background: var(--card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow);
}

.stat-tile {
  min-height: 82px;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.stat-tile strong {
  color: var(--primary);
  font-family: var(--font-mono);
  font-size: 1.45rem;
  line-height: 1;
}

.intelligence-layout {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
}

.intelligence-block {
  min-width: 0;
  padding: var(--space-5);
}

.block-title {
  margin-bottom: var(--space-3);
  color: var(--primary);
  font-size: 0.88rem;
  font-weight: 700;
}

.summary-text,
.compressed-text,
.empty-line {
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.6;
}

.compressed-text {
  max-height: 130px;
  overflow: auto;
}

.keyword-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-4);
}

.keyword-chip,
.count-badge,
.severity-pill {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 0.72rem;
  font-weight: 700;
}

.keyword-chip {
  background: var(--accent-subtle);
  color: var(--accent);
}

.cluster-list,
.contradiction-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.cluster-row,
.contradiction-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  min-height: 42px;
  padding: var(--space-2) 0;
  border-top: 1px solid var(--border);
}

.cluster-row:first-child,
.contradiction-row:first-child {
  border-top: none;
}

.cluster-row strong,
.cluster-row span {
  display: block;
}

.cluster-row strong {
  color: var(--primary);
  font-size: 0.84rem;
}

.cluster-row span {
  color: var(--text-secondary);
  font-size: 0.76rem;
}

.count-badge {
  background: var(--tag-bg);
  color: var(--primary);
}

.severity-pill {
  background: var(--warn-bg);
  color: var(--warn-text);
  text-transform: uppercase;
}

.action-btn--accent {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--card);
}

@media (max-width: 767px) {
  .panel-header,
  .panel-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .intelligence-layout {
    grid-template-columns: 1fr;
  }
}
</style>
