<template>
  <aside v-if="detail" class="memory-preview" aria-label="Memory detail preview">
    <div class="preview-header">
      <div class="preview-heading">
        <span class="preview-kicker">{{ detail.kicker }}</span>
        <h3>{{ detail.title }}</h3>
      </div>
      <button class="icon-btn" type="button" aria-label="Close preview" title="Close preview" @click="$emit('close')">
        X
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
      <span class="preview-label">Concepts</span>
      <div class="preview-chips">
        <span v-for="concept in detail.concepts.slice(0, 8)" :key="concept" class="preview-chip">
          {{ concept }}
        </span>
      </div>
    </div>

    <div class="preview-section" v-if="detail.tags.length">
      <span class="preview-label">Tags</span>
      <div class="preview-chips">
        <span v-for="tag in detail.tags.slice(0, 8)" :key="tag" class="preview-chip">
          {{ tag }}
        </span>
      </div>
    </div>

    <dl class="preview-facts" v-if="detail.facts.length">
      <div v-for="fact in detail.facts" :key="fact.label">
        <dt>{{ fact.label }}</dt>
        <dd>{{ fact.value }}</dd>
      </div>
    </dl>

    <router-link v-if="fullDetailPath" class="action-btn action-btn--primary preview-link" :to="fullDetailPath">
      Open full detail
    </router-link>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AgentMemory } from '@/types'
import type { MemoryGraphNode } from '@/api/graph'

const props = withDefaults(defineProps<{
  memory?: AgentMemory | null
  graphNode?: MemoryGraphNode | null
  graphConnectionCount?: number
}>(), {
  memory: null,
  graphNode: null,
  graphConnectionCount: 0,
})

defineEmits<{
  (e: 'close'): void
}>()

const detail = computed(() => {
  if (props.memory) {
    return {
      kicker: 'Detail panel',
      title: props.memory.title,
      type: props.memory.type,
      typeClass: `preview-type--${props.memory.type}`,
      content: props.memory.content,
      concepts: props.memory.concepts,
      tags: props.memory.tags || [],
      meta: [
        `Strength ${strengthPercent(props.memory.strength)}%`,
        ...(props.memory.sessionIds?.length ? [props.memory.sessionIds.slice(0, 2).join(', ')] : []),
        ...(props.memory.archived ? ['Archived'] : []),
      ],
      facts: [
        { label: 'Created', value: formatDate(props.memory.createdAt) },
        { label: 'Updated', value: formatDate(props.memory.updatedAt) },
        { label: 'Version', value: String(props.memory.version || 1) },
      ],
    }
  }

  if (props.graphNode) {
    return {
      kicker: 'Graph node',
      title: props.graphNode.label,
      type: props.graphNode.type,
      typeClass: `preview-type--${props.graphNode.type}`,
      content: props.graphNode.contentSnippet || 'No content preview.',
      concepts: [],
      tags: props.graphNode.tags || [],
      meta: [
        props.graphNode.provider || 'Unknown provider',
        `Strength ${strengthPercent(props.graphNode.strength)}%`,
        ...(props.graphNode.sessionId ? [props.graphNode.sessionId] : []),
      ],
      facts: [
        { label: 'Provider', value: props.graphNode.provider || 'Unknown' },
        { label: 'Connections', value: String(props.graphConnectionCount || 0) },
        { label: 'Node ID', value: props.graphNode.id },
      ],
    }
  }

  return null
})

const fullDetailPath = computed(() => (
  props.memory ? `/memory/${props.memory.id}` : ''
))

function strengthPercent(strength: number) {
  const raw = strength * 10
  if (Number.isNaN(raw)) return 0
  return Math.max(0, Math.min(100, Math.round(raw)))
}

function formatDate(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Unknown'
  return date.toLocaleString()
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
  letter-spacing: 0.06em;
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
</style>
