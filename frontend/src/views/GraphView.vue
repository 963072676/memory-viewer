<template>
  <div class="graph-view">
    <div class="view-header">
      <div>
        <h2 class="section-title">Memory Graph</h2>
        <p class="panel-caption">
          {{ providerCaption }}
        </p>
      </div>
      <form class="graph-controls" @submit.prevent="loadGraph">
        <input
          v-model.trim="filters.provider"
          class="control-input"
          type="text"
          placeholder="Provider"
          aria-label="Provider"
        />
        <input
          v-model.trim="filters.sessionId"
          class="control-input"
          type="text"
          placeholder="Session"
          aria-label="Session"
        />
        <input
          v-model.number="filters.limit"
          class="control-input control-input--small"
          type="number"
          min="1"
          max="500"
          aria-label="Limit"
        />
        <button class="action-btn" type="submit" :disabled="loading">
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
      </form>
    </div>

    <div class="graph-stats">
      <div class="stat-tile">
        <span>Nodes</span>
        <strong>{{ graph?.meta.node_count ?? 0 }}</strong>
      </div>
      <div class="stat-tile">
        <span>Edges</span>
        <strong>{{ graph?.meta.edge_count ?? 0 }}</strong>
      </div>
      <div class="stat-tile">
        <span>Max Weight</span>
        <strong>{{ graph?.meta.max_weight ?? 0 }}</strong>
      </div>
      <div class="stat-tile">
        <span>Providers</span>
        <strong>{{ graph?.meta.providers.length ?? 0 }}</strong>
      </div>
    </div>

    <div v-if="loading && !graph" class="graph-state">Building graph...</div>
    <div v-else-if="error" class="graph-state graph-state--error">
      <p>{{ error }}</p>
      <button class="action-btn" type="button" @click="loadGraph">Retry</button>
    </div>
    <div v-else-if="!graph?.nodes.length" class="graph-state">No memories available for graph visualization.</div>

    <section v-else class="graph-shell">
      <div class="graph-toolbar">
        <div class="provider-list">
          <span v-for="provider in graph.meta.providers" :key="provider" class="provider-chip">
            {{ provider }}
          </span>
        </div>
        <div class="edge-note">{{ graph.edges.length }} semantic relations</div>
      </div>

      <div class="graph-canvas">
        <RelationGraph
          :nodes="graph.nodes"
          :edges="relationEdges"
          :selected-node-id="selectedNode?.id"
          @node-click="onNodeClick"
        />

        <transition name="slide">
          <aside v-if="selectedNode" class="node-detail">
            <div class="detail-header">
              <span class="provider-chip">{{ selectedNode.provider }}</span>
              <button class="close-btn" type="button" aria-label="Close" @click="selectedNode = null">X</button>
            </div>
            <h3>{{ selectedNode.label }}</h3>
            <p>{{ selectedNode.contentSnippet || 'No content preview.' }}</p>
            <div class="detail-grid">
              <span>Type</span>
              <strong>{{ selectedNode.type }}</strong>
              <span>Strength</span>
              <strong>{{ selectedNode.strength }}</strong>
              <span>Connections</span>
              <strong>{{ connectedEdges.length }}</strong>
            </div>
            <div v-if="selectedNode.tags.length" class="tag-row">
              <span v-for="tag in selectedNode.tags.slice(0, 6)" :key="tag" class="tag-chip">{{ tag }}</span>
            </div>
          </aside>
        </transition>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import RelationGraph from '@/components/Layout/RelationGraph.vue'
import {
  fetchMemoryGraph,
  type MemoryGraphNode,
  type MemoryGraphResponse,
} from '@/api/graph'

const graph = ref<MemoryGraphResponse | null>(null)
const selectedNode = ref<MemoryGraphNode | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const filters = reactive({
  provider: '',
  sessionId: '',
  limit: 200,
})

const providerCaption = computed(() => {
  const providers = graph.value?.meta.providers || []
  return providers.length ? providers.join(', ') : 'All providers'
})

const relationEdges = computed(() => (
  graph.value?.edges.map(edge => ({
    source: edge.source,
    target: edge.target,
    label: edge.shared_concepts.slice(0, 3).join(', '),
    relation_type: edge.relation_type,
  })) || []
))

const connectedEdges = computed(() => {
  if (!selectedNode.value || !graph.value) return []
  const id = selectedNode.value.id
  return graph.value.edges.filter(edge => edge.source === id || edge.target === id)
})

async function loadGraph() {
  loading.value = true
  error.value = null
  try {
    graph.value = await fetchMemoryGraph({
      provider: filters.provider || undefined,
      sessionId: filters.sessionId || undefined,
      limit: Number(filters.limit) || 200,
    })
    if (selectedNode.value && !graph.value.nodes.some(node => node.id === selectedNode.value?.id)) {
      selectedNode.value = null
    }
  } catch (e: any) {
    error.value = e?.message || 'Failed to load memory graph'
  } finally {
    loading.value = false
  }
}

function onNodeClick(node: { id: string }) {
  selectedNode.value = graph.value?.nodes.find(item => item.id === node.id) || null
}

onMounted(loadGraph)
</script>

<style scoped>
.graph-view {
  padding-bottom: 40px;
}

.view-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  flex-wrap: wrap;
  margin-bottom: var(--space-5);
}

h2.section-title {
  position: relative;
  padding-left: 12px;
  color: var(--primary);
  font-size: 1.5rem;
  font-weight: 600;
}

h2.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 3px;
  height: 60%;
  border-radius: 0 2px 2px 0;
  background: var(--accent);
  transform: translateY(-50%);
}

.panel-caption {
  margin-top: var(--space-1);
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.graph-controls {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.control-input {
  width: 150px;
  min-height: 38px;
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--card);
  color: var(--primary);
  font-family: var(--font);
  font-size: 0.84rem;
}

.control-input--small {
  width: 86px;
}

.control-input:focus {
  border-color: var(--accent);
  outline: none;
  box-shadow: 0 0 0 4px var(--accent-glow);
}

.graph-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.stat-tile {
  min-height: 82px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: var(--space-4);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--card);
}

.stat-tile span {
  color: var(--text-secondary);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.stat-tile strong {
  color: var(--primary);
  font-family: var(--font-mono);
  font-size: 1.45rem;
  line-height: 1;
}

.graph-state {
  padding: var(--space-8) var(--space-5);
  border: 1px dashed var(--border);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  text-align: center;
}

.graph-state--error {
  color: var(--error-text);
}

.graph-shell {
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--card);
  box-shadow: var(--shadow);
  overflow: hidden;
}

.graph-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  min-height: 48px;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border);
}

.provider-list,
.tag-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.provider-chip,
.tag-chip {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 0.72rem;
  font-weight: 700;
}

.provider-chip {
  background: var(--accent-subtle);
  color: var(--accent);
}

.tag-chip {
  background: var(--tag-bg);
  color: var(--text-secondary);
}

.edge-note {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.graph-canvas {
  position: relative;
  min-height: 560px;
}

.node-detail {
  position: absolute;
  top: var(--space-4);
  right: var(--space-4);
  width: min(320px, calc(100% - 32px));
  padding: var(--space-4);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--card);
  box-shadow: var(--shadow-elevated);
  z-index: 2;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.close-btn {
  width: 28px;
  height: 28px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--card);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.72rem;
  font-weight: 800;
}

.node-detail h3 {
  margin-bottom: var(--space-2);
  color: var(--primary);
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.35;
}

.node-detail p {
  margin-bottom: var(--space-4);
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.55;
}

.detail-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--space-2) var(--space-3);
  margin-bottom: var(--space-4);
  font-size: 0.82rem;
}

.detail-grid span {
  color: var(--text-secondary);
}

.detail-grid strong {
  color: var(--primary);
}

.slide-enter-active,
.slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateX(12px);
}

@media (max-width: 767px) {
  .view-header,
  .graph-controls,
  .graph-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .control-input,
  .control-input--small {
    width: 100%;
  }

  .graph-canvas {
    min-height: 480px;
  }

  .node-detail {
    position: absolute;
    left: var(--space-3);
    right: var(--space-3);
    top: auto;
    bottom: var(--space-3);
    width: auto;
  }
}
</style>
