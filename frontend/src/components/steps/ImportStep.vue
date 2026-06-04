<template>
  <div class="import-step">
    <h3>📥 {{ $t('zh_9b417e') }}</h3>
    <p class="desc">{{ $t('zh_7b9837') }}，{{ $t('zh_862088') }}</p>
    <div class="import-options">
      <div class="option-card" @click="mode = 'file'">
        <span class="option-icon">📄</span>
        <div>
          <div class="option-title">{{ $t('zh_d30e63') }}</div>
          <div class="option-desc">JSON / Markdown {{ $t('zh_0066cf') }}</div>
        </div>
      </div>
      <div class="option-card" @click="mode = 'skip'">
        <span class="option-icon">⏭️</span>
        <div>
          <div class="option-title">{{ $t('zh_c0bb09') }}</div>
          <div class="option-desc">{{ $t('zh_300a8c') }}</div>
        </div>
      </div>
    </div>
    <div v-if="mode === 'file'" class="file-upload">
      <input type="file" accept=".json,.md,.txt" @change="handleFile" class="file-input" />
      <div v-if="imported" class="import-result">✅ {{ $t('zh_0d2282') }} {{ count }} 条记忆</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { request } from '@/api/index'

const mode = ref('')
const imported = ref(false)
const count = ref(0)

async function handleFile(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  try {
    const text = await file.text()
    const data = JSON.parse(text)
    const memories = Array.isArray(data) ? data : data.memories || [data]
    count.value = memories.length
    imported.value = true
  } catch {
    alert('文件格式不支持，请使用 JSON 格式')
  }
}
</script>

<style scoped>
.import-step h3 { margin-bottom: 8px; }
.desc { color: #666; margin-bottom: 20px; font-size: 14px; }
.import-options { display: flex; gap: 12px; margin-bottom: 20px; }
.option-card { flex: 1; padding: 16px; border: 2px solid var(--border, #e0e0e0); border-radius: 12px; cursor: pointer; display: flex; align-items: center; gap: 12px; transition: all 0.2s; }
.option-card:hover { border-color: #007aff; }
.option-icon { font-size: 28px; }
.option-title { font-weight: 600; font-size: 14px; }
.option-desc { font-size: 12px; color: #666; }
.file-upload { margin-top: 12px; }
.file-input { font-size: 14px; }
.import-result { margin-top: 12px; padding: 10px; background: #e8f5e9; border-radius: 8px; color: #2e7d32; }
</style>
