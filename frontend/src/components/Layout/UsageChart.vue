<template>
  <div class="usage-chart">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="chart-controls">
        <select v-model="selectedPeriod" @change="loadData" class="period-select">
          <option value="1h">1{{ $t('i18n.hours') }}</option>
          <option value="24h">24{{ $t('i18n.hours') }}</option>
          <option value="7d">7天</option>
          <option value="30d">30天</option>
        </select>
      </div>
    </div>
    <div v-if="loading" class="chart-loading">加载中...</div>
    <div v-else-if="data.length === 0" class="chart-empty">{{ $t('i18n.empty.chart_data') }}</div>
    <div v-else class="chart-body">
      <div class="chart-bars">
        <div
          v-for="(item, i) in data"
          :key="i"
          class="bar-group"
          :title="`${item.label}: ${item.value}`"
        >
          <div class="bar" :style="{ height: barHeight(item.value) + '%' }"></div>
          <div class="bar-label">{{ item.label }}</div>
        </div>
      </div>
    </div>
    <div v-if="summary" class="chart-summary">
      <div class="summary-item" v-for="(val, key) in summary" :key="key">
        <span class="summary-label">{{ key }}</span>
        <span class="summary-value">{{ val }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { request } from '@/api/index'

interface ChartItem {
  label: string
  value: number
}

const props = defineProps<{
  title: string
  endpoint: string
  valueKey?: string
  labelKey?: string
}>()

const data = ref<ChartItem[]>([])
const loading = ref(false)
const selectedPeriod = ref('24h')
const summary = ref<Record<string, string> | null>(null)

const maxValue = computed(() => Math.max(1, ...data.value.map(d => d.value)))

function barHeight(value: number): number {
  return (value / maxValue.value) * 100
}

async function loadData() {
  loading.value = true
  try {
    const res = await request<any>(`${props.endpoint}?period=${selectedPeriod.value}`)
    if (Array.isArray(res)) {
      data.value = res.map((item: any) => ({
        label: item[props.labelKey || 'timestamp'] || '',
        value: item[props.valueKey || 'requests'] || 0,
      }))
    } else if (res.trends) {
      data.value = res.trends.map((t: any) => ({
        label: new Date(t.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
        value: t.requests || 0,
      }))
      summary.value = {
        '总请求数': res.trends.reduce((s: number, t: any) => s + t.requests, 0).toString(),
        '平均延迟': `${(res.trends.reduce((s: number, t: any) => s + t.avg_latency_ms, 0) / Math.max(1, res.trends.length)).toFixed(1)}ms`,
      }
    } else if (res.endpoints) {
      data.value = res.endpoints.slice(0, 15).map((e: any) => ({
        label: e.endpoint.split(' ').pop()?.slice(0, 20) || '',
        value: e.count || 0,
      }))
    }
  } catch (e: any) {
    console.error('Chart load error:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => loadData())
</script>

<style scoped>
.usage-chart {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  margin-bottom: 16px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chart-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary);
}

.period-select {
  padding: 4px 8px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg-recessed);
  font-size: 0.8rem;
  color: var(--primary);
  font-family: var(--font);
}

.chart-loading,
.chart-empty {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 200px;
  padding-bottom: 24px;
  position: relative;
}

.bar-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
}

.bar {
  width: 100%;
  max-width: 30px;
  background: var(--accent);
  border-radius: 4px 4px 0 0;
  min-height: 2px;
  transition: height 0.3s ease;
}

.bar-label {
  font-size: 0.6rem;
  color: var(--text-secondary);
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 50px;
  text-align: center;
}

.chart-summary {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
  flex-wrap: wrap;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.summary-label {
  font-size: 0.7rem;
  color: var(--text-secondary);
}

.summary-value {
  font-size: 1rem;
  font-weight: 600;
  color: var(--accent);
}
</style>
