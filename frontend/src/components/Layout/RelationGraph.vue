<template>
  <div class="relation-graph" ref="containerRef">
    <div class="zoom-controls">
      <button class="zoom-btn" @click="zoomIn" title="放大">+</button>
      <button class="zoom-btn" @click="zoomOut" title="缩小">−</button>
      <button class="zoom-btn" @click="resetView" title="重置">⟲</button>
    </div>
    <svg
      :width="width"
      :height="height"
      class="graph-svg"
      @wheel.prevent="onWheel"
      @mousedown="onSvgMouseDown"
      @mousemove="onMouseMove"
      @mouseup="onMouseUp"
      @mouseleave="onMouseUp"
    >
      <g :transform="`translate(${pan.x},${pan.y}) scale(${zoom})`">
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

// Zoom & Pan state
const zoom = ref(1)
const pan = ref({ x: 0, y: 0 })
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0 })
const ZOOM_MIN = 0.2
const ZOOM_MAX = 5
const ZOOM_STEP = 0.15

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
  const repulsion = 2500
  const attraction = 0.002
  const damping = 0.85
  const centerForce = 0.005
  const cx = width.value / 2
  const cy = height.value / 2

  const nodes = layoutNodes.value
  const nodeMap = new Map(nodes.map(n => [n.id, n]))

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

  // Attraction along edges (alpha applied to match repulsion scale)
  props.edges.forEach(e => {
    const a = nodeMap.get(e.source)
    const b = nodeMap.get(e.target)
    if (!a || !b) return
    const dx = b.x - a.x
    const dy = b.y - a.y
    const dist = Math.sqrt(dx * dx + dy * dy) || 1
    const force = dist * attraction * alpha
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

// Drag support (zoom-aware)
function startDrag(node: LayoutNode, e: MouseEvent) {
  dragNode.value = node
}

function toGraphCoords(clientX: number, clientY: number): { x: number; y: number } {
  if (!containerRef.value) return { x: clientX, y: clientY }
  const rect = containerRef.value.getBoundingClientRect()
  return {
    x: (clientX - rect.left - pan.value.x) / zoom.value,
    y: (clientY - rect.top - pan.value.y) / zoom.value,
  }
}

function onMouseMove(e: MouseEvent) {
  if (dragNode.value && containerRef.value) {
    const coords = toGraphCoords(e.clientX, e.clientY)
    dragNode.value.x = coords.x
    dragNode.value.y = coords.y
    dragNode.value.vx = 0
    dragNode.value.vy = 0
    updateEdges()
  } else if (isPanning.value) {
    pan.value = {
      x: pan.value.x + (e.clientX - panStart.value.x),
      y: pan.value.y + (e.clientY - panStart.value.y),
    }
    panStart.value = { x: e.clientX, y: e.clientY }
  }
}

function onMouseUp() {
  dragNode.value = null
  isPanning.value = false
}

function onSvgMouseDown(e: MouseEvent) {
  // Only start panning if clicking on empty space (not a node)
  if ((e.target as Element).tagName === 'svg' || (e.target as Element).tagName === 'line') {
    isPanning.value = true
    panStart.value = { x: e.clientX, y: e.clientY }
  }
}

// Zoom handlers
function onWheel(e: WheelEvent) {
  const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP
  const newZoom = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, zoom.value + delta))

  // Zoom towards cursor position
  if (containerRef.value) {
    const rect = containerRef.value.getBoundingClientRect()
    const mx = e.clientX - rect.left
    const my = e.clientY - rect.top
    const scale = newZoom / zoom.value
    pan.value = {
      x: mx - (mx - pan.value.x) * scale,
      y: my - (my - pan.value.y) * scale,
    }
  }
  zoom.value = newZoom
}

function zoomIn() {
  zoom.value = Math.min(ZOOM_MAX, zoom.value + ZOOM_STEP)
}

function zoomOut() {
  zoom.value = Math.max(ZOOM_MIN, zoom.value - ZOOM_STEP)
}

function resetView() {
  zoom.value = 1
  pan.value = { x: 0, y: 0 }
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
  cursor: grab;
}

.graph-svg:active {
  cursor: grabbing;
}

.zoom-controls {
  position: absolute;
  bottom: 12px;
  right: 12px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.zoom-btn {
  width: 32px;
  height: 32px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--card);
  color: var(--primary);
  font-size: 1.1rem;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s ease, border-color 0.15s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.zoom-btn:hover {
  background: var(--tag-bg);
  border-color: var(--border-strong);
}

.zoom-btn:active {
  transform: scale(0.95);
}

.node-group {
  cursor: pointer;
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
