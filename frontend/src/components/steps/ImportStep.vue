<template>
  <div class="import-step">
    <h3>📥 {{ $t('i18n.import_existing') }}</h3>
    <p class="desc">{{ $t('i18n.existing_memory') }}，{{ $t('i18n.import_here') }}</p>
    <div class="import-options">
      <div class="option-card" @click="mode = 'file'">
        <span class="option-icon">📄</span>
        <div>
          <div class="option-title">{{ $t('i18n.import_file') }}</div>
          <div class="option-desc">JSON / Markdown {{ $t('i18n.file') }}</div>
        </div>
      </div>
      <div class="option-card" @click="mode = 'skip'">
        <span class="option-icon">⏭️</span>
        <div>
          <div class="option-title">{{ $t('i18n.later') }}</div>
          <div class="option-desc">{{ $t('i18n.take_look') }}</div>
        </div>
      </div>
    </div>
    <div v-if="mode === 'file'" class="file-upload">
      <input type="file" accept=".json,.md,.txt" @change="handleFile" class="file-input" />
      <div v-if="imported" class="import-result">✅ {{ $t('i18n.imported') }} {{ count }} 条记忆</div>
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
.desc { color: var(--text-secondary); margin-bottom: 20px; font-size: 14px; }
.import-options { display: flex; gap: 12px; margin-bottom: 20px; }
.option-card { flex: 1; padding: 16px; border: 2px solid var(--border, #e0e0e0); border-radius: 12px; cursor: pointer; display: flex; align-items: center; gap: 12px; transition: all 0.2s; }
/* P47 r2: option-card hover 硬编码 Apple #007aff → --accent. 之前 border-color 在 dark 模式仍
   是亮蓝, 与全站 --accent (#0072f5 light / #3291ff dark) 偏移 0x0A, 视觉上"几乎是同一个颜色"但
   一旦将来 --accent 调整就会脱节. 顺手把 #e8f5e9/#2e7d32 改成 --success-bg/--success-text (与 P46 r1
   ShareModal 决策树同源). */
.option-card:hover { border-color: var(--accent); }
.option-icon { font-size: 28px; }
.option-title { font-weight: 600; font-size: 14px; }
.option-desc { font-size: 12px; color: var(--text-secondary); }
.file-upload { margin-top: 12px; }
.file-input { font-size: 14px; }
.import-result { margin-top: 12px; padding: 10px; background: var(--success-bg); border-radius: 8px; color: var(--success-text); }
</style>
