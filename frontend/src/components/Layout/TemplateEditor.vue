<template>
  <div class="template-editor">
    <div class="editor-header">
      <h3>{{ isEdit ? 'Edit Template' : 'New Template' }}</h3>
      <button class="btn-close" @click="$emit('close')">✕</button>
    </div>
    <div class="editor-body">
      <div class="form-group">
        <label>Name</label>
        <input v-model="form.name" placeholder="Template name" />
      </div>
      <div class="form-group">
        <label>Description</label>
        <input v-model="form.description" placeholder="Description" />
      </div>
      <div class="form-group">
        <label>Icon</label>
        <input v-model="form.icon" placeholder="📝" style="width: 60px;" />
      </div>
      <div class="form-group">
        <label>Title Template</label>
        <input v-model="form.title_template" placeholder="e.g. Task: {task_name}" />
      </div>
      <div class="form-group">
        <label>Content Template</label>
        <textarea v-model="form.content_template" rows="4" placeholder="e.g. Task: {task_name}&#10;Outcome: {outcome}"></textarea>
      </div>
      <div class="form-group">
        <label>Default Type</label>
        <select v-model="form.default_type">
          <option value="fact">Fact</option>
          <option value="pattern">Pattern</option>
          <option value="preference">Preference</option>
          <option value="bug">Bug</option>
          <option value="workflow">Workflow</option>
        </select>
      </div>
      <div class="form-group">
        <label>Default Tags (comma-separated)</label>
        <input v-model="tagsInput" placeholder="tag1, tag2" />
      </div>

      <!-- Fields -->
      <div class="fields-section">
        <div class="fields-header">
          <label>Fields</label>
          <button class="btn-add-field" @click="addField">+ Add Field</button>
        </div>
        <div v-for="(field, i) in form.fields" :key="i" class="field-row">
          <input v-model="field.name" placeholder="name" class="field-input" />
          <input v-model="field.label" placeholder="label" class="field-input" />
          <select v-model="field.type" class="field-select">
            <option value="text">text</option>
            <option value="select">select</option>
            <option value="tags">tags</option>
            <option value="number">number</option>
            <option value="date">date</option>
          </select>
          <label class="field-req"><input type="checkbox" v-model="field.required" /> Req</label>
          <button class="btn-remove" @click="form.fields.splice(i, 1)">✕</button>
        </div>
      </div>
    </div>
    <div class="editor-footer">
      <button class="btn-cancel" @click="$emit('close')">Cancel</button>
      <button class="btn-save" @click="save" :disabled="!form.name">Save</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'

const emit = defineEmits<{ close: []; saved: [] }>()
const toast = useToast()

const form = ref({
  name: '', description: '', icon: '📝',
  title_template: '', content_template: '',
  default_type: 'fact', default_tags: [] as string[],
  fields: [] as any[],
})
const tagsInput = ref('')
const isEdit = computed(() => false)

function addField() {
  form.value.fields.push({ name: '', label: '', type: 'text', required: false })
}

async function save() {
  try {
    form.value.default_tags = tagsInput.value.split(',').map(t => t.trim()).filter(Boolean)
    await request<any>('/templates', {
      method: 'POST',
      body: JSON.stringify(form.value),
    })
    toast.success('Template created!')
    emit('saved')
  } catch (e: any) {
    toast.error(e.message || 'Failed to save template')
  }
}
</script>

<style scoped>
.template-editor {
  background: var(--card, #fff); border-radius: 16px; width: 100%; max-width: 600px;
  max-height: 80vh; overflow-y: auto; box-shadow: var(--shadow-modal);
}
.editor-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; border-bottom: 1px solid var(--border, #e5e5ea);
}
.editor-header h3 { margin: 0; font-size: 1.1rem; }
.btn-close { background: none; border: none; font-size: 1.2rem; cursor: pointer; }
.editor-body { padding: 20px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-size: 0.8rem; font-weight: 600; margin-bottom: 4px; color: var(--text-secondary, #86868b); }
.form-group input, .form-group textarea, .form-group select {
  width: 100%; padding: 8px 10px; border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px; font-size: 0.85rem; font-family: var(--font);
  background: var(--card, #fff); color: var(--text, #1d1d1f); box-sizing: border-box;
}
.fields-section { margin-top: 16px; }
.fields-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.btn-add-field {
  padding: 4px 10px; border: 1px solid var(--border, #e5e5ea);
  border-radius: 6px; background: var(--tag-bg, #f5f5f7); font-size: 0.8rem; cursor: pointer;
}
.field-row { display: flex; gap: 6px; margin-bottom: 6px; align-items: center; }
.field-input { flex: 1; padding: 6px 8px; border: 1px solid var(--border, #e5e5ea); border-radius: 6px; font-size: 0.8rem; }
.field-select { width: 80px; padding: 6px; border: 1px solid var(--border, #e5e5ea); border-radius: 6px; font-size: 0.8rem; }
.field-req { font-size: 0.75rem; display: flex; align-items: center; gap: 2px; }
.btn-remove { background: none; border: none; color: var(--error, #ff3b30); cursor: pointer; }
.editor-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 12px 20px; border-top: 1px solid var(--border, #e5e5ea);
}
.btn-cancel, .btn-save {
  padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; cursor: pointer; font-family: var(--font);
}
.btn-cancel { background: var(--card, #fff); border: 1px solid var(--border, #e5e5ea); }
.btn-save { background: var(--accent, #007aff); color: #fff; border: none; }
.btn-save:disabled { opacity: 0.5; }
</style>
