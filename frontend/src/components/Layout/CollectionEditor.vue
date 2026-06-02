<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h3>{{ isEditing ? 'Edit Collection' : 'Create Collection' }}</h3>
        <button class="btn-close" @click="$emit('close')">✕</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>Name *</label>
          <input v-model="form.name" placeholder="e.g. Important Patterns" />
        </div>
        <div class="form-group">
          <label>Description</label>
          <textarea v-model="form.description" placeholder="What is this collection about?" rows="2"></textarea>
        </div>
        <div class="form-row">
          <div class="form-group form-half">
            <label>Icon</label>
            <div class="icon-picker">
              <button
                v-for="icon in iconOptions"
                :key="icon"
                class="icon-option"
                :class="{ active: form.icon === icon }"
                @click="form.icon = icon"
              >
                {{ icon }}
              </button>
            </div>
          </div>
          <div class="form-group form-half">
            <label>Color</label>
            <div class="color-picker">
              <button
                v-for="color in colorOptions"
                :key="color"
                class="color-option"
                :class="{ active: form.color === color }"
                :style="{ background: color }"
                @click="form.color = color"
              ></button>
            </div>
          </div>
        </div>

        <div class="form-divider"></div>
        <h4 class="filter-title">Query Filters</h4>

        <div class="form-group">
          <label>Memory Type</label>
          <select v-model="form.filters.type">
            <option value="">All Types</option>
            <option value="pattern">Pattern</option>
            <option value="fact">Fact</option>
            <option value="preference">Preference</option>
            <option value="bug">Bug</option>
            <option value="workflow">Workflow</option>
            <option value="architecture">Architecture</option>
          </select>
        </div>
        <div class="form-group">
          <label>Tags (comma separated)</label>
          <input v-model="tagsInput" placeholder="e.g. important, python" />
        </div>
        <div class="form-row">
          <div class="form-group form-half">
            <label>Min Strength</label>
            <input v-model.number="form.filters.strength_min" type="number" min="0" max="10" step="1" placeholder="0" />
          </div>
          <div class="form-group form-half">
            <label>Max Strength</label>
            <input v-model.number="form.filters.strength_max" type="number" min="0" max="10" step="1" placeholder="10" />
          </div>
        </div>
        <div class="form-group">
          <label>Search Query</label>
          <input v-model="form.filters.query" placeholder="Text to match in title/content" />
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-cancel" @click="$emit('close')">Cancel</button>
        <button class="btn-save" @click="handleSave" :disabled="!form.name || saving">
          {{ saving ? 'Saving...' : (isEditing ? 'Update' : 'Create') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import type { Collection } from '@/api/collections'

const props = defineProps<{
  collection?: Collection | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved', data: any): void
}>()

const isEditing = computed(() => !!props.collection)
const saving = ref(false)

const iconOptions = ['📁', '📂', '⭐', '🔖', '📌', '🎯', '💡', '🔥', '💎', '🧩', '📚', '🏷️']
const colorOptions = ['#007aff', '#34c759', '#ff9500', '#ff3b30', '#af52de', '#5856d6', '#ff2d55', '#00c7be', '#ff6482', '#30b0c7']

const form = reactive({
  name: '',
  description: '',
  icon: '📁',
  color: '#007aff',
  filters: {
    type: '',
    tags: [] as string[],
    strength_min: undefined as number | undefined,
    strength_max: undefined as number | undefined,
    query: '',
  },
})

const tagsInput = ref('')

// Initialize form from collection prop
watch(() => props.collection, (col) => {
  if (col) {
    form.name = col.name
    form.description = col.description || ''
    form.icon = col.icon || '📁'
    form.color = col.color || '#007aff'
    form.filters.type = col.filters?.type || ''
    form.filters.tags = col.filters?.tags || []
    form.filters.strength_min = col.filters?.strength_min
    form.filters.strength_max = col.filters?.strength_max
    form.filters.query = col.filters?.query || ''
    tagsInput.value = (col.filters?.tags || []).join(', ')
  }
}, { immediate: true })

function handleSave() {
  // Parse tags from comma-separated input
  form.filters.tags = tagsInput.value
    .split(',')
    .map(t => t.trim())
    .filter(Boolean)

  // Clean empty filters
  const data: any = {
    name: form.name,
    description: form.description,
    icon: form.icon,
    color: form.color,
    filters: {} as any,
  }
  if (form.filters.type) data.filters.type = form.filters.type
  if (form.filters.tags.length) data.filters.tags = form.filters.tags
  if (form.filters.strength_min != null) data.filters.strength_min = form.filters.strength_min
  if (form.filters.strength_max != null) data.filters.strength_max = form.filters.strength_max
  if (form.filters.query) data.filters.query = form.filters.query

  emit('saved', data)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal {
  background: var(--card);
  border-radius: 16px;
  width: 100%;
  max-width: 520px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-height: 85vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--primary);
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: var(--text-secondary);
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--primary);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 0.85rem;
  font-family: var(--font);
  box-sizing: border-box;
  background: var(--bg);
  color: var(--primary);
}

.form-group textarea {
  resize: vertical;
}

.form-row {
  display: flex;
  gap: 12px;
}

.form-half {
  flex: 1;
}

.form-divider {
  height: 1px;
  background: var(--border);
  margin: 16px 0;
}

.filter-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--primary);
  margin: 0 0 12px;
}

.icon-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.icon-option {
  width: 36px;
  height: 36px;
  border: 2px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  cursor: pointer;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.2s;
}

.icon-option.active,
.icon-option:hover {
  border-color: var(--accent);
}

.color-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.color-option {
  width: 28px;
  height: 28px;
  border: 3px solid transparent;
  border-radius: 50%;
  cursor: pointer;
  transition: border-color 0.2s, transform 0.15s;
}

.color-option.active,
.color-option:hover {
  border-color: var(--primary);
  transform: scale(1.15);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 20px;
  border-top: 1px solid var(--border);
}

.btn-cancel,
.btn-save {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  cursor: pointer;
  font-family: var(--font);
}

.btn-cancel {
  background: var(--card);
  border: 1px solid var(--border);
  color: var(--primary);
}

.btn-save {
  background: var(--accent);
  color: #fff;
  border: none;
}

.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
