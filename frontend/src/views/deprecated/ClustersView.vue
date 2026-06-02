<template>
  <div class="clusters-view">
    <div class="clusters-header">
      <h2>🫧 记忆聚类</h2>
      <button class="btn-refresh" @click="loadClusters" :disabled="loading">
        🔄 刷新
      </button>
    </div>

    <div v-if="loading && clusters.length === 0" class="loading-state">
      加载中...
    </div>
    <div v-else-if="error" class="error-state">
      <p>⚠️ {{ error }}</p>
      <button class="btn-retry" @click="loadClusters">点击重试</button>
    </div>
    <div v-else-if="clusters.length === 0" class="empty-state">
      <p>暂无聚类数据</p>
      <p class="empty-hint">聚类会根据记忆的内容自动分组</p>
    </div>
    <template v-else>
      <!-- Bubble visualization -->
      <div class="bubble-container" ref="bubbleContainer">
        <svg :width="svgWidth" :height="svgHeight" class="bubble-svg">
          <g v-for="cluster in positionedClusters" :key="cluster.id">
            <circle
              :cx="cluster.x"
              :cy="cluster.y"
              :r="cluster.radius"
              :fill="cluster.color"
              :stroke="selectedCluster?.id === cluster.id ? 'var(--primary, #007aff)' : 'transparent'"
              stroke-width="3"
              class="bubble"
              @click="selectCluster(cluster)"
            />
            <text
              :x="cluster.x"
              :y="cluster.y - 6"
              text-anchor="middle"
              class="bubble-label"
              :font-size="Math.max(10, cluster.radius / 4)"
            >
              {{ truncateLabel(cluster.label, cluster.radius) }}
            </text>
            <text
              :x="cluster.x"
              :y="cluster.y + 10"
              text-anchor="middle"
              class="bubble-count"
              :font-size="Math.max(9, cluster.radius / 5)"
            >
              {{ cluster.memory_count }}
            </text>
          </g>
        </svg>
      </div>

      <!-- Cluster details panel -->
      <transition name="slide-panel">
        <div v-if="selectedCluster" class="cluster-detail-panel">
          <div class="detail-header">
            <h3>
              <span class="detail-dot" :style="{ background: selectedCluster.color }"></span>
              {{ selectedCluster.label }}
            </h3>
            <button class="detail-close" @click="selectedCluster = null">✕</button>
          </div>
          <div class="detail-meta">
            <span>{{ selectedCluster.memory_count }} 条记忆</span>
            <span v-if="selectedCluster.dominant_type">
              主要类型: <span class="type-badge" :class="'type-' + selectedCluster.dominant_type">{{ selectedCluster.dominant_type }}</span>
            </span>
          </div>
          <div v-if="selectedCluster.keywords?.length" class="detail-keywords">
            <span class="detail-label">关键词</span>
            <div class="keyword-tags">
              <span v-for="kw in selectedCluster.keywords" :key="kw" class="keyword-tag">{{ kw }}</span>
            </div>
          </div>
          <div v-if="loadingMemories" class="detail-loading">加载记忆中...</div>
          <div v-else class="detail-memories">
            <div
              v-for="mem in clusterMemories"
              :key="mem.id"
              class="cluster-memory-item"
            >
              <div class="memory-title">{{ mem.title }}</div>
              <div class="memory-snippet">{{ truncateText(mem.content, 100) }}</div>
              <div class="memory-meta">
                <span class="memory-type" :class="'type-' + mem.type">{{ mem.type }}</span>
                <span class="memory-strength">💪 {{ (mem.strength * 10).toFixed(0) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'
import type { AgentMemory } from '@/types'

interface Cluster {
  id: string
  label: string
  memory_count: number
  dominant_type: string
  keywords: string[]
  type_distribution: Record<string, number>
  memory_ids: string[]
}

interface ClusterDetail {
  cluster: Cluster
  memories: AgentMemory[]
}

interface PositionedCluster extends Cluster {
  x: number
  y: number
  radius: number
  color: string
}

const toast = useToast()

const clusters = ref<Cluster[]>([])
const selectedCluster = ref<PositionedCluster | null>(null)
const clusterMemories = ref<AgentMemory[]>([])
const loading = ref(false)
const loadingMemories = ref(false)
const error = ref('')
const bubbleContainer = ref<HTMLElement | null>(null)
const svgWidth = ref(800)
const svgHeight = ref(500)

// Color palette for types
const typeColors: Record<string, string> = {
  pattern: '#34c759',
  fact: '#007aff',
  preference: '#ff2d55',
  bug: '#ff9500',
  workflow: '#af52de',
  architecture: '#5ac8fa',
}

function getClusterColor(cluster: Cluster): string {
  if (cluster.dominant_type && typeColors[cluster.dominant_type]) {
    return typeColors[cluster.dominant_type]
  }
  // Hash-based fallback
  const colors = ['#007aff', '#34c759', '#ff9500', '#ff2d55', '#af52de', '#5ac8fa', '#ffcc00']
  let hash = 0
  for (const ch of cluster.id) hash = ((hash << 5) - hash + ch.charCodeAt(0)) | 0
  return colors[Math.abs(hash) % colors.length]
}

const positionedClusters = computed<PositionedCluster[]>(() => {
  if (clusters.value.length === 0) return []

  const w = svgWidth.value
  const h = svgHeight.value
  const padding = 60
  const maxCount = Math.max(1, ...clusters.value.map(c => c.memory_count))

  // Simple circle packing: arrange in a grid-like spiral
  const positioned: PositionedCluster[] = []
  const sorted = [...clusters.value].sort((a, b) => b.memory_count - a.memory_count)

  for (let i = 0; i < sorted.length; i++) {
    const cluster = sorted[i]
    const radius = Math.max(30, Math.min(100, (cluster.memory_count / maxCount) * 100))
    const color = getClusterColor(cluster)

    // Spiral placement
    const angle = i * 2.39996 // golden angle
    const dist = Math.sqrt(i + 1) * 50
    const x = w / 2 + Math.cos(angle) * dist
    const y = h / 2 + Math.sin(angle) * dist

    // Clamp to bounds
    const cx = Math.max(padding + radius, Math.min(w - padding - radius, x))
    const cy = Math.max(padding + radius, Math.min(h - padding - radius, y))

    positioned.push({
      ...cluster,
      x: cx,
      y: cy,
      radius,
      color,
    })
  }

  return positioned
})

function truncateLabel(label: string, radius: number): string {
  const maxLen = Math.max(4, Math.floor(radius / 5))
  return label.length > maxLen ? label.slice(0, maxLen - 1) + '…' : label
}

function truncateText(text: string, maxLen: number): string {
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

async function loadClusters() {
  loading.value = true
  error.value = ''
  try {
    const res = await request<{ clusters: any[] }>('/clusters')
    // Map backend field names to frontend interface
    clusters.value = (res.clusters || []).map((c: any) => ({
      id: c.id,
      label: c.name || c.label || '未命名',
      memory_count: c.count || c.memory_count || 0,
      dominant_type: c.dominant_type || (c.type_distribution ? Object.entries(c.type_distribution).sort((a: any, b: any) => b[1] - a[1])[0]?.[0] : ''),
      keywords: c.centroid_concepts || c.keywords || [],
      type_distribution: c.type_distribution || {},
      memory_ids: c.memory_ids || [],
    }))
  } catch (e: any) {
    error.value = e.message || '加载聚类数据失败'
  } finally {
    loading.value = false
  }
}

async function selectCluster(cluster: PositionedCluster) {
  selectedCluster.value = cluster
  loadingMemories.value = true
  clusterMemories.value = []
  try {
    const res = await request<ClusterDetail>(`/clusters/${cluster.id}`)
    clusterMemories.value = res.memories || []
  } catch (e: any) {
    toast.error(e.message || '加载聚类记忆失败')
  } finally {
    loadingMemories.value = false
  }
}

function handleResize() {
  if (bubbleContainer.value) {
    svgWidth.value = bubbleContainer.value.clientWidth
    svgHeight.value = Math.max(400, Math.min(600, window.innerHeight * 0.5))
  }
}

onMounted(() => {
  loadClusters()
  handleResize()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.clusters-view {
  padding-bottom: 40px;
}

.clusters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.clusters-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary, #007aff);
  margin: 0;
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

.btn-refresh:hover {
  background: var(--tag-bg, #f2f2f7);
}

.btn-refresh:disabled {
  opacity: 0.5;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary, #86868b);
  font-size: 1rem;
}

.error-state {
  color: var(--error, #ff3b30);
}

.btn-retry {
  margin-top: 12px;
  padding: 8px 20px;
  border: 1px solid var(--error, #ff3b30);
  border-radius: 8px;
  background: transparent;
  color: var(--error, #ff3b30);
  cursor: pointer;
  font-family: var(--font);
}

.empty-hint {
  font-size: 0.85rem;
  color: var(--text-secondary, #86868b);
}

/* Bubble container */
.bubble-container {
  background: var(--card, #fff);
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.bubble-svg {
  display: block;
  width: 100%;
}

.bubble {
  cursor: pointer;
  transition: opacity 0.2s ease, filter 0.2s ease;
  opacity: 0.85;
}

.bubble:hover {
  opacity: 1;
  filter: brightness(1.1);
}

.bubble-label {
  fill: #fff;
  font-weight: 600;
  pointer-events: none;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.bubble-count {
  fill: rgba(255, 255, 255, 0.85);
  font-weight: 500;
  pointer-events: none;
}

/* Cluster detail panel */
.cluster-detail-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 400px;
  max-width: 90vw;
  height: 100vh;
  background: var(--card, #fff);
  border-left: 1px solid var(--border, #e5e5ea);
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.08);
  z-index: 100;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border, #e5e5ea);
  flex-shrink: 0;
}

.detail-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text, #1d1d1f);
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.detail-close {
  border: none;
  background: none;
  font-size: 1rem;
  cursor: pointer;
  color: var(--text-secondary, #86868b);
  padding: 4px 8px;
  border-radius: 6px;
}

.detail-close:hover {
  background: var(--tag-bg, #f2f2f7);
}

.detail-meta {
  display: flex;
  gap: 16px;
  padding: 12px 20px;
  font-size: 0.8rem;
  color: var(--text-secondary, #86868b);
  border-bottom: 1px solid var(--border, #e5e5ea);
  flex-shrink: 0;
}

.type-badge {
  font-size: 0.7rem;
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.detail-keywords {
  padding: 12px 20px;
  border-bottom: 1px solid var(--border, #e5e5ea);
  flex-shrink: 0;
}

.detail-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-secondary, #86868b);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: block;
  margin-bottom: 6px;
}

.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.keyword-tag {
  font-size: 0.7rem;
  padding: 2px 8px;
  background: var(--tag-bg, #f2f2f7);
  border-radius: 6px;
  color: var(--text-secondary, #86868b);
}

.detail-loading {
  padding: 30px;
  text-align: center;
  color: var(--text-secondary, #86868b);
  font-size: 0.85rem;
}

.detail-memories {
  flex: 1;
  overflow-y: auto;
  padding: 12px 20px;
}

.cluster-memory-item {
  padding: 12px;
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 10px;
  margin-bottom: 8px;
  transition: border-color 0.15s ease;
}

.cluster-memory-item:hover {
  border-color: var(--primary, #007aff);
}

.memory-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text, #1d1d1f);
  margin-bottom: 4px;
}

.memory-snippet {
  font-size: 0.8rem;
  color: var(--text-secondary, #86868b);
  line-height: 1.4;
  margin-bottom: 6px;
}

.memory-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.memory-type {
  font-size: 0.65rem;
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.memory-strength {
  font-size: 0.75rem;
  color: var(--text-secondary, #86868b);
}

/* Type colors */
.type-pattern { background: #e8f5e9; color: #2e7d32; }
.type-fact { background: #e3f2fd; color: #1565c0; }
.type-preference { background: #fce4ec; color: #c62828; }
.type-bug { background: #fff3e0; color: #e65100; }
.type-workflow { background: #f3e5f5; color: #7b1fa2; }
.type-architecture { background: #e0f2f1; color: #00695c; }

/* Slide panel transition */
.slide-panel-enter-active,
.slide-panel-leave-active {
  transition: transform 0.3s ease;
}

.slide-panel-enter-from,
.slide-panel-leave-to {
  transform: translateX(100%);
}
</style>
