<template>
  <div class="governance-view">
    <div class="gv-header">
      <h2>📋 Memory Governance</h2>
      <div class="gv-actions">
        <button class="btn-evaluate" @click="evaluateAll" :disabled="evaluating">
          {{ evaluating ? '⏳ Evaluating...' : '▶ Evaluate All Now' }}
        </button>
        <button class="btn-create" @click="showCreate = true">+ New Policy</button>
      </div>
    </div>

    <!-- Compliance Summary -->
    <div class="compliance-bar" v-if="report">
      <div class="compliance-stats">
        <div class="stat">
          <span class="stat-value">{{ report.compliance_rate }}%</span>
          <span class="stat-label">Compliance Rate</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ report.compliant_memories }}</span>
          <span class="stat-label">Compliant</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ report.violating_memories }}</span>
          <span class="stat-label">Violating</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ report.enabled_policies }}</span>
          <span class="stat-label">Active Policies</span>
        </div>
      </div>
      <div class="compliance-meter">
        <div class="meter-fill" :style="{ width: report.compliance_rate + '%' }" :class="complianceClass"></div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button :class="{ active: tab === 'policies' }" @click="tab = 'policies'">Policies</button>
      <button :class="{ active: tab === 'violations' }" @click="tab = 'violations'">Violations</button>
      <button :class="{ active: tab === 'report' }" @click="tab = 'report'">Report</button>
    </div>

    <!-- Policies Tab -->
    <div v-if="tab === 'policies'" class="policies-list">
      <div v-for="p in policies" :key="p.id" class="policy-card" :class="{ disabled: !p.enabled }">
        <div class="policy-header">
          <div class="policy-info">
            <span class="policy-type-badge" :class="p.type">{{ p.type }}</span>
            <h3>{{ p.name }}</h3>
          </div>
          <label class="toggle">
            <input type="checkbox" :checked="p.enabled" @change="togglePolicy(p.id)" />
            <span class="toggle-slider"></span>
          </label>
        </div>
        <p class="policy-desc">{{ p.description || 'No description' }}</p>
        <div class="policy-meta">
          <span class="severity" :class="p.severity">{{ p.severity }}</span>
          <span class="action">Action: {{ p.action }}</span>
          <span class="conditions">{{ p.conditions?.length || 0 }} conditions</span>
        </div>
        <div class="policy-actions">
          <button class="btn-sm" @click="evaluatePolicy(p.id)">▶ Evaluate</button>
          <button class="btn-sm btn-danger" @click="deletePolicy(p.id)">Delete</button>
        </div>
      </div>
      <div v-if="!policies.length" class="empty-state">
        <p>No governance policies defined yet.</p>
        <button class="btn-create" @click="showCreate = true">Create First Policy</button>
      </div>
    </div>

    <!-- Violations Tab -->
    <div v-if="tab === 'violations'" class="violations-list">
      <div v-for="v in violations" :key="v.timestamp + v.memory_id" class="violation-item">
        <span class="severity-dot" :class="v.severity"></span>
        <div class="violation-info">
          <span class="violation-policy">{{ v.policy_name }}</span>
          <span class="violation-memory">{{ v.memory_title }}</span>
        </div>
        <span class="violation-action">{{ v.action }}</span>
        <span class="violation-time">{{ formatTime(v.timestamp) }}</span>
      </div>
      <div v-if="!violations.length" class="empty-state">
        <p>🎉 No violations recorded.</p>
      </div>
    </div>

    <!-- Report Tab -->
    <div v-if="tab === 'report' && report" class="report-section">
      <div class="report-grid">
        <div class="report-card">
          <h4>Violations by Type</h4>
          <div v-for="(count, type) in report.violations_by_type" :key="type" class="report-bar">
            <span class="bar-label">{{ type }}</span>
            <div class="bar-track">
              <div class="bar-fill" :style="{ width: (count / report.violating_memories * 100) + '%' }"></div>
            </div>
            <span class="bar-value">{{ count }}</span>
          </div>
          <p v-if="!Object.keys(report.violations_by_type || {}).length" class="no-data">No violations</p>
        </div>
        <div class="report-card">
          <h4>Violations by Severity</h4>
          <div v-for="(count, sev) in report.violations_by_severity" :key="sev" class="report-bar">
            <span class="bar-label severity" :class="String(sev)">{{ sev }}</span>
            <div class="bar-track">
              <div class="bar-fill" :style="{ width: (count / report.violating_memories * 100) + '%' }"></div>
            </div>
            <span class="bar-value">{{ count }}</span>
          </div>
          <p v-if="!Object.keys(report.violations_by_severity || {}).length" class="no-data">No violations</p>
        </div>
      </div>
    </div>

    <!-- Create Policy Modal -->
    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Create Governance Policy</h3>
          <button class="btn-close" @click="showCreate = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Name</label>
            <input v-model="newPolicy.name" placeholder="e.g. 90-Day Retention" />
          </div>
          <div class="form-group">
            <label>Description</label>
            <input v-model="newPolicy.description" placeholder="What does this policy enforce?" />
          </div>
          <div class="form-group">
            <label>Type</label>
            <select v-model="newPolicy.type">
              <option value="retention">Retention</option>
              <option value="quality">Quality</option>
              <option value="tagging">Tagging</option>
              <option value="access">Access</option>
            </select>
          </div>
          <div class="form-group">
            <label>Action</label>
            <select v-model="newPolicy.action">
              <option value="flag">Flag</option>
              <option value="archive">Archive</option>
              <option value="delete">Delete</option>
              <option value="notify">Notify</option>
              <option value="require_approval">Require Approval</option>
            </select>
          </div>
          <div class="form-group">
            <label>Severity</label>
            <select v-model="newPolicy.severity">
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
              <option value="critical">Critical</option>
            </select>
          </div>
          <div class="form-group">
            <label>Conditions</label>
            <div v-for="(c, i) in newPolicy.conditions" :key="i" class="condition-row">
              <select v-model="c.field">
                <option value="age_days">Age (days)</option>
                <option value="strength">Strength</option>
                <option value="title_length">Title Length</option>
                <option value="concepts_count">Concepts Count</option>
                <option value="tags_count">Tags Count</option>
                <option value="has_title">Has Title</option>
                <option value="type">Type</option>
              </select>
              <select v-model="c.operator">
                <option value="gt">Greater Than</option>
                <option value="lt">Less Than</option>
                <option value="eq">Equals</option>
                <option value="neq">Not Equals</option>
                <option value="contains">Contains</option>
                <option value="exists">Exists</option>
                <option value="not_exists">Not Exists</option>
              </select>
              <input v-model="c.value" placeholder="Value" />
              <button class="btn-remove" @click="newPolicy.conditions.splice(i, 1)">✕</button>
            </div>
            <button class="btn-add-condition" @click="addCondition">+ Add Condition</button>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showCreate = false">Cancel</button>
          <button class="btn-save" @click="createPolicy" :disabled="!newPolicy.name">Create</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { request } from '@/api/index'

const tab = ref('policies')
const policies = ref<any[]>([])
const violations = ref<any[]>([])
const report = ref<any>(null)
const evaluating = ref(false)
const showCreate = ref(false)
const newPolicy = ref({
  name: '',
  description: '',
  type: 'retention',
  action: 'flag',
  severity: 'warning',
  conditions: [] as any[],
})

const complianceClass = computed(() => {
  const rate = report.value?.compliance_rate || 0
  if (rate >= 90) return 'good'
  if (rate >= 70) return 'warn'
  return 'bad'
})

async function loadPolicies() {
  try {
    const res = await request<any>('/governance/policies')
    policies.value = res.policies || []
  } catch {}
}

async function loadViolations() {
  try {
    const res = await request<any>('/governance/violations')
    violations.value = res.violations || []
  } catch {}
}

async function loadReport() {
  try {
    const res = await request<any>('/governance/compliance-report')
    report.value = res
  } catch {}
}

async function evaluateAll() {
  evaluating.value = true
  try {
    await request<any>('/governance/evaluate', { method: 'POST' })
    await Promise.all([loadViolations(), loadReport()])
  } catch {}
  evaluating.value = false
}

async function evaluatePolicy(id: string) {
  try {
    await request<any>(`/governance/policies/${id}/evaluate`, { method: 'POST' })
    await Promise.all([loadViolations(), loadReport()])
  } catch {}
}

async function togglePolicy(id: string) {
  try {
    await request<any>(`/governance/policies/${id}/toggle`, { method: 'POST' })
    await loadPolicies()
  } catch {}
}

async function deletePolicy(id: string) {
  try {
    await request<any>(`/governance/policies/${id}`, { method: 'DELETE' })
    await loadPolicies()
  } catch {}
}

async function createPolicy() {
  try {
    await request<any>('/governance/policies', {
      method: 'POST',
      body: JSON.stringify(newPolicy.value),
    })
    showCreate.value = false
    newPolicy.value = { name: '', description: '', type: 'retention', action: 'flag', severity: 'warning', conditions: [] }
    await loadPolicies()
  } catch {}
}

function addCondition() {
  newPolicy.value.conditions.push({ field: 'age_days', operator: 'gt', value: '' })
}

function formatTime(ts: string): string {
  if (!ts) return ''
  try { return new Date(ts).toLocaleString() } catch { return ts }
}

onMounted(() => {
  loadPolicies()
  loadViolations()
  loadReport()
})
</script>

<style scoped>
.governance-view { padding-bottom: 40px; }
.gv-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.gv-header h2 { font-size: 1.5rem; font-weight: 600; margin: 0; }
.gv-actions { display: flex; gap: 8px; }
.btn-evaluate, .btn-create {
  padding: 8px 16px; border: none; border-radius: 8px;
  font-size: 0.85rem; cursor: pointer; font-family: var(--font);
}
.btn-evaluate { background: var(--tag-bg); border: 1px solid var(--border); }
.btn-create { background: var(--accent); color: #fff; }
.btn-evaluate:disabled { opacity: 0.6; }

.compliance-bar {
  background: var(--card); border: 1px solid var(--border); border-radius: 12px;
  padding: 16px; margin-bottom: 20px;
}
.compliance-stats { display: flex; gap: 32px; margin-bottom: 12px; }
.stat { display: flex; flex-direction: column; }
.stat-value { font-size: 1.4rem; font-weight: 700; color: var(--primary); }
.stat-label { font-size: 0.75rem; color: var(--text-secondary); }
.compliance-meter { height: 8px; background: var(--tag-bg); border-radius: 4px; overflow: hidden; }
.meter-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }
.meter-fill.good { background: #34c759; }
.meter-fill.warn { background: #ff9500; }
.meter-fill.bad { background: #ff3b30; }

.tabs { display: flex; gap: 4px; margin-bottom: 16px; }
.tabs button {
  padding: 8px 16px; border: 1px solid var(--border); border-radius: 8px;
  background: var(--card); cursor: pointer; font-family: var(--font); font-size: 0.85rem;
}
.tabs button.active { background: var(--accent); color: #fff; border-color: var(--accent); }

.policy-card {
  background: var(--card); border: 1px solid var(--border); border-radius: 12px;
  padding: 16px; margin-bottom: 12px;
}
.policy-card.disabled { opacity: 0.6; }
.policy-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.policy-info { display: flex; align-items: center; gap: 8px; }
.policy-info h3 { margin: 0; font-size: 1rem; }
.policy-type-badge {
  padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;
  text-transform: uppercase;
}
.policy-type-badge.retention { background: #e3f2fd; color: #1565c0; }
.policy-type-badge.quality { background: #e8f5e9; color: #2e7d32; }
.policy-type-badge.tagging { background: #fff3e0; color: #e65100; }
.policy-type-badge.access { background: #fce4ec; color: #c62828; }
.policy-desc { font-size: 0.85rem; color: var(--text-secondary); margin: 0 0 8px; }
.policy-meta { display: flex; gap: 12px; font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 8px; }
.severity.info { color: #007aff; }
.severity.warning { color: #ff9500; }
.severity.error { color: #ff3b30; }
.severity.critical { color: #af2d1f; font-weight: 700; }
.policy-actions { display: flex; gap: 8px; }
.btn-sm {
  padding: 4px 10px; border: 1px solid var(--border); border-radius: 6px;
  background: var(--tag-bg); cursor: pointer; font-size: 0.75rem; font-family: var(--font);
}
.btn-danger { border-color: var(--error); color: var(--error); }

.toggle { position: relative; display: inline-block; width: 40px; height: 22px; }
.toggle input { opacity: 0; width: 0; height: 0; }
.toggle-slider {
  position: absolute; cursor: pointer; inset: 0; background: var(--border);
  border-radius: 22px; transition: 0.3s;
}
.toggle-slider::before {
  content: ''; position: absolute; height: 16px; width: 16px; left: 3px; bottom: 3px;
  background: white; border-radius: 50%; transition: 0.3s;
}
.toggle input:checked + .toggle-slider { background: var(--accent); }
.toggle input:checked + .toggle-slider::before { transform: translateX(18px); }

.violation-item {
  display: flex; align-items: center; gap: 12px; padding: 10px 12px;
  background: var(--card); border: 1px solid var(--border); border-radius: 8px; margin-bottom: 8px;
}
.severity-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.severity-dot.info { background: #007aff; }
.severity-dot.warning { background: #ff9500; }
.severity-dot.error { background: #ff3b30; }
.severity-dot.critical { background: #af2d1f; }
.violation-info { flex: 1; display: flex; flex-direction: column; }
.violation-policy { font-weight: 600; font-size: 0.85rem; }
.violation-memory { font-size: 0.75rem; color: var(--text-secondary); }
.violation-action { font-size: 0.75rem; color: var(--text-secondary); }
.violation-time { font-size: 0.7rem; color: var(--text-secondary); }

.report-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.report-card {
  background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 16px;
}
.report-card h4 { margin: 0 0 12px; font-size: 0.9rem; }
.report-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.bar-label { width: 100px; font-size: 0.8rem; text-transform: capitalize; }
.bar-track { flex: 1; height: 6px; background: var(--tag-bg); border-radius: 3px; }
.bar-fill { height: 100%; background: var(--accent); border-radius: 3px; }
.bar-value { width: 30px; text-align: right; font-size: 0.8rem; font-weight: 600; }
.no-data { font-size: 0.85rem; color: var(--text-secondary); }

.empty-state { text-align: center; padding: 40px; color: var(--text-secondary); }

.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100;
  display: flex; align-items: center; justify-content: center; padding: 20px;
}
.modal {
  background: var(--card); border-radius: 16px; width: 100%; max-width: 560px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-height: 80vh; overflow-y: auto;
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; border-bottom: 1px solid var(--border);
}
.modal-header h3 { margin: 0; }
.btn-close { background: none; border: none; font-size: 1.2rem; cursor: pointer; }
.modal-body { padding: 20px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-size: 0.8rem; font-weight: 600; margin-bottom: 4px; }
.form-group input, .form-group select {
  width: 100%; padding: 8px 10px; border: 1px solid var(--border);
  border-radius: 8px; font-size: 0.85rem; font-family: var(--font); box-sizing: border-box;
}
.condition-row { display: flex; gap: 6px; margin-bottom: 6px; align-items: center; }
.condition-row select, .condition-row input { flex: 1; padding: 6px; font-size: 0.8rem; border: 1px solid var(--border); border-radius: 6px; }
.btn-remove { background: none; border: none; color: var(--error); cursor: pointer; font-size: 1rem; }
.btn-add-condition {
  padding: 4px 10px; background: var(--tag-bg); border: 1px dashed var(--border);
  border-radius: 6px; cursor: pointer; font-size: 0.8rem; font-family: var(--font);
}
.modal-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 12px 20px; border-top: 1px solid var(--border);
}
.btn-cancel, .btn-save {
  padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; cursor: pointer; font-family: var(--font);
}
.btn-cancel { background: var(--card); border: 1px solid var(--border); }
.btn-save { background: var(--accent); color: #fff; border: none; }
.btn-save:disabled { opacity: 0.5; }

@media (max-width: 767px) {
  .report-grid { grid-template-columns: 1fr; }
  .compliance-stats { flex-wrap: wrap; gap: 16px; }
}
</style>
