<template>
  <div class="annotation-thread">
    <div v-for="ann in annotations" :key="ann.id" class="annotation-item" :class="ann.type">
      <div class="ann-header">
        <span class="ann-avatar" :style="{ background: avatarColor(ann.author) }">{{ (ann.author || '?')[0].toUpperCase() }}</span>
        <span class="ann-author">{{ ann.author || 'Anonymous' }}</span>
        <span class="ann-time">{{ formatTime(ann.timestamp) }}</span>
        <span v-if="ann.type === 'flag'" class="ann-badge flag">🚩 {{ $t('zh_006616') }}</span>
        <span v-if="ann.type === 'suggest'" class="ann-badge suggest">💡 {{ $t('zh_006634') }}</span>
      </div>
      <div class="ann-content">{{ ann.content }}</div>
      <div class="ann-actions">
        <button class="btn-link" @click="replyTo = ann.id">{{ $t('zh_0064f5') }}</button>
        <button v-if="ann.type !== 'comment'" class="btn-link" @click="$emit('resolve', ann.id)">✅ {{ $t('zh_006b82') }}</button>
        <button class="btn-link danger" @click="$emit('delete', ann.id)">删除</button>
      </div>
      <!-- Nested replies -->
      <div v-if="ann.replies && ann.replies.length" class="replies">
        <AnnotationThread :annotations="ann.replies" @reply="(id) => $emit('reply', id)" @resolve="(id) => $emit('resolve', id)" @delete="(id) => $emit('delete', id)" />
      </div>
    </div>
    <div v-if="annotations.length === 0" class="empty-hint">{{ $t('zh_b656ec') }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ annotations: any[] }>()
defineEmits(['reply', 'resolve', 'delete'])

const replyTo = ref<string | null>(null)

function avatarColor(name: string) {
  const colors = ['#007aff', '#34c759', '#ff9500', '#af52de', '#ff3b30', '#5ac8fa']
  let hash = 0
  for (const c of (name || '')) hash = ((hash << 5) - hash) + c.charCodeAt(0)
  return colors[Math.abs(hash) % colors.length]
}

function formatTime(ts: string) {
  if (!ts) return ''
  try {
    return new Date(ts).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  } catch {
    return ts
  }
}
</script>

<style scoped>
.annotation-item { padding: 10px; border-left: 3px solid var(--border, #e0e0e0); margin-bottom: 8px; background: var(--card-bg, #fafafa); border-radius: 0 8px 8px 0; }
.annotation-item.flag { border-left-color: #ff9500; background: #fff8f0; }
.annotation-item.suggest { border-left-color: #5ac8fa; background: #f0f8ff; }
.ann-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; font-size: 13px; }
.ann-avatar { width: 24px; height: 24px; border-radius: 50%; color: white; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; }
.ann-author { font-weight: 600; }
.ann-time { color: #999; font-size: 12px; }
.ann-badge { font-size: 11px; padding: 1px 6px; border-radius: 4px; }
.ann-badge.flag { background: #fff3e0; color: #e65100; }
.ann-badge.suggest { background: #e3f2fd; color: #1565c0; }
.ann-content { font-size: 14px; margin-left: 32px; line-height: 1.5; }
.ann-actions { margin-left: 32px; margin-top: 4px; display: flex; gap: 12px; }
.btn-link { background: none; border: none; color: #007aff; cursor: pointer; font-size: 12px; padding: 0; }
.btn-link.danger { color: #ff3b30; }
.btn-link:hover { text-decoration: underline; }
.replies { margin-left: 24px; margin-top: 8px; }
.empty-hint { color: #999; font-size: 13px; padding: 8px; }
</style>
