<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h3>{{ isEditing ? 'Edit Collection' : 'Create Collection' }}</h3>
        <button class="btn-close" @click="$emit('close')">✕</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>{{ $t('en_name_required') }}</label>
          <input v-model="form.name" :placeholder="$t('en_collection_name_hint')" />
        </div>
        <div class="form-group">
          <label>{{ $t('en_description') }}</label>
          <textarea v-model="form.description" :placeholder="$t('en_collection_desc_hint')" rows="2"></textarea>
        </div>
        <div class="form-row">
          <div class="form-group form-half">
            <label>{{ $t('en_icon') }}</label>
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
            <label>{{ $t('en_color') }}</label>
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
        <h4 class="filter-title">{{ $t('en_query_filters') }}</h4>

        <div class="form-group">
          <label>{{ $t('en_memory_type') }}</label>
          <select v-model="form.filters.type">
            <option value="">{{ $t('en_all_types') }}</option>
            <option value="pattern">{{ $t('en_type_pattern') }}</option>
            <option value="fact">{{ $t('en_type_fact') }}</option>
            <option value="preference">{{ $t('en_type_preference') }}</option>
            <option value="bug">{{ $t('en_type_bug') }}</option>
            <option value="workflow">{{ $t('en_type_workflow') }}</option>
            <option value="architecture">{{ $t('en_type_architecture') }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>{{ $t('en_tags_comma') }}</label>
          <input v-model="tagsInput" :placeholder="$t('en_tags_hint')" />
        </div>
        <div class="form-row">
          <div class="form-group form-half">
            <label>{{ $t('en_min_strength') }}</label>
            <input v-model.number="form.filters.strength_min" type="number" min="0" max="10" step="1" placeholder="0" />
          </div>
          <div class="form-group form-half">
            <label>{{ $t('en_max_strength') }}</label>
            <input v-model.number="form.filters.strength_max" type="number" min="0" max="10" step="1" placeholder="10" />
          </div>
        </div>
        <div class="form-group">
          <label>{{ $t('en_search_query') }}</label>
          <input v-model="form.filters.query" :placeholder="$t('en_text_match_hint')" />
        </div>
      </div>
      <div class="modal-footer">
        <button class="action-btn" @click="$emit('close')">{{ $t('en_cancel') }}</button>
        <button class="action-btn action-btn--accent" @click="handleSave" :disabled="!form.name || saving">
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
// P48 r2: 10 调色板 token 化 — 数组存 'var(--collection-color-N)' 引用而非字面 hex。
// dark 模式自动跟随 variables.css (light: 500 阶, dark: 前 5 色 400 阶，后 5 色 Apple hex 不变)。
// 决策：保留 hex string 在 backend (向后兼容旧 collection 数据 — `col.color` 仍是 hex，
// CollectionCard 仍可读 + 拼接 '20' alpha)；新 picker 选中的色存为 var() 引用。
const colorOptions = [
  'var(--collection-color-1)',  'var(--collection-color-2)',
  'var(--collection-color-3)',  'var(--collection-color-4)',
  'var(--collection-color-5)',  'var(--collection-color-6)',
  'var(--collection-color-7)',  'var(--collection-color-8)',
  'var(--collection-color-9)',  'var(--collection-color-10)',
]

const form = reactive({
  name: '',
  description: '',
  icon: '📁',
  color: 'var(--collection-color-1)',
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
    // P48 r2: 新 collection 默认 var() 引用，legacy hex 保留（CollectionCard 仍可读）。
    form.color = col.color || 'var(--collection-color-1)'
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
  background: var(--modal-backdrop);
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
  box-shadow: var(--shadow-modal);
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

/* P38 r23: btn-cancel / btn-save → .action-btn (r21 global system). */
</style>
