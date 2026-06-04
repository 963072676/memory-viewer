<template>
  <div class="lineage-graph" ref="graphContainer">
    <div v-if="loading" class="loading-state">{{ $t('zh_2c04aa') }}...</div>
    <div v-else-if="error" class="error-state">
      <p>⚠️ {{ error }}</p>
      <button class="btn-retry" @click="loadGraph">{{ $t('zh_006cc1') }}</button>
    </div>
    <div v-else-if="nodes.length === 0" class="empty-state">
      <p>{{ $t('zh_a7cf2b') }}</p>
      <p class="empty-hint">{{ $t('zh_72c825') }}</p>
    </div>
    <template v-else>
      <div class="graph-toolbar">
        <div class="legend">
          <span v-for="(label, source) in sourceLabels" :key="source" class="legend-item">
            <span class="legend-icon">{{ sourceIcons[source] || '📦' }}</span>
            <span>{{ label }}</span>
          </span>
        </div>
        <button class="btn-backfill" @click="backfillLegacy" :disabled="backfilling">
          {{ backfilling ? '回填中...' : '📦 回填历史记忆' }}
        </button>
      </div>
      <div class="graph-canvas" ref="canvasRef">
        <svg :width="width" :height="height">
          <g v-for="link in graphLinks" :key="`${link.source}-${link.target}`">
            <line
              :x1="getNodePos(link.source).x"
              :y1="getNodePos(link.source).y"
              :x2="getNodePos(link.target).x"
              :y2="getNodePos(link.target).y"
              stroke="var(--border, #e5e5ea)"
              stroke-width="2"
              stroke-dasharray="4,4"
              marker-end="url(#arrow)"
            />
          </g>
          <defs>
            <marker id="arrow" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="var(--text-secondary, #86868b)" />
            </marker>
          </defs>
          <g v-for="node in positionedNodes" :key="node.id">
            <circle
              :cx="node.x"
              :cy="node.y"
              :r="18"
              :fill="getNodeColor(node)"
              stroke="var(--border, #e5e5ea)"
              stroke-width="2"
              class="node-circle"
              @click="selectNode(node)"
            />
            <text
              :x="node.x"
              :y="node.y! + 1"
              text-anchor="middle"
              dominant-baseline="central"
              font-size="14"
              class="node-icon"
            >{{ node.icon }}</text>
            <text
              :x="node.x"
              :y="node.y! + 30"
              text-anchor="middle"
              font-size="10"
              fill="var(--text-secondary, #86868b)"
              class="node-label"
            >{{ truncateLabel(node.label, 12) }}</text>
          </g>
        </svg>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'

interface LineageNode {
  id: string
  label: string
  source: string
  icon: string
  type: string
  x?: number
  y?: number
}

interface LineageLink {
  source: string
  target: string
}

const toast = useToast()
const graphContainer = ref<HTMLElement | null>(null)
const canvasRef = ref<HTMLElement | null>(null)

const nodes = ref<LineageNode[]>([])
const links = ref<LineageLink[]>([])
const loading = ref(false)
const error = ref('')
const backfilling = ref(false)
const width = ref(800)
const height = ref(500)

const sourceIcons: Record<string, string> = {
  manual: '✍️',
  import: '📥',
  agent: '🤖',
  merge: '🔀',
  derived: '🔗',
  legacy: '📦',
}

const sourceLabels: Record<string, string> = {
  manual: '手动创建',
  import: '导入',
  agent: 'Agent生成',
  merge: '合并',
  derived: '衍生',
  legacy: '历史',
}

const sourceColors: Record<string, string> = {
  manual: '#007aff',
  import: '#34c759',
  agent: '#af52de',
  merge: '#ff9500',
  derived: '#5ac8fa',
  legacy: '#86868b',
}

const positionedNodes = computed<LineageNode[]>(() => {
  if (nodes.value.length === 0) return []
  const w = width.value
  const h = height.value
  const padding = 50
  const n = nodes.value.length

  return nodes.value.map((node, i) => {
    // Layout in a circle
    const angle = (2 * Math.PI * i) / n
    const radius = Math.min(w, h) / 2 - padding
    return {
      ...node,
      x: w / 2 + Math.cos(angle) * radius,
      y: h / 2 + Math.sin(angle) * radius,
    }
  })
})

const graphLinks = computed(() => links.value)

function getNodePos(id: string) {
  const node = positionedNodes.value.find(n => n.id === id)
  return node ? { x: node.x!, y: node.y! } : { x: width.value / 2, y: height.value / 2 }
}

function getNodeColor(node: LineageNode): string {
  return sourceColors[node.source] || '#86868b'
}

function truncateLabel(label: string, maxLen: number): string {
  return label.length > maxLen ? label.slice(0, maxLen - 1) + '…' : label
}

function selectNode(node: LineageNode) {
  // Could navigate to memory detail
  toast.info(`记忆: ${node.label} (${node.source})`)
}

async function loadGraph() {
  loading.value = true
  error.value = ''
  try {
    const res = await request<{ nodes: LineageNode[]; links: LineageLink[] }>('/lineage/graph')
    nodes.value = res.nodes || []
    links.value = res.links || []
    // Update canvas size
    if (canvasRef.value) {
      width.value = canvasRef.value.clientWidth
      height.value = Math.max(400, Math.min(600, window.innerHeight * 0.5))
    }
  } catch (e: any) {
    error.value = e.message || '加载谱系数据失败'
  } finally {
    loading.value = false
  }
}

async function backfillLegacy() {
  backfilling.value = true
  try {
    const res = await request<{ backfilled: number }>('/lineage/backfill', { method: 'POST' })
    toast.success(`已回填 ${res.backfilled} 条历史记忆`)
    await loadGraph()
  } catch (e: any) {
    toast.error(e.message || '回填失败')
  } finally {
    backfilling.value = false
  }
}

onMounted(() => {
  loadGraph()
})
</script>

<style scoped>
.lineage-graph {
  padding-bottom: 40px;
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

.graph-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;
}

.legend {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: var(--text-secondary, #86868b);
}

.legend-icon {
  font-size: 1rem;
}

.btn-backfill {
  padding: 6px 12px;
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px;
  background: var(--card, #fff);
  color: var(--primary, #007aff);
  font-size: 0.8rem;
  cursor: pointer;
  font-family: var(--font);
}

.btn-backfill:hover {
  background: var(--tag-bg, #f2f2f7);
}

.btn-backfill:disabled {
  opacity: 0.5;
}

.graph-canvas {
  background: var(--card, #fff);
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px;
  overflow: hidden;
}

.graph-canvas svg {
  display: block;
  width: 100%;
}

.node-circle {
  cursor: pointer;
  transition: transform 0.2s;
}

.node-circle:hover {
  filter: brightness(1.15);
}

.node-icon {
  pointer-events: none;
}

.node-label {
  pointer-events: none;
}
</style>
