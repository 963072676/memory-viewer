<template>
  <div class="anomalies-view">
    <div class="anomalies-header">
      <h2>⚠️ 异常检测</h2>
      <div class="header-actions">
        <button class="btn-check" :disabled="checking" @click="triggerCheck">
          {{ checking ? '检测中...' : '🔍 立即检测' }}
        </button>
        <button class="btn-refresh" @click="loadAll">🔄 刷新</button>
      </div>
    </div>

    <!-- Health Dashboard -->
    <div class="health-section">
      <div class="health-ring-container">
        <svg viewBox="0 0 120 120" class="health-ring">
          <circle cx="60" cy="60" r="52" fill="none" stroke="var(--border, #e5e5ea)" stroke-width="8" />
          <circle
            cx="60" cy="60" r="52"
            fill="none"
            :stroke="healthColor"
            stroke-width="8"
            stroke-linecap="round"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="circumference - (circumference * (healthScore / 100))"
            transform="rotate(-90 60 60)"
            class="health-ring-fill"
          />
          <text x="60" y="55" text-anchor="middle" class="health-ring-value">{{ healthScore }}</text>
          <text x="60" y="72" text-anchor="middle" class="health-ring-label">健康度</text>
        </svg>
      </div>
      <div class="health-breakdown">
        <div
          v-for="(dim, idx) in healthDimensions"
          :key="idx"
          class="health-dim"
        >
          <div class="dim-header">
            <span class="dim-name">{{ dim.name }}</span>
            <span class="dim-score" :style="{ color: dim.color }">{{ dim.score }}</span>
          </div>
          <div class="dim-bar">
            <div class="dim-bar-fill" :style="{ width: dim.score + '%', background: dim.color }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Anomaly Timeline -->
    <div class="timeline-section">
      <div class="section-header">
        <h3>📋 异常时间线</h3>
        <div class="filter-chips">
          <button
            v-for="f in severityFilters"
            :key="f.value"
            class="filter-chip"
            :class="{ active: activeSeverity === f.value }"
            @click="activeSeverity = f.value"
          >
            {{ f.icon }} {{ f.label }}
          </button>
        </div>
      </div>

      <div v-if="loading && anomalies.length === 0" class="loading-state">加载中...</div>
      <div v-else-if="filteredAnomalies.length === 0" class="empty-state">暂无异常事件</div>
      <div v-else class="anomaly-timeline">
        <div
          v-for="anomaly in filteredAnomalies"
          :key="anomaly.id"
          class="anomaly-item"
          :class="'severity-' + anomaly.severity"
        >
          <div class="anomaly-dot" :class="'dot-' + anomaly.severity"></div>
          <div class="anomaly-content">
            <div class="anomaly-title-row">
              <span class="anomaly-title">{{ anomaly.title }}</span>
              <span class="anomaly-time">{{ formatTime(anomaly.detected_at) }}</span>
            </div>
            <div class="anomaly-desc">{{ anomaly.description }}</div>
            <div class="anomaly-meta">
              <span class="anomaly-type-badge">{{ anomaly.anomaly_type }}</span>
              <span class="anomaly-severity-badge" :class="'severity-' + anomaly.severity">
                {{ anomaly.severity }}
              </span>
              <span v-if="anomaly.affected_count" class="anomaly-affected">
                影响 {{ anomaly.affected_count }} 条记忆
              </span>
            </div>
            <div v-if="anomaly.suggested_action" class="anomaly-action">
              💡 建议: {{ anomaly.suggested_action }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Alert Configuration -->
    <div class="config-section">
      <div class="section-header" @click="showConfig = !showConfig">
        <h3>⚙️ 告警配置</h3>
        <span>{{ showConfig ? '▲' : '▼' }}</span>
      </div>
      <transition name="expand">
        <div v-if="showConfig" class="config-body">
          <div v-if="loadingThresholds" class="loading-state">加载配置中...</div>
          <div v-else class="config-list">
            <div v-for="(thresh, key) in thresholds" :key="key" class="config-item">
              <div class="config-label">{{ key }}</div>
              <div class="config-value-row">
                <input
                  type="number"
                  :value="thresh"
                  class="config-input"
                  @change="updateThreshold(String(key), Number(($event.target as HTMLInputElement).value))"
                />
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'

interface Anomaly {
  id: string
  title: string
  description: string
  anomaly_type: string
  severity: 'info' | 'warning' | 'critical'
  detected_at: string
  affected_count?: number
  suggested_action?: string
  resolved: boolean
}

interface HealthScoreResponse {
  overall_score: number
  color: string
  dimensions: Record<string, { score: number; description: string }>
}

interface CheckResponse {
  success: boolean
  new_anomalies: number
  anomalies: Anomaly[]
}

const toast = useToast()

const anomalies = ref<Anomaly[]>([])
const healthScore = ref(0)
const healthDimensions = ref<Array<{ name: string; score: number; color: string }>>([])
const thresholds = ref<Record<string, number>>({})
const loading = ref(false)
const checking = ref(false)
const loadingThresholds = ref(false)
const activeSeverity = ref<string | null>(null)
const showConfig = ref(false)

const circumference = 2 * Math.PI * 52

const healthColor = computed(() => {
  if (healthScore.value >= 80) return '#34c759'
  if (healthScore.value >= 50) return '#ff9500'
  return '#ff3b30'
})

const severityFilters = [
  { value: '' as string, icon: '📋', label: '全部' },
  { value: 'critical', icon: '🔴', label: '严重' },
  { value: 'warning', icon: '🟡', label: '警告' },
  { value: 'info', icon: '🔵', label: '信息' },
]

const filteredAnomalies = computed(() => {
  let result = [...anomalies.value].sort((a, b) =>
    new Date(b.detected_at).getTime() - new Date(a.detected_at).getTime()
  )
  if (activeSeverity.value) {
    result = result.filter(a => a.severity === activeSeverity.value)
  }
  return result
})

function dimensionColor(score: number): string {
  if (score >= 80) return '#34c759'
  if (score >= 50) return '#ff9500'
  return '#ff3b30'
}

async function loadAnomalies() {
  loading.value = true
  try {
    const res = await request<{ anomalies: Anomaly[] }>('/anomalies?limit=100')
    anomalies.value = res.anomalies || []
  } catch (e: any) {
    toast.error(e.message || '加载异常列表失败')
  } finally {
    loading.value = false
  }
}

async function loadHealth() {
  try {
    const res = await request<any>('/anomalies/health')
    // Backend returns { overall, memory_stability, strength_health, ... }
    healthScore.value = res.overall ?? res.overall_score ?? 0

    const dims: Array<{ name: string; score: number; color: string }> = []
    // Handle both flat backend format and nested frontend format
    if (res.dimensions) {
      for (const [key, val] of Object.entries(res.dimensions || {})) {
        dims.push({
          name: key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
          score: (val as any).score ?? 0,
          color: dimensionColor((val as any).score ?? 0),
        })
      }
    } else {
      // Flat backend format
      const dimKeys = ['memory_stability', 'strength_health', 'api_performance', 'error_rate']
      for (const key of dimKeys) {
        if (res[key] !== undefined) {
          dims.push({
            name: key.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase()),
            score: res[key],
            color: dimensionColor(res[key]),
          })
        }
      }
    }
    healthDimensions.value = dims
  } catch {
    // silent
  }
}

async function loadThresholds() {
  loadingThresholds.value = true
  try {
    const res = await request<{ thresholds: Record<string, number> }>('/anomalies/thresholds')
    thresholds.value = res.thresholds || {}
  } catch {
    // silent
  } finally {
    loadingThresholds.value = false
  }
}

async function triggerCheck() {
  checking.value = true
  try {
    const res = await request<CheckResponse>('/anomalies/check', { method: 'POST' })
    toast.success(`检测完成，发现 ${res.new_anomalies} 个新异常`)
    await loadAnomalies()
    await loadHealth()
  } catch (e: any) {
    toast.error(e.message || '异常检测失败')
  } finally {
    checking.value = false
  }
}

async function updateThreshold(key: string, value: number) {
  try {
    await request('/anomalies/thresholds', {
      method: 'PUT',
      body: JSON.stringify({ key, value }),
    })
    thresholds.value[key] = value
    toast.success(`阈值 ${key} 已更新`)
  } catch (e: any) {
    toast.error(e.message || '更新阈值失败')
  }
}

function formatTime(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleString('zh-CN')
  } catch {
    return dateStr
  }
}

function loadAll() {
  loadAnomalies()
  loadHealth()
  loadThresholds()
}

onMounted(loadAll)
</script>

<style scoped>
.anomalies-view {
  padding-bottom: 40px;
}

.anomalies-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.anomalies-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary, #007aff);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn-check,
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

.btn-check:hover,
.btn-refresh:hover {
  background: var(--tag-bg, #f2f2f7);
}

.btn-check:disabled {
  opacity: 0.5;
}

/* Health Section */
.health-section {
  display: flex;
  gap: 32px;
  align-items: center;
  padding: 24px;
  background: var(--card, #fff);
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px;
  margin-bottom: 24px;
}

.health-ring-container {
  flex-shrink: 0;
}

.health-ring {
  width: 140px;
  height: 140px;
}

.health-ring-fill {
  transition: stroke-dashoffset 0.8s ease;
}

.health-ring-value {
  font-size: 1.8rem;
  font-weight: 700;
  fill: var(--text, #1d1d1f);
}

.health-ring-label {
  font-size: 0.7rem;
  fill: var(--text-secondary, #86868b);
}

.health-breakdown {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.health-dim {
  width: 100%;
}

.dim-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.dim-name {
  font-size: 0.8rem;
  color: var(--text, #1d1d1f);
  text-transform: capitalize;
}

.dim-score {
  font-size: 0.8rem;
  font-weight: 600;
}

.dim-bar {
  height: 6px;
  background: var(--border, #e5e5ea);
  border-radius: 3px;
  overflow: hidden;
}

.dim-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}

/* Timeline */
.timeline-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text, #1d1d1f);
  margin: 0;
}

.filter-chips {
  display: flex;
  gap: 6px;
}

.filter-chip {
  padding: 4px 10px;
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px;
  background: var(--bg, #fff);
  font-size: 0.75rem;
  cursor: pointer;
  font-family: var(--font);
  color: var(--text, #1d1d1f);
  transition: all 0.15s ease;
}

.filter-chip.active {
  border-color: var(--primary, #007aff);
  background: rgba(0, 122, 255, 0.05);
  color: var(--primary, #007aff);
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary, #86868b);
  font-size: 0.9rem;
}

.anomaly-timeline {
  position: relative;
  padding-left: 24px;
}

.anomaly-timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--border, #e5e5ea);
}

.anomaly-item {
  position: relative;
  margin-bottom: 16px;
  padding: 14px 16px;
  background: var(--card, #fff);
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 10px;
  transition: border-color 0.15s ease;
}

.anomaly-item:hover {
  border-color: var(--primary, #007aff);
}

.anomaly-item.severity-critical {
  border-left: 3px solid #ff3b30;
}

.anomaly-item.severity-warning {
  border-left: 3px solid #ff9500;
}

.anomaly-item.severity-info {
  border-left: 3px solid #007aff;
}

.anomaly-dot {
  position: absolute;
  left: -20px;
  top: 18px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid var(--card, #fff);
}

.dot-critical { background: #ff3b30; }
.dot-warning { background: #ff9500; }
.dot-info { background: #007aff; }

.anomaly-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 4px;
}

.anomaly-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text, #1d1d1f);
}

.anomaly-time {
  font-size: 0.7rem;
  color: var(--text-secondary, #86868b);
  white-space: nowrap;
}

.anomaly-desc {
  font-size: 0.8rem;
  color: var(--text-secondary, #86868b);
  line-height: 1.4;
  margin-bottom: 8px;
}

.anomaly-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.anomaly-type-badge {
  font-size: 0.65rem;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--tag-bg, #f2f2f7);
  color: var(--text-secondary, #86868b);
  font-weight: 600;
}

.anomaly-severity-badge {
  font-size: 0.65rem;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.anomaly-severity-badge.severity-critical {
  background: #ffebee;
  color: #c62828;
}

.anomaly-severity-badge.severity-warning {
  background: #fff3e0;
  color: #e65100;
}

.anomaly-severity-badge.severity-info {
  background: #e3f2fd;
  color: #1565c0;
}

.anomaly-affected {
  font-size: 0.7rem;
  color: var(--text-secondary, #86868b);
}

.anomaly-action {
  margin-top: 8px;
  font-size: 0.8rem;
  color: var(--primary, #007aff);
  padding: 8px 10px;
  background: rgba(0, 122, 255, 0.05);
  border-radius: 8px;
}

/* Config section */
.config-section {
  background: var(--card, #fff);
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px;
  overflow: hidden;
}

.config-section .section-header {
  padding: 14px 20px;
  cursor: pointer;
  margin-bottom: 0;
}

.config-section .section-header:hover {
  background: var(--bg-secondary, #f9f9f9);
}

.config-body {
  padding: 0 20px 16px;
}

.config-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.config-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary, #86868b);
  text-transform: capitalize;
}

.config-input {
  padding: 6px 10px;
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px;
  font-size: 0.85rem;
  font-family: var(--font);
  width: 100%;
  box-sizing: border-box;
}

.config-input:focus {
  outline: none;
  border-color: var(--primary, #007aff);
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 500px;
}
</style>
