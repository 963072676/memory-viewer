<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h3>🔗 Create Memory Link</h3>
        <button class="btn-close" @click="$emit('close')">✕</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>Source Memory</label>
          <div class="memory-display">
            <span class="memory-badge">{{ sourceTitle || sourceId }}</span>
          </div>
        </div>

        <div class="form-group">
          <label>Target Memory *</label>
          <div class="search-wrapper">
            <input
              v-model="searchQuery"
              placeholder="Search for target memory..."
              @input="onSearch"
            />
            <div v-if="searchResults.length" class="search-dropdown">
              <div
                v-for="result in searchResults"
                :key="result.id"
                class="search-result"
                @click="selectTarget(result)"
              >
                <span class="result-type" :class="result.type">{{ result.type }}</span>
                <span class="result-title">{{ result.title }}</span>
              </div>
            </div>
          </div>
          <div v-if="selectedTarget" class="selected-target">
            <span class="target-badge">
              {{ selectedTarget.title }}
              <button class="clear-btn" @click="selectedTarget = null">✕</button>
            </span>
          </div>
        </div>

        <div class="form-group">
          <label>Relation Type *</label>
          <select v-model="relationType">
            <option value="">Select a relation type</option>
            <option value="related">Related</option>
            <option value="depends_on">Depends On</option>
            <option value="contradicts">Contradicts</option>
            <option value="extends">Extends</option>
            <option value="derived_from">Derived From</option>
            <option value="duplicates">Duplicates</option>
            <option value="references">References</option>
          </select>
        </div>

        <div class="form-group">
          <label>Label (optional)</label>
          <input v-model="label" placeholder="e.g. implements pattern X" />
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-cancel" @click="$emit('close')">Cancel</button>
        <button
          class="btn-save"
          @click="handleCreate"
          :disabled="!selectedTarget || !relationType || creating"
        >
          {{ creating ? 'Creating...' : 'Create Link' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { request } from '@/api/index'
import { createLink } from '@/api/links'

const props = defineProps<{
  sourceId: string
  sourceTitle?: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'created'): void
}>()

const searchQuery = ref('')
const searchResults = ref<Array<{ id: string; title: string; type: string }>>([])
const selectedTarget = ref<{ id: string; title: string } | null>(null)
const relationType = ref('')
const label = ref('')
const creating = ref(false)

let searchTimeout: ReturnType<typeof setTimeout> | null = null

function onSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  if (searchQuery.value.length < 2) {
    searchResults.value = []
    return
  }
  searchTimeout = setTimeout(async () => {
    try {
      const res = await request<any>(`/search/quick?q=${encodeURIComponent(searchQuery.value)}&limit=8`)
      searchResults.value = (res.results || []).filter((r: any) => r.id !== props.sourceId)
    } catch {
      searchResults.value = []
    }
  }, 300)
}

function selectTarget(result: { id: string; title: string; type: string }) {
  selectedTarget.value = { id: result.id, title: result.title }
  searchQuery.value = ''
  searchResults.value = []
}

async function handleCreate() {
  if (!selectedTarget.value || !relationType.value) return
  creating.value = true
  try {
    await createLink({
      source_id: props.sourceId,
      target_id: selectedTarget.value.id,
      relation_type: relationType.value,
      label: label.value || undefined,
    })
    emit('created')
  } catch (e) {
    console.error('Failed to create link:', e)
  } finally {
    creating.value = false
  }
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
  max-width: 480px;
  box-shadow: var(--shadow-modal);
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
.form-group select {
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

.memory-display {
  padding: 6px 0;
}

.memory-badge {
  display: inline-block;
  padding: 4px 10px;
  background: var(--tag-bg);
  border-radius: 6px;
  font-size: 0.8rem;
  color: var(--primary);
}

.search-wrapper {
  position: relative;
}

.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 10;
  box-shadow: var(--shadow);
}

.search-result {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.search-result:hover {
  background: var(--tag-bg);
}

.result-type {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 4px;
  background: var(--tag-bg);
  color: var(--text-secondary);
  text-transform: capitalize;
}

.result-title {
  font-size: 0.8rem;
  color: var(--primary);
}

.selected-target {
  margin-top: 8px;
}

.target-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: var(--accent);
  color: white;
  border-radius: 6px;
  font-size: 0.8rem;
}

.clear-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 0.85rem;
  padding: 0;
  line-height: 1;
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
