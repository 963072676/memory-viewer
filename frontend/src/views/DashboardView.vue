<template>
  <div class="dashboard-view">
    <div class="dashboard-header">
      <h2>📊 统计仪表盘</h2>
      <button class="btn-refresh" @click="loadStats">🔄 刷新</button>
    </div>

    <!-- F-37: Activity Heatmap -->
    <ActivityHeatmap @day-click="onHeatmapDayClick" />

    <div v-if="loading" class="loading-state">加载中...</div>
    <div v-else-if="error" class="error-state">
      <p>⚠️ {{ error }}</p>
      <button class="btn-retry" @click="loadStats">点击重试</button>
    </div>
    <div v-else-if="stats" class="dashboard-grid">
      <!-- P37: Summary Cards — 三段式（标题-大值-副标）Geist 风格 -->
      <div class="summary-row">
        <div class="summary-card">
          <div class="summary-label">总记忆数</div>
          <div class="summary-value">{{ stats.total.toLocaleString() }}</div>
          <div class="summary-foot">All Sources</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">平均强度</div>
          <div class="summary-value">{{ stats.avg_strength.toFixed(1) }}</div>
          <div class="summary-foot">/ 10.0</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">类型数</div>
          <div class="summary-value">{{ Object.keys(stats.by_type).length }}</div>
          <div class="summary-foot">Categories</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">活跃月份</div>
          <div class="summary-value">{{ Object.keys(stats.by_month).length }}</div>
          <div class="summary-foot">Months</div>
        </div>
      </div>

      <!-- Type Distribution Bar Chart -->
      <div class="chart-card">
        <h3>📋 按类型分布</h3>
        <div v-if="Object.keys(stats.by_type).length === 0" class="chart-empty">暂无数据</div>
        <div v-else class="bar-chart">
          <div v-for="(count, type) in stats.by_type" :key="type" class="bar-row">
            <span class="bar-label">{{ type }}</span>
            <div class="bar-track">
              <div
                class="bar-fill"
                :class="'type-' + type"
                :style="{ width: (count / maxTypeCount * 100) + '%' }"
              ></div>
            </div>
            <span class="bar-value">{{ count }}</span>
          </div>
        </div>
      </div>

      <!-- Strength Distribution Histogram -->
      <div class="chart-card">
        <h3>💪 Strength 分布</h3>
        <div v-if="maxStrengthCount === 0" class="chart-empty">暂无数据</div>
        <div v-else class="histogram">
          <div v-for="i in 11" :key="i - 1" class="hist-column">
            <div class="hist-bar-wrapper">
              <div
                class="hist-bar"
                :style="{ height: ((stats.strength_distribution[String(i - 1)] || 0) / maxStrengthCount * 100) + '%' }"
              ></div>
            </div>
            <div class="hist-count">{{ stats.strength_distribution[String(i - 1)] || 0 }}</div>
            <div class="hist-label">{{ i - 1 }}</div>
          </div>
        </div>
      </div>

      <!-- Timeline (by month) -->
      <div class="chart-card">
        <h3>📅 按月创建趋势</h3>
        <div v-if="Object.keys(stats.by_month).length === 0" class="chart-empty">暂无数据</div>
        <div v-else class="timeline-chart">
          <div v-for="(count, month) in stats.by_month" :key="month" class="timeline-bar">
            <div class="timeline-label">{{ month }}</div>
            <div class="timeline-track">
              <div
                class="timeline-fill"
                :style="{ width: (count / maxMonthCount * 100) + '%' }"
              ></div>
            </div>
            <div class="timeline-value">{{ count }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { request } from '@/api/index'
import ActivityHeatmap from '@/components/Layout/ActivityHeatmap.vue'

interface Stats {
  total: number
  avg_strength: number
  by_type: Record<string, number>
  strength_distribution: Record<string, number>
  by_month: Record<string, number>
}

const stats = ref<Stats | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const maxTypeCount = computed(() => {
  if (!stats.value) return 1
  return Math.max(1, ...Object.values(stats.value.by_type))
})

const maxStrengthCount = computed(() => {
  if (!stats.value) return 1
  return Math.max(1, ...Object.values(stats.value.strength_distribution))
})

const maxMonthCount = computed(() => {
  if (!stats.value) return 1
  return Math.max(1, ...Object.values(stats.value.by_month))
})

async function loadStats() {
  loading.value = true
  error.value = null
  try {
    stats.value = await request<Stats>('/agentmemory/stats')
  } catch (e: any) {
    error.value = e.message || '加载统计数据失败'
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)

function onHeatmapDayClick(date: string) {
  // Navigate to filtered memory list for that date
  console.log('Heatmap day clicked:', date)
}
</script>

<style scoped>
.dashboard-view {
  padding-bottom: 40px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
}

.dashboard-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary);
  margin: 0;
  letter-spacing: -0.02em;
}

/* P37: btn-refresh — Geist 风格 outline 按钮 */
.btn-refresh {
  padding: 8px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--card);
  color: var(--primary);
  font-size: 0.8125rem;
  font-weight: 500;
  font-family: var(--font);
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.btn-refresh:hover {
  background: var(--bg-recessed);
  border-color: var(--border-strong);
}

.loading-state,
.error-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  font-size: 1rem;
}

.error-state {
  color: var(--error);
  text-align: center;
  padding: 60px 20px;
}

.btn-retry {
  margin-top: 12px;
  padding: 8px 20px;
  border: 1px solid var(--error);
  border-radius: 8px;
  background: transparent;
  color: var(--error);
  font-size: 0.875rem;
  font-family: var(--font);
  cursor: pointer;
  transition: background 0.2s;
}

.btn-retry:hover {
  background: var(--error-bg);
}

/* P37: Summary Cards — Geist Stats 卡风格（标题-大值-副标） */
.summary-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.summary-card {
  background: var(--card);
  border-radius: var(--radius-md);
  padding: 20px 24px;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.summary-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-1px);
}

.summary-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
  letter-spacing: 0.01em;
  line-height: 1.3;
}

.summary-value {
  font-family: var(--font-mono);
  font-size: 2rem;
  font-weight: 600;
  color: var(--primary);
  line-height: 1.1;
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}

.summary-foot {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  font-weight: 500;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

/* P37: Chart Cards — 用 box-shadow 替代 border 营造悬浮感 */
.chart-card {
  background: var(--card);
  border-radius: var(--radius-lg);
  padding: 24px 28px;
  margin-bottom: 20px;
  box-shadow: var(--shadow);
  transition: box-shadow 0.2s ease;
}

.chart-card:hover {
  box-shadow: var(--shadow-hover);
}

.chart-card h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 20px;
}

.chart-empty {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* Bar Chart (Type Distribution) */
.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bar-label {
  min-width: 90px;
  font-size: 0.8rem;
  color: var(--primary);
  text-transform: capitalize;
  text-align: right;
}

.bar-track {
  flex: 1;
  height: 24px;
  background: var(--tag-bg);
  border-radius: 6px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.5s ease;
  min-width: 4px;
}

.bar-fill.type-pattern { background: #4caf50; }
.bar-fill.type-fact { background: #2196f3; }
.bar-fill.type-preference { background: #e91e63; }
.bar-fill.type-bug { background: #ff9800; }
.bar-fill.type-workflow { background: #9c27b0; }
.bar-fill.type-architecture { background: #009688; }

.bar-value {
  min-width: 30px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--primary);
  text-align: right;
}

/* Histogram (Strength Distribution) */
.histogram {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 180px;
  padding-bottom: 30px;
  position: relative;
}

.hist-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  position: relative;
}

.hist-bar-wrapper {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.hist-bar {
  width: 80%;
  max-width: 40px;
  background: var(--accent);
  border-radius: 4px 4px 0 0;
  transition: height 0.5s ease;
  min-height: 2px;
}

.hist-count {
  font-size: 0.65rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

.hist-label {
  font-size: 0.7rem;
  color: var(--text-secondary);
  font-weight: 600;
  position: absolute;
  bottom: 0;
}

/* Timeline Chart */
.timeline-chart {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.timeline-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.timeline-label {
  min-width: 70px;
  font-size: 0.8rem;
  color: var(--primary);
  text-align: right;
  font-family: monospace;
}

.timeline-track {
  flex: 1;
  height: 20px;
  background: var(--tag-bg);
  border-radius: 6px;
  overflow: hidden;
}

.timeline-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), #64b5f6);
  border-radius: 6px;
  transition: width 0.5s ease;
  min-width: 4px;
}

.timeline-value {
  min-width: 30px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--primary);
  text-align: right;
}

.dashboard-grid {
  display: flex;
  flex-direction: column;
}

/* Responsive */
@media (max-width: 767px) {
  h2 {
    font-size: 1.2rem;
  }

  .summary-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .summary-value {
    font-size: 1.5rem;
  }

  .bar-label {
    min-width: 60px;
    font-size: 0.7rem;
  }

  .histogram {
    height: 120px;
  }

  .timeline-label {
    min-width: 50px;
    font-size: 0.7rem;
  }
}
</style>
