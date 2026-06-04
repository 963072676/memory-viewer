<template>
  <div class="tag-manager">
    <div class="tag-list">
      <span v-for="tag in localTags" :key="tag" class="tag-pill">
        {{ tag }}
        <button
          v-if="!readonly"
          type="button"
          class="tag-remove"
          @click.stop="removeTag(tag)"
        >×</button>
      </span>
    </div>
    <div v-if="!readonly" class="tag-input-wrapper">
      <input
        v-model="inputValue"
        type="text"
        class="tag-input"
        placeholder="$t('zh_5a1514')"
        @keydown.enter.prevent="addTag"
        @input="onInput"
        @focus="showSuggestions = true"
        @blur="hideSuggestions"
      />
      <div v-if="showSuggestions && filteredSuggestions.length > 0" class="tag-suggestions">
        <div
          v-for="s in filteredSuggestions"
          :key="s"
          class="suggestion-item"
          @mousedown.prevent="selectSuggestion(s)"
        >
          {{ s }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = withDefaults(defineProps<{
  tags: string[]
  readonly?: boolean
  allTags?: string[] | undefined
}>(), {
  readonly: false,
  allTags: undefined,
})

const emit = defineEmits<{
  (e: 'update:tags', tags: string[]): void
}>()

const localTags = ref<string[]>([...props.tags])
const inputValue = ref('')
const showSuggestions = ref(false)

watch(() => props.tags, (newTags) => {
  localTags.value = [...newTags]
}, { deep: true })

const filteredSuggestions = computed(() => {
  if (!props.allTags || !inputValue.value.trim()) return []
  const query = inputValue.value.trim().toLowerCase()
  return props.allTags
    .filter(t => t.toLowerCase().includes(query) && !localTags.value.includes(t))
    .slice(0, 8)
})

function addTag() {
  const val = inputValue.value.trim().toLowerCase()
  if (val && !localTags.value.includes(val)) {
    localTags.value.push(val)
    emit('update:tags', [...localTags.value])
  }
  inputValue.value = ''
}

function removeTag(tag: string) {
  localTags.value = localTags.value.filter(t => t !== tag)
  emit('update:tags', [...localTags.value])
}

function selectSuggestion(tag: string) {
  const val = tag.trim().toLowerCase()
  if (val && !localTags.value.includes(val)) {
    localTags.value.push(val)
    emit('update:tags', [...localTags.value])
  }
  inputValue.value = ''
  showSuggestions.value = false
}

function onInput() {
  showSuggestions.value = true
}

function hideSuggestions() {
  // Delay to allow mousedown on suggestion to fire first
  setTimeout(() => {
    showSuggestions.value = false
  }, 150)
}
</script>

<style scoped>
.tag-manager {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.7rem;
  padding: 3px 8px;
  border-radius: 12px;
  background: var(--tag-bg);
  color: var(--text-secondary);
  white-space: nowrap;
}

.tag-remove {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.875rem;
  padding: 0;
  line-height: 1;
}

.tag-remove:hover {
  color: var(--error);
}

.tag-input-wrapper {
  position: relative;
}

.tag-input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--primary);
  font-size: 0.8rem;
  font-family: var(--font);
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.tag-input:focus {
  border-color: var(--accent);
}

.tag-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-top: 4px;
  z-index: 20;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  max-height: 160px;
  overflow-y: auto;
}

.suggestion-item {
  padding: 6px 12px;
  font-size: 0.8rem;
  color: var(--primary);
  cursor: pointer;
  transition: background 0.15s;
}

.suggestion-item:hover {
  background: var(--tag-bg);
}
</style>
