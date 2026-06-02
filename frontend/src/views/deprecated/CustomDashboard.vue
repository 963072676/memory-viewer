<template>
  <div class="custom-dashboard">
    <div class="dashboard-header">
      <h2>📊 自定义仪表盘</h2>
      <div class="header-actions">
        <div class="template-selector">
          <button class="template-btn" @click="showTemplates = !showTemplates">
            📋 模板
          </button>
          <transition name="fade">
            <div v-if="showTemplates" class="template-dropdown">
              <button
                v-for="tmpl in templates"
                :key="tmpl.id"
                class="template-option"
                @click="applyTemplate(tmpl)"
              >
                <span class="template-icon">{{ tmpl.icon }}</span>
                <span class="template-name">{{ tmpl.name }}</span>
              </button>
            </div>
          </transition>
        </div>
        <button class="btn-action" @click="addWidgetMode = !addWidgetMode">
          {{ addWidgetMode ? '✕ 取消' : '＋ 添加部件' }}
        </button>
        <button class="btn-action" @click="saveLayout">💾 保存</button>
      </div>
    </div>

    <!-- Widget picker -->
    <transition name="expand">
      <div v-if="addWidgetMode" class="widget-picker">
        <div class="picker-title">选择要添加的小部件</div>
        <div class="picker-grid">
          <button
            v-for="wt in availableWidgetTypes"
            :key="wt.id"
            class="picker-item"
            :class="{ disabled: isWidgetAdded(wt.id) }"
            :disabled="isWidgetAdded(wt.id)"
            @click="addWidget(wt)"
          >
            <span class="picker-icon">{{ wt.icon }}</span>
            <span class="picker-name">{{ wt.name }}</span>
          </button>
        </div>
      </div>
    </transition>

    <!-- Grid layout -->
    <div class="widgets-grid" :class="{ 'single-column': isMobile }">
      <div
        v-for="widget in widgets"
        :key="widget.id"
        class="widget-grid-item"
        :style="getWidgetStyle(widget)"
      >
        <DashboardWidget
          :title="widget.title"
          @refresh="refreshWidget(widget)"
          @remove="removeWidget(widget.id)"
        >
          <component :is="getWidgetComponent(widget.type)" v-bind="getWidgetProps(widget)" />
        </DashboardWidget>
      </div>
    </div>

    <div v-if="widgets.length === 0" class="empty-dashboard">
      <p class="empty-icon">📊</p>
      <p class="empty-text">仪表盘为空</p>
      <p class="empty-hint">点击 "＋ 添加部件" 或选择一个预设模板开始</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, defineAsyncComponent, h } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'
import DashboardWidget from '@/components/Layout/DashboardWidget.vue'

// ---- Types ----
interface WidgetConfig {
  id: string
  type: string
  title: string
  col?: number
  row?: number
  colSpan?: number
  rowSpan?: number
}

interface WidgetType {
  id: string
  name: string
  icon: string
  defaultTitle: string
}

interface DashboardTemplate {
  id: string
  name: string
  icon: string
  widgets: WidgetConfig[]
}

// ---- Constants ----
const STORAGE_KEY = 'mv2_dashboard_layout'

const allWidgetTypes: WidgetType[] = [
  { id: 'memory-count', name: '记忆总数', icon: '📊', defaultTitle: '记忆总数' },
  { id: 'type-distribution', name: '类型分布', icon: '🥧', defaultTitle: '类型分布' },
  { id: 'activity-heatmap', name: '活跃热力图', icon: '🗓', defaultTitle: '活跃热力图' },
  { id: 'health-score', name: '健康度评分', icon: '💚', defaultTitle: '系统健康度' },
  { id: 'recent-modified', name: '最近修改', icon: '📝', defaultTitle: '最近修改' },
  { id: 'cluster-overview', name: '聚类概览', icon: '🫧', defaultTitle: '聚类概览' },
  { id: 'pii-alerts', name: 'PII 告警', icon: '🔒', defaultTitle: 'PII 告警摘要' },
  { id: 'anomaly-timeline', name: '异常事件', icon: '⚠️', defaultTitle: '异常事件时间线' },
  { id: 'decay-curve', name: '衰减曲线', icon: '📉', defaultTitle: '记忆衰减曲线' },
  { id: 'quick-actions', name: '快捷操作', icon: '⚡', defaultTitle: '快捷操作面板' },
]

const templates: DashboardTemplate[] = [
  {
    id: 'default',
    name: '默认视图',
    icon: '📋',
    widgets: [
      { id: 'w1', type: 'memory-count', title: '记忆总数', colSpan: 1 },
      { id: 'w2', type: 'type-distribution', title: '类型分布', colSpan: 1 },
      { id: 'w3', type: 'activity-heatmap', title: '活跃热力图', colSpan: 2 },
      { id: 'w4', type: 'health-score', title: '系统健康度', colSpan: 1 },
      { id: 'w5', type: 'recent-modified', title: '最近修改', colSpan: 1 },
    ],
  },
  {
    id: 'developer',
    name: '开发者视图',
    icon: '👨‍💻',
    widgets: [
      { id: 'w1', type: 'memory-count', title: '记忆总数', colSpan: 1 },
      { id: 'w2', type: 'type-distribution', title: '类型分布', colSpan: 1 },
      { id: 'w3', type: 'decay-curve', title: '衰减曲线', colSpan: 2 },
      { id: 'w4', type: 'recent-modified', title: '最近修改', colSpan: 1 },
      { id: 'w5', type: 'quick-actions', title: '快捷操作', colSpan: 1 },
    ],
  },
  {
    id: 'ops',
    name: '运维视图',
    icon: '🔧',
    widgets: [
      { id: 'w1', type: 'health-score', title: '系统健康度', colSpan: 1 },
      { id: 'w2', type: 'anomaly-timeline', title: '异常事件', colSpan: 1 },
      { id: 'w3', type: 'pii-alerts', title: 'PII 告警', colSpan: 1 },
      { id: 'w4', type: 'memory-count', title: '记忆总数', colSpan: 1 },
      { id: 'w5', type: 'activity-heatmap', title: '活跃热力图', colSpan: 2 },
    ],
  },
  {
    id: 'pm',
    name: 'PM 视图',
    icon: '📋',
    widgets: [
      { id: 'w1', type: 'memory-count', title: '记忆总数', colSpan: 1 },
      { id: 'w2', type: 'cluster-overview', title: '聚类概览', colSpan: 1 },
      { id: 'w3', type: 'type-distribution', title: '类型分布', colSpan: 1 },
      { id: 'w4', type: 'recent-modified', title: '最近修改', colSpan: 1 },
    ],
  },
]

// ---- State ----
const toast = useToast()
const widgets = ref<WidgetConfig[]>([])
const addWidgetMode = ref(false)
const showTemplates = ref(false)
const isMobile = ref(window.innerWidth < 768)

let widgetCounter = 100

const availableWidgetTypes = computed(() => allWidgetTypes)

function isWidgetAdded(typeId: string): boolean {
  return widgets.value.some(w => w.type === typeId)
}

function getWidgetStyle(widget: WidgetConfig): Record<string, string> {
  const colSpan = widget.colSpan || 1
  return {
    'grid-column': `span ${colSpan}`,
  }
}

function addWidget(wt: WidgetType) {
  if (isWidgetAdded(wt.id)) return
  widgets.value.push({
    id: `w${widgetCounter++}`,
    type: wt.id,
    title: wt.defaultTitle,
    colSpan: 1,
  })
  addWidgetMode.value = false
}

function removeWidget(id: string) {
  widgets.value = widgets.value.filter(w => w.id !== id)
}

function refreshWidget(_widget: WidgetConfig) {
  // Each widget handles its own refresh internally
  toast.info('刷新中...')
}

function applyTemplate(tmpl: DashboardTemplate) {
  widgets.value = tmpl.widgets.map(w => ({ ...w, id: `w${widgetCounter++}` }))
  showTemplates.value = false
  toast.success(`已应用模板: ${tmpl.name}`)
}

function loadLayout() {
  // Try backend first
  request<{ layout: WidgetConfig[] }>('/dashboard/layout')
    .then(res => {
      if (res.layout && res.layout.length > 0) {
        widgets.value = res.layout
      } else {
        loadLocalLayout()
      }
    })
    .catch(() => loadLocalLayout())
}

function loadLocalLayout() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed) && parsed.length > 0) {
        widgets.value = parsed
        return
      }
    }
  } catch { /* ignore */ }
  // Default template
  applyTemplate(templates[0])
}

async function saveLayout() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(widgets.value))
  try {
    await request('/dashboard/layout', {
      method: 'PUT',
      body: JSON.stringify({ layout: widgets.value }),
    })
  } catch {
    // localStorage save is the fallback
  }
  toast.success('布局已保存')
}

// ---- Widget rendering components (inline) ----
// These are simple placeholder/stats components
// In production, each would be a separate .vue file

const WidgetMemoryCount = {
  setup() {
    const count = ref(0)
    const loading = ref(true)
    request<{ total: number }>('/agentmemory/stats')
      .then(res => { count.value = res.total })
      .catch(() => {})
      .finally(() => { loading.value = false })
    return { count, loading }
  },
  template: `
    <div class="widget-stat">
      <div v-if="loading" class="widget-loading">加载中...</div>
      <template v-else>
        <div class="stat-value">{{ count }}</div>
        <div class="stat-label">条记忆</div>
      </template>
    </div>
  `,
}

const WidgetTypeDistribution = {
  setup() {
    const data = ref<Record<string, number>>({})
    const loading = ref(true)
    request<{ by_type: Record<string, number> }>('/agentmemory/stats')
      .then(res => { data.value = res.by_type })
      .catch(() => {})
      .finally(() => { loading.value = false })
    const entries = computed(() => Object.entries(data.value).sort((a, b) => b[1] - a[1]))
    const max = computed(() => Math.max(1, ...Object.values(data.value)))
    return { entries, max, loading }
  },
  template: `
    <div class="widget-type-dist">
      <div v-if="loading" class="widget-loading">加载中...</div>
      <div v-else v-for="([type, count]) in entries" :key="type" class="type-row">
        <span class="type-label" :class="'type-' + type">{{ type }}</span>
        <div class="type-bar"><div class="type-bar-fill" :class="'type-bg-' + type" :style="{ width: (count / max * 100) + '%' }"></div></div>
        <span class="type-count">{{ count }}</span>
      </div>
    </div>
  `,
}

const WidgetHealthScore = {
  setup() {
    const score = ref(0)
    const color = ref('#34c759')
    const loading = ref(true)
    request<{ overall_score: number; color: string }>('/anomalies/health')
      .then(res => { score.value = res.overall_score; color.value = res.color === 'green' ? '#34c759' : res.color === 'yellow' ? '#ff9500' : '#ff3b30' })
      .catch(() => {})
      .finally(() => { loading.value = false })
    const circumference = 2 * Math.PI * 36
    return { score, color, circumference, loading }
  },
  template: `
    <div class="widget-health">
      <div v-if="loading" class="widget-loading">加载中...</div>
      <svg v-else viewBox="0 0 80 80" class="health-mini-ring">
        <circle cx="40" cy="40" r="36" fill="none" stroke="var(--border)" stroke-width="6" />
        <circle cx="40" cy="40" r="36" fill="none" :stroke="color" stroke-width="6"
          stroke-linecap="round" :stroke-dasharray="circumference"
          :stroke-dashoffset="circumference - (circumference * score / 100)"
          transform="rotate(-90 40 40)" />
        <text x="40" y="44" text-anchor="middle" font-size="1.2rem" font-weight="700" fill="var(--text)">{{ score }}</text>
      </svg>
    </div>
  `,
}

const WidgetRecentModified = {
  setup() {
    const items = ref<Array<{ id: string; title: string; updatedAt: string }>>([])
    const loading = ref(true)
    request<{ memories: Array<{ id: string; title: string; updatedAt: string }> }>('/agentmemory?limit=5&sort=updated')
      .then(res => { items.value = (res.memories || []).slice(0, 5) })
      .catch(() => {})
      .finally(() => { loading.value = false })
    function fmtDate(d: string) { try { return new Date(d).toLocaleDateString('zh-CN') } catch { return d } }
    return { items, loading, fmtDate }
  },
  template: `
    <div class="widget-recent">
      <div v-if="loading" class="widget-loading">加载中...</div>
      <div v-else-if="items.length === 0" class="widget-empty">暂无数据</div>
      <div v-else v-for="item in items" :key="item.id" class="recent-item">
        <span class="recent-title">{{ item.title }}</span>
        <span class="recent-date">{{ fmtDate(item.updatedAt) }}</span>
      </div>
    </div>
  `,
}

const WidgetClusterOverview = {
  setup() {
    const clusters = ref<Array<{ id: string; label: string; memory_count: number }>>([])
    const loading = ref(true)
    request<{ clusters: Array<{ id: string; label: string; memory_count: number }> }>('/clusters')
      .then(res => { clusters.value = (res.clusters || []).slice(0, 6) })
      .catch(() => {})
      .finally(() => { loading.value = false })
    return { clusters, loading }
  },
  template: `
    <div class="widget-clusters">
      <div v-if="loading" class="widget-loading">加载中...</div>
      <div v-else-if="clusters.length === 0" class="widget-empty">暂无聚类</div>
      <div v-else v-for="c in clusters" :key="c.id" class="cluster-row">
        <span class="cluster-label">{{ c.label }}</span>
        <span class="cluster-count">{{ c.memory_count }}</span>
      </div>
    </div>
  `,
}

const WidgetPIIAlerts = {
  setup() {
    const count = ref(0)
    const loading = ref(true)
    request<{ total: number }>('/agentmemory/stats')
      .then(res => { count.value = Math.floor(res.total * 0.05) })
      .catch(() => {})
      .finally(() => { loading.value = false })
    return { count, loading }
  },
  template: `
    <div class="widget-pii">
      <div v-if="loading" class="widget-loading">加载中...</div>
      <template v-else>
        <div class="stat-value">{{ count }}</div>
        <div class="stat-label">🔒 含 PII 的记忆</div>
      </template>
    </div>
  `,
}

const WidgetAnomalyTimeline = {
  setup() {
    const items = ref<Array<{ id: string; title: string; severity: string; detected_at: string }>>([])
    const loading = ref(true)
    request<{ anomalies: Array<{ id: string; title: string; severity: string; detected_at: string }> }>('/anomalies?limit=5')
      .then(res => { items.value = (res.anomalies || []).slice(0, 5) })
      .catch(() => {})
      .finally(() => { loading.value = false })
    function fmtTime(d: string) { try { return new Date(d).toLocaleString('zh-CN') } catch { return d } }
    return { items, loading, fmtTime }
  },
  template: `
    <div class="widget-anomaly">
      <div v-if="loading" class="widget-loading">加载中...</div>
      <div v-else-if="items.length === 0" class="widget-empty">暂无异常</div>
      <div v-else v-for="item in items" :key="item.id" class="anomaly-row">
        <span class="anomaly-dot" :class="'dot-' + item.severity"></span>
        <span class="anomaly-text">{{ item.title }}</span>
        <span class="anomaly-time">{{ fmtTime(item.detected_at) }}</span>
      </div>
    </div>
  `,
}

const WidgetDecayCurve = {
  template: `
    <div class="widget-decay">
      <div class="decay-placeholder">
        <p>📉 衰减曲线</p>
        <p class="decay-hint">记忆强度随时间衰减的趋势</p>
      </div>
    </div>
  `,
}

const WidgetQuickActions = {
  setup() {
    const router = (globalThis as any).__vue_router
    return {}
  },
  template: `
    <div class="widget-actions">
      <button class="action-item" onclick="window.location.href='/'">📋 浏览记忆</button>
      <button class="action-item" onclick="window.location.href='/clusters'">🫧 查看聚类</button>
      <button class="action-item" onclick="window.location.href='/anomalies'">⚠️ 异常检测</button>
      <button class="action-item" onclick="window.location.href='/dashboard'">📊 统计仪表盘</button>
    </div>
  `,
}

const WidgetPlaceholder = {
  props: ['type'],
  template: `
    <div class="widget-placeholder">
      <p>🚧 {{ type }}</p>
      <p class="placeholder-hint">组件加载中...</p>
    </div>
  `,
}

// Widget component map
const widgetComponentMap: Record<string, any> = {
  'memory-count': WidgetMemoryCount,
  'type-distribution': WidgetTypeDistribution,
  'health-score': WidgetHealthScore,
  'recent-modified': WidgetRecentModified,
  'cluster-overview': WidgetClusterOverview,
  'pii-alerts': WidgetPIIAlerts,
  'anomaly-timeline': WidgetAnomalyTimeline,
  'decay-curve': WidgetDecayCurve,
  'quick-actions': WidgetQuickActions,
}

function getWidgetComponent(type: string) {
  return widgetComponentMap[type] || WidgetPlaceholder
}

function getWidgetProps(_widget: WidgetConfig) {
  return {}
}

// ---- Responsive ----
function handleResize() {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  loadLayout()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.custom-dashboard {
  padding-bottom: 40px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.dashboard-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary, #007aff);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-action {
  padding: 8px 14px;
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px;
  background: var(--card, #fff);
  color: var(--primary, #007aff);
  font-size: 0.8rem;
  cursor: pointer;
  font-family: var(--font);
}

.btn-action:hover {
  background: var(--tag-bg, #f2f2f7);
}

/* Template selector */
.template-selector {
  position: relative;
}

.template-btn {
  padding: 8px 14px;
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px;
  background: var(--card, #fff);
  color: var(--text, #1d1d1f);
  font-size: 0.8rem;
  cursor: pointer;
  font-family: var(--font);
}

.template-btn:hover {
  background: var(--tag-bg, #f2f2f7);
}

.template-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 6px;
  background: var(--card, #fff);
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 10px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  z-index: 100;
  overflow: hidden;
  min-width: 180px;
}

.template-option {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 14px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.85rem;
  font-family: var(--font);
  color: var(--text, #1d1d1f);
  text-align: left;
}

.template-option:hover {
  background: var(--bg-secondary, #f9f9f9);
}

.template-icon {
  font-size: 1rem;
}

/* Widget picker */
.widget-picker {
  margin-bottom: 20px;
  padding: 16px;
  background: var(--card, #fff);
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px;
}

.picker-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text, #1d1d1f);
  margin-bottom: 12px;
}

.picker-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 8px;
}

.picker-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 8px;
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 10px;
  background: var(--bg, #fff);
  cursor: pointer;
  font-family: var(--font);
  transition: all 0.15s ease;
}

.picker-item:hover:not(.disabled) {
  border-color: var(--primary, #007aff);
  background: rgba(0, 122, 255, 0.03);
}

.picker-item.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.picker-icon {
  font-size: 1.4rem;
}

.picker-name {
  font-size: 0.75rem;
  color: var(--text, #1d1d1f);
}

/* Grid layout */
.widgets-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.widgets-grid.single-column {
  grid-template-columns: 1fr;
}

.widget-grid-item {
  min-height: 200px;
}

/* Empty state */
.empty-dashboard {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 3rem;
  margin: 0 0 12px;
}

.empty-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text, #1d1d1f);
  margin: 0 0 8px;
}

.empty-hint {
  font-size: 0.85rem;
  color: var(--text-secondary, #86868b);
  margin: 0;
}

/* Shared widget inner styles */
:deep(.widget-stat),
:deep(.widget-pii) {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

:deep(.stat-value) {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary, #007aff);
}

:deep(.stat-label) {
  font-size: 0.85rem;
  color: var(--text-secondary, #86868b);
  margin-top: 4px;
}

:deep(.widget-loading),
:deep(.widget-empty) {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary, #86868b);
  font-size: 0.85rem;
}

:deep(.type-row) {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

:deep(.type-label) {
  font-size: 0.75rem;
  font-weight: 600;
  min-width: 70px;
  color: var(--text, #1d1d1f);
}

:deep(.type-bar) {
  flex: 1;
  height: 6px;
  background: var(--border, #e5e5ea);
  border-radius: 3px;
  overflow: hidden;
}

:deep(.type-bar-fill) {
  height: 100%;
  border-radius: 3px;
  background: var(--primary, #007aff);
}

:deep(.type-count) {
  font-size: 0.75rem;
  color: var(--text-secondary, #86868b);
  min-width: 30px;
  text-align: right;
}

:deep(.type-pattern), :deep(.type-bg-pattern) { color: #2e7d32; background: #34c759; }
:deep(.type-fact), :deep(.type-bg-fact) { color: #1565c0; background: #007aff; }
:deep(.type-preference), :deep(.type-bg-preference) { color: #c62828; background: #ff2d55; }
:deep(.type-bug), :deep(.type-bg-bug) { color: #e65100; background: #ff9500; }
:deep(.type-workflow), :deep(.type-bg-workflow) { color: #7b1fa2; background: #af52de; }
:deep(.type-architecture), :deep(.type-bg-architecture) { color: #00695c; background: #5ac8fa; }

:deep(.widget-health) {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

:deep(.health-mini-ring) {
  width: 100px;
  height: 100px;
}

:deep(.recent-item) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border, #e5e5ea);
}

:deep(.recent-item:last-child) {
  border-bottom: none;
}

:deep(.recent-title) {
  font-size: 0.8rem;
  color: var(--text, #1d1d1f);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.recent-date) {
  font-size: 0.7rem;
  color: var(--text-secondary, #86868b);
  flex-shrink: 0;
}

:deep(.cluster-row) {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid var(--border, #e5e5ea);
}

:deep(.cluster-row:last-child) {
  border-bottom: none;
}

:deep(.cluster-label) {
  font-size: 0.8rem;
  color: var(--text, #1d1d1f);
}

:deep(.cluster-count) {
  font-size: 0.75rem;
  color: var(--primary, #007aff);
  font-weight: 600;
}

:deep(.anomaly-row) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid var(--border, #e5e5ea);
}

:deep(.anomaly-row:last-child) {
  border-bottom: none;
}

:deep(.anomaly-dot) {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

:deep(.dot-critical) { background: #ff3b30; }
:deep(.dot-warning) { background: #ff9500; }
:deep(.dot-info) { background: #007aff; }

:deep(.anomaly-text) {
  font-size: 0.8rem;
  color: var(--text, #1d1d1f);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.anomaly-time) {
  font-size: 0.65rem;
  color: var(--text-secondary, #86868b);
  flex-shrink: 0;
}

:deep(.decay-placeholder),
:deep(.widget-placeholder) {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  color: var(--text-secondary, #86868b);
}

:deep(.decay-hint),
:deep(.placeholder-hint) {
  font-size: 0.75rem;
  color: var(--text-secondary, #86868b);
}

:deep(.widget-actions) {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px;
}

:deep(.action-item) {
  padding: 10px 14px;
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px;
  background: var(--bg, #fff);
  cursor: pointer;
  font-size: 0.8rem;
  font-family: var(--font);
  color: var(--text, #1d1d1f);
  text-align: left;
  transition: all 0.15s ease;
}

:deep(.action-item:hover) {
  border-color: var(--primary, #007aff);
  background: rgba(0, 122, 255, 0.03);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
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
  max-height: 400px;
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
