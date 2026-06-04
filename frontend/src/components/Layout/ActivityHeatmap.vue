<template>
  <div class="heatmap-container">
    <div class="heatmap-header">
      <h3>🗓️ {{ $t('zh_1e907a') }}</h3>
      <div class="heatmap-controls">
        <select v-model="selectedMetric" class="heatmap-select" @change="loadData">
          <option value="created">{{ $t('zh_00645e') }}</option>
          <option value="modified">{{ $t('zh_00641d') }}</option>
          <option value="accessed">{{ $t('zh_006c03') }}</option>
        </select>
        <button class="heatmap-refresh" @click="loadData" :disabled="loading">🔄</button>
      </div>
    </div>

    <div v-if="loading" class="heatmap-loading">加载中...</div>
    <div v-else-if="error" class="heatmap-error">{{ error }}</div>
    <div v-else class="heatmap-body">
      <!-- Month labels -->
      <div class="heatmap-months">
        <span v-for="month in monthLabels" :key="month.label"
              :style="{ gridColumn: month.col }">{{ month.label }}</span>
      </div>

      <!-- Grid -->
      <div class="heatmap-grid-wrapper">
        <!-- Day-of-week labels -->
        <div class="heatmap-weekdays">
          <span>一</span><span>三</span><span>五</span>
        </div>
        <div class="heatmap-grid" ref="gridRef">
          <div
            v-for="(cell, idx) in cells"
            :key="idx"
            class="heatmap-cell"
            :class="cell.level"
            :title="cell.tooltip"
            @click="onCellClick(cell)"
          />
        </div>
      </div>

      <!-- Legend -->
      <div class="heatmap-legend">
        <span class="heatmap-legend-label">少</span>
        <div class="heatmap-cell level-0" />
        <div class="heatmap-cell level-1" />
        <div class="heatmap-cell level-2" />
        <div class="heatmap-cell level-3" />
        <div class="heatmap-cell level-4" />
        <span class="heatmap-legend-label">多</span>
      </div>

      <!-- Stats -->
      <div class="heatmap-stats" v-if="summary">
        <span>📊 共 <strong>{{ summary.total_events }}</strong> {{ $t('zh_0d5cd1') }}</span>
        <span>📅 {{ $t('zh_00680c') }} <strong>{{ summary.active_days }}</strong> 天</span>
        <span>🔥 {{ $t('zh_abce73') }} <strong>{{ summary.max_day_count }}</strong></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { request } from '@/api/index'
import type { HeatmapData, HeatmapSummaryResponse } from '@/types'

const router = useRouter()
const emit = defineEmits<{
  (e: 'dayClick', date: string): void
}>()

const selectedMetric = ref<'created' | 'modified' | 'accessed'>('created')
const loading = ref(false)
const error = ref<string | null>(null)
const heatData = ref<HeatmapData>({})
const summary = ref<Omit<HeatmapSummaryResponse, 'data'> | null>(null)

interface HeatCell {
  date: string
  count: number
  level: string
  tooltip: string
  weekIndex: number
  dayOfWeek: number
}

// Generate calendar cells for the past 365 days
const cells = computed<HeatCell[]>(() => {
  const result: HeatCell[] = []
  const today = new Date()

  // Find the start: go back ~52 weeks to the start of that week (Monday)
  const start = new Date(today)
  start.setDate(start.getDate() - 364)
  // Adjust to previous Monday
  const dow = start.getDay()
  const offset = dow === 0 ? 6 : dow - 1
  start.setDate(start.getDate() - offset)

  let current = new Date(start)
  let weekIndex = 0

  while (current <= today) {
    const dateStr = formatDate(current)
    const count = heatData.value[dateStr] || 0
    const level = getLevel(count, summary.value?.max_day_count || 0)
    const dayOfWeek = current.getDay() === 0 ? 6 : current.getDay() - 1 // Mon=0, Sun=6

    if (dayOfWeek === 0 && current > start) {
      weekIndex++
    }

    result.push({
      date: dateStr,
      count,
      level,
      tooltip: `${dateStr}: ${count} 条记忆`,
      weekIndex,
      dayOfWeek,
    })

    current.setDate(current.getDate() + 1)
  }

  return result
})

// Month labels based on cell data
const monthLabels = computed(() => {
  const labels: Array<{ label: string; col: number }> = []
  let lastMonth = -1
  const monthNames = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']

  for (const cell of cells.value) {
    const d = new Date(cell.date)
    const m = d.getMonth()
    if (m !== lastMonth && d.getDate() <= 7) {
      labels.push({ label: monthNames[m], col: cell.weekIndex + 1 })
      lastMonth = m
    }
  }
  return labels
})

function getLevel(count: number, maxCount: number): string {
  if (count === 0) return 'level-0'
  if (maxCount === 0) return 'level-0'
  const ratio = count / maxCount
  if (ratio <= 0.25) return 'level-1'
  if (ratio <= 0.50) return 'level-2'
  if (ratio <= 0.75) return 'level-3'
  return 'level-4'
}

function formatDate(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

async function loadData() {
  loading.value = true
  error.value = null
  try {
    const resp = await request<HeatmapSummaryResponse>(
      `/metrics/heatmap/summary?metric=${selectedMetric.value}&days=365`
    )
    heatData.value = resp.data
    summary.value = {
      metric: resp.metric,
      days: resp.days,
      total_events: resp.total_events,
      max_day_count: resp.max_day_count,
      active_days: resp.active_days,
      total_days: resp.total_days,
    }
  } catch (e: any) {
    error.value = e.message || '加载热力图失败'
  } finally {
    loading.value = false
  }
}

function onCellClick(cell: HeatCell) {
  if (cell.count > 0) {
    emit('dayClick', cell.date)
    router.push({ name: 'agentmemory', query: { date: cell.date } })
  }
}

onMounted(loadData)
</script>

<style scoped>
.heatmap-container {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
}

.heatmap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.heatmap-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary);
}

.heatmap-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.heatmap-select {
  padding: 4px 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--primary);
  font-size: 0.8rem;
  font-family: var(--font);
  outline: none;
  cursor: pointer;
}

.heatmap-select:focus {
  border-color: var(--accent);
}

.heatmap-refresh {
  padding: 4px 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  cursor: pointer;
  font-size: 0.8rem;
}

.heatmap-refresh:hover {
  background: var(--tag-bg);
}

.heatmap-loading,
.heatmap-error {
  text-align: center;
  padding: 30px;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.heatmap-error {
  color: var(--error, #d93025);
}

.heatmap-body {
  overflow-x: auto;
}

.heatmap-months {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: calc(100% / 53);
  font-size: 0.65rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
  padding-left: 28px;
  min-width: 640px;
}

.heatmap-grid-wrapper {
  display: flex;
  gap: 4px;
  min-width: 640px;
}

.heatmap-weekdays {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 0.6rem;
  color: var(--text-secondary);
  padding: 2px 0;
  width: 24px;
  flex-shrink: 0;
}

.heatmap-weekdays span {
  height: 13px;
  display: flex;
  align-items: center;
}

.heatmap-grid {
  display: grid;
  grid-template-rows: repeat(7, 13px);
  grid-auto-flow: column;
  grid-auto-columns: 13px;
  gap: 2px;
  flex: 1;
}

.heatmap-cell {
  width: 11px;
  height: 11px;
  border-radius: 2px;
  cursor: pointer;
  transition: transform 0.1s;
}

.heatmap-cell:hover {
  transform: scale(1.4);
}

/* Levels — P38 r22: GitHub 硬编码绿 (9be9a8/40c463/30a14e/216e39) → 全站 --accent 蓝渐变。
   5 档 token 已在 variables.css 定义（--heatmap-0/1/2/3/4），
   color-mix 自动跟随 light/dark 两套 --accent，深色背景下 alpha 自动混 dark 底色。
   删除原 dark-mode 9 行 hardcoded GitHub 绿（0e4429/006d32/26a641/39d353）— token 自适应。 */
.heatmap-cell.level-0 {
  background: var(--heatmap-0);
}

.heatmap-cell.level-1 {
  background: var(--heatmap-1);
}

.heatmap-cell.level-2 {
  background: var(--heatmap-2);
}

.heatmap-cell.level-3 {
  background: var(--heatmap-3);
}

.heatmap-cell.level-4 {
  background: var(--heatmap-4);
}

.heatmap-legend {
  display: flex;
  align-items: center;
  gap: 3px;
  justify-content: flex-end;
  margin-top: 8px;
  font-size: 0.65rem;
  color: var(--text-secondary);
}

.heatmap-legend-label {
  margin: 0 4px;
}

.heatmap-stats {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  flex-wrap: wrap;
}

.heatmap-stats strong {
  color: var(--primary);
}

/* Responsive */
@media (max-width: 767px) {
  .heatmap-container {
    padding: 12px;
  }

  .heatmap-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }

  .heatmap-stats {
    flex-direction: column;
    gap: 4px;
  }
}
</style>
