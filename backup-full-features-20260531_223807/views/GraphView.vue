<template>
  <div class="graph-view">
    <div class="graph-header">
      <h2>🕸️ Memory Graph</h2>
      <div class="graph-controls">
        <span class="graph-stats" v-if="!loading && nodes.length">
          {{ nodes.length }} nodes · {{ edges.length }} edges
        </span>
        <button class="btn-link" @click="showLinkCreator = true" :disabled="!selectedNode">
          🔗 Link Memory
        </button>
        <button class="action-btn" @click="loadGraph" :disabled="loading">
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">Building graph...</div>

    <div v-else-if="error" class="error-state">
      <p>⚠️ Failed to load graph</p>
      <button class="action-btn" @click="loadGraph">Retry</button>
    </div>

    <div v-else-if="nodes.length === 0" class="empty-state">
      <p>No memories available for graph visualization</p>
    </div>

    <div v-else class="graph-container">
      <RelationGraph
        :nodes="nodes"
        :edges="edges"
        :selected-node-id="selectedNode?.id"
        @node-click="onNodeClick"
      />

      <!-- Node detail panel -->
      <transition name="slide">
        <div v-if="selectedNode" class="node-detail">
          <div class="detail-header">
            <span class="detail-type" :class="selectedNode.type">{{ selectedNode.type }}</span>
            <button class="btn-close" @click="selectedNode = null">✕</button>
          </div>
          <h4>{{ selectedNode.label }}</h4>
          <p class="detail-strength">Strength: {{ selectedNode.strength }}</p>
          <div class="detail-connections">
            <span class="conn-label">Connections: {{ connectionCount }}</span>
          </div>
          <button class="btn-create-link" @click="showLinkCreator = true">
            🔗 Create Link
          </button>
        </div>
      </transition>

      <!-- Legend -->
      <div class="graph-legend">
        <div class="legend-item" v-for="(color, type) in typeColors" :key="type">
          <span class="legend-dot" :style="{ background: color }"></span>
          <span>{{ type }}</span>
        </div>
      </div>
    </div>

    <LinkCreator
      v-if="showLinkCreator && selectedNode"
      :source-id="selectedNode.id"
      :source-title="selectedNode.label"
      @close="showLinkCreator = false"
      @created="onLinkCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getGraph } from '@/api/agentmemory'
import type { GraphResponse } from '@/types'
import RelationGraph from '@/components/Layout/RelationGraph.vue'
import LinkCreator from '@/components/Layout/LinkCreator.vue'
import { useToast } from '@/composables/useToast'

const toast = useToast()

const loading = ref(false)
const error = ref(false)
const nodes = ref<Array<{ id: string; label: string; type: string; strength: number }>>([])
const edges = ref<Array<{ source: string; target: string; label?: string }>>([])
const selectedNode = ref<{ id: string; label: string; type: string; strength: number } | null>(null)
const showLinkCreator = ref(false)

const typeColors: Record<string, string> = {
  pattern: '#2e7d32',
  fact: '#1565c0',
  preference: '#c62828',
  bug: '#e65100',
  workflow: '#7b1fa2',
  architecture: '#00695c',
}

const connectionCount = computed(() => {
  if (!selectedNode.value) return 0
  const id = selectedNode.value.id
  return edges.value.filter(e => e.source === id || e.target === id).length
})

async function loadGraph() {
  loading.value = true
  error.value = false
  try {
    const data: GraphResponse = await getGraph()
    nodes.value = data.nodes.map(n => ({
      id: n.id,
      label: n.label,
      type: n.type,
      strength: n.strength,
    }))
    edges.value = data.edges.map(e => ({
      source: e.source,
      target: e.target,
      label: e.shared_concepts?.join(', '),
    }))
  } catch (e) {
    console.error('Failed to load graph:', e)
    error.value = true
  } finally {
    loading.value = false
  }
}

function onNodeClick(node: any) {
  selectedNode.value = node
}

function onLinkCreated() {
  showLinkCreator.value = false
  toast.success('Link created successfully')
  loadGraph()
}

onMounted(loadGraph)
</script>

<style scoped>
.graph-view {
  padding-bottom: 40px;
}

.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.graph-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary, #007aff);
  margin: 0;
}

.graph-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.graph-stats {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.action-btn,
.btn-link {
  padding: 8px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--primary);
  font-size: 0.8rem;
  font-family: var(--font);
  cursor: pointer;
  transition: background 0.2s;
}

.action-btn:hover,
.btn-link:hover {
  background: var(--tag-bg);
}

.action-btn:disabled,
.btn-link:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-link {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}

.loading-state,
.empty-state,
.error-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  font-size: 1rem;
}

.graph-container {
  position: relative;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  min-height: 500px;
}

.node-detail {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 240px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--shadow);
  z-index: 10;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.detail-type {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: capitalize;
  background: var(--tag-bg);
  color: var(--text-secondary);
}

.detail-type.pattern { background: #e8f5e9; color: #2e7d32; }
.detail-type.fact { background: #e3f2fd; color: #1565c0; }
.detail-type.preference { background: #fce4ec; color: #c62828; }
.detail-type.bug { background: #fff3e0; color: #e65100; }
.detail-type.workflow { background: #f3e5f5; color: #7b1fa2; }
.detail-type.architecture { background: #e0f2f1; color: #00695c; }

.btn-close {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 1rem;
}

.node-detail h4 {
  margin: 0 0 6px;
  font-size: 0.95rem;
  color: var(--primary);
}

.detail-strength {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin: 0 0 8px;
}

.detail-connections {
  margin-bottom: 12px;
}

.conn-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.btn-create-link {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--accent);
  border-radius: 8px;
  background: transparent;
  color: var(--accent);
  font-size: 0.8rem;
  cursor: pointer;
  font-family: var(--font);
  transition: background 0.2s;
}

.btn-create-link:hover {
  background: var(--accent);
  color: white;
}

.graph-legend {
  position: absolute;
  bottom: 12px;
  right: 12px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.65rem;
  color: var(--text-secondary);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.25s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

@media (max-width: 767px) {
  .graph-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .node-detail {
    position: fixed;
    top: auto;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    border-radius: 16px 16px 0 0;
  }

  .graph-legend {
    position: static;
    margin-top: 12px;
  }
}
</style>
