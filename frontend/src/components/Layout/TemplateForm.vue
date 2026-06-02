<template>
  <div class="template-form">
    <div class="form-header">
      <h3>{{ template?.icon }} {{ template?.name }}</h3>
      <button class="btn-close" @click="$emit('close')">✕</button>
    </div>
    <div class="form-body">
      <p class="form-desc">{{ template?.description }}</p>
      <div v-for="field in (template?.fields || [])" :key="field.name" class="form-group">
        <label>
          {{ field.label }}
          <span v-if="field.required" class="required">*</span>
        </label>
        <!-- Text input -->
        <input v-if="field.type === 'text' || !field.type" v-model="values[field.name]" :placeholder="field.label" />
        <!-- Number input -->
        <input v-else-if="field.type === 'number'" v-model="values[field.name]" type="number" :min="field.min" :max="field.max" />
        <!-- Date input -->
        <input v-else-if="field.type === 'date'" v-model="values[field.name]" type="date" />
        <!-- Select input -->
        <select v-else-if="field.type === 'select'" v-model="values[field.name]">
          <option value="">Select...</option>
          <option v-for="opt in (field.options || [])" :key="opt" :value="opt">{{ opt }}</option>
        </select>
        <!-- Tags input -->
        <input v-else-if="field.type === 'tags'" v-model="values[field.name]" placeholder="tag1, tag2, tag3" />
      </div>
    </div>
    <div class="form-footer">
      <button class="btn-cancel" @click="$emit('close')">Cancel</button>
      <button class="btn-create" @click="createMemory" :disabled="submitting">
        {{ submitting ? 'Creating...' : 'Create Memory' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'

const props = defineProps<{ template: any }>()
const emit = defineEmits<{ close: []; created: [] }>()
const toast = useToast()

const values = ref<Record<string, any>>({})
const submitting = ref(false)

onMounted(() => {
  if (props.template?.fields) {
    for (const field of props.template.fields) {
      values.value[field.name] = ''
    }
  }
})

async function createMemory() {
  submitting.value = true
  try {
    await request<any>(`/templates/${props.template.id}/create-memory`, {
      method: 'POST',
      body: JSON.stringify({ values: values.value }),
    })
    emit('created')
  } catch (e: any) {
    toast.error(e.message || 'Failed to create memory')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.template-form {
  background: var(--card, #fff); border-radius: 16px; width: 100%; max-width: 500px;
  max-height: 80vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.form-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; border-bottom: 1px solid var(--border, #e5e5ea);
}
.form-header h3 { margin: 0; font-size: 1.1rem; }
.btn-close { background: none; border: none; font-size: 1.2rem; cursor: pointer; }
.form-body { padding: 20px; }
.form-desc { font-size: 0.85rem; color: var(--text-secondary, #86868b); margin: 0 0 16px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-size: 0.8rem; font-weight: 600; margin-bottom: 4px; color: var(--text-secondary, #86868b); }
.required { color: var(--error, #ff3b30); }
.form-group input, .form-group select {
  width: 100%; padding: 8px 10px; border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px; font-size: 0.85rem; font-family: var(--font);
  background: var(--card, #fff); color: var(--text, #1d1d1f); box-sizing: border-box;
}
.form-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 12px 20px; border-top: 1px solid var(--border, #e5e5ea);
}
.btn-cancel, .btn-create {
  padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; cursor: pointer; font-family: var(--font);
}
.btn-cancel { background: var(--card, #fff); border: 1px solid var(--border, #e5e5ea); }
.btn-create { background: var(--accent, #007aff); color: #fff; border: none; }
.btn-create:disabled { opacity: 0.5; }
</style>
