<template>
  <div class="rag-response" v-if="response">
    <div class="rag-header">
      <h3>🤖 AI Answer</h3>
      <div class="confidence-indicator">
        <span class="confidence-label">Confidence:</span>
        <div class="confidence-bar">
          <div class="confidence-fill" :style="{ width: `${(response.confidence || 0) * 100}%` }" :class="confidenceClass"></div>
        </div>
        <span class="confidence-value">{{ Math.round((response.confidence || 0) * 100) }}%</span>
      </div>
    </div>

    <div class="rag-answer" v-html="formatAnswer(response.answer)"></div>

    <!-- Sources with Citations -->
    <div class="rag-sources" v-if="response.sources?.length">
      <h4>📚 Sources</h4>
      <RagCitation v-for="(src, i) in response.sources" :key="src.id" :source="src" :index="i + 1" />
    </div>

    <!-- Follow-up Questions -->
    <div class="rag-followup" v-if="response.follow_up_questions?.length">
      <h4>💡 Follow-up Questions</h4>
      <div class="followup-chips">
        <button
          v-for="q in response.follow_up_questions"
          :key="q"
          class="followup-chip"
          @click="$emit('followup', q)"
        >{{ q }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import RagCitation from './RagCitation.vue'

const props = defineProps<{ response: any }>()
defineEmits<{ followup: [query: string] }>()

const confidenceClass = computed(() => {
  const c = props.response?.confidence || 0
  if (c >= 0.7) return 'high'
  if (c >= 0.4) return 'medium'
  return 'low'
})

function formatAnswer(text: string): string {
  if (!text) return ''
  // Simple markdown-like formatting
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\[(\d+)\]/g, '<sup class="citation-ref">[$1]</sup>')
    .replace(/\n/g, '<br>')
}
</script>

<style scoped>
.rag-response {
  background: var(--card, #fff); border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px; padding: 20px; margin-top: 16px;
  border-left: 4px solid var(--accent, #007aff);
}
.rag-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;
}
.rag-header h3 { margin: 0; font-size: 1rem; color: var(--primary, #007aff); }
.confidence-indicator { display: flex; align-items: center; gap: 8px; }
.confidence-label { font-size: 0.75rem; color: var(--text-secondary, #86868b); }
.confidence-bar { width: 80px; height: 6px; background: var(--tag-bg, #f5f5f7); border-radius: 3px; overflow: hidden; }
.confidence-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
.confidence-fill.high { background: #34c759; }
.confidence-fill.medium { background: #ff9500; }
.confidence-fill.low { background: #ff3b30; }
.confidence-value { font-size: 0.75rem; font-weight: 600; color: var(--text, #1d1d1f); }
.rag-answer {
  font-size: 0.9rem; line-height: 1.7; color: var(--text, #1d1d1f);
  margin-bottom: 16px; padding: 12px; background: var(--tag-bg, #f5f5f7); border-radius: 8px;
}
.rag-sources { margin-bottom: 16px; }
.rag-sources h4 { margin: 0 0 8px; font-size: 0.9rem; }
.rag-followup h4 { margin: 0 0 8px; font-size: 0.9rem; }
.followup-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.followup-chip {
  padding: 6px 12px; border: 1px solid var(--border, #e5e5ea);
  border-radius: 16px; background: var(--card, #fff); font-size: 0.8rem;
  cursor: pointer; font-family: var(--font); color: var(--primary, #007aff);
  transition: all 0.2s;
}
.followup-chip:hover { background: var(--accent, #007aff); color: #fff; }
:deep(.citation-ref) {
  font-size: 0.7rem; color: var(--accent, #007aff); font-weight: 600; cursor: pointer;
}
</style>
