<template>
  <div class="config-step">
    <h3>🔗 连接记忆数据源</h3>
    <p class="desc">配置 Memory Viewer 读取你的 Agent 记忆</p>
    
    <!-- 快速开始按钮 -->
    <div class="quick-start-section">
      <button class="btn-quick-start" @click="useQuickStart">
        <span class="quick-icon">🚀</span>
        <span class="quick-text">快速开始</span>
      </button>
      <span class="quick-hint">使用内置示例数据，无需配置</span>
    </div>
    
    <div class="divider"><span>或手动配置</span></div>
    
    <div class="config-form">
      <div class="field">
        <label>数据源路径</label>
        <input v-model="path" type="text" placeholder="/path/to/agentmemory.json" class="input" @keydown="handleKeydown" />
        <span class="hint">agentmemory.json 文件的绝对路径</span>
      </div>
      <div class="field">
        <label>API 端点 (可选)</label>
        <input v-model="api" type="text" placeholder="http://localhost:8000" class="input" @keydown="handleKeydown" />
        <span class="hint">如果 Memory Viewer 已运行，自动检测</span>
      </div>
      
      <!-- 预设配置 -->
      <div class="presets">
        <span class="presets-label">预设配置:</span>
        <button class="preset-btn" @click="usePreset('hermes')">🤖 Hermes</button>
        <button class="preset-btn" @click="usePreset('agentmemory')">📦 AgentMemory</button>
        <button class="preset-btn" @click="usePreset('local')">💻 本地</button>
      </div>
      
      <div class="status" :class="status">
        {{ status === 'connected' ? '✅ 连接成功' : status === 'error' ? '❌ 连接失败' : '💡 填写路径后自动检测' }}
      </div>
    </div>
    
    <!-- 跳过按钮 -->
    <div class="skip-section">
      <button class="btn-skip-config" @click="skipConfig">跳过配置 → 使用示例数据</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const emit = defineEmits<{
  (e: 'skip'): void
}>()

const path = ref(localStorage.getItem('memory-source-path') || '')
const api = ref(localStorage.getItem('memory-api') || '')
const status = ref<'idle' | 'connected' | 'error'>('idle')

// Auto-save
import { watch } from 'vue'
watch(path, (v) => localStorage.setItem('memory-source-path', v))
watch(api, (v) => localStorage.setItem('memory-api', v))

// Press Enter on config fields to trigger quick start
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    useQuickStart()
  }
}

function useQuickStart() {
  // 使用快速开始，跳过配置
  emit('skip')
}

function usePreset(preset: string) {
  const presets: Record<string, { path: string; api: string }> = {
    hermes: {
      path: '/opt/hermes/.hermes/memories/agentmemory.json',
      api: ''
    },
    agentmemory: {
      path: '/opt/data/.agentmemory/standalone.json',
      api: ''
    },
    local: {
      path: '/data/.agentmemory/standalone.json',
      api: 'http://localhost:8501'
    }
  }
  const config = presets[preset]
  if (config) {
    path.value = config.path
    api.value = config.api
    localStorage.setItem('memory-source-path', config.path)
    localStorage.setItem('memory-api', config.api)
  }
}

function skipConfig() {
  emit('skip')
}
</script>

<style scoped>
.config-step h3 { margin-bottom: 8px; }
.desc { color: #666; margin-bottom: 20px; font-size: 14px; }

/* Quick start section */
.quick-start-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.btn-quick-start {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 32px;
  background: white;
  color: #667eea;
  border: none;
  border-radius: 24px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.btn-quick-start:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}

.quick-icon { font-size: 18px; }
.quick-text { font-size: 16px; }
.quick-hint { font-size: 12px; margin-top: 8px; opacity: 0.9; }

.divider {
  display: flex;
  align-items: center;
  margin: 16px 0;
  color: #999;
  font-size: 13px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border, #ddd);
}

.divider span { padding: 0 12px; }

/* Form styles */
.field { margin-bottom: 16px; }
.field label { display: block; font-weight: 600; font-size: 14px; margin-bottom: 4px; }
.input { width: 100%; padding: 10px 12px; border: 1px solid var(--border, #ddd); border-radius: 8px; font-size: 14px; background: var(--card-bg, #fff); }
.input:focus { outline: none; border-color: #007aff; }
.hint { font-size: 12px; color: #999; margin-top: 4px; display: block; }

/* Presets */
.presets {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 12px 0;
  flex-wrap: wrap;
}

.presets-label { font-size: 13px; color: #666; }
.preset-btn {
  padding: 6px 12px;
  border: 1px solid var(--border, #ddd);
  border-radius: 16px;
  background: var(--card-bg, #fff);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-btn:hover {
  border-color: #007aff;
  background: #f0f7ff;
}

.status { padding: 10px; border-radius: 8px; font-size: 14px; margin-top: 16px; background: #f8f9fa; }
.status.connected { background: #e8f5e9; color: #2e7d32; }
.status.error { background: #ffebee; color: #c62828; }

/* Skip section */
.skip-section { margin-top: 16px; text-align: center; }
.btn-skip-config {
  background: none;
  border: none;
  color: #007aff;
  font-size: 13px;
  cursor: pointer;
  text-decoration: underline;
}

.btn-skip-config:hover { color: #0056b3; }
</style>
