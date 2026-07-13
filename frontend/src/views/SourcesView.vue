<template>
  <div class="sources-view" :aria-busy="loading">
    <div class="view-header">
      <h2 class="section-title">🔌 {{ $t('i18n.source_management') }}</h2>
      <button type="button" class="action-btn" :disabled="loading" @click="loadSources">
        <span class="refresh-icon" :class="{ spinning: loading }" aria-hidden="true">↻</span>
        {{ loading ? $t('i18n.source_loading') : $t('i18n.source_refresh') }}
      </button>
    </div>

    <div v-if="loading && sources.length === 0" class="loading-state" role="status" aria-live="polite">
      <span>{{ $t('i18n.source_loading') }}</span>
      <div class="summary-row loading-summary" aria-hidden="true">
        <div v-for="i in 4" :key="`summary-${i}`" class="summary-card skeleton-block"></div>
      </div>
      <div class="sources-grid" aria-hidden="true">
        <div v-for="i in 2" :key="`source-${i}`" class="source-card skeleton-source"></div>
      </div>
    </div>

    <div v-else-if="loadError" class="error-state" role="alert">
      <div class="error-copy">
        <strong>{{ $t('i18n.load_failed') }}</strong>
        <span>{{ $t('i18n.source_load_failed_message') }}</span>
      </div>
      <button type="button" class="action-btn" @click="loadSources">{{ $t('i18n.retry') }}</button>
    </div>

    <template v-else>
      <!-- Aggregate stats -->
      <div class="summary-row">
        <div class="summary-card">
          <div class="summary-value">{{ totalMemories }}</div>
          <div class="summary-label">{{ $t('i18n.total_memories') }}</div>
        </div>
        <div class="summary-card" :class="{ success: onlineCount > 0 }">
          <div class="summary-value">{{ onlineCount }}</div>
          <div class="summary-label">{{ $t('i18n.online_source') }}</div>
        </div>
        <div class="summary-card" :class="{ warn: offlineCount > 0 }">
          <div class="summary-value">{{ offlineCount }}</div>
          <div class="summary-label">{{ $t('i18n.offline_source') }}</div>
        </div>
        <div class="summary-card">
          <div class="summary-value">{{ sources.length }}</div>
          <div class="summary-label">{{ $t('i18n.total_registered') }}</div>
        </div>
      </div>

      <!-- Source cards -->
      <div class="sources-grid" role="list" :aria-label="$t('i18n.source_list_aria')">
        <article
          v-for="source in sources"
          :key="source.name"
          class="source-card"
          :class="{ expanded: expandedSources.has(source.name), disabled: !source.enabled }"
          role="listitem"
        >
          <button
            type="button"
            class="source-header"
            :aria-expanded="expandedSources.has(source.name)"
            :aria-controls="sourceDetailId(source.name)"
            :aria-label="$t(expandedSources.has(source.name) ? 'i18n.source_collapse' : 'i18n.source_expand', { name: source.name })"
            @click="toggleExpand(source.name)"
          >
            <div class="source-info">
              <div class="source-title">
                <span class="source-name">{{ source.name }}</span>
                <span class="source-type-badge">{{ source.type }}</span>
              </div>
              <div class="source-meta">
                <span class="memory-count">{{ $t('i18n.source_memory_count', { count: source.count }) }}</span>
                <span class="health-badge" :class="source.healthy ? 'healthy' : 'unhealthy'">
                  <span class="health-dot" aria-hidden="true"></span>
                  {{ source.healthy ? $t('i18n.healthy') : $t('i18n.unhealthy') }}
                </span>
                <span
                  class="enabled-badge"
                  :class="source.enabled ? 'enabled' : 'disabled'"
                >{{ source.enabled ? $t('i18n.enabled') : $t('i18n.disabled') }}</span>
              </div>
            </div>
            <span class="expand-icon" aria-hidden="true">⌄</span>
          </button>

          <transition name="expand">
            <div
              v-if="expandedSources.has(source.name)"
              :id="sourceDetailId(source.name)"
              class="source-detail"
              role="region"
              :aria-label="$t('i18n.source_details_aria', { name: source.name })"
            >
              <div class="detail-grid">
                <div class="detail-item">
                  <span class="detail-label">{{ $t('i18n.name') }}</span>
                  <span class="detail-value">{{ source.name }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">{{ $t('i18n.type') }}</span>
                  <span class="detail-value">{{ source.type }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">{{ $t('i18n.source.health') }}</span>
                  <span class="detail-value" :class="source.healthy ? 'text-success' : 'text-error'">
                    {{ source.healthy ? $t('i18n.healthy') : $t('i18n.unhealthy') }}
                  </span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">{{ $t('i18n.memory_count') }}</span>
                  <span class="detail-value">{{ source.count }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">{{ $t('i18n.source.enabled') }}</span>
                  <span class="detail-value" :class="source.enabled ? 'text-success' : 'text-muted'">
                    {{ source.enabled ? $t('i18n.enabled') : $t('i18n.disabled') }}
                  </span>
                </div>
              </div>
              <div class="detail-actions">
                <button
                  type="button"
                  class="action-btn action-btn--primary action-btn--sm"
                  :aria-label="$t('i18n.source_open_memories', { name: source.name })"
                  @click="viewSourceMemories(source.name)"
                >
                  {{ $t('i18n.view_memory') }}
                </button>
              </div>
            </div>
          </transition>
        </article>
      </div>

      <div v-if="sources.length === 0">
        <EmptyState
          icon="📭"
          :title="$t('i18n.source_empty_title')"
          :message="$t('i18n.source_empty_message')"
          :action-text="$t('i18n.source_refresh')"
          @action="loadSources"
        />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchSources, type SourceInfo } from '@/api/sources'
import EmptyState from '@/components/Layout/EmptyState.vue'

const router = useRouter()

const loading = ref(false)
const loadError = ref(false)
const sources = ref<SourceInfo[]>([])
const expandedSources = ref(new Set<string>())
let loadRequestId = 0

const totalMemories = computed(() => sources.value.reduce((sum, s) => sum + s.count, 0))
const onlineCount = computed(() => sources.value.filter(s => s.healthy && s.enabled).length)
const offlineCount = computed(() => sources.value.filter(s => !s.healthy || !s.enabled).length)

function toggleExpand(name: string) {
  const s = new Set(expandedSources.value)
  if (s.has(name)) {
    s.delete(name)
  } else {
    s.add(name)
  }
  expandedSources.value = s
}

function sourceDetailId(name: string) {
  return `source-detail-${name.replace(/[^a-zA-Z0-9_-]/g, '-')}`
}

function viewSourceMemories(name: string) {
  router.push({ path: '/', query: { source: name } })
}

async function loadSources() {
  const requestId = ++loadRequestId
  loading.value = true
  loadError.value = false
  try {
    const res = await fetchSources()
    if (requestId !== loadRequestId) return
    sources.value = res.sources
    const names = new Set(res.sources.map(source => source.name))
    expandedSources.value = new Set([...expandedSources.value].filter(name => names.has(name)))
  } catch (e) {
    if (requestId !== loadRequestId) return
    console.error('Failed to load sources:', e)
    loadError.value = true
  } finally {
    if (requestId === loadRequestId) loading.value = false
  }
}

onMounted(() => loadSources())
onUnmounted(() => { loadRequestId++ })
</script>

<style scoped>
.sources-view {
  padding-bottom: 40px;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary);
}

/* P38 r20: section-title 左侧 3px accent bar — 与全站其他 view 同源 (r15 模式). */
h2.section-title { position: relative; padding-left: 12px; }
h2.section-title::before { content: ''; position: absolute; left: 0; top: 50%; transform: translateY(-50%); width: 3px; height: 60%; background: var(--accent); border-radius: 0 2px 2px 0; }

.refresh-icon {
  display: inline-block;
  line-height: 1;
}

.refresh-icon.spinning {
  animation: source-spin 0.8s linear infinite;
}

.loading-state {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px 0;
  color: var(--text-secondary);
}

.loading-summary {
  margin-bottom: 0;
}

.skeleton-block,
.skeleton-source {
  border-color: transparent;
  background: linear-gradient(90deg, var(--tag-bg) 25%, var(--border) 50%, var(--tag-bg) 75%);
  background-size: 200% 100%;
  animation: source-shimmer 1.4s ease-in-out infinite;
}

.skeleton-block {
  height: 92px;
}

.skeleton-source {
  height: 92px;
}

.error-state {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px;
  border: 1px solid var(--error-border);
  border-radius: var(--radius);
  background: var(--error-bg);
}

.error-copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 4px;
  color: var(--error);
}

.error-copy span {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

/* Summary cards */
.summary-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 32px;
}

.summary-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  text-align: center;
}

.summary-card.success {
  border-color: var(--success-text, #22c55e);
}

.summary-card.warn {
  border-color: var(--error-text, #ef4444);
}

.summary-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary);
}

.summary-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* Source cards grid */
.sources-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.source-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  transition: border-color 0.2s;
}

.source-card:hover {
  border-color: var(--border-strong);
}

.source-card.disabled {
  border-style: dashed;
}

.source-header {
  display: flex;
  width: 100%;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font: inherit;
  text-align: left;
  user-select: none;
}

.source-header:hover {
  background: var(--tag-bg);
}

.source-header:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}

.source-info {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 8px;
}

.source-title {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.source-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary);
  overflow-wrap: anywhere;
}

.source-type-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 6px;
  background: var(--tag-bg);
  color: var(--text-secondary);
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  border: 1px solid var(--border);
}

.source-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.memory-count {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.enabled-badge {
  display: inline-flex;
  align-items: center;
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.health-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--tag-bg);
  font-size: 0.7rem;
  font-weight: 600;
}

.health-badge.healthy {
  border-color: color-mix(in srgb, var(--success-text) 18%, transparent);
  background: var(--success-bg);
  color: var(--success-text);
}

.health-badge.unhealthy {
  border-color: var(--error-border);
  background: var(--error-bg);
  color: var(--error);
}

.enabled-badge.enabled {
  /* P38 r17: 改 hardcoded rgba(34, 197, 94, 0.1) → var(--success-bg).
     此前是 P44 漏网: dark 模式 --success-bg = #1b3a1b (深绿), 但 hardcoded rgba 不会跟随主题,
     导致 dark 模式 enabled badge 仍是浅绿底 (alpha 0.1) + 浅绿文字, 与 dark 卡片背景对比度不足.
     改 token 后两套主题都走 --success-bg, 维持 light/dark 视觉一致性.
     P38 r19: 加 1px border (color-mix 18%) 与全站 badge 节奏统一 — r17 之前 enabled-badge 无 border
     是 P39 时代漏网 (dot 都没有), 现在补齐"6px radius + 1px border + uppercase + 600" 四件套,
     与 MemoryCard .card-type / HomeView .source-badge / SourcesView .source-type-badge 视觉同源. */
  background: var(--success-bg);
  color: var(--success-text);
  border: 1px solid color-mix(in srgb, var(--success-text) 18%, transparent);
}

.enabled-badge.disabled {
  /* P38 r17: 同步用 --tag-bg / --text-secondary token, 不再硬编码灰色 alpha.
     P38 r19: 加 1px border (var(--border) — disabled 不像 enabled 有独立 hue,
     用通用 border 即可), 与 .enabled-badge.enabled 视觉同构 (都有 border). */
  background: var(--tag-bg);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

/* Health dot */
.health-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
  background: currentColor;
}

.expand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  font-size: 1rem;
  color: var(--text-secondary);
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.source-card.expanded .expand-icon {
  transform: rotate(180deg);
}

/* Expanded detail */
.source-detail {
  border-top: 1px solid var(--border);
  padding: 16px;
  background: var(--bg);
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 0.7rem;
  color: var(--text-secondary);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 0.875rem;
  color: var(--primary);
  font-weight: 500;
}

.text-success {
  color: var(--success-text, #22c55e);
}

.text-error {
  color: var(--error-text, #ef4444);
}

.text-muted {
  color: var(--text-secondary);
}

.detail-actions {
  display: flex;
  gap: 8px;
}

/* Expand transition */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 480px;
}

@keyframes source-spin {
  to { transform: rotate(360deg); }
}

@keyframes source-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Responsive */
@media (max-width: 767px) {
  h2 {
    font-size: 1.2rem;
  }

  .view-header {
    flex-direction: column;
    align-items: stretch;
  }

  .summary-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .summary-value {
    font-size: 1.5rem;
  }

  .source-header {
    padding: 12px;
  }

  .error-state {
    align-items: stretch;
    flex-direction: column;
  }

  .detail-grid {
    grid-template-columns: 1fr 1fr;
  }

  .detail-actions .action-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
