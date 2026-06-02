<template>
  <div class="relation-graph" ref="containerRef">
    <svg
      :width="width"
      :height="height"
      class="graph-svg"
      @mousedown="onMouseDown"
      @mousemove="onMouseMove"
      @mouseup="onMouseUp"
    >
      <!-- Edges -->
      <g class="edges">
        <g v-for="edge in layoutEdges" :key="edge.id">
          <line
            :x1="edge.sx"
            :y1="edge.sy"
            :x2="edge.tx"
            :y2="edge.ty"
            :stroke="edge.highlighted ? 'var(--accent)' : 'var(--border)'"
            :stroke-width="edge.highlighted ? 2 : 1"
            stroke-opacity="0.6"
          />
          <text
            v-if="edge.label"
            :x="(edge.sx + edge.tx) / 2"
            :y="(edge.sy + edge.ty) / 2 - 6"
            text-anchor="middle"
            class="edge-label"
            :fill="edge.highlighted ? 'var(--accent)' : 'var(--text-secondary)'"
          >
            {{ edge.label }}
          </text>
        </g>
      </g>
      <!-- Nodes -->
      <g class="nodes">
        <g
          v-for="node in layoutNodes"
          :key="node.id"
          class="node-group"
          :class="{ selected: node.id === selectedNodeId, dimmed: selectedNodeId && !node.connected }"
          @mousedown.stop="startDrag(node, $event)"
          @click.stop="$emit('node-click', node)"
        >
          <circle
            :cx="node.x"
            :cy="node.y"
            :r="node.radius"
            :fill="node.color"
            stroke="var(--card)"
            stroke-width="2"
          />
          <text
            :x="node.x"
            :y="node.y + node.radius + 14"
            text-anchor="middle"
            class="node-label"
            fill="var(--primary)"
          >
            {{ truncatedLabel(node.label) }}
          </text>
        </g>
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

interface GraphNodeInput {
  id: string
  label: string
  type: string
  strength?: number
}

interface GraphEdgeInput {
  source: string
  target: string
  label?: string
  relation_type?: string
}

interface LayoutNode extends GraphNodeInput {
  x: number
  y: number
  vx: number
  vy: number
  radius: number
  color: string
  connected: boolean
}

interface LayoutEdge {
  id: string
  sx: number
  sy: number
  tx: number
  ty: number
  label?: string
  highlighted: boolean
}

const props = defineProps<{
  nodes: GraphNodeInput[]
  edges: GraphEdgeInput[]
  selectedNodeId?: string | null
}>()

defineEmits<{
  (e: 'node-click', node: LayoutNode): void
}>()

const containerRef = ref<HTMLElement | null>(null)
const width = ref(800)
const height = ref(500)

const typeColors: Record<string, string> = {
  pattern: '#2e7d32',
  fact: '#1565c0',
  preference: '#c62828',
  bug: '#e65100',
  workflow: '#7b1fa2',
  architecture: '#00695c',
}

const layoutNodes = ref<LayoutNode[]>([])
const layoutEdges = ref<LayoutEdge[]>([])
let animFrame = 0
const dragNode = ref<LayoutNode | null>(null)

function truncatedLabel(label: string): string {
  return label.length > 16 ? label.slice(0, 14) + '…' : label
}

function initLayout() {
  const w = width.value
  const h = height.value
  const cx = w / 2
  const cy = h / 2

  layoutNodes.value = props.nodes.map((n, i) => {
    const angle = (2 * Math.PI * i) / Math.max(props.nodes.length, 1)
    const r = Math.min(w, h) * 0.3
    return {
      ...n,
      x: cx + r * Math.cos(angle) + (Math.random() - 0.5) * 40,
      y: cy + r * Math.sin(angle) + (Math.random() - 0.5) * 40,
      vx: 0,
      vy: 0,
      radius: 6 + (n.strength || 5) * 0.8,
      color: typeColors[n.type] || '#888',
      connected: true,
    }
  })
  updateEdges()
}

function updateEdges() {
  const nodeMap = new Map(layoutNodes.value.map(n => [n.id, n]))
  const connectedIds = new Set<string>()

  if (props.selectedNodeId) {
    connectedIds.add(props.selectedNodeId)
    props.edges.forEach(e => {
      if (e.source === props.selectedNodeId) connectedIds.add(e.target)
      if (e.target === props.selectedNodeId) connectedIds.add(e.source)
    })
    layoutNodes.value.forEach(n => {
      n.connected = connectedIds.has(n.id)
    })
  } else {
    layoutNodes.value.forEach(n => { n.connected = true })
  }

  layoutEdges.value = props.edges.map((e, i) => {
    const s = nodeMap.get(e.source)
    const t = nodeMap.get(e.target)
    if (!s || !t) return null
    const highlighted = props.selectedNodeId
      ? (e.source === props.selectedNodeId || e.target === props.selectedNodeId)
      : false
    return {
      id: `edge-${i}`,
      sx: s.x,
      sy: s.y,
      tx: t.x,
      ty: t.y,
      label: e.label || e.relation_type,
      highlighted,
    }
  }).filter(Boolean) as LayoutEdge[]
}

// Force simulation
function simulate() {
  const alpha = 0.1
  const repulsion = 800
  const attraction = 0.005
  const damping = 0.85
  const centerForce = 0.01
  const cx = width.value / 2
  const cy = height.value / 2

  const nodes = layoutNodes.value
  const edgeSet = new Set(props.edges.map(e => `${e.source}:${e.target}`))

  // Repulsion between all node pairs
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i]
      const b = nodes[j]
      let dx = b.x - a.x
      let dy = b.y - a.y
      const dist = Math.sqrt(dx * dx + dy * dy) || 1
      const force = repulsion / (dist * dist)
      const fx = (dx / dist) * force * alpha
      const fy = (dy / dist) * force * alpha
      a.vx -= fx
      a.vy -= fy
      b.vx += fx
      b.vy += fy
    }
  }

  // Attraction along edges
  props.edges.forEach(e => {
    const a = nodes.find(n => n.id === e.source)
    const b = nodes.find(n => n.id === e.target)
    if (!a || !b) return
    const dx = b.x - a.x
    const dy = b.y - a.y
    const dist = Math.sqrt(dx * dx + dy * dy) || 1
    const force = dist * attraction
    a.vx += (dx / dist) * force
    a.vy += (dy / dist) * force
    b.vx -= (dx / dist) * force
    b.vy -= (dy / dist) * force
  })

  // Center gravity + damping + boundary
  nodes.forEach(n => {
    if (n === dragNode.value) return
    n.vx += (cx - n.x) * centerForce
    n.vy += (cy - n.y) * centerForce
    n.vx *= damping
    n.vy *= damping
    n.x += n.vx
    n.y += n.vy
    n.x = Math.max(n.radius, Math.min(width.value - n.radius, n.x))
    n.y = Math.max(n.radius, Math.min(height.value - n.radius, n.y))
  })

  updateEdges()
}

function tick() {
  simulate()
  animFrame = requestAnimationFrame(tick)
}

// Drag support
function startDrag(node: LayoutNode, e: MouseEvent) {
  dragNode.value = node
}

function onMouseMove(e: MouseEvent) {
  if (!dragNode.value || !containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  dragNode.value.x = e.clientX - rect.left
  dragNode.value.y = e.clientY - rect.top
  dragNode.value.vx = 0
  dragNode.value.vy = 0
  updateEdges()
}

function onMouseUp() {
  dragNode.value = null
}

function onMouseDown() {
  // noop, handled by node
}

function resize() {
  if (containerRef.value) {
    width.value = containerRef.value.clientWidth
    height.value = containerRef.value.clientHeight || 500
  }
}

watch(() => [props.nodes, props.edges], () => {
  initLayout()
}, { deep: true })

onMounted(() => {
  resize()
  initLayout()
  tick()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  cancelAnimationFrame(animFrame)
  window.removeEventListener('resize', resize)
})
</script>

<style scoped>
.relation-graph {
  width: 100%;
  height: 100%;
  min-height: 400px;
  position: relative;
}

.graph-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.node-group {
  cursor: grab;
  transition: opacity 0.2s;
}

.node-group:active {
  cursor: grabbing;
}

.node-group.dimmed {
  opacity: 0.25;
}

.node-group.selected circle {
  stroke: var(--accent);
  stroke-width: 3;
}

.node-label {
  font-size: 0.65rem;
  pointer-events: none;
  font-family: var(--font);
}

.edge-label {
  font-size: 0.55rem;
  pointer-events: none;
  font-family: var(--font);
}
</style>
