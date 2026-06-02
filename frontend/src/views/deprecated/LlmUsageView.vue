<template>
  <div class="llm-usage">
    <div class="view-header">
      <h1>💰 LLM Usage & Cost Dashboard</h1>
      <p class="subtitle">Track token consumption and costs across all AI-powered features</p>
      <div class="period-selector">
        <button v-for="p in periods" :key="p.value" class="period-btn" :class="{ active: period === p.value }" @click="period = p.value; fetchUsage()">
          {{ p.label }}
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="summary-cards">
      <div class="stat-card">
        <span class="stat-icon">🔤</span>
        <div class="stat-info">
          <span class="stat-value">{{ summary.total_tokens?.toLocaleString() || '0' }}</span>
          <span class="stat-label">Total Tokens</span>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon">💵</span>
        <div class="stat-info">
          <span class="stat-value">${{ summary.total_cost?.toFixed(2) || '0.00' }}</span>
          <span class="stat-label">Total Cost</span>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon">📊</span>
        <div class="stat-info">
          <span class="stat-value">{{ summary.total_requests?.toLocaleString() || '0' }}</span>
          <span class="stat-label">Total Requests</span>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon">⚡</span>
        <div class="stat-info">
          <span class="stat-value">{{ summary.avg_tokens_per_request?.toFixed(0) || '0' }}</span>
          <span class="stat-label">Avg Tokens/Request</span>
        </div>
      </div>
    </div>

    <!-- Feature Breakdown -->
    <div class="feature-breakdown">
      <h2>Usage by Feature</h2>
      <div class="feature-table">
        <div class="table-header">
          <span>Feature</span>
          <span>Requests</span>
          <span>Tokens</span>
          <span>Cost</span>
          <span>% of Total</span>
        </div>
        <div v-for="feat in features" :key="feat.name" class="table-row">
          <span class="feature-name">{{ feat.icon }} {{ feat.name }}</span>
          <span>{{ feat.requests.toLocaleString() }}</span>
          <span>{{ feat.tokens.toLocaleString() }}</span>
          <span>${{ feat.cost.toFixed(2) }}</span>
          <div class="usage-bar-cell">
            <div class="usage-bar" :style="{ width: feat.percentage + '%' }"></div>
            <span class="usage-pct">{{ feat.percentage.toFixed(1) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Trends -->
    <div class="trends-section">
      <h2>Daily Trends</h2>
      <div class="trend-chart">
        <div class="chart-bars">
          <div v-for="day in trends" :key="day.date" class="chart-bar-group">
            <div class="chart-bar" :style="{ height: (day.tokens / maxTrendTokens * 100) + '%' }" :title="`${day.date}: ${day.tokens} tokens`"></div>
            <span class="chart-label">{{ day.date.slice(5) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Cost Optimization Tips -->
    <div class="tips-section">
      <h2>💡 Cost Optimization Tips</h2>
      <div class="tips-list">
        <div v-for="tip in tips" :key="tip.title" class="tip-card">
          <span class="tip-icon">{{ tip.icon }}</span>
          <div class="tip-content">
            <h4>{{ tip.title }}</h4>
            <p>{{ tip.description }}</p>
          </div>
          <span class="tip-savings">Save up to {{ tip.savings }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface UsageSummary {
  total_tokens: number
  total_cost: number
  total_requests: number
  avg_tokens_per_request: number
}

interface FeatureUsage {
  name: string
  icon: string
  requests: number
  tokens: number
  cost: number
  percentage: number
}

interface TrendDay {
  date: string
  tokens: number
  cost: number
}

const period = ref('7d')
const periods = [
  { value: '1d', label: 'Today' },
  { value: '7d', label: '7 Days' },
  { value: '30d', label: '30 Days' },
  { value: '90d', label: '90 Days' },
]

const summary = ref<UsageSummary>({ total_tokens: 0, total_cost: 0, total_requests: 0, avg_tokens_per_request: 0 })
const features = ref<FeatureUsage[]>([])
const trends = ref<TrendDay[]>([])
const maxTrendTokens = computed(() => Math.max(...trends.value.map(d => d.tokens), 1))

const tips = [
  { icon: '🎯', title: 'Use shorter prompts', description: 'Reduce NLQ and RAG prompt sizes to save tokens.', savings: '20-30%' },
  { icon: '📦', title: 'Batch digest generation', description: 'Generate weekly instead of daily digests.', savings: '85%' },
  { icon: '🔍', title: 'Cache RAG responses', description: 'Enable response caching for repeated queries.', savings: '40-60%' },
  { icon: '⚙️', title: 'Set token budgets', description: 'Configure max_tokens per feature in governance policies.', savings: '15-25%' },
]

async function fetchUsage() {
  try {
    const res = await fetch(`/api/llm-usage/summary?period=${period.value}`)
    if (res.ok) {
      const data = await res.json()
      summary.value = data.summary || summary.value
      features.value = data.features || []
      trends.value = data.trends || []
    }
  } catch {
    // Use mock data for demo
    summary.value = { total_tokens: 1250000, total_cost: 18.75, total_requests: 3420, avg_tokens_per_request: 365 }
    features.value = [
      { name: 'RAG Search', icon: '🔍', requests: 1200, tokens: 480000, cost: 7.20, percentage: 38.4 },
      { name: 'AI Digest', icon: '📋', requests: 45, tokens: 225000, cost: 3.38, percentage: 18.0 },
      { name: 'NLQ', icon: '💬', requests: 890, tokens: 267000, cost: 4.01, percentage: 21.4 },
      { name: 'Auto-Tag', icon: '🏷️', requests: 1100, tokens: 165000, cost: 2.48, percentage: 13.2 },
      { name: 'Conflict Detection', icon: '⚡', requests: 85, tokens: 68000, cost: 1.02, percentage: 5.4 },
      { name: 'Embeddings', icon: '🧮', requests: 100, tokens: 45000, cost: 0.68, percentage: 3.6 },
    ]
    trends.value = Array.from({ length: 7 }, (_, i) => ({
      date: new Date(Date.now() - (6 - i) * 86400000).toISOString().split('T')[0],
      tokens: Math.floor(150000 + Math.random() * 100000),
      cost: 0,
    }))
  }
}

onMounted(fetchUsage)
</script>

<style scoped>
.llm-usage { padding: 20px; }
.view-header h1 { font-size: 1.5rem; margin-bottom: 4px; }
.subtitle { color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 16px; }
.period-selector { display: flex; gap: 8px; margin-bottom: 20px; }
.period-btn { padding: 6px 14px; border: 1px solid var(--border); border-radius: 6px; background: var(--card); cursor: pointer; font-size: 0.8rem; color: var(--text-secondary); }
.period-btn.active { background: var(--accent); color: white; border-color: var(--accent); }
.summary-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; display: flex; align-items: center; gap: 12px; }
.stat-icon { font-size: 1.5rem; }
.stat-value { font-size: 1.4rem; font-weight: 700; display: block; }
.stat-label { font-size: 0.75rem; color: var(--text-secondary); }
.feature-breakdown { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; margin-bottom: 24px; }
.feature-breakdown h2 { font-size: 1rem; margin-bottom: 12px; }
.feature-table { width: 100%; }
.table-header, .table-row { display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr 1.5fr; padding: 8px 0; align-items: center; font-size: 0.85rem; }
.table-header { font-weight: 600; color: var(--text-secondary); border-bottom: 1px solid var(--border); }
.table-row { border-bottom: 1px solid var(--border); }
.feature-name { font-weight: 500; }
.usage-bar-cell { display: flex; align-items: center; gap: 8px; }
.usage-bar { height: 8px; background: var(--accent); border-radius: 4px; min-width: 4px; }
.usage-pct { font-size: 0.75rem; color: var(--text-secondary); }
.trends-section { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; margin-bottom: 24px; }
.trends-section h2 { font-size: 1rem; margin-bottom: 12px; }
.chart-bars { display: flex; align-items: flex-end; gap: 8px; height: 150px; }
.chart-bar-group { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; justify-content: flex-end; }
.chart-bar { width: 100%; background: var(--accent); border-radius: 4px 4px 0 0; min-height: 4px; transition: height 0.3s; }
.chart-label { font-size: 0.65rem; color: var(--text-secondary); margin-top: 4px; }
.tips-section { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; }
.tips-section h2 { font-size: 1rem; margin-bottom: 12px; }
.tips-list { display: flex; flex-direction: column; gap: 12px; }
.tip-card { display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--bg); border-radius: var(--radius); }
.tip-icon { font-size: 1.2rem; }
.tip-content { flex: 1; }
.tip-content h4 { font-size: 0.85rem; margin: 0 0 2px; }
.tip-content p { font-size: 0.75rem; color: var(--text-secondary); margin: 0; }
.tip-savings { font-size: 0.75rem; color: var(--success-text); font-weight: 600; }
</style>
