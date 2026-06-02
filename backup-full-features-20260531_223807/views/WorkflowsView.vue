<template>
  <div class="workflows-view">
    <div class="workflows-header">
      <h2>⚙️ 工作流自动化</h2>
      <div class="header-actions">
        <button class="btn-create" @click="showBuilder = true">+ 创建规则</button>
      </div>
    </div>

    <!-- Templates -->
    <div v-if="workflows.length === 0 && !loading" class="templates-section">
      <h3>🚀 快速开始 — 选择模板</h3>
      <div class="template-cards">
        <div v-for="tpl in templates" :key="tpl.id" class="template-card" @click="createFromTemplate(tpl)">
          <div class="template-icon">{{ tpl.icon }}</div>
          <div class="template-name">{{ tpl.name }}</div>
          <div class="template-desc">{{ tpl.description }}</div>
        </div>
      </div>
    </div>

    <!-- Workflow List -->
    <div v-if="loading" class="loading-state">加载工作流...</div>
    <div v-else-if="workflows.length > 0" class="workflow-list">
      <div v-for="wf in workflows" :key="wf.id" class="workflow-card" :class="{ disabled: !wf.enabled }">
        <div class="wf-header">
          <div class="wf-title">
            <span class="wf-icon">{{ wf.enabled ? '🟢' : '⚪' }}</span>
            {{ wf.name }}
          </div>
          <div class="wf-actions">
            <button class="btn-sm" @click="toggleWorkflow(wf)">{{ wf.enabled ? '禁用' : '启用' }}</button>
            <button class="btn-sm" @click="executeWorkflow(wf)">▶ 执行</button>
            <button class="btn-sm btn-danger" @click="deleteWorkflow(wf)">🗑️</button>
          </div>
        </div>
        <div class="wf-meta">
          <span>触发: {{ wf.trigger?.type || 'manual' }}</span>
          <span>条件: {{ wf.conditions?.length || 0 }} 个</span>
          <span>动作: {{ wf.actions?.length || 0 }} 个</span>
        </div>
        <WorkflowLog :logs="wf.recent_logs || []" />
      </div>
    </div>

    <!-- Builder Modal -->
    <div v-if="showBuilder" class="modal-overlay" @click.self="showBuilder = false">
      <div class="modal-content">
        <WorkflowBuilder @save="handleSave" @cancel="showBuilder = false" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'
import WorkflowBuilder from '@/components/Layout/WorkflowBuilder.vue'
import WorkflowLog from '@/components/Layout/WorkflowLog.vue'

const toast = useToast()
const loading = ref(false)
const showBuilder = ref(false)
const workflows = ref<any[]>([])

const templates = [
  { id: 'archive-stale', name: '归档过期记忆', icon: '📦', description: '自动归档超过 90 天未更新且强度低于 0.3 的记忆', trigger: { type: 'schedule', config: { cron: '0 3 * * 0' } }, conditions: [{ field: 'age_days', op: '>', value: 90 }, { field: 'strength', op: '<', value: 0.3 }], actions: [{ type: 'archive' }] },
  { id: 'cleanup-low', name: '清理低强度记忆', icon: '🧹', description: '删除强度低于 0.1 的记忆', trigger: { type: 'schedule', config: { cron: '0 4 1 * *' } }, conditions: [{ field: 'strength', op: '<', value: 0.1 }], actions: [{ type: 'delete' }] },
  { id: 'auto-tag-new', name: '新建记忆自动标签', icon: '🏷️', description: '新创建的记忆自动根据内容打标签', trigger: { type: 'on_memory_create' }, conditions: [], actions: [{ type: 'auto_tag' }] },
]

async function loadWorkflows() {
  loading.value = true
  try {
    const res = await request<any>('/workflows')
    workflows.value = res.workflows || []
  } catch (e: any) {
    toast.error('加载工作流失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

async function createFromTemplate(tpl: any) {
  try {
    await request('/workflows', { method: 'POST', body: JSON.stringify({ name: tpl.name, description: tpl.description, trigger: tpl.trigger, conditions: tpl.conditions, actions: tpl.actions, enabled: true }) })
    toast.success(`已创建: ${tpl.name}`)
    await loadWorkflows()
  } catch (e: any) {
    toast.error('创建失败: ' + e.message)
  }
}

async function handleSave(rule: any) {
  try {
    await request('/workflows', { method: 'POST', body: rule })
    toast.success('规则已创建')
    showBuilder.value = false
    await loadWorkflows()
  } catch (e: any) {
    toast.error('保存失败: ' + e.message)
  }
}

async function toggleWorkflow(wf: any) {
  try {
    await request(`/workflows/${wf.id}`, { method: 'PUT', body: JSON.stringify({ enabled: !wf.enabled }) })
    wf.enabled = !wf.enabled
  } catch (e: any) {
    toast.error('更新失败')
  }
}

async function executeWorkflow(wf: any) {
  try {
    const res = await request<any>(`/workflows/${wf.id}/execute`, { method: 'POST' })
    toast.success(`执行完成: ${res.affected || 0} 条记忆受影响`)
    await loadWorkflows()
  } catch (e: any) {
    toast.error('执行失败: ' + e.message)
  }
}

async function deleteWorkflow(wf: any) {
  if (!confirm(`确定删除规则 "${wf.name}"?`)) return
  try {
    await request(`/workflows/${wf.id}`, { method: 'DELETE' })
    toast.success('已删除')
    await loadWorkflows()
  } catch (e: any) {
    toast.error('删除失败')
  }
}

onMounted(loadWorkflows)
</script>

<style scoped>
.workflows-view { padding: 20px; }
.workflows-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.btn-create { background: #007aff; color: white; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 14px; }
.templates-section { margin-bottom: 24px; }
.template-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; margin-top: 12px; }
.template-card { background: var(--card-bg, #f8f9fa); border: 1px solid var(--border, #e0e0e0); border-radius: 12px; padding: 16px; cursor: pointer; transition: all 0.2s; }
.template-card:hover { border-color: #007aff; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.template-icon { font-size: 28px; margin-bottom: 8px; }
.template-name { font-weight: 600; margin-bottom: 4px; }
.template-desc { font-size: 12px; color: #666; }
.workflow-card { background: var(--card-bg, #fff); border: 1px solid var(--border, #e0e0e0); border-radius: 12px; padding: 16px; margin-bottom: 12px; }
.workflow-card.disabled { opacity: 0.6; }
.wf-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.wf-title { font-weight: 600; font-size: 16px; }
.wf-icon { margin-right: 8px; }
.wf-actions { display: flex; gap: 8px; }
.btn-sm { padding: 4px 10px; border: 1px solid var(--border, #ddd); border-radius: 6px; background: var(--card-bg, #f8f9fa); cursor: pointer; font-size: 12px; }
.btn-sm:hover { background: #eee; }
.btn-danger { color: #ff3b30; }
.wf-meta { display: flex; gap: 16px; font-size: 13px; color: #666; margin-bottom: 8px; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: var(--card-bg, #fff); border-radius: 16px; padding: 24px; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto; }
.loading-state { text-align: center; padding: 40px; color: #999; }
</style>
