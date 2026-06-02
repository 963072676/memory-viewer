<template>
  <div class="metrics-view">
    <div class="view-header">
      <h2>📊 性能监控</h2>
      <button class="action-btn" @click="fetchMetrics">刷新</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <EmptyState v-else-if="loadError" icon="⚠️" message="性能数据加载失败" action-text="点击重试" @action="fetchMetrics" />

    <div v-else-if="data">
      <!-- Global stats -->
      <div class="summary-row">
        <div class="summary-card">
          <div class="summary-value">{{ data.total_requests }}</div>
          <div class="summary-label">总请求数</div>
        </div>
        <div class="summary-card">
          <div class="summary-value">{{ data.avg_duration_ms }}ms</div>
          <div class="summary-label">平均耗时</div>
        </div>
        <div class="summary-card">
          <div class="summary-value">{{ data.p50_ms }}ms</div>
          <div class="summary-label">P50</div>
        </div>
        <div class="summary-card">
          <div class="summary-value">{{ data.p95_ms }}ms</div>
          <div class="summary-label">P95</div>
        </div>
        <div class="summary-card">
          <div class="summary-value">{{ data.p99_ms }}ms</div>
          <div class="summary-label">P99</div>
        </div>
      </div>

      <!-- Per-endpoint table -->
      <section class="metrics-section">
        <h3>端点统计</h3>
        <div class="table-wrap">
          <table class="metrics-table">
            <thead>
              <tr>
                <th>端点</th>
                <th>请求数</th>
                <th>平均耗时</th>
                <th>P50</th>
                <th>P95</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(stats, endpoint) in data.endpoints" :key="endpoint">
                <td class="endpoint-cell">{{ endpoint }}</td>
                <td>{{ stats.count }}</td>
                <td>{{ stats.avg_ms }}ms</td>
                <td>{{ stats.p50_ms }}ms</td>
                <td>{{ stats.p95_ms }}ms</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Recent requests -->
      <section class="metrics-section">
        <h3>最近请求</h3>
        <div class="table-wrap">
          <table class="metrics-table">
            <thead>
              <tr>
                <th>时间</th>
                <th>方法</th>
                <th>路径</th>
                <th>状态</th>
                <th>耗时</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(r, i) in data.recent" :key="i">
                <td class="time-cell">{{ formatTime(r.timestamp) }}</td>
                <td><span :class="'method-badge method-' + r.method?.toLowerCase()">{{ r.method }}</span></td>
                <td class="endpoint-cell">{{ r.path }}</td>
                <td><span :class="['status-badge', r.status < 400 ? 'status-ok' : 'status-err']">{{ r.status }}</span></td>
                <td>{{ r.duration_ms?.toFixed(1) }}ms</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import EmptyState from '@/components/Layout/EmptyState.vue'

interface EndpointStats { count: number; avg_ms: number; p50_ms: number; p95_ms: number }
interface RecentReq { method: string; path: string; status: number; duration_ms: number; timestamp: number }
interface MetricsData {
  total_requests: number; avg_duration_ms: number; p50_ms: number; p95_ms: number; p99_ms: number
  endpoints: Record<string, EndpointStats>; recent: RecentReq[]
}

const loading = ref(false)
const data = ref<MetricsData | null>(null)
const loadError = ref(false)

function formatTime(ts: number): string {
  return new Date(ts * 1000).toLocaleTimeString('zh-CN')
}

async function fetchMetrics() {
  loading.value = true
  loadError.value = false
  try {
    const res = await fetch('/api/metrics')
    data.value = await res.json()
  } catch (e) {
    console.error('Failed to fetch metrics:', e)
    loadError.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchMetrics())
</script>

<style scoped>
.metrics-view { padding-bottom: 40px; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
h2 { font-size: 1.5rem; font-weight: 600; color: var(--primary); }
h3 { font-size: 1.1rem; font-weight: 600; margin-bottom: 12px; color: var(--primary); }
.action-btn { padding: 8px 16px; border: 1px solid var(--border); border-radius: 8px; background: var(--card); color: var(--primary); cursor: pointer; font-size: 0.85rem; }
.loading { text-align: center; padding: 40px; color: var(--text-secondary); }
.summary-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; margin-bottom: 32px; }
.summary-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; text-align: center; }
.summary-value { font-size: 1.8rem; font-weight: 700; color: var(--primary); }
.summary-label { font-size: 0.8rem; color: var(--text-secondary); margin-top: 4px; }
.metrics-section { margin-bottom: 28px; }
.table-wrap { overflow-x: auto; }
.metrics-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.metrics-table th { text-align: left; padding: 10px 12px; border-bottom: 2px solid var(--border); color: var(--text-secondary); font-weight: 600; }
.metrics-table td { padding: 8px 12px; border-bottom: 1px solid var(--border); }
.endpoint-cell { font-family: monospace; font-size: 0.8rem; }
.time-cell { white-space: nowrap; font-size: 0.8rem; }
.method-badge { padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
.method-get { background: var(--info-bg); color: var(--info-text); }
.method-post { background: var(--success-bg); color: var(--success-text); }
.method-put { background: var(--warn-bg); color: var(--warn-text); }
.method-patch { background: var(--error-bg); color: var(--error-text); }
.method-delete { background: var(--error-bg); color: var(--error-text); }
.status-badge { padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
.status-ok { background: var(--success-bg); color: var(--success-text); }
.status-err { background: var(--error-bg); color: var(--error-text); }

/* Responsive */
@media (max-width: 767px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .summary-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .summary-value {
    font-size: 1.4rem;
  }
}
</style>
