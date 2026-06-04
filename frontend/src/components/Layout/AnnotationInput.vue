<template>
  <div class="annotation-input">
    <div class="input-row">
      <textarea
        v-model="content"
        :placeholder="placeholder"
        class="input-textarea"
        rows="2"
        @keydown.ctrl.enter="submit"
        @keydown.meta.enter="submit"
      />
    </div>
    <div class="input-actions">
      <select v-model="annType" class="type-select">
        <option value="comment">💬 {{ $t('zh_006bfa') }}</option>
        <option value="flag">🚩 {{ $t('zh_b7c731') }}</option>
        <option value="suggest">💡 {{ $t('zh_b2cea6') }}</option>
      </select>
      <input v-model="author" type="text" placeholder="$t('zh_a9e6fb')" class="author-input" />
      <button class="action-btn action-btn--accent action-btn--sm" :disabled="!content.trim()" @click="submit">
        {{ submitLabel || '发送' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  placeholder?: string
  submitLabel?: string
}>()

const emit = defineEmits(['submit'])

const content = ref('')
const annType = ref('comment')
const author = ref(localStorage.getItem('annotation-author') || '')

function submit() {
  if (!content.value.trim()) return
  if (author.value) localStorage.setItem('annotation-author', author.value)
  emit('submit', {
    content: content.value.trim(),
    type: annType.value,
    author: author.value || 'Anonymous',
  })
  content.value = ''
}
</script>

<style scoped>
.annotation-input { margin-top: 8px; }
.input-textarea { width: 100%; border: 1px solid var(--border, #ddd); border-radius: 8px; padding: 8px; font-size: 13px; resize: vertical; font-family: inherit; background: var(--card-bg, #fff); }
.input-textarea:focus { outline: none; border-color: var(--accent); }
.input-actions { display: flex; gap: 8px; margin-top: 6px; align-items: center; }
.type-select { border: 1px solid var(--border, #ddd); border-radius: 6px; padding: 4px 8px; font-size: 12px; background: var(--card-bg, #fff); }
.author-input { border: 1px solid var(--border, #ddd); border-radius: 6px; padding: 4px 8px; font-size: 12px; width: 100px; background: var(--card-bg, #fff); }
/* P38 r23: btn-submit → .action-btn + --accent + --sm. 之前 hardcoded #007aff (Apple 蓝)
   不与全站 Vercel 蓝 token 同源, dark 模式 white text 也不跟随 var(--card). */
.action-btn { margin-left: auto; }
</style>
