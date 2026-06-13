<template>
  <!-- P38 r14: a11y — role/aria-modal/aria-labelledby + Esc to close
       P38 r29: 包裹 .modal-fade transition — 之前硬切, 现在与 WhatsNewModal
       共享 main.css 全局 .modal-pop-in / .modal-pop-out (200ms scale + fade). -->
  <transition name="modal-fade">
  <div class="create-modal-overlay" @click.self="$emit('close')" @keydown.esc="$emit('close')">
    <div
      class="create-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="create-modal-title"
    >
      <h2 id="create-modal-title">{{ $t('i18n.create_memory') }}</h2>
      <form @submit.prevent="onSubmit">
        <div class="form-group">
          <label>{{ $t('i18n.template') }}</label>
          <div class="template-select-wrapper">
            <select v-model="selectedTemplateId" class="template-select" @change="onTemplateChange">
              <option value="">✏️ {{ $t('i18n.custom') }}</option>
              <option v-for="tpl in templates" :key="tpl.id" :value="tpl.id">
                {{ tpl.icon }} {{ tpl.name }}
              </option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>Title <span class="required">*</span></label>
          <input v-model="form.title" type="text" required :placeholder="$t('i18n.create.title')" />
        </div>
        <div class="form-group">
          <label>Content <span class="required">*</span></label>
          <textarea v-model="form.content" required rows="4" :placeholder="$t('i18n.create.content')"></textarea>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>{{ $t('en_type') }}</label>
            <select v-model="form.type">
              <option value="pattern">{{ $t('en_type_pattern') }}</option>
              <option value="fact">{{ $t('en_type_fact') }}</option>
              <option value="preference">{{ $t('en_type_preference') }}</option>
              <option value="bug">{{ $t('en_type_bug') }}</option>
              <option value="workflow">{{ $t('en_type_workflow') }}</option>
              <option value="architecture">{{ $t('en_type_architecture') }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>{{ $t('en_strength') }}</label>
            <input v-model.number="form.strength" type="range" min="1" max="10" />
            <span class="strength-val">{{ form.strength * 10 }}%</span>
          </div>
        </div>
        <div class="form-group">
          <label>{{ $t('en_concepts') }}</label>
          <input v-model="conceptsStr" type="text" placeholder="$t('i18n.comma_separated')，如: hermes, kanban" />
        </div>
        <div class="form-group">
          <label>{{ $t('i18n.label') }}</label>
          <TagManager :tags="formTags" :all-tags="allTagNames" @update:tags="formTags = $event" />
        </div>
        <div class="form-actions">
          <button type="button" class="action-btn" @click="$emit('close')">取消</button>
          <button type="submit" class="action-btn action-btn--accent" :disabled="submitting">
            {{ submitting ? '创建中...' : '创建' }}
            <kbd class="submit-hint">⌘↵</kbd>
          </button>
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
      </form>
    </div>
  </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { createAgentMemory } from '@/api/agentmemory'
import { useAgentMemoryStore } from '@/stores/agentmemory'
import { useToast } from '@/composables/useToast'
import TagManager from './TagManager.vue'
import { fetchTemplates } from '@/api/agentmemory'
import type { MemoryTemplate } from '@/types'

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'created'): void
}>()

const toast = useToast()
const agentMemoryStore = useAgentMemoryStore()

const form = reactive({
  title: '',
  content: '',
  type: 'pattern',
  strength: 5,
})
const conceptsStr = ref('')
const formTags = ref<string[]>([])
const submitting = ref(false)
const error = ref('')
const templates = ref<MemoryTemplate[]>([])
const selectedTemplateId = ref('')

const allTagNames = computed(() => agentMemoryStore.allTags.map(t => t.tag))

// Fetch templates on mount
fetchTemplates().then(res => {
  templates.value = res.templates || []
}).catch(() => {
  // Silently fail — template selector will just have only "自定义"
})

function onTemplateChange() {
  if (!selectedTemplateId.value) {
    // Reset to defaults
    form.title = ''
    form.content = ''
    form.type = 'pattern'
    conceptsStr.value = ''
    return
  }
  const tpl = templates.value.find(t => t.id === selectedTemplateId.value)
  if (tpl) {
    form.type = tpl.type || 'pattern'
    form.title = tpl.title_template || ''
    form.content = tpl.content_template || ''
    conceptsStr.value = (tpl.suggested_concepts || []).join(', ')
  }
}

// Ctrl+Enter to submit quickly
function handleKeydown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault()
    if (!submitting.value && form.title.trim() && form.content.trim()) {
      onSubmit()
    }
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

async function onSubmit() {
  if (!form.title.trim() || !form.content.trim()) {
    error.value = 'Title 和 Content 不能为空'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    const concepts = conceptsStr.value
      .split(',')
      .map(c => c.trim())
      .filter(Boolean)
    await createAgentMemory({
      title: form.title,
      content: form.content,
      type: form.type,
      concepts,
      strength: form.strength,
      tags: formTags.value.length > 0 ? formTags.value : undefined,
    })
    toast.success('记忆创建成功')
    emit('created')
    emit('close')
  } catch (e: any) {
    const msg = e.message || '创建失败'
    error.value = msg
    toast.error(msg)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.create-modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--modal-backdrop);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  /* P38 r10: backdrop fade-in — 200ms 慢于页面切换 (150ms)，区分"打开"与"换页" */
  animation: modal-backdrop-in 200ms ease-out;
}

.create-modal {
  background: var(--card);
  border-radius: 16px;
  padding: 32px;
  width: 90%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  /* P38 r10: 弹窗弹出动画 — scale(0.96) + translateY(8px) → scale(1) + translateY(0)，
     200ms ease-out，强调"目标到达"感。Apple/Vercel 模态的经典节奏。 */
  animation: modal-pop-in 200ms cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modal-backdrop-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modal-pop-in {
  from {
    opacity: 0;
    transform: scale(0.96) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* P38 r10: 减少动效偏好用户 — 直接显示 */
@media (prefers-reduced-motion: reduce) {
  .create-modal-overlay,
  .create-modal {
    animation: none;
  }
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

.template-select-wrapper {
  position: relative;
}

.template-select {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid var(--accent);
  border-radius: 10px;
  background: var(--bg);
  color: var(--primary);
  font-size: 0.875rem;
  font-family: var(--font);
  font-weight: 500;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  cursor: pointer;
  appearance: auto;
}

/* P38 r14: :focus → :focus-visible (键盘焦点专用，不再 mouse click 触发) + rgba 改 token */
.template-select:focus-visible {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.required {
  color: var(--error);
}

input[type='text'],
textarea,
select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--primary);
  font-size: 0.875rem;
  font-family: var(--font);
  outline: none;
  transition: border-color 0.2s;
}

/* P38 r14: :focus → :focus-visible (键盘焦点专用) */
input:focus-visible,
textarea:focus-visible,
select:focus-visible {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

.strength-val {
  font-size: 0.875rem;
  color: var(--accent);
  font-weight: 600;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

/* P38 r23: btn-cancel / btn-submit → .action-btn (r21 global system).
   .action-btn 默认 8px 16px padding + 0.85rem 字号与旧值接近, form-actions
   的 padding 略缩到 6px 14px 让 modal 底部更克制。
   .submit-hint 保留 — kbd hint 是 form 提交快捷键, 跟按钮系统无关。 */

.submit-hint {
  margin-left: 8px;
  font-size: 0.7rem;
  padding: 2px 5px;
  border: 1px solid rgba(255,255,255,0.4);
  border-radius: 4px;
  background: rgba(255,255,255,0.15);
  color: rgba(255,255,255,0.9);
  font-family: var(--font-mono);
  font-weight: 500;
}

.error-msg {
  color: var(--error);
  font-size: 0.875rem;
  margin-top: 12px;
}

/* Responsive */
@media (max-width: 767px) {
  .create-modal {
    width: 95%;
    padding: 24px;
  }

  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions button {
    width: 100%;
  }
}
</style>
