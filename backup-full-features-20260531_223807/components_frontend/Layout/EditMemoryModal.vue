<template>
  <div class="edit-modal-overlay" @click.self="$emit('close')">
    <div class="edit-modal">
      <h2>编辑记忆</h2>
      <form @submit.prevent="onSubmit">
        <div class="form-group">
          <label>Content</label>
          <textarea v-model="form.content" rows="5" placeholder="记忆内容"></textarea>
        </div>
        <div class="form-group">
          <label>Strength: <span class="strength-val">{{ form.strength * 10 }}%</span></label>
          <input v-model.number="form.strength" type="range" min="1" max="10" class="strength-slider" />
        </div>
        <div class="form-group">
          <label>Concepts</label>
          <div class="concepts-editor">
            <div class="concept-tags">
              <span v-for="(c, i) in form.concepts" :key="i" class="concept-tag">
                {{ c }}
                <button type="button" class="tag-remove" @click="removeConcept(i)">×</button>
              </span>
            </div>
            <div class="concept-input-row">
              <input
                v-model="newConcept"
                type="text"
                placeholder="输入概念后回车添加"
                @keydown.enter.prevent="addConcept"
              />
              <button type="button" class="btn-add-tag" @click="addConcept">+</button>
            </div>
          </div>
        </div>
        <div class="form-group">
          <label>标签</label>
          <TagManager :tags="formTags" :all-tags="allTagNames" @update:tags="formTags = $event" />
        </div>
        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="$emit('close')">取消</button>
          <button type="submit" class="btn-submit" :disabled="submitting">
            {{ submitting ? '保存中...' : '保存' }}
          </button>
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import type { AgentMemory } from '@/types'
import { updateAgentMemory, setMemoryTags } from '@/api/agentmemory'
import { useAgentMemoryStore } from '@/stores/agentmemory'
import { useToast } from '@/composables/useToast'
import TagManager from './TagManager.vue'

const props = defineProps<{
  memory: AgentMemory
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'updated'): void
}>()

const toast = useToast()
const agentMemoryStore = useAgentMemoryStore()

const form = reactive({
  content: props.memory.content,
  strength: props.memory.strength,
  concepts: [...props.memory.concepts],
})

const formTags = ref<string[]>([...(props.memory.tags || [])])
const newConcept = ref('')
const submitting = ref(false)
const error = ref('')

const allTagNames = computed(() => agentMemoryStore.allTags.map(t => t.tag))

function addConcept() {
  const val = newConcept.value.trim()
  if (val && !form.concepts.includes(val)) {
    form.concepts.push(val)
  }
  newConcept.value = ''
}

function removeConcept(index: number) {
  form.concepts.splice(index, 1)
}

async function onSubmit() {
  submitting.value = true
  error.value = ''
  try {
    await updateAgentMemory(props.memory.id, {
      content: form.content,
      strength: form.strength,
      concepts: form.concepts,
    })
    // Save tags separately
    await setMemoryTags(props.memory.id, formTags.value)
    toast.success('记忆更新成功')
    emit('updated')
    emit('close')
  } catch (e: any) {
    const msg = e.message || '保存失败'
    error.value = msg
    toast.error(msg)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.edit-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.edit-modal {
  background: var(--card);
  border-radius: 16px;
  padding: 32px;
  width: 90%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
}

h2 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 24px;
  color: var(--primary);
}

.form-group {
  margin-bottom: 16px;
}

label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--primary);
  font-size: 0.875rem;
  font-family: var(--font);
  outline: none;
  resize: vertical;
  transition: border-color 0.2s;
}

textarea:focus {
  border-color: var(--accent);
}

.strength-val {
  color: var(--accent);
  font-weight: 600;
}

.strength-slider {
  width: 100%;
  margin-top: 4px;
}

.concepts-editor {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.concept-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.concept-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  padding: 4px 10px;
  border-radius: 12px;
  background: var(--tag-bg);
  color: var(--text-secondary);
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

.concept-input-row {
  display: flex;
  gap: 8px;
}

.concept-input-row input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--primary);
  font-size: 0.875rem;
  font-family: var(--font);
  outline: none;
}

.concept-input-row input:focus {
  border-color: var(--accent);
}

.btn-add-tag {
  padding: 8px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--tag-bg);
  color: var(--primary);
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel {
  padding: 10px 20px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-family: var(--font);
}

.btn-submit {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  background: var(--accent);
  color: white;
  cursor: pointer;
  font-family: var(--font);
  font-weight: 500;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-msg {
  color: var(--error);
  font-size: 0.875rem;
  margin-top: 12px;
}

/* Responsive */
@media (max-width: 767px) {
  .edit-modal {
    width: 95%;
    padding: 24px;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions button {
    width: 100%;
  }
}
</style>
