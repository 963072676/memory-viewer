<template>
  <div class="config-step">
    <h3>🔗 {{ $t('zh_1249c5') }}</h3>
    <p class="desc">{{ $t('zh_006ca4') }} Memory Viewer {{ $t('zh_ca8eb0') }} Agent 记忆</p>
    
    <!-- 快速开始按钮 -->
    <div class="quick-start-section">
      <button class="btn-quick-start" @click="useQuickStart">
        <span class="quick-icon">🚀</span>
        <span class="quick-text">{{ $t('zh_b36798') }}</span>
      </button>
      <span class="quick-hint">{{ $t('zh_d3cc17') }}，{{ $t('zh_b6cfba') }}</span>
    </div>
    
    <div class="divider"><span>{{ $t('zh_2e4796') }}</span></div>
    
    <div class="config-form">
      <div class="field">
        <label>{{ $t('zh_6c0370') }}</label>
        <input v-model="path" type="text" placeholder="/path/to/agentmemory.json" class="input" @keydown="handleKeydown" />
        <span class="hint">agentmemory.json {{ $t('zh_2daed4') }}</span>
      </div>
      <div class="field">
        <label>API {{ $t('zh_0069b3') }} ({{ $t('zh_0064cc') }})</label>
        <input v-model="api" type="text" placeholder="http://localhost:8000" class="input" @keydown="handleKeydown" />
        <span class="hint">{{ $t('zh_00655b') }} Memory Viewer {{ $t('zh_0d2967') }}，{{ $t('zh_c507cb') }}</span>
      </div>
      
      <!-- 预设配置 -->
      <div class="presets">
        <span class="presets-label">{{ $t('zh_d264b7') }}:</span>
        <button class="preset-btn" @click="usePreset('hermes')">🤖 Hermes</button>
        <button class="preset-btn" @click="usePreset('agentmemory')">📦 AgentMemory</button>
        <button class="preset-btn" @click="usePreset('local')">💻 {{ $t('zh_00670e') }}</button>
      </div>
      
      <div class="status" :class="status">
        {{ status === 'connected' ? '✅ 连接成功' : status === 'error' ? '❌ 连接失败' : '💡 填写路径后自动检测' }}
      </div>
    </div>
    
    <!-- 跳过按钮 -->
    <div class="skip-section">
      <button class="btn-skip-config" @click="skipConfig">{{ $t('zh_ccaa94') }} → {{ $t('zh_038820') }}</button>
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
  /* P47 r2: linear-gradient 硬编码 #667eea/#764ba2 → --accent-secondary (vars.css 已定义 #6366f1).
     SetupWizard banner 之前是"紫色独立品牌" — 现在与全站 --accent 同源 hue 偏移 90° (indigo),
     视觉上仍是 hero 横幅, 但已 token 化. 顺手把 on-accent color:white → var(--card). */
  background: linear-gradient(135deg, var(--accent-secondary) 0%, var(--accent) 100%);
  border-radius: 12px;
  color: var(--card);
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
  box-shadow: var(--shadow-toolbar);
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
/* Form styles */ .field { margin-bottom: 16px; }
.field label { display: block; font-weight: 600; font-size: 14px; margin-bottom: 4px; }
/* P47 r2: input / preset-btn / hint 硬编码 #007aff / #f0f7ff / #999 / #666 → 全站 token. */
.input { width: 100%; padding: 10px 12px; border: 1px solid var(--border, #ddd); border-radius: 8px; font-size: 14px; background: var(--card, #fff); }
.input:focus { outline: none; border-color: var(--accent); }
.hint { font-size: 12px; color: var(--text-tertiary); margin-top: 4px; display: block; }

/* Presets */
.presets {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 12px 0;
  flex-wrap: wrap;
}

.presets-label { font-size: 13px; color: var(--text-secondary); }
.preset-btn {
  padding: 6px 12px;
  border: 1px solid var(--border, #ddd);
  border-radius: 16px;
  background: var(--card, #fff);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-btn:hover {
  border-color: var(--accent);
  background: var(--accent-subtle);
}

/* P47 r2: ConfigStep status 硬编码 Material hex → 全站 token. .connected = success,
   .error = error. 与 P46 r1 ShareModal level-view/level-comment/level-edit 决策树同源. */
.status { padding: 10px; border-radius: 8px; font-size: 14px; margin-top: 16px; background: var(--bg-recessed); }
.status.connected { background: var(--success-bg); color: var(--success-text); }
.status.error { background: var(--error-bg); color: var(--error-text); }

/* Skip section */ .skip-section { margin-top: 16px; text-align: center; }
/* P47 r2: btn-skip-config 硬编码 Apple #007aff / #0056b3 → --accent / --accent-hover.
   SetupWizard 全套 (ImportStep/ConfigStep/DoneStep) 现在统一使用 --accent, 与全站主品牌色一致. */
.btn-skip-config {
  background: none;
  border: none;
  color: var(--accent);
  font-size: 13px;
  cursor: pointer;
  text-decoration: underline;
}

.btn-skip-config:hover { color: var(--accent-hover); }
</style>
