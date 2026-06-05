<template>
  <div class="dashboard-view">
    <div class="dashboard-header">
      <h2 class="section-title">📊 {{ $t('zh_4dc488') }}</h2>
      <button class="action-btn" @click="loadStats">🔄 刷新</button>
    </div>

    <!-- F-37: Activity Heatmap -->
    <ActivityHeatmap @day-click="onHeatmapDayClick" />

    <div v-if="loading" class="loading-state">加载中...</div>
    <div v-else-if="error" class="error-state">
      <p>⚠️ {{ error }}</p>
      <button class="action-btn action-btn--danger" @click="loadStats">点击{{ $t('zh_006cc1') }}</button>
    </div>
    <div v-else-if="stats" class="dashboard-grid">
      <!-- P38 r9: count-up 动画 — 从 0 滚动到目标值（800ms ease-out-cubic）。
           替代原版"瞬时显示"，给 Dashboard 首屏"载入感"。 -->
      <div class="summary-row">
        <div class="summary-card">
          <div class="summary-label">{{ $t('zh_b380bf') }}</div>
          <div class="summary-value">{{ stats ? displayTotal : '—' }}</div>
          <div class="summary-foot">{{ $t('en_all_sources') }}</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">{{ $t('zh_b1a7a7') }}</div>
          <div class="summary-value">{{ stats ? displayAvgStrength : '—' }}</div>
          <div class="summary-foot">/ 10.0</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">{{ $t('zh_0da3e8') }}</div>
          <div class="summary-value">{{ stats ? displayTypeCount : '—' }}</div>
          <div class="summary-foot">{{ $t('en_categories') }}</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">{{ $t('zh_baab58') }}</div>
          <div class="summary-value">{{ stats ? displayMonthCount : '—' }}</div>
          <div class="summary-foot">{{ $t('en_months') }}</div>
        </div>
      </div>

      <!-- Type Distribution Bar Chart -->
      <div class="chart-card">
        <h3>📋 {{ $t('zh_4ddd85') }}</h3>
        <div v-if="Object.keys(stats.by_type).length === 0" class="chart-empty">
          <span class="chart-empty-mark" aria-hidden="true">∅</span>
          <span class="chart-empty-text">{{ $t('zh_b651d3') }}</span>
        </div>
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
        <h3>💪 Strength {{ $t('zh_00645b') }}</h3>
        <div v-if="maxStrengthCount === 0" class="chart-empty">
          <span class="chart-empty-mark" aria-hidden="true">∅</span>
          <span class="chart-empty-text">{{ $t('zh_b651d3') }}</span>
        </div>
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
        <h3>📅 {{ $t('zh_82acd7') }}</h3>
        <div v-if="Object.keys(stats.by_month).length === 0" class="chart-empty">
          <span class="chart-empty-mark" aria-hidden="true">∅</span>
          <span class="chart-empty-text">{{ $t('zh_b651d3') }}</span>
        </div>
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
import { useCountUp } from '@/composables/useCountUp'

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

/* P38 r9: count-up 动画 — 4 个 summary card 数字从 0 滚动到目标。
 * 800ms 动画 + easeOutCubic（"快进 + 慢停"，强调目标到达）。
 * 减少动效偏好的用户自动跳过（useCountUp 内部检测）。 */
const { value: totalRaw } = useCountUp(
  computed(() => stats.value?.total),
  { duration: 800 },
)
const { value: avgStrengthRaw } = useCountUp(
  computed(() => stats.value?.avg_strength),
  { duration: 800, format: (n) => n.toFixed(1) },
)
const { value: typeCountRaw } = useCountUp(
  computed(() => (stats.value ? Object.keys(stats.value.by_type).length : 0)),
  { duration: 600 },
)
const { value: monthCountRaw } = useCountUp(
  computed(() => (stats.value ? Object.keys(stats.value.by_month).length : 0)),
  { duration: 600 },
)

/* 对 total 做千分位格式化（动画过程中也会保留千分位） */
const displayTotal = computed(() => {
  // 动画过程是字符串，尝试解析后重新格式化
  const n = Number(totalRaw.value)
  if (Number.isFinite(n)) return n.toLocaleString()
  return totalRaw.value
})
const displayAvgStrength = avgStrengthRaw
const displayTypeCount = typeCountRaw
const displayMonthCount = monthCountRaw

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
  margin-bottom: var(--space-7);    /* P41: 32 → --space-7 (32px)，与 P40 spacing scale 对齐 */
  padding-bottom: var(--space-5);   /* P41: 20 → --space-5 */
  gap: var(--space-3);              /* P41: 与 P40 HomeView 标题区节奏一致 */
  border-bottom: 1px solid var(--border);
}

.dashboard-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary);
  margin: 0;
  letter-spacing: -0.02em;
}

/* P38 r20: section-title 左侧 3px accent bar — 与 HomeView / AppSidebar / HermesMemoryView / AgentMemoryView 同源 (r15 模式). */
.dashboard-header h2.section-title {
  position: relative;
  padding-left: 12px;
}

.dashboard-header h2.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: var(--accent);
  border-radius: 0 2px 2px 0;
}

/* P38 r21: button system unification — .action-btn + variants defined
   globally in styles/main.css. Local .btn-refresh / .btn-retry removed. */

.loading-state,
.error-state {
  text-align: center;
  padding: 60px var(--space-5);     /* P41: 20 → --space-5 */
  color: var(--text-secondary);
  font-size: 1rem;
}

.error-state {
  color: var(--error);
  text-align: center;
  padding: 60px var(--space-5);
}

/* P37: Summary Cards — Geist Stats 卡风格（标题-大值-副标） */
.summary-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: var(--space-4);                /* P41: 16 → --space-4 */
  margin-bottom: var(--space-7);      /* P41: 32 → --space-7 */
}

.summary-card {
  background: var(--card);
  border-radius: var(--radius-md);
  padding: var(--space-5) var(--space-6);  /* P41: 20 24 → --space-5 --space-6 */
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);                /* P41: 8 → --space-2 */
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
  padding: var(--space-6) var(--space-7);  /* P41: 24 28 → --space-6 --space-7 (24 32) */
  margin-bottom: var(--space-5);          /* P41: 20 → --space-5 */
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
  margin-bottom: var(--space-5);          /* P41: 20 → --space-5 */
}

/* P44: chart-empty 增加视觉锚点（∅ mark + 文字），
   三处保持单行但视觉重量提升，避免 chart card 显得空洞。
   不引入完整 EmptyState 组件 — 数据返回时立即替换。 */
.chart-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  text-align: center;
  padding: var(--space-8) var(--space-5);
  color: var(--text-tertiary);
  font-size: 0.8125rem;
  letter-spacing: 0.01em;
}

.chart-empty-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 999px;
  background: var(--tag-bg);
  color: var(--text-tertiary);
  font-size: 0.875rem;
  line-height: 1;
  font-weight: 500;
}

.chart-empty-text {
  color: var(--text-secondary);
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
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
}

/* P38: dot prefix mirrors the MemoryCard chip dot — same hue, same shape,
   so dashboard "type distribution" reads as the same visual language */
.bar-label::after {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.7;
  flex-shrink: 0;
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

/* P38: type bars reuse --type-*-text token so dark mode is auto and the
   bar color matches the chip color elsewhere in the app (MemoryCard / UnifiedCard) */
.bar-fill.type-pattern     { background: var(--type-pattern-text); }
.bar-fill.type-fact        { background: var(--type-fact-text); }
.bar-fill.type-preference  { background: var(--type-preference-text); }
.bar-fill.type-bug         { background: var(--type-bug-text); }
.bar-fill.type-workflow    { background: var(--type-workflow-text); }
.bar-fill.type-architecture{ background: var(--type-architecture-text); }

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
  gap: var(--space-2);                /* P41: 8 → --space-2 */
}

.timeline-bar {
  display: flex;
  align-items: center;
  gap: var(--space-3);                /* P41: 12 → --space-3 */
}

.timeline-label {
  min-width: 70px;
  font-size: 0.8rem;
  color: var(--primary);
  text-align: right;
  font-family: var(--font-mono);  /* P41: 与 P40 TabBar/MemoryCard 统一 Geist mono 语言 */
}

.timeline-track {
  flex: 1;
  height: var(--space-5);             /* P41: 20 → --space-5 */
  background: var(--tag-bg);
  border-radius: var(--radius-sm);    /* P41: 6 → --radius-sm (6px) */
  overflow: hidden;
}

.timeline-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 6px;
  transition: width 0.5s ease;
  min-width: 4px;
  /* P38: hairline highlight at the top of the bar — gives the bar a
     subtle "tube" feel without breaking the token system */
  box-shadow: inset 0 1px 0 0 color-mix(in srgb, var(--card) 18%, transparent);
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
