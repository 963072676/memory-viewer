<template>
  <div class="templates-view">
    <div class="templates-header">
      <h2>📝 Memory Templates</h2>
      <button class="btn-create" @click="showEditor = true">+ New Template</button>
    </div>

    <div v-if="showEditor" class="editor-overlay">
      <TemplateEditor @close="showEditor = false" @saved="onTemplateSaved" />
    </div>

    <div v-if="showForm" class="editor-overlay">
      <TemplateForm :template="activeTemplate" @close="showForm = false" @created="onMemoryCreated" />
    </div>

    <div class="template-gallery">
      <TemplateCard
        v-for="tpl in templates"
        :key="tpl.id"
        :template="tpl"
        @use="useTemplate"
        @edit="editTemplate"
        @delete="deleteTemplate"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'
import TemplateCard from '@/components/Layout/TemplateCard.vue'
import TemplateEditor from '@/components/Layout/TemplateEditor.vue'
import TemplateForm from '@/components/Layout/TemplateForm.vue'

const toast = useToast()
const templates = ref<any[]>([])
const showEditor = ref(false)
const showForm = ref(false)
const activeTemplate = ref<any>(null)

async function loadTemplates() {
  try {
    const res = await request<any>('/templates')
    templates.value = res.templates || []
  } catch {}
}

function useTemplate(tpl: any) {
  activeTemplate.value = tpl
  showForm.value = true
}

function editTemplate(tpl: any) {
  activeTemplate.value = tpl
  showEditor.value = true
}

async function deleteTemplate(tpl: any) {
  if (tpl.builtin) { toast.error('Cannot delete built-in templates'); return }
  try {
    await request<any>(`/templates/${tpl.id}`, { method: 'DELETE' })
    toast.success('Template deleted')
    await loadTemplates()
  } catch {}
}

function onTemplateSaved() {
  showEditor.value = false
  loadTemplates()
}

function onMemoryCreated() {
  showForm.value = false
  toast.success('Memory created from template!')
}

onMounted(() => loadTemplates())
</script>

<style scoped>
.templates-view { padding-bottom: 40px; }
.templates-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;
}
.templates-header h2 { font-size: 1.5rem; font-weight: 600; color: var(--primary, #007aff); margin: 0; }
.btn-create {
  padding: 8px 16px; border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px; background: var(--accent, #007aff); color: #fff;
  font-size: 0.85rem; cursor: pointer; font-family: var(--font);
}
.template-gallery {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px;
}
.editor-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100;
  display: flex; align-items: center; justify-content: center; padding: 20px;
}
</style>
