<template>
  <aside class="memory-preview" aria-label="Memory detail preview">
    <div class="preview-header">
      <div class="preview-heading">
        <span class="preview-kicker">Detail panel</span>
        <h3>{{ memory.title }}</h3>
      </div>
      <button class="icon-btn" type="button" aria-label="Close preview" title="Close preview" @click="$emit('close')">
        X
      </button>
    </div>

    <div class="preview-meta">
      <span class="preview-type" :class="`preview-type--${memory.type}`">{{ memory.type }}</span>
      <span>Strength {{ strengthPercent }}%</span>
      <span v-if="memory.sessionIds?.length">{{ memory.sessionIds.slice(0, 2).join(', ') }}</span>
      <span v-if="memory.archived">Archived</span>
    </div>

    <div class="preview-content">
      {{ memory.content }}
    </div>

    <div class="preview-section" v-if="memory.concepts.length">
      <span class="preview-label">Concepts</span>
      <div class="preview-chips">
        <span v-for="concept in memory.concepts.slice(0, 8)" :key="concept" class="preview-chip">
          {{ concept }}
        </span>
      </div>
    </div>

    <div class="preview-section" v-if="memory.tags?.length">
      <span class="preview-label">Tags</span>
      <div class="preview-chips">
        <span v-for="tag in memory.tags.slice(0, 8)" :key="tag" class="preview-chip">
          {{ tag }}
        </span>
      </div>
    </div>

    <dl class="preview-facts">
      <div>
        <dt>Created</dt>
        <dd>{{ formatDate(memory.createdAt) }}</dd>
      </div>
      <div>
        <dt>Updated</dt>
        <dd>{{ formatDate(memory.updatedAt) }}</dd>
      </div>
      <div>
        <dt>Version</dt>
        <dd>{{ memory.version || 1 }}</dd>
      </div>
    </dl>

    <router-link class="action-btn action-btn--primary preview-link" :to="`/memory/${memory.id}`">
      Open full detail
    </router-link>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AgentMemory } from '@/types'

const props = defineProps<{
  memory: AgentMemory
}>()

defineEmits<{
  (e: 'close'): void
}>()

const strengthPercent = computed(() => {
  const raw = props.memory.strength * 10
  if (Number.isNaN(raw)) return 0
  return Math.max(0, Math.min(100, Math.round(raw)))
})

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
