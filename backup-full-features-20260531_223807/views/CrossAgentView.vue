<template>
  <div class="cross-agent">
    <div class="view-header">
      <h1>🤝 Cross-Agent Knowledge Insights</h1>
      <p class="subtitle">Analyze knowledge overlap, gaps, and complementary areas across agent profiles</p>
    </div>

    <!-- Agent Selector -->
    <div class="agent-selector">
      <h3>Select Agents to Compare</h3>
      <div class="agent-chips">
        <button
          v-for="agent in agents"
          :key="agent"
          class="agent-chip"
          :class="{ active: selectedAgents.includes(agent) }"
          @click="toggleAgent(agent)"
        >
          {{ agent }}
        </button>
      </div>
      <button class="btn-compare" @click="compareAgents" :disabled="selectedAgents.length < 2 || loading">
        {{ loading ? '⏳ Analyzing...' : '🔍 Compare Agents' }}
      </button>
    </div>

    <!-- Comparison Matrix -->
    <div v-if="comparison" class="comparison-section">
      <h2>📊 Comparison Matrix</h2>
      <div class="matrix-container">
        <div class="matrix-grid">
          <div class="matrix-header">
            <div class="matrix-corner"></div>
            <div v-for="a in selectedAgents" :key="a" class="matrix-col-header">{{ a }}</div>
          </div>
          <div v-for="(row, i) in comparison.matrix" :key="i" class="matrix-row">
            <div class="matrix-row-header">{{ selectedAgents[i] }}</div>
            <div
              v-for="(val, j) in row"
              :key="j"
              class="matrix-cell"
              :style="{ background: getOverlapColor(val) }"
              :title="`${selectedAgents[i]} × ${selectedAgents[j]}: ${(val * 100).toFixed(0)}% overlap`"
            >
              {{ (val * 100).toFixed(0) }}%
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Shared Themes -->
    <div v-if="comparison?.shared_themes?.length" class="themes-section">
      <h2>🔗 Shared Themes</h2>
      <div class="themes-grid">
        <div v-for="theme in comparison.shared_themes" :key="theme.name" class="theme-card">
          <div class="theme-header">
            <span class="theme-icon">🏷️</span>
            <h4>{{ theme.name }}</h4>
            <span class="theme-count">{{ theme.memory_count }} memories</span>
          </div>
          <p class="theme-desc">{{ theme.description }}</p>
          <div class="theme-agents">
            <span v-for="a in theme.agents" :key="a" class="agent-badge">{{ a }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Knowledge Gaps -->
    <div v-if="gaps?.length" class="gaps-section">
      <h2>🕳️ Knowledge Gaps</h2>
      <div class="gaps-list">
        <div v-for="gap in gaps" :key="gap.topic" class="gap-card">
          <div class="gap-header">
            <span class="gap-icon">⚠️</span>
            <h4>{{ gap.topic }}</h4>
            <span :class="['gap-severity', gap.severity]">{{ gap.severity }}</span>
          </div>
          <p class="gap-desc">{{ gap.description }}</p>
          <div class="gap-agents">
            <span class="gap-label">Missing in:</span>
            <span v-for="a in gap.missing_agents" :key="a" class="agent-badge missing">{{ a }}</span>
          </div>
          <div class="gap-suggestion">
            <span class="suggestion-icon">💡</span>
            <span>{{ gap.suggestion }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Complementary Insights -->
    <div v-if="insights?.length" class="insights-section">
      <h2>💡 Complementary Insights</h2>
      <div class="insights-list">
        <div v-for="insight in insights" :key="insight.title" class="insight-card">
          <span class="insight-icon">{{ insight.icon }}</span>
          <div class="insight-content">
            <h4>{{ insight.title }}</h4>
            <p>{{ insight.description }}</p>
            <div class="insight-agents">
              <span v-for="a in insight.agents" :key="a" class="agent-badge">{{ a }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!comparison && !loading" class="empty-state">
      <span class="empty-icon">🤖</span>
      <p>Select at least 2 agents and click Compare to analyze knowledge distribution</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Comparison {
  matrix: number[][]
  shared_themes: { name: string; description: string; memory_count: number; agents: string[] }[]
}

interface Gap {
  topic: string
  description: string
  severity: 'high' | 'medium' | 'low'
  missing_agents: string[]
  suggestion: string
}

interface Insight {
  icon: string
  title: string
  description: string
  agents: string[]
}

const agents = ref<string[]>([])
const selectedAgents = ref<string[]>([])
const loading = ref(false)
const comparison = ref<Comparison | null>(null)
const gaps = ref<Gap[]>([])
const insights = ref<Insight[]>([])

function toggleAgent(agent: string) {
  const idx = selectedAgents.value.indexOf(agent)
  if (idx >= 0) selectedAgents.value.splice(idx, 1)
  else selectedAgents.value.push(agent)
}

function getOverlapColor(val: number) {
  if (val > 0.7) return 'rgba(76, 175, 80, 0.3)'
  if (val > 0.4) return 'rgba(255, 193, 7, 0.3)'
  return 'rgba(244, 67, 54, 0.2)'
}

async function compareAgents() {
  loading.value = true
  try {
    const res = await fetch('/api/cross-agent/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agents: selectedAgents.value }),
    })
    if (res.ok) {
      const data = await res.json()
      comparison.value = data.comparison
      gaps.value = data.gaps || []
      insights.value = data.insights || []
    }
  } catch {
    // Mock data
    comparison.value = {
      matrix: [[1, 0.45, 0.3], [0.45, 1, 0.6], [0.3, 0.6, 1]],
      shared_themes: [
        { name: 'User Preferences', description: 'Common user preference patterns', memory_count: 23, agents: selectedAgents.value },
        { name: 'Error Handling', description: 'Shared error handling knowledge', memory_count: 15, agents: selectedAgents.value.slice(0, 2) },
      ],
    }
    gaps.value = [
      { topic: 'Security Best Practices', description: 'No agent has comprehensive security knowledge', severity: 'high', missing_agents: selectedAgents.value, suggestion: 'Create security-focused memories from documentation' },
      { topic: 'Performance Optimization', description: 'Limited performance tuning knowledge', severity: 'medium', missing_agents: selectedAgents.value.slice(1), suggestion: 'Add performance benchmarking memories' },
    ]
    insights.value = [
      { icon: '🔄', title: 'Knowledge Transfer Opportunity', description: 'Agent A has deep API knowledge that could benefit Agent B', agents: selectedAgents.value.slice(0, 2) },
      { icon: '📚', title: 'Complementary Expertise', description: 'Agents cover different domains with minimal overlap', agents: selectedAgents.value },
    ]
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const res = await fetch('/api/profiles')
    if (res.ok) {
      const data = await res.json()
      agents.value = data.profiles || data || []
    }
  } catch {
    agents.value = ['chief-agent', 'daily', 'coder', 'researcher', 'planner']
  }
})
</script>

<style scoped>
.cross-agent { padding: 20px; }
.view-header h1 { font-size: 1.5rem; margin-bottom: 4px; }
.subtitle { color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 20px; }
.agent-selector { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; margin-bottom: 24px; }
.agent-selector h3 { font-size: 0.95rem; margin-bottom: 12px; }
.agent-chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.agent-chip { padding: 6px 14px; border: 1px solid var(--border); border-radius: 20px; background: var(--bg); cursor: pointer; font-size: 0.85rem; color: var(--text-secondary); }
.agent-chip.active { background: var(--accent); color: white; border-color: var(--accent); }
.btn-compare { padding: 8px 20px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }
.btn-compare:disabled { opacity: 0.5; cursor: not-allowed; }
.comparison-section, .themes-section, .gaps-section, .insights-section { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; margin-bottom: 24px; }
.comparison-section h2, .themes-section h2, .gaps-section h2, .insights-section h2 { font-size: 1rem; margin-bottom: 12px; }
.matrix-container { overflow-x: auto; }
.matrix-grid { display: grid; gap: 2px; }
.matrix-header, .matrix-row { display: grid; gap: 2px; }
.matrix-corner { background: transparent; }
.matrix-col-header, .matrix-row-header { padding: 8px; font-size: 0.8rem; font-weight: 600; background: var(--bg); text-align: center; }
.matrix-cell { padding: 8px; text-align: center; font-size: 0.85rem; font-weight: 500; border-radius: 4px; }
.themes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
.theme-card { background: var(--bg); border-radius: var(--radius); padding: 12px; }
.theme-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.theme-icon { font-size: 1rem; }
.theme-header h4 { font-size: 0.85rem; margin: 0; flex: 1; }
.theme-count { font-size: 0.75rem; color: var(--text-secondary); }
.theme-desc { font-size: 0.8rem; color: var(--text-secondary); margin: 0 0 8px; }
.theme-agents { display: flex; gap: 4px; flex-wrap: wrap; }
.agent-badge { font-size: 0.7rem; padding: 2px 8px; background: var(--tag-bg); border-radius: 10px; color: var(--text-secondary); }
.agent-badge.missing { background: #fce4ec; color: #c62828; }
.gaps-list { display: flex; flex-direction: column; gap: 12px; }
.gap-card { background: var(--bg); border-radius: var(--radius); padding: 12px; }
.gap-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.gap-icon { font-size: 1rem; }
.gap-header h4 { font-size: 0.85rem; margin: 0; flex: 1; }
.gap-severity { font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; font-weight: 600; }
.gap-severity.high { background: #fce4ec; color: #c62828; }
.gap-severity.medium { background: #fff3e0; color: #e65100; }
.gap-severity.low { background: #e8f5e9; color: #2e7d32; }
.gap-desc { font-size: 0.8rem; color: var(--text-secondary); margin: 0 0 8px; }
.gap-agents { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; }
.gap-label { font-size: 0.75rem; color: var(--text-secondary); }
.gap-suggestion { display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: var(--accent); }
.suggestion-icon { font-size: 0.9rem; }
.insights-list { display: flex; flex-direction: column; gap: 12px; }
.insight-card { display: flex; gap: 12px; background: var(--bg); border-radius: var(--radius); padding: 12px; }
.insight-icon { font-size: 1.2rem; }
.insight-content h4 { font-size: 0.85rem; margin: 0 0 4px; }
.insight-content p { font-size: 0.8rem; color: var(--text-secondary); margin: 0 0 8px; }
.insight-agents { display: flex; gap: 4px; }
.empty-state { text-align: center; padding: 60px 20px; color: var(--text-secondary); }
.empty-icon { font-size: 3rem; display: block; margin-bottom: 12px; }
</style>
