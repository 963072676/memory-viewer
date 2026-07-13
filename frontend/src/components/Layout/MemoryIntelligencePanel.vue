<template>
  <section class="intelligence-panel">
    <div class="panel-header">
      <div>
        <h3>{{ $t('i18n.intelligence_title') }}</h3>
        <div class="panel-meta">
          <span>{{ $t('i18n.intelligence_memory_count', { count: summary?.memoryCount ?? 0 }) }}</span>
          <span>{{ providerLabel }}</span>
          <span>{{ sessionStore.activeSessionId || $t('i18n.intelligence_all_sessions') }}</span>
        </div>
      </div>
      <div class="panel-actions">
        <label class="compression-control">
          <span>{{ $t('i18n.intelligence_max_chars') }}</span>
          <input
            v-model.number="compressionMaxChars"
            class="compression-input"
            type="number"
            min="120"
            max="4000"
            step="100"
            :disabled="compressing"
          />
        </label>
        <button class="action-btn" type="button" :disabled="loading" @click="loadAll">
          {{ loading ? $t('i18n.intelligence_refreshing') : $t('i18n.intelligence_refresh') }}
        </button>
        <button class="action-btn action-btn--accent" type="button" :disabled="compressing" @click="compress">
          {{ compressing ? $t('i18n.intelligence_compressing') : $t('i18n.intelligence_compress') }}
        </button>
      </div>
    </div>

    <div v-if="loading && !summary" class="panel-state">{{ $t('i18n.intelligence_loading') }}</div>
    <div v-else-if="error" class="panel-state panel-state--error">
      <p>{{ error }}</p>
      <button class="action-btn" type="button" @click="loadAll">{{ $t('i18n.retry') }}</button>
    </div>

    <template v-else>
      <div class="intelligence-stats">
        <div class="stat-tile">
          <span class="stat-label">{{ $t('i18n.intelligence_keywords') }}</span>
          <strong>{{ summary?.keywords?.length ?? 0 }}</strong>
        </div>
        <div class="stat-tile">
          <span class="stat-label">{{ $t('i18n.intelligence_tags') }}</span>
          <strong>{{ summary?.tagInsights?.length ?? summary?.topTags?.length ?? 0 }}</strong>
        </div>
        <div class="stat-tile">
          <span class="stat-label">{{ $t('i18n.intelligence_clusters') }}</span>
          <strong>{{ clusters?.total ?? 0 }}</strong>
        </div>
        <div class="stat-tile">
          <span class="stat-label">{{ $t('i18n.intelligence_contradictions') }}</span>
          <strong>{{ contradictions?.total ?? 0 }}</strong>
        </div>
        <div class="stat-tile">
          <span class="stat-label">{{ $t('i18n.intelligence_compressed') }}</span>
          <strong>{{ compression?.compressedCount ?? 0 }}</strong>
        </div>
      </div>

      <div class="intelligence-layout">
        <div id="memory-intelligence-summary" class="intelligence-block" tabindex="-1">
          <div class="block-title">{{ $t('i18n.intelligence_summary') }}</div>
          <p class="summary-text">{{ summary?.summary || $t('i18n.intelligence_no_memories') }}</p>
          <div class="keyword-row">
            <span v-for="keyword in keywords" :key="keyword" class="keyword-chip">{{ keyword }}</span>
          </div>
        </div>

        <div id="memory-intelligence-tags" class="intelligence-block" tabindex="-1">
          <div class="block-title">{{ $t('i18n.intelligence_top_tags') }}</div>
          <div v-if="!topTags.length" class="empty-line">{{ $t('i18n.intelligence_no_tags') }}</div>
          <div v-else class="tag-insight-list" :aria-label="$t('i18n.intelligence_top_tags')">
            <div v-for="(insight, index) in topTags" :key="insight.tag" class="tag-insight">
              <button
                class="tag-insight__toggle"
                type="button"
                :aria-expanded="expandedTag === insight.tag"
                :aria-controls="`intelligence-tag-${index}`"
                :aria-label="$t('i18n.intelligence_explore_tag', {
                  tag: insight.tag,
                  count: insight.count,
                })"
                @click="toggleTag(insight.tag)"
              >
                <span class="tag-insight__identity">
                  <span class="tag-rank">{{ index + 1 }}</span>
                  <span class="tag-insight__text">
                    <strong>{{ insight.tag }}</strong>
                    <span>{{ insight.providers.join(', ') }}</span>
                  </span>
                </span>
                <span class="cluster-actions">
                  <span class="count-badge">{{ insight.count }}</span>
                  <span
                    class="cluster-chevron"
                    :class="{ 'cluster-chevron--open': expandedTag === insight.tag }"
                    aria-hidden="true"
                  >›</span>
                </span>
              </button>

              <div
                v-if="expandedTag === insight.tag"
                :id="`intelligence-tag-${index}`"
                class="cluster-members tag-members"
              >
                <div class="cluster-members__meta">
                  {{ $t('i18n.intelligence_tag_members', {
                    shown: insight.memories.length,
                    count: insight.count,
                  }) }}
                </div>
                <RouterLink
                  v-for="memory in insight.memories"
                  :key="`${memory.provider}-${memory.id}`"
                  class="cluster-member"
                  :to="{
                    name: 'memory-detail',
                    params: { id: memory.id },
                    query: { source: memory.provider },
                  }"
                  :aria-label="$t('i18n.intelligence_open_memory', { title: memory.title })"
                >
                  <span class="cluster-member__body">
                    <strong>{{ memory.title }}</strong>
                    <span>{{ memory.content }}</span>
                  </span>
                  <span class="cluster-member__provider">{{ memory.provider }}</span>
                  <span class="cluster-member__arrow" aria-hidden="true">→</span>
                </RouterLink>
              </div>
            </div>
          </div>
        </div>

        <div class="intelligence-block">
          <div class="block-heading">
            <div class="block-title">{{ $t('i18n.intelligence_compression') }}</div>
            <span v-if="compression" class="compression-limit">
              {{ $t('i18n.intelligence_max_chars_applied', { count: compression.maxChars }) }}
            </span>
          </div>
          <p class="compressed-text">{{ compression?.compressed || summary?.summary || $t('i18n.intelligence_no_compression') }}</p>
        </div>

        <div id="memory-intelligence-clusters" class="intelligence-block" tabindex="-1">
          <div class="block-title">{{ $t('i18n.intelligence_clusters') }}</div>
          <div v-if="!clusters?.clusters.length" class="empty-line">{{ $t('i18n.intelligence_no_clusters') }}</div>
          <div v-else class="cluster-list">
            <div v-for="cluster in clusters.clusters" :key="cluster.id" class="cluster-item">
              <button
                class="cluster-row"
                type="button"
                :aria-expanded="expandedClusterId === cluster.id"
                :aria-controls="`intelligence-${cluster.id}`"
                @click="toggleCluster(cluster.id)"
              >
                <span class="cluster-heading">
                  <strong>{{ cluster.name }}</strong>
                  <span>{{ cluster.providers.join(', ') }}</span>
                </span>
                <span class="cluster-actions">
                  <span class="count-badge">{{ cluster.count }}</span>
                  <span
                    class="cluster-chevron"
                    :class="{ 'cluster-chevron--open': expandedClusterId === cluster.id }"
                    aria-hidden="true"
                  >›</span>
                </span>
              </button>

              <div
                v-if="expandedClusterId === cluster.id"
                :id="`intelligence-${cluster.id}`"
                class="cluster-members"
              >
                <div class="cluster-members__meta">
                  {{ $t('i18n.intelligence_cluster_members', { count: cluster.members.length }) }}
                </div>
                <RouterLink
                  v-for="member in cluster.members"
                  :key="`${member.provider}-${member.id}`"
                  class="cluster-member"
                  :to="{
                    name: 'memory-detail',
                    params: { id: member.id },
                    query: { source: member.provider },
                  }"
                  :aria-label="$t('i18n.intelligence_open_memory', { title: member.title })"
                >
                  <span class="cluster-member__body">
                    <strong>{{ member.title }}</strong>
                    <span>{{ member.content }}</span>
                  </span>
                  <span class="cluster-member__provider">{{ member.provider }}</span>
                  <span class="cluster-member__arrow" aria-hidden="true">→</span>
                </RouterLink>
              </div>
            </div>
          </div>
        </div>

        <div id="memory-intelligence-contradictions" class="intelligence-block intelligence-block--wide" tabindex="-1">
          <div class="block-title">{{ $t('i18n.intelligence_contradictions') }}</div>
          <div v-if="!contradictions?.contradictions.length" class="empty-line">{{ $t('i18n.intelligence_no_contradictions') }}</div>
          <div v-else class="contradiction-list">
            <div
              v-for="item in contradictions.contradictions"
              :key="item.id"
              class="contradiction-item"
              :class="`contradiction-item--${item.severity}`"
            >
              <button
                class="contradiction-row"
                type="button"
                :aria-expanded="expandedContradictionId === item.id"
                :aria-controls="`intelligence-${item.id}`"
                :aria-label="$t('i18n.intelligence_review_pair', {
                  first: item.memoryA.title,
                  second: item.memoryB.title,
                })"
                @click="toggleContradiction(item.id)"
              >
                <span class="contradiction-heading">
                  <span class="severity-pill" :class="`severity-pill--${item.severity}`">
                    {{ severityLabel(item.severity) }}
                  </span>
                  <span class="contradiction-terms">{{ item.sharedTerms.slice(0, 4).join(', ') }}</span>
                </span>
                <span
                  class="cluster-chevron"
                  :class="{ 'cluster-chevron--open': expandedContradictionId === item.id }"
                  aria-hidden="true"
                >›</span>
              </button>

              <div
                v-if="expandedContradictionId === item.id"
                :id="`intelligence-${item.id}`"
                class="contradiction-review"
              >
                <div class="shared-terms">
                  <span class="shared-terms__label">{{ $t('i18n.intelligence_shared_terms') }}</span>
                  <span class="shared-terms__chips">
                    <span v-for="term in item.sharedTerms" :key="term" class="keyword-chip">{{ term }}</span>
                  </span>
                </div>

                <div class="contradiction-pair">
                  <RouterLink
                    class="contradiction-memory"
                    :to="{
                      name: 'memory-detail',
                      params: { id: item.memoryA.id },
                      query: { source: item.memoryA.provider },
                    }"
                    :aria-label="$t('i18n.intelligence_open_memory', { title: item.memoryA.title })"
                  >
                    <span class="contradiction-memory__meta">
                      <span>{{ $t('i18n.intelligence_memory_a') }}</span>
                      <span class="provider-chip">{{ item.memoryA.provider }}</span>
                    </span>
                    <strong>{{ item.memoryA.title }}</strong>
                    <span class="contradiction-memory__content">{{ item.memoryA.content }}</span>
                    <span class="contradiction-memory__arrow" aria-hidden="true">→</span>
                  </RouterLink>

                  <RouterLink
                    class="contradiction-memory"
                    :to="{
                      name: 'memory-detail',
                      params: { id: item.memoryB.id },
                      query: { source: item.memoryB.provider },
                    }"
                    :aria-label="$t('i18n.intelligence_open_memory', { title: item.memoryB.title })"
                  >
                    <span class="contradiction-memory__meta">
                      <span>{{ $t('i18n.intelligence_memory_b') }}</span>
                      <span class="provider-chip">{{ item.memoryB.provider }}</span>
                    </span>
                    <strong>{{ item.memoryB.title }}</strong>
                    <span class="contradiction-memory__content">{{ item.memoryB.content }}</span>
                    <span class="contradiction-memory__arrow" aria-hidden="true">→</span>
                  </RouterLink>
                </div>

                <div class="review-caption">{{ $t('i18n.intelligence_candidate_review') }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
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
const { t } = useI18n()
const summary = ref<IntelligenceSummary | null>(null)
const compression = ref<IntelligenceCompression | null>(null)
const clusters = ref<IntelligenceClusters | null>(null)
const contradictions = ref<IntelligenceContradictions | null>(null)
const loading = ref(false)
const compressing = ref(false)
const compressionMaxChars = ref<number | string>(700)
const error = ref<string | null>(null)
const expandedTag = ref<string | null>(null)
const expandedClusterId = ref<string | null>(null)
const expandedContradictionId = ref<string | null>(null)

const providerLabel = computed(() => (
  summary.value?.providers?.length ? summary.value.providers.join(', ') : t('i18n.intelligence_all_providers')
))
const sessionParam = computed(() => sessionStore.activeSessionId || undefined)
const keywords = computed(() => summary.value?.keywords?.slice(0, 8) || [])
const topTags = computed(() => summary.value?.tagInsights?.slice(0, 10) || [])

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
    if (expandedTag.value && !nextSummary.tagInsights?.some(insight => insight.tag === expandedTag.value)) {
      expandedTag.value = null
    }
    if (expandedClusterId.value && !nextClusters.clusters.some(cluster => cluster.id === expandedClusterId.value)) {
      expandedClusterId.value = null
    }
    if (
      expandedContradictionId.value
      && !nextContradictions.contradictions.some(item => item.id === expandedContradictionId.value)
    ) {
      expandedContradictionId.value = null
    }
  } catch (e: any) {
    error.value = e?.message || t('i18n.intelligence_load_failed')
  } finally {
    loading.value = false
  }
}

async function compress() {
  const parsedMaxChars = Number(compressionMaxChars.value)
  const normalizedMaxChars = compressionMaxChars.value === '' || !Number.isFinite(parsedMaxChars)
    ? 700
    : Math.min(4000, Math.max(120, Math.round(parsedMaxChars)))
  compressionMaxChars.value = normalizedMaxChars
  compressing.value = true
  error.value = null
  try {
    compression.value = await compressIntelligenceMemories({
      sessionId: sessionParam.value,
      limit: 200,
      maxChars: normalizedMaxChars,
    })
  } catch (e: any) {
    error.value = e?.message || t('i18n.intelligence_compress_failed')
  } finally {
    compressing.value = false
  }
}

function toggleCluster(clusterId: string) {
  expandedClusterId.value = expandedClusterId.value === clusterId ? null : clusterId
}

function toggleTag(tag: string) {
  expandedTag.value = expandedTag.value === tag ? null : tag
}

function toggleContradiction(contradictionId: string) {
  expandedContradictionId.value = expandedContradictionId.value === contradictionId ? null : contradictionId
}

function severityLabel(severity: string) {
  const key = ['low', 'medium', 'high'].includes(severity) ? severity : 'unknown'
  return t(`i18n.intelligence_severity_${key}`)
}

onMounted(() => {
  loadAll()
})

watch(() => sessionStore.activeSessionId, () => {
  compression.value = null
  expandedTag.value = null
  expandedClusterId.value = null
  expandedContradictionId.value = null
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

.compression-control {
  display: grid;
  gap: 4px;
  color: var(--text-secondary);
  font-size: 0.72rem;
  font-weight: 600;
}

.compression-input {
  width: 108px;
  min-height: 36px;
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--card);
  color: var(--primary);
  font-size: 0.82rem;
}

.compression-input:focus {
  border-color: var(--accent);
  outline: none;
  box-shadow: 0 0 0 4px var(--accent-glow);
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
  scroll-margin-top: 88px;
}

.intelligence-block:focus {
  outline: 2px solid var(--accent);
  outline-offset: 3px;
}

.intelligence-block--wide {
  grid-column: 1 / -1;
}

.block-title {
  margin-bottom: var(--space-3);
  color: var(--primary);
  font-size: 0.88rem;
  font-weight: 700;
}

.block-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.block-heading .block-title {
  margin-bottom: 0;
}

.compression-limit {
  flex: 0 0 auto;
  padding: 3px 7px;
  border-radius: var(--radius-sm);
  background: var(--tag-bg);
  color: var(--text-secondary);
  font-size: 0.7rem;
  font-weight: 600;
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
.tag-chip,
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

.tag-rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: var(--radius-sm);
  background: var(--card);
  color: var(--text-secondary);
  font-family: var(--font-mono);
  font-size: 0.68rem;
  line-height: 1;
}

.tag-insight-list {
  display: flex;
  max-height: 420px;
  flex-direction: column;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.tag-insight {
  border-top: 1px solid var(--border);
}

.tag-insight:first-child {
  border-top: none;
}

.tag-insight__toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  min-height: 42px;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font: inherit;
  text-align: left;
}

.tag-insight__toggle:hover .tag-insight__text strong,
.tag-insight__toggle:focus-visible .tag-insight__text strong {
  color: var(--accent);
}

.tag-insight__toggle:focus-visible {
  border-radius: var(--radius-sm);
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}

.tag-insight__identity {
  display: flex;
  align-items: center;
  min-width: 0;
  gap: var(--space-2);
}

.tag-insight__text,
.tag-insight__text strong,
.tag-insight__text span {
  display: block;
}

.tag-insight__text {
  min-width: 0;
}

.tag-insight__text strong,
.tag-insight__text span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-insight__text strong {
  color: var(--primary);
  font-size: 0.8rem;
  transition: color 0.15s ease;
}

.tag-insight__text span {
  color: var(--text-secondary);
  font-size: 0.7rem;
}

.tag-members {
  border-left-color: var(--type-preference-text);
}

.cluster-list,
.contradiction-list {
  display: flex;
  flex-direction: column;
}

.cluster-list {
  max-height: 520px;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.contradiction-list {
  max-height: 620px;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.cluster-item,
.contradiction-item {
  border-top: 1px solid var(--border);
}

.cluster-item:first-child,
.contradiction-item:first-child {
  border-top: none;
}

.cluster-row,
.contradiction-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  min-height: 42px;
  padding: var(--space-2) 0;
}

.cluster-row,
.contradiction-row {
  width: 100%;
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font: inherit;
  text-align: left;
}

.cluster-row:hover .cluster-heading strong,
.cluster-row:focus-visible .cluster-heading strong,
.contradiction-row:hover .contradiction-terms,
.contradiction-row:focus-visible .contradiction-terms {
  color: var(--accent);
}

.cluster-row:focus-visible,
.contradiction-row:focus-visible {
  border-radius: var(--radius-sm);
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}

.cluster-heading,
.cluster-heading strong,
.cluster-heading span {
  display: block;
}

.cluster-heading {
  min-width: 0;
}

.cluster-heading strong {
  color: var(--primary);
  font-size: 0.84rem;
  transition: color 0.15s ease;
}

.cluster-heading span {
  color: var(--text-secondary);
  font-size: 0.76rem;
}

.cluster-actions {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
  gap: var(--space-2);
}

.count-badge {
  background: var(--tag-bg);
  color: var(--primary);
}

.cluster-chevron {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  overflow: hidden;
  color: var(--text-secondary);
  font-size: 1.25rem;
  line-height: 1;
  transform: rotate(0deg);
  transition: transform 0.15s ease;
}

.cluster-chevron--open {
  transform: rotate(90deg);
}

.cluster-members {
  margin: 0 0 var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-left: 2px solid var(--accent);
  background: var(--bg);
}

.cluster-members__meta {
  margin-bottom: var(--space-1);
  color: var(--text-tertiary);
  font-size: 0.72rem;
  font-weight: 600;
}

.cluster-member {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto 16px;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) 0;
  color: inherit;
  text-decoration: none;
}

.cluster-member + .cluster-member {
  border-top: 1px solid var(--border);
}

.cluster-member:hover .cluster-member__body strong,
.cluster-member:focus-visible .cluster-member__body strong {
  color: var(--accent);
}

.cluster-member:focus-visible {
  border-radius: var(--radius-sm);
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.cluster-member__body {
  min-width: 0;
}

.cluster-member__body strong,
.cluster-member__body span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cluster-member__body strong {
  color: var(--primary);
  font-size: 0.8rem;
  transition: color 0.15s ease;
}

.cluster-member__body span,
.cluster-member__provider {
  color: var(--text-secondary);
  font-size: 0.72rem;
}

.cluster-member__provider {
  max-width: 110px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cluster-member__arrow {
  color: var(--accent);
  font-size: 0.85rem;
}

.contradiction-heading {
  display: flex;
  align-items: center;
  min-width: 0;
  gap: var(--space-2);
}

.contradiction-terms {
  min-width: 0;
  overflow: hidden;
  color: var(--text-secondary);
  font-size: 0.78rem;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 0.15s ease;
}

.severity-pill--low {
  background: var(--tag-bg);
  color: var(--text-secondary);
}

.severity-pill--medium {
  background: var(--warn-bg);
  color: var(--warn-text);
}

.severity-pill--high {
  background: var(--error-bg);
  color: var(--error-text);
}

.contradiction-review {
  margin: 0 0 var(--space-3);
  padding: var(--space-3);
  border-left: 2px solid var(--warn-text);
  background: var(--bg);
}

.contradiction-item--low .contradiction-review {
  border-left-color: var(--text-tertiary);
}

.contradiction-item--high .contradiction-review {
  border-left-color: var(--error-text);
}

.shared-terms {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.shared-terms__label {
  flex-shrink: 0;
  padding-top: 3px;
  color: var(--text-tertiary);
  font-size: 0.72rem;
  font-weight: 600;
}

.shared-terms__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
}

.shared-terms .keyword-chip {
  min-height: 20px;
  padding: 1px 6px;
  font-size: 0.68rem;
}

.contradiction-pair {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.contradiction-memory {
  position: relative;
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-3);
  color: inherit;
  text-decoration: none;
}

.contradiction-memory + .contradiction-memory {
  border-left: 1px solid var(--border);
}

.contradiction-memory:hover strong,
.contradiction-memory:focus-visible strong {
  color: var(--accent);
}

.contradiction-memory:focus-visible {
  border-radius: var(--radius-sm);
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}

.contradiction-memory__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  color: var(--text-tertiary);
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
}

.provider-chip {
  max-width: 120px;
  overflow: hidden;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  background: var(--tag-bg);
  color: var(--text-secondary);
  font-size: 0.66rem;
  text-overflow: ellipsis;
  text-transform: none;
  white-space: nowrap;
}

.contradiction-memory strong {
  padding-right: var(--space-4);
  overflow: hidden;
  color: var(--primary);
  font-size: 0.8rem;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 0.15s ease;
}

.contradiction-memory__content {
  display: -webkit-box;
  overflow: hidden;
  color: var(--text-secondary);
  font-size: 0.74rem;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.contradiction-memory__arrow {
  position: absolute;
  top: 42px;
  right: var(--space-3);
  color: var(--accent);
  font-size: 0.85rem;
}

.review-caption {
  margin-top: var(--space-2);
  color: var(--text-tertiary);
  font-size: 0.68rem;
  text-align: center;
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

  .compression-input {
    width: 100%;
  }

  .cluster-member {
    grid-template-columns: minmax(0, 1fr) 16px;
  }

  .cluster-member__provider {
    display: none;
  }

  .shared-terms {
    flex-direction: column;
  }

  .contradiction-pair {
    grid-template-columns: 1fr;
  }

  .contradiction-memory + .contradiction-memory {
    border-top: 1px solid var(--border);
    border-left: 0;
  }
}
</style>
