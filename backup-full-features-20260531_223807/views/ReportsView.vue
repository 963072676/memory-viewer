<template>
  <div class="reports-view">
    <div class="reports-header">
      <h2>📊 Advanced Export & Reporting</h2>
      <div class="header-controls">
        <select v-model="selectedTemplate" class="template-select">
          <option value="">Select a report template...</option>
          <option v-for="tpl in templates" :key="tpl.id" :value="tpl.id">
            {{ tpl.icon }} {{ tpl.name }}
          </option>
        </select>
        <button class="btn-generate" @click="showFilters = !showFilters">
          🔍 Filters {{ hasFilters ? '*' : '' }}
        </button>
        <button class="btn-generate primary" @click="generateReport" :disabled="generating || !selectedTemplate">
          {{ generating ? '⏳ Generating...' : '📄 Generate Report' }}
        </button>
      </div>
    </div>

    <!-- Filters Panel -->
    <div v-if="showFilters" class="filters-panel">
      <div class="filter-row">
        <div class="filter-group">
          <label>Type Filter</label>
          <select v-model="filters.type" class="filter-select">
            <option value="">All Types</option>
            <option value="pattern">Pattern</option>
            <option value="fact">Fact</option>
            <option value="preference">Preference</option>
            <option value="workflow">Workflow</option>
            <option value="bug">Bug</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Tag Filter</label>
          <input v-model="filters.tag" type="text" placeholder="Filter by tag..." class="filter-input" />
        </div>
        <div class="filter-group">
          <label>Search Query</label>
          <input v-model="filters.q" type="text" placeholder="Search in title/content..." class="filter-input" />
        </div>
        <div class="filter-actions">
          <button class="btn-clear" @click="clearFilters">Clear</button>
        </div>
      </div>
    </div>

    <!-- Preview area -->
    <div v-if="currentReport" class="report-preview">
      <div class="preview-header">
        <div class="preview-info">
          <h3>{{ currentReport.template_name }}</h3>
          <span class="preview-meta">
            {{ currentReport.memory_count }} memories | Generated {{ formatTime(currentReport.generated_at) }}
          </span>
        </div>
        <div class="preview-actions">
          <button class="btn-action" @click="downloadReport(currentReport.id, 'html')">
            📥 Download HTML
          </button>
          <button class="btn-action" @click="viewFullReport(currentReport.id)">
            🔍 View Full Report
          </button>
        </div>
      </div>
      <div class="preview-frame-wrapper">
        <iframe v-if="currentReportContent" :srcdoc="currentReportContent" class="preview-frame" sandbox="allow-same-origin"></iframe>
        <div v-else class="preview-loading">Loading preview...</div>
      </div>
    </div>

    <!-- History Sidebar / Main -->
    <div class="reports-content">
      <div class="reports-main">
        <div v-if="!currentReport && !generating" class="empty-state">
          <div class="empty-icon">📊</div>
          <h3>Advanced Export & Reporting</h3>
          <p>Select a template and click "Generate Report" to create a new report.</p>
          <p class="empty-hint">Reports can be filtered by type, tag, or search query.</p>
        </div>
        <div v-if="generating" class="loading-state">
          <div class="spinner"></div>
          <p>Generating report...</p>
          <p class="loading-detail">This may take a few seconds for large datasets.</p>
        </div>
      </div>

      <!-- History Sidebar -->
      <div class="reports-sidebar">
        <h3>📜 Report History</h3>
        <div v-if="history.length === 0" class="empty-hint">No reports generated yet</div>
        <div v-else class="history-list">
          <div
            v-for="report in history"
            :key="report.id"
            class="history-item"
            :class="{ active: currentReport?.id === report.id }"
            @click="selectReport(report)"
          >
            <div class="history-icon">{{ getTemplateIcon(report.template_id) }}</div>
            <div class="history-info">
              <div class="history-name">{{ report.template_name }}</div>
              <div class="history-meta">
                {{ report.memory_count }} memories | {{ formatTime(report.generated_at) }}
              </div>
            </div>
            <button class="btn-download-sm" @click.stop="downloadReport(report.id, 'html')" title="Download">
              📥
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'

interface Report {
  id: string
  template_id: string
  template_name: string
  format: string
  filters: Record<string, string>
  memory_count: number
  generated_at: string
  elapsed_seconds: number
  size_bytes: number
}

interface ReportTemplate {
  id: string
  name: string
  description: string
  icon: string
  format: string
}

const toast = useToast()
const templates = ref<ReportTemplate[]>([])
const history = ref<Report[]>([])
const selectedTemplate = ref('')
const generating = ref(false)
const currentReport = ref<Report | null>(null)
const currentReportContent = ref('')
const showFilters = ref(false)
const filters = ref<Record<string, string>>({})

const hasFilters = computed(() => Object.values(filters.value).some(v => v && v.trim() !== ''))

function getTemplateIcon(templateId: string): string {
  const tpl = templates.value.find(t => t.id === templateId)
  return tpl?.icon || '📄'
}

function formatTime(isoString: string): string {
  if (!isoString) return 'N/A'
  const d = new Date(isoString.replace('Z', '+00:00'))
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

async function loadTemplates() {
  try {
    const res = await request<any>('/reports/templates')
    templates.value = res.templates || []
  } catch (e: any) {
    toast.error('Failed to load templates')
  }
}

async function loadHistory() {
  try {
    const res = await request<any>('/reports/history')
    history.value = res.reports || []
  } catch (e: any) {
    // silently fail - history not critical
  }
}

async function generateReport() {
  if (!selectedTemplate.value) {
    toast.error('Please select a template first')
    return
  }
  generating.value = true
  currentReport.value = null
  currentReportContent.value = ''
  try {
    const res = await request<any>('/reports/generate', {
      method: 'POST',
      body: JSON.stringify({
        template_id: selectedTemplate.value,
        filters: filters.value,
        format: 'html',
      }),
    })
    currentReport.value = res.report
    currentReportContent.value = res.content || ''
    toast.success('Report generated!')
    await loadHistory()
  } catch (e: any) {
    toast.error(e.message || 'Failed to generate report')
  } finally {
    generating.value = false
  }
}

async function selectReport(report: Report) {
  try {
    currentReport.value = report
    // Get content
    const content = await request<string>(`/reports/${report.id}/content`)
    // The content endpoint returns raw HTML, but our request wrapper tries to parse JSON
    // Use fetch directly for raw HTML
    const apiBase = '/api'
    const response = await fetch(`${apiBase}/reports/${report.id}/content`)
    currentReportContent.value = await response.text()
  } catch (e: any) {
    toast.error('Failed to load report')
  }
}

function downloadReport(reportId: string, format: string) {
  window.open(`/api/reports/${reportId}/download?format=${format}`, '_blank')
}

function viewFullReport(reportId: string) {
  window.open(`/api/reports/${reportId}/content`, '_blank')
}

function clearFilters() {
  filters.value = { type: '', tag: '', q: '' }
}

onMounted(() => {
  loadTemplates()
  loadHistory()
})
</script>

<style scoped>
.reports-view { padding-bottom: 40px; }
.reports-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
}
.reports-header h2 { font-size: 1.5rem; font-weight: 600; color: var(--primary, #007aff); margin: 0; }
.header-controls { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.template-select {
  padding: 8px 12px; border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px; background: var(--card, #fff); font-size: 0.85rem;
  font-family: var(--font); color: var(--text, #1d1d1f); min-width: 200px;
}
.btn-generate {
  padding: 8px 14px; border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px; background: var(--card, #fff); color: var(--text, #1d1d1f);
  font-size: 0.85rem; cursor: pointer; font-family: var(--font);
}
.btn-generate.primary { background: var(--accent, #007aff); color: #fff; border-color: var(--accent, #007aff); }
.btn-generate:disabled { opacity: 0.5; cursor: not-allowed; }
.filters-panel {
  background: var(--card, #fff); border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px; padding: 16px; margin-bottom: 20px;
}
.filter-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; }
.filter-group { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 150px; }
.filter-group label { font-size: 0.75rem; font-weight: 600; color: var(--text-secondary, #86868b); text-transform: uppercase; }
.filter-select, .filter-input {
  padding: 8px 10px; border: 1px solid var(--border, #e5e5ea);
  border-radius: 6px; font-size: 0.85rem; font-family: var(--font);
  background: var(--bg, #f5f5f7); color: var(--text, #1d1d1f);
}
.filter-actions { display: flex; align-items: flex-end; }
.btn-clear {
  padding: 8px 14px; border: 1px solid var(--border, #e5e5ea);
  border-radius: 6px; background: transparent; color: var(--text-secondary, #86868b);
  font-size: 0.85rem; cursor: pointer; font-family: var(--font);
}
.report-preview {
  background: var(--card, #fff); border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px; padding: 16px; margin-bottom: 20px;
}
.preview-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px; flex-wrap: wrap; gap: 8px;
}
.preview-info h3 { margin: 0; font-size: 1rem; color: var(--primary, #007aff); }
.preview-meta { font-size: 0.8rem; color: var(--text-secondary, #86868b); }
.preview-actions { display: flex; gap: 8px; }
.btn-action {
  padding: 6px 12px; border: 1px solid var(--border, #e5e5ea);
  border-radius: 6px; background: var(--bg, #f5f5f7); font-size: 0.8rem;
  cursor: pointer; font-family: var(--font);
}
.preview-frame-wrapper { border: 1px solid var(--border, #e5e5ea); border-radius: 8px; overflow: hidden; }
.preview-frame { width: 100%; height: 500px; border: none; }
.preview-loading { padding: 40px; text-align: center; color: var(--text-secondary, #86868b); }
.reports-content { display: grid; grid-template-columns: 1fr 300px; gap: 24px; }
@media (max-width: 767px) { .reports-content { grid-template-columns: 1fr; } }
.reports-sidebar {
  background: var(--card, #fff); border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px; padding: 16px; height: fit-content;
}
.reports-sidebar h3 { margin: 0 0 12px; font-size: 1rem; font-weight: 600; }
.empty-hint { text-align: center; color: var(--text-secondary, #86868b); font-size: 0.85rem; padding: 20px; }
.empty-state { text-align: center; padding: 60px 20px; color: var(--text-secondary, #86868b); }
.empty-icon { font-size: 3rem; margin-bottom: 12px; }
.empty-state h3 { margin: 0 0 8px; color: var(--text, #1d1d1f); }
.empty-state p { margin: 0 0 8px; }
.empty-hint { font-size: 0.8rem; }
.loading-state { text-align: center; padding: 60px 20px; }
.spinner { width: 32px; height: 32px; border: 3px solid var(--border, #e5e5ea); border-top-color: var(--accent, #007aff); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 12px; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-detail { font-size: 0.85rem; color: var(--text-secondary, #86868b); }
.history-list { display: flex; flex-direction: column; gap: 8px; }
.history-item {
  display: flex; align-items: center; gap: 8px; padding: 8px;
  border-radius: 8px; cursor: pointer; transition: background 0.15s;
  border: 1px solid transparent;
}
.history-item:hover { background: var(--bg, #f5f5f7); }
.history-item.active { background: var(--bg, #f5f5f7); border-color: var(--accent, #007aff); }
.history-icon { font-size: 1.2rem; }
.history-info { flex: 1; min-width: 0; }
.history-name { font-size: 0.85rem; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.history-meta { font-size: 0.7rem; color: var(--text-secondary, #86868b); }
.btn-download-sm {
  padding: 4px 6px; border: none; background: transparent; cursor: pointer;
  font-size: 0.9rem; border-radius: 4px;
}
.btn-download-sm:hover { background: var(--border, #e5e5ea); }
</style>