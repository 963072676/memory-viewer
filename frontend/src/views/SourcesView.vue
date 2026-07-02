<template>
  <div class="sources-view">
    <div class="view-header">
      <h2 class="section-title">🔌 {{ $t('i18n.source_management') }}</h2>
      <button class="action-btn" @click="loadSources" :disabled="loading">
        {{ loading ? '加载中...' : '刷新' }}
      </button>
    </div>

    <div v-if="loading && sources.length === 0" class="loading">加载中...</div>

    <div v-else-if="loadError" class="error-state">
      <p>⚠️ {{ $t('i18n.load_failed') }}，点击{{ $t('i18n.retry') }}</p>
      <button class="action-btn" @click="loadSources">{{ $t('i18n.retry') }}</button>
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
      <div class="sources-grid">
        <div
          v-for="source in sources"
          :key="source.name"
          class="source-card"
          :class="{ expanded: expandedSources.has(source.name), disabled: !source.enabled }"
        >
          <div class="source-header" @click="toggleExpand(source.name)">
            <div class="source-info">
              <div class="source-title">
                <span class="health-dot" :class="source.healthy ? 'healthy' : 'unhealthy'"></span>
                <span class="source-name">{{ source.name }}</span>
                <span class="source-type-badge">{{ source.type }}</span>
              </div>
              <div class="source-meta">
                <span class="memory-count">{{ source.count }} 条记忆</span>
                <span
                  class="enabled-badge"
                  :class="source.enabled ? 'enabled' : 'disabled'"
                >{{ source.enabled ? $t('i18n.enabled') : $t('i18n.disabled') }}</span>
              </div>
            </div>
            <span class="expand-icon">{{ expandedSources.has(source.name) ? '▲' : '▼' }}</span>
          </div>

          <transition name="expand">
            <div v-if="expandedSources.has(source.name)" class="source-detail">
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
                <button class="action-btn action-btn--sm" @click.stop="viewSourceMemories(source.name)">
                  {{ $t('i18n.view_memory') }}
                </button>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <div v-if="sources.length === 0">
        <!-- P38 r30: EmptyState message prop 改 v-bind -->
        <EmptyState icon="📭" :message="$t('i18n.registered_sources')" />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchSources, type SourceInfo } from '@/api/sources'
import EmptyState from '@/components/Layout/EmptyState.vue'

const router = useRouter()

const loading = ref(false)
const loadError = ref(false)
const sources = ref<SourceInfo[]>([])
const expandedSources = ref(new Set<string>())

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

function viewSourceMemories(name: string) {
  router.push({ path: '/', query: { source: name } })
}

async function loadSources() {
  loading.value = true
  loadError.value = false
  try {
    const res = await fetchSources()
    sources.value = res.sources
  } catch (e) {
    console.error('Failed to load sources:', e)
    loadError.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => loadSources())
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

/* P38 r21: button system unification — .action-btn + .action-btn--sm
   are global. Local rules removed. */

.loading {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.error-state {
  text-align: center;
  padding: 40px;
  color: var(--error-text, #ef4444);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
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
  border-color: var(--accent, #007aff);
}

.source-card.disabled {
  opacity: 0.6;
}

.source-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  cursor: pointer;
  user-select: none;
}

.source-header:hover {
  background: var(--tag-bg);
}

.source-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.source-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.source-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary);
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
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.health-dot.healthy {
  background: var(--success-text);
  /* P38 r17: 改 hardcoded rgba 阴影 → color-mix + 主题色, 让阴影跟随 dark/light 自动调亮.
     此前 0.4 alpha 固定值在 dark 背景上发光感很弱 (深绿 + alpha 模糊后几乎看不见).
     改 color-mix(in srgb, var(--success-text) 40%, transparent) 在 dark 模式下也保持"健康发光"质感. */
  box-shadow: 0 0 6px color-mix(in srgb, var(--success-text) 40%, transparent);
}

.health-dot.unhealthy {
  background: var(--error-text);
  box-shadow: 0 0 6px color-mix(in srgb, var(--error-text) 40%, transparent);
}

.expand-icon {
  font-size: 0.75rem;
  color: var(--text-secondary);
  flex-shrink: 0;
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
  max-height: 300px;
}

/* Responsive */
@media (max-width: 767px) {
  h2 {
    font-size: 1.2rem;
  }

  .view-header {
    flex-direction: column;
    align-items: flex-start;
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

  .detail-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
