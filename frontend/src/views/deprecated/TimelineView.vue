<template>
  <div class="timeline-view">
    <div class="timeline-header">
      <div class="header-left">
        <h2>📅 时间线</h2>
        <p class="timeline-desc">按日期浏览 AgentMemory 记忆</p>
      </div>
      <div class="header-right">
        <div class="zoom-controls">
          <span class="zoom-label">缩放：</span>
          <button
            v-for="level in zoomLevels"
            :key="level.value"
            class="zoom-btn"
            :class="{ active: zoomLevel === level.value }"
            @click="zoomLevel = level.value"
          >
            {{ level.label }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>
    <div v-else-if="groups.length === 0" class="empty-state">暂无记忆数据</div>

    <template v-else>
      <div class="timeline">
        <div v-for="group in groups" :key="group.label" class="timeline-group">
          <div class="group-header" @click="toggleGroup(group.label)">
            <span class="group-chevron" :class="{ collapsed: !expandedGroups.has(group.label) }">
              ▶
            </span>
            <span class="group-label">{{ group.label }}</span>
            <span class="group-count">{{ group.items.length }} 条</span>
          </div>

          <div v-if="expandedGroups.has(group.label)" class="group-items">
            <MemoryCard
              v-for="memory in group.items"
              :key="memory.id"
              :memory="memory"
            />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAgentMemoryStore } from '@/stores/agentmemory'
import MemoryCard from '@/components/Layout/MemoryCard.vue'
import type { AgentMemory } from '@/types'

const agentMemoryStore = useAgentMemoryStore()
const loading = computed(() => agentMemoryStore.loading)

const zoomLevels = [
  { label: '日', value: 'day' },
  { label: '周', value: 'week' },
  { label: '月', value: 'month' }
] as const

type ZoomLevel = 'day' | 'week' | 'month'
const zoomLevel = ref<ZoomLevel>('day')

// Track which groups are expanded
const expandedGroups = ref<Set<string>>(new Set())

interface TimelineGroup {
  label: string
  items: AgentMemory[]
}

function formatDateKey(dateStr: string, level: ZoomLevel): string {
  const d = new Date(dateStr)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')

  if (level === 'day') {
    return `${year}-${month}-${day}`
  }

  if (level === 'week') {
    // Get Monday of the week
    const dayOfWeek = d.getDay() || 7 // Convert Sunday 0 to 7
    const monday = new Date(d)
    monday.setDate(d.getDate() - dayOfWeek + 1)
    const monYear = monday.getFullYear()
    const monMonth = String(monday.getMonth() + 1).padStart(2, '0')
    const monDay = String(monday.getDate()).padStart(2, '0')
    const sun = new Date(monday)
    sun.setDate(monday.getDate() + 6)
    const sunMonth = String(sun.getMonth() + 1).padStart(2, '0')
    const sunDay = String(sun.getDate()).padStart(2, '0')
    return `${monYear}-${monMonth}-${monDay} ~ ${sunMonth}-${sunDay}`
  }

  // Month level
  return `${year}-${month}`
}

function getGroupLabel(dateStr: string, level: ZoomLevel): string {
  if (level === 'day') {
    return formatDateKey(dateStr, 'day')
  }

  if (level === 'week') {
    const d = new Date(dateStr)
    const dayOfWeek = d.getDay() || 7
    const monday = new Date(d)
    monday.setDate(d.getDate() - dayOfWeek + 1)
    return formatDateKey(monday.toISOString(), 'week')
  }

  // Month
  const d = new Date(dateStr)
  const year = d.getFullYear()
  const month = d.getMonth() + 1
  const monthNames = ['一月', '二月', '三月', '四月', '五月', '六月',
                      '七月', '八月', '九月', '十月', '十一月', '十二月']
  return `${year}年 ${monthNames[month - 1]}`
}

const groups = computed<TimelineGroup[]>(() => {
  const map = new Map<string, AgentMemory[]>()

  // Only non-archived memories, sorted by updatedAt desc
  const sorted = [...agentMemoryStore.memories]
    .filter(m => !m.archived)
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())

  for (const m of sorted) {
    const label = getGroupLabel(m.updatedAt, zoomLevel.value)
    if (!map.has(label)) map.set(label, [])
    map.get(label)!.push(m)
  }

  // Convert to array and expand all groups by default
  const result = Array.from(map.entries()).map(([label, items]) => ({ label, items }))

  // Expand all groups initially
  expandedGroups.value = new Set(result.map(g => g.label))

  return result
})

function toggleGroup(label: string) {
  if (expandedGroups.value.has(label)) {
    expandedGroups.value.delete(label)
  } else {
    expandedGroups.value.add(label)
  }
  // Force reactivity
  expandedGroups.value = new Set(expandedGroups.value)
}

onMounted(() => {
  if (agentMemoryStore.memories.length === 0) {
    agentMemoryStore.fetchMemories()
  }
})
</script>

<style scoped>
.timeline-view {
  padding-bottom: 40px;
}

.timeline-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 32px;
  gap: 16px;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.timeline-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary);
  margin: 0;
  letter-spacing: -0.01em;
}

.timeline-desc {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 4px;
}

.zoom-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  padding: 0 8px;
}

.zoom-btn {
  padding: 6px 14px;
  font-size: 0.8rem;
  font-weight: 500;
  border: none;
  border-radius: calc(var(--radius) - 2px);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.zoom-btn:hover {
  background: var(--tag-bg);
  color: var(--primary);
}

.zoom-btn.active {
  background: var(--accent);
  color: white;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.timeline-group {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.group-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s ease;
}

.group-header:hover {
  background: var(--tag-bg);
}

.group-chevron {
  font-size: 0.65rem;
  color: var(--text-secondary);
  transition: transform 0.2s ease;
  display: inline-block;
}

.group-chevron.collapsed {
  transform: rotate(0deg);
}

.group-chevron:not(.collapsed) {
  transform: rotate(90deg);
}

.group-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--primary);
  letter-spacing: -0.01em;
}

.group-count {
  font-size: 0.75rem;
  padding: 2px 10px;
  border-radius: 12px;
  background: var(--tag-bg);
  color: var(--text-secondary);
  margin-left: auto;
}

.group-items {
  display: flex;
  flex-direction: column;
  gap: 1px;
  background: var(--border);
  border-top: 1px solid var(--border);
}

.group-items > :deep(.memory-card) {
  border: none;
  border-radius: 0;
  box-shadow: none;
}

.group-items > :deep(.memory-card:hover) {
  transform: none;
  box-shadow: none;
}

.group-items > :deep(.memory-card:first-child) {
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}

.group-items > :deep(.memory-card:last-child) {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}

/* Responsive */
@media (max-width: 767px) {
  .timeline-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .zoom-controls {
    width: 100%;
    justify-content: center;
  }

  .group-header h2 {
    font-size: 1.2rem;
  }
}
</style>