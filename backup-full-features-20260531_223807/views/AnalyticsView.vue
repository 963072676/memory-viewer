<template>
  <div class="analytics-view">
    <div class="analytics-header">
      <h2>📊 API 使用分析</h2>
      <div class="header-controls">
        <select v-model="period" @change="loadAll" class="period-select">
          <option value="1h">1小时</option>
          <option value="24h">24小时</option>
          <option value="7d">7天</option>
          <option value="30d">30天</option>
        </select>
        <button class="btn-refresh" @click="loadAll" :disabled="loading">🔄 刷新</button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="summary-cards">
      <div class="card">
        <div class="card-icon">📨</div>
        <div class="card-content">
          <div class="card-value">{{ summary.total_requests }}</div>
          <div class="card-label">总请求数</div>
        </div>
      </div>
      <div class="card">
        <div class="card-icon">⚡</div>
        <div class="card-content">
          <div class="card-value">{{ summary.avg_latency_ms }}ms</div>
          <div class="card-label">平均延迟</div>
        </div>
      </div>
      <div class="card">
        <div class="card-icon">❌</div>
        <div class="card-content">
          <div class="card-value">{{ summary.error_rate }}%</div>
          <div class="card-label">错误率</div>
        </div>
      </div>
      <div class="card">
        <div class="card-icon">⏱️</div>
        <div class="card-content">
          <div class="card-value">{{ summary.p95_ms }}ms</div>
          <div class="card-label">P95 延迟</div>
        </div>
      </div>
    </div>

    <!-- Charts -->
    <UsageChart title="📈 请求趋势" endpoint="/analytics/trends" valueKey="requests" labelKey="timestamp" />

    <!-- Endpoint Breakdown -->
    <div class="endpoints-section">
      <h3>🔥 热门端点</h3>
      <div v-if="endpoints.length === 0" class="empty-hint">暂无端点数据</div>
      <div v-else class="endpoint-table">
        <div class="endpoint-header">
          <span>端点</span>
          <span>请求数</span>
          <span>平均延迟</span>
          <span>错误率</span>
        </div>
        <div v-for="ep in endpoints" :key="ep.endpoint" class="endpoint-row">
          <span class="endpoint-name">{{ ep.endpoint }}</span>
          <span class="endpoint-count">{{ ep.count }}</span>
          <span class="endpoint-latency">{{ ep.avg_ms }}ms</span>
          <span class="endpoint-error" :class="{ 'has-errors': ep.error_rate > 0 }">{{ ep.error_rate }}%</span>
        </div>
      </div>
    </div>

    <!-- LLM Cost Breakdown -->
    <div class="cost-section">
      <h3>💰 LLM 成本分析</h3>
      <div v-if="costs.features?.length === 0" class="empty-hint">暂无 LLM 使用数据</div>
      <template v-else>
        <div class="cost-summary">
          <span>总 Token（输入）: <strong>{{ costs.total_tokens_in }}</strong></span>
          <span>总 Token（输出）: <strong>{{ costs.total_tokens_out }}</strong></span>
          <span>预估成本: <strong>${{ costs.total_estimated_cost }}</strong></span>
        </div>
        <div class="cost-table">
          <div class="cost-header">
            <span>功能</span>
            <span>调用次数</span>
            <span>输入 Token</span>
            <span>输出 Token</span>
            <span>预估成本</span>
          </div>
          <div v-for="f in costs.features" :key="f.feature" class="cost-row">
            <span>{{ f.feature }}</span>
            <span>{{ f.calls }}</span>
            <span>{{ f.tokens_in }}</span>
            <span>{{ f.tokens_out }}</span>
            <span>${{ f.estimated_cost }}</span>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'
import UsageChart from '@/components/Layout/UsageChart.vue'

const toast = useToast()
const loading = ref(false)
const period = ref('24h')

const summary = ref({
  total_requests: 0,
  avg_latency_ms: 0,
  error_rate: 0,
  p50_ms: 0,
  p95_ms: 0,
})

const endpoints = ref<any[]>([])
const costs = ref<any>({})

async function loadAll() {
  loading.value = true
  try {
    const [usageRes, epRes, costRes] = await Promise.all([
      request<any>(`/analytics/usage?period=${period.value}`),
      request<any>(`/analytics/endpoints?period=${period.value}`),
      request<any>('/analytics/costs'),
    ])
    summary.value = usageRes
    endpoints.value = epRes.endpoints || []
    costs.value = costRes
  } catch (e: any) {
    toast.error(e.message || '加载分析数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => loadAll())
</script>

<style scoped>
.analytics-view {
  padding-bottom: 40px;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.analytics-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary, #007aff);
  margin: 0;
}

.header-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.period-select {
  padding: 6px 10px;
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px;
  background: var(--card, #fff);
  font-size: 0.85rem;
  font-family: var(--font);
  color: var(--text, #1d1d1f);
}

.btn-refresh {
  padding: 8px 14px;
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px;
  background: var(--card, #fff);
  color: var(--primary, #007aff);
  font-size: 0.8rem;
  cursor: pointer;
  font-family: var(--font);
}

.btn-refresh:disabled { opacity: 0.5; }

/* Summary cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--card, #fff);
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px;
}

.card-icon {
  font-size: 1.8rem;
}

.card-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--primary, #007aff);
}

.card-label {
  font-size: 0.75rem;
  color: var(--text-secondary, #86868b);
}

/* Endpoint table */
.endpoints-section,
.cost-section {
  background: var(--card, #fff);
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.endpoints-section h3,
.cost-section h3 {
  margin: 0 0 12px;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text, #1d1d1f);
}

.empty-hint {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary, #86868b);
  font-size: 0.85rem;
}

.endpoint-table,
.cost-table {
  width: 100%;
  border-collapse: collapse;
}

.endpoint-header,
.cost-header {
  display: grid;
  grid-template-columns: 3fr 1fr 1fr 1fr;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border, #e5e5ea);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary, #86868b);
}

.cost-header {
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
}

.endpoint-row,
.cost-row {
  display: grid;
  grid-template-columns: 3fr 1fr 1fr 1fr;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border, #e5e5ea);
  font-size: 0.8rem;
  color: var(--text, #1d1d1f);
}

.cost-row {
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
}

.endpoint-name {
  font-family: monospace;
  font-size: 0.75rem;
  word-break: break-all;
}

.endpoint-error.has-errors {
  color: var(--error, #ff3b30);
  font-weight: 600;
}

.cost-summary {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
  font-size: 0.85rem;
  color: var(--text-secondary, #86868b);
  flex-wrap: wrap;
}

.cost-summary strong {
  color: var(--primary, #007aff);
}
</style>
