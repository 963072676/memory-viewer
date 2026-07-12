<template>
  <aside v-if="detail" class="memory-preview" :aria-label="$t('i18n.preview_aria')">
    <div class="preview-header">
      <div class="preview-heading">
        <span class="preview-kicker">{{ detail.kicker }}</span>
        <h3>{{ detail.title }}</h3>
      </div>
      <button
        class="icon-btn"
        type="button"
        :aria-label="$t('i18n.close')"
        :title="$t('i18n.close')"
        @click="$emit('close')"
      >
        ×
      </button>
    </div>

    <div class="preview-meta" v-if="detail.meta.length">
      <span class="preview-type" :class="detail.typeClass">{{ detail.type }}</span>
      <span v-for="item in detail.meta" :key="item">{{ item }}</span>
    </div>

    <div class="preview-content">
      {{ detail.content }}
    </div>

    <div class="preview-section" v-if="detail.concepts.length">
      <span class="preview-label">{{ $t('i18n.concepts') }}</span>
      <div class="preview-chips">
        <span v-for="concept in detail.concepts.slice(0, 8)" :key="concept" class="preview-chip">
          {{ concept }}
        </span>
      </div>
    </div>

    <div class="preview-section" v-if="detail.tags.length">
      <span class="preview-label">{{ $t('i18n.intelligence_tags') }}</span>
      <div class="preview-chips">
        <span v-for="tag in detail.tags.slice(0, 8)" :key="tag" class="preview-chip">
          {{ tag }}
        </span>
      </div>
    </div>

    <dl class="preview-facts" v-if="detail.facts.length">
      <div v-for="fact in detail.facts" :key="fact.label">
        <dt>{{ fact.label }}</dt>
        <dd :title="fact.value">{{ fact.value }}</dd>
      </div>
    </dl>

    <router-link v-if="fullDetailPath" class="action-btn action-btn--primary preview-link" :to="fullDetailPath">
      {{ $t('i18n.preview_open_full_detail') }}
    </router-link>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AgentMemory } from '@/types'
import type { MemoryGraphNode } from '@/api/graph'
import type { UnifiedMemory } from '@/api/sources'

const props = withDefaults(defineProps<{
  memory?: AgentMemory | null
  graphNode?: MemoryGraphNode | null
  unifiedMemory?: UnifiedMemory | null
  graphConnectionCount?: number
}>(), {
  memory: null,
  graphNode: null,
  unifiedMemory: null,
  graphConnectionCount: 0,
})

defineEmits<{
  (e: 'close'): void
}>()

const { locale, t } = useI18n()

const detail = computed(() => {
  if (props.memory) {
    return {
      kicker: t('i18n.preview_detail_panel'),
      title: props.memory.title,
      type: props.memory.type,
      typeClass: `preview-type--${props.memory.type}`,
      content: props.memory.content,
      concepts: props.memory.concepts,
      tags: props.memory.tags || [],
      meta: [
        `${t('i18n.preview_strength')} ${strengthPercent(props.memory.strength)}%`,
        ...(props.memory.sessionIds?.length ? [props.memory.sessionIds.slice(0, 2).join(', ')] : []),
        ...(props.memory.archived ? [t('i18n.archived')] : []),
      ],
      facts: [
        { label: t('en_created'), value: formatDate(props.memory.createdAt) },
        { label: t('en_updated'), value: formatDate(props.memory.updatedAt) },
        { label: t('en_version'), value: String(props.memory.version || 1) },
      ],
    }
  }

  if (props.unifiedMemory) {
    const memory = props.unifiedMemory
    return {
      kicker: t('i18n.preview_unified_memory'),
      title: memory.title,
      type: memory.type || t('i18n.preview_unknown'),
      typeClass: `preview-type--${memory.type || 'unknown'}`,
      content: memory.content || t('i18n.preview_no_content'),
      concepts: memory.concepts || [],
      tags: stringList(memory.metadata?.tags),
      meta: [
        memory.source || t('i18n.preview_unknown_provider'),
        ...(hasStrength(memory.strength)
          ? [`${t('i18n.preview_strength')} ${strengthPercent(memory.strength)}%`]
          : []),
      ],
      facts: [
        ...(memory.createdAt ? [{ label: t('en_created'), value: formatDate(memory.createdAt) }] : []),
        ...(memory.updatedAt ? [{ label: t('en_updated'), value: formatDate(memory.updatedAt) }] : []),
        { label: t('i18n.preview_provider'), value: memory.source || t('i18n.preview_unknown') },
        ...(stringValue(memory.metadata?.profile)
          ? [{ label: t('i18n.preview_profile'), value: stringValue(memory.metadata?.profile) }]
          : []),
        ...(stringValue(memory.metadata?.file)
          ? [{ label: t('i18n.preview_file'), value: stringValue(memory.metadata?.file) }]
          : []),
        { label: t('i18n.preview_memory_id'), value: memory.id },
      ],
    }
  }

  if (props.graphNode) {
    return {
      kicker: t('i18n.preview_graph_node'),
      title: props.graphNode.label,
      type: props.graphNode.type,
      typeClass: `preview-type--${props.graphNode.type}`,
      content: props.graphNode.contentSnippet || t('i18n.preview_no_content'),
      concepts: [],
      tags: props.graphNode.tags || [],
      meta: [
        props.graphNode.provider || t('i18n.preview_unknown_provider'),
        `${t('i18n.preview_strength')} ${strengthPercent(props.graphNode.strength)}%`,
        ...(props.graphNode.sessionId ? [props.graphNode.sessionId] : []),
      ],
      facts: [
        { label: t('i18n.preview_provider'), value: props.graphNode.provider || t('i18n.preview_unknown') },
        { label: t('i18n.preview_connections'), value: String(props.graphConnectionCount || 0) },
        { label: t('i18n.preview_node_id'), value: props.graphNode.id },
      ],
    }
  }

  return null
})

const fullDetailPath = computed(() => {
  if (props.memory) return `/memory/${props.memory.id}`
  if (props.unifiedMemory?.source === 'agentmemory') {
    return `/memory/${props.unifiedMemory.id}`
  }
  return ''
})

function stringList(value: unknown) {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : []
}

function stringValue(value: unknown) {
  return typeof value === 'string' ? value : ''
}

function hasStrength(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value)
}

function strengthPercent(strength: number) {
  const raw = strength * 10
  if (Number.isNaN(raw)) return 0
  return Math.max(0, Math.min(100, Math.round(raw)))
}

function formatDate(value: string | undefined) {
  if (!value) return t('i18n.preview_unknown')
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return t('i18n.preview_unknown')
  return date.toLocaleString(locale.value)
}
</script>

<style scoped>
.memory-preview {
  position: sticky;
  top: 92px;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  max-height: calc(100vh - 116px);
  padding: var(--space-5);
  overflow: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--card);
  box-shadow: var(--shadow);
}

.preview-header,
.preview-meta,
.preview-chips,
.preview-facts div {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.preview-header {
  justify-content: space-between;
}

.preview-heading {
  min-width: 0;
}

.preview-kicker,
.preview-label,
.preview-facts dt {
  color: var(--text-secondary);
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
}

.preview-heading h3 {
  margin: 2px 0 0;
  color: var(--primary);
  font-size: 1.05rem;
  line-height: 1.3;
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  width: 30px;
  height: 30px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--card);
  color: var(--text-secondary);
  cursor: pointer;
  font-family: var(--font);
  font-size: 0.76rem;
  font-weight: 700;
}

.icon-btn:hover {
  border-color: var(--border-strong);
  color: var(--primary);
}

.preview-meta,
.preview-chips {
  flex-wrap: wrap;
}

.preview-meta span,
.preview-chip,
.preview-type {
  display: inline-flex;
  align-items: center;
  min-height: 22px;
  padding: 2px 8px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--tag-bg);
  color: var(--text-secondary);
  font-size: 0.68rem;
  font-weight: 600;
}

.preview-type {
  text-transform: uppercase;
  letter-spacing: 0;
}

.preview-type--pattern {
  background: var(--type-pattern-bg);
  color: var(--type-pattern-text);
}

.preview-type--workflow {
  background: var(--type-workflow-bg);
  color: var(--type-workflow-text);
}

.preview-type--fact {
  background: var(--type-fact-bg);
  color: var(--type-fact-text);
}

.preview-type--preference {
  background: var(--type-preference-bg);
  color: var(--type-preference-text);
}

.preview-type--bug {
  background: var(--type-bug-bg);
  color: var(--type-bug-text);
}

.preview-type--architecture {
  background: var(--type-architecture-bg);
  color: var(--type-architecture-text);
}

.preview-content {
  max-height: 280px;
  overflow: auto;
  padding: var(--space-4);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg-recessed);
  color: var(--primary);
  font-size: 0.88rem;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

.preview-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.preview-facts {
  display: grid;
  gap: var(--space-2);
  margin: 0;
}

.preview-facts div {
  justify-content: space-between;
  min-width: 0;
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--border);
}

.preview-facts dd {
  margin: 0;
  overflow: hidden;
  color: var(--primary);
  font-size: 0.78rem;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-link {
  justify-content: center;
  text-decoration: none;
}

@media (max-width: 980px) {
  .memory-preview {
    position: static;
    max-height: none;
  }
}

@media (max-width: 767px) {
  .memory-preview {
    position: fixed;
    inset: 72px 12px calc(76px + env(safe-area-inset-bottom, 0px));
    z-index: 90;
    max-height: none;
    box-shadow: var(--shadow-modal);
  }
}
</style>
