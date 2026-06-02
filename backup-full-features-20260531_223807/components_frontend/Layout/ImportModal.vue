<template>
  <div class="import-modal-overlay" @click.self="$emit('close')">
    <div class="import-modal">
      <h2>导入记忆</h2>
      <div class="drop-zone" @dragover.prevent @drop.prevent="onDrop" @click="fileInput?.click()">
        <input ref="fileInput" type="file" accept=".json,.md" @change="onFileSelect" hidden />
        <div class="drop-content">
          <span class="drop-icon">📁</span>
          <p>拖拽文件到此处，或点击选择</p>
          <p class="drop-hint">支持 JSON / Markdown 格式</p>
        </div>
      </div>
      <div v-if="selectedFile" class="file-info">
        <span>{{ selectedFile.name }}</span>
        <span class="file-size">{{ formatSize(selectedFile.size) }}</span>
      </div>
      <div v-if="result" class="import-result" :class="{ success: result.success }">
        <p>导入完成: 新增 {{ result.imported }}，跳过 {{ result.skipped }}，失败 {{ result.failed }}</p>
      </div>
      <div class="form-actions">
        <button class="btn-cancel" @click="$emit('close')">关闭</button>
        <button class="btn-submit" @click="onImport" :disabled="!selectedFile || importing">
          {{ importing ? '导入中...' : '开始导入' }}
          <kbd v-if="selectedFile && !importing" class="submit-hint">↵</kbd>
        </button>
      </div>
      <p v-if="error" class="error-msg">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { importAgentMemory } from '@/api/agentmemory'

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'imported'): void
}>()

const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const importing = ref(false)
const error = ref('')
const result = ref<any>(null)

function onDrop(e: DragEvent) {
  const file = e.dataTransfer?.files[0]
  if (file) selectedFile.value = file
}

function onFileSelect(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) selectedFile.value = file
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function onImport() {
  if (!selectedFile.value) return
  importing.value = true
  error.value = ''
  try {
    result.value = await importAgentMemory(selectedFile.value)
    if (result.value.success) {
      emit('imported')
    }
  } catch (e: any) {
    error.value = e.message || '导入失败'
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.import-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.import-modal {
  background: var(--card);
  border-radius: 16px;
  padding: 32px;
  width: 90%;
  max-width: 480px;
}

h2 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 24px;
}

.drop-zone {
  border: 2px dashed var(--border);
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.drop-zone:hover {
  border-color: var(--accent);
  background: rgba(0, 113, 227, 0.05);
}

.drop-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 12px;
}

.drop-hint {
  color: var(--text-secondary);
  font-size: 0.8rem;
  margin-top: 4px;
}

.file-info {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  background: var(--tag-bg);
  border-radius: 8px;
  margin-top: 16px;
  font-size: 0.875rem;
}

.file-size {
  color: var(--text-secondary);
}

.import-result {
  margin-top: 16px;
  padding: 12px;
  border-radius: 8px;
  background: var(--success-bg);
  color: var(--success-text);
}

.import-result.success {
  background: var(--success-bg);
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

.submit-hint {
  margin-left: 8px;
  font-size: 0.7rem;
  padding: 2px 5px;
  border: 1px solid rgba(255,255,255,0.4);
  border-radius: 4px;
  background: rgba(255,255,255,0.15);
  color: rgba(255,255,255,0.9);
  font-family: monospace;
}

/* Responsive */
@media (max-width: 767px) {
  .import-modal {
    width: 95%;
    padding: 24px;
  }

  .drop-zone {
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
