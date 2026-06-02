<template>
  <div class="health-scan-view">
    <div class="hs-header">
      <h2>🩺 Health Scanner</h2>
      <button class="btn-scan" @click="runScan" :disabled="scanning">
        {{ scanning ? '⏳ Scanning...' : '▶ Run Scan' }}
      </button>
    </div>

    <div v-if="scanning" class="scanning-state">
      <div class="scan-spinner"></div>
      <p>Scanning your memories for health issues...</p>
    </div>

    <div v-else-if="!result && !loading" class="empty-state">
      <p>🩺 No scan results yet</p>
      <button class="btn-scan" @click="runScan">Run your first health scan</button>
    </div>

    <div v-else-if="loading" class="loading-state">Loading last scan results...</div>

    <div v-else-if="result" class="scan-results">
      <!-- Score Gauge + Stats -->
      <div class="score-section">
        <HealthScoreGauge :score="result.overall_score" :size="180" />
        <div class="score-stats">
          <div class="stat">
            <span class="stat-value">{{ result.total_memories }}</span>
            <span class="stat-label">Total Memories</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ result.issues.length }}</span>
            <span class="stat-label">Issues Found</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ formatDate(result.scanned_at) }}</span>
            <span class="stat-label">Last Scan</span>
          </div>
        </div>
      </div>

      <!-- Breakdown -->
      <div class="breakdown-section" v-if="result.breakdown">
        <h3>Breakdown</h3>
        <div class="breakdown-grid">
          <div class="breakdown-card">
            <span class="bd-value">{{ result.breakdown.strength_avg?.toFixed(1) }}</span>
            <span class="bd-label">Avg Strength</span>
          </div>
          <div class="breakdown-card">
            <span class="bd-value">{{ result.breakdown.stale_count }}</span>
            <span class="bd-label">Stale Memories</span>
          </div>
          <div class="breakdown-card">
            <span class="bd-value">{{ result.breakdown.duplicate_count }}</span>
            <span class="bd-label">Duplicates</span>
          </div>
          <div class="breakdown-card">
            <span class="bd-value">{{ result.breakdown.missing_concepts_count }}</span>
            <span class="bd-label">Missing Concepts</span>
          </div>
          <div class="breakdown-card">
            <span class="bd-value">{{ result.breakdown.missing_tags_count }}</span>
            <span class="bd-label">Missing Tags</span>
          </div>
          <div class="breakdown-card">
            <span class="bd-value">{{ result.breakdown.low_health_count }}</span>
            <span class="bd-label">Low Health</span>
          </div>
        </div>
      </div>

      <!-- Issues -->
      <div class="issues-section" v-if="result.issues.length">
        <h3>Issues ({{ result.issues.length }})</h3>
        <div class="issues-grid">
          <IssueCard
            v-for="issue in sortedIssues"
            :key="issue.id"
            :issue="issue"
          />
        </div>
      </div>

      <div v-else class="no-issues">
        <p>🎉 No issues found! Your memory database is healthy.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { runHealthScan, getLastScan, type HealthScanResult } from '@/api/healthScan'
import { useToast } from '@/composables/useToast'
import HealthScoreGauge from '@/components/Layout/HealthScoreGauge.vue'
import IssueCard from '@/components/Layout/IssueCard.vue'

const toast = useToast()

const loading = ref(false)
const scanning = ref(false)
const result = ref<HealthScanResult | null>(null)

const sortedIssues = computed(() => {
  if (!result.value) return []
  const order = { critical: 0, warning: 1, info: 2 }
  return [...result.value.issues].sort((a, b) => order[a.severity] - order[b.severity])
})

function formatDate(ts: string): string {
  if (!ts) return 'N/A'
  try {
    return new Date(ts).toLocaleDateString()
  } catch {
    return ts
  }
}

async function runScan() {
  scanning.value = true
  try {
    result.value = await runHealthScan()
    toast.success('Health scan complete')
  } catch (e: any) {
    toast.error('Scan failed: ' + (e.message || ''))
  } finally {
    scanning.value = false
  }
}

async function loadLastScan() {
  loading.value = true
  try {
    result.value = await getLastScan()
  } catch {
    // No previous scan
  } finally {
    loading.value = false
  }
}

onMounted(loadLastScan)
</script>

<style scoped>
.health-scan-view {
  padding-bottom: 40px;
}

.hs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.hs-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary, #007aff);
  margin: 0;
}

.btn-scan {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: var(--accent, #007aff);
  color: #fff;
  font-size: 0.85rem;
  cursor: pointer;
  font-family: var(--font);
  transition: opacity 0.2s;
}

.btn-scan:hover {
  opacity: 0.9;
}

.btn-scan:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.scanning-state,
.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  font-size: 1rem;
}

.scan-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  margin: 0 auto 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.scan-results {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.score-section {
  display: flex;
  align-items: center;
  gap: 32px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
}

.score-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--primary);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.breakdown-section h3,
.issues-section h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--primary);
  margin: 0 0 12px;
}

.breakdown-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
}

.breakdown-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bd-value {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--primary);
}

.bd-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.issues-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.no-issues {
  text-align: center;
  padding: 40px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
}

.no-issues p {
  font-size: 1rem;
  color: var(--text-secondary);
  margin: 0;
}

@media (max-width: 767px) {
  .score-section {
    flex-direction: column;
    text-align: center;
  }

  .score-stats {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    gap: 24px;
  }

  .breakdown-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
