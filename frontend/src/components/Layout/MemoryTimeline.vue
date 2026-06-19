<template>
  <div class="memory-timeline" aria-label="Memory timeline">
    <div
      v-for="group in groups"
      :key="group.key"
      class="timeline-group"
    >
      <div class="timeline-date">
        <span class="timeline-date__label">{{ group.label }}</span>
        <span class="timeline-date__count">{{ group.items.length }} memories</span>
      </div>

      <div class="timeline-items">
        <article
          v-for="memory in group.items"
          :key="memory.id"
          class="timeline-item"
        >
          <div class="timeline-rail" aria-hidden="true">
            <span class="timeline-dot" :class="`timeline-dot--${memory.type}`"></span>
          </div>

          <div class="timeline-card">
            <div class="timeline-card__header">
              <div class="timeline-title-wrap">
                <span class="timeline-type" :class="`timeline-type--${memory.type}`">{{ memory.type }}</span>
                <router-link :to="`/memory/${memory.id}`" class="timeline-title">
                  {{ memory.title }}
                </router-link>
              </div>
              <span class="timeline-time">{{ formatTime(memory.updatedAt || memory.createdAt) }}</span>
            </div>

            <p class="timeline-content">{{ truncate(memory.content, 180) }}</p>

            <div class="timeline-meta">
              <span class="timeline-strength">Strength {{ Math.round(memory.strength * 10) }}%</span>
              <span v-if="memory.sessionIds?.length" class="timeline-session">
                {{ memory.sessionIds.slice(0, 2).join(', ') }}
              </span>
              <span v-for="tag in (memory.tags || []).slice(0, 3)" :key="tag" class="timeline-tag">
                {{ tag }}
              </span>
            </div>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AgentMemory } from '@/types'

const props = defineProps<{
  memories: AgentMemory[]
}>()

interface TimelineGroup {
  key: string
  label: string
  items: AgentMemory[]
}

const groups = computed<TimelineGroup[]>(() => {
  const byDay = new Map<string, TimelineGroup>()
  const sorted = [...props.memories].sort((a, b) => (
    timestamp(b.updatedAt || b.createdAt) - timestamp(a.updatedAt || a.createdAt)
  ))

  for (const memory of sorted) {
    const date = new Date(memory.updatedAt || memory.createdAt)
    const key = Number.isNaN(date.getTime()) ? 'unknown' : date.toISOString().slice(0, 10)
    const label = Number.isNaN(date.getTime())
      ? 'Unknown date'
      : date.toLocaleDateString(undefined, {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })

    if (!byDay.has(key)) {
      byDay.set(key, { key, label, items: [] })
    }
    byDay.get(key)?.items.push(memory)
  }

  return Array.from(byDay.values())
})

function timestamp(value: string) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? 0 : date.getTime()
}

function formatTime(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Unknown time'
  return date.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
  })
}

function truncate(value: string, max: number) {
  if (value.length <= max) return value
  return `${value.slice(0, max).trim()}...`
}
</script>

<style scoped>
.memory-timeline {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.timeline-group {
  display: grid;
  grid-template-columns: minmax(148px, 180px) minmax(0, 1fr);
  gap: var(--space-5);
}

.timeline-date {
  position: sticky;
  top: 96px;
  align-self: start;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding-top: var(--space-2);
}

.timeline-date__label {
  color: var(--primary);
  font-size: 0.86rem;
  font-weight: 650;
}

.timeline-date__count {
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.timeline-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.timeline-item {
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr);
  gap: var(--space-3);
}

.timeline-rail {
  position: relative;
  display: flex;
  justify-content: center;
}

.timeline-rail::before {
  content: '';
  position: absolute;
  top: 22px;
  bottom: -18px;
  width: 1px;
  background: var(--border);
}

.timeline-dot {
  position: relative;
  z-index: 1;
  width: 10px;
  height: 10px;
  margin-top: 19px;
  border: 2px solid var(--card);
  border-radius: var(--radius-pill);
  background: var(--accent);
  box-shadow: 0 0 0 1px var(--border-strong);
}

.timeline-dot--pattern {
  background: var(--type-pattern-text);
}

.timeline-dot--workflow {
  background: var(--type-workflow-text);
}

.timeline-dot--fact {
  background: var(--type-fact-text);
}

.timeline-dot--preference {
  background: var(--type-preference-text);
}

.timeline-dot--bug {
  background: var(--type-bug-text);
}

.timeline-dot--architecture {
  background: var(--type-architecture-text);
}

.timeline-card {
  min-width: 0;
  padding: var(--space-4);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--card);
  box-shadow: var(--shadow);
  transition: border-color 0.2s ease, box-shadow 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              transform 0.25s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.timeline-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
}

.timeline-card__header,
.timeline-title-wrap,
.timeline-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.timeline-card__header {
  justify-content: space-between;
  margin-bottom: var(--space-2);
}

.timeline-title-wrap {
  min-width: 0;
}

.timeline-title {
  overflow: hidden;
  color: var(--primary);
  font-size: 0.95rem;
  font-weight: 650;
  text-decoration: none;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.timeline-title:hover {
  color: var(--accent);
}

.timeline-time {
  flex: 0 0 auto;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  font-size: 0.72rem;
}

.timeline-content {
  display: -webkit-box;
  overflow: hidden;
  margin: 0 0 var(--space-3);
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.6;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.timeline-meta {
  flex-wrap: wrap;
}

.timeline-type,
.timeline-strength,
.timeline-session,
.timeline-tag {
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

.timeline-type {
  flex: 0 0 auto;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.timeline-type--pattern {
  background: var(--type-pattern-bg);
  color: var(--type-pattern-text);
}

.timeline-type--workflow {
  background: var(--type-workflow-bg);
  color: var(--type-workflow-text);
}

.timeline-type--fact {
  background: var(--type-fact-bg);
  color: var(--type-fact-text);
}

.timeline-type--preference {
  background: var(--type-preference-bg);
  color: var(--type-preference-text);
}

.timeline-type--bug {
  background: var(--type-bug-bg);
  color: var(--type-bug-text);
}

.timeline-type--architecture {
  background: var(--type-architecture-bg);
  color: var(--type-architecture-text);
}

@media (max-width: 760px) {
  .timeline-group {
    grid-template-columns: 1fr;
    gap: var(--space-3);
  }

  .timeline-date {
    position: static;
    flex-direction: row;
    justify-content: space-between;
    padding-top: 0;
  }

  .timeline-card__header {
    align-items: flex-start;
    flex-direction: column;
  }

  .timeline-title {
    white-space: normal;
  }
}
</style>
